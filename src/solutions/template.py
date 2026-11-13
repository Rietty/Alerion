from utils.decorators import benchmark


@benchmark
def parse(data: str) -> list[str]:
    return data.splitlines()


@benchmark
def part_1(data: list[str]) -> int:
    return 0


@benchmark
def part_2(data: list[str]) -> int:
    return 0


@benchmark
def part_3(data: list[str]) -> int:
    return 0


test_data_1 = """
"""
test_data_2 = test_data_1
test_data_3 = test_data_1

# Optional: if set, --test checks the result against these.
# expected_1 = 0
