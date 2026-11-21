# P104: sharp 8/8 networks and the first extra-node obstruction

This is a network-level result for the P104 labels, **not** a construction of a
legal #7113 caller word and not a proof of NET-D56. The constructions and
reductions below use PR [#7852](https://github.com/CrocSwap/integer-mult-bounds/pull/7852)
at head `41beda1d6435760dc99e38bd7e65f36798aad212`, by DreamingOfClouds with
Claude Opus 5.5, as their starting point. In particular:

* `Net8.lean`, Git blob `498fc7a0e23438823c8f5a5d8a647b5f9aab1791`, defines
  `N8.NetW`, `gatS`, `depS` and `drop`, and proves `net8` for exactly 8
  gatherers and 8 depositors. `NetW` does **not** include `b_k ≤ a_k` as a
  field; the word bridge supplies it.
* `DataIdA.lean`, Git blob `a5b7ff35d74ca0810edd243a6655d930f22777c6`,
  supplies the packed doubled E8 roots `rootCode`.
* `DecoderWall4Data.lean`, Git blob `90949f8d5dbcdee99974de505018768f4f9f640e`,
  supplies the 104 9-bit P104 labels `labs`.

The finite examples have been checked by an exact Python verifier; they are
not Lean-checked. The structural lemmas are paper proofs; they are not Lean
proofs. The example's 8/8 nonvacuity is a network instance, not a `Word`
instance. The 9/8 and 8/9 examples have **D = 56**, so they do not disprove
the desired D ≥ 56 extension.

## The exact network conditions

The nodes are ordered, the charts `a_k,b_k` are subspaces of F₂⁹, and
`F`, `G`, and strictly lower triangular `H` have rational entries. For each
port `p`, `q_p` is its 9-bit label, with the ordinary binary dot product.
The conditions checked are:

1. `F[k,p] ≠ 0` implies `q_p ∈ a_k`.
2. `G[s,k] ≠ 0` implies `b_k ⊆ q_s⊥`.
3. `H[k,j] ≠ 0` implies `j < k` and `b_j ⊆ a_k`.
4. `M = G (I-H)⁻¹ F` satisfies `M[s,p] = δ_sp c_s` whenever
   `q_s · q_p = 1`, with every `c_s ≠ 0`.

A gathering node has a nonzero row of `F`; a depositing node has a nonzero
column of `G`. The drop is `max(dim a_k − dim b_k, 0)` as a natural-number
subtraction. All explicit networks here also satisfy `b_k ⊆ a_k`, the
stronger bridge condition.

## Exact examples

The accompanying [p104_roots.json](p104_roots.json) is part of this
construction and contains the complete two 104-entry source tables; its
SHA-256 is `2693077172c0e3036fdc293f1d8d71d5f20830a3eb2a88c0cc4fc0623e6310b7`.
Write `r_p[i] = ((rootCode[p] >> (3i)) & 7) − 2` for `0 ≤ i < 8` and
`q_p = labs[p]`. No other instance data are required.

For each row below, let `f_i` and `d_i` be integer vectors in R⁸, `u_i`
and `v_i` be the indicated binary masks, and `e_i` the indicated integer.

| i | f_i | d_i | u_i | v_i | e_i |
|---:|---|---|---:|---:|---:|
| 0 | (0,0,0,0,-1,0,0,1) | (1,1,-1,-1,-1,1,-1,1) | 7 | 67 | 2 |
| 1 | (-1,0,0,0,0,1,0,0) | (-1,-1,-1,1,1,1,-1,1) | 25 | 137 | 2 |
| 2 | (-1,1,-1,-1,1,-1,1,1) | (0,0,-1,0,0,0,1,0) | 42 | 266 | 2 |
| 3 | (0,1,0,1,0,0,0,0) | (1,-1,1,-1,1,1,1,1) | 76 | 289 | -2 |
| 4 | (0,1,0,0,1,0,0,0) | (1,1,1,-1,1,1,-1,1) | 104 | 97 | 2 |
| 5 | (1,0,0,1,0,0,0,0) | (1,-1,-1,1,1,1,1,1) | 162 | 127 | 2 |
| 6 | (0,0,0,0,0,-1,0,1) | (-1,-1,1,1,1,-1,-1,1) | 448 | 52 | 2 |
| 7 | (-1,1,1,1,-1,1,1,1) | (0,0,1,0,0,0,1,0) | 491 | 82 | 2 |

The exact identity `f_i · d_j = e_i δ_ij` makes the two sets dual bases.
Set, for the 8 nodes `i=0,...,7`,

```
a_i = u_i⊥               b_i = span_F₂{v_i}
F[i,p] = f_i · r_p        G[s,i] = (d_i · r_s)/(8 e_i)
H = 0                    c_s = 1.
```

The finite checker verifies that all the `F` and `G` supports obey the
stated charts, each `b_i ⊆ a_i`, all eight nodes have both roles, and
`dim a_i=8`, `dim b_i=1`. The dual-basis identity yields
`M[s,p]=(r_s·r_p)/8`. The checker independently verifies every odd cell and
every diagonal for the 104 pinned labels, so it does not rely on a claimed
E8 parity identity. Hence this is an actual **8/8 NetW with D = 56**. It
supplies explicit network-level nonvacuity for `net8` and shows that its
bound is sharp.

For the 9/8 example, insert a new node before the eight nodes, numbered 0,
and renumber the old nodes 1,...,8. Move the sole read of port 0 from old
node 0 to the new node: `F[new,0]=-2`, `F[old 0,0]=0`, and leave all other
`F` and `G` entries unchanged. Take `a_new=b_new=span{11}` and add the
single relay `H[old 0,new]=1`. Port 0 has label 11 and `f_0·r_0=-2`;
the label belongs to the old `a_0`. The relay reconstructs exactly the old
input at old node 0. The new node has drop 0, the old eight each drop 7,
and **there are exactly nine active gatherers, eight active depositors,
D=56, and a gatherer with `dim a=1`**. Thus the proposed unconditional
extension of `N8.gat_dim` from eight to nine gatherers is false, even under
`b≤a` and at equality in the sought wall.

There is also a 9/8 example *outside* the conditional theorem below. Insert
two nodes ahead of the eight original nodes; both have zero drop, with

```
a_new0 = b_new0 = {x : x·7=0, x·1=0}
a_new1 = b_new1 = {x : x·7=0, x·510=0}.
```

These charts each have dimension 7 and lie inside the original first chart
`7⊥`. Move every nonzero read of the original first `F` row to exactly one
new node, according to whether the label's bit 0 is 0 or 1, and relay both
new nodes to the original first node with coefficient 1. All 104 source
labels have odd parity, so the `x·510=0` condition holds for a label with
bit 0 equal to 1; the original support already lies in `7⊥`. The old first
node keeps its deposit but has no F reads. The transfer stays unchanged,
and the resulting network has **9 gatherers, 8 depositors, D=56, and two
active gatherers with dimension 7**. It witnesses that the two-low case is
nonempty even at equality; it does not show D<56. The reversed network has
two active depositors of `dim b=2`.

Reverse the earlier one-read split as described below. The result has **eight gatherers,
nine depositors, D=56, and a depositor with `dim b=8`**, refuting the
unconditional extension of `N8.dep_dim` to nine depositors. These are legal
separators to those *intermediate dimension claims*, not to D ≥ 56.

## Time reversal and orthogonal complements

For any `NetW` on `n` nodes, let `rev(k)=n−1−k` and define

```
a'[rev(k)] = b_k⊥                    b'[rev(k)] = a_k⊥
F'[rev(k),p] = G[p,k]                G'[s,rev(k)] = F[k,s]
H'[rev(j),rev(k)] = H[k,j]           c'_s = c_s.
```

The binary dot product on F₂⁹ is nondegenerate and symmetric. Thus the F/G
support laws swap, and `b_j⊆a_k` becomes `b'_{rev(k)}⊆a'_{rev(j)}`.
The reversed order makes `H'` strictly lower triangular and the transfer is
`M'=Mᵀ`. On odd cells the old off-diagonal entry is zero, and on a diagonal
`c_s` remains the same. Therefore `NetW` and the diagonal condition are
preserved, with gatherer and depositor counts exchanged.

For each node, `dim a'=9−dim b` and `dim b'=9−dim a`; natural subtraction
gives exactly the original truncated drop, even if `b⊄a`. If `b⊆a`, the
reversed charts satisfy the same property. Consequently the whole 9/8
network D ≥ 56 question is equivalent to the 8/9 question. A single proof
or a single counterexample for one case settles the other.

## A conditional 9/8 theorem and its remaining obstruction

The following arguments use the P104 8-row rigidity already proved at the
pinned head (`N8.decPhi`, `N8.decLam`, `DFR.dyadicRigidity8`, and
`DF.row_span_ge_eight`) plus the relay cut `N8.cut_rank`. They do not use
the unproved decoder wall or the stronger `b≤a` condition.

**Theorem, paper proof.** Let a P104 `NetW` have exactly nine gathering
nodes and exactly eight depositing nodes. If at most one gathering node has
`dim a < 8`, then its total drop is at least 56. This includes the explicit
9/8 example above, whose one small gatherer has dimension 1. Reversal gives
the dual result: for 8/9, D ≥ 56 if at most one depositing node has
`dim b > 1`.

Proof. Let `T` be the 104-by-9 matrix formed by restricting the columns of
`G(I−H)⁻¹` to the nine gatherers. The P104 clique gives `rank M ≥ 8`, while
the eight columns of `G` at depositing nodes give `rank M ≤ 8` and
`rank T ≤ 8`. Since `M=T F_gat`, both ranks are exactly 8. The kernel of T
is one-dimensional; call the support of a nonzero kernel vector `C`.

For a gathering node `j` outside `C`, delete any `h∈C` algebraically from
the 9-column factorization by substituting its dependence on the other
eight columns. The corresponding `F` row at `j` is unchanged. This gives
an 8-row decoder, so the proved 8-row rigidity forces the span of its F
support, and hence `a_j`, to have dimension at least 8. Thus every
gatherer with `dim a<8` lies in `C`.

For each level `l=2,...,8`, let `Cl={k: dim b_k < l ≤ dim a_k}`. All
depositing nodes have `dim b≤1` by the original `dep_dim`. If no gatherer
is low, the original `cl_cut` applies. If exactly one gatherer is low, it
belongs to `C`, so the other eight columns of `T` are linearly independent.
All walks from those eight gatherers to any depositor meet `Cl`: absent a
crossing, dimension at least `l` propagates through each relay until it
contradicts `dim b≤1` at the destination. Apply `cut_rank` with an artificial
input matrix injecting independent unit inputs at just those eight high
gatherers. It implies `|Cl|≥rank(T_high)=8`. Summing the seven levels gives
`D≥Σ_{l=2}^8 |Cl|≥56`, using the same per-node crossing bookkeeping as
`N8.net8`. ∎

Two further exact restrictions identify what remains. If `C={h}`, its one
column is zero and the `h` row of F can be erased with no change to M, so
the pinned `net8` already applies. If `j,h∈C` are distinct, eliminating
`h` algebraically gives an 8-row decoder whose `j` input support lies in
the union of the original `j` and `h` supports. Rigidity therefore yields
`dim(a_j+a_h)≥8`. In particular, a hypothetical D<56 network must have at
least two low gatherers, both in the same dependence circuit, and any two
of its low-gatherer charts span at least eight dimensions.

More specifically, if `|C|=2`, let its chart dimensions be `d_1,d_2`.
For levels `2≤l≤min(max(d_1,d_2),8)`, the seven non-circuit columns plus
at least one of the circuit columns are independent and high, so `|Cl|≥8`.
At every remaining level up to 8, the seven non-circuit columns give
`|Cl|≥7`. It follows that

```
D ≥ 49 + max(min(max(d_1,d_2),8) − 1, 0) ≥ 52,
```

because `dim(a_1+a_2)≥8` forces `max(d_1,d_2)≥4`. This is a weaker
conditional lower bound than 56, not an extension of NET8.

One additional subcase closes at 56. Suppose all nine gathering charts have
dimension at least 7 and at most two have dimension below 8. If at most one
is low, apply the theorem above. With exactly two low, the other seven
columns of `T` are independent: both omitted low nodes are in `C`. Levels
2,...,7 cut eight independent columns, and level 8 cuts at least those
seven, giving `D≥55`. If **any depositing node d has b_d=0**, then `D≥56`.
Indeed, the rank-eight factorization through eight depositors forces every
row of `(I−H)⁻¹F` indexed by a depositor to be nonzero. Choose a nonzero
input-to-d contribution; it contains a support path from an active gatherer
to d. That path starts with `dim a≥7` and ends with `dim b=0`, so it meets
`Cl_1`. This one additional crossing is disjoint in the level count from
the crossings at levels 2,...,8. This argument, too, does not assume
`b≤a`. Thus a D<56 counterexample in this two-low, dimension-7 case would
also require every depositor's b chart to have dimension exactly 1.

### The remaining one-dimensional depositor charts

The following restriction applies to **any** P104 `NetW` with exactly eight
depositors, regardless of the number of gatherers or the size of D. If a
depositor's `b` has dimension 1, its unique nonzero vector must be one of
the 16 masks

```
7, 25, 42, 52, 67, 76, 82, 97,
104, 127, 137, 162, 266, 289, 448, 491.
```

Two different depositors cannot have the same one-dimensional `b`. For
each such b, the corresponding column of G has nonzero support on exactly
the 52 ports with `q_s·b=0`, and is zero on the other 52 ports.

Proof. Let `W=diag(c)⁻¹ G_dep` and let U be the eight effective input rows
at the depositing nodes, so `WU=diag(c)⁻¹M`. The clique and eight
depositors imply all three matrices have rank 8, so W has independent
columns and `col W=col(diag(c)⁻¹M)`. The upstream 8-row rigidity theorem
`DW6.rigid_gram` writes the latter matrix as `Λ Γ Λ⁻¹/2` for a diagonal
Λ with no zero entries and the signed E8 Gram Γ. Because `Γ=RRᵀ/4`, where
R has the 104 doubled-root rows, `col W=col(ΛR)`. Thus each W column has
the form `Λ R z` for a nonzero `z∈Q⁸`.

For `b=span{v}`, the G-support condition forces `r_s·z=0` for every
`s` with `q_s·v=1`. The separate exact checker
[`check_hyperplanes.py`](check_hyperplanes.py) examines all 511 nonzero
binary normals. For the 495 omitted masks, the outside-root matrix has
rank 8 over a prime field and hence at least 8 over Q. For the 16 masks
above, exact rational elimination gives rank 7, so its nullspace is a
single line. The checker also computes a null vector and confirms its
nonzero root evaluations occur exactly on the 52 inside ports. Therefore
v must be in the displayed list, and its W column is determined up to a
scalar once Λ is fixed. Two columns with the same v would be proportional,
contrary to their independence. Since c and Λ have no zero entries, the
same support statement holds for G. ∎

In the two-low dimension-7 subcase with a hypothetical D<56, the preceding
section forces all eight b charts to be one-dimensional; hence they must
be eight distinct members of this 16-element list, with their eight null
vectors linearly independent. The checker enumerates the 12,870 distinct
8-subsets and finds 8,766 with independent null vectors. This is a finite
restriction on the remaining case, not a proof that it is impossible. For
this last count, the computed integral null vectors have squared lengths
at most 8, so Hadamard bounds every 8-by-8 determinant by 4,096. The
2,147,483,647-prime modular determinant is therefore zero exactly when the
integer determinant is zero.

## Verification

Run `python3 check_separator.py` beside `p104_roots.json`; Python 3's
standard library suffices. The checker builds every rational matrix and
binary subspace from the formulas above, verifies support, DAG, relay,
`b≤a`, the entire rational transfer, all applicable odd-cell conditions, the
counts and drops, and the reversed example. It checks the fixture SHA-256.
If the two pinned Lean source files are placed alongside the checker, it
additionally verifies both Git blob IDs and the extracted source arrays.
Current output:

```
base: nodes=8, gathers=8, deposits=8, D=56
split: nodes=9, gathers=9, deposits=8, D=56
  gather dimensions: [1, 8, 8, 8, 8, 8, 8, 8, 8]
reversed split: nodes=9, gathers=8, deposits=9, D=56
two-low split: nodes=10, gathers=9, deposits=8, D=56
  gather dimensions: [7, 7, 8, 8, 8, 8, 8, 8, 8]
reversed two-low split: nodes=10, gathers=8, deposits=9, D=56
split port=0, label=11; all NetW and b≤a checks passed
```

There are 10,816 total cells; the verifier checks the odd-cell condition
wherever it applies and also checks its closed transfer formula on every
one of those cells. The claim is based on this exact
finite computation and the displayed elementary linear-algebra proofs, not
on a formal kernel replay. The Python checker and proof are new work; the
P104 data and 8-row rigidity are attributed to the pinned upstream package.
Run `python3 check_hyperplanes.py` for the finite rank and 52-support checks
used in the preceding restriction.
The campaign's `02-net-general` lane independently replayed the checker
against the pinned source blobs and reviewed the support, drop, reversal,
and conditional circuit argument; this was a paper/code review, not a Lean
verification. The present lane independently reviewed that lane's
cover-edge contraction argument and replayed its controls against the same
pinned data.

## Open next questions

* Resolve the general 9/8 case with at least two low gatherers. In the
  dimension-7/two-low case, a hypothetical D<56 must use eight distinct
  one-dimensional depositor masks from the stated finite set, with their
  associated null vectors independent. The equality example shows that
  this two-low case is inhabited.
* Formalize the reverse-network map, the synthetic-input cut, the small
  cases, and the concrete `NetW` nonvacuity in Lean, with the exact
  upstream hypotheses and natural-subtraction drop convention.
* Separately determine whether any explicit network here can be realized
  by a legal word; no converse to the word-to-network bridge is claimed.
