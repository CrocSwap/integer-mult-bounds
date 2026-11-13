"""Complete fixed-caller rank-17 productive prefix census."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps, loads
from pathlib import Path
from runpy import run_path
from signal import SIGALRM, alarm, signal
from sys import argv

ROOT = Path(__file__).resolve().parent
ENGINE = ROOT / "7398/engines/forward.py"
ENGINE_SHA = "1043c6cb86af5c3fe348e62e5e7f89c2148e1273f1456382907a1a77a739b0df"
CALLER_SHA = "255d89f38cd45e38e5770f559bc43dc217e989032359768cdc7e8cdfd64b47bc"
ROLES = (7, 10, 25, 28)
ONE = (Q(1), Q(0))
CASE_COUNT = 4 * 4784
CAP = 30


def emit(result):
    print(dumps(result, indent=2, sort_keys=True, default=str), flush=True)


def classify(rows, bodies):
    shapes = {(phase % 2, mask) for row in rows for phase, mask in row}
    assert shapes
    masks = {mask for _, mask in shapes}
    phases = {phase for phase, _ in shapes}
    if len(masks) != 1 or next(iter(masks)) not in {(body,) for body in bodies}:
        return "FOREIGN_OR_MIXED_BODY", None
    if len(phases) != 1:
        return "MIXED_PARITY", None
    return "SURVIVES_NECESSARY_PREFIX", (next(iter(masks))[0], next(iter(phases)))


def census(tape, meta, propagate, roots, active):
    alpha = Q(meta["alpha2"])
    for role in ROLES:
        active["role"], active["cut"] = role, 0
        exponent, sign, *mask = meta["diagonal"][role]
        bodies = tuple(i for i, power in enumerate(mask, 1) if power)
        assert exponent == -1 and sign == 0 and len(bodies) == sum(mask) == 2
        rows = [{} for _ in range(meta["roles"])]
        rows[role] = {(0, ()): ONE}
        record = {"first_stages": bodies, "survivors": [], "counts": Counter(),
                  "classified_boundaries": 0, "intervals": [], "witnesses": {},
                  "endpoint_recovered": False}
        roots[role] = record
        for cut in range(len(tape) + 1):
            active["cut"] = cut
            status, witness = classify(rows, bodies)
            record["counts"][status] += 1
            record["classified_boundaries"] += 1
            if record["intervals"] and record["intervals"][-1][2] == status:
                record["intervals"][-1][1] = cut
            else:
                record["intervals"].append([cut, cut, status])
            if witness:
                first_body, parity = witness
                record["survivors"].append({"cut": cut, "first_body_stage": first_body,
                                            "first_parity": parity})
            if status not in record["witnesses"]:
                record["witnesses"][status] = {"cut": cut, "terms": [
                    (index, phase, stages, a, b) for index, row in enumerate(rows)
                    for (phase, stages), (a, b) in sorted(row.items())]}
            if cut < len(tape):
                propagate(rows, tape[cut], alpha)
        assert rows[role] == {(3, bodies): ONE}
        assert all(not row for index, row in enumerate(rows) if index != role)
        record["endpoint_recovered"] = True
    active.clear()


def main():
    assert __debug__
    roots, active = {}, {}
    def cap(_signal, _frame):
        emit({"status": "CAPPED", "roots": roots, "active": active, "case_count": CASE_COUNT, "runner_cap_seconds": CAP})
        raise SystemExit(124)

    signal(SIGALRM, cap)
    alarm(CAP)
    raw = (Path(argv[1]) / "7113-CALLER.json").read_bytes()
    assert sha256(raw).hexdigest() == CALLER_SHA and sha256(ENGINE.read_bytes()).hexdigest() == ENGINE_SHA
    data = loads(raw)
    tape, meta = data["events"], data["types"]["A"]
    assert len(tape) == 4783 and meta["roles"] == 36 and len(meta["ports"]) == 96
    assert tuple(i for i, row in enumerate(meta["diagonal"]) if sum(row[2:]) == 2) == ROLES
    assert classify([{(1, (9,)): ONE}], (9, 10))[1] == (9, 1)
    assert classify([{(1, (9,)): ONE, (0, (9,)): ONE}], (9, 10))[1] is None
    assert classify([{(0, ()): ONE}], (9, 10))[1] is None
    census(tape, meta, run_path(str(ENGINE))["propagate"], roots, active)
    assert sum(r["classified_boundaries"] for r in roots.values()) == CASE_COUNT
    emit({"status": "EXACT_FIXED_PREFIX_CENSUS", "roots": roots,
          "case_count": CASE_COUNT, "runner_cap_seconds": CAP, "unresolved": [],
          "caller_sha256": CALLER_SHA, "engine_sha256": ENGINE_SHA})
    alarm(0)


if __name__ == "__main__":
    main()
