κ = 8.01083628465007e-4

# PR #346's w3 bit word with Jacob Sussman's E8 unit as the complex supplier

A conditional finite construction with **κ = 801083628465007/10¹⁸ ≈ 8.01083628465007 × 10⁻⁴**: +1.07 % over PR #346
(7.92580093369946e-4), +0.96 % over the best κ in an open PR title at packaging time (#350, 7.93469326753735e-4), and
+4.82 % over PR #315. The bit side now binds. The complex supplier is 9.3 % above it.

| side | supplier | coarse saving |
| --- | --- | ---: |
| bit | PR #346's word, unchanged (PR #325's p10b word + w3 Design T + twin condensation) | c = 32069035133443/(4·10¹⁶) ≈ 8.01725878336075·10⁻⁴ |
| complex | Jacob Sussman's E8 unit `gcert1-e8-r783` (h = 9, v = 120, R = 783, m = 45) | b = 876248285600677/10¹⁸ ≈ 8.76248285600677·10⁻⁴ |

## What changed

Only the complex supplier. Every complex program in this repository so far has been a paired-cube program: the star
scatter with h centres of rank h − 2, at p = 10 or 11. On 10 October Sussman published a new gcert/1 unit on the
E8 label family (label width 9, 120 source/target pairs, block size 45, 783 helpers). It scatters through eight
totals held at the full frame, using an explicit scatter table. It is the certificate behind his Lean theorem
`wht_main_block_B2Ge8x`:

    ∃ solve W, WHTProgram solve W ∧ WHTTimeBoundsAt (1 - 8762479/10^10) W

That theorem is kernel-checked in his repository (jacobalansussman/wht-power-saving-lean at `9c94857`, `VERIFY.md`).
His README notes that this repository's complex side is the quantity of that theorem. Its five-stage B2 price is
the same formula the complex checks here use (H₅ = 5·H + 2v at ranks 2h−2, h−1, 2h+2, 4; W = 4v + R). The exact
coarse saving under PR #315's two moment engines is b above, consistent with his Lean figure 8762479/10¹⁰ from above.

It also fits PR #315's finite bridge with more room than the p = 10 program:

| quantity | E8 | p = 10 paired cubes (PR #346) | bridge limit |
| --- | ---: | ---: | --- |
| m | 45 | 100 | the bridge text assumes m ≤ 72; the guard recomputes every bound for the actual m |
| maximum child / half-shrink | 20 (40 < 45) | 42 (84 < 100) | 2·max child < m |
| external row coefficient | 11,119 | 15,125 | < 20,161 |
| induction gap | 49·B | 115·B | ≥ 1·B |

## Complex checks

`code/complex/certify_complex.py` (step 5 of `verify.sh`, about 3 seconds):

1. **PR #315's portable complex checks, generalized** (`portable_complex.py`, `code/`). These are the checks that
   PR #346 ported to p = 10:
   - Sussman's `gx.check1` with the exact scalar identity, and his `gxcore` mirror, with flipped-sign controls;
   - every label and paid child;
   - both scalar words and temporary lifetimes;
   - the five-window splice with all mutation controls rejected;
   - the finite precision guard.

   The paired-cube assumptions are now read from the certificate, the way `gx.scat_row` reads them
   (`code/scatter.py`):
   - the scatter is a table or the star rule;
   - the number of retained totals is any count up to h, the reserved centre slots;
   - each centre child has the rank of its total's frame;
   - final climbs are exactly the helpers not already at the full frame after phase B, and no x or y role (for E8,
     783 − 8 = 775).

   All counts are pinned in `pins-e8.json`.
2. **Lean binding.** Sussman's own generators are vendored unchanged at `9c94857` (`inputs/e8/tools/`). From the
   vendored certificate they regenerate the 24 Lean modules and the comparator configuration of
   `wht_main_block_B2Ge8x`, and all 25 must equal his files byte for byte (`RESULT: REPRODUCED`). No Lean is run
   here.
3. **Stand-alone replay.** His `tools/e8/replay.py` shares no code with gx. It must accept the certificate at
   figure 8762479.
4. **Exact b**, from the guard's own five-stage histogram (tally 56,715, deficit 120), with both rational moment
   engines and the 10⁻¹⁶ bad-class fallback. The next 10⁻¹⁸ grid point must fail.

**Regression of the generalization.** `python3 -B code/complex/regress_pr346.py <#346>/research/w3-p10b-complex-p10`
runs the original and the generalized checks on PR #346's own p = 10 program and pins. They agree byte for byte on
both scalar schedules, both splice programs, the primitive expansions, the ledger, the labels and the precision
guard. The generalized run only adds the keys `centres` and `centre_ranks`.

## Bit word

The bit word, its data and its checks are PR #346's, byte-identical (`data/bit/`, `code/builders/`, `code/checkers/`,
`code/pricing/`, steps 1–4 of `verify.sh`). `SOURCE-pr346.json` records the git blob id of every file carried over
unchanged from PR #346 at `11b4de5` (73 files), the 11 edited files and the 32 not carried over (PR #346's p = 10
complex producer, its modules, program and receipts). Step 0 of `verify.sh` checks the blob ids (`code/provenance.py`). The vendored base snapshot (PR #325 p10b, root 7.70276909563042·10⁻⁴) is
rebuilt through Design T and twin condensation to the hash-checked final word (root 8.01726·10⁻⁴). On that word
`verify.sh` runs:

- PR #266's official legality and five-stage columns checkers;
- exact rational nondegeneracy and the prime-witness rule on the 320 new frames;
- the width-100 bank tiling.

`code/pricing/certify_bit.py` then certifies c and runs PR #315's outer assembly with the E8 b. All 47 strict
constraints are positive (including `complex_above_bit` and `leaf_saving_above_bit`), and the adjacent 10⁻¹⁸ κ is
rejected.

## Verify

    bash research/w3-p10b-e8-complex/verify.sh /tmp/w3-p10b-e8-verify

About five minutes. It needs Python 3.12+ with `requirements.txt` (numpy, mpmath), g++ (C++17) and Boost headers. The
final line is:

    PASS conditional kappa = 801083628465007/1000000000000000000 = 0.000801083628465007

Receipts of this run are in `receipts/`:
- `complex-guard-e8.json`: the full complex guard output;
- `kappa.json`;
- PR #346's official-checker receipts, unchanged.

## Open obligations

- **Bit side.** All of PR #346's open obligations remain unchanged: PR #310's native downstream chain; PR #315's
  scalar/prime/finite stages, replaced by the official cohort checkers; the inherited row constants 9909 + 252;
  every inherited interface of PR #315/#325.
- **Complex side.**
  - The generalization of the portable complex checks to table scatter and full-rank totals is new code, checked by
    regression against PR #346 and by the E8 run.
  - PR #200's complete complex checker and PR #194's contract, which #346 ran on its #202-tree program, work on
    that producer's format and are not run on E8. In their place stand Sussman's Lean theorem (checked in his
    repository, not rebuilt here), his two checkers, his independent replay, and the byte-for-byte Lean-data
    regeneration.
- This is a conditional finite construction, not a formal verification of the multiplication theorem.

Because the bit side binds, a bit-side improvement on this word now raises κ until it reaches the E8 complex
saving, about 8.76·10⁻⁴.

## Credits

- Complex unit, Lean theorem, generators and replay: Jacob Sussman (wht-power-saving-lean). His unit uses devices
  from this repository: jamesyc #124 and eumemic #143; Chafik Boukhalfa #200/#233; icekylinx #184, carried in
  ikeboy's #191/#193.
- Bit word and package base: LJH-217 (#346), on DreamingOfClouds' #325/#315 and utcorvusvolat-dotcom's w3 work
  (#310).
- Official checkers: #266.
- Complex checks: the #315/#304/#256/#233/#202/#200/#194/#184 lineage.

See `NOTICE.md`.
