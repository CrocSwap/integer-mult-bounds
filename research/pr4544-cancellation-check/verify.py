#!/usr/bin/env python3
"""Independent check of PR #4544 (Clear1nsight): the sharp cancellation audit of PR #4483 Section 4.

Written separately from #4544's checker; nothing is imported from it. Checks, in exact rational arithmetic:
  1. the slack identity (1-b)(eI-B-F) = (e-b)A-(1-e)F+(1-e)(bI-B) as a polynomial identity in Q[b,e,B,F,A], I=B+F+A;
  2. the extremiser: at B*=b(A+F)/(1-b) the exit fraction equals (bA+F)/(A+F), as a polynomial identity, and the
     fraction is linear-fractional in B, hence monotone, so the maximum over 0<=B<=B* sits at an endpoint (grid check);
  3. necessity of #4483's own threshold (10): with only F<=X and A>=D*X known, the adversary A=D*X, F=X with a
     saturated mirror has exit fraction (bD+1)/(D+1), and (D+1)(e-(bD+1)/(D+1)) = (e-b)D-(1-e) identically;
  4. #4544's two failure controls (root debit dropped; leaf mass dropped);
  5. the binding: the pinned source PROOF.md (sha256) states equations (2), (3), (9), (10), (11) as #4544 uses them.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Fr
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "research/rank-convergence/PROOF.md"
SOURCE_SHA256 = "3c971c5670669cb36312815b111e64c83e1490a10ee82f5412bd9aee01e9c376"
VARS = ("b", "e", "B", "F", "A", "D")


def need(condition, message):
    if not condition:
        raise AssertionError(message)


class P:
    """Sparse multivariate polynomial over Q in VARS."""

    def __init__(self, terms=None):
        self.t = {k: v for k, v in (terms or {}).items() if v}

    @staticmethod
    def var(name):
        k = [0] * len(VARS)
        k[VARS.index(name)] = 1
        return P({tuple(k): Fr(1)})

    @staticmethod
    def const(c):
        return P({(0,) * len(VARS): Fr(c)})

    def __add__(self, o):
        o = o if isinstance(o, P) else P.const(o)
        t = dict(self.t)
        for k, v in o.t.items():
            t[k] = t.get(k, 0) + v
        return P(t)

    __radd__ = __add__

    def __neg__(self):
        return P({k: -v for k, v in self.t.items()})

    def __sub__(self, o):
        return self + (-(o if isinstance(o, P) else P.const(o)))

    def __rsub__(self, o):
        return P.const(o) - self

    def __mul__(self, o):
        o = o if isinstance(o, P) else P.const(o)
        t = {}
        for k1, v1 in self.t.items():
            for k2, v2 in o.t.items():
                k = tuple(x + y for x, y in zip(k1, k2))
                t[k] = t.get(k, 0) + v1 * v2
        return P(t)

    __rmul__ = __mul__

    def is_zero(self):
        return not self.t


def symbolic():
    b, e, B, F, A, D = (P.var(v) for v in VARS)
    I = B + F + A
    slack = (1 - b) * (e * I - B - F) - ((e - b) * A - (1 - e) * F + (1 - e) * (b * I - B))
    need(slack.is_zero(), "slack identity")
    # Rejection control: dropping the mirror slack term breaks the identity.
    need(not ((1 - b) * (e * I - B - F) - ((e - b) * A - (1 - e) * F)).is_zero(), "rejection control")
    # Extremiser, cleared of the denominator (1-b): Bs = b(A+F)/(1-b), so (1-b)Bs = b(A+F).
    # (Bs+F)/(Bs+A+F) = (bA+F)/(A+F)  <=>  ((1-b)Bs+(1-b)F)(A+F) = (bA+F)((1-b)Bs+(1-b)(A+F)).
    sB = b * (A + F)
    ext = (sB + (1 - b) * F) * (A + F) - (b * A + F) * (sB + (1 - b) * (A + F))
    need(ext.is_zero(), "extremiser value")
    # Derivative numerator of (B+F)/(B+A+F) in B: (B+A+F) - (B+F) = A >= 0 (monotone nondecreasing).
    need(((B + A + F) - (B + F) - A).is_zero(), "monotonicity numerator")
    # Necessity of (10): (D+1)*e - (bD+1) = (e-b)D - (1-e).
    nec = (D + 1) * e - (b * D + 1) - ((e - b) * D - (1 - e))
    need(nec.is_zero(), "necessity of (10)")
    return 4


def frac(B, F, A):
    return (B + F) / (B + A + F)


def grid():
    vals = [Fr(n, d) for d in (1, 2, 3, 5, 7) for n in range(0, 2 * d + 1)]
    betas = [Fr(n, 8) for n in range(0, 8)]
    cases = 0
    for b in betas:
        for A in vals[::3]:
            for F in vals[::3]:
                if A + F == 0:
                    continue
                Bs = b * (A + F) / (1 - b)
                top = (b * A + F) / (A + F)
                need(frac(Bs, F, A) == top, "attained")
                need(frac(Fr(0), F, A) <= top, "endpoint order")
                for j in range(9):
                    need(frac(Bs * j / 8, F, A) <= top, "interior below the maximum")
                # The guarantee B+F <= eI for all admissible B holds iff top <= e iff (e-b)A >= (1-e)F.
                for e in [Fr(n, 16) for n in range(1, 16)]:
                    if e <= b:
                        continue
                    need((top <= e) == ((e - b) * A >= (1 - e) * F), "threshold equivalence")
                    cases += 1
    return cases


def controls():
    b, e = Fr(1, 4), Fr(1, 2)
    F, gross, R = Fr(1), Fr(2), Fr(1, 2)
    A = gross - R
    I = (A + F) / (1 - b)
    B = b * I
    need(I + R == B + F + gross, "exact cancellation (2)")
    need((B + F) / I == Fr(11, 20) and Fr(11, 20) > e, "root-debit control exits above eta")
    need((e - b) * gross == (1 - e) * F, "gross test passes with equality")
    need(not ((e - b) * A >= (1 - e) * F), "net test rejects")
    # Leaf omission: A=0, F=1 gives exit fraction 1 > eta although A >= 0.
    need(frac(Fr(0), Fr(1), Fr(0)) == 1, "leaf-omission control")
    # Zero mass: A=F=0 and B<=bI with I=B force I=B=0.
    return 2


def binding():
    raw = SOURCE.read_bytes()
    need(hashlib.sha256(raw).hexdigest() == SOURCE_SHA256, "pinned source bytes")
    text = raw.decode("utf-8")
    for s in ("I_t+R_t = B_t+F_t+(T_t-P_t)H_t.", "F_t <= P_t^(G+1).", "Set A_t=(T-P)H_t-R_t.",
              "A_t >=D_ell(t)P^(G+1),", "(eta-beta)D_ell(t) >=1-eta,", "B_t+F_t <=eta I_t.",
              "B_t<=beta I_t", "beta<eta<1"):
        need(s in text, f"source states: {s}")
    return 8


def main():
    report = {"status": "PASS_PR4544_CANCELLATION_CHECK", "symbolic_identities": symbolic(),
              "grid_threshold_cases": grid(), "failure_controls": controls(), "source_statements_bound": binding(),
              "new_kappa_claimed": False}
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    sys.exit(main())
