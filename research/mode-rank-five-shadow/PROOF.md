# One rank-five flat has a filled three-dimensional mode shadow

The proof and finite certificate were produced by Nick Petalas. New work is
Apache-2.0. This is an exact finite result for one fixed mode matrix.
Independent human and formal proof-kernel review are unclaimed.

## Statement

Let the rows of the 112-by-8 integer mode matrix in Dillon Amburgey's
`research/coded-native-caller/NORMALIZERS.json` be `m_0,...,m_111`, indexed
from zero. Put `L = span_Z {m_i}` and `Z = sum_i [0,1] m_i`.
Let `F = span_R {m_0,...,m_4}`. These five rows are

```text
1 1 1 1 0 0 0 0
1 1 0 0 1 1 0 0
1 0 1 0 1 0 1 0
1 0 0 1 0 1 1 0
1 0 0 1 1 0 0 1
```

Define the rational quotient map `pi(x) = B x / 2`, with

```text
B = [-2 0 1  1  1 1 0 0]
    [-2 1 0  1  1 0 1 0]
    [ 1 0 0 -1 -1 0 0 1].
```

**Finite theorem.** `ker(pi) = F`, `pi(L) = Z^3`, and

```text
pi(Z) intersect Z^3 = { sum_i epsilon_i pi(m_i) : epsilon_i in {0,1} }.
```

The left-hand side has exactly **103,333** points. Exactly **94,599** are
strictly interior, and **8,734** are on the boundary. Thus this particular
three-dimensional shadow has no lattice hole, even on its boundary.

## Quotient and row flat

Exact rational row reduction gives rank five for the five displayed rows
and rank three for B. Each displayed row is annihilated by B, so F is exactly
the kernel. Of the 112 rows, exactly 15 are annihilated. Their rank is five.
They form the closed row flat with span F. A generic functional in F's
three-dimensional annihilator exposes a face parallel to F, so this is a
shadow along a codimension-three face in the sense of apoursh's #6829.

The verifier computes every `B m_i`, checks divisibility by two, and sets
`q_i = pi(m_i)`. Some q_i are the signed coordinate unit vectors. Hence
`span_Z {q_i} = Z^3`, without any lattice saturation or index assumption.

For enumeration, replace each q_i whose first nonzero coordinate is negative
by `p_i = -q_i`; leave the others unchanged. Let t be the sum of the q_i
that were replaced. Then both the zonotope and its subset sums translate
by the same integer vector:

```text
sum_i [0,1] q_i = t + sum_i [0,1] p_i,
{sum_i epsilon_i q_i} = t + {sum_i epsilon_i p_i}.
```

Consequently filling can be checked for the p_i. This reorientation leaves
15 zero generators. The 14 distinct nonzero generators and multiplicities
are emitted in the computed receipt. The exact coordinate bounding box is

```text
[0,86] x [-1,85] x [-49,5],
```

which contains 416,295 integer points.

## Complete finite certificate

The verifier uses two different representations of subset sums. First,
encode a point in that box as

```text
index(x,y,z) = x + 87(y+1) + 87^2(z+49).
```

Starting with the bit for the origin, update `S <- S union (S+p_i)` for
each of the 112 generators. A signed integer bit shift implements this
update. At every prefix, each genuine subset sum lies in the global box,
because the sum of coordinatewise negative contributions is a lower bound
and the sum of positive contributions is an upper bound. Thus no encoded
shift crosses a coordinate boundary, wraps, or discards a genuine point.
The final set has 103,333 bits. A separate tuple-set recurrence computes
all subset sums and agrees with every bit, without integer encoding.

The closed three-dimensional zonotope has a complete facet description
obtained as follows. For each pair of distinct generator directions, take
their cross product. Discard zero products, divide by the gcd, and identify
opposite normals. There are exactly 25 resulting normal pairs. For each
primitive normal n, the exact support inequalities are

```text
sum_i min(0,n.p_i) <= n.x <= sum_i max(0,n.p_i).
```

These inequalities define the zonotope. Indeed, each facet's parallel
generators span a two-dimensional plane, so two independent generators
produce its normal in the cross-product list. Conversely every listed
inequality is valid. A bounded full-dimensional polytope is the
intersection of its facet half-spaces. No floating-point hull computation
or predecessor facet census is used here.

For each of the 87-by-55 possible pairs `(y,z)`, intersect these 25
inequalities to obtain the exact integer x interval. The closed intervals
contain 103,333 points, each present in the subset bitset. Replacing each
primitive integral support inequality by its strict version gives 94,599
interior points, also all present. A separate pointwise scan tests all
416,295 points against all 25 inequalities and compares every closed
membership decision with the tuple set. It independently reproduces both
counts. Their difference is the boundary count.

The receipt is computed at execution time and binds the six package files
and the subset bitset by SHA256. It is not a handwritten or committed log.

## Controls and implementation bounds

Removing one actually reached interior point creates exactly one detected
hole in both the closed and interior scans. A small full-rank integer
zonotope with generators `(1,-3,0),(1,-2,0),(1,0,0),(0,0,1),(0,0,1)` has
holes; the verifier checks their exact counts rather than assuming every
zonotope fills. An independent tuple encoding of that example checks signed
shifts. These are five explicit control predicates, counted in the receipt.

The verifier is nonrecursive and read-only. The source boundary checks eight
columns, 112 rows, entries in {-1,0,1}, and its pinned SHA256. Geometry accepts
at most 112 three-coordinate generators, coordinates bounded by eight, and
a box of at most 500,000 points. Every enumeration is bounded by these
finite dimensions. No function exceeds 60 physical lines.

Power-of-ten rule 3 deviation applies to Python integers, Fractions, JSON,
sets and tuples: CPython allocates managed objects during the calculation.
The scope is this finite verifier. The enforced box capacity bounds each
reachable set by 500,000 tuples; at most the existing and one shifted set
are live during an update. The bitset has at most 500,000 bits. File inputs
are pinned and bounded. Both normal and optimized warning-strict replay
exercise the same checks, which use explicit exceptions rather than Python
assertions. Follow-up if the input family grows is to retain explicit
capacity bounds or switch the tuple cross-check to fixed packed storage.
Separate compiler/type analysis is not supplied for this standard-library
Python research script.

## Scope and predecessors

Armin Pourshafeie / apoursh's #6829 poses the codimension-three question
and proves filling of every facet and ridge shadow. Those results are cited,
not rechecked. The new calculation begins in a different quotient and proves
the displayed one-flat statement only. Dillon Amburgey's #4933 supplies M.
Nick Petalas's #6312 defines the exact-mode rounding radius, and apoursh's
#6320 reduces radius one to full eight-dimensional lattice filling; #6333
gives the retained upper bound three halves. Cross products, zonotope support
functions, exact elimination and subset-sum dynamic programming are classical.

This does not classify rank-five flats, prove filling for every
three-dimensional shadow, or settle full eight-dimensional filling or R=1.
No physical rounder, compiler, precision, tape, ownership, stock, supplier
admission, new kappa, selected-frontier change or complete multiplication
theorem follows. All five selected framework assumptions remain.

## Open next questions

- Classify rank-five row flats up to the mode matrix's signed code symmetries.
  Begin by mapping the 15-row flat above into that catalogue. A complete
  orbit inventory is not supplied here.
- Test a different rank-five-flat orbit with the same lattice-index and
  full-membership checks. Larger quotient boxes may need a different exact
  representation. Filling every such shadow would still leave higher
  codimensions and full R=1 open.
