# The shortened quotient has no commuting rank-two stage system

**Source-bound application of a known support obstruction; no new κ.** The
18-dimensional shortened root in Section 7 cannot have pairwise-commuting
rank-two idempotents supporting all eighteen full queries. This excludes every
such family, beyond the explicit repaired projectors whose first pair fails to
commute. The proof concerns supporting subspaces alone and introduces no
caller, stage-price, ordinary-control, or prefix-commutation assumption.

## 1. Exact sources and relation to prior work

The quotient uses DreamingOfClouds's CrocSwap/integer-mult-bounds#6833, head
`51f54e3c31f2f3a3e056a483b3ed66ae916ad06a`. Retained `chain_root.py` has Git blob
`ca1e0244f1329c153c1224b05bf0c0c5d5e2367b` and SHA256
`6f4046c804f27071d88ce05820c75baebe9cbf32533c4ba89285c413bfc8edaa`.
The exact construction is recorded in the
[published block-carrier proof, Section 7](https://github.com/CubeJerry/integer-mult-bounds/blob/cda67c44abe75022a3048714b7e7270097564bdf/research/p104-block-bridge-carriers/PROOF.md).

Ali Romman's CrocSwap/integer-mult-bounds#6398 already proves the support
obstruction below, including the absence of a prefix-commutation premise.
Its exact proof is `research/mixed-projector-root-headroom/PROOF.md`, Section 2,
at head `dee2663ba0918be86993fd9d63c8d64b020f4c83`, Git blob
`f910b5fbf9a9d519fa7d7c7503de51df5a796368`, SHA256
`68be52ab098ff9dd6edfe938e5bf36d14d5f49aa1cac94a3d0784566c05363e9`.
The same proof is retained by CrocSwap/integer-mult-bounds#6717.
The query-defect and shortest-header lineage also includes
CrocSwap/integer-mult-bounds#6832 and CrocSwap/integer-mult-bounds#6842.

This note independently reproduces that known argument and verifies its exact
applicability to the new quotient. No new general support threshold is claimed.
The parallel [all-defect support study](https://github.com/CubeJerry/integer-mult-bounds/blob/b269b953f1e06583551470b088d4632a282e149c/research/noidle-root-defect/PROOF.md)
addresses non-shortest roots; it is not needed as a premise here.

## 2. Known lemma: at most two supports when n is at least four

Work over a field of characteristic different from two. Suppose `n>=4` and `N=n+1`
nonzero rank-one square-zero queries `R_i=x_i y_i` satisfy

\[
(I-2R_{N-1})\cdots(I-2R_0)=-I_n.
\]

If `F` selected queries admit pairwise-commuting rank-two idempotents `J_i`
with `J_iR_i=R_iJ_i=R_i`, then **`F≤2`**.

### Normalize the Gram without changing the queries

Write `X=[x_0 ... x_{N-1}]`, let `Y` have rows `y_i`, and put
`G=YX`, `A=I+2 lower(G)`. Ordered-product expansion gives
`XA^{-1}Y=I_n`. Hence `Q=A^{-1}YX` is a rank-`n` idempotent and

\[
H=A-G=A(I-Q),\qquad \operatorname{rank}H=N-n=1.
\]

Its diagonal entries are one and its off-diagonal entries are
`H_ij=sign(i−j)G_ij`. Factor `H=uv`. Every `u_i v_i=1`, so all these scalar
factors are nonzero. The gauges `x_i→u_i x_i`, `y_i→u_i^{-1}y_i` leave `R_i`
and its supporting idempotent unchanged, and yield

\[
y_ix_j=\operatorname{sign}(i-j)\quad(i\ne j),\qquad y_ix_i=0.\tag{1}
\]

### Intersecting support edges occupy at most three coordinates

Commuting idempotents simultaneously diagonalize over the original field by
successive image/kernel splittings. Each selected `J_i` then has a two-element
coordinate support `C_i`. Since `R_i` has rank one, its support equations imply
`J_ix_i=x_i` and `y_iJ_i=y_i`. By (1), every two selected supports intersect.

A pairwise-intersecting family of two-element sets, allowing repeats, is either
a star or is contained in a triangle. Indeed, take two distinct edges `{a,b}`,
`{a,c}`. If another edge misses `a`, it must be `{b,c}`; any further edge
meeting all three belongs to that same triangle. If there are no two distinct
edges, the family is already a star.

A star cannot have three distinct leaves. Choose chronological indices
`i<j<k` with distinct leaves and common hub `a`. All pairwise cross-Grams then
factor solely through that hub. Put `α_l=x_l[a]`, `β_l=y_l[a]`; these scalars
are nonzero because their cross-products equal `±1`. The equations

\[
\beta_i\alpha_j=\beta_i\alpha_k=-1,\qquad
\beta_j\alpha_i=\beta_k\alpha_i=1
\]

imply `α_j=α_k` and `β_j=β_k`. But then `β_jα_k=β_kα_j`, contradicting their
required values `−1` and `1`. Characteristic different from two is essential.
Thus a star has at most two distinct leaves, and its union has at most three
coordinates; a triangle has the same bound. Repeated supports add no coordinates.

If three selected queries existed, extend their indices to four; there are
enough positions since n>=4. The four-site sign Gram is invertible, so both the
selected three columns and the selected three rows are independent. The
integer inverse of S4 has entries `(-1)^(i+j)sign(i−j)`.

Their supporting union has dimension at most three. Independence forces its
dimension to equal three, and both restricted three-by-three factor matrices
are invertible. Their product would make the selected Gram invertible. But
that Gram is S3, whose rank is two. This contradiction proves the known F<=2
bound. It uses both column and row independence, not the column-only dimension
argument that would yield the weaker universal F<=3 statement.

### The dimension exception and an attaining two-support control

In dimension two use

\[
(x_0,y_0)=((1,0),(0,-1)),\quad
(x_1,y_1)=((0,1),(1,0)),\quad
(x_2,y_2)=((-1,1),(1,1)).
\]

All three queries are nonzero rank one and square zero, and their chronological
product is `−I_2`. Taking every supporting projector to be `I_2` attains `F=3`.
This is a boundary control showing why n>=4 is needed; it is not a new theorem
or a profitable supplier. In the canonical n=4, N=5 root, the first and last
queries share the rank-two projector `x_0 y_4 - x_4 y_0`, attaining two
commuting supports. Both controls are checked exactly.

## 3. Apply the lemma to the exact 18-dimensional quotient

Use this package's notation `P=P_E+P_v`, `R=I−P`, and `W=im R`. The source has
twenty coordinates and `rank P=2`, so `dim W=18`. Every full query
`N_i=x_i y_i` obeys `PN_i=N_iP=0`. Its nonzero column lies in `W`; its nonzero
row vanishes on `im P`, so its restriction to `W` is still nonzero rank one.
It remains square zero. The middle query `uw*` has the same properties:
`Pu=0`, `w*P=0`, `w*u=0`, with both factors nonzero.

The bridge decomposition is `B=I−2P−2uw*`. Replace the three thin factors by
`I−2uw*=B+2P`. Every surrounding full query fixes `P` on both sides, so the
complete source endpoint changes from `−I_20` to `−I_20+2P`. Its restriction
to `W` is `−I_W`. There are precisely eighteen full factors and one thin factor:

\[
n=18,\quad N=19=n+1,\quad F=18.
\]

A commuting rank-two supporting family for those eighteen full factors would
contradict the known lemma's `F≤2`. The conclusion covers every such family,
not only compression, local repairs, or a particular quotient basis.

## 4. What remains open

The common-coordinate rank-two branch of the shortened word's productive
interface problem is closed. Individual rank-two projector repairs remain
valid, but no alternative rank-two supporting family can make all eighteen
commute. Global ordinary similarity cannot change this obstruction.

The lemma does **not** require no idle work, productive-target pricing,
stage variables, actual-prefix commutation, or the ordinary-control hypotheses
used elsewhere to interpret a full caller. It uses only the stated root,
rank, characteristic, and supporting-projector assumptions. A proposed escape
must change at least one of those assumptions; relabeling the same supports
or choosing different local rank-two projectors cannot suffice.

Noncommuting target representations, larger stages and their paid idle work,
changed query counts or ranks, non-square-zero aggregates, additional restored
state, and different native suppliers remain separate possibilities. Each
still needs a complete arbitrary-input identity, restoration and a favorable
recursive invoice. The corollary changes neither the finite-mask price result,
the selected frontier nor its five inherited framework assumptions.

The source and quotient identities are already checked by this package's
primary and independent geometry replays. `verify_quotient_support.py` supplies
small exact controls for the sign inverse, the n=2 exception, the attaining
two-support example, and
a four-query support family that fails exactly the commutation premise. A
corrupted inverse is detected. The universal conclusion is the proof above,
not a finite-search inference. After placing the checker beside this note:

```bash
python -B research/p104-block-bridge-carriers/verify_quotient_support.py
python -O -B research/p104-block-bridge-carriers/verify_quotient_support.py
```

Both commands print `PASS_KNOWN_QUOTIENT_SUPPORT_CAP`, with dimension-exception
example `n=2, N=3, F=3`, the known cap two for n>=4, and four noncommuting projector
pairs in the omitted-commutation boundary control. Both modes were executed.

Prepared for @CubeJerry with substantial OpenAI GPT-6 Astra Pro assistance and
independent mathematical review. Credit Ali Romman (#6398), the retained source and query-defect
lineage named above. Apache-2.0.
