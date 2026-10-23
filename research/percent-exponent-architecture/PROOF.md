# Cost barriers for a saving of 1/100

This note gives necessary conditions for specified finite interfaces. It does
not prove a new multiplication bound. In particular, it does not rule out
`kappa = 0.01` for a different architecture.

## 1. A paid-moment inequality

Let an ordinary finite supplier have ambient width `m`, stock `W`, and `n_r`
children of width `0 < r < m`. Put

```
D = m W - sum_r n_r r,
C = sum_r n_r r log(m/r).
```

Acceptance at a positive saving `a` requires

```
sum_r n_r r (m/r)^a < m W.
```

Since `exp(x) >= 1+x`, necessarily `a C < D`. For any retained submultiset
of children, `C_keep <= C`, so `a < D/C_keep`. Dropping all other entropy
costs is a favorable relaxation, not an implementation. Positive wrappers,
fallbacks and scalar tolls cannot improve this upper bound when they leave
this moment and its deficit budget intact.

The elementary entropy bound was also used in DaysSky's PR #192. The use
here is different: discard the entire auxiliary circuit and bound the data
interface itself. The balanced assembly has `kappa < a/(1+a) < a` for its
limiting ordinary supplier (cf. PR #183). We use the weaker `kappa < a` for
the displayed ceilings. No historical factor-of-five assembly is used.

## 2. The current data itineraries already exclude 0.01

The pinned complex profile is PR #193, whose full commit is recorded
in `inputs/complex-pr193.json`. The bit profile is PR #187, pinned separately
in `inputs/bit-pr187.json`. The input files contain the complete child
histograms and the exact source/target subhistograms, with source-file hashes.
The checker recounts stock, rank, deficit and submultiset inclusion.

In the three-block shared-core interface, `m=3h` and `D=2v-3 ell`.
The data submultiset consists of three copies of the source and target
itineraries and `2v` rank-two complement children. It is:

| Profile | h | v | ell | Data children, width: multiplicity |
| --- | ---: | ---: | ---: | --- |
| Complex #193 | 22 | 1320 | 440 | 1:15840, 2:6600, 18:7920 |
| Bit #187 | 24 | 1760 | 528 | 1:18480, 2:6160, 20:5280, 21:2640, 22:2640 |

These give the following strict upper bounds on `a`, with every auxiliary
entropy cost removed:

| Profile | Retain the copied-center loss | Grant zero center loss, D <= 2v |
| --- | ---: | ---: |
| Complex #193 | 0.004433342 | 0.008866683 |
| Bit #187 | 0.004893592 | 0.008897440 |

At `a=0.01` the data alone require deficit greater than `2.28165 v` and
`2.27179 v`, respectively. Both exceed even the favorable `2v` budget.
The required deficit is computed directly from the exponential uplift, not
by treating the first-order approximation as an equality.

Thus eliminating auxiliary calls or copied-center loss while keeping these
data calls and `D<=2v` cannot reach 0.01. This does not cover a change in
data interfaces, cross-stage fusion, a different deficit identity, or a new
recurrence. A finite-leaf or multitype scheme must be assessed against its
actual recurrence; it cannot be inserted into this theorem by name alone.

## 3. An odd-dimensional paired-cube extension

This is a proposed algebraic family and an optimistic cost screen. We do
not supply its complete framed side circuit, bit companion, prime compiler
or all-size assembly.

Let `d=2t+1 >= 3` and `p>=d+1`. Partition `h=2p` coordinates into pairs.
Each port chooses one coordinate from each of `d` distinct pairs. There are
`v=2^d binom(p,d)` ports. Define the scalar fitting matrix

```
B[T,S] = b_d(|T intersection S|),
b_d(z) = product_(j=1..t) (z-(2j-1))/(d-(2j-1)).
```

Its diagonal is one, and every off-diagonal odd intersection is a root.
Let `B_block` keep only pairs in the same selector cube, and put
`K=I-B_block`, `H=B_block-B`. Then `K+H+B=I`, and both side terms are
supported on binary-orthogonal source/target pairs.

### The local K is an involution in every odd dimension

On a selector cube `F2^d`, let `P` project onto Walsh characters of degree
at most `t`. Exactly half of all characters have that degree, so the
diagonal of `2P` is one. Complementing a character multiplies its value at
a difference `x` by `(-1)^|x|`. At every nonzero even-weight `x`, the sum of
all characters is zero and is twice the low-degree sum. Thus the kernel of
`2P` vanishes there.

Its radial kernel is a polynomial of degree at most `t` in intersection
size. The `t` prescribed roots and its diagonal value identify it uniquely
as `b_d`. Consequently `B_block=2P` and `(I-B_block)^2=I`. Its nonzero
off-diagonal entries join opposite selector parities. Its entries are
dyadic by the Walsh formula, irrespective of how the product polynomial is
written.

Each parity class of addresses spans a binary `d`-space: the pair-difference
vectors with even selector parity have dimension `d-1`, and adding one
odd-norm port adds one dimension. The opposite class is orthogonal to it.
The original-source mixing argument therefore has candidate source chain
`[d-1,h-d-1,1]`. A retained lexicographic target flag has chain
`[h-d-1,1,...,1]` with `d` ones. These are compatible endpoint ingredients,
not a complete global word.

### Copied t-star center budget

The polynomial `b_d(z)` has degree `t`. Write
`b_d(z)=sum_j b_j binom(z,j)`. For a transversal coordinate t-subset `U`,
use the star `Z_U=sum_(S containing U) x_S`. The identity

```
sum_(U subset S, |U|=t) binom(|U intersection T|,j)
  = binom(|S intersection T|,j) binom(d-j,t-j)
```

expresses the whole center matrix through these stars, using scatter
coefficient `sum_j b_j binom(|U intersection T|,j)/binom(d-j,t-j)`.
There are `2^t binom(p,t)` such stars.

The span of the ports in a fixed star has dimension `h-2t`. The fixed
partner coordinates vanish; the fixed selected coordinates have one common
coefficient. Differences of outside ports generate the even-parity space
on the other `2(p-t)` coordinates: flips generate each pair difference, and
exchanging selected pairs generates all even pair occupancies. The strict
inequality `p>d` ensures those exchanges exist. One star port supplies the
remaining dimension. Thus the copied-star interface has

```
ell = 2^t binom(p,t) (h-2t),
D <= 2v-3 ell,       m=3h=6p.
```

The inequality is a hypothesis inherited from this copied-center shared
compiler, allowing additional nonmonotone losses. A construction that
changes this center budget is outside the screen.

### A ceiling even with redesigned local data chains

Put `f(r)=r log(3h/r)`, with `f(0)=0`. It is increasing on `[0,h]`.
A data chain whose endpoints have distance `h-1` has total jump rank at
least `h-1`. If one jump is at least `h-1`, its entropy is already at least
`f(h-1)`. Otherwise concavity gives
`f(r) >= r f(h-1)/(h-1)` for every jump, and summing proves the same bound.
This permits nonmonotone chains, provided every local jump is at most `h`.

Six source/target chains per port and the two complement children therefore
give the circuit-independent floor

```
C_data/v >= 6(h-1) log(3h/(h-1)) + 4 log(3h/2).
```

Together with `D<=2v-3 ell`, every supplier in this stated family satisfies

```
a < 0.008094.
```

The largest relaxed bound in the finite part occurs at `(p,d)=(13,5)` and
is less than `0.008093706`. Keeping the specific destructive-source and
lexicographic target chains instead gives `a<0.005164`, with the largest
relaxation at `(p,d)=(14,5)`.

This is an infinite-family screen, not just a finite parameter scan. For
`p>=30`, `D/v<=2`, and the data lower bound is strictly greater than
`(12p-2) log 3`. The resulting ceiling
`2/((12p-2) log 3)` decreases with p and is already below both finite maxima
at p=30. The checker exhausts all odd `3<=d<p` for `4<=p<30`, and verifies
this tail using rational logarithm enclosures.

## 4. Changing a rank-minimal center basis cannot reduce the triple loss

Here keep the original paired **triples**, with `p>=5`, `h=2p`. Let `A` be
the port-by-coordinate incidence matrix. A nonzero row in its coordinate
star span has values

```
f(S) = sum_(i in S) c_i.
```

For every such characteristic-zero coefficient vector, the binary span of
the ports where `f(S)` is nonzero has dimension at least `h-2`.

First suppose the coefficients differ within one coordinate pair i. For
each outside two-coordinate edge from distinct pairs, at least one of its
two extensions by pair i has nonzero f: their values differ by a fixed
nonzero coefficient difference. The projections of these supported ports
onto the outside coordinates therefore contain all edges of the connected
complete multipartite graph on the other p-1 coordinate pairs. Its binary
edge span has dimension `h-3`. Lift the three edges of an outside triangle
using supported ports. Their outside coordinates sum to zero, while their
pair-i coordinates have odd total parity and do not vanish. The projection
kernel has dimension at least one, proving the `h-2` bound.

Otherwise both coefficients in pair i have one value a_i. A coarse triple
is active when its three a-values sum to a nonzero value; then all its eight
selectors belong to the support. If one pair i is never active, equations
`a_i+a_j+a_k=0` for all other j,k force all outside a_j to be one value b
and `a_i=-2b`. Nonzero f implies b is nonzero. The support is exactly every
triple avoiding pair i. Since p-1>=4, these ports span all `h-2` outside
coordinates over F2.

If every pair is active, the support contains all p pair-difference
directions. If all a_i agree, the whole port family is supported. Otherwise
choose a_i different from a_j. For each pair k,l outside i,j, at least one
of the coarse triples `{i,k,l}`, `{j,k,l}` is active. Projecting their
coarse incidence vectors outside i,j gives all edges on p-2 vertices,
whose span has dimension p-3. A triangle of such edges lifts to a nonzero
kernel vector on i,j, giving coarse span at least p-2. Quotienting the
full coordinate support by the p pair-difference directions thus proves
dimension at least `p+(p-2)=h-2`.

Now A has rational rank h. Indeed, a coefficient relation zero on every
port first forces equality within every pair by selector flips, and then
forces all pair coefficients equal by comparing triples; three times that
common coefficient is zero. Also

```
B = (AA^T-J)/2 = A (I-J_h/9) A^T / 2.
```

The middle matrix is invertible because the even integer h is not 9.
Hence B has rank h and its row space is exactly the coordinate-star span.
In any factorization `B=UV` through exactly h scalar centers, V has h
independent nonzero rows in that same span. The support lemma charges
at least `h-2` copied-center dimensions per row:

```
ell >= h(h-2).
```

The coordinate stars attain equality. Thus merely rotating, mixing or
rescaling a rank-minimal center basis cannot reduce the selected triple
construction's center loss. For the selected p=11 this lower bound is 440.

The qualifier **rank-minimal** matters. An overcomplete factor may use
rows outside the star row space whose contributions cancel after scatter;
this proof does not bound such a factor. Sharing the center computation
across stages or replacing copied centers also changes the hypotheses.
At p=4 the support lemma itself fails: a linear form supported on the one
cube avoiding a specified pair has binary support rank 4, below h-2=6.
That is an explicit domain control, not omitted from the checker.

## 5. A common triangular frame flag precludes any bit rank deficit

Consider the general finite bit contract: every role has an arbitrary
independent input, the completed scalar circuit is a permutation `rho`, all
incidences of a gate share one rational matrix, and

```
M_out(rho(w)) - M_in(w) = I_m.
```

If all source, gate and sink matrices are simultaneously upper triangular
over one characteristic-zero extension field, then **s >= Wm**. The matrices
need not commute, be projections, or be diagonalizable.

To prove this, conjugate them by the common basis; rational matrix ranks do
not change on extending the field. For one diagonal coordinate j, partition
all vertices by their j-th diagonal entry `lambda`. Regard all gates with
the same entry as a single processor and allow it free internal computation.
Its known inputs are exactly the source roles labeled lambda. Every output
at this processor demands an independent original input labeled lambda-1,
by the endpoint equation, so none of those requested inputs is initially
known there.

Each incoming edge from a different label carries one scalar. The rank of
the requested outside-input transfer, or equivalently its entropy for
uniform independent bits, forces at least one such incoming edge per output
at that processor. Summing over processors gives at least W edges whose
j-th diagonal entries change. This argument permits arbitrary communication
between gates with the same label, so that relaxation can only strengthen
the exclusion.

An upper triangular matrix has rank at least its number of nonzero diagonal
entries: take the principal minor on those entries. Therefore

```
s = sum_edges rank(M_head-M_tail)
  >= sum_j number_of_edges_with_changed_diagonal_j
  >= Wm.
```

In particular, pairwise commuting frames are excluded: a finite commuting
family over an algebraically closed characteristic-zero field is
simultaneously triangularizable, by a common eigenvector and induction on
the quotient. A rational common eigenbasis is not required.

`triangular_obstruction.py` checks a supplied exact rational common basis,
or pairwise commutation. Failing either sufficient check does not establish
a deficit. This theorem concerns the rational-matrix **bit shear** contract;
it is not a theorem about all binary Lagrangian/Clifford frame families.

## 6. Locally reused Fano networks

The graph and balanced 10-role, 14-vertex model come from the retained
`scripts/experiments/fano_completion.py` and `balanced_fano.py`, with their
original attribution. Earlier work excluded the unmodified balanced model
with the three Fano demands fixed. Here an auxiliary output stub may be
connected to a later auxiliary input stub. Each stub is used at most once.
Chronology prevents cycles; no additional decoding circuit is appended.

There are exactly 87 such choices, including the unchanged graph. Inputs
and outputs after each splice are checked to remain partitions of the
physical roles. Every remaining input is independent. Sixteen choices
preserve the original three-demand routing obstruction. On each of these,
the independent standard-library meet-in-the-middle replay excludes all
`6^14` choices of local `GL(2,F2)` matrices, with the other outputs free.

The broader C++ check drops even those three terminal obligations. For every
one of the 87 topologies it enumerates **all** completed scalar permutations
and all port-routing permutations. The sets are equal. Hence none of these
scalar completions admits a rational rank deficit in any dimension, by the
retained routing theorem. Keeping only one prefix per key would be
insufficient for this claim; the implementation retains every prefix and
checks every matching suffix/prefix pair.

Each half has `6^7=279936` assignments. A complete product is a permutation
exactly when the columns of the prefix and inverse suffix agree as
multisets. Both local direction choices and all auxiliary permutations are
included. Routing independently enumerates straight/cross choices at the
14 vertices. Small controls compare this algorithm with direct enumeration
of every complete local word.

Vector blocks are separate solver experiments. A `sat` result would need an
independent all-column replay, routing analysis and rational-frame witness.
An `unsat` solver report is not upgraded here to a separately checked
impossibility proof; `unknown` and timeout remain unresolved. No vector
experiment is used in the exact ceilings above.

## Arithmetic and limits

Logarithms use binary range reduction and
`log x=2 sum_(j>=0) z^(2j+1)/(2j+1)`, `z=(x-1)/(x+1)`, with an explicit
geometric tail. Lower bounds are rounded down on a `10^-24` rational grid.
The exponential uplift uses a finite sum of positive Taylor terms. All
upper ceilings divide by a lower entropy bound, so rounding is favorable
to the hypothetical candidate. No floating-point value is an acceptance
criterion.

Finite arithmetic and bounded exhaustive search do not formalize the whole
multiplication theorem. The inherited analytic, all-size, weighted compiler,
row restoration, precision and fixed-tape contracts remain separate. The
results above identify assumptions a successful new architecture must change;
they do not assert that any suggested replacement will succeed.
