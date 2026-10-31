#!/usr/bin/env python3
"""Independent exact check of #4338's ordinary B2 bootstrap arithmetic.

Standard library only; no code from #4338. Its PROOF.md is vendored byte-identically
(vendor/NOTICE.md) and phrase-checked; H, a1 and C are read from their canonical files on
main. The moment at 576/577 is enclosed with exact rationals: ln by atanh after reducing by
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
PROOF_SHA256 = "c2ca95cc85439768ebfae81057b845b9e26cc8f153ef787c15f74127456dba8b"
PHRASES = [
    "a2 = 57697923247/33292900000000",
    "T_B2(V,e) <= 4283584 A V e^(1-a2),",
    "a2-C = 342853411912956978405651/166464500000000000000000000000.",
    "`a1=169711/100000000=0.00169711`",
    "`s=(1-10^-24)C-10^-27`",
    "a_next = s(1-s)+s*a1 = 0.001730921627244654642552821294... .",
    "(1-10^-24)*q/(1+q) = 0.001727930714600372546778004395...,",
    "which is below `0.001727989140903569` by more than `5.8426*10^-8`.",
    "q=(1-2*10^-24)*a_next,",
    "Instead choose the independent BIT coupling `c=1/577`.",
    "H={1:381024,2:400416,3:22752,4:26880,\n   5:29376,6:17376,7:26784,42:288},",
    "m=64, W=28416, epsilon=10^-16,\nF=32*64^2*sum(H)=118606528512.",
    "mu_1 = 2874298095721977/2890625000000000 < 199/200,",
    "[999998938581682162866772413602,\n  999998938581682162866772413603]/10^30 < 999999/1000000.",
    "The old `9999/10000` power cap is false at this coupling.",
    "T1(n,w) <= 200 A n + 1000000 A n^(1-c) w^p1.",
    "`17^128>32*16^128`",
    "`32780*(17/16)*20=696575<2^20`",
    "T_B2(V,e)/V <= A[801n + 4000000 n^(1-c) w^p1 + k+w+1].",
    "801 + 4000000*(17/16) + 32780 + 2 + 1 = 4283584.",
    "Now `a2=c(1-c)+c*a1`. Since `c>a1`,",
    "| `c-a2` | `2076753/33292900000000` |",
    "| `1-a2-c` | `33177502076753/33292900000000` |",
    "| `1-a2-c(1-a1)` | `331776/332929` |",
    "| `1-c` | `576/577` |",
    "Their minimum is the first.",
    "Since `17/10000<c<1/512`",
    "For the finite fallback range `e<2^20`, `e^a2<2^(20/512)<2`",
]
M = 64


def need(condition, message):
    if not condition:
        raise AssertionError(message)


def atanh_ln(x, terms=60):
    z = (x - 1) / (x + 1)
    s = 2 * sum(z ** (2 * k + 1) / (2 * k + 1) for k in range(terms + 1))
    return s, s + 2 * z ** (2 * terms + 3) / ((2 * terms + 3) * (1 - z * z))


def ln_bounds(x):
    k = (x.numerator // x.denominator).bit_length() - 1
    a, b = atanh_ln(Q(2))
    c, d = atanh_ln(x / 2 ** k)
    return k * a + c, k * b + d


def exp_bounds(y, terms=30):
    """0 <= y <= 1"""
    s, term = Q(0), Q(1)
    for k in range(terms + 1):
        s += term
        term = term * y / (k + 1)
    return s, s + 3 * term


def moment(t, H, W, fallback):
    """mu_t = (sum H[r] (r/64)^t + fallback (1/64)^t) / W, with (r/64)^t = (r/64) exp((1-t) ln(64/r))"""
    lo = hi = Q(0)
    for r, n in list(H.items()) + [(1, fallback)]:
        l_lo, l_hi = ln_bounds(Q(M, r))
        lo += n * Q(r, M) * exp_bounds((1 - t) * l_lo)[0]
        hi += n * Q(r, M) * exp_bounds((1 - t) * l_hi)[1]
    return lo / W, hi / W


def main():
    raw = (HERE / "vendor/B2-PROOF.md").read_bytes()
    need(hashlib.sha256(raw).hexdigest() == PROOF_SHA256, "vendored B2-PROOF.md")
    text = raw.decode()
    for phrase in PHRASES:
        need(phrase in text, f"phrase: {phrase[:50]}")
    pins = {row["path"]: row["sha256"] for row in json.loads((HERE / "SOURCES.json").read_text())["files"]}

    def pinned(rel):
        if rel == "certificates/selected-result.json":
            return json.loads(selected_at_base_path().read_text())
        path = ROOT / rel
        need(hashlib.sha256(path.read_bytes()).hexdigest() == pins[rel], f"pin {rel}")
        return json.loads(path.read_text())

    sel = pinned("research/e8-bit-p111-tuned/tune/EXPECTED.json")["nine"]
    H = {int(r): n for r, n in sel["profile"].items()}
    a1 = Q(pinned("research/selected-bit-recursive-closure/RESULT.json")["recursion"]["moments"]["ordinary_saving"])
    C = Q(pinned("research/staged-fourth-mixture-ceiling/RESULT.json")["root_decimal_bracket"][0])
    need(H == {1: 381024, 2: 400416, 3: 22752, 4: 26880, 5: 29376, 6: 17376, 7: 26784, 42: 288}, "H is the selected BIT profile")
    need(a1 == Q(169711, 10**8) and C == Q("0.001730980255989036959962"), "a1 from PR2899's closure, C from the pooled ceiling")
    W, eps, c = 28416, Q(1, 10**16), Q(1, 577)

    # 1. the rate and its excess over C
    a2 = c * (1 - c) + c * a1
    need(a2 == Q(57697923247, 33292900000000), "a2 = c(1-c) + c a1")
    need(a2 - C == Q(342853411912956978405651, 166464500000000000000000000000) > 0, "a2 - C as stated, positive")

    # 2. section 1: bootstrapping at the complex rate misses the legacy target after the outer loss
    s = (1 - Q(1, 10**24)) * C - Q(1, 10**27)
    a_next = s * (1 - s) + s * a1
    q = (1 - 2 * Q(1, 10**24)) * a_next
    k_out = (1 - Q(1, 10**24)) * q / (1 + q)
    need(f"{float(a_next):.15f}" == "0.001730921627245" and str(a_next.numerator * 10**30 // a_next.denominator).startswith("1730921627244654642552821294"), "a_next digits")
    need(str(k_out.numerator * 10**30 // k_out.denominator).startswith("1727930714600372546778004395"), "outer-loss digits")
    shortfall = Q("0.001727989140903569") - k_out
    need(Q(58426, 10**12) < shortfall < Q(58427, 10**12), "short of the legacy target by 5.8426e-8 to 5.8427e-8")

    # 3. the stopped recurrence moments
    F = 32 * M * M * sum(H.values())
    need(F == 118606528512 and sum(H.values()) == 904896, "F = 32*64^2*sum(H)")
    mu1 = (sum(n * Q(r, M) for r, n in H.items()) + eps * F * Q(1, M)) / W
    need(mu1 == Q(2874298095721977, 2890625000000000) and mu1 < Q(199, 200), "mu_1 exact and < 199/200")
    t = 1 - c
    m_lo, m_hi = moment(t, H, W, eps * F)
    need(m_hi - m_lo < Q(1, 10**33), "enclosure width below 1e-33")
    stated = (Q(999998938581682162866772413602, 10**30), Q(999998938581682162866772413603, 10**30))
    need(stated[0] <= m_lo and m_hi <= stated[1], "mu_(576/577) inside the stated 1e-30 interval")
    need(m_hi < Q(999999, 10**6) and m_lo > Q(9999, 10**4), "below 1 - 1e-6; the old 9999/10000 cap is false")
    need(1 / (1 - Q(199, 200)) == 200 and 1 / (1 - Q(999999, 10**6)) == 10**6, "the two induction coefficients")
    # control: dropping the fallback weight moves mu_(576/577) out of the stated interval
    need(moment(t, H, W, 0)[1] < stated[0], "control: the fallback weight is needed for the stated interval")

    # 4. stock fit, wrapper and all-width coefficient
    need(17 ** 128 > 32 * 16 ** 128 and 32780 * Q(17, 16) * 20 == 696575 < 2 ** 20, "fit comparisons as stated")
    # 2^(20 c) < 17/16 and 2k < e at e = 2^20, with k <= 16390 e^c log2 e
    ln2_lo, ln2_hi = ln_bounds(Q(2))
    need(exp_bounds(20 * c * ln2_hi)[1] < Q(17, 16), "2^(20/577) < 17/16")
    need(2 * 16390 * Q(17, 16) * 20 < 2 ** 20, "2k < e at e = 2^20")
    need(801 == 4 * 200 + 1 and 4000000 == 4 * 10**6, "four root calls")
    need(1 - c + c * (c - a1) == 1 - a2, "n^(1-c) w^(c-a1) exponent: (1-c) + c(c-a1) = 1-a2")
    need(exp_bounds((c - a1) * ln2_hi)[1] < Q(17, 16), "2^(c-a1) < 17/16")
    need(a2 < c and 1 - a2 - c > Q(1, 2) and c + Q(1, 2) <= 1 - a2, "a2 < c, 1-a2-c > 1/2")
    need(801 + 4000000 * Q(17, 16) + 32780 + 2 + 1 == 4283584, "coefficient 4283584")
    need(Q(17, 10000) < c < Q(1, 512) and a2 < Q(1, 512) and 20 * a2 < 1, "17/10000 < c < 1/512 and 2^(20 a2) < 2")

    # 5. the gap table
    gaps = {"c-a2": c - a2, "1-a2-c": 1 - a2 - c, "1-a2-c(1-a1)": 1 - a2 - c * (1 - a1), "1-c": 1 - c}
    need(gaps == {"c-a2": Q(2076753, 33292900000000), "1-a2-c": Q(33177502076753, 33292900000000),
                  "1-a2-c(1-a1)": Q(331776, 332929), "1-c": Q(576, 577)}, "gap table")
    need(gaps["1-a2-c(1-a1)"] == (1 - c) ** 2 and min(gaps, key=gaps.get) == "c-a2", "(1-c)^2 and the minimum gap")

    sel_kappa = Q(pinned("certificates/selected-result.json")["kappa"])
    print(json.dumps({
        "status": "PASS_PR4338_B2_CHAIN_CHECK",
        "a2": f"{float(a2):.15f}",
        "a2_minus_C": f"{float(a2 - C):.4e}",
        "a2_vs_selected_bit_lower": f"{float(a2 - Q(sel['bit_lower'])):.4e}",
        "mu_1": f"{float(mu1):.12f}",
        "mu_576_577_gap_to_1": f"{float(1 - m_hi):.6e}",
        "legacy_shortfall": f"{float(shortfall):.6e}",
        "min_gap_c_minus_a2": f"{float(gaps['c-a2']):.4e}",
        "selected_kappa": str(sel_kappa),
        "new_kappa_claimed": False,
    }, indent=1))


if __name__ == "__main__":
    sys.exit(main())
