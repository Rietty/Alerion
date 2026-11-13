from collections.abc import Callable
from dataclasses import dataclass, field
from types import ModuleType
from typing import Any, Literal, get_args

from ecd import get_inputs, submit
from loguru import logger as log

type Part = Literal[1, 2, 3]
type Answer = int | str

PARTS: tuple[Part, ...] = get_args(Part.__value__)


def _compose(
    parse: Callable[[str], Any],
    fn: Callable[[Any], Answer],
) -> Callable[[str], Answer]:
    # A helper function avoids the late-binding bug you'd get from a lambda in a loop.
    return lambda raw: fn(parse(raw))


@dataclass(frozen=True)
class Solution:
    """Everything needed to run one quest. Each part maps raw text to an answer."""

    parts: dict[Part, Callable[[str], Answer]]
    samples: dict[Part, str] = field(default_factory=dict)
    expected: dict[Part, Answer] = field(default_factory=dict)  # answers for samples

    def run(self, part: Part, raw: str) -> Answer:
        if part not in self.parts:
            raise KeyError(f"Part {part} is not implemented")
        return self.parts[part](raw)

    @classmethod
    def from_module(cls, module: ModuleType) -> Solution:
        """Build a Solution from a quest module.

        Expected names: parse (or parse_N per part), part_N, test_data_N,
        and optionally expected_N, for N in 1..3.
        """
        default_parse = getattr(module, "parse", None)
        parts: dict[Part, Callable[[str], Answer]] = {}
        samples: dict[Part, str] = {}
        expected: dict[Part, Answer] = {}

        for n in PARTS:
            fn = getattr(module, f"part_{n}", None)
            if fn is None:
                continue  # part not written yet

            parse = getattr(module, f"parse_{n}", default_parse)
            if parse is None:
                raise AttributeError(f"{module.__name__} needs `parse` or `parse_{n}`")
            parts[n] = _compose(parse, fn)

            sample = getattr(module, f"test_data_{n}", None)
            if sample is not None:
                # Trim the newlines from triple-quoted strings so splitlines()
                # doesn't produce an empty first line.
                samples[n] = sample.strip("\n")
            if hasattr(module, f"expected_{n}"):
                expected[n] = getattr(module, f"expected_{n}")

        if not parts:
            raise AttributeError(f"{module.__name__} defines no part_1/part_2/part_3")
        return cls(parts=parts, samples=samples, expected=expected)


def submit_answer(answer: Answer, *, event: int, quest: int, part: Part) -> None:
    submit(quest=quest, event=event, answer=answer, part=part, quiet=True)


def solve_problem(
    event: int,
    quest: int,
    part: Part,
    solution: Solution,
    publish: bool = False,
) -> Answer | None:
    # Each part has its own input, keyed by the part number as a string.
    inputs = get_inputs(event=event, quest=quest)
    try:
        raw = inputs[str(part)]
    except KeyError:
        log.error(f"No input for part {part}; available keys: {list(inputs)}")
        return None

    try:
        result = solution.run(part, raw)
    except KeyError as e:
        log.error(e)
        return None

    log.info(f"Event {event} quest {quest} part {part}: {result}")

    if publish:
        submit_answer(result, event=event, quest=quest, part=part)

    return result


def test_problem(
    part: Part,
    solution: Solution,
    file: str | None = None,
) -> bool | None:
    """Run a part against its sample (or a local file) and check the expected answer."""
    if file:
        log.info(f"Reading from {file}...")
        with open(file) as f:
            raw = f.read()
    elif part in solution.samples:
        raw = solution.samples[part]
    else:
        log.error(f"No sample data for part {part}")
        return None

    try:
        result = solution.run(part, raw)
    except KeyError as e:
        log.error(e)
        return None

    log.info(f"Test part {part}: {result}")

    # A local file is real input, so there's nothing to compare it against.
    if file or part not in solution.expected:
        return None

    ok = str(result) == str(solution.expected[part])
    if ok:
        log.success("Matches expected")
    else:
        log.error(f"Expected {solution.expected[part]!r}, got {result!r}")
    return ok
