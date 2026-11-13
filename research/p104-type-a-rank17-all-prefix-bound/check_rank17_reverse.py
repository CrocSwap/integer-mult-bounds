"""Census all literal Type A rank-17 root cuts with the pinned inverse engine."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from time import perf_counter

CALLER = "07a76c5e2738882c0cb322278e56f6cae3c9885d"
ROOTS = {7: (7, 8), 10: (9, 10), 25: (7, 8), 28: (9, 10)}
PRIOR_CUTS = {10: {1743, 1744}, 28: {1767, 1768}}
PINS = {
    "inputs/7113-CALLER.json": "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc",
    "next-root28/7398/inputs/reverse.py": "d763b974585a439472bcaacf0913fc5c8469ea24212545287a3a359526ff51cd",
}
CAP = 30
STAGES = 17
EVENTS = 4783
N = 36
ONE = (Q(1), Q(0))
ZERO_MASK = (0,) * STAGES


def emit(record):
    print(dumps(record, sort_keys=True, indent=2, default=str), flush=True)


def classify(rows, allowed):
    found = set()
    parity = set()
    for row in rows:
        for (phase, powers), coefficient in row.items():
            assert any(coefficient) and 0 <= phase <= 3 and len(powers) == STAGES
            found.add(powers)
            parity.add(phase % 2)
    assert found
    if len(found) == len(parity) == 1:
        (mask,) = found
        if 0 <= min(mask) <= max(mask) <= 1 and sum(mask) == 1:
            stage = mask.index(1) + 1
            if stage in allowed:
                (bit,) = parity
                return "survivor", stage, bit
    if any(sum(mask) != 1 or min(mask) < 0 or max(mask) > 1
           or mask.index(1) + 1 not in allowed for mask in found):
        return "foreign_body", None, None
    if len(found) > 1:
        return "mixed_body", None, None
    assert len(parity) > 1
    return "mixed_parity", None, None


def terms(rows):
    return [[role, phase, [j for j, multiplicity in enumerate(mask, 1) for _ in range(multiplicity)],
             str(a), str(b)] for role, row in enumerate(rows)
            for (phase, mask), (a, b) in sorted(row.items())]


def mask(stages):
    return tuple(int(j in stages) for j in range(1, STAGES + 1))


def controls(engine):
    b7, b8, b10 = map(mask, ((7,), (8,), (10,)))
    assert classify([{(0, b7): ONE}, {(2, b7): (Q(0), Q(1))}], (7, 8)) == ("survivor", 7, 0)
    assert classify([{(1, b8): ONE}, {(3, b8): ONE}], (7, 8)) == ("survivor", 8, 1)
    assert classify([{(0, b7): ONE, (3, b7): ONE}], (7, 8))[0] == "mixed_parity"
    assert classify([{(0, b7): ONE, (2, b8): ONE}], (7, 8))[0] == "mixed_body"
    assert classify([{(0, b10): ONE}], (7, 8))[0] == "foreign_body"
    assert classify([{(0, ZERO_MASK): ONE}], (7, 8))[0] == "foreign_body"
    return engine["control"]() + ["even_single_body", "odd_single_body", "mixed_parity",
                                  "mixed_body", "foreign_body", "zero_body"]


def root_census(root, allowed, tape, kind, undo, record):
    full_mask = mask(allowed)
    assert kind["diagonal"][root] == [-1, 0, *full_mask]
    rows = [{} for _ in range(N)]
    rows[root] = {(3, full_mask): ONE}
    alpha = Q(kind["alpha2"])
    boundaries = range(len(tape), -1, -1)
    for cut in boundaries:
        decision, stage, parity = classify(rows, allowed)
        grouped_decision = ("MIXED_PARITY" if decision == "mixed_parity" else
                            "SURVIVOR" if decision == "survivor" else "FOREIGN_OR_MIXED_BODY")
        record["first_witness"][grouped_decision] = {"cut": cut, "terms": terms(rows)}
        intervals = record["intervals"]
        if intervals and intervals[-1][2] == grouped_decision:
            intervals[-1][0] = cut
        else:
            intervals.append([cut, cut, grouped_decision])
        if decision == "survivor":
            record["survivors"].append({"cut": cut, "first_body_stage": stage, "first_parity": parity})
            key = (stage, parity)
            if key not in record["earliest_term_witness"]:
                record["earliest_term_witness"][key] = None
            record["earliest_term_witness"][key] = {"cut": cut, "terms": terms(rows)}
        if cut in PRIOR_CUTS.get(root, ()):
            record["prior_cuts"][cut] = {"decision": decision, "terms": terms(rows)}
        record["counts"][decision] += 1
        record["last_completed_cut"] = cut
        record["unvisited"] = [0, cut - 1] if cut else None
        if cut:
            undo(rows, tape[cut - 1], alpha)
    assert rows[root] == {(0, ZERO_MASK): ONE}
    assert all(not row for i, row in enumerate(rows) if i != root)
    record["endpoint_recovered"] = True


def public_records(roots):
    for root, record in roots.items():
        yield root, dict(record, survivors=sorted(record["survivors"], key=lambda row: row["cut"]),
                         intervals=list(reversed(record["intervals"])),
                         earliest_term_witness={f"{s}/{p}": w
                                                for (s, p), w in record["earliest_term_witness"].items()})


def main():
    assert __debug__
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("handoff_root", type=Path)
    parser.add_argument("--forward-receipt", type=Path)
    parser.add_argument("--forward-sha256")
    args = parser.parse_args()
    assert (args.forward_receipt is None) == (args.forward_sha256 is None)
    started = perf_counter()
    roots = {
        root: {"last_completed_cut": None, "unvisited": [0, EVENTS], "endpoint_recovered": False,
               "survivors": [], "counts": Counter(), "earliest_term_witness": {}, "prior_cuts": {},
               "first_witness": {}, "intervals": []}
        for root in ROOTS
    }

    def cap(_signal, _frame):
        emit({"status": "UNRESOLVED_CAP", "roots": dict(public_records(roots)),
              "caller_head": CALLER, "pins": PINS, "seconds": perf_counter() - started})
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(CAP)
    raw = {path: (args.handoff_root / path).read_bytes() for path in PINS}
    assert {path: sha256(data).hexdigest() for path, data in raw.items()} == PINS
    caller = loads(raw["inputs/7113-CALLER.json"])
    tape = caller["events"]
    kind = caller["types"]["A"]
    assert (len(tape), caller["stages"], kind["roles"], len(kind["ports"]), kind["offset"]) == (
        EVENTS, STAGES, N, 96, 0)
    exact = {i for i, (phase, imag, *stages) in enumerate(kind["diagonal"])
             if abs(phase) % 2 + 8 * sum(stages) == 17 and imag == 0}
    assert exact == ROOTS.keys()
    engine = run_path(str(args.handoff_root / "next-root28/7398/inputs/reverse.py"))
    checks = controls(engine)
    for root, allowed in ROOTS.items():
        root_census(root, allowed, tape, kind, engine["undo"], roots[root])
        assert sum(roots[root]["counts"].values()) == EVENTS + 1
    output = dict(public_records(roots))
    if args.forward_receipt is not None:
        forward_raw = args.forward_receipt.read_bytes()
        assert sha256(forward_raw).hexdigest() == args.forward_sha256
        forward = loads(forward_raw)["roots"]
        assert {str(k) for k in output} == forward.keys()
        for root, record in output.items():
            earlier = forward[str(root)]
            assert record["survivors"] == earlier["survivors"], root
            assert record["intervals"] == earlier["intervals"], root
            assert record["first_witness"] == earlier["witnesses"], root
            grouped = {"FOREIGN_OR_MIXED_BODY": record["counts"]["foreign_body"] + record["counts"]["mixed_body"],
                       "MIXED_PARITY": record["counts"]["mixed_parity"], "SURVIVOR": record["counts"]["survivor"]}
            assert {k: n for k, n in grouped.items() if n} == earlier["counts"], root
    emit({"status": "PASS_ALL_RANK17_REVERSE_BOUNDARIES", "roots": output, "controls": checks,
          "caller_head": CALLER, "pins": PINS, "events": EVENTS, "boundaries": len(ROOTS) * (EVENTS + 1),
          "forward_sha256": args.forward_sha256, "runner_cap_seconds": CAP,
          "seconds": perf_counter() - started})
    alarm(0)


if __name__ == "__main__":
    main()
