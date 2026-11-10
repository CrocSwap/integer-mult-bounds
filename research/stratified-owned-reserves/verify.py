#!/usr/bin/env python3
"""Exact bounded corroboration, not an executed supplier dispatcher.

Prepared for CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
from fractions import Fraction
from hashlib import sha256, sha1
from itertools import product
import json
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def load_source(path):
    import types
    module = types.ModuleType("stack_model_source")
    module.__file__ = str(path)
    old = sys.modules.get(module.__name__)
    sys.modules[module.__name__] = module
    try:
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    finally:
        if old is None:
            sys.modules.pop(module.__name__, None)
        else:
            sys.modules[module.__name__] = old
    return module


M = load_source(PACKAGE / "stack_model.py")


def need(condition, label):
    if not condition:
        raise SystemExit("FAIL_STRATIFIED_OWNED_RESERVES: " + label)


def rejects(function, label):
    try:
        function()
    except (ValueError, SystemExit):
        return label
    raise SystemExit("negative control unexpectedly accepted: " + label)


def source_bindings():
    source = json.loads((PACKAGE / "SOURCES.json").read_text())
    live = [row for row in source["files"] if row["usage"] == "input"]
    for row in live:
        raw = (ROOT / row["path"]).read_bytes()
        need(sha256(raw).hexdigest() == row["sha256"], "SHA " + row["path"])
        blob = sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        need(blob == row["git_blob"], "Git blob " + row["path"])
    app = (ROOT / "docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md").read_text()
    pattern = r"\.0034\s*->\s*\.0038507\s*->\s*\.00385248"
    need(re.search(pattern, app) is not None, "actual frozen backend chain")
    for token in ["ρ=1/250", "**134**", "W(w)^D_stock(e) S_old", "107,352",
                  "117,612", "product of simultaneous BIT and complex reservations",
                  "ordinary maps/high-part exchanges", "with atom exponent"]:
        need(token in app, "source application token " + token)
    geometry = (ROOT / "research/delayed-cover-batch-allocation/PROOF.md").read_text()
    need("V/L" in geometry, "whole-high contraction")
    atom = (ROOT / "notes/stopped-product-interface.tex").read_text()
    need("volume factor below four" in atom and "below $q^2$" in atom,
         "retained embedding factors")
    need(re.search(pattern, app.replace(".0038507", ".0034", 1)) is None,
         "wrong middle backend rejects")
    return {"live_pins": len(live), "backend_savings": [".0034", ".0038507", ".00385248"],
            "source_rho": "1/250", "raw_bit_ambient_cap": 134,
            "source_application_sha256": sha256(app.encode()).hexdigest()}


def enumerate_paths(stages, start, depth):
    """Independent bounded route expansion, without Bellman updates."""
    by_name = {s.name: s for s in stages}
    stack = [(start, Fraction(1), (Fraction(0),) * len(stages[0].local), 0)]
    while stack:
        name, volume, totals, used = stack.pop()
        s = by_name[name]
        now = tuple(x + volume * c for x, c in zip(totals, s.local, strict=True))
        yield now
        if used == depth:
            continue
        if s.contraction:
            stack.append((name, volume * s.contraction, now, used + 1))
        for other, inflation in s.lower:
            stack.append((other, volume * inflation, now, used + 1))


def stack_certificates():
    comparisons = 0
    graphs = 0
    for costs in product((1, 2), repeat=3):
        for rhos in product((Fraction(0), Fraction(1, 2)), repeat=3):
            for mask in range(8):
                edges = [[], [], []]
                for bit, (i, j) in enumerate(((1, 0), (2, 0), (2, 1))):
                    if mask & (1 << bit):
                        edges[i].append((str(j), Fraction(2 if bit % 2 else 1)))
                stages = tuple(M.Stage(str(i), rhos[i], (Fraction(costs[i]),), tuple(edges[i]))
                               for i in range(3))
                bound = M.potentials(stages)
                graphs += 1
                for path in enumerate_paths(stages, "2", 8):
                    comparisons += 1
                    need(path[0] <= bound["2"][0], "bounded independent path")
                for s in stages:
                    b = bound[s.name][0]
                    need(b >= s.local[0] + s.contraction * b, "self inequality")
                    for j, a in s.lower:
                        need(b >= s.local[0] + a * bound[j][0], "descending inequality")
    chosen = M.selected_relaxation(3, 3)
    bound = M.potentials(chosen)
    expected = {"B0": 1, "K1": 5, "O1": 91, "K2": 365, "O2": 6571, "C": 6572}
    need({key: int(value[0]) for key, value in bound.items()} == expected,
         "selected graph symbolic unit example")
    selected_paths = list(enumerate_paths(chosen, "C", 10))
    need(max(p[0] for p in selected_paths) == bound["C"][0], "attaining finite path")
    rows = [(i + 1, 2 * i + 1, 1) for i in range(6)]
    typed = M.selected_relaxation(3, 5, rows)
    typed_bound = M.potentials(typed)
    for path in enumerate_paths(typed, "C", 9):
        need(all(x <= y for x, y in zip(path, typed_bound["C"], strict=True)),
             "per-tape weighted path")
    controls = [
        rejects(lambda: M.potentials([M.Stage("x", Fraction(1), (Fraction(1),))]),
                "same-stage noncontraction"),
        rejects(lambda: M.potentials([M.Stage("low", Fraction(0), (Fraction(1),),
                                                (("high", Fraction(1)),)),
                                      M.Stage("high", Fraction(0), (Fraction(1),))]),
                "upward edge / cycle"),
    ]
    need(sum([1] * 7) > 2, "same-volume chain exceeds one-provider geometric two")
    controls.append("seven same-volume frames exceed 2V")
    return {"graphs": graphs, "bounded_path_comparisons": comparisons,
            "selected_bounded_paths": len(selected_paths), "unit_example": expected,
            "controls": controls}


def history_controls():
    tapes = 3
    initial = [11, 19, 7]
    origin = [2, 3, 1]
    historical = initial.copy()
    all_paths = []
    node_count = 0

    def visit(vol, level, path):
        nonlocal node_count
        node_count += 1
        local = [c * vol for c in (1, 2, 3)]
        for t in range(tapes):
            historical[t] = max(historical[t], origin[t] + local[t])
        new_path = [p + x for p, x in zip(path, local, strict=True)]
        all_paths.append(tuple(new_path))
        if level:
            saved = origin.copy()
            for t in range(tapes):
                origin[t] += local[t]
            visit(vol // 2, level - 1, new_path)
            after_first = origin.copy()
            visit(vol // 2, level - 1, new_path)
            need(origin == after_first, "sibling returns to same origin")
            origin[:] = saved

    visit(64, 4, [0, 0, 0])
    per_tape = [max(p[t] for p in all_paths) for t in range(tapes)]
    need(all(h <= k + b for h, k, b in zip(historical, initial, per_tape, strict=True)),
         "historical coordinate envelope")
    need(origin == [2, 3, 1], "root origins restored")
    peaks = [(80, 0), (0, 80)]
    history = sum(max(row[t] for row in peaks) for t in range(2))
    live_max = max(map(sum, peaks))
    need(history == 160 and live_max == 80, "sum of maxima differs from maximum sum")
    need(7 * 80 > 80, "append-only sibling history violates restored-origin bound")
    need(1000 + 80 > 80, "warm erased entry backing must be included")
    need(23 * 64 > 64, "dropping external factor undercounts physical field")
    return {"reference_nodes": node_count, "historical_extents": historical,
            "path_extents": per_tape, "role_rotating_history": history,
            "false_max_live": live_max,
            "controls": ["append-only sibling", "entry backing omitted", "external factor omitted",
                         "aggregate-live maximum substituted"]}


def stock_checks():
    cases = 0
    monotone = 0
    for n in (2, 3, 5):
        for numerator, denominator in ((1, 2), (1, 3), (2, 3), (1, 250)):
            previous = None
            for e_max in range(1, 101):
                bar = M.reserve_envelope(e_max, n, numerator, denominator)
                if previous:
                    need(all(a <= b for a, b in zip(previous, bar, strict=True)),
                         "safe envelope monotone")
                    monotone += 1
                previous = bar
                for e in range(1, e_max + 1):
                    actual = M.stock_exponents(e, n, numerator, denominator)
                    need(all(a <= b for a, b in zip(actual, bar, strict=True)),
                         "every smaller width in reserve envelope")
                    cases += 1
    k = 3215
    e0, e1 = k ** 250, k ** 250 + 1
    need((k - 1) ** 250 < e0 <= k ** 250 < e1 <= (k + 1) ** 250,
         "exact selected-rho atom widths")
    n0, n1 = M.ceil_div(e0, k), M.ceil_div(e1, k + 1)
    need(2 ** 2901 < n0 <= 2 ** 2902, "first depth interval")
    need(2 ** 2900 < n1 <= 2 ** 2901, "second depth interval")
    d0, d1 = 2 + M.ceil_log(n0, 2), 2 + M.ceil_log(n1, 2)
    exponent_delta = 4 * (k * d1 - (k - 1) * d0)
    need((d0, d1, d1 - d0, exponent_delta) == (2904, 2903, -1, -1244),
         "symbolic stock decrease")
    need(2 * (3 * 3 - 1) * (3 * 3 - 3) == 96, "GL2 algebraic control")
    need(M.stock_exponents(2 ** 100, 2, 1, 250)[1] > 2,
         "bootstrap count is not depth stock")
    return {"smaller_width_checks": cases, "monotonicity_checks": monotone,
            "rho": "1/250", "discontinuity_k": k,
            "e0_description": "3215^250", "e1_description": "3215^250+1",
            "depths": [d0, d1], "ratio": "L^-1*q^-1244",
            "counterexample_scope": "stock formula at N=2; no selected-instance or prime admission claim",
            "controls": ["raw endpoint stock substituted", "bootstrap count substituted for depth"]}


def product_reservations():
    count = 0
    for radices in ((2, 3), (2, 3, 5), (3, 4, 2, 3), (1, 2, 1, 5)):
        total = 1
        for radix in radices:
            total *= radix
        seen = set()
        for coordinates in product(*(range(r) for r in radices)):
            rank = M.mixed_rank(coordinates, radices)
            need(rank not in seen, "independent reservation injective")
            seen.add(rank)
            need(M.mixed_unrank(rank, radices) == coordinates, "reservation inverse")
            for i, r in enumerate(radices):
                changed = list(coordinates)
                changed[i] = (changed[i] + 1) % r
                returned = list(M.mixed_unrank(M.mixed_rank(changed, radices), radices))
                returned[i] = (returned[i] - 1) % r
                need(tuple(returned) == coordinates, "other stage factors and returned row survive")
            count += 1
        need(seen == set(range(total)), "complete simultaneous stock")
        for q in range(total, 2 * total + 1):
            padded = total * M.ceil_div(q, total)
            need(q <= padded < 2 * q, "single complete-row padding")
    need(max(2, 3, 5) < 2 * 3 * 5, "max is not product")
    return {"complete_product_coordinates": count,
            "controls": ["max stock substituted for product", "external stage coordinate dropped"]}


def main():
    need(sys.argv[1:] in ([], ["--emit"]), "command-line arguments")
    result = {"schema": 1, "scope": "conditional allocation accounting; no new kappa",
              "source": source_bindings(), "stack": stack_certificates(),
              "history": history_controls(), "stock": stock_checks(),
              "reservations": product_reservations()}
    canonical = json.dumps(result, sort_keys=True, separators=(",", ":"))
    if sys.argv[1:] == ["--emit"]:
        print(json.dumps(result, sort_keys=True, indent=2))
    else:
        frozen = json.loads((PACKAGE / "RESULT.json").read_text())
        need(canonical == json.dumps(frozen, sort_keys=True, separators=(",", ":")),
             "complete typed result equality")
        print("PASS_STRATIFIED_OWNED_RESERVES", sha256(canonical.encode()).hexdigest())


if __name__ == "__main__":
    main()
