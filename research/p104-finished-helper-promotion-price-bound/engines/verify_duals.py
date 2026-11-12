"""Verify previously frozen separating inputs by exact forward rational rows."""
from fractions import Fraction as Q
from runpy import run_path
from pathlib import Path
from signal import SIGALRM, alarm, signal

ROOT = Path(__file__).resolve().parent


def timeout(*_):
    raise TimeoutError("20-second exact dual readback cap")


def dot(row, dual):
    return sum(row[j]*x for j, x in dual.items() if j in row)


def readback(word, independent, lead):
    signal(SIGALRM, timeout)
    alarm(20)
    try:
        base = run_path(str(ROOT / "bank_gate.py"))
        add, scalar = base["add"], base["scalar"]
        n, m = word["public"], word["owned_fields"]
        rows = [{i: Q(1)} for i in range(n)] + [{} for _ in range(m)]
        charts = word["initial"] + [None] * m
        assert (n, m, len(word["program"])) == (1501, 68, 76466)
        left = {tuple(key): (r, p, c, dual, value)
                for _, key, r, p, c, dual, value in independent}
        assert len(left) == len(lead) == 119 and left.keys() == lead.keys()
        source_clock, bank_clock = {}, {}
        for key, (r, p, c, dual, value) in left.items():
            a, s, b = key
            assert word["program"][a][:2] == word["program"][b][:2] == ["MOVE", r]
            assert word["program"][s][:3] == ["ADD", r, p]
            assert word["program"][b][3] == c
            assert s not in source_clock and b not in bank_clock
            source_clock[s] = bank_clock[b] = key
        targets = {}
        checked = 0
        for t, (op, d, *a) in enumerate(word["program"][:max(bank_clock)+1]):
            if t in source_clock:
                key = source_clock[t]
                targets[key] = rows[left[key][1]].copy()
            if op == "MOVE":
                assert charts[d] == a[0]
                charts[d] = a[1]
            elif op == "INIT":
                assert charts[d] is None and not rows[d]
                charts[d] = a[0]
            elif op == "CLEAR":
                assert charts[d] == a[0]
                charts[d] = None
                rows[d].clear()
            elif op == "SCALE":
                assert charts[d] == a[1] and scalar(a[0])
                rows[d] = {j: x*scalar(a[0]) for j, x in rows[d].items()}
            else:
                s, k, c = a
                assert op in ("ADD", "COPY") and s != d and charts[d] == charts[s] == c
                assert op != "COPY" or not rows[d]
                add(rows[d], rows[s], scalar(k))
            if t not in bank_clock:
                continue
            key = bank_clock[t]
            r, _, c, dual, value = left[key]
            bank = [row for j, (chart, row) in enumerate(zip(charts, rows, strict=True)) if chart == c and j != r]
            target = targets.pop(key)
            for coeffs, expected in ((dual, value), lead[key]):
                x = {int(j): Q(v) for j, v in coeffs.items()}
                assert all(0 <= j < n and v for j, v in x.items())
                assert all(not dot(row, x) for row in bank)
                assert dot(target, x) == Q(expected) != 0
                checked += 1
            if key == (48765,48766,48767):
                assert charts[831] == 306 and rows[831] == {831: Q(1)}
                assert [len(word["frames"][f]) for f in (3,306,127)] == [0,4,9]
                assert target == {831: Q(-1),1497: Q(1)}
                # Reversing the witness sign fails its exact signed target check.
                assert dot(target, {831: Q(-1)}) != Q(value)
        assert checked == 238 and not targets
        return checked
    finally:
        alarm(0)
