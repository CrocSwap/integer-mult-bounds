"""Replay the literal negative-half table against exact signed arithmetic."""

import json
from pathlib import Path


GLYPHS = frozenset(("0", "1", "P0", "P1", "S0", "S1"))
PACKAGE = Path(__file__).resolve().parent
MAX_WIDTH = 4096


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_table():
    with (PACKAGE / "TABLE.txt").open(encoding="ascii") as source:
        text = source.read(4097)
    require(len(text) <= 4096, "table exceeds 4096 characters")
    table = {}
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        state, read, coin, target, write, move = line.split()
        require(read in GLYPHS and write in GLYPHS, "invalid glyph")
        require(move in ("-1", "0", "1"), "invalid movement")
        require(coin in ("*", "0", "1"), "invalid coin")
        require(state[0] == target[0] and state[0] in "FI", "mixed directions")
        for bit in (0, 1) if coin == "*" else (int(coin),):
            key = (state, read, bit)
            require(key not in table, "duplicate input row")
            table[key] = (target, write, int(move))
    require(len(table) == 70, "expected 70 coin-expanded rows")
    for direction in "FI":
        require(sum(key[0].startswith(direction) for key in table) == 35,
                "expected 35 rows per direction")
    return table


def check_local_inverse(table):
    directions = {}
    predecessors = set()
    for (_, _, coin), (target, write, move) in table.items():
        require(directions.setdefault(target, move) == move,
                "ambiguous incoming head movement")
        key = (target, write, coin)
        require(key not in predecessors, "ambiguous predecessor row")
        predecessors.add(key)


def signed_bounds(width):
    return -(1 << (width - 1)), (1 << (width - 1)) - 1


def marked_bits(value, width, parity):
    lower, upper = signed_bounds(width)
    require(lower <= value <= upper, "value outside signed width")
    bits = [str((value >> bit) & 1) for bit in range(width)]
    bits[-1] = "S" + bits[-1]
    return [f"P{parity}", *bits]


def execute(table, tape, origin, width, coin, direction):
    require(2 <= width <= MAX_WIDTH, "unsupported replay width")
    head, state = origin, direction + "0"
    for steps in range(4 * width + 2):
        require(origin <= head <= origin + width, "exterior head excursion")
        if state == direction + "H":
            return steps, state, head
        row = table.get((state, tape[head], coin))
        if row is None:
            return steps, state, head
        state, tape[head], move = row
        head += move
    raise ValueError("transition bound exceeded")


def expected_steps(x, width, coin):
    quotient, parity = divmod(x, 2)
    if parity * coin:
        return 2 * width + 1
    trailing_zeros = (quotient & -quotient).bit_length() - 1
    turning_index = width - 1 if quotient == 0 else trailing_zeros
    return 2 * width + 2 * turning_index + 3


def round_trip(table, x, width, coin, origin):
    prefix = list(("S1", "P1", "0", "S0")[:origin])
    suffix = ["P0", "S1", "1"]
    initial = prefix + marked_bits(x, width, 0) + suffix
    tape = initial.copy()
    steps, state, head = execute(table, tape, origin, width, coin, "F")
    y, remainder = divmod(-x, 2)
    y += int(coin < remainder)
    expected = prefix + marked_bits(y, width, x % 2) + suffix
    require((state, head) == ("FH", origin), "forward return")
    require(tape == expected, "forward endpoint")
    require(steps == expected_steps(x, width, coin), "forward invoice")
    inverse = execute(table, tape, origin, width, coin, "I")
    require(inverse == (steps, "IH", origin), "inverse return or invoice")
    require(tape == initial, "inverse endpoint")
    return 2 * steps


def inverse_boundary(table, width, y, parity, coin):
    tape = marked_bits(y, width, parity)
    steps, state, head = execute(table, tape, 0, width, coin, "I")
    x = -2 * y + parity * (1 - 2 * coin)
    lower, upper = signed_bounds(width)
    if lower <= x <= upper:
        require((steps, state, head) == (expected_steps(x, width, coin), "IH", 0),
                "valid inverse return or invoice")
        require(tape == marked_bits(x, width, 0), "valid inverse endpoint")
        return True
    require(state in ("IU0", "IU1") and head == width,
            "nonimage did not stop at sign guard")
    require(tape[head] != ("S1" if state == "IU0" else "S0"),
            "inverse stopped on a valid sign symbol")
    return False


def check_round_trips(table):
    exhaustive = translated = transitions = 0
    for width in range(2, 11):
        lower, upper = signed_bounds(width)
        for x in range(lower, upper + 1):
            for coin in (0, 1):
                transitions += round_trip(table, x, width, coin, 0)
                exhaustive += 1
    for width in (16, 64, 257, 1024, MAX_WIDTH):
        lower, upper = signed_bounds(width)
        for x in (lower, lower + 1, -2, -1, 0, 1, upper - 1, upper):
            for coin in (0, 1):
                for origin in (1, 2, 4):
                    steps = round_trip(table, x, width, coin, origin)
                    if x == 0:
                        require(steps == 2 * (4 * width + 1), "worst-case witness")
                    transitions += steps
                    translated += 1
    return exhaustive, translated, transitions


def check_inverse_boundary(table):
    accepted = rejected = 0
    for width in range(2, 9):
        lower, upper = signed_bounds(width)
        for y in range(lower, upper + 1):
            for parity in (0, 1):
                for coin in (0, 1):
                    if inverse_boundary(table, width, y, parity, coin):
                        accepted += 1
                    else:
                        rejected += 1
    return accepted, rejected


def check_controls(table):
    flipped_coin = {(state, read, 1 - coin): row
                    for (state, read, coin), row in table.items()}
    missing_guard = table | {("IU0", "S0", 0): ("IB", "S0", -1)}
    excursion = table | {("F0", "P0", 0): ("FS", "P0", -1)}
    collision = table | {("FR", "P1", 1): ("FH", "P1", 0)}
    controls = (
        ("forward endpoint", round_trip, (flipped_coin, 1, 3, 0, 0)),
        ("nonimage did not stop at sign guard", inverse_boundary,
         (missing_guard, 2, -2, 0, 0)),
        ("exterior head excursion", round_trip, (excursion, 0, 3, 0, 2)),
        ("ambiguous predecessor row", check_local_inverse, (collision,)),
        ("ambiguous incoming head movement", check_local_inverse, (excursion,)),
    )
    for message, check, arguments in controls:
        try:
            check(*arguments)
        except ValueError as error:
            require(str(error) == message, f"wrong failure reason: {error}")
        else:
            raise ValueError(f"control failed to reject: {message}")
    return len(controls)


def main():
    table = load_table()
    check_local_inverse(table)
    exhaustive, translated, transitions = check_round_trips(table)
    accepted, rejected = check_inverse_boundary(table)
    controls = check_controls(table)
    print(json.dumps({
        "status": "PASS_FUSED_NEGATIVE_HALF_TAPE",
        "rows": len(table),
        "exhaustive_round_trips": exhaustive,
        "translated_round_trips": translated,
        "round_trip_transitions": transitions,
        "inverse_images": accepted,
        "inverse_nonimages": rejected,
        "rejecting_controls": controls,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
