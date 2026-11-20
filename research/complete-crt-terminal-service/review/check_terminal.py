"""Independent raw-character-array interpreter for the literal CRT terminal.

The only symbol imported from the implementation is compile_terminal.
No author Port, execute, fixture, Entry, Word, relocation or digest is used.
Prepared for Jerry Chen / CubeJerry with OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import json
import sys

HERE = Path(__file__).resolve().parent
TOKENS = ("0", "1", "L", "R", "_", "5", "6", "7", "8", "9", "10", "11", "12", "13")
CHARS = tuple("01LR_56789abcd")
TO_CHAR = dict(zip(TOKENS, CHARS))
TO_TOKEN = dict(zip(CHARS, TOKENS))
BASE = 1435098


def require(condition, message):
    if not condition:
        raise ValueError(message)


class WindowError(ValueError):
    pass


def fingerprint(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def graph_scan(code, roles, base=0):
    addressed, written, targets = set(), set(), []
    census = Counter()
    for local, row in enumerate(code):
        op = row[0]
        census[op] += 1
        require(op in ("R", "W", "M", "J", "H"), "nonliteral graph opcode")
        if op in ("R", "W", "M"):
            require(len(row) == 3 and type(row[1]) is int and 0 <= row[1] < roles,
                    "fixed role operand")
            addressed.add(row[1])
        if op == "R":
            require(set(row[2]) == set(TOKENS), "complete fixed alphabet branch")
            targets.extend(row[2].values())
        elif op == "W":
            require(row[2] in TOKENS, "literal write symbol")
            written.add(row[1])
        elif op == "M":
            require(type(row[2]) is int and row[2] in (-1, 1), "unit head movement")
        elif op == "J":
            require(len(row) == 2, "jump arity")
            targets.append(row[1])
        else:
            require(len(row) == 2 and row[1] in ("CLOSED", "NUMERICAL_CLOSED", "REJECTED"),
                    "finite terminal tag")
        if op in ("W", "M"):
            require(local + 1 < len(code), "fallthrough leaves graph")
    require(all(type(q) is int and base <= q < base + len(code) for q in targets),
            "branch target outside suffix")
    require(addressed == set(range(8, roles)), "complete addressed role set")
    require(not (addressed & set(range(8))), "protected role addressed")
    return {"states": len(code), "roles": roles, "addressed_roles": sorted(addressed),
            "written_roles": sorted(written), "static_opcodes": dict(sorted(census.items())),
            "target_min": min(targets), "target_max": max(targets), "sha256": fingerprint(code)}


def shift_targets(code, offset):
    # Independent relocation. No prefix is generated or allocated.
    result = []
    for row in code:
        if row[0] == "R":
            result.append(("R", row[1], {symbol: target + offset for symbol, target in row[2].items()}))
        elif row[0] == "J":
            result.append(("J", row[1] + offset))
        else:
            result.append(row)
    return tuple(result)


def run_raw(code, cells, heads, role_count, base=0):
    """All state is raw character arrays, integers, and a literal program counter."""
    require(len(cells) == len(heads) and len(cells) >= role_count, "complete physical context")
    require(len({id(row) for row in cells}) == len(cells), "distinct supplied physical arrays")
    backing = tuple(map(id, cells))
    capacities = tuple(map(len, cells))
    intervals = [[head, head] for head in heads]
    touched = set()
    counts = {op: 0 for op in ("R", "W", "M", "J", "H")}
    trace = sha256()
    pc, steps = base, 0
    while True:
        require(base <= pc < base + len(code), "execution escaped terminal suffix")
        row = code[pc - base]
        op = row[0]
        steps += 1
        require(steps <= 1000000, "independent watchdog")
        counts[op] += 1
        trace.update((str(pc - base) + ":" + op + ";").encode())
        if op in ("R", "W", "M"):
            role = row[1]
            require(type(role) is int and 0 <= role < role_count, "dynamic role escape")
            position = heads[role]
            if not 0 <= position < len(cells[role]):
                raise WindowError("unbacked current cell")
            touched.add(role)
            trace.update((str(role) + ":" + str(position) + ":" + cells[role][position] + ";").encode())
            if op == "R":
                pc = row[2][TO_TOKEN[cells[role][position]]]
            elif op == "W":
                cells[role][position] = TO_CHAR[row[2]]
                pc += 1
            else:
                destination = position + row[2]
                if not 0 <= destination < len(cells[role]):
                    raise WindowError("missing supplied destination cell on role " + str(role))
                heads[role] = destination
                intervals[role][0] = min(intervals[role][0], destination)
                intervals[role][1] = max(intervals[role][1], destination)
                pc += 1
        elif op == "J":
            pc = row[1]
        elif op == "H":
            require(backing == tuple(map(id, cells)) and capacities == tuple(map(len, cells)),
                    "backing identity/capacity changed")
            return {"status": row[1], "instructions": steps, "opcodes": counts,
                    "touched_roles": sorted(touched), "intervals": intervals,
                    "normalized_trace_sha256": trace.hexdigest()}
        else:
            raise ValueError("unexpected interpreter opcode")


def raw_fixture(p, lengths, variant=0, free_records=56):
    # Fixture preparation uses only raw characters and integer coordinates.
    cells, heads = [], []
    for role in range(76):
        if role < 8 or role >= 73:
            capacity = p + 17 + 3 * role + variant
            row = [CHARS[(j * 5 + role + variant) % len(CHARS)] for j in range(capacity)]
            head = 0 if role % 3 == 0 else capacity - 1 if role % 3 == 1 else (7 * role + p) % capacity
            if head == 1:
                head = 2
        elif role < 64:
            capacity = p + 2 + 3 * role + (p + variant + role) % 11
            row, head = ["L"] + ["_"] * (capacity - 1), 1
        elif role < 68:
            row, head = ["_"] * (8 + 5 * (role - 64) + variant), 0
        elif role == 68:
            row = ["L"] + ["0"] * p + ["R"] + ["_"] * (37 + variant + p % 7)
            head = 1
        elif role == 69:
            available = list(range(64 - free_records, 64))
            rotation = (variant * 13 + p) % len(available)
            available = available[rotation:] + available[:rotation]
            if variant % 2:
                available.reverse()
            row = ["L"] + ["1" if slot & (1 << bit) else "0"
                             for slot in available for bit in range(6)] + ["R"]
            row += ["_"] * (379 + variant - len(row))
            head = 0
        else:
            n = lengths[role - 70]
            alphabet = [char for char in CHARS if char not in ("L", "_")]
            row = ["L"] + [alphabet[(j + role + variant) % len(alphabet)] for j in range(n)]
            row += ["_"] * (1 + 19 * (role - 69) + p % 13 + variant)
            head = 1
        cells.append(row)
        heads.append(head)
    if free_records == 55:
        cells[8][1:p + 2] = ["1"] * p + ["R"]
    return cells, heads


def snapshot(cells, heads):
    return tuple(map(id, cells)), tuple(tuple(row) for row in cells), tuple(heads)


def check_complete(cells, heads, old):
    require(tuple(map(id, cells)) == old[0], "physical owner identities")
    require(tuple(map(len, cells)) == tuple(map(len, old[1])), "historical backing was refunded")
    protected = (*range(8), 73, 74, 75)
    require(all(tuple(cells[i]) == old[1][i] and heads[i] == old[2][i] for i in protected),
            "dirty protected owner/head changed")
    require(all(all(char == "_" for char in cells[i]) for i in range(8, 73)),
            "owned history not completely blank")
    require(all(heads[i] == (0 if i in (64, 65, 66, 67, 69) else 1) for i in range(8, 73)),
            "terminal ready head not restored")


def expected_price(p, lengths, partial=False):
    u = p if partial else p + sum(lengths)
    return {"R": (839 if partial else 848) + 2 * u,
            "W": (396 if partial else 399) + u,
            "M": (1662 if partial else 1680) + 2 * u,
            "J": 2 * u, "H": 1}


def positive_cases(code, shifted):
    receipts = []
    for p in (4, 8, 23, 128, 1024):
        patterns = [(0, 0, 0), (1, 2, 3), (17, 31, 5), (p + 5, 2 * p + 3, p // 2 + 11)]
        for variant, lengths in enumerate(patterns):
            results, outcomes = [], []
            for graph, base in ((code, 0), (shifted, BASE)):
                cells, heads = raw_fixture(p, lengths, variant)
                old = snapshot(cells, heads)
                got = run_raw(graph, cells, heads, 73, base)
                require(got["status"] == "CLOSED", "terminal failed on admitted raw fixture")
                require(got["opcodes"] == expected_price(p, lengths), "exact independent opcode price")
                require(got["instructions"] == 2928 + 7 * (p + sum(lengths)), "exact total price")
                check_complete(cells, heads, old)
                expected_ranges = [[old[2][i], old[2][i]] for i in range(76)]
                for i in range(8, 64): expected_ranges[i] = [0, 1]
                for i in range(64, 68): expected_ranges[i] = [0, 7]
                expected_ranges[68], expected_ranges[69] = [0, p + 1], [0, 337]
                for j, n in enumerate(lengths): expected_ranges[70 + j] = [0, n + 1]
                require(got["intervals"] == expected_ranges and got["touched_roles"] == list(range(8, 73)),
                        "exact footprint, full head returns and protected framing")
                results.append(got)
                outcomes.append((cells, heads))
            require(results[0] == results[1] and outcomes[0] == outcomes[1], "independent relocated execution differs")
            receipts.append({"P": p, "record_lengths": list(lengths), "variant": variant,
                             "opcodes": results[0]["opcodes"], "instructions": results[0]["instructions"],
                             "retained_capacities": list(map(len, outcomes[0][0])),
                             "normalized_trace_sha256": results[0]["normalized_trace_sha256"],
                             "local_and_relocated_equal": True})
    return receipts


def controls(code, compile_terminal):
    p, lengths = 23, (19, 7, 31)
    cells, heads = raw_fixture(p, lengths, 2)
    old = snapshot(cells, heads)
    marker_write = max(i for i, row in enumerate(code) if row == ("W", 70, "_"))
    mutant = list(code)
    mutant[marker_write] = ("J", marker_write + 1)
    got = run_raw(tuple(mutant), cells, heads, 73)
    need_counts = expected_price(p, lengths)
    need_counts["W"] -= 1
    need_counts["J"] += 1
    require(got["status"] == "CLOSED" and got["opcodes"] == need_counts and cells[70][0] == "L",
            "returning omitted-marker-write control")
    try:
        check_complete(cells, heads, old)
    except ValueError as exc:
        require(str(exc) == "owned history not completely blank", "unexpected mutation failure")
    else:
        raise ValueError("returning mutation escaped independent postcondition")

    cells, heads = raw_fixture(8, (7, 3, 5), 1)
    cells[70] = cells[70][:8]  # L plus seven body characters; no first blank.
    identity_before, capacity_before = id(cells[70]), len(cells[70])
    try:
        run_raw(code, cells, heads, 73)
    except WindowError as exc:
        require("role 70" in str(exc), "unexpected window failure")
    else:
        raise ValueError("missing first blank silently granted")
    require(id(cells[70]) == identity_before and len(cells[70]) == capacity_before,
            "missing-window case allocated a cell")

    cells, heads = raw_fixture(128, (5, 11, 17), 3, free_records=55)
    old = snapshot(cells, heads)
    got_live = run_raw(code, cells, heads, 73)
    require(got_live["status"] == "REJECTED" and got_live["opcodes"] ==
            {"R": 364, "W": 0, "M": 387, "J": 0, "H": 1}, "read-only live-slot rejection")
    require(tuple(tuple(row) for row in cells) == old[1] and tuple(map(id, cells)) == old[0],
            "live-slot rejection wrote or replaced a backing")

    small, metadata = compile_terminal(False)
    partial_scan = graph_scan(small, 70)
    require(len(small) == 2904 and metadata["roles"] == 70, "fixed-70 graph shape")
    cells, heads = raw_fixture(p, lengths, 1)
    old = snapshot(cells, heads)
    partial = run_raw(small, cells, heads, 70)
    require(partial["status"] == "NUMERICAL_CLOSED" and partial["opcodes"] == expected_price(p, lengths, True),
            "fixed-70 partial price")
    require(all(tuple(cells[i]) == old[1][i] and heads[i] == old[2][i] and cells[i][0] == "L"
                for i in range(70, 73)), "fixed-70 footprint did not preserve out-of-binding records")
    return {"omitted_record_marker_write": {"state": marker_write, "returns_closed": True,
                                              "complete_postcondition_rejects": True},
            "missing_backed_first_blank": {"role": 70, "supplied_cells": 8, "rejected_without_grant": True},
            "live_owned_slot": {"free_records": 55, "status": got_live["status"],
                                "opcodes": got_live["opcodes"], "contents_unchanged": True},
            "fixed_70_obstruction": {"graph": partial_scan, "status": partial["status"],
                                     "opcodes": partial["opcodes"], "all_three_record_owners_unchanged": True}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--terminal", required=True, type=Path)
    parser.add_argument("--expected", type=Path, default=HERE / "EXPECTED.json")
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    path = args.terminal.resolve()
    require(path.name == "terminal.py", "explicit terminal.py source")
    sys.path.insert(0, str(path.parent))
    from terminal import compile_terminal  # Sole implementation import.
    require(Path(compile_terminal.__code__.co_filename).resolve() == path, "wrong compiler imported")
    code, metadata = compile_terminal()
    original = graph_scan(code, 73)
    require(len(code) == 2949 and metadata["roles"] == 73 and metadata["labels"]["TERMINAL"] == 0,
            "frozen terminal graph shape")
    require(original["sha256"] == "f060e7097028921bda8945724d0b9668cdc20e9d6552d65215a925ee5bd78914"
            == metadata["sha256"], "canonical graph fingerprint")
    shifted = shift_targets(code, BASE)
    relocated = graph_scan(shifted, 73, BASE)
    packets = positive_cases(code, shifted)
    result = {"status": "PASS_INDEPENDENT_RAW_CRT_TERMINAL", "source_sha256": sha256(path.read_bytes()).hexdigest(),
              "alphabet_renaming": dict(zip(TOKENS, CHARS)), "graph": original,
              "relocated_graph": relocated, "relocation_base": BASE,
              "physical_context_owners": 76, "positive_packets": len(packets),
              "terminal_executions": 2 * len(packets), "cases": packets,
              "total_positive_instructions": 2 * sum(row["instructions"] for row in packets),
              "controls": controls(code, compile_terminal),
              "scope": "Independent raw-character/head interpreter and complete terminal postconditions; no author executor, Entry/Word fixtures or million-state prefix reconstruction."}
    if not args.record:
        require(result == json.loads(args.expected.read_text()), "frozen independent receipt differs")
    print(json.dumps(result, indent=2, sort_keys=True))
    if not args.record:
        print("PASS_INDEPENDENT_RAW_CRT_TERMINAL")


if __name__ == "__main__":
    main()
