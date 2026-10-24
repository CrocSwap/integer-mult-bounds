# Exact identity-pivot Schur dimension, including singular products

**Written algebraic theorem with exact finite corroboration. No new kappa.**
Prepared for **ssafwann** with substantial **OpenAI Codex (gpt-6-astra)**
assistance, by one agent. Apache-2.0.

[PR4657](https://github.com/CrocSwap/integer-mult-bounds/pull/4657) leaves a gap
between its lower bound and its `4d` construction when the leading block `H`
of `PQ` has singular `H+H²`. This package closes that gap, including the first
open case `d=3,n=11`, and determines the minimum for **every prescribed H**:

\[
\boxed{n_{\min}(H)=4d+\dim\ker(H+H^2).}
\]

Consequently the minimum with H unrestricted is **4d for every d>=2** and
**5 for d=1**. The scalar conclusion agrees with Ryanson Jonathan's #4609.
For d=3, n=11 is impossible; n=12 is attained. Singular H+H² costs at least
one extra dimension beyond 4d, but is entirely compatible with sharpness.

The new step is that maximum Schur-commutator rank forces **both directions**
of the inclusion/projection maps on each of three joint eigenspaces to have
rank d. A rank estimate on the compressed blocks alone misses this condition.
A split factorization construction attains every resulting sector bound.

## 1. Statement and conventions

All matrices are over F2, act on column vectors, and need not be symmetric.
Let d>=1, and let commuting idempotents P,Q on V=F2^n have leading blocks I_d:

\[
P=\begin{pmatrix}I&R\\ C&D\end{pmatrix},\quad
Q=\begin{pmatrix}I&L\\ E&F\end{pmatrix},\quad
S=D+CR,\quad Z=F+EL,\quad K=SZ+ZS.
\]

Write U=F2^d, let i:U->V be the coordinate inclusion and pi:V->U the
coordinate projection, and put H=pi PQ i, W=I+H. Define

\[
a=\dim\ker H,\quad b=\dim\ker W,\quad t=\dim\ker(H+H^2)=a+b.
\]

The last equality holds without diagonalizability: if H W x=0 then
x=W x+H x, with W x in ker H and H x in ker W; these two kernels intersect
trivially because H+W=I.

**Theorem.** For every prescribed H in M_d(F2), the least n admitting such
P,Q with rank K=2d and pi PQ i=H is 4d+t. Moreover, write

\[
V=V_{00}\oplus V_{10}\oplus V_{01}\oplus V_{11}
\]

for the simultaneous eigenspaces of P,Q, and r_ab=dim V_ab. Every sharp pair
satisfies

\[
(r_{00},r_{10},r_{01},r_{11})
\ \ge\ (d-b,d+b,d+b,d+a) \tag{1}
\]

componentwise. All four equalities are attainable simultaneously, for every H.
In particular rank P and rank Q are each at least 2d+t, and the construction
attains equality in both. These are existential finite-dimensional statements,
not header counts or uniform physical implementations.

## 2. Factorization and the six-map criterion

The four joint projectors are

\[
E_{00}=(I+P)(I+Q),\quad E_{10}=P(I+Q),\quad
E_{01}=(I+P)Q,\quad E_{11}=PQ.
\]

They sum to I and pairwise annihilate. Set Y_j=E_j i:U->V_j and
X_j=pi|V_j:V_j->U. Their products are

\[
X_{00}Y_{00}=X_{10}Y_{10}=X_{01}Y_{01}=W,\qquad X_{11}Y_{11}=H. \tag{2}
\]

Here is the identity-pivot specialization of Nick Petalas's ordered
factorization (#4597), as used in #4657:

\[
K=A_0B_0,\qquad A_0=(ZC\ \ C+E),\qquad
B_0=\begin{pmatrix}R+L\\RZ\end{pmatrix}. \tag{3}
\]

For completeness, put G=(PQ)21 and T=(PQ)12. Commutation gives
RE=LC=H+I, DE=G+C, FC=G+E, RF=T+L, LD=T+R and
DF+FD=ER+CL. Expanding SZ+ZS and substituting these equalities yields

\[
K=G(R+L)+(C+E)T+CHL+EHR.
\]

Since ZC=G+EH and RZ=T+HL, this is exactly (3). No preceding executable or
unwritten lemma is needed to check the identity.

Use ambient versions of the two factors:

\[
A=\big(QPi+QiH\ \ (P+Q)i\big):U^2\to V,\qquad
B=\begin{pmatrix}\pi(P+Q)\\\pi PQ+H\pi Q\end{pmatrix}:V\to U^2.
\]

We have pi A=0 and B i=0. In the decomposition V=iU direct-sum ker pi,
A has bottom block A_0 and B has right block B_0. Thus their ranks equal
those of A_0,B_0. In joint-sector coordinates their actions are

\[
A(x,y)=\big(0,\ Y_{10}y,\ Y_{01}(Hx+y),\ Y_{11}Wx\big), \tag{4}
\]
\[
B(v_{00},v_{10},v_{01},v_{11})=
\big(X_{10}v_{10}+X_{01}v_{01},\ HX_{01}v_{01}+WX_{11}v_{11}\big). \tag{5}
\]

**Criterion.** rank K=2d if and only if all three Y_10,Y_01,Y_11 are
injective and all three X_10,X_01,X_11 are surjective.

**Necessity.** If rank K=2d, (3) makes A injective and B surjective.
For any nonzero z in a proposed kernel of a Y map, (2) supplies the relation
in the middle column, and (4) gives the nonzero kernel vector in the last:

| Supposed kernel | Forced relation | Vector killed by A |
|---|---|---|
| Y_10 z=0 | Hz=z | (z,z) |
| Y_01 z=0 | Hz=z | (z,0) |
| Y_11 z=0 | Hz=0 | (z,0) |

All three are contradictions. Apply the same argument to P^T,Q^T: their
pivots are I, they are commuting idempotents, their Schur commutator is K^T,
and their sector-inclusion maps are the transposes of the original
sector-projection maps, after identifying each sector with its image.
Equivalently rank(E_j^T i)=rank(pi E_j)=rank X_j. It follows that each X_j
for j=10,01,11 has rank d, hence is surjective.

**Sufficiency.** If the three Y maps are injective, A(x,y)=0 first gives
y=0, then Hx=0 and Wx=0, hence x=0. If a row covector (u,v) annihilates B,
(5) on sectors 10,01,11 gives

\[
uX_{10}=0,\quad (u+vH)X_{01}=0,\quad vWX_{11}=0.
\]

Surjectivity of the X maps implies u=0, vH=0 and vW=0, hence v=0. Thus B
is onto. Because B i=0, its restriction to ker pi is also onto. The product
A_0 B_0 therefore has rank 2d. This proves both directions of the criterion;
it does not confuse the rank of a rectangular product with its reverse.

## 3. Sharp lower bound and construction for every H

For j=10,01,11, the criterion and the rank inequality for X_j Y_j give

\[
\operatorname{rank}(X_jY_j)\ge
\operatorname{rank}X_j+\operatorname{rank}Y_j-r_j=2d-r_j.
\]

With (2), this proves r_10,r_01>=d+b and r_11>=d+a. The remaining sector
needs only r_00>=rank W=d-b. Summing proves n>=4d+a+b=4d+t.
Also rank P=r_10+r_11 and rank Q=r_01+r_11, proving their stated bounds.

To attain all of these bounds, factor a d-by-d matrix T through dimension
**d+nullity(T)** with an injective right factor and surjective left factor.
Choose columns N_T forming a complement to im T, and take

\[
X_T=(T\ \ N_T),\qquad Y_T=\begin{pmatrix}I\\0\end{pmatrix}.
\]

Then X_T Y_T=T, Y_T is injective and X_T is surjective. Use this factorization
for W in sectors 10 and 01, and for H in sector 11. In sector 00 take any
rank factorization X_00 Y_00=W through dimension rank W; the zero-dimensional
sector is allowed when W=0. Form

\[
i=\begin{pmatrix}Y_{00}\\Y_{10}\\Y_{01}\\Y_{11}\end{pmatrix},\qquad
\pi=(X_{00}\ \ X_{10}\ \ X_{01}\ \ X_{11}).
\]

Then pi i=W+W+W+H=I. On the four-sector ambient direct sum set
P0=diag(0,I,0,I), Q0=diag(0,0,I,I), with the stated sector dimensions.
They are commuting idempotents, and

\[
\pi P_0i=\pi Q_0i=W+H=I,\qquad \pi P_0Q_0i=H.
\]

Choose columns N forming a basis of ker pi. The matrix M=(i N) is invertible:
pi i=I gives V=im i direct-sum ker pi. Therefore

\[
P=M^{-1}P_0M,\qquad Q=M^{-1}Q_0M
\]

have precisely the required coordinate pivots and product compression. All
six active maps have rank d, so the criterion makes rank K=2d. The ambient
dimension is exactly (d-b)+2(d+b)+(d+a)=4d+t. This proves the fixed-H theorem
without assuming that H is invertible, semisimple, or a field generator.

For unrestricted H, use the credited seeds from lee-phys's #4634:

\[
H_2=\begin{pmatrix}0&1\\1&1\end{pmatrix},\qquad
H_3=\begin{pmatrix}0&0&1\\1&0&1\\0&1&0\end{pmatrix}.
\]

They satisfy H2²+H2+I=0 and H3³+H3+I=0, which imply that both H and I+H
are invertible. Direct sums of H2 cover even d>=2; one H3 plus copies of H2
cover odd d>=3. Thus t=0 is attainable for every d>=2. For d=1, H is 0 or 1,
so t=1 and the fixed-H theorem gives n=5. This recovers the predecessor
scalar minimum, rather than claiming that known case as new work.

## 4. A singular, non-semisimple witness

For H=((0,1,0),(0,0,1),(0,0,0)), we have a=1,b=0,t=1. The optimal sector
dimensions are (3,3,3,4), so n=13 and rank P=rank Q=7. The construction
produces the following literal matrices (each binary string is one row):

```text
P =                    Q =
1001100000100          1000001100100
0100110000010          0100000110010
0010010000001          0010000010001
0000100000100          1000001100100
0000010000010          0100000110010
0000000000001          0010000010001
1001100000100          0000000100100
0100110000010          0000000010010
0010010000001          0000000000001
0001100001100          0000001101100
0000110000110          0000000110110
0000010000011          0000000010011
0000000000001          0000000000001
```

The verifier directly checks P²=P, Q²=Q, PQ=QP, both I3 pivots, the prescribed
H, and rank[S,Z]=6. This discriminates between a singularity obstruction at
n=4d and the incorrect assertion that singular H+H² forbids sharpness at all.

## 5. Reproduction and evidence boundaries

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/identity-pivot-sector-bound
python3.12 -B scripts/check_research_commit.py --package research/identity-pivot-sector-bound --check-source-history
```

The registered commands run ordinary and optimized (`-O`) checks, using explicit
exceptions. A Git-free export can run `python3.12 -I -O -B verify.py` directly.
No predecessor executable or external mathematical input is loaded. The all-size
claims above are written proofs; finite checks corroborate their identities and
construction rather than replacing them.

- All **530** matrices H of sizes 1,2,3 are constructed and checked by direct
  full-matrix multiplication and elimination, including every singular H.
  Dimension distributions: d=1: {5:2}; d=2: {8:2,9:6,10:8};
  d=3: {12:48,13:196,14:210,15:58}. Counts concern H, not headers or all pairs.
- The 4d family is checked at d=2..12. The literal nilpotent witness and a
  larger-ambient zero padding are checked separately.
- All ordered identity-pivot commuting-idempotent pairs at (n,d)=(3,1) and
  (4,2) are checked: 253 and 1,219 pairs. Both coordinate descriptions of the
  factors, the six-map criterion and all sector inequalities are checked.
  Their commutator rank distributions are {0:241,1:12} and {0:1147,1:72}.
- Six one-sided degenerations preserve commutation, idempotence and identity
  pivots but remove exactly one of the six map conditions, and lose sharpness.
  Four further controls reject nonbinary data, universal 4d attainment for
  fixed singular H, a blanket singular-product exclusion, and applying this
  theorem to #4634's nonidentity-pivot pair. Ten controls total.

Independent human review, formal proof-kernel verification, complete-header
counts and physical supplier admission are unclaimed. Lean, Docker and the
selected scientific cold replay are outside this isolated algebraic task.
Hosted CI status is reported separately in the PR; local passes do not imply
hosted execution or scientific acceptance.

## 6. Scope, coordination and credit

Base: canonical main `b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`, priority revision 7,
selected conditional kappa 0.00302015. The task is a **changed**
`formal-interface-lemma` card: the explicit open handoff from #4657, not a
Lean theorem or a proof about the selected caller. Coordination and the family
expansion decision are in [Discussion4653](https://github.com/CrocSwap/integer-mult-bounds/discussions/4653).

The decision is **narrow, then stop this dimension question**. The theorem and
construction supply exact algebraic dimensions and ranks. Header selection and
emission, physical reads, owned/borrowed state, dirty compensation/restoration,
stock, dispatch and the complete consumer bill remain unknown, not zero. This
result changes a dimension-existence decision, with no claimed paid-work saving,
new kappa, selected-frontier change or supplier implementation. A subsequent
header/caller question needs a separate contract and cost allowance.

Predecessors (inspected open, author-reported status; no acceptance implied):

| Contributor / source | Exact inspected head | Reused contribution |
|---|---|---|
| ssafwann, #4657 | `b79f90bc8d839a4998a40b10bcb437e87baa8397` | Identity factorization, prior dimension bounds and 4d family, open singular case; basic matrix helpers adapted |
| Nick Petalas, #4597 | `dfeb8ca729a04aea4aa290438f2ed50a37a9c7cb` | Ordered Schur factorization; retained #4278/#4259/#4228 lineage |
| Ryanson Jonathan, #4609 | `eb5ccf9288808d973551e6264300d30d2f6e48a0` | Previously established scalar binary minimum |
| Ryanson Jonathan, #4617 | `96c01a2124e234d798e9e97643c20fb5b430840d` | Identity-pivot 5d family and dimension question; Claude Code assistance disclosed there |
| lee-phys, #4634 | `9f053f7051e5fc3327d4337bb4bd8ac52cf5fcd0` | Unrestricted invertible-pivot 3d optimum; reused seeds and nonidentity control formula; OpenAI Codex assistance |

Cinna Davis's #4100 supplies the earlier BIT request/header setting. The new
contribution is the six-map criterion, sharp prescribed-H bound and construction.
Pending sources are exact citations, with byte hashes in TASK.json, not runtime
Git dependencies. No predecessor archive is modified or duplicated. Repository
tooling retains Douglas Colkitt's and the other tool contributors' attribution.

## Open next questions

The identity-pivot minimum, including prescribed H, is now closed by the written
argument. The nearby remaining interface question is a **count**, not a new seed:
for a fixed pair of commuting binary idempotents, how many complete coordinate
headers make all six maps full rank while giving identity pivots? The criterion
identifies the simultaneous conditions but does not count them. Start with one
small fixed sector decomposition and enumerate complete invertible headers,
checking the six-map count against direct Schur ranks. Any density claim must
specify its ensemble and preserve dependencies among the six events; a product
of marginal counts is not justified. No claim is held on that follow-up, and no
physical implementation should be inferred from such a count alone.
