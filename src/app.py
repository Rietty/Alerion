import importlib
import sys
from typing import TypedDict, Unpack, cast, get_args

import click
import cloup
import dotenv
from loguru import logger as log

from utils.solver import Part, Solution, solve_problem, test_problem

dotenv.load_dotenv()


class MainKwargs(TypedDict):
    event: int
    quest: int
    part: int
    test: bool
    file: str | None
    submit: bool


def to_part(n: int) -> Part:
    """Narrow a plain int to the Part literal for the type checker."""
    if n not in get_args(Part.__value__):
        raise ValueError(f"part must be one of {get_args(Part.__value__)}, got {n!r}")
    return cast(Part, n)


def load_solution(event: int, quest: int) -> Solution:
    module = importlib.import_module(f"solutions.e{event}.quest{quest:02d}")
    return Solution.from_module(module)


@cloup.command()
@cloup.option("--event", "-e", type=int, required=True, help="Event year (e.g. 2025).")
@cloup.option("--quest", "-q", type=int, required=True, help="Quest number.")
@cloup.option(
    "--part",
    "-p",
    type=click.IntRange(1, 3),
    required=True,
    help="Quest part (1, 2 or 3).",
)
@cloup.option_group(
    "Data",
    "Deciding on data source and destination.",
    cloup.option(
        "--test",
        "-t",
        is_flag=True,
        default=False,
        help="Solve the sample input instead of the quest input.",
    ),
    cloup.option(
        "--submit",
        "-s",
        is_flag=True,
        default=False,
        help="Submit the solution after solving it.",
    ),
    cloup.option("--file", "-f", type=str, default=None, help="Path to an input file."),
    constraint=cloup.constraints.mutually_exclusive,
)
def main(**kwargs: Unpack[MainKwargs]) -> None:
    """Solve a specific Everybody Codes quest."""
    event = kwargs["event"]
    quest = kwargs["quest"]
    part = to_part(kwargs["part"])

    try:
        solution = load_solution(event, quest)

        if kwargs["test"] or kwargs["file"]:
            log.info(f"Testing event {event}, quest {quest}, part {part}...")
            test_problem(part=part, solution=solution, file=kwargs["file"])
        else:
            log.info(f"Solving event {event}, quest {quest}, part {part}...")
            solve_problem(
                event=event,
                quest=quest,
                part=part,
                solution=solution,
                publish=kwargs["submit"],
            )
    except Exception as e:
        log.error(f"{type(e).__name__}: {e}")
        raise


if __name__ == "__main__":
    log.remove()
    format = (
        "[<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green>] "
        "[<level>{level: >5}</level>] "
        "[<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>] "
        "<level>{message}</level>"
    )
    log.add(sys.stdout, format=format, colorize=True)
    main()
