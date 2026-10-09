#!/usr/bin/env python3
"""Independent pinned-source patch for the fast Gaussian resampling witness.

Builds on the compressed-complex patch. The finite networks, compact-control
movement, reservation, repair and guard are unchanged. The one-dimensional
resampling lemma gets chirped-correlation Gaussian maps and a sharper Neumann
count, the tensor interface its new time bound, and the assembly the new
Gaussian width, cost row, margin and parameters.
"""
import difflib
from pathlib import Path

from fast_gaussian import witness_only
from make_patch import replace_once
from make_complex_circuit_patch import patched_files as complex_files

ROOT = Path(__file__).resolve().parents[1]


def note(name): return (ROOT/'notes'/name).read_text()


def resampling(text):
    text = replace_once(text, r'''be integers, with $\gcd(s,t)=1$ and
\[
 \theta:=t/s-1>p/\alpha^4.
\]''', r'''be integers, with $\gcd(s,t)=1$. Put $\sigma=t/s$ and
$\theta:=\sigma-1$, and assume
\[
 \alpha^{-2}\le\theta\le\tfrac14,\qquad
 n_{\alpha,\theta}:=\min\Bigl\{\Bigl\lceil\frac p{\alpha^2\theta}\Bigr\rceil,
   \Bigl\lceil\frac{p+1}{4\alpha^2}+\frac1\theta\Bigr\rceil\Bigr\}.
\]''')
    text = replace_once(text, r'''than $p^2$ and time
\[
 O(tp^{3/2+\delta}\alpha).
\]
The constant is uniform in $p,s,t,\alpha$.''', r'''than $p^2$, using respectively
\[
 O((t+p)p^{1+\delta})\quad\text{and}\quad
 O(n_{\alpha,\theta}(t+p)p^{1+\delta})
\]
time. The constants are uniform in $p,s,t,\alpha$.''')
    text = replace_once(text, r'''frequency by $-s$. Since $\alpha^2<p$ and $\theta>p/\alpha^4$, we have
$\alpha^2\theta>p/\alpha^2>1$. Thus $\|N-I\|<1/2$, so $N$ is invertible''',
        r'''frequency by $-s$. The cited Lemma~4.6 assumes only $\alpha^2\theta\ge1$,
which holds here; it gives $\|N-I\|<2.01e^{-\pi/2}<0.42$. The proof of the cited
Proposition~4.7(i) uses only this bound, $\alpha\ge2$ and the cited Lemma~4.5,
so its norm bounds below also hold. Thus $\|N-I\|<1/2$, so $N$ is invertible''')
    text = replace_once(text, r'''\paragraph{Ordered numerical maps.}
Lemmas~4.8, 4.9 and 4.12 of
\cite{HarveyHoeven2021} supply the following algorithms. Their inputs
and outputs are in increasing coordinate order, and every output is in
the disk grid. The record conversions and tape movement needed to use
these routines in our format are accounted for below. Their numerical
guarantees are
\[
\begin{array}{c|c|c}
 \text{map}&\text{error bound}&\text{time bound}\\ \hline
 \widetilde{\mathsf S}'&16p&O(tp^{3/2+\delta}\alpha)\\
 \widetilde{\mathsf J}'&3p^2/4&O(tp^{3/2+\delta}\alpha)\\
 \widetilde{\mathsf D}'&4&O(tp^{1+\delta}).
\end{array}
\]''', r'''\paragraph{Ordered numerical maps.}
Lemma~4.8 of \cite{HarveyHoeven2021} supplies $\widetilde{\mathsf D}'$.
Lemma~\ref{lem:chirped-gaussian} below supplies $\widetilde{\mathsf S}'$
and an approximation $\widetilde E$ of $E=N-I$ by chirped correlations.
For $\widetilde{\mathsf J}'$ we use the Neumann evaluation of
\cite[Lemma~4.12]{HarveyHoeven2021} with this $\widetilde E$ and with
$n_{\alpha,\theta}$ terms. Its error analysis uses only $\|E\|<1/2$,
$\varepsilon(\widetilde E)<p/3$, $n\le p$, and the bound
$\|E^n\|\le2^{-p}$, which replaces $\|E\|^n\le2^{-p}$; the tail uses
$\|E^{n+k}\|\le\|E^n\|\|E\|^k$. Corollary~\ref{cor:neumann-count} supplies
$n\le p$ and $\|E^n\|\le2^{-p}$, so the error bound $3p^2/4$ of that lemma
is unchanged. Inputs and outputs are in increasing coordinate order, and
every output is in the disk grid. The record conversions and tape
movement needed in our format are accounted for below. The guarantees are
\[
\begin{array}{c|c|c}
 \text{map}&\text{error bound}&\text{time bound}\\ \hline
 \widetilde{\mathsf S}'&16p&O((t+p)p^{1+\delta})\\
 \widetilde{\mathsf J}'&3p^2/4&O(n_{\alpha,\theta}(t+p)p^{1+\delta})\\
 \widetilde{\mathsf D}'&4&O(tp^{1+\delta}).
\end{array}
\]''')
    text = replace_once(text, r'''transform identity. The algorithms for $A$ and $B_0$ use $C$ and the
three quoted arithmetic maps, with all their original truncations.''',
        r'''transform identity. The algorithms for $A$ and $B_0$ use $C$, the
quoted map $\widetilde{\mathsf D}'$, and the maps of
Lemma~\ref{lem:chirped-gaussian}, whose truncations contain those of the
cited Lemmas~4.9 and~4.11.''')
    text = replace_once(text, r'''The remaining tape movement inside the quoted algorithms also has the
claimed bound. The $\mathsf S'$ procedure uses a consecutive periodic input
window of radius $\lceil\sqrt p\rceil\alpha$ for each output. Visiting
these $O(p)$-bit records costs $O(tp\sqrt p\alpha)$ tape steps.
Remark~4.10 in the cited paper charges the extra jumps at the cyclic
boundary by the same bound.''', r'''Tape movement inside $\widetilde{\mathsf S}'$ and $\widetilde E$,
including the cyclic boundary, is included in
Lemma~\ref{lem:chirped-gaussian}.''')
    text = replace_once(text, r'''Put $E=N-I$ and $k=\lceil p/(\alpha^2\theta)\rceil$. Under the present
hypotheses, Lemma~4.11 gives, for every $z\in\mathbb D_p^s$,
\[
 \widetilde E z\in\mathbb D_p^s,\qquad
 2^p\|\widetilde E z-Ez\|<p/3.
\]
Its proof establishes the rounded output bound
\[
 \|\widetilde E z\|<0.42\|z\|+(p/3)2^{-p}<1.
\]''', r'''Put $k=n_{\alpha,\theta}$. Lemma~\ref{lem:chirped-gaussian} gives, for
every $z\in\mathbb D_p^s$,
\[
 \widetilde E z\in\mathbb D_p^s,\qquad
 2^p\|\widetilde E z-Ez\|<p/3,
\]
and its proof establishes the rounded output bound
\[
 \|\widetilde E z\|<0.42\|z\|+(p/3)2^{-p}<1.
\]''')
    text = replace_once(text, r'''Since $k\leq\alpha^2+1<p+1$, each component of any signed partial
numerator sum has magnitude at most $k2^p$ and needs
$p+\lceil\log_2(k+1)\rceil+O(1)=O(p)$ bits. Inside one $\widetilde E$
row, the $2m$ disk-grid summands of Lemma~4.11 likewise need
$p+\lceil\log_2(2m+1)\rceil+O(1)=O(p)$ accumulator bits, where
$m=\lceil\sqrt p/(2\alpha)\rceil$. These partial sums are accumulated
exactly on separate tapes; only completed iterates are fed into
$\widetilde E$.

The window of radius $m$ in one $\widetilde E$ call has tape movement
cost $O(tp(1+\sqrt p/\alpha))$, including the analogous boundary
accounting. The exact row additions cost $O(smp)$, within this bound.
The $k-1$ calls therefore spend
\[
 O\bigl((\alpha^2+1)tp(1+\sqrt p/\alpha)\bigr)
 =O(tp\sqrt p\alpha)
\]
on these scans and additions, using $2\leq\alpha<\sqrt p$.
For either Gaussian procedure, if a window
radius $w$ satisfies $s\leq2w$, then $O(1+w/s)$ traversals of the period
cost $O((s+w)p)=O(wp)$ per output. This also covers windows longer than
one period. The current iterate, next iterate, and running sum use a
fixed number of tapes holding $O(p)$-bit records. Outer accumulation
costs $O(ksp)=O(tp\alpha^2)$, within $O(tp\sqrt p\alpha)$.
All truncations are those of the cited algorithms, and the tape count
and constants remain uniform in the parameters.''', r'''Since $k\leq p$, each component of any signed partial
numerator sum has magnitude at most $k2^p$ and needs
$p+\lceil\log_2(k+1)\rceil+O(1)=O(p)$ bits. These partial sums are
accumulated exactly on separate tapes; only completed iterates are fed into
$\widetilde E$.

The $k-1$ calls of $\widetilde E$ cost $O(k(t+p)p^{1+\delta})$, including
their tape movement, by Lemma~\ref{lem:chirped-gaussian}. The current
iterate, next iterate, and running sum use a fixed number of tapes holding
$O(p)$-bit records. Outer accumulation costs $O(ksp)$, within the same
bound. All truncations contain those of the cited algorithms, and the tape
count and constants remain uniform in the parameters.''')
    text = replace_once(text, r'''\end{proof}

\subsection{Growing dimension and the padded array}''', r'''\end{proof}

'''+note('fast-gaussian-resampling.tex')+r'''
\subsection{Growing dimension and the padded array}''')
    text = replace_once(text, r'''less than $dp^2$. The total time spent in the
one-dimensional algorithms for both maps is
$O(dTp^{3/2+\delta}\alpha)$, with a constant independent of $d$.''',
        r'''less than $dp^2$. Put $n_*=\max_in_{\alpha,\theta_i}$. If every
$t_i\ge p$, the total time spent in the one-dimensional algorithms for both
maps is $O(dTp^{1+\delta}(1+n_*))$, with a constant independent of $d$.''')
    text = replace_once(text, r'''\[
 \sum_{i=1}^d\frac{T}{t_i}
           O(t_i p^{3/2+\delta}\alpha)
   =O(dTp^{3/2+\delta}\alpha).
\]''', r'''\[
 \sum_{i=1}^d\frac{T}{t_i}
           O\bigl(n_*(t_i+p)p^{1+\delta}\bigr)
   =O(dTp^{1+\delta}(1+n_*)),
\]
using $t_i\ge p$.''')
    return text


def assembly(text):
    text = replace_once(text, r'''contractions; their disk-grid approximations have error less than
$p^2 2^{-p}$ and cost $O(tp^{3/2+\delta}\alpha)$ on a line of length
$t$.''', r'''contractions; their disk-grid approximations have error less than
$p^2 2^{-p}$ and cost $O(n(t+p)p^{1+\delta})$ on a line of length
$t$, where $n$ is the Neumann count of Lemma~\ref{lem:no-sort-resampling}.''')
    start = text.index('Put $a=296/10^{11}$')
    end = text.index(r'\subsection{Input and transform sizes}', start)
    text = text[:start]+r'''Put $a=296/10^{11}$ and $a_{\rm c}=14/10^9$.
Choose
\begin{equation}\label{eq:fixed-parameters}
\begin{gathered}
 \tau=1-a,\quad\sigma=1-a_{\rm c},\quad
 \beta=\frac{19}{25},\quad\zeta=\frac1{10000},\quad
 C_1=5-4\beta+\zeta=\frac{19601}{10000},\\
 \epsilon=\frac{49999}{100000},\quad c=\frac{9999}{10000},\quad\delta=\frac1{10^6},\\
 \lambda=1-\frac{29595}{10^{13}},\quad
 \lambda'=1-\frac{2959}{10^{12}},\quad
 \kappa=\frac{1479}{10^{12}}>2^{-30}.
\end{gathered}
\end{equation}
Since $\sigma<\tau$, the compact-control recurrence has
$\chi=\tau+(1-\beta)\max\{\sigma-\tau,0\}=\tau$, and exact rational
comparisons give
\[
 \max\{\tau,\sigma,\chi\}<\lambda<\lambda'<1,\quad
 \sigma+\beta(1-\sigma)<\lambda',\quad 1-c<\lambda'.
\]
The stopping test is $e^{1000}<d$. Section~\ref{sec:compact-stopped-guard}
proves the displayed $C_1$, with $\epsilon C_1<1$.
The Gaussian choice below gives the remaining comparisons
\[
 2\epsilon<1,\quad
 \epsilon(1-\tau)<1-\tau,\quad
 2\epsilon+\delta<1,\quad
 \epsilon(1+c)<1,\quad \epsilon+\delta<1.
\]

'''+text[end:]
    text = replace_once(text, r'''Set
\[
 \alpha=\left\lceil(32db)^{1/4}\right\rceil,
 \qquad \gamma=2d\alpha^2,\qquad \eta=\frac1{4d}.
\]
The ceiling does not affect the needed bounds: for $A\ge1$,
$\lceil A\rceil\le2A$, and hence
\begin{equation}\label{eq:gamma}
 \alpha\le2(32db)^{1/4},\qquad
 \gamma<46d^{3/2}\sqrt b\le46b^{1/2+3\epsilon/2}=46b^{159997/200000}.
\end{equation}
It follows that $2\le\alpha<\sqrt p$ eventually and $\gamma=o(b)$.
For example $b\ge2^{40}$ implies $\gamma\le b/4$.''', r'''Set
\[
 \alpha=\Bigl\lfloor\sqrt{b/(8d)}\Bigr\rfloor,
 \qquad \gamma=2d\alpha^2,\qquad \eta=\frac1{4d}.
\]
Then
\begin{equation}\label{eq:gamma}
 \gamma\le b/4,\qquad \alpha^2<p.
\end{equation}
For large $n$ also $b\ge96d$; then $\sqrt{b/(8d)}\ge2\sqrt3$, so
$\alpha\geq2$ and $\alpha^2\geq b/(16d)$.''')
    text = replace_once(text, r'''Writing $\theta_i=t_i/s_i-1$, the upper bound on $s_i$ gives
$\theta_i\geq\eta/(1-\eta)>\eta$. Therefore
\[
 \alpha^4\theta_i>\frac{32db}{4d}=8b>6b=p.
\]
The choice of $\alpha$ gives
$\alpha=\Theta(p^{1/4+\epsilon/4})$, and \eqref{eq:gamma} already
ensures $2\leq\alpha<\sqrt p$ for large $n$. We also have
$t_i\leq r\leq T<8n/b<2^{6b}=2^p$.''', r'''Writing $\theta_i=t_i/s_i-1$, the bounds on $s_i$ give
$\eta<\theta_i<2\eta/(1-2\eta)=1/(2d-1)\le1/4$ once $d\geq3$. Therefore
\[
 \alpha^2\theta_i>\frac b{16d}\cdot\frac1{4d}=\frac b{64d^2}\geq1
\]
once $b\geq64d^2$, which holds for large $n$ because $d^2\le b^{2\epsilon}$
and $2\epsilon<1$. The Neumann counts of
Lemma~\ref{lem:no-sort-resampling} satisfy
\[
 n_{\alpha,\theta_i}\le\frac{p+1}{4\alpha^2}+\frac1{\theta_i}+1
   \le\frac{(6b+1)16d}{4b}+4d+1\le30d.
\]
We also have $t_i\leq r\leq T<8n/b<2^{6b}=2^p$ and $t_i\ge r/2>p$.''')
    text = replace_once(text, r'''Gaussian line maps & $dp^{1/2+\delta}\alpha$ & $3/4+\delta+5\epsilon/4$\\''',
                        r'''Gaussian line maps & $d^2p^\delta$ & $2\epsilon+\delta$\\''')
    text = replace_once(text, r''' g_5=1/4-\delta-5\epsilon/4,\\''', r''' g_5=1-\delta-2\epsilon,\\''')
    text = replace_once(text, r'''       =\frac{14779261}{25\cdot10^{15}}>\frac{59}{10^{11}}=\kappa.''',
                        r'''       =\frac{147947041}{10^{17}}>\frac{1479}{10^{12}}=\kappa.''')
    text = replace_once(text, r'''The guard is $O(d^{49961/10000})=o(p)$, while
$\alpha=\Theta(p^{119999/400000})$ and
$\gamma=O(p^{159997/200000})=o(p)$. Also
$K=\Theta(p^{19979001/10^8})=o(\ell)$, $K/\log p\to\infty$,
and $\ell=\Theta(p^{80001/100000})$. The prime-interval ratio grows as
$p^{30001/50000}$.''', r'''The guard is $O(d^{19601/10000})=o(p)$, while
$\alpha=\Theta(p^{50001/200000})$ and $\gamma\le b/4$. Also
$K=\Theta(p^{499940001/10^9})=o(\ell)$, $K/\log p\to\infty$,
and $\ell=\Theta(p^{50001/100000})$. The prime-interval ratio grows as
$p^{1/50000}$, and so does $b/d^2$.''')
    text = replace_once(text, r'''For Gaussian resampling, axis $i$ has at most $T/t_i$ processed lines.
The line-machine costs therefore sum to
\[
 \sum_{i=1}^d\frac{T}{t_i}
       O(t_i p^{3/2+\delta}\alpha)
 =O(dTp^{3/2+\delta}\alpha).
\]
Dividing by $V=Tp$ gives the fifth row.  The factor
$\alpha=\Theta(p^{1/4+\epsilon/4})$ explains its displayed power of $p$.''',
        r'''For Gaussian resampling, axis $i$ has at most $T/t_i$ processed lines,
each of length $t_i>p$. Since every Neumann count is at most $30d$, the
line-machine costs sum to
\[
 \sum_{i=1}^d\frac{T}{t_i}
       O(30d\,t_i p^{1+\delta})
 =O(d^2Tp^{1+\delta}).
\]
Dividing by $V=Tp$ gives the fifth row.''')
    return text


def patched_files():
    witness_only()  # full checks run in fast_gaussian.py and the tests
    for name, old, new in complex_files():
        if name.endswith(('main.tex', '00-introduction.tex')):
            new = replace_once(new, r'\kappa=59/10^{11}', r'\kappa=1479/10^{12}')
            if name.endswith('main.tex'):
                new = replace_once(new, r'''\small Compressed complex network: eumemic}''',
                                   r'''\small Compressed complex network and fast resampling: eumemic}''')
                new = replace_once(new, r'''and a compressed complex network prepared with assistance from Claude
(Anthropic).''', r'''and a compressed complex network and faster Gaussian resampling prepared
with assistance from Claude (Anthropic).''')
        elif name.endswith('07-resampling.tex'): new = resampling(new)
        elif name.endswith('08-assembly.tex'): new = assembly(new)
        new = new.replace('% Compressed complex network added October 7, 2026.\n',
                          '% Compressed complex network added October 7, 2026.\n'
                          '% Fast Gaussian resampling added October 8, 2026.\n')
        yield name, old, new


if __name__ == '__main__':
    patch = ''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True), fromfile=f'a/{name}', tofile=f'b/{name}'))
        for name, old, new in patched_files())
    (ROOT/'patches/fast-gaussian-30.patch').write_text(patch)
    print('Wrote independent fast-Gaussian patch; conditional kappa=1479/10^12 > 2^-30.')
