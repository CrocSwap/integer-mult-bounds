"""Try one previously certified exact direction in one literal sweep."""
from collections import defaultdict
from fractions import Fraction
from functools import cache
from json import dumps
from pathlib import Path
from runpy import run_path
from signal import alarm

SCOPE = run_path(str(Path(__file__).with_name("scope.py")))
Q = cache(Fraction)


def walk(word, keys, rows):
    charts = word["initial"] + [None] * word["owned_fields"]
    n = word["public"]
    x = {int(r): Q(v) for r, v in SCOPE["FIXED"].items()}
    state = [x.get(r, 0) for r in range(len(charts))]
    fresh = set()
    cuts = defaultdict(list)
    for k in keys:
        cuts[k[-1]].append(k)
    end = max(cuts)
    tape = word["program"]
    for t in range(end + 1):
        for k in cuts.get(t, ()):
            assert all(charts[r] == k[4] for r in k[:4])
            y = [state[r] for r in k[:4]]
            target = x.get(k[0], 0) - x.get(k[1], 0)
            assert target == -1
            rows.append({
                "key": k, "decision": "unresolved" if any(y) else "excluded",
                "witness": SCOPE["FIXED"], "rows": list(map(str, y)),
                "target": str(target),
            })
        if t == end:
            break
        op, d, *args = tape[t]
        if op == "MOVE":
            a, b, owned = args
            assert charts[d] == a and owned == (d >= n)
            charts[d] = b
        elif op == "INIT":
            assert d >= n and charts[d] is None
            charts[d], state[d] = args[0], 0
            fresh.add(d)
            continue
        elif op == "CLEAR":
            assert d >= n and charts[d] == args[0]
            charts[d], state[d] = None, 0
        elif op == "SCALE":
            assert charts[d] == args[1]
            state[d] *= Q(args[0])
        else:
            s, coef, chart = args
            assert op in ("COPY", "ADD") and s != d and charts[d] == charts[s] == chart
            if op == "COPY":
                assert d >= n and d in fresh and not state[d]
            state[d] += Q(coef) * state[s]
        fresh.discard(d)


def main():
    assert __debug__
    SCOPE["start"]()
    keys, cuts, word = SCOPE["inputs"]()
    rows = []
    capped = False
    try:
        walk(word, keys, rows)
    except TimeoutError:
        capped = True
    finally:
        alarm(0)
    resolved = {tuple(x["key"]): x for x in rows}
    print(dumps({
        "head": SCOPE["HEAD"], "caller": SCOPE["CALLER"],
        "method": "one archived exact direction, forward sweep", "cap_seconds": SCOPE["CAP"],
        "pins": SCOPE["PINS"], "cut_coverage": sum(b-a+1 for a,b in cuts.values()),
        "rows": [resolved.get(k, {"key": k, "decision": "unresolved"}) for k in keys],
        "cap_reached": capped,
    }, sort_keys=True, indent=2))
    if capped:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
