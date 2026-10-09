#!/usr/bin/env python3
"""Independent upstream patch for zero-loss side-role sharing and kappa=2^-75."""
import difflib
from pathlib import Path
from make_patch import replace_once
from tune_routing import patched_files as tuned_files
from reuse_network import certificate

ROOT=Path(__file__).resolve().parents[1]

REUSE_PROOF=r'''
\subsection{Sharing side roles between the first and third stages}
\label{sec:side-role-sharing}
We improve only the bit network. The complex network and its guard-width
constants remain unchanged. Here $h=46$ is even. Fix the same ordering of
$\mathcal T$ in all three factors, and list each triple's $z_{\rm b}$
neighbors in that order. Write $n_S(j)$ for the $j$th neighbor of $S$.

There is an explicit permutation $\pi$ of $\mathcal T$ such that
$|T\cap\pi(T)|=1$. Pair the ground points consecutively. If $T$ contains
one complete pair and a singleton, keep the singleton and cycle the complete
pair through the ordered list of pairs other than the singleton's pair.
There are at least two choices in that list. Otherwise $T$ uses three
pairs: keep the point from the least indexed pair and flip the other two
points to their partners. The first rule is a cycle on each class with a
fixed singleton; the second is an involution. The classes are disjoint,
so the map is bijective and has the required intersection in every case.
In particular $t_T\perp t_{\pi(T)}$ for the rational label form.

A stage-1 side role is indexed by fixed second and third triples $(A,B)$
and physical target/source triples $(S,n_S(j))$ in the first factor.
Identify it with the stage-3 side role whose fixed first and second triples
are $(S,\pi(A))$, and whose target/source triples are $(B,n_B(j))$.
This is a bijection between all stage-1 and stage-3 side roles: from the latter
role recover $A$ using $\pi^{-1}$ and recover $j$ from the neighbor list of $B$.
Thus exactly
\[
 R=N z_{\rm b}=9475984020888000
\]
pairs of roles are identified. Stage 2 retains its separate side roles;
all central roles remain separate.

The first-stage invocations finish before the third-stage invocations begin.
Each scalar invocation restores its own auxiliary values for every initial
value. Consequently the same physical auxiliary value can be used in its
paired invocation without changing the scalar bank exchange or the restoration
of any remaining auxiliary role. No gate within one invocation identifies two
of its simultaneous roles.

It remains to check the address frames: scalar restoration alone would not
justify the rank saving. The last stage-1 gate on this shared role has label
\[
 E=F\otimes\langle t_A\rangle\otimes\langle t_B\rangle,
 \qquad \dim E=h.
\]
Its first stage-3 gate has label
\[
 H=\langle t_S\otimes t_{\pi(A)}\rangle^\perp_{F\otimes F}
       \otimes\langle t_B\rangle,
 \qquad \dim H=h^2-1.
\]
Orthogonality of $t_A,t_{\pi(A)}$ gives $E\subset H$. Both spaces are
nondegenerate by the same tensor decompositions as before. The new joining
edge therefore has rational projection-difference rank $h^2-1-h$.
It replaces the old edge from $E$ to the stage-1 scratch sink $\mathcal F$
and the old edge from the stage-3 scratch source $0$ to $H$. Their ranks
sum to $(m-h)+(h^2-1)$, exactly $m$ more. All other edges and all gate
labels are unchanged; no new decreasing edge is introduced.

Every shared role still has initial matrix zero and final matrix $I_m$,
and the scalar permutation fixes that role. Data-role endpoints are unchanged.
Thus the all-role endpoint identity in the bit interface is retained.
The new finite network has
\begin{align*}
 W_{\rm b}^*&=W_{\rm b}-R=18958995769111200,\\
 s_{\rm b}^*&=s_{\rm b}-mR=1845392811609813681600,\\
 W_{\rm b}^*m-s_{\rm b}^*&=N-2L_{\rm b}>0.
\end{align*}
\begin{proposition}[Shared-role bit interface]\label{prop:reused-bit-interface}
The shared-role bit network uses pointwise XOR gates and is a permutation on
all its input roles, including arbitrary auxiliary inputs. Its rational gate
matrices satisfy the endpoint identities of
Proposition~\ref{prop:bit-motif-interface}, with $W_{\rm b}^*$ roles and
total edge rank $s_{\rm b}^*<W_{\rm b}^*m$.
\end{proposition}
\begin{proof}
The scalar restoration, new-edge rank, and unchanged endpoint identities have
just been verified. Apply the common-frame identity to the resulting fixed
circuit. Its gate matrices and rational shear factorizations are finite data,
so the original fixed-tape interchange construction applies with these new
constants. Neither the matching nor the larger finite compilation depends on
the eventual input length.
\end{proof}

\subsection{Explicit rational bounds for the two recurrences}
Put
\[
 a_{\rm b}=\frac{27}{10^{12}},\qquad
 a_{\rm c}=\frac9{500000000000},\qquad L=\frac{5743}{500}.
\]
The new bit deficit and unchanged complex deficit are
\[
 \eta_{\rm b}^*=\frac{W_{\rm b}^*m-s_{\rm b}^*}{W_{\rm b}^*m}
   =\frac9{29015910268}>a_{\rm b}L,
 \qquad
 \eta_{\rm c}=\frac7{22253827054}>a_{\rm c}L.
\]
For $1\le x\le2$ put $z=(x-1)/(x+1)$ and
\[
 S(x)=2\sum_{j=0}^{23}\frac{z^{2j+1}}{2j+1},\qquad
 R(x)=\frac{2z^{49}}{49(1-z^2)}.
\]
The logarithm series gives $S(x)\le\log x\le S(x)+R(x)$.
Exact rational comparison at $m=97336$ gives
\[
 \log m\le16(S(2)+R(2))+S(m/2^{16})+R(m/2^{16})<L.
\]
For either corresponding saving $a$ and deficit $\eta$,
$m^{1-a}=m\exp(-a\log m)>m(1-aL)>m(1-\eta)$.
We may therefore take
\begin{equation}\label{eq:explicit-motif-exponents}
 \tau=1-a_{\rm b},\qquad \sigma=1-a_{\rm c},
\end{equation}
so $s_{\rm b}^*/W_{\rm b}^*<m^\tau$ and
$s_{\rm c}/W_{\rm c}<m^\sigma$. The two networks have the same fixed
label dimension here but different wire counts, as allowed by their interfaces.
'''


def patched_files():
    certificate()
    for name,old,new in tuned_files():
        if name.endswith(('main.tex','00-introduction.tex')):
            new=replace_once(new,r'\kappa=2^{-76}',r'\kappa=2^{-75}')
        elif name.endswith('03-motifs.tex'):
            start=new.index(r'\subsection{Explicit rational bounds for the two recurrences}')
            new=new[:start]+REUSE_PROOF
        elif name.endswith('04-swap.tex'):
            new=new.replace('prop:bit-motif-interface','prop:reused-bit-interface')
            new=replace_once(new,r'$W=W_{\rm b}$ and $s=s_{\rm b}$',
                             r'$W=W_{\rm b}^*$ and $s=s_{\rm b}^*$')
            new=replace_once(new,r'1-\frac{9}{500000000000}',r'1-\frac{27}{10^{12}}')
        elif name.endswith('05-layers.tex'):
            new=replace_once(new,r'\tau=\sigma=1-\frac{9}{500000000000}',
                r'\tau=1-\frac{27}{10^{12}},\qquad \sigma=1-\frac9{500000000000}')
        elif name.endswith('08-assembly.tex'):
            new=replace_once(new,'Put $a=9/500000000000$ and choose',
                             r'Put $a=27/10^{12}$ and $a_{\rm c}=9/500000000000$ and choose')
            new=replace_once(new,r'\tau=\sigma=1-a',r'\tau=1-a,\quad \sigma=1-a_{\rm c}')
            new=new.replace(r'\kappa=2^{-76}',r'\kappa=2^{-75}')
            new=replace_once(new,r'\sigma+\beta(1-\sigma)=1-a/10',
                             r'\sigma+\beta(1-\sigma)=1-a_{\rm c}/10')
            anchor='The rational stopping comparison'
            new=replace_once(new,anchor,
                r'The separate layer requirement $\sigma<\lambda$ follows from '
                r'$19a^2/20<a_{\rm c}$; the leaf comparison follows from '
                r'$9a^2<a_{\rm c}$. '+anchor)
        yield name,old,new


if __name__=='__main__':
    patch=''.join(''.join(difflib.unified_diff(old.splitlines(keepends=True),
        new.splitlines(keepends=True),fromfile=f'a/{name}',tofile=f'b/{name}'))
        for name,old,new in patched_files())
    (ROOT/'patches/h46-shared-side-75.patch').write_text(patch)
    print('Wrote independent conditional h46-shared-side-75.patch')
