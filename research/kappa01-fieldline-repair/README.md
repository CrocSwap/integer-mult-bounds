# The C4-free fitting-rank gate for the field-line repair

**The proposed `F_(2^k)^3` line family cannot reach κ = 0.1 through its scalar
one-array-per-query decoder contract.** A source-derived rank argument gives
more than `V/4` paid scalar queries, each of native rank at least `k`. With
three stages this forces target moment greater than

```
3*(2/7)^(8/9) + (3/8)*(1/7)^(8/9)
    = 1.051658213344872... > 1.
```

This applies to every `q=2^k`, including large fields not excluded by a
particular independent-set bound. It does not exclude matrix-valued payload
coding, a multi-array native primitive, changed endpoint masks, fused public
data legs, another coverage law, or another multiplication framework.

## 1. The geometric family and its exact permission graph

Let `F=GF(q)`, `q=2^k`, with the symmetric nondegenerate bilinear form

```
B((z,x,y),(z',x',y')) = z*z' + x*y' + y*x'
```

on `F^3`. For each `a=(x,y)` in `F^2`, define the `F`-line
`E_a = F*(1,x,y)`. Regard it as a binary subspace of dimension `k` under
the trace form `Tr_(F/F2) B`; the ambient binary dimension is `h=3k`.
Each `E_a` is nondegenerate because its restricted form is `Tr(s*t)`.
There are `V=q^2` such ports, with

```
E_a orthogonal to E_b  iff  det(a,b)=1.
```

This defines a simple undirected graph `G` on `F^2`: the determinant is
symmetric in characteristic two and `det(a,a)=0`. The zero vector is
isolated. Two distinct vertices have at most one common neighbor. If they
are linearly independent, the equations `det(a,c)=det(b,c)=1` have one
solution. If `b=t*a` with `t!=1`, they have none; zero vertices have none.
Thus `G` has no four-cycle, even as a non-induced subgraph.

The [finite field reconstruction](../kappa01-repair/field_geometry.py) and
its receipt check representative fields, trace pairing ranks and exact
coclique controls. The argument here covers all field sizes algebraically.

## 2. A rank bound for arbitrary complex fitting matrices

**Lemma.** Let `G` be any simple undirected C4-free graph on `n>0` vertices.
Every complex matrix `M` with nonzero diagonal and `M_ij=0` whenever distinct
`i,j` are nonadjacent has

```
rank_C(M) > n/4.
```

No symmetry, positivity, integrality, normality or common eigenbasis of `M`
is assumed. Allowed off-diagonal entries may vanish or have arbitrary
complex values.

The proof uses the matrix-scaling method of Codenotti, Pudlak and Resta,
*Some structural properties of low rank matrices related to computational
complexity*, revised ECCC TR97-043 (1998), Section 4, particularly Lemma 11
and Corollary 13, pages 10. Their real-matrix consequence is rank greater
than `n/6` for this mask; Haviv's *On Minrank and Forbidden Subgraphs*
(APPROX/RANDOM 2018), Section 1.2, explicitly records it. The argument below
specializes their method to undirected masks using a three-column overlap
bound. No claim of novelty or optimality is made.

**Reduction to total support.** Make the directed support graph of `M`,
with arc `i -> j` when `M_ij!=0`. Simultaneously permuting rows and columns
by strongly connected components makes `M` block triangular. Each diagonal
block has total support: every nonzero off-diagonal entry belongs to a
directed cycle, which extends to a nonzero permutation diagonal by fixing
all other vertices. Diagonal entries already have that property. For such
blocks, the rank of the full matrix is at least the sum of their ranks,
as seen by combining nonsingular minors into a block triangular minor.
It therefore suffices to treat a block with total support.

**Scaling.** Apply positive row and column scaling to `|M_ij|^2`. The
total-support scaling theorem of Sinkhorn and Knopp (1967, pages 343--346)
gives diagonal scalings making this matrix
doubly stochastic. Taking square roots of those scalings gives a matrix
`B` with the same complex rank and support as `M`, and

```
sum_j |B_ij|^2 = 1,       sum_i |B_ij|^2 = 1.
```

This is the complex version of the scaling step in CPR Lemma 11; it uses
the same nonnegative scaling theorem on squared moduli. The scalings may
be real rather than rational, which is harmless for a complex-rank bound.

**Overlap and trace.** Write `A=B B*`, which is positive semidefinite and
has `tr(A)=n`. The supports of two distinct rows `i,j` of `B` have at most
three common columns: possibly `i` and `j`, and at most one common graph
neighbor. Cauchy--Schwarz therefore gives

```
|A_ij|^2 <= 3 * sum_t |B_it|^2 |B_jt|^2,    i!=j.
```

Put `S4=sum_it |B_it|^4>0`. The doubly stochastic identities yield

```
tr(A^2) = sum_ij |A_ij|^2
        <= n + 3*sum_t[(sum_i |B_it|^2)^2 - sum_i |B_it|^4]
         = 4n - 3S4 < 4n.
```

The spectral Cauchy--Schwarz inequality for the positive semidefinite `A`
gives `rank(A) >= tr(A)^2/tr(A^2) > n/4`. Also `rank(A)=rank(B)`.
Applying this bound to every total-support diagonal block proves the lemma.

A conservative alternative, requiring only the published real rank bound,
already suffices below: normalize the diagonal of a complex fitting matrix
to one and take its real part. This remains a real fitting matrix and has
real rank at most twice the original complex rank. Thus CPR's bound implies
`rank_C(M)>n/12`, without using the stronger overlap calculation.

## 3. Turning query rank into native cost

Fix the scalar decoder contract: a fitting matrix is a sum of outer
products `M=sum_l u_l v_l^T` over `Q(i)` (or `C`). Its diagonal is one and
its other forced entries vanish; free entries are exactly the graph edges
above. Each term is one scalar total carried by one native array. Its tariff
is the binary pairing rank between the complete sums of source port spaces
and reader port spaces in that term's supports.

Each support span is an `F`-linear subspace of `F^3`. For any two such spans
`U,T`,

```
rank_F2(Tr B restricted to U x T) = k * rank_F(B restricted to U x T).
```

Indeed the trace-annihilator of `T` in `U` is exactly its `B`-annihilator:
if `B(u,t)` is nonzero for some `t`, varying `t` through its scalar
multiples makes `Tr B(u,t)` nonzero somewhere, by nondegeneracy of the
finite-field trace pairing. Both kernels are the same `F`-subspace, so
converting dimensions to binary dimensions multiplies rank by `k`.
Every nonzero tariff is consequently at least `k`.

If a term has tariff zero, every source line in its support is orthogonal
to every reader line in its support. Such a term has entries only in free
positions and has zero diagonal, since each `E_a` is nondegenerate. Remove
all zero-tariff terms. The remaining sum is still a fitting matrix.
With `L` paid scalar terms its rank is at most `L`, so Section 2 gives

```
L > V/4,         total copy rank C >= kL > Vk/4.
```

This argument allows arbitrary cancellations among paid terms and arbitrary
complex scalar weights. It does not sum separate per-plane decoder floors.
Its limit is the explicitly stated scalar-total and complete-support tariff.

## 4. The strict target gate

For the candidate three-stage compressed window, `h=3k`, `m=7k` and
`W=2V`. Keeping its separate public data legs forces `6V` rank-`2k`
children, giving normalized data moment

```
D = 3*(2/7)^(8/9) = 0.985156473147628... .
```

There are three invocations of the paid decoder. Each of its `L>V/4`
terms costs at least one rank-`k` child. Since `x^(8/9)` is increasing,

```
M(1/9) >= D + (3L/(2V))*(1/7)^(8/9)
        > D + (3/8)*(1/7)^(8/9)
         = 1.051658213344872... > 1.
```

The conclusion does not need a maximum copy rank. If a descent is split
into smaller children with the same or greater total rank, concavity only
increases its moment. It does require separate scalar-query lifetimes;
a new fused primitive serving several independent totals changes that
contract and needs its own invoice.

The mass-only relaxation also fails: granting every copy-rank unit the
maximum local rank `h` gives

```
M(1/9) > D + (1/8)*(3/7)^(8/9)
         = 1.044016375488343... > 1.
```

Even the conservative published-real-theorem route `L>V/12` gives a
count-based lower bound `1.007323719880043...` and a mass-only bound
`1.004776440594533...`, both above one. These checks show that closing the
candidate does not depend on the improvement from twelve to four.

Under the retained strict outer transfer, κ = 0.1 needs primitive saving
strictly above `1/9`. Failure already at that boundary is decisive for the
stated scalar-decoder family. All other helper, tape, precision, phase,
frame, routing and restoration costs were granted free in these bounds.

## Replay and controls

```
python3 -I -B research/kappa01-fieldline-repair/verify.py
```

`RESULT.json` contains outward rational gate intervals. The verifier checks
exact Gaussian-rational matrix fixtures for the overlap/trace bound,
including nonsymmetric phases, the rank-one triangle attainer, and a K4
control which violates the C4-free hypothesis and defeats the claimed
bound. It checks a reducible support block, exclusive receipt output, and
the contrast between the passing data-only relaxation and each failing
fully charged lower bound. These finite controls corroborate the formulas;
the all-size result rests on the proof and the cited total-support scaling
theorem, not exhaustive fitting-matrix enumeration.

External references and hashes of the source PDF inspected in this session
are in `SOURCES.json`. The original PDF's text encoding was unreadable, so
the relevant pages were rendered and visually inspected. No paper or
production supplier is altered. No selected result is changed, and no new
κ or complete supplier is claimed.

## Sources, attribution and next question

- Codenotti, Pudlak and Resta, revised ECCC TR97-043 (1998), Section 4:
  <https://eccc.weizmann.ac.il/report/1997/043/revision/1/download>.
- Haviv, *On Minrank and Forbidden Subgraphs* (2018), Section 1.2:
  <https://drops.dagstuhl.de/storage/00lipics/lipics-vol116-approx-random2018/LIPIcs.APPROX-RANDOM.2018.42/LIPIcs.APPROX-RANDOM.2018.42.pdf>.
- Sinkhorn and Knopp, *Concerning nonnegative matrices and doubly stochastic
  matrices*, Pacific Journal of Mathematics 21 (1967), 343--348:
  <https://msp.org/pjm/1967/21-2/pjm-v21-n2-p14-p.pdf>.
- The geometric construction and finite trace/coclique checks are in
  [the local field repair](../kappa01-repair/field_geometry.py); the related
  compressed-window pressure accounting is credited in
  [the bit repair analysis](../kappa01-bit-repair/PROOF.md).

The remaining repair question is precise: can an operator-valued decoder or
a genuinely joint native consumer break the scalar-query rank tariff while
preserving arbitrary payloads, all dirty inputs and the complete endpoint?
The scalar fitting-matrix family analyzed here cannot supply the target.

Prepared with substantial OpenAI Codex assistance and a separate AI review
of the core argument. No independent human or formal-kernel verification is
claimed. New material is Apache-2.0; external sources retain their rights.
