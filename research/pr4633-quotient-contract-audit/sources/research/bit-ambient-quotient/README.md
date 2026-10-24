# Conditional kappa = 0.012401 (BIT-limited, +310.6%): BIT supplier to 0.012401086416 by an ambient quotient (kernel 150)

**Scoped finite construction with exact local replay evidence. Not a multiplication theorem.**

With the complex supplier at 0.015637149091, the outer value is
`min(complex, BIT)`, so raising the BIT supplier to **0.012401086416** raises the
outer kappa from 0.00302015 to **0.012401**, a **+310.6%** gain limited by the BIT
side itself.

The BIT supplier's local word is PR589's E8 word: `h = 8`, `V = 111` roles per
side, `R = 439` helpers, 661 roles, 636 frames and 249 records. Frames are stored
by annihilator rows, so a frame is the GF(2) nullspace of its rows.

For a nonzero kernel `v` with lowest set bit `j`,

```
phi(x) = drop_j( x xor v when bit_j(x) is set else x )
```

is linear and surjective onto `F2^7` with kernel `span{v}`. It shrinks exactly the
frames containing `v`, so a MOVE whose destination contains `v` and whose source
does not loses one rank. Frames with the same image are identified, the helper
finals are restored to the full `F2^8` (the contract requires every helper to be
physically `D_I8`, and the tensor block to stay 7), and every MOVE rank is
recomputed from the new dimensions.

The kernel is chosen by replay, not by arithmetic: `scan_kernels.py` builds,
replays and prices all 255 directions. **All 255 replay, and `150` has the highest
admissible kappa.**

| quantity | emitted | quotient |
|---|---:|---:|
| frames | 636 | **117** |
| frame dimensions | see source | `{0:1, 1:16, 2:19, 3:11, 4:7, 5:41, 6:20, 7:1, 8:1}` |
| main widths | `{7: 222}` | `{6: 107, 7: 105, 8: 10}` |
| helper widths | `{8: 439}` | `{8: 439}` (start dim 0, final dim 8) |
| paid profile | `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` | `{1:1198, 2:1255, 3:207, 4:86, 5:41, 6:23, 7:1}` |
| paid rank mass | 5,129 | **5,023** |
| rank surplus | 753 | **2,661** |
| **BIT kappa** | **0.003464248972** | **0.012401086416** |

`+0.008937`, **+258.0%** on the BIT supplier. Both screen constraints hold at the
new kappa.

## Why the quotient is legitimate

The quotient recognises a one-dimensional gauge direction in the ambient: the
frames containing `v` lose exactly one dimension, and nothing else moves. The
shipped local record interpreter then replays the rewritten word unchanged:

| check | result |
|---|---:|
| forward replay | 24,305 ADDs, 9 COPY episodes, all 661 endpoints exact |
| reverse replay | 24,305 ADDs, 9 COPY episodes, all 661 endpoints exact |
| arbitrary input columns, both directions | exact |
| owned COPY cleanup | exact |
| helper finals at dim 8 | 439 of 439 |
| helper starts at ground | 439 of 439 |
| source word reproduces the declared bill | `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` |
| emitted BIT kappa reproduces the frontier | 0.003464248972 |

The last two rows are the calibration: replaying the *pinned source word* through
the same interpreter reproduces the declared local bill exactly, and the emitted
invoice's screen reproduces the frontier's BIT kappa to twelve digits. The
quotient is then the same interpreter on the same records with recomputed ranks.

**The block stays 7.** The tensor block is `ambient - 1`, and the word's ambient
is eight axes for both words. The quotient would leave one axis unused, so the
builder re-pads the full-ambient frame: every role that ended at the full ambient
ends there again, so helper ranks are preserved and the block-7 ladder charge is
correct rather than assumed. `verify.py` asserts `ambient_dim == 8` and that no
helper final is below 8.

## Evidence and reproduction

```sh
python3 -B research/bit-ambient-quotient/build.py          # writes the artifact
python3 -B research/bit-ambient-quotient/verify.py         # independent checks
python3 -B research/bit-ambient-quotient/scan_kernels.py   # the kernel choice
```

`verify.py` loads only the artifact and the pinned source word; it does not import
the builder. The two-constraint screen is inlined (tail offset `1/5`, cutoff `20`,
gamma `0.97`), so no file outside the base commit is required.

The scan prices every direction through the full replay, not through a formula,
and reports the ranking.

## What is not claimed

- **The admission parameters are declared constants.** `atom 0.004`,
  `ordinary 0.0034364` and `admitted 0.0034` are literals in
  `research/query-thinned-controllers/verify.py`; they are not derived from the
  supplier word and are not raised here. The 0.012401 outer value requires them
  raised to match a 0.0124 supplier — the same kind of contract change as
  `controller.py:152` for the mixed main widths.
- **The frame charts collapse**: 636 distinct frames become 117. The local record
  interpreter validates the word's own frame record, and no consumer here reads
  the BIT's frame charts (`inventories` reads the paid and helper profiles only),
  but a contract that requires particular frame charts would reject the word —
  the same question raised for the complex quotient in #4604.
- This is not a multiplication theorem and not a Lean verification.
- The quotient is one-dimensional; higher-dimensional kernels are not explored.
- Only PR589's E8 word is exercised.

## Open next questions

1. **Does a two-dimensional kernel replay?** All 255 one-dimensional quotients
   replay and land between 0.0122 and 0.0124; a plane could shorten more MOVEs.
2. **Which consumer, if any, requires the frame charts?** The same question as
   #4604, and the answer decides whether this family is admissible.
3. **What admission parameters correspond to a 0.0124 supplier?** The declared
   `atom 0.004` and `after_cover 0.00345` are far below the new supplier kappa.
4. **Do the other `h = 8` words admit the same quotient?** 292 such words exist in
   the tree with different frame inventories.

## Attribution

Built on PR589's regenerated E8 word
(`research/kappa-rebuild/bit/sources/pr589-regenerated`) and the local record
interpreter and declared bill of `research/kappa-rebuild/bit/mixed_productive_bit.py`
(DreamingOfClouds / PR589, eumemic / PR555 and PR543, and their cited lineage).
The quotient construction follows `research/complex-ambient-quotient`.

Apache-2.0; substantial AI assistance.
