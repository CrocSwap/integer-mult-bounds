#!/usr/bin/env python3
"""Separate review patches for the direct-axis scheduling audit."""
import difflib
from pathlib import Path

from certify import A, margins, verify_sources
from make_patch import patched_files, pushed_files, replace_once, texq
from nonadjacent import certificate, parameters

ROOT = Path(__file__).resolve().parents[1]


def layout_change(name, text):
    if name.endswith("07-resampling.tex"):
        text = replace_once(text, r"Tp\,d^2(1+\ell^\tau)", r"Tp\,d(1+\ell^\tau)")
        start = text.index("The descriptor records which coordinate")
        end = text.index("Since $t_i\\geq r/2$", start)
        text = text[:start] + r"""The descriptor records which named coordinate each physical address field
holds, together with its width and valid range. Before processing axis $i$,
interchange its entire address field with the innermost field; after processing
its lines, undo precisely that interchange. If it is already innermost, no
interchange is needed. Thus each axis starts and ends in the original field
order, and all axes together require at most $2(d-1)$ field interchanges.

These interchanges need not be adjacent. Lemma~\ref{lem:chunk-swap} permits
an arbitrary intervening field $[G]$, obtained by collapsing the intervening
axes, and a suffix containing the complete coefficient word. For widths that
differ by one, use the explicit nonadjacent construction following that lemma.
Suppressing the prefix and suffix, its two cases are
\[
 (e,x,G,y)\longmapsto(e,y,G,x)\longmapsto(y,G,e,x),
\]
\[
 (x,G,e,y)\longmapsto(e,x,G,y)\longmapsto(e,y,G,x),
\]
where $x,y$ have equal bit width and $e$ is one bit. Each uses one equal-width
interchange and one single-bit move. Empty equal-width pieces require no swap.
The intervening axes keep their internal order, and each complete record keeps
its bit order. The cost of a full field interchange is
$O(Tp(1+\ell^\tau))$, including workspace cleanup.

At a completed interchange the descriptor moves the coordinate names, widths,
and validity bounds with their fields. A processed line therefore still runs
through the same named coordinate in increasing numerical order. Other named
coordinates retain their values; their physical order is immaterial to the
validity test. After the line algorithm, the inverse interchange restores the
original field order. The padded box keeps its full physical size throughout.
Invalid entries remain zero at the completed axis-map boundaries specified
above; temporary bit moves and the internal arithmetic of a swap need not
preserve an intermediate validity mask. The completed permutations and their
inverses are exact, so the contraction and error arguments do not change.

The list and collapsed descriptors are stored on tapes, not in new heads.
Here $t_i\ge2$, so $d\le\log_2T$. With $V$ the physical bit volume,
each collapsed length is at most $V$, and the list of axis names, ranges,
and widths has length polynomial in $\log(2V)$. Ordinary integer arithmetic
therefore prepares each call descriptor in $\operatorname{poly}(\log(2V))=O(V)$
time. Each primitive reuses its fixed work tapes. Thus all exposure and
restoration costs
$O(Tp\,d(1+\ell^\tau))$.

""" + text[end:]
    elif name.endswith("08-assembly.tex"):
        start = text.index("The axis widths are $\\ell$ or $\\ell-1$.")
        end = text.index("This construction describes payload movement", start)
        text = text[:start] + r"""The axis widths are $\ell$ or $\ell-1$. Reverse the axis order by
interchanging physical positions $j$ and $d+1-j$ for
$j=1,\ldots,\lfloor d/2\rfloor$. Every pair is disjoint, so this uses
$\lfloor d/2\rfloor$ full-field interchanges, not a sequence of adjacent moves.
Each is covered by Lemma~\ref{lem:chunk-swap} and its subsequent one-bit-width
extension, with all intervening fields collapsed into its spectator gap.
Its cost is $O(Tp(1+\ell^\tau))$. Keep each axis name and width attached
to that field in the descriptor. The final order is exactly
$(a_1,\ldots,a_d)$, as required by the triangular updates above. Their target
order and their requirement that controls precede targets are unchanged.
The inverse uses the reversed interchange schedule after recovering the digits.

The completed reversal and its inverse preserve complete records and their
internal bit order. Padding is inserted before the forward reversal and
removed only after the inverse reversal, so the insertion/deletion enumeration
is unchanged. Since $d\le\log_2T$, the named-axis list and all collapsed
lengths have polynomial length in $\log(2Tp)$. Each call descriptor can thus
be prepared in $\operatorname{poly}(\log(2Tp))=O(Tp)$ time. The $d$ controlled
rotations and the padding scans cost $O(dTp)$ as above. Therefore $\Phi$,
its inverse, and their padding operations cost
\[
 O\bigl(Tp\,d(1+\ell^\tau)\bigr).
\]
""" + text[end:]
        text = replace_once(text, r"\epsilon(2-\tau)<1-\tau", r"\epsilon(1-\tau)<1-\tau")
        text = replace_once(text,
            r"CRT and axis layouts & $d^2(1+\ell^\tau)$ & $\tau+\epsilon(2-\tau)$",
            r"CRT and axis layouts & $d(1+\ell^\tau)$ & $\tau+\epsilon(1-\tau)$")
        text = replace_once(text, r"g_4&=1-\tau-\epsilon(2-\tau)",
                             r"g_4&=(1-\tau)(1-\epsilon)")
        text = replace_once(text, r"Here $d^2$ is absorbed by $d^2\ell^\tau$",
                             r"Here $d$ is absorbed by $d\ell^\tau$")
        old = r"""Axis exposure and restoration require $O(d^2)$ adjacent axis moves.
Each costs $O(V(1+\ell^\tau))$: peel a single excess bit when widths
differ by one, exchange their equal-width parts, and restore the bit."""
        new = r"""Axis exposure and restoration require $O(d)$ nonadjacent full-field
interchanges by Lemma~\ref{lem:tensor-resampling}; the CRT reversal also
uses $O(d)$ such interchanges. Each costs $O(V(1+\ell^\tau))$, using the
arbitrary spectator gap and the one-bit-width extension of
Lemma~\ref{lem:chunk-swap}. Thus this row has exponent
$\epsilon+\tau(1-\epsilon)$ rather than $2\epsilon+\tau(1-\epsilon)$."""
        text = replace_once(text, old, new)
    return text


def layout_only_files():
    verify_sources()
    for name in ("build/sections/07-resampling.tex", "build/sections/08-assembly.tex"):
        old = (ROOT/"upstream"/name).read_text()
        yield name, old, layout_change(name, old)


def result_files(network):
    """Standalone combined patch, retaining beta=1/2 and C1=20."""
    certificate()
    p = parameters(network)
    k = 78 if network == "h46" else 107
    base = pushed_files("109") if network == "h46" else patched_files(True)
    for name, old, new in base:
        if name.endswith(("main.tex", "00-introduction.tex")):
            previous = 109 if network == "h46" else 153
            new = replace_once(new, rf"\kappa=2^{{-{previous}}}", rf"\kappa=2^{{-{k}}}")
        elif name.endswith("08-assembly.tex"):
            start = new.index("Put $a=9/500000000000$" if network == "h46" else "Take the following fixed rational numbers:")
            end = new.index("The strict final inequality", start)
            a = r"9/500000000000" if network == "h46" else r"2^{-50}"
            new = new[:start]+rf"""Put $a={a}$ and choose
\begin{{equation}}\label{{eq:fixed-parameters}}
\begin{{gathered}}
 \tau=\sigma=1-a,\quad \beta=\frac12,\quad \delta=\frac1{{16}},\quad C_1=20,\\
 \epsilon=\frac1{{40}},\quad c=\frac a2,\quad
 \lambda=1-\frac{{3a^2}}{{4}},\quad \lambda'=1-\frac{{a^2}}{{2}},\quad
 \kappa=2^{{-{k}}}.
\end{{gathered}}
\end{{equation}}
The layer conditions follow from
\[
 \tau(1+c/\beta)=(1-a)(1+a)=1-a^2<\lambda<\lambda'<1,
 \qquad \sigma+\beta(1-\sigma)=1-a/2<\lambda'.
\]
"""+new[end:]
            if network == "h46":
                from certify import pushed
                previous = pushed("109").epsilon
                new = replace_once(new, rf"b^{{{texq(previous)}}}", r"b^{1/40}")
                new = replace_once(new, rf"d^{{{previous.denominator}}}\le b^{{{previous.numerator}}}", r"d^{40}\le b")
            else:
                new = replace_once(new, r"b^{2^{-51}}", r"b^{1/40}")
                new = replace_once(new, r"d^{2^{51}}\le b", r"d^{40}\le b")
            start = new.index("Direct substitution gives", new.index(r"\label{eq:margin-list}"))
            end = new.index("Here $d^2$", start)
            new = new[:start]+rf"""Direct substitution, using the improved nonadjacent layout bound, gives
\[
 G:=\min_i g_i=g_2=g_3=\frac{{a^2}}{{80}}>\kappa=2^{{-{k}}}.
\]
Indeed, $g_1>1/2$, $g_4=39a/40$, $g_5=3/20$,
$g_6=73/80$, and $g_7=1/40$, all exceeding $G$.
Put $\rho=G-\kappa>0$; this fixed gap absorbs the logarithmic factors.

"""+new[end:]
            if network == "frozen":
                new = replace_once(new,
                    "Each of the seven displayed powers is at most $1-2\\kappa$ by\n"
                    "\\eqref{eq:margin-list}.  Any fixed power of $\\log p$ is at most $p^\\kappa$",
                    "Each of the seven displayed powers is at most $1-G$ by\n"
                    "\\eqref{eq:margin-list}. Any fixed power of $\\log p$ is at most $p^\\rho$")
            new = layout_change(name, new)
        yield name, old, new
    name = "build/sections/07-resampling.tex"
    old = (ROOT/"upstream"/name).read_text()
    yield name, old, layout_change(name, old)


if __name__ == "__main__":
    variants = [("nonadjacent-layout.patch", layout_only_files()),
                ("frozen-nonadjacent-107.patch", result_files("frozen")),
                ("h46-nonadjacent-78.patch", result_files("h46"))]
    for filename, files in variants:
        patch = "".join("".join(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=f"a/{name}", tofile=f"b/{name}")) for name, old, new in files)
        (ROOT/"patches"/filename).write_text(patch)
        print(f"Wrote patches/{filename}; conditional direct-axis audit patch")
