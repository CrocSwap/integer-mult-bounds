# Thirty parity-DAG edge obstructions beyond pointwise frame legality

**Scoped negative result and exact local repairs; no new kappa.**
In the historical `ParitySide(10)` DAG, 30 internal edges have individually
legal endpoint frames but **no legal nested endpoint pair at any dimension**.
These are distinct from the common-span and incident-residual obstructions
already found at individual nodes. A second group of 50 edges fails at
minimum dimensions and becomes legal by enlarging the target frame from
dimension five to six. These are local repairs, not a compatible DAG labelling.

The investigation base is `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
The assignment seed is 46, structural decoder research. The current selected
bound at that base comes from #942; this package does not modify it.

## Reproduce

From the repository root, with Python 3.11 or later and no extra packages:

```sh
python3.11 -I -O -B research/parity-edge-compatibility-seed46/verify.py
```

Expected output:

```text
PASS_PARITY_EDGE_COMPATIBILITY {"alternating_only": 200, "excluded_local_failure": 784, "legal": 3318} {"impossible": 30, "repairable": 50} controls=10
```

`--emit` prints the regenerated certificate to stdout. JSON whitespace is not
part of the certificate identity. The default command compares the complete
parsed certificate, checks seven SHA-256 source pins, reconstructs all 14,400
signed output coefficients, and checks the exact finite domains below. Its
explicit checks remain active with `-O`.

## What was exhausted

The fixed DAG has 2,271 active nodes and 4,302 internal argument edges.
For every node, let `A` be the span of its ancestor source triples and `B` the
span of its descendant target triples, over `F2^10`. Each frame `U` must be
nondegenerate and satisfy `A <= U <= B-perp`. A legal incident frame also
requires the residual to every actual ancestor source line and descendant
target-line complement to be zero or nonalternating.

The first census enumerates **all minimum separating frames**, then applies
those incident conditions. It does not enlarge a locally failing frame in
this first pass.

| Node result | Count |
| --- | ---: |
| Has an incident-safe minimum separating frame | 2,037 |
| No minimum frame passes the incident conditions | 232 |
| Common-span obstruction | 2 |
| Minimum frames before / after the incident filter | 4,673 / 4,015 |

The 232 locally failing nodes include 100 nondegenerate source spans and
132 radical-one spans. The latter count agrees with #993's 692-node census:
560 work at the separating minimum and 132 do not. This first pass does not
classify the larger-frame possibilities of those 232 nodes.

| Edge result at minimum endpoint dimensions | Count |
| --- | ---: |
| At least one legal frame pair | 3,318 |
| A locally failing endpoint, excluded from the pair question | 784 |
| Nested pairs exist, but every one has an alternating residual | 200 |
| No nested pair, with both endpoints locally feasible | 0 |

All 9,832 endpoint pairs for the 3,518 eligible edges are checked: 5,512 are
legal, 2,054 have a nonzero alternating residual, and 2,266 are not nested.
The 200 failed edges divide into 120 whose source spans are both nondegenerate
and **80 whose target source span has radical dimension one**. The former
corroborate the historical source-span repair diagnosis. The latter test the
newly available pointwise completions of #972/#993.

For those 80 edges, both endpoint extension quotients `B-perp/A` have
dimension at most three. The follow-up exhausts **every frame dimension**:
1,155 subspaces at 160 distinct endpoints, yielding 580 incident-safe frames.
Repeated one-vector extension and a separate enumeration of all XOR-closed
quotient subsets agree on every subspace, including rejected ones.

| All-dimension result on these 80 edges | Count |
| --- | ---: |
| No legal endpoint pair at any dimension | 30 |
| Repaired with exactly one additional target dimension | 50 |

For each of the 30 impossible edges, the source has exactly one legal frame
and the target exactly two. All 60 candidate pairs fail the residual rule.
For the other 50 edges the certificate supplies a dimension `(3,6)` pair.
The minimum census excludes added dimension zero, so one is minimal for each
of these local repairs. An added frame dimension is not a paid recursive
cost or an asymptotic improvement.

## A small explicit obstruction

Vectors below are integer bitmasks, with bit zero the first coordinate.
For edge `736 -> 737`, the actual labels are:

| Node | Source triples | Target triples |
| --- | --- | --- |
| 736 | 41, 42, 44 | 56, 208, 336, 400, 592, 656, 784 |
| 737 | 35, 37, 38, 41, 42, 44 | 208, 336, 400, 592, 656, 784 |

Each endpoint admits exactly five separating subspaces before testing
nondegeneracy and incident residuals. After those tests, the complete lists
of legal frames at all dimensions are:

- Source: `U = span(41,5,3)`.
- Target: `V1 = span(32,8,4,2,1)` or `V2 = span(961,32,9,5,3)`.

Both target frames contain `U`. Their residuals are respectively
`{0,15,39,40}` and `{0,15,999,1000}`. Every vector in each residual has even
weight. Thus both nonzero residuals are alternating and have no orthonormal
basis. Individually legal endpoints do not suffice for a legal edge.

For contrast, edge `234 -> 1217` has the legal pair
`U = span(32,20,12)` and `V = span(961,32,16,8,4,3)`.
Its dimensions are three and six. This is a positive control for the
all-dimension search, not an assertion that neighbouring edges also work.

## Why the finite enumeration proves the scoped claims

**Local completeness.** For `A perpendicular B`, a nondegenerate sandwich
exists iff `A intersect B = 0`, with minimum dimension
`dim(A) + dim(rad(A))`; #972 supplies the general extension argument.
In this fixed DAG every unobstructed radical has dimension zero or one.
At radical zero the only minimum frame is `A`. At radical one, every
minimum frame is `A + span(z)` for a vector `z` in `B-perp` that pairs
nontrivially with the radical. The checker enumerates all 1,024 possible
vectors, reduces duplicate spans, and checks their dimension and radical.
This exhausts the minimum domain without relying on a particular completion.

**Incident and edge legality.** For a nondegenerate space `U`, its
characteristic vector `w_U` is defined by `w_U dot x = x dot x` for all
`x` in `U`. If nondegenerate `U <= V`, then
`V = U orthogonal-direct-sum (V intersect U-perp)`, so the residual's
characteristic vector is `w_V + w_U`. A nonzero residual is alternating
exactly when `w_V = w_U`. A zero residual is allowed. This is the same
criterion used in the historical parity repair, not a new transfer theorem.
The scalar source and target labels have odd weight, so their one-dimensional
spaces are nondegenerate. For incident checks the source characteristic is
the source triple `s`, and the target-complement characteristic is `1023+t`.
The checker compares these characteristic tests with literal residual vector
sets and odd-weight membership. It also checks every edge pair directly.

**All dimensions.** Subspaces containing `A` and contained in `B-perp`
correspond bijectively to subspaces of `B-perp/A`. Adding every admissible
vector until closure lists them all. Independently, for quotient dimension
at most three, the checker enumerates every subset of the at most eight
quotient vectors, retaining exactly those containing zero and closed under
XOR. It lifts every retained subset and compares the complete subspace sets
with the first method. Filtering these exhaustive sets by nondegeneracy and
the literal incident conditions cannot omit a legal frame. Checking the
Cartesian product of the endpoint lists proves each reported pair exclusion.

The argument is a finite, executable proof of the stated geometry on the
pinned DAG. It is not a formal proof in a proof assistant, and does not prove
the conditional integer-multiplication theorem.

## Scope, cost and remaining obligations

The optimistic budget can set gates, copies, helpers, source access,
restoration and recursive children to zero and still cannot make any of the
30 obstructed edges legal under this fixed nested-frame contract. This
closes that local geometric mechanism only. It does not exclude changing
the DAG, source/target labels, transfer model, or inserting paid non-nested
transfers. No new supplier or complete cost recurrence is claimed.

The 50 local lifts still need compatible choices on neighbouring edges,
full transfer counts, copy/restoration work, helper and source-access costs,
recursive profiles, and assembly constraints before they could support a
supplier claim. The other 120 minimum-frame failures and the 232 locally
failing nodes are outside this all-dimension follow-up. Inherited compiler,
realization and analytic obligations of the selected bound are unchanged.

`CERTIFICATE.json` contains every minimum-failure row, all 80 all-dimension
edge results, and all legal frames and labels at the 160 extended endpoints.
Minimum-failure rows have fields
`[source,target,source_dim,target_dim,source_choices,target_choices,legal,alternating,not_nested]`.
The digest of the complete eligible-edge table binds the remaining rows in
increasing target-node order, then stored argument order, using compact JSON.
`SOURCES.json` pins runtime inputs and
predecessor heads. `CLAIM.md` records selection, stopping rules and overlap;
`VALIDATION.md` records completed checks. See `NOTICE.md` for attribution.
