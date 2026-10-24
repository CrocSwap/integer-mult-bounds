# Exact Schur dimension for a prescribed scalar pivot and product

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. Let P,Q be
commuting idempotents over any field, with the same nonzero scalar first
entry lambda and prescribed first entry h of PQ. The least ambient dimension
in which their one-coordinate Schur complements have commutator rank two is

```text
                    4 + [1-2lambda != 0],  h=0,
N(lambda,h) =       5 + [lambda != 1],     h=lambda,
                    3 + [1-2lambda+h != 0], otherwise.
```

Here brackets mean the indicator of a field inequality. Every minimum is
attained by the explicit sector construction in [PROOF.md](PROOF.md).
In particular, a nonidentity pivot with h=lambda requires exactly six
dimensions. Over F3, lambda=h=2 requires six, while the same pivot with
h=0 or h=1 requires four. Nonidentity pivots therefore change the endpoint
dimension law, rather than simply replacing the symbol 1 in the old formula.

This answers the scalar part of Open next question 1 in
[PR #4746](https://github.com/CrocSwap/integer-mult-bounds/pull/4746), pinned at
`5f014560d6225cae17598ac479fb29d2947d8e6b`. Its identity-pivot formula,
ssafwann's binary theorem in #4671 and Ryanson Jonathan's earlier unrestricted
small-field minima in #4609 are predecessor results, not new claims here.
The new result is the exact dependence on both prescribed scalars, including
the replacement sharpness criterion, over every field. No new kappa.

## Evidence and reproduction

The written proof decomposes the commuting projectors into their four joint
eigenspaces. The compression products are
`(1-2lambda+h,lambda-h,lambda-h,h)`. Nick Petalas's #4278 factorization
reduces sharpness to two explicit rank-two conditions. Their zero-product
sectors need two dimensions precisely in the endpoint cases above.

The independently written standard-library verifier imports no predecessor
executable. It constructs actual P,Q and checks idempotence, commutation,
both pivots, the prescribed product, direct Schur multiplication and the
ordered factor identity. It covers every nonzero lambda and every h over
F2,F3,F4,F5,F7,F8,F9, totaling **210 parameter pairs**. This includes the
known identity-pivot specialization as a calibration case.

A separate finite optimization enumerates **14,291 scalar vector pairs**
through sector dimensions zero, one and two, recording every possible
zero/nonzero map type and its minimum dimension. It evaluates **1,212
four-sector patterns** and matches the formula in all 210 cases. Two
dimensions suffice to realize any scalar map type, as explained in the
proof; this is not a truncated search over ambient matrices.

Seven controls detect omitted necessary zero-product sectors in both
endpoint cases, a zero pivot, an incorrect sector sign, a mutated projector,
a singular coordinate basis and an unsupported nonfield order. F4,F8,F9
use polynomial quotient fields, not arithmetic modulo their orders. All
checks remain enabled under optimized Python.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/scalar-pivot-schur-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/scalar-pivot-schur-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/scalar-pivot-schur-dimension
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/scalar-pivot-schur-dimension --check-source-history
```

Another CPython 3.12 path may replace the local path. The direct verifier
writes nothing and emits `PASS_SCALAR_PIVOT_SCHUR_DIMENSION` with a generated
receipt binding all six package files by SHA256. The metadata runner and
publication preflight are separate from the mathematical claim.

The selected source-binding orientation passed after its declared inputs
were materialized. Its source hashes and budget metadata are consistent;
no selected scientific replay was run. The card's historical first command
has been replaced by `scripts/research_selected_baseline.py` in current
repository guidance.

## Scope and code constraints

The theorem concerns one scalar deletion, equal nonzero pivots and commuting
idempotents over a field. Unequal pivots, larger deleted blocks with prescribed
matrix product, coefficient rings, later-state transitions and header
probabilities are outside scope. Producer selection, header emission,
dispatch, dirty restoration, stock, precision and the complete consumer
cost are unknown. No physical supplier admission, selected-frontier change
or complete multiplication theorem is claimed. Independent human and formal
proof-kernel review are unclaimed. Lean, Docker and selected cold replay were
not run. All registered local checks are required before publication.

The fixed verifier uses seven fields of size at most nine. Matrices have at
most six rows, elimination at most twelve columns, and vector scans at most
q^4=6561 iterations per field. Each pattern product has four finite factors,
each containing at most four map types. Only counters, small field tables
and the current construction persist. There is no recursion, subprocess,
code generation or user-controlled input. Functions stay below 60 physical
lines. Explicit exceptions enforce bounds and invariants under -O. Warnings
are errors in both registered commands; syntax and function lengths are
also inspected locally. No external static analyzer is installed or claimed.

Power of Ten rule 3 deviation: CPython arithmetic, iterators and collections
allocate dynamically. This bounded standalone verifier cannot prohibit
runtime allocation. The fixed field, vector, matrix and six-file receipt
capacities bound live data; no state accumulates across the 210 cases.
Both registered modes exercise the bounds and seven rejection controls.
Reassess fixed storage and input validation before adding larger domains
or an external parameter interface. The deviation is confined to this
verifier, which owns no external mutable resources.

## Open next questions

1. Determine the minimum for unequal nonzero scalar pivots p,q with
   prescribed h. The same four-sector method starts with products
   `(1-p-q+h,p-h,q-h,h)`, but its independent-direction cases need a new
   classification. This would separate equality of pivots from scalarity.
2. Determine the prescribed-matrix-product minimum for a common nonidentity
   scalar block lambda I_d. Start with one nondiagonal H; scalar sector-map
   nonvanishing no longer determines rank. This theorem gives no all-d bound.
3. Count complete headers for one fixed nonidentity scalar profile. Dimension
   feasibility does not provide frequency or a paid header producer. Specify
   the header ensemble before deriving a count or claiming a physical gain.

## Credit and task scope

Nick Petalas's #4746 supplies the explicit open question and all-field
identity-pivot predecessor. ssafwann's #4671/#4657 supplies the binary
dimension theorem, six-map method and split sector construction.
Nick Petalas's #4278/#4597 supplies the scalar and ordered block Schur
factorizations. Ryanson Jonathan's #4609/#4617 and lee-phys's #4634 supply
preceding small-field and unrestricted-block sharpness constructions.
Nick Petalas's #4259/#4228 retains the laminar-header and single-request
context. Cinna Davis supplies the BIT request setting; source527,
commdata2338 and Jose Manuel retain the normalizer lineage credit.

The formal-interface-lemma card is explicitly changed to this algebraic
side theorem. The work supplies a new prescribed-boundary dimension law,
without auditing another contributor or expanding a physical mechanism.
Exact citations, source provenance, overlap coverage, the advance claim and
the preserved checkout state are recorded in TASK.json and SOURCES.json.
