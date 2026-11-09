## Why this matters

The actual canonical `Reference.for_cap` computes a narrow row-gap certificate
but leaves a positive value conditional. The Core/halo production family then
requires that same literal certificate to reach `1/(16p^2)`. A generic ideal
gap or unspecified high-precision rounding budget does not establish the
constructor's actual admission.

## Exact result

For every integer p>=2, radius R>=1, target t>=1 and legal cap/cut request,
under the source domain `theta in [1/(4p^2),1/p^2]` and
`pi alpha^2>=4 log(16p)`, the unchanged constructor returns

`reference.narrow_gap > (1/8-2^-46)/p^2 > 1/(16p^2)`.

No extra precision, larger target, changed Reference or different rounding
is introduced. The source's own normalized cap quantity has `qbar>=16pB`,
forcing `Q*>=2^21 alpha^2 pB` and `E>=47+ceil(log2 p^2)`. That existing
allocation funds the full reference error and both outward endpoint excesses.
The global narrow inverse is not assumed to derive its own admission.

## Novelty and predecessors

CrocSwap/integer-mult-bounds#4648 supplies the ideal/half-gap budget and leaves
actual W/precision binding open. The canonical raw Gaussian proof supplies
the literal certificate and cap error, while leaving positivity conditional.
This package supplies the missing allocation-to-certificate implication.
It does not reclaim those predecessor estimates or prove a new general
Gaussian theorem. `forward-fine-theta-conditioning` concerns the broad inverse
and explicitly excludes this narrow statement.

All 14 scientific inputs and card provenance are pinned to canonical base
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The original constructor/interval
bodies execute unchanged; no source body is projected by this adapter.

## Reproduction and checks

```sh
python3 -B research/production-reference-gap/verify.py
python3 -O -B research/production-reference-gap/verify.py
python3 scripts/research_package.py --package research/production-reference-gap --check-only
python3 scripts/research_package.py --package research/production-reference-gap
python3 scripts/check_research_commit.py --package research/production-reference-gap --check-modes
```

Expected status is `PASS_PRODUCTION_REFERENCE_GAP`. Exact source-bound evidence
covers 37 actual cap constructions, 505 integer interval-budget cases and 6
failure controls. A separate rational log/pi/direct-positive-Taylor oracle
checks alpha ceilings and actual certificates without importing the retained
interval backend. The largest period 2^37 and cap 2^15 remain lazy metadata;
no huge field, weight bank or native production run is claimed.

## Costs, limitations and kappa status

**No new kappa.** This removes one source-specific numerical admission,
conditional on the explicitly credited ideal, scalar enclosure and constructor
theorems. It does not collectively discharge the five selected assumptions.
Legal period cuts, complete shared-context delivery, source H/ideal N and
full transform integration, physical/native contracts and final recovery
remain required. Arbitrary manually specified References can still fail;
the controls demonstrate that scope boundary.

The proof records an explicit sufficient onset for the unchanged O(p)
allocation bounds and keeps source descriptor costs, O(p^2 log p) offline
weights, subsequent page/Schur work and backing separate. No constructor-only
bill is passed off as the cost of the complete Gaussian transform.

Prepared for **@CubeJerry** with substantial OpenAI assistance. Jose Manuel/
jmbarrancoml, Mason Hale, unpaidmoon/#4648 and the retained PR1673/PR1786/
PR4100 contributors retain their credit in NOTICE.md. Independent lead review
is separate evidence, not human or formal proof-kernel acceptance.
