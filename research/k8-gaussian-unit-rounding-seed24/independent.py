#!/usr/bin/env python3
"""Literal-lowerer grid audit, separately implemented by the same AI-assisted author.

It shares source authentication with model.py, but not its cost formula, helper
selection, incidence extraction, breakpoint search, Gaussian lowering or replay.
Hanson Sun with OpenAI Codex; Apache-2.0. PR696 lowerer: Sagar Thakrar.
"""
from fractions import Fraction
from functools import lru_cache
import gzip
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import model


def insist(ok, message):
    if not ok:
        raise ValueError(message)


def run():
    model.check_sources()
    root = model.ROOT
    with tarfile.open(root / model.ARCHIVE1042) as archive:
        programs = json.loads(gzip.decompress(archive.extractfile("slots/local/LOCAL-PROGRAMS.json.gz").read()))
        word = json.loads(gzip.decompress(archive.extractfile("slots/local/CANONICAL-WORD.json.gz").read()))
    spec = importlib.util.spec_from_file_location("independent_pr696", root / model.LOWER)
    lowerer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lowerer)
    census = json.loads(gzip.decompress((model.HERE / "CENSUS.json.gz").read_bytes()))
    certificate = json.loads((model.HERE / "CERTIFICATE.json").read_bytes())

    @lru_cache(maxsize=None)
    def literal(q):
        return len(lowerer.lower(["add", ("target",), ("source",),
                                  q.numerator, q.denominator], work=("work",)))

    def two(k):
        return Fraction(2 ** k) if k >= 0 else Fraction(1, 2 ** -k)

    # Reconstruct the exclusion contract register by register, not by using the
    # producer's domain routine or the supplied helper list.
    eligible = []
    for h in range(224, 704):
        if h in word["centers"] or word["start"][h] != 0 or word["final"][h] != 1:
            continue
        blocked = False
        for events in programs.values():
            for event in events:
                if event[0] == "residual_adapter" and event[2] == h:
                    blocked = True
                elif event[0] == "scalar" and event[1][0] in ("copy", "clear") and ["L", h] in event[1][1:]:
                    blocked = True
        if not blocked:
            eligible.append(h)
    insist(eligible == certificate["eligible_helpers"] and len(eligible) == 237, "independent helper domain")
    summary = {"helper_count": len(eligible), "orientations": {}}
    for orientation, events in programs.items():
        target_terms = {h: [] for h in eligible}
        source_terms = {h: [] for h in eligible}
        baseline = 0
        for event in events:
            if event[0] != "scalar":
                continue
            op = event[1]
            baseline += 2 * len(lowerer.lower(op))
            if op[0] == "add":
                q = Fraction(op[3], op[4])
                if op[1][0] == "L" and op[1][1] in target_terms:
                    target_terms[op[1][1]].append(q)
                if op[2][0] == "L" and op[2][1] in source_terms:
                    source_terms[op[2][1]].append(q)
        insist(baseline == certificate["orientations"][orientation]["programs"]["baseline"]["invoice"]["complex_scalar_primitives"], "literal full baseline")
        rows = {r["helper"]: r for r in census[orientation]}
        grid_evaluations = 0
        term_evaluations = 0
        critical_rows = []
        for h in eligible:
            incoming, outgoing = target_terms[h], source_terms[h]
            all_terms = incoming + outgoing
            exponents = []
            for q in all_terms:
                n, d, exponent = abs(q.numerator), q.denominator, 0
                while n % 2 == 0:
                    n //= 2
                    exponent += 1
                while d > 1:
                    insist(d % 2 == 0, "dyadic source")
                    d //= 2
                    exponent -= 1
                exponents.append(exponent)
            radius = max([abs(e) for e in exponents] + [0]) + 3
            lo, hi = -radius, radius
            original = 2 * sum(literal(q) for q in all_terms)

            def r(k):
                return 4 * abs(k) + 2 * sum(literal(q * two(k)) for q in incoming) + 2 * sum(literal(q / two(k)) for q in outgoing) - original

            def g(a):
                # Two copies of the exact predecessor coefficient circuit,
                # one extra target accumulation each, and optimal boundaries.
                return 2 * abs(2 * a + 1) + 4 + sum(2 * literal(q * two(a)) + 2 for q in incoming) + sum(2 * literal(q / two(a + 1)) + 2 for q in outgoing) - original

            real_grid = [(k, r(k)) for k in range(lo, hi + 1)]
            odd_grid = [(a, g(a)) for a in range(lo, hi + 1)]
            def key(pair):
                return pair[1], abs(pair[0]), pair[0]
            insist(list(min(real_grid, key=key)) == rows[h]["real_best"], "independent real minimum")
            insist(list(min(odd_grid, key=key)) == rows[h]["odd_best"], "independent odd minimum")
            for k, value in rows[h]["real_candidates"]:
                insist(lo <= k <= hi and r(k) == value, "real breakpoint receipt")
            for a, value in rows[h]["odd_candidates"]:
                insist(lo <= a <= hi and g(a) == value, "odd breakpoint receipt")
            slope = 4 + 2 * len(all_terms)
            for cost in (r, g):
                insist(cost(lo - 1) - cost(lo) == slope and cost(hi + 1) - cost(hi) == slope,
                        "independent outward tails")
            for a in range(lo, hi + 1):
                insist(2 * g(a) >= r(a) + r(a + 1) + 8, "single-helper common rounding")
            grid_evaluations += len(real_grid) + len(odd_grid)
            term_evaluations += (len(real_grid) + len(odd_grid)) * len(all_terms)
            critical_rows.append([h, lo, hi, min(real_grid, key=key), min(odd_grid, key=key)])
        summary["orientations"][orientation] = {
            "complete_scalar_baseline": baseline, "integer_grid_evaluations": grid_evaluations,
            "incident_term_evaluations": term_evaluations,
            "grid_rows_sha256": model.sha(model.canonical(critical_rows))}

    # Independently decide unit membership by computing the actual reciprocal,
    # then compare the normal-form implementation on a finite exact domain.
    units = nonunits = 0
    seen = set()
    for denominator_exponent in range(4):
        for re in range(-16, 17):
            for im in range(-16, 17):
                z = Fraction(re, 2 ** denominator_exponent), Fraction(im, 2 ** denominator_exponent)
                if z == (0, 0) or z in seen:
                    continue
                seen.add(z)
                norm = z[0] * z[0] + z[1] * z[1]
                reciprocal = z[0] / norm, -z[1] / norm
                is_unit = all(q.denominator & (q.denominator - 1) == 0 for q in reciprocal)
                try:
                    coordinates = model.unit_coordinates(z)
                except ValueError:
                    insist(not is_unit, "unit wrongly rejected")
                    nonunits += 1
                else:
                    insist(is_unit and model.gauge(*coordinates) == z, "nonunit or wrong normal form")
                    units += 1
    summary["unit_membership_grid"] = {"distinct_nonzero_inputs": len(seen), "units": units, "nonunits": nonunits,
                                       "numerators": [-16, 16], "common_denominator_exponents": [0, 3]}
    summary["literal_distinct_coefficients"] = literal.cache_info().currsize
    summary["status"] = "PASS_INDEPENDENT_LITERAL_GAUSSIAN_GRID"
    return summary


if __name__ == "__main__":
    result = run()
    path = model.HERE / "INDEPENDENT.json"
    if sys.argv[1:] == ["--write"]:
        path.write_text(json.dumps(result, indent=2) + "\n")
    else:
        insist(sys.argv[1:] in ([], ["--json"]), "arguments")
        insist(result == json.loads(path.read_bytes()), "independent receipt mismatch")
    print(json.dumps(result, indent=2) if sys.argv[1:] == ["--json"] else result["status"])
