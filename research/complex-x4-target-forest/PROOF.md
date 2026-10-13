# Signed target forests for the selected X4 compensation panel

This is a finite circuit construction and an exact cost optimum within a stated
forest class. It does not assert a new exponent or optimality among arbitrary
circuits. The source is the selected PR799 X4 word, at audited source head
`80e6463157cfc80b85af09e7e2f14748fe2dac60`, read from the accepted replay archive
on base `91a2094f2e022930069e8cfdc810a3ea1b81cd09`. The package's executable
source pins and receipt identify the precise archive members and counts.

## 1. The boundary being replaced

Let `y` denote the 112 compensation targets and `h` the arbitrary public helper
inputs. Write `C_i` for row `i` of the exact dyadic compensation matrix. The
forward panel has the complete logical boundary

```text
(y, h) -> (y + C h, h).
```

Neither vector is assumed zero. The coefficient-work register can initially
contain arbitrary private dirt; its paid lowering clears it. All instructions
introduced by this construction occur at the panel's inherited zero frame.
The source checker must establish that frame and panel identification; the
linear argument alone would not establish geometric legality.

Choose a rooted forest on the 112 target labels. Every nonroot `i` has one
parent `p(i)` and one sign `epsilon_i` in `{+1,-1}`. Prepare targets with

```text
y_i <- y_i + epsilon_i y_p(i)
```

The executable recipe stores `sign_i=-epsilon_i`, so its equivalent notation
is `y_i <- y_i-sign_i*y_p(i)` and `C_i-sign_i*C_p(i)`.

in leaf-before-parent order. A parent's original input has not yet been
modified when one of its children uses it. Consequently the product `T` of
these shears has rows `e_i + epsilon_i e_p(i)` at nonroots and `e_i` at roots;
no ancestor terms have silently appeared. This is a unit triangular matrix
after a forest ordering, hence invertible over the dyadic rationals.

Run ordinary compensation on the transformed targets with rows

```text
root i:       C_i
nonroot i:    C_i + epsilon_i C_p(i).
```

Finally undo each preparation shear, with its opposite sign, in reverse
chronological order. This yields, for arbitrary target and helper inputs,

```text
T^-1 (T y + T C h) = y + C h.
```

All forward helper inputs are unchanged. Restoring in the wrong order is not
generally valid on a path of length two: a child must use the already-restored
parent when its own shear is undone. The exact recipe contains both orders.
Neither the proof nor the replay permits replacing `Ty` by zero.

## 2. Complete scalar cost in the specified lowering

The class uses the unchanged cleared-work binary-Horner lowering, independently
for every nonzero coefficient. Put `c(0)=0`. For a nonzero reduced dyadic
coefficient `q=a/2^k`, where `a` is a nonzero integer and `k>=0`, the cost per
real component is

```text
c(q) = 3 + floor(log2(abs(a))) + popcount(abs(a)) + k.
```

The bill is one initial work clear, `floor(log2(abs(a)))` doublings,
`popcount(abs(a))` source additions, `k` halvings, one signed target
accumulation, and one final work clear. This includes leading-bit source
access and permits arbitrary initial work. It also proves `c(-q)=c(q)` and
`c(1)=c(-1)=4`. Thus a preparation shear and its restoration cost **eight**
primitives per real component, including their coefficient work. They are
not treated as two cost-free changes of notation or as two unit additions.
Both real components of a complex stream are charged separately.

For a row `v`, let `R(v)=sum_j c(v_j)`. A root contributes `R(C_i)`. An edge
from nonroot `i` to parent `j` with sign `epsilon` contributes

```text
w(i,j,epsilon) = R(C_i + epsilon C_j) + 8.
```

This is a complete forward-panel bill within this class. It includes every
residual coefficient macro, source access, preparation and restoration. No
extra helper, frame change, copy, recursive child or center is introduced.
Every non-scalar event and every scalar macro outside the panel remains the
corresponding pinned source event. Those unchanged costs are retained in the
full-program comparison; they are not a source of the reported saving.

The model deliberately does not combine neighboring work clears, replace unit
Horner circuits by a cheaper lowering, share coefficient work across entries,
or fold the basis changes into an adjacent phase. Those are different classes.

## 3. Exact forest optimum by a superroot spanning tree

Construct a multigraph with target vertices `0,...,111` and one superroot `r`.
These are abstract labels; the source registers are `112,...,223`, and the
recipe represents the superroot by `-1`.
Include edge `(r,i)` of weight `R(C_i)` for every target. Between every two
distinct targets include two parallel edges with the weights
`w(i,j,+1)` and `w(i,j,-1)`. There are
`112 + 2*binom(112,2) = 12,544` edges and 113 vertices.

The target-edge weights are independent of orientation. For the plus sign
this follows by commutativity; for the minus sign it follows from
`C_j-C_i=-(C_i-C_j)` and the sign-invariance of `c`. More uniformly,
`C_j+epsilon C_i = epsilon(C_i+epsilon C_j)`.

Any target forest becomes a spanning tree by joining each of its roots to
`r`. Its complete cost is exactly the resulting tree's weight. Conversely,
orient any spanning tree away from `r`, remove `r` and its incident edges,
and retain the sign on each target edge. Each remaining component has one
root, each other target has one parent, and Section 1 realizes precisely the
tree's cost. These operations preserve cost in both directions. A tree cannot
use both parallel edges between the same vertices, because they would form
a cycle in the multigraph.

It follows that a minimum spanning tree attains the minimum complete cost
over this **single-parent signed-unit target-forest class**. This is not a
heuristic claim about the deterministic tie ordering. Seed 34 only chooses
among tied options; it does not restrict the edge census.

The finite certificate is checkable without trusting the construction's
Kruskal algorithm: check that the selected edges form a spanning tree, sum
their exact integer prices, then check for every graph edge that its weight
is at least the largest selected-edge weight on the unique tree path between
its endpoints. If a cheaper graph edge violated this condition, exchanging
it with that largest path edge would improve the tree. Conversely, when all
these cycle inequalities hold, repeated exchanges transform any spanning
tree into the selected tree without increasing weight, proving minimality.
An independently coded Prim computation supplies an additional exact check.

This floor excludes nonunit parent coefficients, multiple parents, helper
basis changes, shared subexpressions, and changes outside the panel. It is
not an impossibility theorem for cheaper compensation circuits.

The attained recipe has six roots and 106 signed target edges. It replaces
6,320 compensation additions by 2,324: 106 preparation, 2,112 residual, and
106 restoration additions. Its exact minimum is **10,883** primitives per
real component, compared with the original panel's **34,728**. Equivalently,
these count complex-stream primitives before charging two real components.
The complete emitted scalar-program counts are:

| Orientation | Original real primitives | Forest real primitives | Saving |
| --- | ---: | ---: | ---: |
| Forward | 193,162 | 145,472 | 47,690 |
| Inverse transpose | 193,210 | 145,520 | 47,690 |

These counts do not combine this construction with a different scalar
lowering or with other pending supplier changes.

## 4. Inverse-transpose orientation

A logical addition `G=I+q e_t e_s^T`, with distinct source and target, has
`G^-T=I-q e_s e_t^T`. Thus inverse-transposition swaps source and target and
negates the coefficient. If macros are executed chronologically as
`G_1,...,G_m`, their total map is `G_m...G_1`, whose inverse transpose is
`G_m^-T...G_1^-T`. Execute the inverse-transposed macros in the **same
chronological order** and then lower each one afresh. Their coefficient
magnitudes, and hence their scalar bills, are unchanged.

This argument concerns invertible logical macros. The private-work CLEAR
primitives are not invertible and are not inverse-transposed. Their charged
implementation is separately checked on arbitrary private work inputs.

The inverse-transpose panel maps `(y,h)` to `(y,h-C^T y)`. It intentionally
writes helpers in this orientation; the forward panel's unchanged-helper
statement must not be applied to it. The complete supplier's required
endpoint, including public helper restoration and private clearing, must
therefore be replayed in each orientation against its pinned baseline.

## 5. Numerical scope, checks and inherited obligations

Endpoint equality does not imply safe intermediate magnitudes. Prefix bounds
must be recomputed from the actual candidate instruction stream in both
orientations, including basis changes and all binary-Horner work. For a
positive upper envelope, a signed addition is safely bounded by adding the
absolute coefficient times the source bound; dyadic scaling and work clears
are applied at their actual positions. Acceptance requires the fresh bound
to meet the inherited 192-bit local payload allowance. A smaller gate count
alone is insufficient, and no containment in the original prefix trace is
asserted. This exact finite bound does not settle all-size rounding or tape
precision.

Literal primitive replay on all 728 logical and nine arbitrary private input
columns gives the following positive prefix envelopes:

| Orientation | Original | Forest | Original / forest bits |
| --- | ---: | ---: | ---: |
| Forward | `6812058044968180837/256` | `6812058044968180837/256` | 55 / 55 |
| Inverse transpose | `48299247699832632898063/16` | `219829455967238186882729/16` | 72 / 74 |

The increased inverse-transpose envelope is explicitly charged; it is not
inherited unchanged. Both remain below `2^192`. The largest exact fractional
grid depths of actual replayed rows are respectively 3 and 19 bits, unchanged
between original and candidate. These are finite-stream measurements, not a
general precision theorem.

Useful adverse controls include: omitting preparation (which may pass a
helper-only replay but fails arbitrary target columns), omitting restoration,
changing one sign or transformed coefficient, reordering a length-two path's
preparation, omitting work clear, and underbilling the two unit boundaries.
The certificate must also reject non-tree edges, altered edge prices, and a
nonminimal tree even if its resulting linear map is correct. A failed search,
a rejected corrupted certificate and a general proof are different evidence.

The finite word replay and the forest-class proof do not reprove geometric
and physical admission, global hosting/invoices, outer assembly, or a full
multiplication theorem. Production use requires typed construction integration
and refreshed bindings. All inherited compiler/common-label/mutable-source,
whole-call hosting, precision/tape, analytic-transfer and bit-supplier
assumptions remain. The selected conditional exponent is unchanged.

## 6. Predecessors and attribution

This does not claim invention of restored target forests or their spanning
tree reduction. Credit Sricharan Vagvala's PR749 for rational restored target
pairs, Oscar Fennell's PR759 for binary target forests and the superroot
reduction, and **PR816 by @dd-hemant**, pinned at
`133735a2cc2319c12ba5d786214b2217e083e7da`, for the same signed rational
coefficient-dependent forest mechanism on historical CK. **PR901 by ToikY**,
pinned at `dbe8dc01f8306bd7dab8d861a953b23e5cda6a70`, applies disjoint restored
target pairs to this selected X4 compensation panel. This contribution checks
the larger forest class on that selected panel rather than asserting priority
for the mechanism. No savings from those separate packages are assumed
additive or imported without source verification.

The X4 supplier retains Jeremy Kothe's PR799, Chafik Boukhalfa's PR741,
icekylinx's gauge44, and the compiler/cold/owner and other contributors named
in the selected maintainer review and original notices. This proof was
prepared for Ross with substantial OpenAI Codex assistance, including a
separate proof-review worker. Apache-2.0 applies to the new contribution;
predecessor notices are retained. No independent human review is claimed.
