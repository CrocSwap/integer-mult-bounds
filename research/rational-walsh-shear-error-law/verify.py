#!/usr/bin/env python3
# research/rational-walsh-shear-error-law/verify.py
# Author: mithrax-exo (Apache-2.0 License)
"""Cached O(q) quotient-torus verifier for the Universal Rational Walsh-Shear Error Law (extending #7474)."""
import argparse
import json
import math
import sys

def round_half_even(num: int, den: int) -> int:
    q, rem = divmod(2 * num, den)
    if (q & 1) == 0:
        return q // 2
    m = (q - 1) // 2
    return (m + 1) if rem > 0 else (m if (m & 1) == 0 else (m + 1))

def predicted_4q_max(p: int, q: int) -> int:
    assert q >= 2 and math.gcd(abs(p), q) == 1
    return 5 * q - 4 + (q % 4) + abs(p)

def precompute_block_states(need_s_mod_4q: bool, s_local_idx: int, q: int):
    P_a = (8 * q) if need_s_mod_4q else 8
    uniq = {}
    for a in range(P_a):
        for b in range(8):
            for x0, x1 in ((a, b), (b, a)):
                u0, u1 = x0 + x1, x0 - x1
                y0, y1 = round_half_even(u0, 2), round_half_even(u1, 2)
                ys_mod = ((y0 if s_local_idx == 0 else y1) % (4 * q)) if need_s_mod_4q else 0
                key = (y0 % 4, y1 % 4, 2 * y0 - u0, 2 * y1 - u1, ys_mod)
                if key not in uniq:
                    uniq[key] = (u0, u1, y0, y1)
    return list(uniq.values())

def verify_periodicity_samples(p: int, q: int) -> None:
    P = 8 * q
    for t, s in ((0, 1), (1, 2), (2, 0), (3, 2)):
        for x in ((1, 4, 0, 1), (3, -2, 7, 4)):
            vals = []
            for sh in ((0, 0, 0, 0), (P, 0, 0, 0), (0, -P, P, -P)):
                xx = tuple(x[i] + sh[i] for i in range(4))
                u = (xx[0] + xx[1], xx[0] - xx[1], xx[2] + xx[3], xx[2] - xx[3])
                y = [round_half_even(uk, 2) for uk in u]
                z = list(y)
                z[t] = round_half_even(q * y[t] + p * y[s], q)
                F = (
                    round_half_even(z[0] + z[2], 2),
                    round_half_even(z[1] + z[3], 2),
                    round_half_even(z[0] - z[2], 2),
                    round_half_even(z[1] - z[3], 2),
                )
                v = [q * uk for uk in u]
                v[t] += p * u[s]
                C4q = (v[0] + v[2], v[1] + v[3], v[0] - v[2], v[1] - v[3])
                vals.append([4 * q * F[k] - C4q[k] for k in range(4)])
            assert vals[0] == vals[1] == vals[2]

def verify_all_for_q(q: int) -> int:
    base_reps = precompute_block_states(False, 0, q)
    s0_reps = precompute_block_states(True, 0, q)
    s1_reps = precompute_block_states(True, 1, q)

    coprime_ps = [p for p in range(1, 2 * q) if math.gcd(p, q) == 1]
    for p in coprime_ps:
        verify_periodicity_samples(p, q)
        exp = predicted_4q_max(p, q)
        for sgn in (1, -1):
            ps = sgn * p
            for t in range(4):
                for s in range(4):
                    if t == s:
                        continue
                    b0 = (s0_reps if s == 0 else s1_reps) if s in (0, 1) else base_reps
                    b1 = (s0_reps if s == 2 else s1_reps) if s in (2, 3) else base_reps
                    best = -1
                    for u0, u1, y0, y1 in b0:
                        for u2, u3, y2, y3 in b1:
                            u = (u0, u1, u2, u3)
                            y = (y0, y1, y2, y3)
                            zt = round_half_even(q * y[t] + ps * y[s], q)
                            z0 = zt if t == 0 else y0
                            z1 = zt if t == 1 else y1
                            z2 = zt if t == 2 else y2
                            z3 = zt if t == 3 else y3
                            f0 = round_half_even(z0 + z2, 2)
                            f1 = round_half_even(z1 + z3, 2)
                            f2 = round_half_even(z0 - z2, 2)
                            f3 = round_half_even(z1 - z3, 2)
                            v0, v1, v2, v3 = q * u0, q * u1, q * u2, q * u3
                            pus = ps * u[s]
                            if t == 0: v0 += pus
                            elif t == 1: v1 += pus
                            elif t == 2: v2 += pus
                            else: v3 += pus
                            mx = max(
                                abs(4 * q * f0 - (v0 + v2)),
                                abs(4 * q * f1 - (v1 + v3)),
                                abs(4 * q * f2 - (v0 - v2)),
                                abs(4 * q * f3 - (v1 - v3)),
                            )
                            if mx > best:
                                best = mx
                    assert best == exp, f"Mismatch at alpha={ps}/{q}, ({t},{s}): {best} != {exp}"
    return 2 * len(coprime_ps)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--qmax", type=int, default=8, help="Max denominator q to verify (pass 16 for full 316-shear run)")
    args = ap.parse_args()

    total_pairs = sum(verify_all_for_q(q) for q in range(2, args.qmax + 1))
    print("PASS_UNIVERSAL_RATIONAL_WALSH_SHEAR_LAW")
    print(json.dumps({
        "status": "PASS",
        "qmax_verified": args.qmax,
        "signed_coprime_shears_verified": total_pairs,
        "formula": "(5*q - 4 + (q mod 4) + |p|) / (4*q) * h",
        "quarter_shear_peak": "17/16",
        "half_shear_peak_pr7474": "9/8",
        "third_shear_peak": "5/4",
    }))
    return 0

if __name__ == "__main__":
    sys.exit(main())
