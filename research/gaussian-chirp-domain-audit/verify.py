#!/usr/bin/env python3
"""Source-bound, exact audit of the Gaussian chirp domain and block budgets.

Only source composition uses the repository generator. All arithmetic and
window checks below are independent, standard-library implementations.
This is not a formal proof of the analytic or multitape theorems.
"""

import argparse
from fractions import Fraction as Q
import hashlib
import json
from math import gcd, isqrt
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SEED = 64
K_UPPER = Q(891, 196)  # pi / ln(2) < (22/7) / (56/81); see README.


def require(condition, message):
    if not condition:
        raise ValueError(message)


def ceil_div(a, b):
    return -(-a // b)


def ceil_sqrt(n):
    r = isqrt(n)
    return r + (r * r != n)


def ceil_log2(n):
    require(n > 0, "logarithm requires a positive integer")
    return (n - 1).bit_length()


def nearest(j, s, t):
    # floor(t*j/s + 1/2), including negative j and ties rounded upward.
    return (2 * t * j + s) // (2 * s)


def rejected(check, *args):
    try:
        check(*args)
    except ValueError:
        return True
    raise ValueError("negative control was accepted")


def compact(text):
    return re.sub(r"\s+", "", text)


def check_domain(text):
    label = r"\label{lem:no-sort-resampling}"
    require(text.count(label) == 1, "need one no-sort lemma")
    statement = compact(text.split(label)[1].split(r"\end{lemma}")[0])
    for token in (
        r"p>100", r"2\leq\alpha<\sqrtp", "beintegers",
        r"\gcd(s,t)=1", r"\alpha^{-2}\le\theta\le\tfrac14",
    ):
        require(token in statement, "missing domain token: " + token)
    require(text.count(r"\label{lem:chirped-gaussian}") == 1,
            "need one chirped Gaussian lemma")
    require("AssumethehypothesesofLemma~\\ref{lem:no-sort-resampling}" in compact(text),
            "chirp lemma no longer inherits no-sort domain")


def check_assembly(text):
    text = compact(text)
    for token in (
        r"\eta<\theta_i<2\eta/(1-2\eta)=1/(2d-1)\le1/4",
        r"\alpha^2\theta_i>\fracb{16d}\cdot\frac1{4d}=\fracb{64d^2}\geq1",
        r"b\geq64d^2",
    ):
        require(token in text, "missing assembly domain argument: " + token)


def check_sources():
    pins = json.loads((HERE / "SOURCES.json").read_text())
    for path, expected in pins["files_sha256"].items():
        actual = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        require(actual == expected, "source pin changed: " + path)
    sys.path.insert(0, str(ROOT / "scripts"))
    from make_fast_gaussian_patch import patched_files

    rendered = {}
    for name, old, new in patched_files():
        if name.endswith(("07-resampling.tex", "08-assembly.tex")):
            require(old == (ROOT / "upstream" / name).read_text(),
                    "generator did not start from pinned upstream: " + name)
            rendered[name] = new
    resampling = rendered["build/sections/07-resampling.tex"]
    assembly = rendered["build/sections/08-assembly.tex"]
    check_domain(resampling)
    check_assembly(assembly)
    require((ROOT / "notes/fast-gaussian-resampling.tex").read_text() in resampling,
            "the audited note is not inserted verbatim")
    hashes = {name: hashlib.sha256(text.encode()).hexdigest()
              for name, text in rendered.items()}
    require(hashes == pins["generated_sha256"], "generated source changed")
    upper = r"\alpha^{-2}\le\theta\le\tfrac14"
    controls = {
        "removed_upper_domain_bound": rejected(
            check_domain, resampling.replace(upper, r"\alpha^{-2}\le\theta")),
        "removed_lower_domain_bound": rejected(
            check_domain, resampling.replace(upper, r"0<\theta\le\tfrac14")),
        "removed_assembly_upper_bound": rejected(
            check_assembly, assembly.replace(r"1/(2d-1)\le1/4", r"1/(2d-1)")),
    }
    return {"generated_sha256": hashes, "negative_controls": controls}


def budget(p, alpha, forward_precision=None, correction_precision=None):
    require(p >= 101 and 2 <= alpha and alpha * alpha < p, "invalid p, alpha")
    m_s = ceil_sqrt(p) * alpha
    # Smallest integer m with (2*alpha*m)^2 >= p: exact ceil(sqrt(p)/(2*alpha)).
    m_e = ceil_div(ceil_sqrt(p), 2 * alpha)
    l_s, l_e = 3 * m_s + 3, 3 * m_e + 1
    gamma_s, gamma_e = ceil_div(7 * p, 5), 29 * p
    exponent_b = ceil_div(57 * alpha * alpha, 50)
    require(gamma_s <= 2 * 3 * p and gamma_e <= 2 * 34 * p, "Gamma exceeds 2P")
    require(m_s < 2 * p and m_e < 2 * p, "window exceeds cost envelope")
    require(100 * exponent_b <= 115 * p, "input scale exceeds 1.15p bits")
    require(l_s < 4 * p and l_e <= p, "length envelope failed")
    require(4 * ceil_log2(l_s) <= p, "forward logarithm envelope failed")
    require(ceil_log2(l_e) <= p - 1, "correction logarithm envelope failed")
    require(K_UPPER * Q((m_s - 1) ** 2, 4 * alpha * alpha) < gamma_s,
            "forward chirp amplification exceeds Gamma")
    require(K_UPPER * Q(alpha * alpha * (2 * m_e + 1) ** 2, 4) < gamma_e,
            "correction chirp amplification exceeds Gamma")
    require(K_UPPER * Q(alpha * alpha, 4) < exponent_b,
            "input amplification exceeds B")
    need_s = p + gamma_s + ceil_log2(l_s) + 11
    need_e = p + gamma_e + exponent_b + ceil_log2(l_e) + 11
    slack_s = (3 * p if forward_precision is None else forward_precision) - need_s
    slack_e = (34 * p if correction_precision is None else correction_precision) - need_e
    require(slack_s >= 0 and slack_e >= 0, "insufficient certified precision")
    return slack_s, slack_e


def check_arithmetic():
    # Exact endpoints used in the written uniform proof, not a finite theorem claim.
    require(2 * (Q(1, 3) + Q(1, 81)) == Q(56, 81), "log lower bound")
    require(K_UPPER * Q(121, 400) < Q(7, 5), "forward uniform amplification")
    require(K_UPPER * Q(25, 4) < 29, "correction uniform amplification")
    require(K_UPPER / 4 < Q(57, 50), "uniform input amplification")
    for p in range(101, 105):
        require(4 * p <= 2 ** (p // 4), "log-envelope induction base")
    require(Q(53, 20) * 101 + 12 < 3 * 101, "forward uniform precision")
    require(Q(1607, 50) * 101 + 11 < 34 * 101, "correction uniform precision")

    count = 0
    minima = {"forward": None, "correction": None}
    for p in range(101, 1024 + SEED + 1):
        for alpha in range(2, isqrt(p - 1) + 1):
            slacks = budget(p, alpha)
            count += 1
            for name, slack in zip(minima, slacks):
                if minima[name] is None or slack < minima[name]["bits"]:
                    minima[name] = {"bits": slack, "p": p, "alpha": alpha}
    controls = {
        # These violate the published sufficient budget, not a necessary one.
        "forward_P_equals_2p": rejected(budget, 101, 10, 202, None),
        "correction_P_equals_31p": rejected(budget, 101, 10, None, 3131),
    }
    return {"p_inclusive": [101, 1024 + SEED], "all_integer_alpha": "2 <= alpha; alpha^2 < p",
            "pairs_checked": count, "minimum_precision_slack": minima,
            "negative_controls": controls}


def correction_window(s, t, m, start, length=None):
    length = 2 * m + 2 if length is None else length
    origin = nearest(start, s, t)
    for offset in range(m):
        b = nearest(start + offset, s, t) - origin
        require(0 <= b < length, "selected coordinate outside correlation window")
        # Entire inclusive |h|<=m window fits in [start-m, start+2m].
        require(start - m <= start + offset - m and
                start + offset + m <= start + 2 * m, "correction input omitted")


def check_windows():
    pairs = blocks = outputs = 0
    for s in range(2, 64 + SEED + 1):
        for t in range(s + 1, 5 * s // 4 + 1):
            if gcd(s, t) != 1:
                continue
            pairs += 1
            for m in range(1, SEED // 8 + 2):
                # All residues, seed-rotated, including negative periodic representatives.
                for i in range(s):
                    start = (i + SEED) % s - s
                    correction_window(s, t, m, start)
                    blocks += 1
                    outputs += m
                # Every output residue for the forward map, also covering periodic boundaries.
                for k0 in range(t):
                    j0 = (s * k0) // t - m
                    for b in range(m):
                        # Exact integer endpoints of |j - (k0+b)/sigma| < m.
                        first = (s * (k0 + b)) // t - m + 1
                        last = ceil_div(s * (k0 + b), t) + m - 1
                        require(j0 <= first <= last <= j0 + 3 * m + 2,
                                "forward input window omitted a truncated term")

    # Old upstream hypotheses permit this tuple; the GENERATED domain excludes it.
    p, alpha, s, t = 101, 2, 2, 19
    theta = Q(t, s) - 1
    require(theta > Q(p, alpha ** 4) and gcd(s, t) == 1 and t < 2 ** p,
            "old-header counterexample does not satisfy old hypotheses")
    require(alpha * alpha < p and theta > Q(1, 4), "domain control is not separated")
    m = ceil_div(ceil_sqrt(p), 2 * alpha)
    require(nearest(1, s, t) == 10 and 2 * m + 2 == 8,
            "wrong out-of-domain witness")
    controls = {
        "old_header_E_window": rejected(correction_window, s, t, m, 0),
        "shortened_in_domain_E_window": rejected(correction_window, 4, 5, 3, 0, 3),
    }
    return {"s_inclusive": [2, 64 + SEED], "t_domain": "s < t <= 5*s/4, gcd(s,t)=1",
            "m_inclusive": [1, SEED // 8 + 1], "coprime_pairs": pairs,
            "correction_blocks": blocks, "correction_outputs": outputs,
            "forward_residues": "all k0 in [0,t), all offsets in [0,m)",
            "negative_controls": controls,
            "old_header_witness": {"p": p, "alpha": alpha, "s": s, "t": t,
                                   "theta": str(theta), "m": m, "L_B": 2 * m + 2,
                                   "missing_q_1": 10}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write the deterministic audit receipt")
    args = parser.parse_args()
    result = {"status": "PASS_SCOPED_GAUSSIAN_CHIRP_DOMAIN_AUDIT", "assignment_seed": SEED,
              "sources": check_sources(), "arithmetic": check_arithmetic(), "windows": check_windows(),
              "scope": "Source composition and exact bounded arithmetic/window replay; not the full analytic, rounding, tape or multiplication theorem."}
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    receipt = HERE / "RECEIPT.json"
    if args.write:
        receipt.write_text(encoded)
    else:
        require(receipt.read_text() == encoded, "receipt differs; inspect changes before regenerating")
    print(result["status"])
    print("Exact parameter pairs:", result["arithmetic"]["pairs_checked"])
    print("Exact correction windows:", result["windows"]["correction_blocks"])
    print("All 7 negative controls rejected; receipt matches" if not args.write else
          "All 7 negative controls rejected; receipt written")


if __name__ == "__main__":
    main()
