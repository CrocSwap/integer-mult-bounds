#!/usr/bin/env python3
"""Independent exact check of #4270's conservative exponent chain (kappa = 1/580).

Standard library only; no code from #4270. Constants come from its OUTER-JOIN.md
and the pooled fill's RESULT.json, vendored byte-identically (see vendor/NOTICE.md).
The pooled moment is enclosed with exact rationals: ln by atanh after reducing by
powers of two, exp by Taylor with a Lagrange remainder.
Ryanson Jonathan with Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
"""
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# The selected record as of this package's base commit (git blob b1fea0c9), vendored after main reselected it.
SELECTED_AT_BASE_SHA256 = "bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129"


def selected_at_base_path():
    path = HERE / "SELECTED-AT-BASE.json"
    if hashlib.sha256(path.read_bytes()).hexdigest() != SELECTED_AT_BASE_SHA256:
        raise AssertionError("vendored selected record")
    return path
VENDORED = {
    "vendor/OUTER-JOIN.md": "bfb4677ee82ffc070be880eca87af05fd096686b464dfd5268cee1b27afa453e",
    "vendor/pr4181-RESULT.json": "d823509ea38e545db6c287a85c00bc4257825fb2710728dfc776c8801d2becd9",
}
PHRASES = [
    "tau = 332353/332929,", "sigma_star = 0.99826995,", "alpha_layer = 0.99827,", "theta_stop = 1/1000000.",
    "`C=0.001730980255989036959962`", "the root reservation exponent is still `.998`.",
    "Phi = 1-(997/1000)(1-alpha_layer) = 0.99827519.", "`beta=41544341/41616125<Phi`",
    "payload terms have powers `.997` and at most `.9981`", "has power `3/5`, below Phi.",
    "1-Phi = 0.00172481 > 1/580,", "Fourier rate `.00172380303` does not itself reach `1/580`",
    "`O(V [g^alpha_layer log p + (g+1)^tau (log p)^(1+tau)]).`".strip("`"),
]
M, W = 73, 322560   # pooled moment width and role count, as in #4270's ledger and #4088/#4181


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atanh_ln(x, terms=45):
    z = (x - 1) / (x + 1)
    s = 2 * sum(z ** (2 * k + 1) / (2 * k + 1) for k in range(terms + 1))
    return s, s + 2 * z ** (2 * terms + 3) / ((2 * terms + 3) * (1 - z * z))


def ln_bounds(x):
    k = (x.numerator // x.denominator).bit_length() - 1
    a, b = atanh_ln(Q(2))
    c, d = atanh_ln(x / 2 ** k)
    return k * a + c, k * b + d


def exp_bounds(y, terms=30):
    s, term = Q(0), Q(1)
    for k in range(terms + 1):
        s += term
        term = term * y / (k + 1)
    return s, s + 3 * term


def moment_bounds(profile, a):
    """sum_r n_r (r/M)^(1-a) / W, with (r/M)^(1-a) = (r/M) exp(a ln(M/r))."""
    lo = hi = Q(0)
    for r, n in profile.items():
        ln_lo, ln_hi = ln_bounds(Q(M, r))
        lo += n * Q(r, M) * exp_bounds(a * ln_lo)[0]
        hi += n * Q(r, M) * exp_bounds(a * ln_hi)[1]
    return lo / W, hi / W


def main():
    for rel, digest in VENDORED.items():
        need(hashlib.sha256((HERE / rel).read_bytes()).hexdigest() == digest, f"vendored {rel}")
    text = (HERE / "vendor/OUTER-JOIN.md").read_text()
    need(all(p in text for p in PHRASES), "OUTER-JOIN.md phrases")
    pins = {row["path"]: row["sha256"] for row in json.loads((HERE / "SOURCES.json").read_text())["files"]}
    sel_path = selected_at_base_path()
    selected_kappa = Q(json.loads(sel_path.read_text())["kappa"])

    fill = json.loads((HERE / "vendor/pr4181-RESULT.json").read_text())
    profile = {int(r): n for r, n in fill["profile"].items()}
    root_lo, root_hi = Q(fill["root_lower"]), Q(fill["root_upper"])
    C = Q("0.001730980255989036959962")
    need(C == root_lo and root_hi - root_lo == Q(1, 10**24), "C is the pooled fill's certified root bracket")

    # 1. The pooled moment straddles 1 across the bracket (this pins M and W given the profile).
    at_c, above = moment_bounds(profile, root_lo), moment_bounds(profile, root_hi)
    need(at_c[1] < 1 < above[0], "pooled moment < 1 at 1-C and > 1 just above")
    margin = 1 - at_c[1]

    tau, sigma, alpha, theta = Q(332353, 332929), Q("0.99826995"), Q("0.99827"), Q(1, 10**6)
    # 2. Stopped tree: moment(sigma) <= moment(1-C) < 1 needs sigma > 1-C; tau < sigma < alpha.
    need(sigma > 1 - C, "sigma_star > 1 - C")
    need(tau < sigma < alpha, "tau < sigma_star < alpha_layer")
    internal = sigma - theta * (sigma - tau)
    leaf = sigma + theta * (1 - sigma)
    need(internal < alpha and leaf < alpha and Q("0.998") < alpha, "stopped-tree and reservation exponents")

    # 3. Outer layer: Phi as written, and every listed cost power strictly below it.
    phi = 1 - Q(997, 1000) * (1 - alpha)
    need(phi == Q("0.99827519"), "Phi = 0.99827519 exactly")
    beta = Q(41544341, 41616125)
    powers = {"full-support router beta": beta, "Gaussian payload .997": Q("0.997"),
              "Gaussian payload .9981": Q("0.9981"), "scalar words 3/5": Q(3, 5),
              "support second term .997 tau": Q("0.997") * tau, "CRT D Tp term .997": Q("0.997")}
    for name, power in powers.items():
        need(power < phi, f"{name} < Phi")

    # 4. The conclusion: 1 - Phi > 1/580 > selected kappa; the old rate alone falls short.
    kappa = Q(1, 580)
    need(1 - phi > kappa > selected_kappa, "1 - Phi > 1/580 > selected kappa")
    need(Q("0.00172380303") < kappa, "control: the old physical Fourier rate does not reach 1/580")

    print(json.dumps({
        "status": "PASS_PR4270_OUTER_EXPONENT_CHAIN",
        "pooled_moment_upper_at_1_minus_C": f"1 - {float(margin):.6e}",
        "sigma_star_minus_1_minus_C": f"{float(sigma - (1 - C)):.3e}",
        "sigma_star_minus_tau": f"{float(sigma - tau):.3e}",
        "alpha_minus_leaf_exponent": f"{float(alpha - leaf):.3e}",
        "phi_minus_beta": f"{float(phi - beta):.3e}",
        "one_minus_phi_minus_kappa": f"{float(1 - phi - kappa):.3e}",
        "kappa_minus_selected": f"{float(kappa - selected_kappa):.3e}",
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
