"""Exact checks of the new attaining family; no predecessor replay or imports."""

import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from model import MAX_G, MAX_N, locate, readout_formula, require, sizes, witness, word


def add_terms(target, source, factor, sign):
    for monomial, coefficient in source.items():
        key = monomial + (factor,)
        value = target.get(key, 0) + sign * coefficient
        if value:
            target[key] = value
        else:
            target.pop(key, None)
        require(len(key) <= MAX_N and len(target) <= 512
                and abs(value).bit_length() <= 64, "symbolic capacity exceeded")


def backwards(events, cut, register, selected, mass):
    """One row walks backward, recording channels before crossing each injection."""
    require(0 < cut <= len(events), "invalid cut")
    require(len(selected) == len(set(selected)), "duplicate injection")
    chosen = set(selected)
    row = {register: {(): 1}}
    channels = {}
    full = []
    for j in range(cut - 1, -1, -1):
        source, target, factor, sign = events[j]
        polynomial = row.get(target, {})
        if j in chosen:
            channels[j] = dict(polynomial)
        if sum(abs(c) for c in polynomial.values()) == mass:
            full.append(j)
        if polynomial:
            add_terms(row.setdefault(source, {}), polynomial, factor, sign)
    return channels, tuple(sorted(full))


def forwards(events, injection, cut, register):
    """Independent column propagation from one completed-leaf destination."""
    column = {events[injection][1]: {(): 1}}
    for j in range(injection + 1, cut):
        source, target, factor, sign = events[j]
        source_poly = column.get(source, {})
        if source_poly:
            target_poly = column.setdefault(target, {})
            for monomial, coefficient in source_poly.items():
                key = (factor,) + monomial
                value = target_poly.get(key, 0) + sign * coefficient
                if value:
                    target_poly[key] = value
                else:
                    target_poly.pop(key, None)
                require(len(key) <= MAX_N and len(target_poly) <= 512
                        and abs(value).bit_length() <= 64, "column capacity exceeded")
    return column.get(register, {})


def prefix_row(events, start, cut):
    row = {4: {(): 1}}
    for j in range(cut - 1, start - 1, -1):
        source, target, factor, sign = events[j]
        polynomial = row.get(target, {})
        if polynomial:
            add_terms(row.setdefault(source, {}), polynomial, factor, sign)
    return {v: p for v, p in row.items() if p}


def run_case(g):
    n, cut, selected = witness(g)
    events = word(n)
    require(len(events) == 4**g - 3 * 2 ** (g - 1), "total-length formula")
    require(cut == (43 * 4 ** (g - 2) + 2) // 3 - 3 * 2 ** (g - 1),
            "cut-position formula")
    channels, full = backwards(events, cut, 4, selected, g - 1)
    require(full == selected, "attaining set differs from complete cut scan")
    start, _ = locate(n, ("V'",))
    row = prefix_row(events, start, cut)
    require(row == readout_formula(g), "readout formula differs from literal prefix")
    observations = 0
    for injection in selected:
        polynomial = channels[injection]
        require(sum(abs(c) for c in polynomial.values()) == g - 1, "channel mass")
        require(len(polynomial) == g - 1, "distinct channel monomials")
        require(all(abs(c) == 1 for c in polynomial.values()), "unit coefficients")
        require(forwards(events, injection, cut, 4) == polynomial,
                "forward column differs from backward row")
        observations += len(polynomial)
    counts = sizes(n)
    boundaries = (counts[n // 2], counts[n // 2] + counts[n - n // 2], start)
    groups = [0] * 4
    for injection in selected:
        groups[sum(injection >= b for b in boundaries)] += 1
    require(groups == [2 * g - 3, 2, 2 * g - 3, 1], "phase-family counts")
    return {"g": g, "factors": n, "leaves": len(events), "cut": cut,
            "channels": len(selected), "monomials": observations, "groups": groups}


def controls():
    rejected = 0
    for bad in (2, MAX_G + 1, True, 3.0, "3"):
        try:
            witness(bad)
        except ValueError:
            rejected += 1
    require(rejected == 5, "invalid-depth controls")
    n, cut, selected = witness(3)
    events = word(n)
    _, wrong_row = backwards(events, cut, 3, selected, 2)
    require(wrong_row != selected, "wrong scratch level must lose attainment")
    _, wrong_cut = backwards(events, cut - 4, 4, selected, 2)
    require(wrong_cut != selected, "changed cut must lose attainment")
    try:
        backwards(events, cut, 4, selected + (selected[0],), 2)
    except ValueError:
        rejected += 1
    require(rejected == 6, "duplicate errors must not count twice")
    start, _ = locate(n, ("V'",))
    formula = readout_formula(3)
    reversed_row = {v: {tuple(reversed(m)): c for m, c in p.items()}
                    for v, p in formula.items()}
    require(prefix_row(events, start, cut) != reversed_row, "factor order control")
    unsigned = [(x, y, f, 1) for x, y, f, _ in events]
    require(any(forwards(events, i, cut, 4) != forwards(unsigned, i, cut, 4)
                for i in selected), "inverse-sign control")
    require(sum(abs(c) for c in forwards(events, 0, cut, 4).values()) != 2,
            "nonfamily injection control")
    return {"rejections": rejected, "semantic_controls": 5}


def main():
    require(len(sys.argv) == 1, "this bounded replay accepts no arguments")
    cases = [run_case(g) for g in range(3, MAX_G + 1)]
    result = {"marker": "PASS_ALL_ONES_CHANNEL_ATTAINMENT", "cases": cases,
              "controls": controls(), "python": sys.version.split()[0]}
    here = Path(__file__).resolve().parent
    names = ("README.md", "PROOF.md", "model.py", "verify.py", "TASK.json",
             "SOURCES.json", "VERIFY.json")
    result["sha256"] = {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
                        for name in names}
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
