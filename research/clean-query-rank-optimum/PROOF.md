# Eight is the least paid rank for the four-call clean six-target problem

## 1. Exact scope and credited attainment

Let $K$ be any field of characteristic two and let
$\mathcal A=K[Q]/(Q^2-1)$, with $Q$ a formal central involution.
There are six public coordinates and any finite number $h\geq0$ of
zero-initialized helpers. Free gates are arbitrary constant matrices in
$\operatorname{GL}_{6+h}(K)$. Paid gates are $I+QN_i$, where $N_i$ is a
constant matrix on the **entire** public-plus-helper space,
$N_i^2=0$, and $r_i=\operatorname{rank}N_i\leq2$.
At most four paid gates are allowed. The required endpoint is precisely

\[
             W(x,0)=(Qx,0)\qquad\text{for every }x\in\mathcal A^6.
\]

Every such word has total paid rank $S=\sum_i r_i\geq8$.
Consequently any feasible word under the stated caps has exactly four
rank-two paid calls. The construction of
[PR6808](https://github.com/CrocSwap/integer-mult-bounds/pull/6808),
at head 518351a389e32e2ccdf0a1ca55580e9c60d65492, attains $S=8$
with two clean helpers. Thus eight is the minimum total paid rank,
allowing any finite clean workspace, in this at-most-four-call model.
The attaining construction and its minimum-helper theorem are credited,
not reconstructed or replayed here.

The method is the classical full-rank factorization and $UV/VU$ fixed-space
argument used in Nick Petalas's
[PR6800, section 3](https://github.com/petalas/integer-mult-bounds/blob/c94197e40c9e8a25f643d776160659871e5ce9ac/research/restored-dirty-query-capacity/PROOF.md).
Its projection case already gives $r_i\leq S-n$. The point checked here is
that the same needed inequality survives the weaker clean public-column
promise, without assuming the normalized matrix is a projection. The
retained source manifest governs the exact predecessor paths and bytes.

## 2. Normalize the word without losing helper columns

Put $\varepsilon=Q+1$. In characteristic two,
$\mathcal A=K[\varepsilon]/(\varepsilon^2)$, with $1,\varepsilon$
linearly independent over $K$. For every permitted paid term,

\[
 I+QN_i=(I+N_i)(I+\varepsilon N_i).
\]

The constant factor $I+N_i$ is invertible. Moving all constant factors and
free gates to the left conjugates the $N_i$ by constant invertible matrices.
After relabeling these conjugates, the full word is

\[
 W=C(I+\varepsilon M),\qquad
 M=\sum_i N_i,\qquad N_i^2=0,\quad
 \operatorname{rank}N_i=r_i,\quad C\in\operatorname{GL}_{6+h}(K).
                                                               \tag{1}
\]

Products of two $\varepsilon$ terms vanish; no commutation of the $N_i$
is needed. All matrices in (1) still act on all $6+h$ coordinates.

Let $P=K^6\oplus0_h$ be the public subspace. Compare the two formal
coefficients of the clean endpoint on $p\in P$. They give

\[
                    Cp=p,\qquad CMp=p.
\]

Since $C$ fixes $P$ pointwise, so does $C^{-1}$. Therefore

\[
                           Mp=p\quad(p\in P).             \tag{2}
\]

This does not say $C=I$ on the helper columns, nor that $M^2=M$.
In public/helper blocks it only says
$M=\begin{pmatrix}I_6&B\\0&D\end{pmatrix}$ for unspecified $B,D$.
The proof below retains them. Evaluating only $Q=1$, or replacing these
columns by zero, would not justify (2) or the desired formal endpoint.

## 3. The fixed-subspace rank lemma

The following lemma holds over **any** field, with no characteristic
restriction. Let $H$ be a finite-dimensional vector space, let
$N_i\in\operatorname{End}(H)$ be square-zero, and suppose
$M=\sum_iN_i$ fixes pointwise a subspace $P\subset H$ of dimension $d$.
Write $r_i=\operatorname{rank}N_i$ and $S=\sum_i r_i$. Then

\[
                         S\geq d+\max_i r_i.              \tag{3}
\]

To prove it, factor each nonzero term through $L_i=K^{r_i}$ as
$N_i=U_iV_i$, with $U_i:L_i\to H$ injective and
$V_i:H\to L_i$ surjective. Square-zero gives $V_iU_i=0$:
for any $w=V_ix$, the equality
$U_i(V_iU_i)w=N_i^2x=0$ and injectivity of $U_i$ imply this claim.
Zero terms can be omitted.

Set $L=\bigoplus_iL_i$, so $\dim L=S$, and concatenate the maps as

\[
 U:L\to H,\qquad V:H\to L,\qquad UV=M,\qquad E=VU.
\]

Because $UVp=p$ on $P$, the restriction $V|_P$ is injective:
$Vp=0$ would imply $p=UVp=0$. Moreover

\[
                  E(Vp)=VUVp=Vp.
\]

Thus the fixed space of $E$ contains $V(P)$ of dimension $d$.
Rank-nullity implies
$\operatorname{rank}(I_L-E)\leq S-d$.
On the other hand its call-diagonal block on $L_i$ is
$I_{r_i}-V_iU_i=I_{r_i}$. A submatrix cannot have larger rank than the
full matrix, so $\operatorname{rank}(I_L-E)\geq r_i$ for each $i$.
Combining the two inequalities proves (3).

Only an inclusion in the fixed space is used. The argument neither
identifies its entire fixed space nor imposes a polynomial identity on
$E$ or $M$. It is consequently valid for arbitrary helper dimension and
arbitrary helper columns.

## 4. Apply the lemma to the four-call problem

Apply (3) to (1)--(2), with $d=6$. A feasible word has positive total
rank. Pad with zero-rank terms to four positions if necessary.
The largest of these four ranks is at least $S/4$, so

\[
                S\geq6+\max_i r_i\geq6+S/4.
\]

Hence $S\geq8$. The rank caps also give $S\leq4\cdot2=8$.
Equality forces four nonzero calls, each of rank two. Together with the
credited PR6808 word this proves the exact optimum asserted in section 1.
No finite matrix experiment or census is needed for this universal lower
bound.

The at-most-four-call hypothesis is essential to this deduction.
It is not an optimum over unrestricted call counts, a classification
for other public dimensions, or a reproof of the minimum-helper result.
The factorization lemma itself is field-independent; the formal-query
normalization and application here require characteristic two.

In particular, removing the four-call cap already allows a credited
smaller-total-rank word. PR6800's theorem, using the workspace-free
attainment of Josie Elliston6138, applies at $n=6$, $k=7$, $r=1$:
$m_7=6$ and $6+\lceil6/6\rceil=7$. It supplies seven rank-one calls
with no workspace and total paid rank seven. That endpoint also satisfies
the clean promise, and unused zero helpers can be appended. Thus a
rank-eight lower bound without the four-call restriction would be false;
this is a known predecessor boundary, not a new construction or an
unresolved claim about unrestricted calls. No such word is replayed here.

## 5. Evidence, lineage, and remaining obligations

This is a source-aware written proof. The coordinator supplied the proposed
fixed-space extension before this draft, and the author had prior exposure
to PR6800 and PR6808. It is not blind discovery, human acceptance, or a
formal-kernel certificate. Any separately reported finite checks must
state their observed domains and do not substitute for the quantified
argument above. No predecessor program, construction, matrix experiment,
or checker was executed by this proof role.

Nick Petalas6800 supplies the normalization, projection Gram-complement
method, and clean-versus-dirty boundary; ToikY/Codex6808 supplies the
four-rank-two clean word and its helper theorem. Josie Elliston6138,
Nick Petalas6122, Cinna Davis's simplex/controller line, Ali Romman5617,
and Matarener6114 retain the lineage credited by those sources.

Paid rank here is an abstract query cost. Preparation and ownership of
the zero helpers, implementation and pricing of free bases, native
alignment and chronology, precision, cleanup/restoration outside the
stated endpoint, and a complete physical supplier invoice remain open.
No selected-frontier, multiplication exponent, or all-five-assumptions
admission follows.
