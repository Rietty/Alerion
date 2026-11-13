from collections import Counter

from utils.decorators import benchmark


def calculate_required(enemy: str, extra: int) -> int:
    match enemy:
        case "A":
            return 0 + extra
        case "B":
            return 1 + extra
        case "C":
            return 3 + extra
        case "D":
            return 5 + extra
        case _:
            return 0


def calculate_extra(enemies: str) -> int:
    return len(enemies) - 1 - enemies.count("x")


@benchmark
def parse(data: str) -> str:
    return data


@benchmark
def part_1(data: str) -> int:
    c = Counter(data)
    return c["B"] + (c["C"] * 3)


@benchmark
def part_2(data: str) -> int:
    total = 0
    for i in range(0, len(data), 2):
        enemies = data[i : i + 2]
        offset = calculate_extra(enemies)
        total += sum(calculate_required(e, offset) for e in enemies)
    return total


@benchmark
def part_3(data: str) -> int:
    total = 0
    for i in range(0, len(data), 3):
        enemies = data[i : i + 3]
        offset = calculate_extra(enemies)
        total += sum(calculate_required(e, offset) for e in enemies)
    return total


test_data_1 = """ABBAC"""
test_data_2 = """AxBCDDCAxD"""
test_data_3 = """xBxAAABCDxCC"""

# Optional: if set, --test checks the result against these.
expected_1 = 5
expected_2 = 28
expected_3 = 30
