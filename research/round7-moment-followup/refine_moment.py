#!/usr/bin/env python3
"""Frozen Round7 BIT moment enclosure ablation; no construction/assembly retuning.

Portable in research/round7-moment-refinement; elsewhere supply --repo. Each --output must
be new. Arithmetic is exact; decimal fields are display only. The companion's
unchanged conditional construction and assembly hypotheses remain necessary.
"""
import argparse
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import subprocess
import sys

PIN = "741e7aa078392553815df7926ee17ac5e25a8c38"
SCALE = 10**18
ROUND = 10**40


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def js(x):
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): js(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [js(v) for v in x]
    return x


def floorq(x, den=ROUND):
    return Q((x * den).numerator // (x * den).denominator, den)


def ceilq(x, den=ROUND):
    return -floorq(-x, den)


@lru_cache(None)
def logs40(x):
    """Base-two reduction; 40-term atanh with explicit geometric remainder."""
    assert x >= 1
    k = 0
    while x > 2:
        k += 1
        x /= 2
    def small(y):
        z = (y - 1) / (y + 1)
        power, val = z, Q(0)
        for j in range(40):
            val += power / (2 * j + 1)
            power *= z * z
        return 2 * val, 2 * (val + power / (81 * (1 - z * z)))
    a, b = small(x)
    c, d = small(Q(2))
    return a + k * c, b + k * d


def taylor_moment(c, saving):
    lo, hi = Q(0), Q(0)
    terms = {}
    for t, n in c["hist"]:
        loglo, loghi = logs40(Q(c["m"], t))
        u, v = floorq(saving * loglo), ceilq(saving * loghi)
        assert 0 <= u <= v < Q(1, 1000)
        pl, ph, sl, sh = Q(1), Q(1), Q(1), Q(1)
        for j in range(1, 9):
            pl, ph = pl * u / j, ph * v / j
            sl, sh = sl + pl, sh + ph
        # Degree 9 first omitted term; every later ratio <= v/10.
        sh += ph * v / 9 / (1 - v / 10)
        el, eh = floorq(sl), ceilq(sh)
        weight = Q(t * n, c["m"] * c["W"])
        lo += weight * el
        hi += weight * eh
        terms[t] = dict(weight=weight, log_lower=loglo, log_upper=loghi,
                        exponent_lower=u, exponent_upper=v,
                        exp_lower=el, exp_upper=eh)
    return dict(lower=lo, upper=hi, terms=terms)


def crossing(fun):
    lo, hi = 1, 10**14
    assert fun(Q(lo, SCALE))["upper"] < 1
    assert fun(Q(hi, SCALE))["lower"] > 1
    steps = 0
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        b = fun(Q(mid, SCALE))
        if b["upper"] < 1:
            lo = mid
        elif b["lower"] > 1:
            hi = mid
        else:
            raise ArithmeticError("Enclosure is too wide to classify this grid point")
        steps += 1
    return dict(saving=Q(lo, SCALE), next_saving=Q(hi, SCALE),
                accepted=fun(Q(lo, SCALE)), rejected=fun(Q(hi, SCALE)), steps=steps)


def main():
    if not __debug__:
        raise SystemExit("Assertions required; Python -O unsupported")
    sys.set_int_max_str_digits(0)
    sys.dont_write_bytecode = True
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    repo = args.repo.resolve()
    # These immutable sources may live in an additive later commit.
    expected = {
        "lean/round7-histograms.json": "8fd0abe6c230980b9a0c4a175e06ca1808b0fe5ead0cf9f268496111c2e11d2c",
        "scripts/certificate_round3.py": "53deb36c0f5daffc68ee02dabf189d2700f39a2bb3f01b55c663c49cd315b9ae",
        "independent/two-stage-bit/moment.py": "4ca6b15fa6cf799b7252d9a70d5c66dcbe86f3cc16b03b7c6f03ccda66df41be",
    }
    for name, digest in expected.items():
        assert sha(repo / name) == digest, name
    data = json.loads((repo / "lean/round7-histograms.json").read_text())
    c = data["bit"]
    assert c["m"] == 529 and c["W"] == 108516254 and c["s"] == 57403754177
    assert sum(t * n for t, n in c["hist"]) == c["s"]
    sys.path.insert(0, str(repo / "scripts"))
    sys.path.insert(0, str(repo / "independent/two-stage-bit"))
    import moment
    from certificate_round3 import evaluate
    lu = {t: moment.ln_upper(Q(c["m"], t)) for t, _ in c["hist"]}
    mc = dict(m=c["m"], W=c["W"], hist=dict(c["hist"]))
    def recip(a):
        val = moment.F_upper(mc, a, lu)
        # Crossing of this particular majorant, NOT a lower bound on true moment.
        return dict(lower=val, upper=val)
    r = crossing(recip)
    print("reciprocal fine", r["saving"], "next", r["next_saving"], flush=True)
    t = crossing(lambda a: taylor_moment(c, a))
    print("Taylor degree8 fine", t["saving"], "next", t["next_saving"], flush=True)
    variants = {}
    for name, a in (("reciprocal_coarse", Q(*c["a"])), ("reciprocal_fine", r["saving"]),
                    ("taylor_coarse", floorq(t["saving"], 10**9)), ("taylor_fine", t["saving"])):
        assembly = evaluate(a, Q(*data["cx"]["a"]), Q(1, 1000), "crude",
                            m_c=data["cx"]["m"], s_c=data["cx"]["s"])
        assert assembly["ok"] and assembly["c1"] == 14694 and assembly["x"] == 14695
        variants[name] = dict(bit_saving=a, assembly=assembly)
        print(name, a, "kappa", assembly["kappa"], flush=True)
    assert variants["reciprocal_coarse"]["assembly"]["kappa"] == Q(*data["kappa"]["kappa"])
    old = variants["reciprocal_coarse"]["assembly"]["kappa"]
    grid = variants["reciprocal_fine"]["assembly"]["kappa"]
    best = variants["taylor_fine"]["assembly"]["kappa"]
    result = dict(status="PASS primary exact enclosure; independent enclosure required separately",
                  pinned_basis=PIN, source_sha256=expected, verifier_sha256=sha(Path(__file__)),
                  histogram=c, grid_denominator=SCALE, exp_degree=8,
                  log_reduction=2, log_terms=40, directed_rounding=ROUND,
                  reciprocal_fine=r, taylor_fine=t, variants=variants,
                  gain=dict(grid_only=grid-old, tighter_moment_at_fine_grid=best-grid,
                            total=best-old, relative_display_only=float((best-old)/old)),
                  assumptions="Frozen histogram's conditional physical realization and original round3 assembly; unchanged complex saving, beta, crude guard, epsilon/kappa grids.")
    out = args.output.resolve()
    out.mkdir(exist_ok=False, parents=True)
    (out / "certificate.json").write_text(json.dumps(js(result), indent=2, sort_keys=True) + "\n")
    print("PASS", out, flush=True)


if __name__ == "__main__":
    main()
