"""Small exhaustive oracle for the conditional CRT last-Y-bit lowering.

Independent review code; uses complete payload labels, not a machine simulator.
Positions count from the MSB/front.  The final H address bits form the omitted
back suffix; the preceding bit is the last Y bit.  Two front H-bit fields are
arbitrary dirty coordinates.  No production constants are reduced in a claim.
"""
from __future__ import annotations

import json


def bit(value: int, position: int, length: int) -> int:
    return (value >> (length - 1 - position)) & 1


def exchange(value: int, first: int, second: int, length: int) -> int:
    if bit(value, first, length) != bit(value, second, length):
        value ^= (1 << (length - 1 - first)) | (1 << (length - 1 - second))
    return value


def transport_payload(payload: list[int], first: int, second: int, length: int) -> list[int]:
    result = [-1] * len(payload)
    for address, label in enumerate(payload):
        result[exchange(address, first, second, length)] = label
    return result


def source_value(address: int, truth_table: int, y_positions: tuple[int, ...],
                 target: int, length: int) -> int:
    key = 0
    for position in y_positions:
        if position != target:
            key = 2 * key + bit(address, position, length)
    return (truth_table >> key) & 1


def direct(payload: list[int], truth_table: int, y_positions: tuple[int, ...],
           target: int, length: int) -> list[int]:
    result = [-1] * len(payload)
    mask = 1 << (length - 1 - target)
    for address, label in enumerate(payload):
        control = source_value(address, truth_table, y_positions, target, length)
        result[address ^ (mask * control)] = label
    return result


def lowered(payload: list[int], truth_table: int, y_positions: tuple[int, ...],
            target: int, length: int, suffix_width: int,
            *, omit_conjugation: bool = False) -> tuple[list[int], dict[str, int]]:
    last_y = length - suffix_width - 1
    placed = transport_payload(payload, target, last_y, length)
    block_size = 1 << suffix_width
    output = []
    preparations = 0
    for start in range(0, len(placed), 2 * block_size):
        # The evaluator is invoked once for the entire two-block prefix fiber.
        # Target and suffix may be replaced by zero because they are omitted.
        original = start if omit_conjugation else exchange(start, target, last_y, length)
        control = source_value(original, truth_table, y_positions, target, length)
        preparations += 1
        first = placed[start:start + block_size]
        second = placed[start + block_size:start + 2 * block_size]
        if control:
            output.extend(second)
            output.extend(first)
        else:
            output.extend(first)
            output.extend(second)
    restored = transport_payload(output, target, last_y, length)
    return restored, {"preparations": preparations, "buffer_records": block_size,
                      "width_one_exchanges": 0 if target == last_y else 2}


def main() -> None:
    cases = columns = fibers = 0
    lost_transport_witness = None
    last_y_cases = 0
    for suffix_width in (1, 2):
        for y_width in range(1, 5):
            length = 3 * suffix_width + y_width
            positions = tuple(range(2 * suffix_width, length - suffix_width))
            payload = list(range(1 << length))
            for target in positions:
                for table in range(1 << (1 << (y_width - 1))):
                    expected = direct(payload, table, positions, target, length)
                    actual, stats = lowered(payload, table, positions, target, length, suffix_width)
                    if actual != expected:
                        raise RuntimeError("complete dirty-state endpoint mismatch")
                    if stats["preparations"] != 1 << (length - suffix_width - 1):
                        raise RuntimeError("preparation was not charged once per complete fiber")
                    if sorted(actual) != payload:
                        raise RuntimeError("endpoint is not a full permutation")
                    if lowered(actual, table, positions, target, length, suffix_width)[0] != payload:
                        raise RuntimeError("inverse endpoint did not restore complete payload")
                    cases += 1
                    columns += len(payload)
                    fibers += stats["preparations"]
                    if target == positions[-1]:
                        last_y_cases += 1
                        if stats["width_one_exchanges"] != 0:
                            raise RuntimeError("identity last-Y exchange not eliminated")
                    elif lost_transport_witness is None:
                        wrong = lowered(payload, table, positions, target, length, suffix_width,
                                        omit_conjugation=True)[0]
                        if wrong != expected:
                            index = next(i for i, pair in enumerate(zip(wrong, expected))
                                         if pair[0] != pair[1])
                            lost_transport_witness = {
                                "length": length, "suffix_width": suffix_width,
                                "y_width": y_width, "target_physical": target,
                                "table": table, "output_position": index,
                                "expected_label": expected[index], "wrong_label": wrong[index],
                            }
    if lost_transport_witness is None:
        raise RuntimeError("missing-conjugation negative control was not detected")
    print(json.dumps({"status": "PASS", "cases": cases, "columns": columns,
                      "prepared_complete_fibers": fibers,
                      "already_last_y_cases": last_y_cases,
                      "missing_conjugation_control": lost_transport_witness}, sort_keys=True))


if __name__ == "__main__":
    main()
