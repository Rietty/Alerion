from utils.decorators import benchmark


@benchmark
def parse(data: str) -> str:
    return data


@benchmark
def part_1(data: str) -> int:
    return 0


@benchmark
def part_2(data: str) -> int:
    return 0


@benchmark
def part_3(data: str) -> int:
    return 0


test_data_1 = """ABBAC"""
test_data_2 = """AxBCDDCAxD"""
test_data_3 = """xBxAAABCDxCC"""

# Optional: if set, --test checks the result against these.
expected_1 = 5
expected_2 = 28
expected_3 = 30
