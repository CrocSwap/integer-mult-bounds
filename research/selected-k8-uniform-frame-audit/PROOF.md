# Uniform power-cost optimality and rigidity of the optimal paid profile

This is a source-bound extension of Gareth Davidson / bitplane's
[PR1671](https://github.com/CrocSwap/integer-mult-bounds/pull/1671), at
`ce130d291f5ab6dd801544886a16f62d42d86118`. Its symbolic duals are retained
unchanged. Its event/domain construction and the implication from an admissible
physical frame assignment to an LP point remain inherited premises. The new
result is a uniform sign proof and an equality-case consequence, not a new
derivation of the physical interface.

## Statement

Fix the PR1671 R480 k8 word, scalar chronology and coefficients, register
endpoints, A/B pins, centre cut, early-cleanup membership/order and low-end
cone restrictions. Permit every frame in the complete monotone subspace
intervals of its relaxed model. Each dimension-d climb pays one rank-d child;
the eight rank-eight centre children are fixed. Let

    P = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}.

For every real `0 <= a <= 1/32`, P minimizes

    sum_r H_r r^(1-a)

over this frame model, and attains the minimum of its local-polytope LP.
For `0 < a <= 1/32`, **every optimizing assignment has exactly histogram P**.
The same histogram statement holds for the expected child counts of every
optimal fractional LP point. It does not say the frame assignment is unique.
At a=0 every feasible point has the same rank mass, so histogram uniqueness
is not asserted.

Dividing the objective by any common positive width/normalization factor
does not change the comparison. In particular this covers the physical
power price `(r/73)^(1-a)` and the planning point `a=1/99`.

## 1. Exact finite objects and the inherited relaxation

The decompressed word is SHA256
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.
It is bound to the selected word by SLOT-PINS-k8. The event graph has 5,413
gate nodes, of which 1,741 have free frames, in 135 components. The domains
have quotient dimensions 1, 2 or 3, with respectively 2, 5 or 16 subspaces.
Distinctness, containment and the complete subspace counts are checked.
The four graph/domain/cone hashes agree with PR1671.

The inherited LP uses nonnegative gate distributions x and nested adjacent
frame-pair distributions y. Gate distributions normalize to one and both
edge marginals agree with x. Thus every literal feasible assignment is a
zero/one LP point. Edges between fixed/forced nodes and the eight centre
children are included separately.

Every climb's dimension is the difference of its endpoint dimensions.
Along each register these telescope, including in a fractional point because
the edge marginals agree. The endpoint sum plus centres is always 5,586.
This is checked independently from the stated histogram's rank mass.

Put `C_d(a)=d^(1-a)-d`, for d=2,...,9, and C_0=C_1=0. Subtracting the
fixed rank mass from the objective preserves all comparisons. These charges
are PR1671's charges divided by the common positive factor `73^a`, so its
symbolic rational dual coefficients apply unchanged.

For each component, reconstruct `min c.z`, `Az=b`, `z>=0`. The retained dual
q is a vector of rational linear forms in C_2,...,C_9. The checker establishes:

1. All 17,507 rows and 23,004 columns are present.
2. Every dual row is a row of this LP.
3. `b^t q` equals the baseline's reduced histogram as an exact coefficient
   identity, separately in every component.
4. The reduced coefficient vector of every column is `v=c-A^t q`.
5. Fixed plus variable baseline costs reconstruct every entry of P.

A second column assembly starts directly from the event edges and domains.
For gate columns it uses `unary - q_N + sum q_M`; for pair columns it uses
`pair_cost - q_M0 - q_M1`. It independently accounts for edge multiplicity,
nested pairs and ranks, then agrees with the first assembly on every column.
Both assemblies share the pinned event/domain model. This is deliberately
not called an independent physical-interface implementation.

There are 239 distinct reduced vectors. Their multiplicities, exact rational
coordinates, complete column-stream digest and sign proofs are in RESULT.json.

## 2. Uniform reduced-cost signs

For a reduced vector v define

    R_v(a) = sum_(d=2)^9 v_d d (exp(-a log d)-1).

The original reduced cost is the positive multiple `73^a R_v(a)`.

There are three cases:

| Columns | Distinct vectors | Proof |
|---:|---:|---|
| 16,564 | 1 | v=0, identically zero |
| 10 | 1 | v=(-4,0,1,0,0,0,0,0), so R_v(a)=4(1-2^(-a))^2 |
| 6,430 | 237 | Positive rational Bernstein bound for R_v(a)/a |

The square is strictly positive for a>0. It needs its own argument: its
derivative at zero vanishes, and interval cancellation at zero would not
establish strict positivity on an interval beginning at zero.

For the remaining vectors write l_d=log d and use the alternating series
for exp(-a l_d). On the entire interval, `0 <= a l_d < 1`; this domain is
checked with a rational upper bound on log 9. An odd truncation after k=9
is a lower bound on the exponential, and the even truncation after k=8
is an upper bound. For v_d>0 use the former, for v_d<0 the latter. After
subtracting the constant term and dividing by a>0, this gives a polynomial
lower bound of degree at most eight on R_v(a)/a.

The logarithms have independently calculated rational enclosures. Write
`d=2^k u`, `1<=u<2`, and use

    log d = k log 2 + 2 atanh((u-1)/(u+1)),
    log 2 = 2 atanh(1/3).

After j terms, the remaining atanh series is bounded by

    z^(2j+1) / ((2j+1)(1-z^2)).

The code sums until that bound is less than 2^-144 and rounds the final
log bounds outward to multiples of 2^-128. For each signed coefficient of
the polynomial, use the lower or upper log-power endpoint according to
its sign. Since a>=0, lowering every power-basis coefficient preserves the
polynomial lower bound. No floating-point value is an acceptance input.

Let the resulting polynomial be `p(a)=sum_(i=0)^8 c_i a^i` and A=1/32.
Its Bernstein coefficients on [0,A] are exactly

    b_j = sum_(i=0)^j c_i A^i binom(j,i)/binom(8,i).

The Bernstein basis functions `binom(8,j)t^j(1-t)^(8-j)`, t=a/A, are
nonnegative and sum to one. Therefore p(a)>=min_j b_j. All 237 vectors
have strictly positive rational coefficients. The smallest checked bound,
rounded down to a 2^-96 grid, is

    1418585426042207139080866245 / 79228162514264337593543950336
    > 0.0179.

Consequently all 6,440 nonzero reduced-vector columns have strictly positive
cost for `0<a<=1/32`. At a=0 every C_d vanishes. Weak duality plus the exact
objective identities proves the stated uniform optimum.

## 3. Why every optimal paid histogram is the same

Fix any a in the positive interval. For a feasible LP point z, its objective
gap from the baseline is the sum of z_j times the reduced cost of column j.
Every summand is nonnegative, and every column whose **coefficient vector**
is nonzero has strictly positive cost. Equality therefore forces z_j=0
on every such column.

On the remaining columns the residual coefficient vector is identically
zero. Hence the vector equation, not merely its evaluation at this a, is

    sum_j z_j c_j = b^t q.

All expected rank-2 through rank-9 counts equal the baseline component
counts. Restoring the fixed contributions gives P at those ranks. The
invariant rank mass 5,586 then forces the rank-1 count to be 2,412.

The conclusion does not require linear independence of the evaluated real
numbers C_d(a), nor uniqueness of the dual or primal LP point. It follows
from the strict signs and exact vector identities.

As a positive boundary fixture, changing the frame of gate G616 from the
zero subspace to span(148), leaving all other frames unchanged, satisfies
the modeled nesting constraints and has exactly histogram P. The full
graph price is recomputed. This is a second feasible **model assignment**;
no separate native/physical admission of the alteration is claimed.

## 4. Limits of the same certificate

Two exact negative controls prevent overstatement:

- For the nondecreasing concave price f(r)=min(r,2), the actual G4277 gate
  column with vector `(-3,1,0,0,0,0,0,0)` has reduced cost -1. The published
  dual therefore does not certify every concave price.
- At a=1/20, an actual G1669/G1670 pair column with vector
  `(0,8,1,-4,0,0,0,0)` has negative reduced cost. Rational 20th-root bounds
  certify its interval in RESULT.json (approximately -0.004265).

These refute extensions of this **particular dual certificate**, not the
optimality of P outside [0,1/32]. No cheaper feasible assignment is supplied
by a negative reduced cost alone. Neither control contradicts PR1671's
two-exponent theorem. The uniform interval is certified, not claimed maximal.

## 5. Relation to the full supplier

The local invariant still leaves 1,646 ideal idle rank units per call under
the inherited `72*(896/9)+64=7232` coverage law. PR1671/PR1240 already prove
the fixed-word packing ceiling `a<0.001690054109089` and its conditional
balanced kappa cap. This package does not improve that cap or repeat its
complete moment arithmetic. Its added information is uniform local
optimality and the impossibility of a different *equally optimal* rank shape
in the positive interval.

Scalar rewrites/reordering, changed endpoints, helper inventories, centre
sharing, different coverage laws and changed physical billing remain outside
scope. The source word, cone contract and finite-domain completeness proof
are inherited; cold supplier replay, native execution, hosting, all-size
compiler, common-label/mutable-source realization, precision/tape, analytic
transfer, bit H1-H5, Lean and human review are not established here.

New proof/checker: Ross Richardson with substantial OpenAI Codex assistance.
Credit Gareth Davidson/bitplane for the unchanged duals and selected-word
LP; Aaron Wang/navinor for the retained model and method; and the source
lineage in NOTICE.md. Apache-2.0.
