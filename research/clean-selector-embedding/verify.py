#!/usr/bin/env python3
"""Exact clean invariant-subspace certificates. ToikY with OpenAI Codex; Apache-2.0."""
import argparse
from fractions import Fraction as F
from hashlib import sha256
from math import comb
import json
from pathlib import Path

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[1]


def need(condition, message):
    if not condition:
        raise ValueError(message)


def multiplicities(n):
    need(type(n) is int and n >= 0, "invalid address width")
    counts = [0] * 4
    for k in range(n + 1):
        counts[k % 4] += comb(n, k)
    return counts


def character_counts(n):
    # Independent roots-of-unity filter: (1+i)^n, evaluated as integer pairs.
    real, imag = 1, 0
    for _ in range(n):
        real, imag = real - imag, real + imag
    alternating = int(n == 0)  # (1-1)^n, including n=0.
    nums = [2**n + alternating + 2*real,
            2**n - alternating + 2*imag,
            2**n + alternating - 2*real,
            2**n - alternating - 2*imag]
    need(all(x % 4 == 0 for x in nums), "nonintegral character filter")
    return [x // 4 for x in nums]


def feasible(n, s, d, phase=0):
    need(type(n) is int and n >= 1 and type(s) is int and s >= 1,
         "positive payload and selector widths required")
    need(type(d) is int and d >= 0 and type(phase) is int and 0 <= phase < 4,
         "invalid native width or phase")
    native, target = multiplicities(d), [2**s*x for x in multiplicities(n)]
    return all(native[(j-phase) % 4] >= target[j] for j in range(4))


def least_width(n, s, phases=(0,)):
    for d in range(n+s, n+s+3):
        for phase in phases:
            if feasible(n, s, d, phase):
                return d, phase
    raise ValueError("proved upper width failed")


def fixed_width_formula(n, s):
    # Closed all-size classification; checked below by independent count oracles.
    extra = 1
    if n == 1 and s % 8 not in (0, 6, 7):
        extra = 2
    elif n == 2 and s % 8 not in (0, 1, 5, 6, 7):
        extra = 2
    return n+s+extra


def injection(n, s, d, phase=0):
    need(feasible(n, s, d, phase), "insufficient native eigenspace")
    pools = [[v for v in range(2**d) if v.bit_count() % 4 == (j-phase) % 4]
             for j in range(4)]
    cursor = [0] * 4
    mapping = []
    for _lane in range(2**s):
        for u in range(2**n):
            j = u.bit_count() % 4
            mapping.append(pools[j][cursor[j]])
            cursor[j] += 1
    return mapping


def validate_mapping(n, s, d, phase, mapping):
    need(len(mapping) == 2**(n+s) and len(set(mapping)) == len(mapping),
         "encoding is not injective")
    need(all(type(v) is int and 0 <= v < 2**d for v in mapping), "encoding range")
    need(all((v.bit_count()+phase) % 4 == (x % 2**n).bit_count() % 4
             for x, v in enumerate(mapping)), "encoding eigenphase mismatch")


def sign(x):
    return -1 if x.bit_count() % 2 else 1


def encoding_columns(n, s, d, mapping):
    # E = H_d P (I_q tensor H_n) / 2^n; columns are exact rational vectors.
    return [[F(sum(sign(u & x)*sign(mapping[lane*2**n+u] & y)
                   for u in range(2**n)), 2**n)
             for y in range(2**d)]
            for lane in range(2**s) for x in range(2**n)]


def add(a, b):
    return a[0]+b[0], a[1]+b[1]


def mul(a, b):
    return a[0]*b[0]-a[1]*b[1], a[0]*b[1]+a[1]*b[0]


def times_i(a, phase):
    return (a, (-a[1], a[0]), (-a[0], -a[1]), (a[1], -a[0]))[phase]


def tensor_action(vector, width, phase=0):
    # Literal C butterflies, without multiplicity/eigenvector formulas.
    need(len(vector) == 2**width, "operator dimension")
    out = list(vector)
    alpha, beta = (F(1, 2), F(1, 2)), (F(1, 2), F(-1, 2))
    for bit in range(width):
        step = 1 << bit
        for x in range(2**width):
            if not x & step:
                a, b = out[x], out[x | step]
                out[x] = add(mul(alpha, a), mul(beta, b))
                out[x | step] = add(mul(beta, a), mul(alpha, b))
    return [times_i(x, phase) for x in out]


def fixture(n, s, d, phase):
    mapping = injection(n, s, d, phase)
    validate_mapping(n, s, d, phase, mapping)
    columns = encoding_columns(n, s, d, mapping)
    ambient, payload = 2**d, len(columns)
    scalar_checks = 0
    for x, column in enumerate(columns):
        left = tensor_action([(a, F(0)) for a in column], d, phase)
        basis = [(F(int(k == x % 2**n)), F(0)) for k in range(2**n)]
        local = tensor_action(basis, n)
        start = (x // 2**n)*2**n
        right = [(sum(columns[start+k][y]*local[k][0] for k in range(2**n)),
                  sum(columns[start+k][y]*local[k][1] for k in range(2**n)))
                 for y in range(ambient)]
        need(left == right, "literal intertwiner failed")
        scalar_checks += ambient
    # Independent exact Gram check gives F E=I for F=2^(n-d) E^T.
    for x in range(payload):
        for y in range(payload):
            dot = sum(a*b for a, b in zip(columns[x], columns[y]))
            need(dot == F(2**d, 2**n)*int(x == y), "left inverse failed")
    return {"n": n, "s": s, "d": d, "phase": phase,
            "ambient_coordinates": ambient, "payload_coordinates": payload,
            "volume_ratio": str(F(ambient, payload)),
            "mapping": mapping, "intertwiner_entries": scalar_checks,
            "gram_entries": payload**2}


def rejection(action):
    try:
        action()
    except ValueError:
        return
    raise ValueError("negative control was accepted")


def compute():
    for n in range(131):
        need(multiplicities(n) == character_counts(n), "multiplicity oracles differ")
    table = []
    for n in range(1, 65):
        for s in range(1, 65):
            N = n+s
            fixed = least_width(n, s)
            phased = least_width(n, s, (0, 2, 1, 3))  # Prefer real signs at equal width.
            # Full-space exclusion for every allowed global fourth-root phase.
            for phase in range(4):
                need(not feasible(n, s, N, phase), "equal-volume encoding admitted")
                need(feasible(n, s, N+2, phase), "two-bit upper bound failed")
            need(fixed[0] in (N+1, N+2) and phased[0] in (N+1, N+2), "width range")
            need(fixed[0] == fixed_width_formula(n, s), "closed fixed-width classification")
            need(phased[0] == N+1, "closed optional-phase classification")
            table.append([n, s, *fixed, *phased])
    fixtures = []
    for n, s in [(1,1), (1,2), (2,1), (2,2), (3,1), (1,4)]:
        for phases in [(0,), (0, 2, 1, 3)]:
            d, phase = least_width(n, s, phases)
            fixtures.append(fixture(n, s, d, phase))
    need(least_width(1, 4) == (7, 0), "fixed-phase motivating width")
    need(least_width(1, 4, (0, 2, 1, 3)) == (6, 2), "rephased motivating width")
    controls = []
    rejection(lambda: injection(1, 4, 6, 0)); controls.append("insufficient i eigenspace")
    m = injection(1, 4, 7)
    wrong = list(m); wrong[1] = wrong[0]
    rejection(lambda: validate_mapping(1, 4, 7, 0, wrong)); controls.append("duplicate eigenvector")
    rejection(lambda: validate_mapping(1, 4, 7, 1, m)); controls.append("unbilled phase")
    rejection(lambda: feasible(0, 1, 2)); controls.append("zero payload width")
    rejection(lambda: feasible(1, 0, 2)); controls.append("no batching")
    # Dirty complement is NOT restored: choose an unused non-fixed Walsh vector.
    dirty = next(v for v in range(128) if v not in m and v.bit_count() % 4 != 0)
    vector = [(F(sign(dirty & x)), F(0)) for x in range(128)]
    after = tensor_action(vector, 7)
    need(after != vector and after == [times_i(z, dirty.bit_count() % 4) for z in vector],
         "dirty-complement control")
    controls.append("dirty complement not restored")
    # Full constant vector alone does not validate a purported full-space encoding.
    ones = [(F(1), F(0))]*32
    need(tensor_action(ones, 5) == ones, "constant vector positive control")
    need(not feasible(1, 4, 5), "constant-only admission")
    controls.append("constant-only smoke test insufficient")
    table_bytes = json.dumps(table, separators=(",", ":")).encode()
    return {"status": "PASS_CLEAN_SELECTOR_EMBEDDING", "no_new_kappa": True,
            "scope": "Exact invariant clean-subspace algebra; inherited full-volume tariff screen only",
            "multiplicity_oracle_widths": 131, "width_cases": len(table),
            "width_table_sha256": sha256(table_bytes).hexdigest(),
            "closed_width_formula": {
                "fixed_n1_extra1_s_mod8": [0,6,7],
                "fixed_n2_extra1_s_mod8": [0,1,5,6,7],
                "fixed_n_at_least3_extra": 1,
                "fixed_other_small_cases_extra": 2,
                "optional_fourth_root_phase_extra": 1},
            "fixed_width_counts": {str(k): sum(row[2]-row[0]-row[1] == k for row in table) for k in (1,2)},
            "optional_phase_width_counts": {str(k): sum(row[4]-row[0]-row[1] == k for row in table) for k in (1,2)},
            "fixtures": fixtures, "controls": controls,
            "motivating_target_counts": [16,16,0,0],
            "native_d6_counts": multiplicities(6), "native_d7_counts": multiplicities(7),
            "tariff": "ambient/payload >= 2; B_native/B_lanes = 2^(d-n-s)*(d/n)^sigma > 2 for 0<sigma<1; all encoder costs waived"}


def check_sources():
    manifest = json.loads((PACKAGE / "SOURCES.json").read_text())
    for row in manifest["files"]:
        if row["usage"] == "input":
            need(sha256((ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"],
                 "changed pinned source: " + row["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write a NEW exact receipt; never overwrite")
    args = parser.parse_args()
    check_sources()
    result = compute()
    expected_path = PACKAGE / "CERTIFICATE.json"
    if args.output is None:
        expected = json.loads(expected_path.read_text())
        need(json.dumps(expected, sort_keys=True, separators=(",", ":")) ==
             json.dumps(result, sort_keys=True, separators=(",", ":")), "certificate mismatch")
    else:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(result, indent=2) + "\n")
    print(result["status"], "width_cases", result["width_cases"], "fixtures", len(result["fixtures"]),
          "controls", len(result["controls"]), "no_new_kappa")


if __name__ == "__main__":
    main()
