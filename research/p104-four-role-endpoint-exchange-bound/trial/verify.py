"""Independently replay either prefix arm on all exact raw cuts."""
from argparse import ArgumentParser
from fractions import Fraction as Q
from hashlib import sha256
from json import dumps
from pathlib import Path
from runpy import run_path
from signal import alarm

SCOPE = run_path(str(Path(__file__).with_name("scope.py")))


def forward(word, cut_checks, seed):
    n = word["public"]
    owned = {}
    chart = dict(enumerate(word["initial"]))
    # Sparse values are evaluated on one literal input at a time.
    values = dict(seed)
    observed = {}
    last = max(cut_checks)
    for t, event in enumerate(word["program"]):
        if t in cut_checks:
            bank, level = cut_checks[t]
            assert all(chart[r] == level for r in bank)
            observed[t] = [values.get(r, Q(0)) for r in bank]
        if t == last:
            return observed
        op, d, *arg = event
        if op == "INIT":
            assert d >= n and d not in owned and d not in chart
            owned[d] = True
            chart[d] = arg[0]
            values.pop(d, None)
            continue
        if op == "CLEAR":
            assert d >= n and d in owned and chart[d] == arg[0]
            del owned[d], chart[d]
            values.pop(d, None)
            continue
        if op == "MOVE":
            assert chart[d] == arg[0] and arg[2] == (d >= n)
            chart[d] = arg[1]
        elif op == "SCALE":
            assert chart[d] == arg[1]
            if d in values:
                values[d] *= Q(arg[0])
        elif op in ("ADD", "COPY"):
            s, coefficient, level = arg
            assert s != d and chart[d] == chart[s] == level
            if op == "COPY":
                assert owned.get(d) is True and not values.get(d)
            value = values.get(d, 0) + Q(coefficient) * values.get(s, 0)
            if value:
                values[d] = value
            else:
                values.pop(d, None)
        else:
            raise ValueError(f"unknown operation {op}")
        if d in owned:
            owned[d] = False
    raise ValueError("missing frozen cut")


def records(raw, mode):
    doc = SCOPE["load"](raw)
    if mode == "archived":
        assert sha256(raw).hexdigest() == SCOPE["PINS"]["lead/PREFIX.json"]
    else:
        assert (doc["head"], doc["caller"]) == (SCOPE["HEAD"], SCOPE["CALLER"])
    if mode in ("per-case", "archived"):
        rows = doc["rows" if mode == "archived" else "results"]
        return {
            tuple(r["key"]): (
                "excluded", r["proof"]["separating_covector"], r["proof"]["separated_target"]
            ) if r["proof"]["status"] == "exact_rank_exclusion" else ("unresolved", None, None)
            for r in rows
        }, len(rows)
    rows = doc["rows"]
    return {
        tuple(r["key"]): (
            r["decision"], r.get("witness"), r.get("target")
        ) for r in rows
    }, len(rows)


def main():
    assert __debug__
    p = ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("per-case", "shared", "archived"))
    p.add_argument("receipt", type=Path)
    args = p.parse_args()
    SCOPE["start"]()
    keys, cuts, word = SCOPE["inputs"](archived=args.mode == "archived")
    raw = args.receipt.read_bytes()
    expected, rows_count = records(raw, args.mode)
    assert len(expected) == rows_count
    assert set(expected).issubset(keys)
    if args.mode in ("shared", "archived"):
        assert set(expected) == set(keys)
    result = []
    capped = False
    try:
        for key in keys:
            decision, witness, target = expected.get(key, ("unresolved", None, None))
            if witness is None:
                assert decision == "unresolved"
                result.append({"key": key, "decision": "unresolved", "raw_cuts": 0})
                continue
            x = {int(r): Q(v) for r,v in witness.items()}
            assert x and all(0 <= r < word["public"] and v for r,v in x.items())
            d = x.get(key[0], 0) - x.get(key[1], 0)
            assert d and d == Q(target)
            lo, hi = cuts[key]
            obs = forward(word, {t: (key[:4], key[4]) for t in range(lo, hi+1)}, x)
            assert len(obs) == hi - lo + 1
            zeros = sum(not any(v) for v in obs.values())
            if decision == "excluded":
                assert zeros == len(obs)
            else:
                assert decision == "unresolved" and any(obs[hi])
            result.append({"key": key, "decision": decision, "raw_cuts": len(obs),
                           "zero_raw_cuts": zeros, "at_representative": list(map(str, obs[hi])),
                           "target": str(d)})
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    result.extend({"key": k, "decision": "unresolved", "raw_cuts": 0} for k in keys[len(result):])
    print(dumps({
        "head": SCOPE["HEAD"], "caller": SCOPE["CALLER"], "mode": args.mode,
        "input_receipt_sha256": sha256(raw).hexdigest(), "pins": SCOPE["PINS"],
        "cap_seconds": SCOPE["CAP"], "cap_reached": capped,
        "raw_cuts_checked": sum(r["raw_cuts"] for r in result),
        "rows": result,
    }, indent=2, sort_keys=True))
    if capped:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
