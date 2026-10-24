# Exact Schur dimension for unequal scalar pivots

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. Over every field,
let P,Q be commuting idempotents with distinct nonzero scalar leading entries
p,q and prescribed leading product entry h. The exact least ambient dimension
attaining Schur-commutator rank two is

```text
N(p,q,h) = 3 + [h in {0,p,q}] + [1-p-q+h != 0].
```

Brackets denote indicators. Every minimum is attained by explicit matrices.
Over F3, p=1,q=2 gives minima five, five and four at h=0,1,2 respectively.
Over F5, p=2,q=3,h=4 gives dimension three.

This answers Open next question 1 of
[PR #4771](https://github.com/CrocSwap/integer-mult-bounds/pull/4771), head
`22cb0bda57237d39d0e6944b232447d3a2809311`. That equal-pivot classification
is cited, not audited. Equality of pivots is a real boundary: at h=p with
p!=q, just one zero-product sector requires two dimensions; at p=q=h,
the predecessor requires two such sectors. No new kappa is claimed.

## Proof and evidence

[PROOF.md](PROOF.md) decomposes the commuting idempotents into four joint
eigenspaces, with compressed products `(1-p-q+h,p-h,q-h,h)`. The three
active directions have pair determinants `h/(pq)`, `-(q-h)/(pq)` and
`(p-h)/(pq)`. Away from the three endpoints, their nonzero products force
rank two. At each endpoint, the missing independent direction requires a
two-dimensional zero-product sector. This proves the lower bound and gives
an attaining construction over every field.

The standalone verifier constructs full matrices for all **1,140** distinct
nonzero pivot/product triples over F3,F4,F5,F7,F8,F9. It checks idempotence,
commutation, both pivots, the product entry, literal Schur multiplication,
commutator rank and the scalar factorization. F4,F8,F9 use polynomial
quotient fields, not arithmetic modulo their orders.

A separate optimization enumerates **14,270** scalar vector pairs and
**3,528** sector-map patterns. Every minimum agrees. Dimensions zero, one
and two realize every possible zero/nonzero scalar-map type, so this covers
the sector optimization rather than truncating an ambient-matrix search.
Eight rejection controls cover all three missing required endpoint sectors,
zero/equal pivots, an out-of-field product, a nonfield order and a mutated
projector. Explicit exceptions keep checks active under optimized Python.

The finite-field and matrix helpers are adapted from Nick Petalas's #4771
verifier, with exact provenance in SOURCES.json. The new constructions,
parameter domain and optimization implement the unequal-pivot theorem.
No predecessor executable is imported or invoked at runtime.

## Reproduction

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unequal-pivot-schur-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/unequal-pivot-schur-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unequal-pivot-schur-dimension
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unequal-pivot-schur-dimension --check-source-history
```

Any CPython 3.12 interpreter can replace the local interpreter path. The direct
verifier writes nothing and prints `PASS_UNEQUAL_PIVOT_SCHUR_DIMENSION`, the
counts above and a generated SHA256 receipt for all six package files.
Metadata and source-history checks are separate from mathematical acceptance.
Each registered command has a 60-second timeout. Local measured durations were
0.113 seconds ordinary and 0.115 seconds optimized on CPython 3.12.15.
These are check durations, not performance comparisons.

The selected source-binding orientation passed after its inputs were
materialized. Current guidance replaces the card's historical first command
with `scripts/research_selected_baseline.py`. This checks metadata only.

## Scope and implementation bounds

The proof covers one-coordinate deletion, distinct nonzero scalar pivots and
commuting field idempotents. Equal pivots are credited predecessor work.
Larger prescribed product blocks, nonfield rings and later elimination
states remain outside scope. Header production/frequency, physical caller,
restoration, stock, precision and the complete consumer bill are unknown.
No supplier admission, selected-frontier change or complete multiplication
theorem is supplied. Independent human and formal proof-kernel review are
unclaimed. No Lean, Docker or selected operator replay was run.

The verifier has no recursion, subprocess, callback or generated code. Its
six fixed field domains have order at most nine; matrices have at most five
rows, helper capacities permit six rows, and elimination has at most twelve
columns. Scalar vector scans total at most 1+9^2+9^4 iterations per field; each pattern product
has four factors of at most four types, and receipts read six files of at
most 100,000 bytes each. No result matrices accumulate across triples.
Functions stay below 60 physical lines. Both registered modes use warnings
as errors. No external static analyzer is installed or claimed.

Power of Ten rule 3 deviation: CPython and its standard library allocate
dynamically. The fixed domains and stated collection limits bound live data,
but do not prohibit allocation after initialization. The verifier owns no
external mutable resources. Reassess capacities before exposing search sizes
as external inputs.

## Open next questions

1. Determine the least dimension for unequal scalar block pivots pI_d,qI_d
   and prescribed leading product H. Begin with a nondiagonal 2-by-2 H.
   Scalar nonvanishing no longer determines sector-map ranks; no block theorem
   is provided here.
2. Count complete headers realizing one prescribed unequal-pivot profile.
   Begin with the F3 p=1,q=2,h=2 construction and specify the weighted header
   ensemble. Existence alone does not give frequency or paid production cost.

Structured questions, first steps and blockers are in [TASK.json](TASK.json).

## Credit and task scope

Nick Petalas's #4771 supplies the explicit open question, equal-pivot theorem
and finite-field/matrix helpers. Nick Petalas's #4746 and ssafwann's
#4671/#4657 supply earlier identity-pivot sector constructions. Nick
Petalas's #4278/#4597 supplies scalar and ordered block factorizations.
Ryanson Jonathan's #4609/#4617 and lee-phys's #4634 supply preceding
small-field and block sharpness examples. Nick Petalas's #4259/#4228
retains the laminar-header and single-request context. Cinna Davis supplies
the BIT request setting; source527, commdata2338 and Jose Manuel retain the
normalizer lineage credit.

The formal-interface-lemma card is explicitly changed to this algebraic side
question. It settles a new prescribed-boundary minimum without extending a
physical construction. Canonical main, source pins and overlap limitations
are recorded in TASK.json and SOURCES.json.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19131498).
