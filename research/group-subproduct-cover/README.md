# Exact subproduct covers with arbitrary scalar workspace

**Written formal-model theorem; no new kappa.** For any field and group,
the paid count for a diagonal tuple of group labels equals its minimum
ordered-subproduct cover, in the arbitrary-rank unit-gate model below.
Extra finite workspace and arbitrary free scalar maps cannot lower this
count. Diagonal projectors attain every cover without workspace.

For three distinct nonidentity labels, with every nonidentity group element
allowed as a paid label, the exact count is two if the triple is `{g,h,gh}`
for some ordered pair. It is three otherwise.

The actual order-21 target `diag([a],[a^2],[a^4])` still costs three. Unlike
the earlier finite census, this conclusion allows every field, any finite
scalar workspace, singular free scalar maps, and paid projectors of any
rank. The old rank-one minimum three therefore also survives those free
scalar resources. In contrast, the Q8 target `diag([i],[j],[k])` takes two
rank-two gates here. Its old rank-one minimum does not transfer to this
larger gate class.

[PROOF.md](PROOF.md) gives the quantified theorem, converse construction,
resource boundary and two examples. [RESULT.json](RESULT.json) holds the
recomputed finite receipt; [SOURCES.json](SOURCES.json) pins the three
predecessor notices and the historical assignment. The finite tables support
the written proof; they do not establish its unbounded quantifiers alone.

A coefficient-rank argument also proves that any two-call realization of a
three-label target needs rank at least two in **each** projector. Therefore
every triple of distinct nonidentity labels has exact rank-one call count
three, over every field and with arbitrary finite free scalar workspace.
Its exact rank-charged cost is also three. The two-call construction costs
at least four rank units.

## Model and complete scope

Work in the formal group algebra `K[G]`. A paid gate is
`D(N,g)=(I-N)[e]+N[g]`, with `N^2=N`. Its cost is one at every rank of N.
Free maps are fixed scalar linear maps, with no address action. They may
change dimension, copy, clear or discard registers. Data-dependent control
and free address operations are outside this class. Group labels are formal
basis elements; a regular action preserves the theorem, but an arbitrary
natural representation need not preserve it.

For a paid word `(g1,...,gk)` in matrix order, all endpoint support lies in
`{g1^b1 ... gk^bk : bj in {0,1}}`. This is the inherited support method.
The new exact criterion requires one such set to contain all target labels.
Conversely, choose one mask for each target and put those bits on the
projector diagonals. This realizes all targets at once. Additional dirty
registers remain untouched. Arbitrary-rank unit cost is an explicit
optimistic relaxation, not an uncharged physical implementation.

The proved bill is only this abstract count. Physical group gates, scalar
maps, source reads, frame changes, precision, recursive children, hosting
and cleanup remain unpriced. The three direct order-21 gates use rank-one
projectors, but no native supplier is supplied. The complete multiplication
exponent and selected frontier are unchanged.

## Exact finite evidence

Two implementations classify every unordered triple of distinct nonidentity
labels in each listed group. They agree on each triple, not only the totals.

| Group | Triples | Minimum two | Minimum three | Regular columns, including two dirty roles |
|---|---:|---:|---:|---:|
| C7 | 20 | 12 | 8 | 700 |
| C7 semidirect C3 | 1140 | 348 | 792 | 119700 |
| Q8 | 35 | 11 | 24 | 1400 |

The primary uses group multiplication tables and sparse integer group-algebra
matrices. It checks all 1195 constructed endpoints over the integers, so
those identities reduce to every field. It also checks 216 complete covers
from three-letter C7 words and 96 scalar interleavings over F2, F3 and F5,
including rectangular endpoint maps, singular free maps and dense rank-two
projectors. Another 96 cases check the two coefficient-cut identities and
rank bounds with singular free maps over the same three fields.

The separate implementation imports no primary code. It obtains C7 and the
order-21 group from permutations of seven points, Q8 from signed quaternion
multiplication, and the triple criterion from ordered pairs inside each
triple. It then checks all 121800 columns of the **regular** action, including
two independent dirty registers. The seven-point action is used to encode
group elements, not to accept formal linear combinations.

Twelve in-verifier controls cover rank-two Q8 construction, reversed order,
group versus scalar signs, dirty return, omitted or changed gates, dirty
endpoint changes, uncovered targets, invalid projectors, empty/repeated
targets and a natural-action alias. That alias has 14 nonzero formal terms
but vanishes in the faithful seven-point group representation. This shows
why faithfulness on group elements is not enough for a group-algebra test.

## Reproduce

Python 3.12 and the standard library, from the repository root:

```sh
python3 -B scripts/research_package.py --package research/group-subproduct-cover
python3 -I -O -B research/group-subproduct-cover/verify.py
python3 -I -O -B research/group-subproduct-cover/independent.py
```

Expected final markers:

```text
PASS_GROUP_SUBPRODUCT_COVER triples=1195 order21_min=3 q8_relaxed_min=2 controls=12 no_new_kappa
PASS_INDEPENDENT_SUBPRODUCT_COVER triples=1195 regular_columns=121800 no_new_kappa
```

Both scripts are read-only by default and use no network or Git. The primary
checks live source bytes by SHA256 and Git blob digest. Receipt comparison
preserves JSON types. The optional `--write-receipt` creates a missing receipt
and refuses overwrite. Exported source files must remain at their declared
repository-relative paths. The registered runner checks provenance separately.

No predecessor circuit census, selected native/full supplier, full-history,
Lean, Docker, independent human or formal-kernel verification is claimed.
The selected source-bound baseline passed at the base; that is not admission.

## Current priorities, overlap and credit

Base `1ec1119972c9aefe42525172d07b332fcff81cb4`, priority revision 7. The
`bit-new-register-model` scope changes the projector rank, field and free
workspace premises. This is a bounded structural screen, not a larger search
inside the old 560-operation alphabet. The complete cost boundary above is
its family decision: finish the exact criterion and stop; unknown physical
costs do not become zero.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167#discussioncomment-19154784)
records the premise change and stop rule. The preclaim overlap scan covers
338 open PRs, 4677 Discussion records and all 7267 base HEAD notes, with
complete pagination at 21:17–21:18 UTC on 2026-10-23. Exact joint-cover and
ordered-subproduct terms, the order-21 scope, and the nearby scalar-workspace
proofs were checked. This is text coverage, not proof of novelty or a scan
of unpublished branches and all diffs.

Credit the following material predecessors:

- OpenAI Codex at Cinna's direction: [PR #2011](https://github.com/CrocSwap/integer-mult-bounds/pull/2011)
  and its [order-21 source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/bit-semidir21-orbit-seed8f89/README.md)
  supply the target, group and original finite rank-one minimum.
- Cinna Davis: the [Q8 source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/bit-q8-three-register-two-call-seed189ad74/README.md)
  supplies the rank-one comparison and its operation boundary.
- JoyboyBrian: the [three-cycle source](https://github.com/CrocSwap/integer-mult-bounds/blob/1ec1119972c9aefe42525172d07b332fcff81cb4/research/three-cycle-address-floor/README.md)
  gives the explicit all-workspace formal subword-support argument. Its
  single-cycle CNOT theorem and retained contributor lineage remain prior work.

The new contribution is the simultaneous cover converse in this relaxed
class, the all-field workspace extension for the actual order-21 target,
the sharp two-call projector-rank bound, and the independent complete triple
classification. It does not claim
invention of group-algebra support expansion or literature priority.
Prepared by Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.

## Open next questions

For four or more distinct targets, when does rank-one cost exceed the relaxed
subproduct-cover cost after arbitrary finite scalar workspace is allowed?
First specify one target and group, then derive coefficient cuts that remain
valid when ordered subproducts collide. The two-call rank proof relies on
four distinct labels and does not establish a longer-word invariant. A larger
census alone would not close the unbounded workspace question. Physical gate
realization and a complete supplier cost remain separate missing work.
