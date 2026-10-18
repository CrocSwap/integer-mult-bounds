# Rank-two binary planes in dimension six

**No nonempty subset of the 336 distinct nondegenerate planes in binary
dimension six passes the three-stage κ = 0.1 target in the scalar
full-support query model below.** This statement is checked for both the
standard dot form and the explicit alternating form `H direct-sum H
direct-sum H`, where `H=[[0,1],[1,0]]`.

This extends the field-line rejection to intersecting binary planes, which
can have several common orthogonal neighbors. It does not cover repeated
ports, arbitrary two-sided block representations, matrix-valued queries,
fused public legs, or a different permission mask. No classification of
binary bilinear forms is needed: the two forms are explicitly reconstructed.

## The exact finite masks

For either displayed form, enumerate every two-dimensional subspace as its
three nonzero vectors `{a,b,a+b}`. Keep it exactly when its two-by-two Gram
determinant is one. This gives 336 planes. Two ports are adjacent precisely
when their complete subspaces are orthogonal.

Each graph is 20-regular, with 3,360 edges. Include the diagonal in each
row support by writing `S_i={i} union N(i)`. The exact unordered-pair census
is the same for the two forms:

| Size of `S_i intersect S_j` | Number of pairs |
|---:|---:|
| 0 | 15,120 |
| 1 | 30,240 |
| 3 | 3,360 |
| 4 | 7,560 |

Every adjacent pair has overlap three; every nonadjacent pair has overlap
zero, one, or four. In particular, **distinct closed row supports overlap
in at most four places**. Passing to an induced subgraph can only reduce
these overlaps.

The geometry explains this small number. Distinct planes span dimension
at least three, so their common orthogonal complement has dimension at
most three. A three-dimensional binary space with the restricted symmetric
form has at most four nondegenerate planes: a form of rank at most one has
none; a form of rank two has a one-dimensional radical and exactly four
complementary planes; for rank three, the form is nonalternating and its
four vectors with nonzero self-pairing give the four nondegenerate planes
by taking perpendicular complements. For an adjacent pair, the sum
is a nondegenerate four-dimensional space, whose perpendicular complement
is one nondegenerate plane; the two diagonal positions add two more
overlaps. The finite census directly verifies the needed bound, so the
exclusion does not depend on a classification proof for these restrictions.

## The bounded-overlap fitting-rank lemma

Suppose a simple undirected graph has closed row-support intersections of
size at most `mu>=1` for distinct vertices. Every complex fitting matrix `M`
with nonzero diagonal and off-diagonal support contained in its edges has

```
rank_C(M) > V/(mu+1).
```

This is the matrix-scaling proof in [the field-line audit](README.md),
with its overlap constant three replaced by `mu`. In detail, decompose the
directed nonzero support into strongly connected components. Each diagonal
block has total support, since every internal edge belongs to a directed
cycle and the remaining diagonal entries complete a permutation. The full
rank is at least the sum of the block ranks.

For a block of size `v`, apply the Sinkhorn–Knopp total-support theorem to
the squared moduli, then square-root its positive scalings. This produces
a same-rank matrix `B` whose rows and columns have squared norm one. For
`A=B B*`, the overlap bound and Cauchy–Schwarz give

```
tr(A)=v,
tr(A^2) <= v + mu*(v-sum_ij |B_ij|^4) < (mu+1)*v.
```

Spectral Cauchy–Schwarz yields `rank(A)>=v^2/tr(A^2)>v/(mu+1)`.
Summing the block bounds proves the assertion, including asymmetric and
arbitrary complex fitting coefficients. The primary scaling theorem and
the source of this rank method are cited and pinned in the parent package;
this is a specialization of the same proof, not a new optimality claim.

For the exact masks here, `mu=4`, hence every induced fitting has rank
strictly greater than `V/5`.

## The scalar-query invoice and target gate

Require the scalar fitting decoder to have diagonal one and permit
off-diagonal entries only at full-orthogonality edges. Express it as
`M=sum_l f_l*g_l^T`. Price each query separately by the binary pairing rank
between the complete sums of reader and source port spaces in its supports.

A zero-tariff term has entries only at free positions and no diagonal,
because each port is nondegenerate. Deleting all such terms preserves the
fitting conditions. If `L` positive-tariff terms remain, rank subadditivity
and the preceding lemma imply `L>V/5`. Each tariff is a positive integer,
so its lower bound is **one**, not the port rank two.

For `h=6,k=2`, the three-stage window has `m=14`, `W=2V`, and `6V` separate
public children of rank four. Its ideal data-only moment is
`3*(2/7)^(8/9)<1`. With three decoder invocations, even granting every
positive query rank one and every other expense free gives

```
M(1/9) > 3*(2/7)^(8/9) + (3/10)*(1/14)^(8/9)
        = 1.013886814008956200... > 1.
```

Splitting a query's tariff into smaller children with the same total rank
cannot reduce this moment, by concavity. Combining independent queries or
public climbs into a new primitive changes the model. The conclusion is
only for the separate-query and separate-public-leg contract just stated.

Under the additional compressed-window coverage hypotheses of
[the bit target proof](../kappa01-bit-repair/PROOF.md), every odd stage count
at least five already fails at `h/k=3` using the data alone. Together, these
results exclude every allowed odd stage in that same model. Failure at
`a=1/9` suffices, since strict κ = 0.1 outer transfer needs `a>1/9`.

## Replay

```sh
python3 -I -O -B research/kappa01-fieldline-repair/planes6.py
```

`PLANES6-RESULT.json` retains both exact plane lists, adjacency masks,
intersection histograms, source pins, and rational target enclosures.
The verifier checks an attaining four-column overlap and rejects applying
the lemma with `mu=4` to `K5`, whose all-ones fitting has rank one. Exact
Gaussian-rational fixtures include asymmetric phases. No numerical spectral
calculation, optimizer, or minimum-rank enumeration is used for acceptance.
