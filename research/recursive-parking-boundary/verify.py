#!/usr/bin/env python3
"""Finite source-bound replay for the all-length proof in README.md.

Finite executions validate the controller and controls, not the universal
quantifiers. --write-result explicitly generates a new receipt. Standard library
only; proof checks remain active under python -O.
"""
import argparse
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import machine as m

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]
SOURCE_DIR = ROOT / "research/machine-transfer-verification/transfer-proof/tapes"


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def source_check():
    data = json.loads((PACKAGE / "SOURCES.json").read_text(encoding="utf-8"))
    pinned = {}
    for record in data["files"]:
        if record["usage"] != "input":
            continue
        digest = sha256((ROOT / record["path"]).read_bytes()).hexdigest()
        m.require(digest == record["sha256"], "source SHA256 mismatch: " + record["path"])
        pinned[record["path"]] = digest
    return pinned


def load_tables():
    texts = ((SOURCE_DIR / "TapeStackPush.lean").read_text(encoding="utf-8"),
             (SOURCE_DIR / "TapeStack.lean").read_text(encoding="utf-8"))
    push = m.parse_instruction_table(texts[0], m.PUSH_MODES, ("source",), 2)
    pop = m.parse_instruction_table(texts[1], m.POP_MODES, ("park", "temp", "out"), 3)
    for key, value in push.items():
        m.require(value == m.reference_push(*key), "push table differs from independent rules")
    for key, value in pop.items():
        m.require(value == m.reference_pop(*key), "pop table differs from independent rules")
    rows = [[list(key), value] for table in (push, pop) for key, value in sorted(table.items())]
    return push, pop, {"push_entries": len(push), "pop_entries": len(pop),
                       "sha256": sha256(canonical(rows)).hexdigest()}


def require_rejected(action, message):
    try:
        action()
    except ValueError:
        return
    raise ValueError("control was not rejected: " + message)


def payloads(length):
    return product(m.BIT, repeat=length)


def blank_work(work):
    m.require(work.io.bits() == () and work.temporary.bits() == (), "unclean wrapper exit")


def check_primitive_runs(push, pop):
    runs, digest = 0, sha256()
    ancestors = [a for length in range(3) for a in product(m.SYMBOLS, repeat=length)]
    for length in range(7):
        for bits in payloads(length):
            for ancestor in ancestors:
                for origin in (-3, 0, 7):
                    source, park = m.Tape.marked(bits), m.Tape.stack(ancestor, origin)
                    temporary = m.Tape.marked()
                    initial = park.snapshot()
                    pushed = m.run_table(push, "copy", [source, park], (0,))
                    m.require(pushed == 2 * length + 2, "push count")
                    m.require(source.bits() == (), "push did not erase/reset source")
                    m.require(min(park.visits) >= origin, "push visited ancestor")
                    popped = m.run_table(pop, "enterDelimiter", [park, temporary, source], (0, 1, 2))
                    m.require(popped == 3 * length + 5, "pop count")
                    m.require(source.bits() == bits, "round trip changed stream order")
                    m.require(temporary.bits() == (), "pop did not clean temporary")
                    m.require(park.snapshot() == initial, "round trip changed parking frame")
                    m.require(min(park.visits) >= origin - 1, "pop read below entry delimiter")
                    m.require(min(park.writes) >= origin, "pop wrote entry delimiter/ancestor")
                    digest.update(canonical([length, bits, ancestor, origin, pushed, popped]))
                    runs += 1
    return {"runs": runs, "payload_lengths": [0, 6], "ancestor_lengths": [0, 2],
            "stack_origins": [-3, 0, 7], "trace_sha256": digest.hexdigest()}


def verify_boundary(work, active, push, pop, child=m.flip_child):
    before = [t.bits() for t in work.roles]
    parking = work.parking.snapshot()
    origin = work.parking.head
    access_start, write_start = len(work.parking.visits), len(work.parking.writes)
    actual = m.boundary(work, active, child, push, pop)
    expected = list(before)
    expected[active] = tuple(m.ONE if b == m.ZERO else m.ZERO for b in before[active])
    m.require([t.bits() for t in work.roles] == expected, "wrong boundary output")
    m.require(work.parking.snapshot() == parking, "boundary parking mismatch")
    blank_work(work)
    m.require(actual["total"] == m.invoice([len(x) for x in before], active), "wrong invoice")
    m.require(actual["dispatch"] == 2 * len(before) + 1, "wrong dispatch count")
    visits, writes = work.parking.visits[access_start:], work.parking.writes[write_start:]
    m.require(min(visits) >= origin - 1, "boundary accessed ancestor")
    m.require(min(writes) >= origin, "boundary wrote entry delimiter/ancestor")
    return actual


def check_boundaries(push, pop):
    runs, digest, largest = 0, sha256(), 0
    ancestors = [(), (m.SEP, m.ZERO, m.ONE, m.BLANK),
                 (m.ONE,) * 3, (m.BLANK, m.SEP)]
    domains = [(2, 5), (3, 3), (4, 2)]
    for width, max_length in domains:
        for length in range(max_length + 1):
            for combined in payloads(width * length):
                bits = [combined[i * length:(i + 1) * length] for i in range(width)]
                for active in range(width):
                    for j, ancestor in enumerate(ancestors):
                        work = m.Workspace([m.Tape.marked(x) for x in bits],
                                           m.Tape.stack(ancestor, j - 1))
                        count = verify_boundary(work, active, push, pop)
                        volume = width * length
                        if volume:
                            m.require(count["total"] <= 14 * volume, "linear equal-role bound")
                        largest = max(largest, count["total"])
                        digest.update(canonical([width, length, combined, active, j, count]))
                        runs += 1
    unequal_runs = 0
    for lengths in ((0, 1), (1, 2), (2, 1, 0), (3, 2, 1, 0)):
        for combined in payloads(sum(lengths)):
            offset, bits = 0, []
            for length in lengths:
                bits.append(combined[offset:offset + length])
                offset += length
            for active in range(len(lengths)):
                work = m.Workspace([m.Tape.marked(x) for x in bits], m.Tape.stack(m.BIT))
                count = verify_boundary(work, active, push, pop)
                digest.update(canonical([lengths, combined, active, count]))
                unequal_runs += 1
    return {"equal_runs": runs, "equal_domains_W_max_n": [list(pair) for pair in domains],
            "unequal_runs": unequal_runs, "largest_equal_wrapper_steps": largest,
            "trace_sha256": digest.hexdigest()}


def fixture_load(tape, bits):
    """Test-only abstract row routing, excluded from physical/cost claims."""
    fresh = m.Tape.marked(bits)
    tape.cells, tape.head = fresh.cells, fresh.head


def nested_child(depth, push, pop, records):
    def run(work):
        if depth == 0:
            m.flip_child(work)
            return
        incoming = work.io.bits()
        width = len(work.roles)
        m.require(len(incoming) % width == 0, "fixture row divisibility")
        # Abstract split/merge shims supply the assumed row-routing contract.
        fixture_load(work.io, ())
        for i, tape in enumerate(work.roles):
            fixture_load(tape, incoming[i::width])
        for active in range(width):
            child_size = len(work.roles[active].bits())
            expected = m.invoice([child_size] * width, active)
            count = verify_boundary(work, active, push, pop,
                                    nested_child(depth - 1, push, pop, records))
            records.append((width, depth, child_size, expected, count["total"]))
        rows = [t.bits() for t in work.roles]
        merged = tuple(b for group in zip(*rows) for b in group)
        for tape in work.roles:
            fixture_load(tape, ())
        fixture_load(work.io, merged)
    return run


def check_nested(push, pop):
    runs, records, digest = 0, [], sha256()
    for width in (2, 3, 4):
        for depth in range(5):
            for leaf_length in (0, 1, 2):
                length = width ** depth * leaf_length
                for ancestor_length in (0, 257):
                    ancestor = tuple(m.SYMBOLS[(j * j + 3 * j + 1) % 4]
                                     for j in range(ancestor_length))
                    bits = [tuple(m.BIT[(j * j + j // 3 + i) % 2] for j in range(length))
                            for i in range(width)]
                    work = m.Workspace([m.Tape.marked(x) for x in bits],
                                       m.Tape.stack(ancestor, -11))
                    count = verify_boundary(work, width - 1, push, pop,
                                            nested_child(depth, push, pop, records))
                    digest.update(canonical([width, depth, leaf_length, ancestor_length, count]))
                    runs += 1
    m.require(all(expected == actual for _, _, _, expected, actual in records), "nested invoice mismatch")
    return {"outer_runs": runs, "nested_boundaries": len(records),
            "depths": [0, 4], "ancestor_lengths": [0, 257],
            "nested_wrapper_steps": sum(x[-1] for x in records),
            "trace_sha256": digest.hexdigest(),
            "row_routing": "abstract fixture shims; excluded from physical/cost claim"}


def ancestor_scan_child(work):
    """One fixed controller preserves endpoints while scanning the whole stack.

    This adverse witness uses a contiguous-stack fixture and restores the exact
    head and all contents. It is not part of the proposed scheduler.
    """
    mode, steps = "start", 0
    while mode != "done":
        symbol = work.parking.read()
        if mode == "start":
            action, mode = (None, -1), "left"
        elif mode == "left":
            action, mode = ((None, 1), "right") if symbol == m.BLANK else ((None, -1), mode)
        elif mode == "right":
            action, mode = (m.STAY, "done") if symbol == m.BLANK else ((None, 1), mode)
        work.parking.perform(action)
        steps += 1
    return steps


def check_controls(push, pop):
    passed = []
    for file, modes, args, arity, old, new, reference in (
        ("TapeStackPush.lean", m.PUSH_MODES, ("source",), 2,
         "⟨some (.bit b), .right⟩", "⟨some .blank, .right⟩", m.reference_push),
        ("TapeStack.lean", m.POP_MODES, ("park", "temp", "out"), 3,
         "⟨some .blank, .left⟩", "⟨some .blank, .right⟩", m.reference_pop),
    ):
        text = (SOURCE_DIR / file).read_text(encoding="utf-8")
        prefix, tail = text.split("def instruction (", 1)
        m.require(old in tail, "mutation missed source instruction")
        mutated = prefix + "def instruction (" + tail.replace(old, new, 1)
        table = m.parse_instruction_table(mutated, modes, args, arity)
        require_rejected(lambda: m.require(all(value == reference(*key) for key, value in table.items()),
                                          "source table mutation"), file)
        passed.append("source_table_mutation_" + file)

    def fixture():
        return m.Workspace([m.Tape.marked(x) for x in ("01", "10", "11")], m.Tape.stack("101"))

    def bad_head(work):
        work.parking.perform((None, 1))

    def bad_bytes(work):
        work.parking.cells[work.parking.head - 2] = m.SEP

    def bad_temp(work):
        work.temporary.cells[0] = m.ONE

    def bad_role(work):
        work.roles[1].cells[0] = m.ONE

    def bad_length(work):
        work.io.cells[len(work.io.bits())] = m.ZERO

    def bad_io_head(work):
        work.io.perform((None, 1))

    for name, child in (("child_parking_head", bad_head), ("child_parked_bytes", bad_bytes),
                        ("child_temporary_cleanup", bad_temp), ("child_role_cleanup", bad_role),
                        ("child_length", bad_length), ("child_io_head", bad_io_head)):
        require_rejected(lambda child=child: m.boundary(fixture(), 0, child, push, pop), name)
        passed.append(name)

    # The drift also breaks the unguarded execution, not just a Python guard.
    work = fixture()
    before = work.parking.snapshot(), [t.bits() for t in work.roles]
    m.boundary(work, 0, bad_head, push, pop, check_contract=False)
    require_rejected(lambda: m.require((work.parking.snapshot(), [t.bits() for t in work.roles]) == before,
                                      "unchecked head drift changed output"), "unchecked head drift")
    passed.append("unchecked_head_drift_breaks_restore")

    work = fixture()
    expected = [t.bits() for t in work.roles]
    m.boundary(work, 0, lambda _: None, push, pop, restore_in_push_order=True)
    require_rejected(lambda: m.require([t.bits() for t in work.roles] == expected, "wrong restore order"),
                     "wrong restore order")
    passed.append("wrong_role_restore_order")

    actual = m.boundary(fixture(), 0, lambda _: None, push, pop)
    require_rejected(lambda: m.require(actual["primitive"] == m.invoice([2] * 3, 0), "unpaid dispatch"),
                     "unpaid dispatch")
    passed.append("omitted_dispatch_charge")

    lengths, active = [1, 2], 0
    require_rejected(lambda: m.require(2 * lengths[active] == sum(lengths), "unequal child volume"),
                     "unequal child volume")
    passed.append("unequal_roles_do_not_give_V_over_W")

    scans = []
    for ancestor_length in (0, 7, 63):
        work = m.Workspace([m.Tape.marked("0"), m.Tape.marked("1")],
                           m.Tape.stack((m.ONE,) * ancestor_length))
        observed = {}

        def scan(work):
            start, origin = len(work.parking.visits), work.parking.head
            observed["steps"] = ancestor_scan_child(work)
            observed["min_offset"] = min(work.parking.visits[start:]) - origin

        before = work.parking.snapshot(), [t.bits() for t in work.roles]
        count = m.boundary(work, 0, scan, push, pop)
        m.require((work.parking.snapshot(), [t.bits() for t in work.roles]) == before,
                  "scan witness did not restore endpoints")
        m.require(count["total"] == 25 and observed["steps"] == 2 * ancestor_length + 9,
                  "scan witness invoice")
        require_rejected(lambda: m.require(observed["min_offset"] >= -1, "ancestor scan"),
                         "endpoint-only locality")
        scans.append({"ancestor_symbols": ancestor_length, "wrapper_steps": count["total"], **observed})
    passed.append("endpoint_preserving_ancestor_scan")
    return {"rejected": passed, "ancestor_scan_witnesses": scans,
            "unequal_volume_witness": {"role_lengths": lengths, "active": active}}


def build_result():
    pins = source_check()
    push, pop, table_result = load_tables()
    return {"status": "PASS_RECURSIVE_PARKING_BOUNDARY", "source_sha256": pins,
            "source_tables": table_result, "primitives": check_primitive_runs(push, pop),
            "boundaries": check_boundaries(push, pop), "nested": check_nested(push, pop),
            "controls": check_controls(push, pop),
            "all_length_invoice": "5*V-n_active+9*W-2 (child execution excluded)",
            "equal_positive_role_bound": "wrapper <= 14*V; child volume V/W",
            "scope": "Written conditional all-length boundary proof plus finite source-bound replay; no Lean rerun or full compiler/scheduler theorem."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-result", type=Path)
    args = parser.parse_args()
    result = build_result()
    if args.write_result is not None:
        with args.write_result.open("x", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        expected = json.loads((PACKAGE / "RESULT.json").read_text(encoding="utf-8"))
        m.require(result == expected, "computed receipt differs from RESULT.json")
    print(f"{result['status']}: {result['source_tables']['push_entries'] + result['source_tables']['pop_entries']} source-table entries; "
          f"{result['boundaries']['equal_runs']} equal-role boundaries; "
          f"{result['nested']['nested_boundaries']} nested boundaries; "
          f"{len(result['controls']['rejected'])} controls rejected")


if __name__ == "__main__":
    main()
