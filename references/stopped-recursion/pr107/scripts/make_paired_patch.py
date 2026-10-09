#!/usr/bin/env python3
"""Independent pinned-upstream patch for the conditional 2^-59 witness."""
import difflib
from pathlib import Path
from make_patch import extended_files,replace_once
from make_nonadjacent_patch import layout_change
from paired_network import certificate

ROOT=Path(__file__).resolve().parents[1]


def assembly(text):
    start=text.index('Take the following fixed rational numbers:')
    end=text.index(r'\subsection{Input and transform sizes}',start)
    text=text[:start]+r'''Put $a=296/10^{11}$ and $a_{\rm c}=1/10^{11}$. Take
\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-a,\quad\sigma=1-a_{\rm c},\quad\beta=\frac{999}{1000},
 \quad\delta=\frac1{10000},\quad C_1=2,\\
 \epsilon=\frac{199}{1000},\quad c=\frac{999a}{1000},\quad
 \lambda=1-\frac{1999a^2}{2000},\quad
 \lambda'=1-\frac{999a^2}{1000},\quad\kappa=2^{-59}.
\end{gathered}
\end{equation}
The layer conditions follow by exact comparison:
\[
 \tau(1+c/\beta)=1-a^2<\lambda<\lambda'<1,\qquad
 \sigma<\lambda,\qquad \sigma+\beta(1-\sigma)<\lambda'.
\]
The rational stopping test is $e^{1000}<d^{999}$.
Section~\ref{sec:stopped-guard} justifies $C_1=2$ for this stopping rule.
The tighter Gaussian choice below replaces the former sufficient restriction
$\epsilon<1/12$ by the sublinear-scaling condition $\epsilon<1/3$.
The dimension and cost comparisons are
\[
 \epsilon<\frac13,\quad 2\epsilon<1,\quad
 \epsilon(1-\tau)<1-\tau,\quad
 \frac34+\delta+\frac54\epsilon<1,\quad
 \epsilon(1+c)<1,\quad \epsilon+\delta<1.
\]

''' +text[end:]
    text=replace_once(text,r'b^{2^{-37}}',r'b^{199/1000}')
    text=replace_once(text,r'd^{2^{37}}\le b',r'd^{1000}\le b^{199}')
    text=text.replace(r'12d^2b',r'32db')
    text=replace_once(text,r'\gamma<28d^2\sqrt b\le28b^{1/2+2\epsilon}\le28b^{2/3}.',
        r'\gamma<46d^{3/2}\sqrt b\le46b^{1/2+3\epsilon/2}=46b^{1597/2000}.')
    text=text.replace(r'b\ge2^{24}',r'b\ge2^{40}')
    text=replace_once(text,r'\alpha^4\theta_i>\frac{32db}{4d}=3db\geq6b=p.',
        r'\alpha^4\theta_i>\frac{32db}{4d}=8b>6b=p.')
    text=text.replace(r'p^{1/4+\epsilon/2}',r'p^{1/4+\epsilon/4}')
    text=replace_once(text,r'$C_1=20$',r'$C_1=2$')
    text=replace_once(text,r'$3/4+\delta+3\epsilon/2$',r'$3/4+\delta+5\epsilon/4$')
    text=replace_once(text,r'g_5=1/4-\delta-3\epsilon/2',r'g_5=1/4-\delta-5\epsilon/4')
    start=text.index('Direct substitution',text.index(r'\label{eq:margin-list}'))
    end=text.index('Here $d$',start)
    text=text[:start]+r'''Exact substitution, using the new Gaussian width and the nonadjacent
layout bound, gives
\[
 G:=\min_i g_i=g_2=g_3=\epsilon\beta a^2
 =\frac{272158569}{156250000000000000000000000}>2^{-59}=\kappa.
\]
The Gaussian margin is $g_5=23/20000$; the other margins are positive
and exceed $G$. Put $\rho=G-\kappa>0$. This strict gap absorbs every
remaining fixed power of $\log p$.
The guard is $O(d^2)=O(p^{199/500})=o(p)$, while
$\alpha=\Theta(p^{1199/4000})$ and $\gamma=O(p^{1597/2000})=o(p)$.
Also $K=\Theta(p^{\epsilon c})=o(\ell)$ with $K/\log p\to\infty$,
and $\ell=\Theta(p^{801/1000})$. The prime-interval ratio grows as
$p^{301/500}$. All eventual construction and precision conditions still hold.

''' +text[end:]
    text=replace_once(text,
        'Each of the seven displayed powers is at most $1-2\\kappa$ by\n'
        '\\eqref{eq:margin-list}.  Any fixed power of $\\log p$ is at most $p^\\kappa$',
        'Each of the seven displayed powers is at most $1-G$ by\n'
        '\\eqref{eq:margin-list}. Any fixed power of $\\log p$ is at most $p^\\rho$')
    return text


def patched_files():
    certificate()
    proof=(ROOT/'notes/paired-construction.tex').read_text()
    guard=(ROOT/'notes/stopped-guard.tex').read_text()
    for name,old,new in extended_files(36,50,12):
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_once(new,r'\kappa=2^{-111}',r'\kappa=2^{-59}')
        elif name.endswith('03-motifs.tex'):
            start=new.index(r'\subsection{Explicit rational bounds for the two recurrences}')
            new=new[:start]+proof
        elif name.endswith('04-swap.tex'):
            new=new.replace('prop:bit-motif-interface','prop:paired-bit-interface')
            new=replace_once(new,r'$W=W_{\rm b}$ and $s=s_{\rm b}$',
                r'$W=W_{\rm b}^{\rm pair}$ and $s=s_{\rm b}^{\rm pair}$')
            new=replace_once(new,'2^{-36}',r'\frac{296}{10^{11}}')
        elif name.endswith('05-layers.tex'):
            new=replace_once(new,r'Fix \(\beta=1/2\),',r'Fix a rational \(9/10\le\beta<1\),')
            start=new.index(r'\subsection{An explicit guard-width bound}')
            end=new.index(r'\begin{proposition}[Simultaneous normalized butterfly layer]',start)
            new=new[:start]+guard+'\n'+new[end:]
            new=replace_once(new,r'\tau=\sigma=1-2^{-36},\qquad \beta=\frac12,\qquad C_1=20.',
                r'\tau=1-\frac{296}{10^{11}},\quad\sigma=1-\frac1{10^{11}},\quad '
                r'9/10\le\beta<1\ (\beta\in\mathbb Q),\quad C_1=2.')
        elif name.endswith('08-assembly.tex'):
            new=assembly(layout_change(name,new))
        yield name,old,new
    name='build/sections/07-resampling.tex';old=(ROOT/'upstream'/name).read_text()
    yield name,old,layout_change(name,old)


if __name__=='__main__':
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True),fromfile=f'a/{name}',tofile=f'b/{name}'))
        for name,old,new in patched_files())
    (ROOT/'patches/h50-paired-59.patch').write_text(patch)
    print('Wrote independent conditional h50-paired-59.patch')
