#!/usr/bin/env python3
"""Independent pinned-source patch for the compact-control layer witness."""
import difflib
from pathlib import Path

from compact_control_layer import certificate
from make_patch import replace_once
from make_paired_patch import patched_files as paired_files

ROOT=Path(__file__).resolve().parents[1]


def note(name):return (ROOT/'notes'/name).read_text()


def layers(text):
    text=text.replace('prop:complex-motif-interface','prop:compact-complex-interface')
    text=replace_once(text,r'\label{sec:fast-butterfly-layers}',r'''\label{sec:fast-butterfly-layers}
Throughout this section, the complex constants are
$m=m_{\rm c}=15625$, $W=W_{\rm c}=58645352620000$ and
$s=s_{\rm c}=916333630984500000$ from
Proposition~\ref{prop:compact-complex-interface}. The bit-swap primitive
retains its separate arity $m_{\rm b}=125000$ and exponent
$\tau=1-296/10^{11}$.''')
    text=replace_once(text,'We implement those\nchanges by moving whole address chunks.',
        'We implement those\nchanges by moving compact dirty-control fields with exact exceptional repair.')
    start=text.index(r'\subsection{Packed changes of selected address bits}')
    end=text.index(r'\subsection{Batching a common layer on a fixed number of tapes}',start)
    # Keep the original wide-slot lemma: the grouped-rectangle appendix
    # still cites its general contract. Only the accelerated layer switches
    # to the new compact-control primitive.
    retained=text[start:end]
    retained=replace_once(retained,r'\label{sec:packed-selected-bits}',r'''\label{sec:packed-selected-bits}
This wide-slot implementation remains available for the grouped-rectangle
appendix. The accelerated layer below instead uses the compact-control
construction of Section~\ref{sec:compact-control-movement}.''')
    text=text[:start]+retained+note('compact-control-movement.tex')+'\n'+text[end:]
    text=replace_once(text,r'O\bigl(V((eK)^\tau+1)\bigr)',r'O\bigl(V((e\log p)^\tau+1)\bigr)')
    text=replace_once(text,r'''Lemma~\ref{lem:packed-selected-bit-rectangle} gives the stated bound for a row addition.''',
        r'''Proposition~\ref{prop:compact-selected-addition} gives the stated bound for a row addition,
using the complete compact fields constructed below.''')
    start=text.index(r'\paragraph{Where the rows come from.}')
    end=text.index(r'\subsection{A guard bound using the actual stopping depth}',start)
    text=text[:start]+note('compact-control-layout.tex')+'\n'+text[end:]
    start=text.index(r'\subsection{A guard bound using the actual stopping depth}')
    end=text.index(r'\begin{proposition}[Simultaneous normalized butterfly layer]',start)
    text=text[:start]+note('compact-control-guard.tex')+'\n'+text[end:]
    start=text.index('Fix\n',text.index(r'\begin{proposition}[Simultaneous normalized butterfly layer]'))
    end=text.index('Fix positive constants',start)
    text=text[:start]+r'''Fix $\tau=1-296/10^{11}$ and $\sigma=1-418/10^{12}$.
Let $c,\epsilon,\lambda,\lambda',\beta,\zeta$ be fixed positive rational numbers
with $0<\beta<1$, and put
\[
 C_1=5-4\beta+\zeta,\qquad
 \chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}.
\]
Require
\[
 \max\{\tau,\sigma,\chi\}<\lambda<\lambda'<1,\qquad
 \max\{\sigma+\beta(1-\sigma),1-c,0\}<\lambda',\qquad
 \epsilon C_1<1.
\]
''' +text[end:]
    text=replace_once(text,r''' C_0=128m\bigl(s_{\rm c}+64(W_{\rm c}+m+1)^3\bigr)^2,''',
        r''' C_0=\left\lceil\max\{128mB^2,18mB^2(1+1/\zeta)\}\right\rceil,
 \qquad B=s_{\rm c}+64(W_{\rm c}+m+1)^3,''')
    text=replace_once(text,'The packed\nselected-bit procedure supplies the binary basis changes.',
        'The compact-control\nselected-bit procedure supplies the binary basis changes.')
    start=text.index('Uniformly for large $p$, the bands give')
    end=text.index('The row construction and the recurrence analysis',start)
    text=text[:start]+r'''Uniformly for large $p$, the bands give $f\le d\le p$ and
\[
 K\ge\tfrac12a_d^cp^{\epsilon c},\qquad
 r\ge2^{(a_r/b_d)p^{1-\epsilon}}.
\]
Thus $K/\log p\to\infty$, $r$ dominates every fixed polynomial, and
$G=4\lceil\log_2p\rceil+6$ eventually obeys
$K\ge G+4\lceil\log_2p\rceil+10$. Every role stream retains both complete
front fields and the complete back field outside its row index. The above
$A_*\le C_Ap$ bound applies to each compact rectangle. For its repair,
\[
 \frac{A_*^3}{R_{\rm g}}\le\frac{C_A^3p^2}{2r},\qquad
 \delta A_*\left(1+\frac{A_*}{R_{\rm g}}\right)
 \le\frac{5C_A}{128p^2}\left(1+\frac{C_A}{2r}\right).
\]
The wider-control rotation bound is also uniform, because every polynomial
offset charge divided by $R_{\rm g}$ tends to zero. Hence
Proposition~\ref{prop:compact-selected-addition} costs
$O(M_{\rm child}R_{\rm g}((f\log p)^\tau+1))$ with a common constant.
Reservation preprocessing costs
$O(V(\log(2d)+d^{\max\{1-c,0\}}\log p+1))$ and is included by the
strict condition $1-c<\lambda'$.
''' +text[end:]
    return text


def assembly(text):
    start=text.index('Put $a=296/10^{11}$')
    end=text.index(r'\subsection{Input and transform sizes}',start)
    text=text[:start]+r'''Put $a=296/10^{11}$ and $a_{\rm c}=418/10^{12}$.
Choose
\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-a,\quad\sigma=1-a_{\rm c},\quad
 \beta=\frac1{1000},\quad\zeta=\frac1{10000},\quad
 C_1=\frac{49961}{10000},\\
 \epsilon=\frac{1999}{10000},\quad c=\frac15,\quad\delta=\frac1{10^6},\\
 \lambda=1-\frac{1671}{4\cdot10^{12}},\quad
 \lambda'=1-\frac{167}{4\cdot10^{11}},\quad
 \kappa=\frac{83}{10^{12}}>2^{-34}.
\end{gathered}
\end{equation}
The new compact-control recurrence has
$\chi=\tau+(1-\beta)(\sigma-\tau)$, and exact rational comparisons give
\[
 \max\{\tau,\sigma,\chi\}<\lambda<\lambda'<1,\quad
 \sigma+\beta(1-\sigma)<\lambda',\quad 1-c<\lambda'.
\]
The stopping test is $e^{1000}<d$. Section~\ref{sec:compact-stopped-guard}
proves the displayed $C_1$, with $\epsilon C_1<1$.
The retained Gaussian choice gives the remaining comparisons
\[
 \epsilon<\tfrac13,\quad 2\epsilon<1,\quad
 \epsilon(1-\tau)<1-\tau,\quad
 \tfrac34+\delta+\tfrac54\epsilon<1,\quad
 \epsilon(1+c)<1,\quad \epsilon+\delta<1.
\]

''' +text[end:]
    text=replace_once(text,r'b^{199/1000}',r'b^{1999/10000}')
    text=replace_once(text,r'd^{1000}\le b^{199}',r'd^{10000}\le b^{1999}')
    text=replace_once(text,r'b^{1597/2000}',r'b^{15997/20000}')
    text=replace_once(text,r'$C_1=2$',r'$C_1=49961/10000$')
    text=replace_once(text,'the\n$O(\\log d)$ reserved row axes and enough bits for all work blocks.',
        'the\n$O(\\log d+d^{1-c}\\log p)$ reserved row and compact-control axes,\n'
        'which form $o(d)$ axes, and enough bits for all work blocks.')
    start=text.index('Exact substitution, using the new Gaussian width')
    end=text.index('Here $d$',start)
    text=text[:start]+r'''Exact substitution in the unchanged seven-term assembly accounting gives
\[
 G_*:=\min_i g_i=g_3=\epsilon(1-\lambda')
       =\frac{333833}{4\cdot10^{15}}>\frac{83}{10^{12}}=\kappa.
\]
The new reservation, compact movement and repair costs are all included
in the completed-layer term $g_3$. Put $\rho=G_*-\kappa>0$; this fixed
strict gap absorbs all remaining fixed powers of $\log p$.
The guard is $O(d^{49961/10000})=o(p)$, while
$\alpha=\Theta(p^{11999/40000})$ and
$\gamma=O(p^{15997/20000})=o(p)$. Also
$K=\Theta(p^{1999/50000})=o(\ell)$, $K/\log p\to\infty$,
and $\ell=\Theta(p^{8001/10000})$. The prime-interval ratio grows as
$p^{3001/5000}$. All construction and precision conditions hold beyond
a common fixed cutoff.

''' +text[end:]
    start=text.index('For one packed change of basis, let')
    end=text.index('Finally, all role, arithmetic, and stack tapes',start)
    text=text[:start]+r'''For a compact-control change of basis of current volume $V_{\rm call}$,
the exceptional fraction is at most $5/(128p^3)$ beyond the common cutoff.
Sorting its keyed exceptional records costs
\[
 O\bigl(V_{\rm call}\delta p(1+1/r)\bigr)=O(V_{\rm call}p^{-2}).
\]
Extraction and reinsertion cost $O(V_{\rm call})$, and polynomial predicate
and key work per record is absorbed by the whole polynomial record suffix.
These are already charged at \emph{each node} in the compact-control
recurrence. Their sum is bounded by that volume-weighted recurrence and
therefore by the completed-layer cost in the table. No claim that their
global total is $o(V)$ is needed, and the old global estimate using an
exponentially small $2^{-K}$ bad fraction is not used for this new gadget.

''' +text[end:]
    text=replace_once(text,'Each of the seven displayed powers is at most $1-G$ by',
        'Each of the seven displayed powers is at most $1-G_*$ by')
    return text


def patched_files():
    certificate()
    for name,old,new in paired_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_once(new,r'\kappa=2^{-59}',r'\kappa=83/10^{12}')
            if name.endswith('main.tex'):
                new=replace_once(new,'pdfauthor={OpenAI}',
                    'pdfauthor={OpenAI (original manuscript); Douglas Colkitt (modifications)}')
                new=replace_once(new,r'\author{OpenAI}',r'''\author{\small Original manuscript: OpenAI\\
\small Compact-control modifications: Douglas Colkitt}''')
                new=replace_once(new,r'\date{September 23, 2026}',
                    r'\date{Original: September 23, 2026; modified: October 7, 2026}')
                new=replace_once(new,r'\maketitle',r'''\maketitle
\begin{quote}\small
\textbf{Modified research draft; not an OpenAI release.}
This derivative incorporates Douglas Colkitt's compact-control construction
and retained project refinements, prepared with assistance from OpenAI Codex.
The revised bound is conditional on the original manuscript's retained
algorithmic and analytic interfaces and the new written arguments. These
modifications have not received independent mathematical review or formal
verification; no endorsement by OpenAI is implied.
\end{quote}''')
        elif name.endswith('03-motifs.tex'):
            start=new.index(r'\subsection{Explicit exponents at ground size fifty}')
            tail=new[start:].replace(r'\sigma=',r'\sigma_{50}=')
            tail=tail.replace('eq:explicit-motif-exponents','eq:paired-intermediate-exponents')
            new=new[:start]+tail+'\n'+note('independent-complex.tex')+r'''
The exponents used from now on are
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-296/10^{11},\qquad\sigma=1-418/10^{12}.
\end{equation}
'''
        elif name.endswith('05-layers.tex'):new=layers(new)
        elif name.endswith('08-assembly.tex'):new=assembly(new)
        new=('% Modified by Douglas Colkitt, October 7, 2026.\n'
             '% Conditional compact-control research draft; see main.tex for scope.\n'+new)
        yield name,old,new


if __name__=='__main__':
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True),fromfile=f'a/{name}',tofile=f'b/{name}'))
        for name,old,new in patched_files())
    (ROOT/'patches/compact-control-34.patch').write_text(patch)
    print('Wrote independent compact-control patch; conditional kappa=83/10^12 > 2^-34.')
