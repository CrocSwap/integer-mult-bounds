#!/usr/bin/env python3
"""Alternative retained-total/compact patch against the pinned source."""
from pathlib import Path
import difflib

ROOT = Path(__file__).resolve().parents[1]
from make_compact_control_patch import patched_files as compact_files
from make_patch import replace_once
from retained_complex import certificate


def shared_retained_section():
    return r"""\subsection{Shared exclusion sums with retained totals}
\label{sec:shared-retained-complex}
This composition uses eumemic's Claude-assisted shared-exclusion circuit
from PR~\#3, commit \texttt{dfe5b818aad4d386cb5dd7d76df108088107765d},
with dleen's grouped-retention and stage-sharing construction above.
The preceding rectangle variant remains an independent construction.
At $h=24$ retain the existing roots
$E_i=\sum_{T\not\ni i}x_T$ for $i<h-1$ and $C_*=\sum_Tx_T$.
Introduce the omitted exclusion $E_{h-1}$ only for this derivation.
On source contributions $\sum_{i=0}^{h-1}E_i=(h-3)C_*$, so the central scatter is
\[
 (Rz)_S=\begin{cases}
 C_*-\frac12\sum_{i\in S}E_i,&h-1\notin S,\\
 \frac{5-h}{2}C_*+\frac12\sum_{i<h-1,\ i\notin S}E_i,&h-1\in S.
 \end{cases}
\]
Its source coefficient is $(|S\cap T|-1)/2$. The unchanged side map
cancels the off-diagonal coefficients. The same reversible wrapper restores
arbitrary dirty scratch, without imposing the source relation on that scratch.
Label $E_i$ by $F_{[h]\setminus\{i\}}$ and $C_*$ by $F$.
Coordinate and pair-star node inclusions, output orthogonality, and
nonalternating residuals are checked on every activated node by the exact
finite generator. These totals have unit-line or zero complements.
The common low/full scatter, complemented reverse mixer, tensor boundaries,
weight-27 endpoints and stage-1/3 join argument above therefore apply with
local loss $\ell=(h-1)^2+h=553$.

Implement the coefficient $-(h-5)/2$ as $h-5$ updates of $-1/2$.
The first grouped pass performs all $E_i$ updates and one global update;
the remaining $h-6$ passes touch only $C_*$ and last-point targets.
These commuting passes share their frame and add no edge rank.
Their two occurrences add $2(h-6)$ scalar gates per invocation.
Every actual coefficient has magnitude at most one and denominator at most two.

\begin{proposition}\label{prop:shared-retained-complex-interface}
The combined motif has the all-role scalar and binary phase contract above,
with $m=13824$, $R_{\rm aux}=90950$, $W=761750114048$,
$L_{\rm loss}=6796219584$, and $s=10530430586099072$.
It supports $\sigma=1-2970/10^{11}$ under the retained compact-control
and analytic interfaces.
\end{proposition}
\begin{proof}
The base has $66518$ additions and $24288$ side outputs.
Retention activates $120$ ancestors and adds $24$ outputs, hence
$C=66638$, $q=24312$ and $R_{\rm aux}=C+q$.
With $v=2024$ and $N=v^3$, stage sharing gives
$W=2N+2v^2R_{\rm aux}$ and $L_{\rm loss}=3v^2\ell$.
Thus $D=2N-2L_{\rm loss}=2990500480$, $s=Wm-D$, and
\[
 \eta=\frac{D}{Wm}=\frac{365}{1285272576},\qquad
 \eta-\frac{2970}{10^{11}}\frac{477}{50}
 =\frac{406952569}{627574500000000000}>0.
\]
The exact logarithm enclosure gives $\log m<477/50$.
The actual scalar gate count is
$3v^2(8v+4C+4+2(h-6))=3475338442752<12W$.
The existing stopped-depth inequalities, including $s<m^5$, hold with these
constants. The normalized passes preserve the magnitude and denominator
premises of that guard. The recurrence and strict consumer comparisons then
follow as in the retained construction. Full source coefficients, retained
integer multiplicities and both compiled frame orientations are certified;
small controls cover dirty scratch and each physical phase edge.
The general tensor and fixed-tape transfer remain the supplied written
arguments and imported interfaces, rather than a full formal theorem.
\end{proof}
"""


def patched_files():
    result = certificate()
    n = result["main"]["counts"]
    retained = (ROOT / "notes/retained-complex-construction.tex").read_text()
    for name,old,new in compact_files():
        if name.endswith(("main.tex","00-introduction.tex")):
            new=replace_once(new,r"\kappa=83/10^{12}",r"\kappa=591/10^{12}")
            if name.endswith('main.tex'):
                new = new.replace('Douglas Colkitt (modifications)',
                                  'Douglas Colkitt, eumemic and dleen (modifications)')
                new = new.replace(r'\small Compact-control modifications: Douglas Colkitt}',
                    r'\small Compact-control modifications: Douglas Colkitt\\'+'\n'+
                    r'\small Shared-exclusion and retained-total extensions: eumemic and dleen}')
                new = new.replace('and retained project refinements, prepared with assistance from OpenAI Codex.',
                    "and retained project refinements, together with eumemic's shared-exclusion\n"
                    "and dleen's retained-total extensions, prepared with Claude and OpenAI Codex assistance.")
        elif name.endswith("03-motifs.tex"):
            new += "\n"+retained+"\n"+shared_retained_section()
        elif name.endswith("05-layers.tex"):
            new=new.replace("prop:compact-complex-interface","prop:shared-retained-complex-interface")
            replacements=((r"m=m_{\rm c}=15625",r"m=m_{\rm c}=13824"),
                          (r"W=W_{\rm c}=58645352620000",f"W=W_{{\\rm c}}={n['W']}"),
                          (r"s=s_{\rm c}=916333630984500000",f"s=s_{{\\rm c}}={n['s']}"),
                          (r"\sigma=1-418/10^{12}",r"\sigma=1-2970/10^{11}"))
            for before, after in replacements:
                new = replace_once(new, before, after)
        elif name.endswith("08-assembly.tex"):
            replacements=((r"a_{\rm c}=418/10^{12}",r"a_{\rm c}=2970/10^{11}"),
                (r"\chi=\tau+(1-\beta)(\sigma-\tau)",r"\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}"),
                (r"c=\frac15",r"c=1"),
                (r"\lambda=1-\frac{1671}{4\cdot10^{12}}",r"\lambda=1-\frac{2959}{10^{12}}"),
                (r"\lambda'=1-\frac{167}{4\cdot10^{11}}",r"\lambda'=1-\frac{2958}{10^{12}}"),
                (r"\kappa=\frac{83}{10^{12}}>2^{-34}",r"\kappa=\frac{591}{10^{12}}>2^{-31}"),
                (r"\frac{333833}{4\cdot10^{15}}>\frac{83}{10^{12}}",r"\frac{2956521}{5\cdot10^{15}}>\frac{591}{10^{12}}"),
                (r"K=\Theta(p^{1999/50000})",r"K=\Theta(p^{1999/10000})"))
            for before, after in replacements:
                new = replace_once(new, before, after)
        yield name,old,"% Retained-total compact-control alternative, October 7, 2026.\n"+new


def patch_text():
    return "".join(
        "".join(difflib.unified_diff(
            old.splitlines(keepends=True), new.splitlines(keepends=True),
            fromfile=f"a/{name}", tofile=f"b/{name}"))
        for name, old, new in patched_files())


if __name__ == "__main__":
    (ROOT/"patches/retained-complex-31.patch").write_text(patch_text())
    print("PASS pinned-source retained-total alternative; kappa=591/10^12")
