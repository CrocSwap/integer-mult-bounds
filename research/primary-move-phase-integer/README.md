# The selected primary stores a width-1 MOVE phase, not a joint phase

**Scoped partial result; no new κ.** Assumption ID `native_all_columns`, one implication. The selected conditional exponent stays κ = 781451/250000000.

The #6030 primary recorder is `local.native` in the PR5827 archive loaded by `research/p104-helper470-twin-rung-removal`. It stores `lower_child` records. Each phase field is a width-1 residue. The function never builds a multiplicity-`f` recipe. Its returned proof sentence still says "frame induction at every positive tensor width".

The first rank-1 MOVE on the selected word is event 9896, `MOVE 236` from frame 3 to frame 7. Its stored integer is `p = 1`. On all 512 basis inputs, deleting the phase gates and rotating by `p` recovers the operator, and rotating by `p+1` does not. On all `512 × 512` pairs of those inputs, the tensor power equals a rotation by `2p`, and a single rotation by the stored integer `p` disagrees.

Copying `p` onto a joint state is the reading that fails. Executing the width-1 phase gate on every column is the reading that matches. This package does not rerun the 2,922-map native replay.

## Scope and evidence

Original card: `uniform-transfer-audit`. Scope status: **refined**. The card asks for one assumption and one quantified implication at the actual caller. The implication is the phase integer stored by the selected primary, the first open question of [the merged MOVE phase law](../move-chart-phase-power/README.md).

Pins are in [SOURCES.json](SOURCES.json). The argument is [PROOF.md](PROOF.md). Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.

Session r102, item 5 of the ordered eligible list. Structured handoffs that are completed, answered on main, or whose artifact is an open pull request are excluded, including the 19 October index, the H25 requests and the 2 November review artifacts through #6396. The revision-8 next-decision table then orders the rows, and unnamed catalogue cards follow:

1. Complex helpers (`p104-side-correction`, `coverage-law-change`).
2. BIT (`bit-helper-contract`).
3. New decoders and interfaces.
4. Supplier audit.
5. **All-size audit (this package).** The scalar lifts #5837 and #6635, the MOVE phase law #6293, and the precision-envelope note #6522 are different implications.
6. Verification tooling.
7. `bit-new-register-model`.
8. `r437-carrier-integration`.
9. `complex-rank-shape-decoder`.
10. `complex-new-helper-inventory`.

## Reproduce

```sh
python3 -B research/primary-move-phase-integer/verify.py
python3 -B scripts/research_package.py --package research/primary-move-phase-integer
```

Observed marker:

```text
PASS_PRIMARY_MOVE_PHASE_INTEGER event=9896 frames=3->7 phase=1 bases=512 pairs=262144 joint_recipe=false
```

The state check is exhaustive for this operator and takes about a second on CPython 3.12. The depth-7 source opener authenticates the archive; it does not run `local.native`.

Not run: the full native replay, the payload-hash recomputation, `make frontier6030-verify`, Lean, and Docker.

## Credit

DreamingOfClouds supplied the selected #6030 word and the verifier that loads this `local.py`. Ali Romman supplied that recorder in the PR5827 archive, and the #5599 word used by the earlier phase census. The chart compiler is the retained `clifford_exact.py` / `native_verify.py` channel. #6293 (unpaidmoon) proved `U^{(⊗)f} = i^{p f} U_0^{(⊗)f}` for every MOVE on this word and left the primary payload unread. #5837 and #6635 lift scalar instructions. #5974 (Mark / Matarener) certifies factorwise phase `i^{p f}` for the older #5599 word. Open PR #6532 (Ali Romman) binds this same event 9896 to an unbiased rounding map and its tensor-power mean. It does not read `local.native` and does not compare a copied width-1 phase integer with `p f`.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.

## Open next questions

Does the predecessor #5907 word, which has 3,454 `MOVE`s, carry the same phase histogram? The first step is the census on `research/p104-helper470-twin-rung-removal/inputs/pr5907-WORD.json.gz`. That file is not an input here.

Separately, does one rank-0 main adapter stored by the same function fail when its width-1 phase is copied onto a joint state? The first step is to lower the first adapter and repeat the width-2 comparison. The source inspection already shows that adapter records have no multiplicity field; the tensor check is not yet run.
