#!/usr/bin/env python3
"""Independent pinned-source patch for Paureel's tuned paired parameters."""
import difflib
from fractions import Fraction as Q
from pathlib import Path

from make_patch import replace_once
from make_paired_patch import patched_files as paired_files
from tune_paired_parameters import certificate, parameters

ROOT = Path(__file__).resolve().parents[1]
KAPPA_TEX = r"\frac{17523184}{10^{25}}"


def tex(q):
    return str(q.numerator) if q.denominator == 1 else rf"\frac{{{q.numerator}}}{{{q.denominator}}}"


def assembly(text):
    p = parameters()
    result = certificate()
    start = text.index(r"Put $a=296/10^{11}$")
    end = text.index(r"\subsection{Input and transform sizes}", start)
    fixed = r"""Put $a=296/10^{11}$ and $a_{\rm c}=1/10^{11}$. Retain the paired
motifs and choose the following exact rational assembly parameters:
\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-a,\quad \sigma=1-a_{\rm c},\quad
 \beta=\frac{99999912384}{10^{11}},\quad
 \epsilon=\frac{1999999999999}{10^{13}},\\
 \delta=10^{-14},\quad C_1=2,\quad c=\beta a,\quad
 \lambda=1-\frac{1+\beta}{2}a^2,\quad
 \lambda'=1-\beta a^2,\quad \kappa=\frac{17523184}{10^{25}}.
\end{gathered}
\end{equation}
The delicate layer conditions are strict because
\[
 \lambda-\tau(1+c/\beta)=\lambda'-\lambda=\frac{1-\beta}{2}a^2>0,
 \qquad \lambda'-[\sigma+\beta(1-\sigma)]
 =(1-\beta)a_{\rm c}-\beta a^2>0.
\]
Also $\max\{\tau,\sigma\}<\lambda<\lambda'<1$.
The rational stopping test is $e^{10^{11}}<d^{99999912384}$.
Section~\ref{sec:stopped-guard} supplies $C_1=2$ for this stopping rule.
All setup and cost conditions are strict:
\[
 \epsilon<\frac13,\quad 2\epsilon<1,\quad
 \epsilon(1-\tau)<1-\tau,\quad
 \frac34+\delta+\frac54\epsilon<1,\quad
 \epsilon(1+c)<1,\quad \epsilon+\delta<1.
\]

"""
    text = text[:start]+fixed+text[end:]
    text = replace_once(text, r"b^{199/1000}", r"b^{1999999999999/10^{13}}")
    text = replace_once(text, r"d^{1000}\le b^{199}", r"d^{10^{13}}\le b^{1999999999999}")
    gamma = Q(1, 2)+Q(3, 2)*p.epsilon
    text = replace_once(text, r"46b^{1597/2000}", "46b^{"+tex(gamma)+"}<46b^{4/5}")
    start = text.index("Exact substitution", text.index(r"\label{eq:margin-list}"))
    end = text.index("Here $d$", start)
    minimum = Q(result["witness"]["minimum_margin"])
    gap = Q(result["witness"]["absorption_gap"])
    final = r"""Exact substitution gives
\[
 G:=\min_i g_i=g_2=g_3=\epsilon\beta a^2
 =MINIMUM>\kappa=KAPPA.
\]
The Gaussian margin is $g_5=23/(2\cdot10^{14})$; all other margins
exceed $G$. The exact absorption gap is $\rho=G-\kappa=GAP>0$.
This fixed positive gap absorbs every remaining fixed power of $\log p$.
The guard is $O(p^{2\epsilon})=o(p)$, while
$\alpha=\Theta(p^{1/4+\epsilon/4})$ and
$\gamma=O(p^{1/2+3\epsilon/2})=o(p)$.
For $b\ge2^{40}$, the strict bound $\gamma<46b^{4/5}$ implies
$\gamma<b/4$ because $184<2^8$. Also
$K=\Theta(p^{\epsilon c})=o(\ell)$, $K/\log p\to\infty$,
and $\ell=\Theta(p^{1-\epsilon})$. The prime-interval ratio grows as
$p^{1-2\epsilon}$. All eventual construction and precision conditions hold.
Every rational exponent is fixed independently of the input length.

""".replace("MINIMUM", tex(minimum)).replace("KAPPA", KAPPA_TEX).replace("GAP", tex(gap))
    return text[:start]+final+text[end:]


def patched_files():
    for name, old, new in paired_files():
        if name.endswith(("main.tex", "00-introduction.tex")):
            new = replace_once(new, r"\kappa=2^{-59}", r"\kappa="+KAPPA_TEX)
        elif name.endswith("08-assembly.tex"):
            new = assembly(new)
        yield name, old, new


if __name__ == "__main__":
    patch = "".join("".join(difflib.unified_diff(
        old.splitlines(keepends=True), new.splitlines(keepends=True),
        fromfile=f"a/{name}", tofile=f"b/{name}")) for name, old, new in patched_files())
    (ROOT/"patches/h50-paired-tuned.patch").write_text(patch)
    print("Wrote independent conditional h50-paired-tuned.patch")
