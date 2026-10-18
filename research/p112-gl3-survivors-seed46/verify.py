#!/usr/bin/env python3
"""Exact dense-projection GL3 COPY obstruction, standard library only.

Cinna Davis, with substantial OpenAI Codex assistance. Apache-2.0.
The free-rectangle support-containment method follows Arham Tahir's PR1331;
the two-coordinate GL3 branch, five-class census and power screen are new.
"""
import argparse
from collections import Counter
import copy
from fractions import Fraction
import hashlib
import importlib.util
from itertools import combinations, product
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import common as C


def rank(rows):
    pivots = {}
    for value in rows:
        while value:
            bit = value.bit_length()-1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def mask(indices):
    return sum(1 << i for i in indices)


def geometry(data):
    roots = set()
    for i, j in combinations(range(8), 2):
        for sign in (-1, 1):
            r = [0]*8
            r[i], r[j] = 2, 2*sign
            roots.add(tuple(r))
    roots.update((1,)+signs for signs in product((-1, 1), repeat=7)
                 if sum(s < 0 for s in signs) % 2 == 0)
    frame = []
    for i in range(0, 8, 2):
        for sign in (1, -1):
            r = [0]*8
            r[i], r[i+1] = 2, 2*sign
            frame.append(tuple(r))
    C.need(len(roots) == 120 and set(frame) <= roots, "120 E8 lines and frame")
    live = [tuple(row) for row in data["roots"]]
    C.need(len(live) == 112 and set(live) == roots-set(frame), "source live root lines")
    C.need([list(r) for r in frame] == data["frame"], "source coordinate frame order")
    dot = lambda a, b: sum(v*w for v, w in zip(a, b))
    x = [[dot(r, f)//4 for f in frame] for r in live]
    C.need(all(dot(r, f) % 4 == 0 for r in live for f in frame), "integral coordinates")
    C.need(x == data["X"] and set(v for row in x for v in row) == {-1, 0, 1}, "source X")
    b = [mask(j for j, s in enumerate(live) if (dot(r, s)//4+1) % 2) for r in live]
    for i, r in enumerate(live):
        for j, s in enumerate(live):
            C.need(dot(r, s) % 4 == 0, "integral root Gram")
            C.need(dot(x[i], x[j]) == dot(r, s)//2, "XX transpose = 2G")
            C.need((b[i] >> j & 1) == (data["labels"][i] & data["duals"][j]).bit_count() % 2,
                   "source labels/duals pairing")
    C.need(rank(b) == 9 and all(b[i] >> i & 1 for i in range(112)), "binary pairing rank/diagonal")
    C.need(all(sum(row[a]*row[d] for row in x) == 56*int(a == d)
               for a in range(8) for d in range(8)), "coordinate orthogonality")
    return x, b


def census(x, b):
    supports = [mask(i for i, row in enumerate(x) if a*row[4]+d*row[6] != 0)
                for a, d in C.NORMALS]
    slices = [[s & b[j] for j in range(112)] for s in supports]
    zero_pairs = [(i, j) for i in range(112) for j in range(112) if not (b[i] >> j & 1)]
    transcript, histograms, minima, witnesses = bytearray(), [], [], []
    for a in range(5):
        minrow = []
        for d in range(5):
            counts, best, witness = Counter(), 10, None
            for i, j in zero_pairs:
                left, right = slices[a][j], slices[d][i]
                cost = rank(b[r] & right for r in range(112) if left >> r & 1)
                transcript.append(cost)
                counts[cost] += 1
                if cost < best:
                    best, witness = cost, [i, j]
            minrow.append(best)
            histograms.append({"left": a, "right": d,
                               "counts": {str(k): v for k, v in sorted(counts.items())}})
            witnesses.append({"left": a, "right": d, "ports": witness, "rank": best})
        minima.append(minrow)
    report = {"records": len(transcript), "zero_pairs": len(zero_pairs),
            "support_sizes": [s.bit_count() for s in supports], "minima": minima,
            "histograms": histograms, "witnesses": witnesses,
            "transcript_sha256": hashlib.sha256(transcript).hexdigest(),
            "slice_dimensions": [{str(k): v for k, v in sorted(Counter(
                rank(b[r] for r in range(112) if s >> r & 1) for s in slots).items())}
                                 for slots in slices]}
    return report, bytes(transcript)


def costs(b, left, right):
    out = []
    for c in range(3):
        source = mask(j for j in range(112) if right[j][c] != (0, 0))
        out.append(rank(b[i] & source for i in range(112) if left[i][c] != (0, 0)))
    return out


def domain(b, u, v, matrix):
    inv = C.inverse_transpose(matrix)
    us = [i for i, z in enumerate(u) if z != (0, 0)]
    vs = [i for i, z in enumerate(v) if z != (0, 0)]
    C.need(us and vs, "nonzero rectangle required")
    C.need(all(not (b[i] >> j & 1) for i in us for j in vs), "rectangle is not free")
    C.need(all(any(matrix[r][c] for r in (0, 1)) and any(inv[r][c] for r in (0, 1))
               for c in range(3)), "three nonzero projected products required")
    return inv


def check_census(result, floor=6):
    C.need(result["zero_pairs"] == 5824 and result["records"] == 25*5824, "census coverage")
    C.need(min(map(min, result["minima"])) >= floor, "survivor floor")
    C.need(result["support_sizes"] == [56, 56, 76, 76, 88], "projective support classes")
    C.need(result["minima"] == [[4+(1 if a < 2 else 2)+(1 if d < 2 else 2)
                                 for d in range(5)] for a in range(5)], "refined 6/7/8 floors")


def verify():
    inputs = C.source_bytes()
    data = C.load(inputs[C.GEOMETRY])
    x, b = geometry(data)
    result, primary_transcript = census(x, b)
    check_census(result)
    spec = importlib.util.spec_from_file_location("independent_s46", HERE/"independent.py")
    independent = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(independent)
    independent_result, independent_transcript = independent.census(data)
    C.need(primary_transcript == independent_transcript, "independent per-record costs disagree")
    C.need(result == independent_result, "independent survivor census disagrees")
    baseline = []
    for c in range(8):
        s = mask(i for i in range(112) if x[i][c])
        baseline.append(rank(b[i] & s for i in range(112) if s >> i & 1))
    C.need(baseline == [8]*8, "baseline COPY rank")
    matrices = [[[1, 2, 3], [2, 5, 7], [3, 7, 11]],
                [[1, 0, 1], [0, 1, 0], [1, 0, 2]]]
    fixtures = []
    for k, matrix in enumerate(matrices):
        for phases in [((1, 0), (1, 0), (1, 0)), ((1, 0), (0, 1), (0, -1))]:
            u, v = [(0, 0)]*112, [(0, 0)]*112
            u[4], v[6] = (0, 1), (1, -1)
            domain(b, u, v, matrix)
            left, right, inv = C.factors(x, u, v, matrix, phases)
            entries = C.identity_check(x, u, v, left, right)
            cc = costs(b, left, right)
            C.need(min(cc) >= 6, "fixture below theorem")
            fixtures.append({"matrix": matrix, "phases": phases, "u_port": 4, "v_port": 6,
                             "u_value": u[4], "v_value": v[6], "costs": cc,
                             "identity_entries": entries})
    controls = []

    def reject(name, function):
        try:
            function()
        except ValueError:
            controls.append(name)
        else:
            raise ValueError("negative control accepted: "+name)

    u, v = [(0, 0)]*112, [(0, 0)]*112
    u[4], v[6] = (1, 0), (1, 0)
    reject("vanishing_projected_product", lambda: domain(b, u, v, [[1,0,0],[0,1,0],[0,0,1]]))
    boundary = [[1,0,1],[0,1,1],[1,0,2]]
    zero_u, coordinate_v = [(0,0)]*112, [(r[4],0) for r in x]
    ll, rr, _ = C.factors(x, zero_u, coordinate_v, boundary)
    C.identity_check(x, zero_u, coordinate_v, ll, rr)
    boundary_cost = costs(b, ll, rr)
    C.need(sum(boundary_cost) < 18, "zero-rectangle boundary counterexample changed")
    reject("zero_rectangle_boundary", lambda: domain(b, zero_u, coordinate_v, boundary))
    bad_v = list(v)
    bad_v[4] = (1,0)
    reject("nonfree_diagonal", lambda: domain(b, u, bad_v, matrices[0]))
    reject("singular_GL3", lambda: C.inverse_transpose([[1,1,1]]*3))
    phases = ((1,0),(0,1),(0,-1))
    ll, rr, _ = C.factors(x, u, v, matrices[0], phases, conjugate_error=True)
    reject("conjugate_instead_of_transpose", lambda: C.identity_check(x, u, v, ll, rr))
    reject("false_floor_seven", lambda: check_census(result, floor=7))
    missing = copy.deepcopy(result)
    missing["records"] -= 1
    reject("incomplete_parameter_coverage", lambda: check_census(missing))
    reject("generic_class_includes_balance", lambda: C.need(
        mask(i for i,r in enumerate(x) if r[4]+r[6])
        == mask(i for i,r in enumerate(x) if r[4]+2*r[6]), "distinct support strata"))
    reject("power_exponent_two", lambda: C.power_screen(Fraction(2)))
    bad_pins = C.load((HERE/"SOURCES.json").read_bytes())
    bad_pins["files"][0]["sha256"] = "0"*64
    reject("corrupted_source_pin", lambda: C.source_bytes(bad_pins))
    return {"schema_version": 1, "assignment_seed": 46, "base_commit": C.BASE,
            "coordinate_pair": list(C.PAIR), "normal_representatives": C.NORMALS,
            "normal_classes": C.NAMES, "baseline_COPY_ranks": baseline,
            "survivor_census": result, "independent_census_agrees": True,
            "fixtures": fixtures, "zero_rectangle_boundary_costs": boundary_cost,
            "controls_rejected": controls,
            "power_examples": [C.power_screen(q) for q in [Fraction(1),Fraction(1,2),Fraction(9,10),Fraction(999,1000)]],
            "COPY_rank_floor": 66, "replacement_floor": 18, "fully_dense_replacement_floor": 24,
            "replacement_power_ratio_floor": "9/8",
            "full_COPY_power_ratio_floor": "33/32",
            "scope": "Nonzero free rectangle; GL3 with three nonzero original-coordinate projections per side; pair4,6; separate-total COPY costs at unchanged width/normalization. Not all GL3 or arbitrary masked decoders; no new kappa."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-certificate", action="store_true")
    parser.add_argument("--check", type=Path, default=HERE/"CERTIFICATE.json")
    args = parser.parse_args()
    result = verify()
    if args.write_certificate:
        (HERE/"CERTIFICATE.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    else:
        C.need(C.canonical(result) == C.canonical(C.load(args.check.read_bytes())), "certificate drift")
    print("PASS_P112_GL3_S46 records=145600 floor=66 power_ratio_floor=9/8 controls=10 no_new_kappa")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(str(exc))
