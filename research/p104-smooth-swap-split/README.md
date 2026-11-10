# Smooth-swap helper split: conditional κ .003637417119941

This exact successor of ToikY's [#7110](https://github.com/CrocSwap/integer-mult-bounds/pull/7110), head `fdb1eb55c4c6604e714c6950e656c67ae0e52370`, improves its conditional claim by **.000000969262210**, from **.003636447857731** to **.003637417119941**. One additional rank-nine helper becomes rank-five and rank-four helpers. The paid profile and signed caller remain unchanged; all 878 added scalar instructions are charged. This is a source-bound conditional construction, not a selected-frontier update or complete multiplication theorem.

## Exact construction and basis choice

Use source cut **37738** (before that zero-based event), pivot **631**, and chart **118**, of dimension five. The helper boundary group has initial chart 3 (dimension zero) and final chart 127 (dimension nine). The cut row and column are

```
a = -14 e1293 + 2 e1294 + e1384 + e631/2 + 3 e632/2
    + e634/2 + 3 e635 - 2 e636,
b = -e1293/16 - e1294/16 + 3 e1295/40 - e631/20 + e632/20
    - e634/5 + e635/10 - 11 e637/40 + 11 e638/40.
```

The complete rational boundary vectors c (113 coordinates) and d (307 coordinates) are in `WITNESS.json`. For the complete prefix P and suffix S, the verifier proves **aP=c**, **Sb=d**, and **ab=cd=1**, including every otherwise-zero public and owned coefficient. Every cut operand is at chart 118; c and d use only the stated helper group. No MOVE is retimed or inserted.

Ali Romman's independent-helper construction uses a boundary basis G with row 631=c and Gd=e631, and a cut basis J with row 631=a and Jb=e631. Emit G⁻¹, the entire prefix, J, the renamed J⁻¹ and suffix, and the renamed G. The old pivot returns at118; fresh independent helper 1483 starts at118 and returns at127. Owned labels shift by one without changing their logical lifetimes. After the entrance basis, the retained pivot contains its own arbitrary independent input at the cut. Replacing that coordinate by the fresh input changes the suffix along b, hence the final boundary along d; G confines the difference to the renamed output. All other helpers and main outputs are preserved.

The new choice is inside the existing basis routine. Since d631=0, the legacy routine swaps with the first nonzero coordinate, d3=677/163840. Its normalization requires SCALE(163840/677), outside the retained 2,3,5 alphabet. The new deterministic rule prefers a nonzero entry whose numerator and denominator use only 2,3,5, then minimizes their combined bit lengths. It chooses **d641=−1/4**, requiring only SCALE(−4). This changes no linear-algebra premise. The entire emitted word is checked against the retained scalar alphabet, including inverse SCALEs. No rational alphabet extension is used.

G has 423 instructions and J has 16. With inverses, the edit adds **872 ADDs and 6 SCALEs**. The program has 72,143 events, 1,484 public fields and 1,084 independent helpers. Owned labels 51, lifetimes 54, peak 43, rises 23 and rise mass 56 are unchanged. Canonical word SHA256 is `3454c4900245ed1814ceeff79a741a45160eb3a93cf8d15f891fe2a67ba036fc`.

## Full price, scalar cost and precision

Per LOCAL, target delta is `{4:+1,5:+1,9:−1}` and paid delta is empty. Across eighteen LOCALs the margin improves by `18(4^p+5^p−9^p)`, strictly positive for every 0<p<1 by strict subadditivity. The full invoice has 117,148 paid and 23,464 productive requests, surplus 1,520 and zero empty-root credit. The complete source-unit ordinary bill is **848,738,320 <10^9**, including the signed caller's actual route charge 1,168,000, recomputed B scalar surcharge, conversions, all new basis instructions and inherited second LAMBDA charge. These units are not literal machine-step counts.

Two rational interval engines certify the new crossing. The independent bracket is

```
(0.00363741711994152260052497254765289,
 0.00363741711994152260052497254765290).
```

The claimed rational is `3637417119941/1000000000000000`. The complete #7110 invoice rejects it. The compiler uses gap 10⁻¹⁷, logarithm power 2233 and H=16480300000000000000000; the paired BIT pin stays .00376669. All compiler and 54 strict plus 4 functional outer inequalities pass. Extra digits of this same root would not be another construction improvement.

`derive_grid.py` derives the denominator LCM from every exact stored prefix coefficient and pre-ADD/COPY product. It finds the same minimal odd scale 1125 and fractional height 24. A distinct fixed-grid integer engine rechecks all divisions and endpoints. Insufficient scale 375 and fractional height 23 are rejection controls. The maximum scaled mass becomes 1636455618522225/16384. The signed caller's precision is freshly reconstructed: context height 450, mass exponent 671 and c=1342. All source coefficients remain within the retained bound; the rational relaxation used in discovery was unnecessary for the accepted construction.

## Reproduction and evidence

```
python3 -I -B research/p104-smooth-swap-split/verify.py
python3.12 -B scripts/research_package.py --package research/p104-smooth-swap-split
```

Expected final line: `PASS_P104_SMOOTH_SWAP_SPLIT 3637417119941/1000000000000000`.

The standalone verifier requires only the standard library and no Git or network. It authenticates the exact seven-file #7110 closure by SHA256 and Git blob, checks nested source manifests, reconstructs #7108/#7109 and the literal #7110 emitter, and verifies the full source invoice. It checks the rational cut, all-input adjoint, independent forward endpoint, newly derived grid, signed caller, ordinary bill, two price engines, BIT source binding, precision and outer gates. The two split chart maps and direct old map are checked on all 512 Gaussian columns with absolute phase; the full width 512 physical word and signed rank-nine caller routes are also replayed. Wrong prefix/suffix, chart, successor frame, deleted corrections and global phase reject. The grid and legacy swap controls are separate.

Every returned receipt field is compared with `RESULT.json`. `--out UNUSED_PATH` writes a new receipt; `--skip-physical` is diagnostic only and is not the registered command. Optimized Python is explicitly rejected because the pinned engines use assertions. `VALIDATION.md`, `REPLAY.txt` and `ENVIRONMENT.json` distinguish actual executions from inherited evidence. This is source-aware reuse of credited engines, not independent human or formal-kernel review.

`DISCOVERY.json` records the bounded search and transfer. The nomination was first found on a separately reproduced chart117 split at local commit d8c7935cb; #7110 had already published that equivalent first gain, so no duplicate PR was opened. The new chart 118 witness was then transferred to exact public #7110 and its entire cut rechecked. Its vectors omit the first split's roles 1285, 1286 and 1482. Alternate nominations are not assumed independent gains. Failed retiming/fusion screens are finite negatives, not optimality claims.

## Remaining obligations and credit

Canonical main at `e54523517d0f03e58352e647c403a5af3e525a57` selects the reviewed #7000 claim .00363005817. The [current application review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md) supplies exact-source occurrence, common-grid scalar, root-boundary and physical-cost substitutions for #7000/#7001, including the BIT ambient 134 repair. That admission does not automatically transfer to this changed native word and signed caller. This package retains the five assumptions `native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`; complete changed-source occurrence/storage/root and physical upper-cost application remain obligations. Finite physical corroboration and a passing source-unit bill do not discharge them. Frozen inputs and selected records are unchanged.

Prepared for dillona with substantial OpenAI Codex assistance; no subagents. Apache-2.0. Credit **Ali Romman** for the independent-helper/basis method; **Jerry Chen / CubeJerry** for counted inventories, retiming, shared-wire composition, caller/BIT and precision engines; **DreamingOfClouds** for the native chain; **ToikY** for #7003/#7004 and the exact signed-caller #7108/#7109/#7110 sources; #7105/#7107 for prior source-bound edits; and all original notices retained in the archive. The new work is the smooth swap choice, this second exact rank-nine witness, complete source-bound verification and explicit grid derivation. No predecessor construction is claimed as newly invented.

## Open next questions

- Recompute residual helper capacity on this exact emitted word using the smooth swap rule. Distinguish repeated nominations of one direction from independent jobs and price all corrections.
- Transfer the current #7000 application proof to the changed native word and signed caller, including actual occurrence allocation, root/storage widths and physical upper-cost constants. The five framework assumptions remain.

Structured blockers are in `TASK.json`; the [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19520521) records current scope and checkpoints.
