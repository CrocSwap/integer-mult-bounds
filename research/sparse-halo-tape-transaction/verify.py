#!/usr/bin/env python3
"""Independent destination-first oracle and physical transaction controls.

The oracle, fixture loader, and observers may use ordinary Python arithmetic.
Only tapes.Program is the claimed sequential algorithm. No oracle is called
from that algorithm. Assertions are deliberately not used as acceptance gates.
"""

import argparse
import hashlib
import importlib.util
import itertools
import json
import platform
from pathlib import Path

_spec = importlib.util.spec_from_file_location("halo_tape_program", Path(__file__).with_name("tapes.py"))
_tapes = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_tapes)
Program, Reject, Tape = _tapes.Program, _tapes.Reject, _tapes.Tape


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def bits(value, width):
    if value < 0 or value >= 1 << width:
        raise ValueError("fixture value outside binary field")
    return format(value, f"0{width}b")


def records(text):
    fields = text.split("#")
    require(fields[-1] == "", "missing record terminator")
    require(len(fields) % 2 == 1, "odd record field count")
    return list(zip(fields[0:-1:2], fields[1:-1:2]))


def fixture(ks, ell, a, b, payload_width=8, spectator_width=0):
    length = 1 << ell
    require(0 <= b < a and length > 4 * a, "inadmissible test geometry")
    require(all(k >= 1 for k in ks), "period contains fewer than two cores")
    periods = tuple(1 << (k + ell) for k in ks)
    spectators = range(1 << spectator_width)
    width = spectator_width + sum(k + ell for k in ks)
    local_width = ell + 2
    mask = (1 << payload_width) - 1
    positions = list(itertools.product(spectators, *map(range, periods)))
    index = {position: i for i, position in enumerate(positions)}

    def global_key(position):
        z, *point = position
        return (bits(z, spectator_width) if spectator_width else "") + "".join(
            bits(x, k + ell) for x, k in zip(point, ks)
        )

    payloads = [bits((i * 37 + 11) & mask, payload_width) for i in range(len(positions))]
    source = "".join(value + "#" for value in payloads)
    coordinates = "0" * spectator_width + "&" + "".join(
        "@" + "0" * k + "#" + "0" * ell + ";" for k in ks
    )
    expected_copies = []
    targets = {}
    fanout = {position: 0 for position in positions}
    # This is destination-first interval expansion, independent of source
    # predicates, first-face prefix flags, and suffix odometers in Program.
    for z in spectators:
        for core in itertools.product(*(range(1 << k) for k in ks)):
            for face in range(len(ks)):
                for side in (0, 1):
                    intervals = []
                    for axis in range(len(ks)):
                        if axis < face:
                            intervals.append((a, length - a))
                        elif axis == face:
                            intervals.append((0, a) if side == 0 else (length - a, length))
                        else:
                            intervals.append((0, length))
                    for local in itertools.product(*(range(hi - lo + 2 * b) for lo, hi in intervals)):
                        point = tuple(
                            (c * length + lo - b + off) % period
                            for c, (lo, _), off, period in zip(core, intervals, local, periods)
                        )
                        position = (z, *point)
                        key = (bits(z, spectator_width) if spectator_width else "")
                        key += "".join(bits(c, k) for c, k in zip(core, ks))
                        key += "".join("1" if axis == face else "0" for axis in range(len(ks)))
                        key += str(side)
                        key += "".join(bits(off, local_width) for off in local)
                        key += global_key(position)
                        expected_copies.append((key, payloads[index[position]]))
                        fanout[position] += 1
                    for point_local in itertools.product(*(range(lo, hi) for lo, hi in intervals)):
                        position = (z, *(c * length + x for c, x in zip(core, point_local)))
                        key = global_key(position)
                        require(key not in targets, "destination partition repeated target")
                        targets[key] = bits((index[position] * 19 + 7) & mask, payload_width)
    # Deliberately reverse the input: physical radix must restore global order.
    returns = "".join(key + "#" + value + "#" for key, value in reversed(sorted(targets.items())))
    final = "".join(
        targets.get(global_key(position), "".join("1" if x == "0" else "0" for x in payload)) + "#"
        for position, payload in zip(positions, payloads)
    )
    constants = tuple(bits(x, local_width) for x in (length, a, b))
    return {
        "ks": ks, "ell": ell, "a": a, "b": b, "P": payload_width,
        "spectator_width": spectator_width, "source": source,
        "coordinates": coordinates, "constants": constants, "returns": returns,
        "copies": sorted(expected_copies), "final": final, "targets": targets,
        "M": len(positions), "B": width, "K": 2 * width + 3 * len(ks) + 1,
        "C": len(expected_copies), "Q": len(targets), "fanout": fanout,
    }


def program(case, returns=None):
    return Program(
        case["source"], case["coordinates"], *case["constants"],
        returns=case["returns"] if returns is None else returns,
    )


def totals(machine):
    bill = machine.ledger()
    return {
        "actions": sum(sum(row.get(key, 0) for key in ("read", "write", "move")) for row in bill.values()),
        "moves": sum(row.get("move", 0) for row in bill.values()),
        "retained_cells": sum(row["retained_cells"] for row in bill.values()),
        "roles": len(bill),
    }


def run_case(case):
    machine = program(case)
    require(machine.phase == "input", "wrong phase at entry")
    machine.gather()
    gathered = records(machine.saved.inspect())
    require(sorted(gathered) == case["copies"], "physical gather differs from destination-first oracle")
    dense_and_emit = totals(machine)
    # Include exact zero-copy and wrap behavior, not just total copy counts.
    require(any(n == 0 for n in case["fanout"].values()), "fixture has no center control")
    if case["b"]:
        require(max(case["fanout"].values()) == 2 ** len(case["ks"]), "corner fanout not exercised")
    machine.sort(machine.saved)
    require(records(machine.saved.inspect()) == case["copies"], "physical radix output is not sorted exactly")
    sorted_bill = totals(machine)
    snapshot = machine.saved.inspect()
    machine.core_complement_test_double()
    require(machine.source.inspect() != case["source"], "core control did not mutate source")
    require(machine.saved.inspect() == snapshot, "core mutation contaminated saved copies")
    machine.merge_returns()
    require(machine.final.inspect() == case["final"], "unique return did not preserve core interior")
    before_erase = totals(machine)
    retained = before_erase["retained_cells"]
    machine.erase_work()
    after_erase = totals(machine)
    require(machine.final.inspect() == case["final"], "erasure damaged final output")
    require(after_erase["retained_cells"] >= retained, "erasure falsely reclaimed retained backing")
    require(all(t.inspect() == "" for t in machine.roles if t is not machine.final), "work erasure incomplete")
    return {
        "geometry": {key: case[key] for key in ("ks", "ell", "a", "b", "P", "spectator_width")},
        "M": case["M"], "B": case["B"], "K": case["K"], "C": case["C"], "Q": case["Q"],
        "maximum_fanout": max(case["fanout"].values()),
        "zero_copy_sources": sum(n == 0 for n in case["fanout"].values()),
        "gather": dense_and_emit, "gather_and_sparse_sort": sorted_bill,
        "before_erase": before_erase, "after_erase": after_erase,
        "output_sha256": hashlib.sha256(machine.final.inspect().encode()).hexdigest(),
    }


def expect_reject(action, label):
    try:
        action()
    except Reject:
        return label
    raise RuntimeError("negative control was not rejected: " + label)


def controls(case):
    passed = []
    # These malformed return streams exercise the actual physical merge.
    target_rows = sorted(case["targets"].items())
    def run_bad(rows):
        stream = "".join(key + "#" + value + "#" for key, value in rows)
        machine = program(case, stream)
        machine.gather()
        machine.core_complement_test_double()
        machine.merge_returns()
    passed.append(expect_reject(lambda: run_bad(target_rows[1:]), "missing_target"))
    passed.append(expect_reject(lambda: run_bad(target_rows + target_rows[:1]), "duplicate_target"))
    interior_key = next(bits(i, case["B"]) for i in range(case["M"]) if bits(i, case["B"]) not in case["targets"])
    passed.append(expect_reject(lambda: run_bad(target_rows + [(interior_key, "0" * case["P"])]), "kept_row_return"))
    machine = program(case)
    passed.append(expect_reject(machine.core_complement_test_double, "core_before_copy"))
    passed.append(expect_reject(machine.merge_returns, "return_before_core"))
    passed.append(expect_reject(lambda: machine.source.move(2), "nonunit_head_jump"))
    # Reverse bucket concatenation is a genuine radix mutation, not an oracle
    # perturbation. Duplicate keys additionally check stable payload order.
    sort_machine = program(case)
    sort_machine.saved = Tape("mutant_sort", "10#00#01#01#10#10#00#11#")
    sort_machine.sort(sort_machine.saved)
    require(records(sort_machine.saved.inspect()) == [("00", "11"), ("01", "01"), ("10", "00"), ("10", "10")], "stable radix duplicate-key check")
    mutant = program(case)
    mutant.saved = Tape("mutant_sort", "10#00#01#01#10#10#00#11#")
    mutant.sort(mutant.saved, reverse_buckets=True)
    require(records(mutant.saved.inspect()) != records(sort_machine.saved.inspect()), "reversed-bucket mutation survived")
    passed.append("reversed_bucket_order_detected")
    passed.append("duplicate_key_stability")
    # A stale-copy mutation after a core change has precisely different bytes.
    stale = program(case)
    stale.gather()
    old = stale.saved.inspect()
    stale.core_complement_test_double()
    changed = Program(stale.source.inspect(), case["coordinates"], *case["constants"])
    changed.gather()
    require(changed.saved.inspect() != old, "copy-after-core mutation not detected")
    passed.append("copy_after_core_detected")
    # This static check excludes the test observer convenience call. It is not
    # runtime enforcement of backend privacy; that boundary also needs review.
    require(".inspect(" not in Path(__file__).with_name("tapes.py").read_text().split("class Program:", 1)[1].split("def ledger", 1)[0], "observer leaked into Program")
    passed.append("no_observer_call_in_program")
    return passed


def arithmetic_controls():
    add_mod, compare, step_binary = _tapes.add_mod, _tapes.compare, _tapes.step_binary
    checked = 0
    for width in range(1, 6):
        for a in range(1 << width):
            for b in range(1 << width):
                left, right = Tape("a", bits(a, width)), Tape("b", bits(b, width))
                got = compare(left, right)
                require(got == ("less" if a < b else "greater" if a > b else "equal"), "bit comparison failure")
                add_mod(left, right)
                require(left.inspect() == bits((a + b) % (1 << width), width), "bit addition failure")
                add_mod(left, right, subtract=True)
                require(left.inspect() == bits(a, width), "bit subtraction failure")
                step_binary(left)
                require(left.inspect() == bits((a + 1) % (1 << width), width), "binary step failure")
                step_binary(left, down=True)
                require(left.inspect() == bits(a, width), "binary reverse-step failure")
                checked += 1
    return checked


def source_bindings():
    package = Path(__file__).resolve().parent
    root = package.parents[1]
    sources = json.loads((package / "SOURCES.json").read_text())
    checked = []
    for row in sources["files"]:
        if row["usage"] == "input":
            content = (root / row["path"]).read_bytes()
            require(hashlib.sha256(content).hexdigest() == row["sha256"], "live source SHA256 mismatch: " + row["path"])
            git_blob = hashlib.sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
            require(git_blob == row["git_blob"], "live source Git blob mismatch: " + row["path"])
            checked.append(row["path"])
    return checked


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quick", action="store_true", help="only the first complete fixture")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    cases = [fixture((1,), 4, 2, 1, 8)]
    if not args.quick:
        cases += [fixture((1, 1), 4, 2, 1, 8), fixture((1, 2), 3, 1, 0, 8, 1)]
    result = {
        "status": "PASS", "python": platform.python_version(),
        "source_bindings": source_bindings(),
        "arithmetic_pairs": arithmetic_controls(),
        "fixtures": [run_case(case) for case in cases],
        "controls": controls(cases[0]),
        "claim": "physical gather/sort/return only; numerical halo consumer is an explicit contract; no new kappa",
    }
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(payload)
    print(payload, end="")


if __name__ == "__main__":
    main()
