# BIT supplier 0.032249423394893 by a three-dimensional ambient quotient

**Scoped finite construction with exact local replay evidence. Not a multiplication theorem.**

**Frontier base: 0.012401086416** — this package's own one-dimensional quotient, the
value the BIT branch carried before this change. The three-dimensional quotient moves
the BIT supplier from `0.012401086416` to **`0.032249423394893`**, a **+160.05%** step
on that base, and from the emitted word's `0.003464248972024` to that value,
**+830.92%** in total.

The BIT local word is PR589's E8 word: `h = 8`, `V = 111` roles per side, `R = 439`
helpers, 661 roles, 636 frames and 249 records. Frames are stored by annihilator
rows, so a frame is the GF(2) nullspace of its rows.

For a kernel subspace `K` of dimension `k`, the map

```
phi(x) = (r_1.x, ..., r_(8-k).x)      over a basis r of the annihilator of K
```

is linear and surjective onto `F2^(8-k)` with kernel exactly `K`. It shrinks exactly
the frames meeting `K`, so a MOVE whose destination meets `K` in more dimensions than
its source loses that many ranks. Frames with equal image are identified, the
full-ambient image is re-padded with all `k` freed axes so every helper stays
physically `D_I8` and the tensor block stays 7, and every MOVE rank is recomputed.

## The kernel dimension is the lever

| kernel dim | kappa | vs base 0.012401086416 |
|---:|---:|---:|
| 1 | 0.012401086416 | — (the base) |
| 2 | 0.021785831250 | +75.68% |
| **3** | **0.032249423394893** | **+160.05%** |
| 4 | 0.017525188018 | +41.32% |

The submitted word uses `K = span{150, 102, 255}` (dimension 3, quotient width 5).
Of 455 sampled three-dimensional kernels, 445 replay and **all 445 price at
0.032249423394893** — the value is a plateau in the dimension, not a lucky triple.

| quantity | emitted | quotient |
|---|---:|---:|
| frames | 636 | **65** |
| frame dimensions | — | `{0:1, 1:13, 2:8, 3:25, 4:16, 5:1, 8:1}` |
| main widths | `{7: 222}` | `{4: 103, 7: 70, 8: 49}` |
| main rank mass | 1,554 | **1,294** |
| helper widths | `{8: 439}` | `{8: 439}` (start dim 0, final dim 8) |
| helper rank mass | 3,512 | 3,512 |
| paid profile | `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` | `{1:1020, 2:495, 3:75, 4:442, 5:143, 6:4, 7:12, 8:2}` |
| paid rank mass | 5,129 | **4,842** |
| rank surplus | 753 | **5,919** |
| **BIT kappa** | **0.003464248972024** | **0.032249423394893** |

## Why the quotient is legitimate

A frame meeting `K` in `j` dimensions loses exactly `j`, and nothing else moves, so
no MOVE is lengthened: `dim phi(F) <= dim F` for every `F`. The shipped local record
interpreter then replays the rewritten word with no change of its own:

| check | result |
|---|---:|
| forward replay | 24,305 ADDs, 9 COPY episodes, all 661 endpoints exact |
| reverse replay | 24,305 ADDs, 9 COPY episodes, all 661 endpoints exact |
| arbitrary input columns, both directions | exact |
| owned COPY cleanup | exact |
| helper finals at dim 8 | 439 of 439 |
| helper starts at ground | 439 of 439 |
| source word reproduces the declared bill | `{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}` |
| emitted BIT kappa reproduces the frontier | 0.003464248972024 |

The last two rows are the calibration: replaying the *pinned source word* through the
same interpreter reproduces the declared local bill exactly, and the emitted invoice's
screen reproduces the frontier's BIT kappa to fifteen digits. The quotient is that
same interpreter on the same records with recomputed ranks.

**The block stays 7.** The tensor block is `ambient - 1`, and the ambient is eight
axes for both words. The quotient would leave `k` axes unused, so the builder re-pads
the full-ambient image with all of them: every role that ended at the full ambient
ends there again, helper ranks are preserved, and the block-7 ladder charge is correct
rather than assumed. `verify.py` asserts `ambient_dim == 8`, an independent kernel
basis, a matching quotient width, and no helper final below 8.

## Reproduce

```sh
python3 -B research/bit-ambient-quotient/build.py          # writes the artifact
python3 -B research/bit-ambient-quotient/verify.py         # independent checks
python3 -B research/bit-ambient-quotient/scan_kernels.py   # the dimension ladder
```

`verify.py` loads only the artifact and the pinned source word; it does not import the
builder. The two-constraint screen is inlined (tail offset `1/5`, cutoff `20`,
gamma `0.97`), so no file outside the base commit is required.

## What is not claimed

- **The outer kappa does not move in this package.** The outer value is
  `min(complex, BIT)`; the complex supplier sets it.
- **The frame charts collapse**: 636 frames become 65. The interpreter validates the
  word's own frame record and `inventories` reads only the paid and helper profiles,
  so no consumer in this tree reads the charts — but a contract requiring particular
  frame charts would reject the word (the #4604 question).
- Kernel dimension 4 replays but prices worse at 0.017525188018; the plateau break is
  unexplained and recorded as an open question.
- This is not a multiplication theorem and not a Lean verification.
- Only PR589's E8 word is exercised; 292 other `h = 8` words are untested.

## Open next questions

1. **Why does dimension 4 fall back to 0.017525188018?** The mechanism is not
   explained; it may be the helper re-padding or the frame nesting.
2. **Can the complex supplier follow?** It needs
   `research/fresh-helper-boundary/native.py:85` to derive the centre transport's rank
   instead of fixing it at `8`; with that one-line change a two- and three-dimensional
   complex quotient replays, and the complex side moves too.
3. **Which consumer, if any, requires the frame charts?** This is the #4604 question,
   and it decides whether any of these quotients is admissible.
4. **What admission parameters correspond to a 0.032249423394893 supplier?** The
   declared literals in `research/query-thinned-controllers/verify.py` are far below
   it.

## Attribution

Built on PR589's regenerated E8 word
(`research/kappa-rebuild/bit/sources/pr589-regenerated`) and the local record
interpreter and declared bill of
`research/kappa-rebuild/bit/mixed_productive_bit.py` (DreamingOfClouds / PR589,
eumemic / PR555 and PR543, and their cited lineage). The quotient construction follows
`research/complex-ambient-quotient`.

Apache-2.0; substantial AI assistance.
