# Exact Schur dimension for a common scalar block

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. For every field K,
every nonzero lambda in K and every prescribed H in M_d(K), d >= 1, the least
ambient dimension of commuting idempotents P,Q with common leading blocks
lambda I_d, leading product block H and Schur-commutator rank 2d is

```text
n_min(lambda,H) = 3d + rank((1-2lambda)I+H)
                     + 2 nullity(lambda I-H) + nullity(H).
```

Every minimum is attained by the construction in [PROOF.md](PROOF.md), including
nondiagonal and nondiagonalizable H. The four minimal joint-sector dimensions
are `(rank((1-2lambda)I+H), d+b, d+b, d+a)`, where `a=nullity(H)` and
`b=nullity(lambda I-H)`. Both input projectors simultaneously have minimum
rank `2d+a+b`.

This answers Open next question 2 of
[PR #4771](https://github.com/CrocSwap/integer-mult-bounds/pull/4771), pinned at
`22cb0bda57237d39d0e6944b232447d3a2809311`. That package treats scalar block
size one. Nick Petalas's #4746 and ssafwann's #4671 treat identity blocks.
Their results are cited inputs and specializations, not audit targets. The new
result allows a nonidentity scalar block and an arbitrary matrix product H.
No new kappa or selected-frontier change is claimed.

For example, over F5 with lambda=2 and `H=[[3,1],[0,3]]`, the exact minimum
is seven, with sectors `(1,2,2,2)`, input ranks four and Schur-commutator
rank four. For the diagonal product `H=3I_2` the minimum is six. Both H and
`2I-H` are invertible in both examples. The nilpotent part changes the
00-sector rank, which the identity-pivot formula does not capture.

## Evidence and reproduction

The proof specializes the ordered block identity of #4597 and proves that
sharpness is equivalent to injectivity and surjectivity of all six active
sector maps. The rank inequality bounds each sector separately. A split
factorization attains all four bounds and both input ranks simultaneously.
The proof holds over every field; the finite checks are corroboration.

The independently written standard-library verifier imports no predecessor
executable. It constructs full P,Q and directly checks idempotence,
commutation, both scalar block pivots, the prescribed product block, Schur
idempotence, rank drops, the ordered commutator factorization, the six-map
criterion, the ambient minimum and both input ranks. Its executed domains are:

- All 3,446 pairs `(lambda,H)` with nonzero lambda and every two-by-two H over
  F2,F3,F4,F5, respectively 16, 162, 768 and 2,500 constructions.
- All 210 scalar pairs over F2,F3,F4,F5,F7,F8,F9, including direct numerical
  comparison with #4771's piecewise scalar specialization.
- 482 additional Jordan and companion-style constructions at d=2,3 over
  those seven fields. These overlap the exhaustive domains where applicable.
- An independent enumeration of 45,900 full-rank factor pairs over F2,
  finding the exact minimum middle dimension for each of the 16 two-by-two
  compressed products. This corroborates the sector cost, rather than
  enumerating all ambient commuting projector pairs.
- Six premise-preserving missing-map controls and five malformed-input
  controls. The former retain commuting idempotents and the prescribed
  compressed products while lowering one necessary injection or surjection.
- All 1,808 field triples test associativity and distributivity; every nonzero
  element has its inverse checked. F4,F8,F9 use irreducible polynomial
  quotients, rather than arithmetic modulo their orders.

Two explicit checks compare the nondiagonal seven-dimensional F5 example
with its six-dimensional diagonal control. The generated stdout receipt binds
all six package files by SHA256. The verifier writes nothing into the checkout.

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/scalar-block-schur-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/scalar-block-schur-dimension/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/scalar-block-schur-dimension
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/scalar-block-schur-dimension --check-source-history
```

The scientific marker is `PASS_SCALAR_BLOCK_SCHUR_DIMENSION`. A different
CPython 3.12 path may replace the local path. All checks use explicit exceptions
and remain active under optimized Python. Metadata and source-history checks
are separate from mathematical verification. The selected source-binding
orientation passed; no selected scientific replay was run.

## Scope and code constraints

This is one deletion with equal nonzero scalar block pivots, field coefficients
and commuting idempotents. It gives no complete-header count, later-state law,
coefficient-ring theorem or arbitrary-block-pivot dimension minimum. Header
production, selection/emission, dispatch, dirty restoration, precision, stock
and the complete physical consumer costs remain unknown. No physical supplier
admission or complete multiplication theorem follows. Independent human and
formal proof-kernel review are unclaimed. Lean, Docker and selected cold replay
were not run.

The verifier has fixed domains, fields of order at most nine, deleted blocks
of size at most three and constructed matrices of size at most 18. Matrix
operations enforce a 24-row, 48-column capacity, including augmented elimination.
The largest exhaustive target scan has 625 matrices per pivot, and the factor
census retains at most 210 full-rank maps and 16 minima. Only the current full
construction and counters persist across target scans. All calls are direct;
there is no recursion, subprocess, callback chain or generated code. Functions
stay below 60 physical lines. Warnings are errors in both registered commands;
syntax, function lengths and dynamic-code calls are inspected locally. No
external static analyzer is installed or claimed.

Power of Ten rule 3 deviation: CPython arithmetic and tuples allocate during
execution, so this standalone verifier cannot prohibit dynamic allocation.
The fixed field, matrix, census and six-file receipt capacities bound its live
data. Both registered modes exercise these bounds, and explicit controls reject
an oversized matrix and invalid target shapes. The deviation is confined to
this verifier; reassess storage and input validation before adding larger
domains or an external parameter interface. It owns no external mutable resource.

## Open next questions

1. Determine the prescribed-H minimum for unequal scalar block pivots pI_d
   and qI_d at d>=2. This would separate equality of the pivots from their
   scalarity. Start with the two ambient factors and an H with an eigenvalue
   at one pivot but not the other. The scalar unequal-pivot question is
   separately claimed and is not delivered here.
2. Count complete headers attaining one nonidentity scalar-block profile.
   Feasibility alone gives no frequency or paid header cover. Start with the
   F5 profile `(1,2,2,2)`, d=2, lambda=2 and the fixed Jordan product above.
   A joint factorization count and the producer/consumer bill remain open.

## Credit and task scope

Nick Petalas's #4771 supplies the explicit open matrix-product question and
scalar predecessor; #4746 supplies the all-field identity-pivot predecessor.
ssafwann's #4671/#4657 supplies the binary fixed-H theorem, six-map method
and split-sector construction. Nick Petalas's #4597/#4278 supplies the ordered
block and scalar Schur factorizations. Ryanson Jonathan's #4609/#4617 and
lee-phys's #4634 supply earlier small-field and unrestricted-block sharpness
constructions. Nick Petalas's #4259/#4228 retains the laminar-header and
single-request context. Cinna Davis supplies the BIT request setting;
source527, commdata2338 and Jose Manuel retain the normalizer lineage credit.

The formal-interface-lemma card is explicitly changed to this algebraic side
question. It resolves a prescribed-boundary dimension question without auditing
another contributor or expanding a physical construction. Exact source pins,
overlap coverage, the advance claim and preserved checkout state are recorded
in TASK.json and SOURCES.json. No predecessor file or credit line is changed.
