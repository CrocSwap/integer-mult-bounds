# Pairing rank for the shipped P111 label decoder

This is a finite algebraic theorem about a fixed decoder and fixed rational
geometry. Its connection to physical copy accounting is conditional as stated
below. It makes no new kappa claim.

## Definitions and finite premises

Let `L[0],...,L[119]` be the Hamming-coordinate E8 root lines in the order used
by #493 and the #545 shipped word. Each has squared norm 4. Put

```text
P = [39,52,57,71,76,78,103,109,114],
S = {0,...,119} minus P,
G[i,j] = <L[i],L[j]>/2,
B[i,j] = (1 + G[i,j]) mod 2,
C = B[P,P],  M = C^(-1),  W = B[S,P].
```

All binary matrices in this note are over F2. Ranks of root spans and pairings
are over Q. The exact checker verifies that `C` is invertible, `rank(W)=9`,
and the restricted decoder is `B[S,S] = W M W^T`.

For a nonzero binary column `x` of length nine, define

```text
R(x) = {i in S : (W x)[i] = 1},
E(x) = span_Q {L[i] : i in R(x)},
beta(x,y) = rank_Q of the dot-product pairing E(x) x E(y).
```

We consider arbitrary finite decompositions

```text
M = sum_j x_j y_j^T,    x_j != 0, y_j != 0,
cost = sum_j beta(x_j,y_j).
```

Equivalently, these decompose `B[S,S]` into scalar totals whose individual
source and reader columns lie in `im(W)`. The full column rank of W makes the
equivalence exact. Repeated terms and cancellations are allowed. Zero terms
can be removed without changing the matrix or cost.

The 511-support census proves these finite premises by rational elimination:

1. `E(e_a) = L[P[a]]^perp`, of dimension seven, for all nine coordinate vectors.
2. Every other nonzero `x` has `E(x) = Q^8`.

Consequently the complete term-cost table is

```text
6  if x=e_a, y=e_b, a!=b, and <L[P[a]],L[P[b]]>=0;
7  if at least one factor is a coordinate vector, except the preceding case;
8  otherwise.
```

For two hyperplanes, the pairing has a one-dimensional kernel exactly when
their normals are orthogonal. A full Q^8 span pairs nondegenerately with the
other span. This proves the table from the two premises; the checker also
recomputes all 81 hyperplane-pair ranks directly. There are 36 cost-six,
9,081 cost-seven and 252,004 cost-eight ordered pairs.

The small matrices needed below are recorded as binary-packed rows, with
bit `j` representing column `j` and all indices zero-based:

```text
C = [17,314,284,462,471,418,472,248,382]
M = [380,422,147,25,381,307,401,326,499]
```

Every diagonal entry of C is one. The five diagonal ones of M are at positions
`{1,3,4,5,8}`. Its principal block at positions `{3,5}` is `I_2`, while
`C[3,5]=C[5,3]=0`. Thus every cost-six matrix unit vanishes throughout that
2-by-2 block. These facts are checked from the generated geometry, not assumed
as arbitrary input constants.

## Theorem

The minimum of `sum_j beta(x_j,y_j)` over the decompositions above is **63**.

### Nine terms: each discount needs an expensive term

More generally, let C be an invertible 9-by-9 binary matrix with unit diagonal.
Suppose `C^(-1) = X Y^T` has exactly nine nonzero rank-one terms. Both X and Y
are invertible, and

```text
Y^T C X = I_9.
```

Let A be the set of coordinate indices occurring as unit columns of X, and D
the corresponding set for Y. Unit columns cannot repeat within a basis. If
`a` belongs to both A and D, let column `i` of X and column `j` of Y both be
`e_a`. Their pairing is `C[a,a]=1`, so duality forces `i=j`. Conversely, a term
`e_a e_a^T` gives such an intersection.

Write `d` for the number of terms with two different unit factors, `s` for
the number with two equal unit factors, `t` for the number with exactly one
unit factor, and `u` for the number with neither factor a unit. Then

```text
9 = d+s+t+u,
|A union D| = (2d+2s+t)-s = 9+d-u <= 9,
```

so `d <= u`. Every cost-six term is among the d terms; every cost-eight term
is among the u terms, and all u terms cost eight. If their counts are `n6`
and `n8`, respectively, `n6 <= d <= u = n8`. Hence

```text
cost = 7*9 - n6 + n8 >= 63.
```

This is a counting proof for every nine-term factorization, not an enumeration
of bases. It uses no symmetry assumption on X or Y.

### Ten terms: diagonal support or a rank-two obstruction

For ten terms, write `n6+n7+n8=10`. Cost at most 62 requires

```text
cost = 60+n7+2*n8 <= 62.
```

If `n8=0`, there are at most two cost-seven terms. Cost-six terms are
off-diagonal matrix units and contribute nothing to the diagonal. A
cost-seven term has a unit factor, so its diagonal is supported at at most
one coordinate. Two such terms cannot produce the five diagonal ones of M.

If `n8=1`, the budget forces `n7=0` and `n6=9`. Every cost-six term vanishes
on the principal block `{3,5}`. The single remaining rank-one term would
therefore have to equal `I_2` on that block, which is impossible by rank.

If `n8>=2`, cost is already at least 64. This exhausts the ten-term case.

### All other term counts and attainment

Fewer than nine rank-one terms cannot sum to the rank-nine matrix M. Eleven
or more nonzero terms cost at least `6*11=66`. Together with the preceding
arguments, this proves the lower bound for every finite term count.

For the upper bound, use the nine column terms

```text
x_j = column j of M,   y_j = e_j.
```

Their sum is M. Every column of M has more than one nonzero entry, so each
term costs seven. The verifier checks all nine terms and their sum. This is
an attaining algebraic star decoder at cost 63; the existing #545/#555
supplier is credited separately and is not replayed here.

## Source numbering

The order in `research/format-limits/scripts/e8units.py::hamming_e8` differs
from the order in `research/e8-bit-carrier-skeleton/code/skeleton/e8.py`.
Both generate the same set of 120 root lines. Expressed in the former's
sorted-tetrad order, the shipped punctures are

```text
[111,52,9,119,76,78,31,37,66].
```

Reusing `[39,52,57,71,76,78,103,109,114]` without this conversion instead
selects a different set, with 44 rather than 36 ordered orthogonal pairs.
The 44 count matches #620's report. Its `geo.py` imports an external
`e8units` module; that local runtime module is not shipped in its directory,
so this note does not assert which exact module bytes ran in the author's
environment. Numerical indices or the report's count alone do not certify a
binding to the shipped supplier. The present check regenerates the supplier's
order and compares every live coordinate directly to the pinned word.

This distinction does not invalidate #620's reported SAT result for its
tested instance. The contribution here is a solver-free proof bound to the
actual shipped geometry, including an explicit rejection of the other order.

## Physical interpretation and limits

The finite optimization theorem above is self-contained given its explicitly
checked geometry. Interpreting beta as a lower bound on paid physical copy
rank additionally uses [#446, Theorem C, section 4](https://github.com/CrocSwap/integer-mult-bounds/blob/309482849b6ddf34db998f53612d34c19f6e3233/research/format-obstructions/PROOF.md):
each scalar total is gathered drop-free, propagated through its copy tree,
and read inside the relevant orthogonal frames. Summing the per-total bounds
requires the additive charging of these trees. That premise is not proved by
this finite checker and does not cover an unpriced shared multi-total primitive.

Under this accounting, even granting free source access, helpers, frame
preparation, restoration and other recursive work cannot lower the copy
charge below the existing 63. Adding those nonnegative expenses cannot make
this particular copy-saving mechanism help. The inherited deficit expression
for this unit therefore remains bounded by

```text
D/T <= (s-1)*111 - s*63 = 48*s - 111.
```

This excludes a cheaper copy charge in the specified factorization class,
not improvements to helper work or a universal bound on multiplication.
Different fitting decoder matrices, factors outside `im(W)`, other punctures,
vector-valued totals, different geometry or different accounting remain open.
No uniqueness claim about arbitrary fitting matrices is inferred from #620's
SAT runs. The selected frontier and all inherited asymptotic compiler,
realization, hosting, precision and analytic assumptions remain unchanged.

The finite premise census and mutation controls are reproducible evidence,
not a machine-formal proof of this argument or of the multiplication theorem.
