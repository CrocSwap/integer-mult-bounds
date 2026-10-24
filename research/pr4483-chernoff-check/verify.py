#!/usr/bin/env python3
"""Independent check of PR #4483 (zxv), research/rank-convergence/PROOF.md sections 2-3, on actual flows.

For the arbitrary-height flow at #4483's height G = (a+b) floor(log_M floor(N/m)), this file's own flow code computes,
at real exponents t, the unit-column potential H_t, root-source potential R_t, inner-source potential I_t,
boundary-exit potential B_t and leaf-exit potential F_t, and checks
  (2)  I_t + R_t = B_t + F_t + (T - P) H_t, EXACTLY as an identity of formal power sums sum_x c_x x^t with integer
       coefficients (hence for every t at once), with a dropped-source rejection control, and numerically at each t
  (7)  (T - P) H_t >= (1 - u_t^ell) P^(G+1) (q^(a ell + 1) - 1)
  (8)  R_t <= q M^lambda v_t^ell P^(G+1)
  (9)  A_t = (T - P) H_t - R_t >= D_ell(t) P^(G+1)
  and the ratio-ordering premise T(t+s)/T(t) >= P(t+s)/P(t),
with u_t, v_t, q as in #4483 (6), for the raw p7 profile with #4483's p7 geometry (M = 256, a = b = 1, s = lambda = 1/10)
and the p16 (#4470) profile with #4532's p16 geometry (M = 1024, a = b = 1, s = 1/20, lambda = 1/10), at several
ranks (heights G up to 6 for p7 and 4 for p16) and exponents above each profile's moment crossing (T > P is (7)'s premise). Profiles are read from main (sha256-pinned); the proof's
equations are bound verbatim to the pinned PROOF.md.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
import hashlib
import json
import math
from math import factorial
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P7 = ROOT / "research/higher-moment-strictification/RESULT.json"
P16 = ROOT / "research/compact-joint-compiler/arithmetic/RESULT.json"
PROOF = ROOT / "research/rank-convergence/PROOF.md"
PINS = {P7: "ad79e3c0459e7b495a0ca34010553b12147779a007389e1695cc1336f123c156", P16: "a6caaa2a6d6460a8c1ef7e48c4853bb27976be33a52b96a4216dfa90d96c9091", PROOF: "3c971c5670669cb36312815b111e64c83e1490a10ee82f5412bd9aee01e9c376"}


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def multis(n, size):
    if n == 1:
        yield (size,); return
    for k in range(size + 1):
        for rest in multis(n - 1, size - k): yield (k,) + rest
def potentials(N, W, P, G, t, formal=False):
    ks = sorted(W); m = ks[-1]
    def c(a):
        v = 1
        for k, x in zip(ks, a): v *= k ** x
        return v
    def u(a):
        v = factorial(sum(a))
        for k, x in zip(ks, a): v = v // factorial(x) * W[k] ** x
        return v
    F = [{1: 1}]
    for d in range(1, G + 1):
        nxt = {}
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                if m * rho * r <= N: nxt[rho * r] = nxt.get(rho * r, 0) + cnt * pr
        F.append(nxt)
    present = lambda rho, a: m * rho * c(a) <= N
    if formal:
        H, R, I, B, Fl = {}, {}, {}, {}, {}

        def acc(d, base, coeff):
            d[base] = d.get(base, 0) + coeff
    else:
        H = R = I = B = Fl = 0.0
    for d in range(G + 1):
        for rho, cnt in F[d].items():
            for b in multis(len(ks), G - d):
                if not present(rho, b): continue
                if formal:
                    acc(H, rho * c(b), cnt * u(b))
                else:
                    H += cnt * u(b) * (rho * c(b)) ** t
                for r, pr in P.items():
                    issued = cnt * pr * u(b); rank = r * rho * c(b)
                    if d == G:
                        if formal:
                            acc(Fl, rank, issued)
                        else:
                            Fl += issued * rank ** t
                        continue
                    D = sum(W[k] * u(tuple(x - (i == j) for j, x in enumerate(b)))
                            for i, k in enumerate(ks) if b[i] > 0 and present(rho * r, tuple(x - (i == j) for j, x in enumerate(b))))
                    if issued - cnt * pr * D:
                        if formal:
                            acc(B, rank, issued - cnt * pr * D)
                        else:
                            B += (issued - cnt * pr * D) * rank ** t
    for a in multis(len(ks), G):
        if present(1, a):
            for k in ks:
                if formal:
                    acc(R, k * c(a), W[k] * u(a))
                else:
                    R += W[k] * u(a) * (k * c(a)) ** t
    for d in range(1, G + 1):
        for rho, cnt in F[d - 1].items():
            for r, pr in P.items():
                for a in multis(len(ks), G - d):
                    if not present(rho * r, a): continue
                    for i, k in enumerate(ks):
                        b = list(a); b[i] += 1
                        if not present(rho, tuple(b)):
                            if formal:
                                acc(I, rho * r * c(tuple(b)), cnt * pr * u(a) * W[k])
                            else:
                                I += cnt * pr * u(a) * W[k] * (rho * r * c(tuple(b))) ** t
    return H, R, I, B, Fl


def mom(h, t):
    return sum(x * k ** t for k, x in h.items())


def exact_identity(W, P, N, G):
    """(2) as an identity of formal power sums sum_x coeff_x x^t, exact for every t at once."""
    H, R, I, B, Fl = potentials(N, W, P, G, None, formal=True)
    lhs, rhs = dict(I), dict(B)
    for x, v in R.items():
        lhs[x] = lhs.get(x, 0) + v
    for x, v in Fl.items():
        rhs[x] = rhs.get(x, 0) + v
    for x, v in H.items():  # (T - P) H = sum_k W_k (k x)^t - sum_r P_r (r x)^t
        for k, w in W.items():
            rhs[k * x] = rhs.get(k * x, 0) + w * v
        for r, q in P.items():
            rhs[r * x] = rhs.get(r * x, 0) - q * v
    lhs = {x: v for x, v in lhs.items() if v}
    rhs = {x: v for x, v in rhs.items() if v}
    need(lhs == rhs, f"exact formal identity (2) at N={N}, G={G}")
    x0 = min(R)  # rejection control: dropping one root source must break the identity
    bad = dict(lhs)
    bad[x0] -= R[x0]
    need({x: v for x, v in bad.items() if v} != rhs, "control: a dropped root source is detected")
    return len(lhs)


def check_case(name, W, P, M, a, b, s, lam, ranks, exponents):
    m = max(W)
    rows = []
    for t in exponents:
        T, Pt = mom(W, t), mom(P, t)
        q = T / Pt
        need(q > 1, f"{name}: (7) premise T(t) > P(t) at t={t}")
        need(mom(W, t + s) / T >= mom(P, t + s) / Pt, f"{name}: ratio ordering at t={t}")
        u_t = M ** (-s) * (mom(W, t + s) / T) ** a * (mom(P, t + s) / Pt) ** b
        v_t = M ** lam * (mom(W, t - lam) / Pt) ** (a + b)
        for N in ranks:
            C = N // m
            ell = 0
            while M ** (ell + 1) <= C:
                ell += 1
            G = (a + b) * ell
            H, R, I, B, Fl = potentials(N, W, P, G, t)
            lhs2, rhs2 = I + R, B + Fl + (T - Pt) * H
            need(abs(lhs2 - rhs2) <= 1e-9 * abs(rhs2), f"{name}: identity (2) at N={N}, t={t}")
            A = (T - Pt) * H - R
            rhs7 = (1 - u_t ** ell) * Pt ** (G + 1) * (q ** (a * ell + 1) - 1)
            rhs8 = q * M ** lam * v_t ** ell * Pt ** (G + 1)
            D = (1 - u_t ** ell) * (q ** (a * ell + 1) - 1) - q * M ** lam * v_t ** ell
            need((T - Pt) * H >= rhs7 * (1 - 1e-12), f"{name}: (7) at N={N}, t={t}")
            need(R <= rhs8 * (1 + 1e-12), f"{name}: (8) at N={N}, t={t}")
            need(A >= D * Pt ** (G + 1) - 1e-9 * abs(D * Pt ** (G + 1)), f"{name}: (9) at N={N}, t={t}")
            if t == exponents[0]:
                bases = exact_identity(W, P, N, G)
            rows.append({"t": t, "N": N, "ell": ell, "G": G, "exact_identity_bases": bases, "ratio7": round(((T - Pt) * H) / rhs7, 4) if rhs7 > 0 else None,
                         "ratio8": round(R / rhs8, 4)})
    return rows


def main():
    for path, digest in PINS.items():
        need(hashlib.sha256(path.read_bytes()).hexdigest() == digest, f"pinned {path.name}")
    o7 = json.loads(P7.read_bytes())["invoice_oracle"]
    W7 = {int(k): v for k, v in o7["targets"].items()}
    P7h = {int(k): v for k, v in o7["paid"].items()}
    d16 = json.loads(P16.read_bytes())
    W16 = {int(k): v for k, v in d16["targets"].items()}
    P16h = {int(k): v for k, v in d16["paid"].items()}
    text = PROOF.read_text(encoding="utf-8")
    for s_ in ("I_t+R_t = B_t+F_t+(T_t-P_t)H_t.", "(T-P)H_t >=(1-u_t^ell)P^(G+1)(q^(a*ell+1)-1).",
               "<=q*M^lambda*v_t^ell*P^(G+1).", "D_ell(t)=(1-u_t^ell)(q^(a*ell+1)-1)-q*M^lambda*v_t^ell."):
        need(s_ in text, f"PROOF.md states: {s_}")
    p7 = check_case("p7", W7, P7h, 256, 1, 1, 0.1, 0.1, (10 ** 5, 10 ** 7, 3 * 10 ** 9), (0.99731352, 0.997481, 0.999))
    p16 = check_case("p16", W16, P16h, 1024, 1, 1, 0.05, 0.1, (2 * 10 ** 5, 2 * 10 ** 8), (0.99697984, 0.997066, 0.999))
    print(json.dumps({"status": "PASS_PR4483_CHERNOFF_CHECK", "p7": p7, "p16": p16,
                      "min_ratio7": min(r["ratio7"] for r in p7 + p16 if r["ratio7"]),
                      "max_ratio8": max(r["ratio8"] for r in p7 + p16), "new_kappa_claimed": False}, indent=1))


if __name__ == "__main__":
    sys.exit(main())
