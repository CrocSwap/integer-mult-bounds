# Four residual physical C5 cost floors

Every finite asymmetric strict scalar fit on the four remaining physical
C5 cores has sharp complete-plane pairing cost20 over Q, R or C.
The cores are `(3,10,4,6,13)`, `(3,10,12,23,13)`, `(6,13,23,54,26)` and
`(14,24,47,18,55)`. Ordinary transpose and the full source/target plane
tariff are part of the theorem. Term count and coefficients are unrestricted.

[PROOF.md](PROOF.md) combines all forced singleton/nonadjacent-pair rank
counts with equality traces. It checks 4,096 actual rectangular tariffs,
58 cost18/19 cases and 5,327 count states. No target is reachable. Exact
cost20 fits give sharpness. The independent script uses dense binary
elimination, integer trace elimination and actual cost layers. Behavioral
controls include a literal cost19 count witness rejected by traces,
loose and capped blocks, malformed source inventories and both live sources.

This closes the four local gaps left after PR3268 and PR3271. PR3271's
already resolved fifth residual is excluded. No new 112-port decoder floor,
native program, supplier, selected frontier or kappa is claimed. Physical
routing, restoration, precision and the complete consumer remain unknown.
The proof uses elementary linear algebra; no human or proof-kernel review
is claimed. The selected cold replay, Lean and Docker are unrun.

## Reproduction

From the repository root with a session-owned external TMPDIR:

```sh
python3.12 -W error -B scripts/research_package.py --package research/c5-residual-trace-completion
```

The direct commands work in a Git-free export with the two declared inputs:

```sh
python3 -I -O -W error -B research/c5-residual-trace-completion/verify.py
python3 -I -O -W error -B research/c5-residual-trace-completion/independent.py
python3 -I -O -W error -B research/c5-residual-trace-completion/test_verify.py
```

The numerical discovery solver is unnecessary. All replay arithmetic is
standard-library integer or rational arithmetic. SOURCES.json authenticates
a fixed inventory with fixed input/provenance usages. Both live scientific
inputs are canonical-main blobs, so CI needs no pending-PR Git objects.
The generic registered wrapper separately needs Git provenance.

## Open next questions

- Can overlapping local floors give a valid global 112-port bound without
  charging a term repeatedly? First define global block weights and verify
  them on the actual full support tariff. Local floor addition is invalid.
- Which legally priced native operation implements a changed decoder
  contract? First state a complete input/output and dirty-restoration
  boundary with its physical invoice. This local theorem provides none.

See TASK.json for the structured questions and ENGINEERING.md for bounded
resource controls. Source recipes remain unchanged.

## Credit

thakrarsagar's PR3256 supplies the weighted-rank/equality-trace method.
PR3268 `ee5d4f466e6e44a1897896324a36aa4c64cf3912` supplies the residual
handoff; thakrarsagar's PR3271 `1bbe044ba2c7187dba149e40734179b2a1ebba84`
resolves the excluded fifth core with a different cover. Retain Tekalign's
PR2782 geometry, Arham Tahir/PR2879, Sagar Thakrar/PR2484, Cinna Davis/PR1825,
Adam Gall/PR1889, Nick Petalas/PR3248, PR3232, ctoth, Philippe Van Velzen
and the retained E8/P112 lineage. Apache-2.0.

A [concurrent public investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587#discussioncomment-19003766) claims the same four-core obligation and proposes exact rational separating inequalities. This package independently uses complete finite-state count closure. Both claims appeared before publication; no priority, exclusivity or literature-wide novelty is asserted. The overlap was disclosed before publication and acknowledged by the internal reviewer.
