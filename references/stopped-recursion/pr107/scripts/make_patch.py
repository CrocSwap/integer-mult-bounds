#!/usr/bin/env python3
"""Produce a review-only patch; leave the pinned upstream files untouched."""
import difflib
from pathlib import Path
from certify import (balanced, certify_network, certify_parameters, network,
                     proposed, verify_sources, pushed, certify_rational_network)

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text, old, new):
    if text.count(old) != 1:
        raise ValueError(f"Expected one occurrence of {old!r}, got {text.count(old)}")
    return text.replace(old, new, 1)


def patched_files(use_balanced=False):
    verify_sources()
    certify_parameters(balanced(50) if use_balanced else proposed(50))
    for name in ("build/main.tex", "build/sections/00-introduction.tex",
                 "build/sections/08-assembly.tex"):
        original = (ROOT / "upstream" / name).read_text()
        changed = replace_once(original, r"\kappa=2^{-182}", r"\kappa=2^{-154}")
        if name.endswith("08-assembly.tex"):
            for old, new in [
                (r"\lambda=1-2^{-52}", r"\lambda=1-2^{-101}"),
                (r"c=2^{-56}", r"c=2^{-51}"),
                (r"\lambda'=1-2^{-54}", r"\lambda'=1-2^{-102}"),
                (r"\epsilon=2^{-75}", r"\epsilon=2^{-51}"),
                (r"\tau(1+c/\beta)<1-31\cdot2^{-55}<\lambda",
                 r"\tau(1+c/\beta)=1-2^{-100}<1-2^{-101}=\lambda"),
                (r"b^{2^{-75}}", r"b^{2^{-51}}"),
                (r"d^{2^{75}}", r"d^{2^{51}}"),
                (r"g_2=2^{-181},\quad g_3=2^{-129}",
                 r"g_2=2^{-152},\quad g_3=2^{-153}"),
                (r"g_4>2^{-51}", r"g_4>2^{-52}"),
                (r"g_7=2^{-75}", r"g_7=2^{-51}"),
                (r"\min_i g_i=2^{-181}=2\kappa", r"\min_i g_i=2^{-153}=2\kappa"),
            ]:
                changed = replace_once(changed, old, new)
        if use_balanced:
            changed = replace_once(changed, r"\kappa=2^{-154}", r"\kappa=2^{-153}")
            if name.endswith("08-assembly.tex"):
                changed = replace_once(changed, r"\lambda=1-2^{-101}",
                                       r"\lambda=1-3\cdot2^{-102}")
                changed = replace_once(changed, r"\lambda'=1-2^{-102}",
                                       r"\lambda'=1-2^{-101}")
                changed = replace_once(changed, r"1-2^{-100}<1-2^{-101}=\lambda",
                                       r"1-2^{-100}<1-3\cdot2^{-102}=\lambda")
                changed = replace_once(changed, r"g_3=2^{-153}", r"g_3=2^{-152}")
                changed = replace_once(changed, r"\min_i g_i=2^{-153}=2\kappa",
                                       r"\min_i g_i=2^{-152}=2\kappa")
        yield name, original, changed


def extended_files(k, h, log_bound):
    """Review patch for the stronger recurrence comparison and optional new h."""
    cert = certify_network(h, k, log_bound)
    certify_parameters(balanced(k))
    for name, original, changed in patched_files(True):
        # All of these literals in these three files refer to the fixed parameters.
        for old, new in [(153, 3*k+3), (152, 3*k+2), (102, 2*k+2),
                         (101, 2*k+1), (100, 2*k), (52, k+2), (51, k+1), (50, k)]:
            changed = changed.replace(f"2^{{-{old}}}", f"2^{{-{new}}}")
        changed = changed.replace("d^{2^{51}}", f"d^{{2^{{{k+1}}}}}")
        yield name, original, changed

    name = "build/sections/03-motifs.tex"
    original = (ROOT / "upstream" / name).read_text()
    changed = original
    before, after = network(100), network(h)
    if h != 100:
        for key in ("v", "N", "m", "I", "zb", "zc", "Wb", "Wc", "sb", "sc"):
            changed = replace_once(changed, str(before[key]), str(after[key]))
        require_count = changed.count("h=100")
        if require_count != 2:
            raise ValueError("Unexpected ground-set references")
        changed = changed.replace("h=100", f"h={h}")
        changed = replace_once(changed, "=-91/9", f"={9-h}/9")
        changed = changed.replace(r"\binom{97}", f"\\binom{{{h-3}}}")
        changed = replace_once(changed, r"3\cdot97", f"3\\cdot{h-3}")
        changed = replace_once(changed, r"c_{\rm b}=100", f"c_{{\\rm b}}={h}")
        changed = replace_once(changed, r"c_{\rm c}=101", f"c_{{\\rm c}}={h+1}")
        from fractions import Fraction
        for role, key, oldratio in [("b", "Lb", r"\frac{100}{539}"),
                                    ("c", "Lc", r"\frac{101}{539}")]:
            ratio = Fraction(after[key], after["N"])
            changed = replace_once(changed, oldratio,
                                   f"\\frac{{{ratio.numerator}}}{{{ratio.denominator}}}")
        for key in ("eta_b", "eta_c"):
            old, new = before[key], after[key]
            changed = replace_once(changed, f"\\frac{{{old.numerator}}}{{{old.denominator}}}",
                                   f"\\frac{{{new.numerator}}}{{{new.denominator}}}")
    oldproof = r"""Both exact deficits displayed above are greater than $20\cdot2^{-50}$.
Since $m<2^{20}$ and $\log 2<1$, we have $\log m<20$, whence
\[
 m^{1-2^{-50}}
 =m\exp(-2^{-50}\log m)
 >m(1-20\cdot2^{-50})>m(1-\eta)
\]"""
    newproof = rf"""Both exact deficits displayed above are greater than ${log_bound}\cdot2^{{-{k}}}$.
The rational comparison $\sum_{{j=0}}^{{{cert['exp_series_terms']-1}}}{log_bound}^j/j!>m$
gives $m<e^{{{log_bound}}}$ and hence $\log m<{log_bound}$, whence
\[
 m^{{1-2^{{-{k}}}}}
 =m\exp(-2^{{-{k}}}\log m)
 >m(1-{log_bound}\cdot2^{{-{k}}})>m(1-\eta)
\]"""
    changed = replace_once(changed, oldproof, newproof)
    changed = changed.replace("2^{-50}", f"2^{{-{k}}}")
    yield name, original, changed

    for name in ("build/sections/04-swap.tex", "build/sections/05-layers.tex"):
        original = (ROOT / "upstream" / name).read_text()
        changed = replace_once(original, "2^{-50}", f"2^{{-{k}}}")
        if h != 100 and name.endswith("05-layers.tex"):
            changed = replace_once(changed, "h=100", f"h={h}")
            for key in ("m", "Wc", "sc"):
                old = format(before[key], ",").replace(",", "{,}")
                new = format(after[key], ",").replace(",", "{,}")
                changed = replace_once(changed, old, new)
        yield name, original, changed


def texq(q):
    return str(q.numerator) if q.denominator == 1 else rf"\frac{{{q.numerator}}}{{{q.denominator}}}"


def pushed_files(variant):
    """Upgrade h46 with rational saving, strict slack and optional variable beta."""
    p = pushed(variant)
    certify_rational_network()
    certify_parameters(p, generalized_beta=variant != "109", strict_margin=True)
    kappa = r"\frac{29}{5\cdot10^{33}}" if variant == "rational" else rf"2^{{-{variant}}}"
    definitions = {
        "109": r"\beta=\frac12,\quad \epsilon=\frac{3a}{4},\quad c=\frac a2,\\ \lambda=1-\frac{3a^2}{4},\quad \lambda'=1-\frac{a^2}{2}",
        "108": r"\beta=\frac34,\quad \epsilon=c=\frac{3a}{4},\\ \lambda=1-\frac{7a^2}{8},\quad \lambda'=1-\frac{3a^2}{4}",
        "rational": r"\beta=\frac{999}{1000},\quad \epsilon=\frac{999a}{1000},\quad c=\frac{998a}{1000},\\ \lambda'=1-ac,\quad \lambda=\frac{\lambda'+(1-a)(1+c/\beta)}{2}",
    }
    for name, original, changed in extended_files(36, 46, 12):
        if name.endswith(("main.tex", "00-introduction.tex")):
            changed = replace_once(changed, r"\kappa=2^{-111}", rf"\kappa={kappa}")
        elif name.endswith("03-motifs.tex"):
            start = changed.index("Both exact deficits displayed above")
            end = changed.index(r"\]", start)+2
            changed = changed[:start] + r"""Put $a=9/500000000000$ and $L=5743/500$.
Both exact deficits displayed above exceed $aL$.
Here is a rational certificate for $\log m<L$. For $1\le x\le2$, put
$z=(x-1)/(x+1)$ and
\[
 S(x)=2\sum_{j=0}^{23}\frac{z^{2j+1}}{2j+1},\qquad
 R(x)=\frac{2z^{49}}{49(1-z^2)}.
\]
The series for $\log x$ gives $S(x)\le\log x\le S(x)+R(x)$.
Since $m=97336$, exact rational comparison gives
\[
 \log m\le16(S(2)+R(2))+S(m/2^{16})+R(m/2^{16})<L.
\]
Consequently, for either deficit $\eta$,
\[
 m^{1-a}=m\exp(-a\log m)>m(1-aL)>m(1-\eta).
\]""" + changed[end:]
            changed = changed.replace("2^{-36}", r"\frac{9}{500000000000}")
        elif name.endswith(("04-swap.tex", "05-layers.tex")):
            changed = replace_once(changed, "2^{-36}", r"\frac{9}{500000000000}")
            if variant != "109" and name.endswith("05-layers.tex"):
                changed = replace_once(changed, r"Fix \(\beta=1/2\),", r"Fix a rational \(0<\beta<1\),")
                changed = replace_once(changed, r"\beta=\frac12", r"0<\beta<1\quad(\beta\in\mathbb Q)")
                anchor = "\\subsection{An explicit guard-width bound}"
                changed = replace_once(changed, anchor, r"""The argument uses only $0<\beta<1$. The stopping comparison is
effective for fixed rational $\beta$: if $\beta=u/v$, compare $e^v<d^u$.
It takes polynomial descriptor work. The recursion depth remains at most
$\lceil\log_m d\rceil$, and every leaf still has $e\le d$; hence the
guard-width argument below and the fixed tape count are unchanged.

"""+anchor)
        elif name.endswith("08-assembly.tex"):
            start = changed.index("Take the following fixed rational numbers:")
            end = changed.index("The strict final inequality", start)
            changed = changed[:start] + rf"""Put $a=9/500000000000$ and take the following fixed rational numbers:
\begin{{equation}}\label{{eq:fixed-parameters}}
\begin{{gathered}}
 \tau=\sigma=1-a,\qquad \delta=\frac1{{16}},\qquad C_1=20,\\
 {definitions[variant]},\\ \kappa={kappa}.
\end{{gathered}}
\end{{equation}}
Exact substitution gives
\[
 \max\{{\tau,\sigma\}}<\tau(1+c/\beta)<\lambda<\lambda'<1,
 \qquad \sigma+\beta(1-\sigma)<\lambda'.
\]
""" + changed[end:]
            changed = replace_once(changed, r"b^{2^{-37}}", rf"b^{{{texq(p.epsilon)}}}")
            changed = replace_once(changed, r"d^{2^{37}}\le b",
                                   rf"d^{{{p.epsilon.denominator}}}\le b^{{{p.epsilon.numerator}}}")
            start = changed.index("Direct substitution gives", changed.index(r"\label{eq:margin-list}"))
            end = changed.index("Here $d^2$", start)
            from certify import margins
            g = min(margins(p).values())
            changed = changed[:start] + rf"""Direct substitution gives $g_2=g_3=\epsilon ac$ and
\[
 G:=\min_i g_i=\epsilon ac={texq(g)}>\kappa.
\]
Indeed, $g_1,g_6>1/2$, $g_5>1/8$, $g_4>a/2000$ and
$g_7>a/2$; each exceeds $G$. Put $\rho=G-\kappa>0$.
This fixed positive gap covers any remaining fixed power of $\log p$.

""" + changed[end:]
            changed = replace_once(changed,
                "Each of the seven displayed powers is at most $1-2\\kappa$ by\n"
                "\\eqref{eq:margin-list}.  Any fixed power of $\\log p$ is at most $p^\\kappa$",
                "Each of the seven displayed powers is at most $1-G$ by\n"
                "\\eqref{eq:margin-list}. Any fixed power of $\\log p$ is at most $p^\\rho$")
        yield name, original, changed


if __name__ == "__main__":
    variants = [("frozen-154.patch", patched_files()),
                ("balanced-153.patch", patched_files(True)),
                ("same-network-129.patch", extended_files(42, 100, 14)),
                ("h46-111.patch", extended_files(36, 46, 12))]
    variants += [(f"h46-{v}.patch", pushed_files(v)) for v in ("109", "108", "rational")]
    for filename, files in variants:
        patch = "".join("".join(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=f"a/{name}", tofile=f"b/{name}"))
            for name, old, new in files)
        path = ROOT / "patches" / filename
        path.parent.mkdir(exist_ok=True)
        path.write_text(patch)
        print(f"Wrote {path.relative_to(ROOT)}; conditional research patch, not a validated theorem")
