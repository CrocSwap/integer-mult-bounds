#!/usr/bin/env python3
"""Conditional 2^-76 witness, composing two previously audited extensions."""
import difflib
import json
from fractions import Fraction as Q
from pathlib import Path

from certify import (A, Parameters, certify_parameters, certify_rational_network,
                     dyadic, margins, require, verify_sources)
from make_patch import pushed_files, replace_once
from make_nonadjacent_patch import result_files

ROOT = Path(__file__).resolve().parents[1]


def parameters(a=A, kappa=dyadic(76)):
    return Parameters(1-a, 1-a, Q(1, 21), 9*a/10,
                      1-19*a*a/20, 1-9*a*a/10, kappa, beta=Q(9, 10))


def certificate():
    p = parameters()
    cert = certify_parameters(p, generalized_beta=True, strict_margin=True,
                              layout_model="nonadjacent")
    require(min(margins(p, layout_model="nonadjacent").values()) == 3*A*A/70,
            "Wrong limiting margin")
    # Three necessary inequalities imply c < a/(1-a), epsilon < 1/20.
    upper = A*A/(20*(1-A))
    require(p.kappa < upper < dyadic(75), "Wrong scope of tuning upper bound")
    return {"upstream_commit": verify_sources(),
            "scope": "Conditional on upstream interfaces, h46 network audit, nonadjacent routing, and variable-beta extension",
            "network": certify_rational_network(), "witness": cert,
            "remaining_exponents": {"dimension": "1/21", "ell": "20/21",
                "guard": "20/21", "alpha": "23/84", "gamma": "25/42",
                "prime_interval": "19/21", "chunk_width": str(p.epsilon*p.c)},
            "transfer": {"a_range": "0 < a < 1/16", "minimum_margin": "3*a^2/70",
                         "margin_ratio_to_previous_recipe": "24/7",
                         "conditions": "compatible primitive exponents tau=sigma=1-a and guard C1=20"},
            "fixed_exponents_upper_bound": {
                "value": str(upper), "formula": "a^2/(20*(1-a))",
                "scope": "fixed tau=1-a, C1=20 and current layer inequalities; any beta in (0,1)",
                "strictly_below_2^-75": True,
                "optimality_claim": False}}


def patched_files():
    certificate()
    generalized = {name: new for name, old, new in pushed_files("108")}
    for name, old, new in result_files("h46"):
        if name.endswith(("main.tex", "00-introduction.tex")):
            new = replace_once(new, r"\kappa=2^{-78}", r"\kappa=2^{-76}")
        elif name.endswith("05-layers.tex"):
            new = generalized[name]
        elif name.endswith("08-assembly.tex"):
            start = new.index("Put $a=9/500000000000$")
            end = new.index("The strict final inequality", start)
            new = new[:start] + r"""Put $a=9/500000000000$ and choose
\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=\sigma=1-a,\quad \beta=\frac9{10},\quad \delta=\frac1{16},\quad C_1=20,\\
 \epsilon=\frac1{21},\quad c=\frac{9a}{10},\quad
 \lambda=1-\frac{19a^2}{20},\quad \lambda'=1-\frac{9a^2}{10},\quad
 \kappa=2^{-76}.
\end{gathered}
\end{equation}
The layer conditions follow from
\[
 \tau(1+c/\beta)=1-a^2<\lambda<\lambda'<1,
 \qquad \sigma+\beta(1-\sigma)=1-a/10<\lambda'.
\]
The rational stopping comparison is $e^{10}<d^9$. The generalized
layer proof retains the original guard exponent; $\epsilon C_1=20/21<1$.
""" + new[end:]
            new = replace_once(new, r"b^{1/40}", r"b^{1/21}")
            new = replace_once(new, r"d^{40}\le b", r"d^{21}\le b")
            start = new.index("Direct substitution, using the improved")
            end = new.index("Here $d$", start)
            new = new[:start] + r"""Direct substitution, using the nonadjacent layout bound, gives
\[
 G:=\min_i g_i=g_2=g_3=\frac{3a^2}{70}>\kappa=2^{-76}.
\]
Indeed, $g_1>1/2$, $g_4=20a/21$, $g_5=13/112$,
$g_6=299/336$, and $g_7=1/21$, all exceeding $G$.
The guard is $d^{20}=\Theta(p^{20/21})=o(p)$;
$\alpha=\Theta(p^{23/84})$ and $\gamma=O(p^{25/42})=o(p)$.
Also $K=\Theta(p^{3a/70})=o(\ell)$ and $K/\log p\to\infty$,
while $\ell=\Theta(p^{20/21})$. Record length remains superpolynomial,
and the prime-interval ratio grows as $p^{19/21}$.
Put $\rho=G-\kappa>0$; this fixed gap absorbs the logarithmic factors.

""" + new[end:]
        yield name, old, new


if __name__ == "__main__":
    result = certificate()
    (ROOT/"certificates/routing-tuned.json").write_text(
        json.dumps(result, indent=2, sort_keys=True)+"\n")
    patch = "".join("".join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{name}", tofile=f"b/{name}")) for name, old, new in patched_files())
    (ROOT/"patches/h46-nonadjacent-76.patch").write_text(patch)
    print("PASS conditional 2^-76: minimum margin", result["witness"]["minimum_margin"])
