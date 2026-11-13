import re

from utils.decorators import benchmark


def count_overlapping(text: str, pattern: str) -> int:
    return len(re.findall(f"(?={re.escape(pattern)})", text))


@benchmark
def parse(data: str) -> tuple[list[str], str]:
    runic: list[str] = []
    words: list[str] = []
    pattern = True
    for line in data.splitlines():
        if line:
            line = line.strip(".,:")
            if pattern:
                runic += line.split(",")
                runic[0] = runic[0].removeprefix("WORDS:")
                pattern = False
            else:
                words = line.split()
    return runic, " ".join(words)


@benchmark
def part_1(data: tuple[list[str], str]) -> int:
    runic, sentence = data
    return sum(count_overlapping(sentence, r) for r in runic)


@benchmark
def part_2(data: tuple[list[str], str]) -> int:
    return 0


@benchmark
def part_3(data: tuple[list[str], str]) -> int:
    return 0


test_data_1 = """WORDS:THE,OWE,MES,ROD,HER

AWAKEN THE POWER ADORNED WITH THE FLAMES BRIGHT IRE
"""
test_data_2 = test_data_1
test_data_3 = test_data_1

# Optional: if set, --test checks the result against these.
expected_1 = 4
