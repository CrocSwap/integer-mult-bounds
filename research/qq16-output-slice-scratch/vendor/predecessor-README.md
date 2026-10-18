# Complete local native decoder for the QQ16 selected-sum interface

This package realizes all of [PR2511](https://github.com/CrocSwap/integer-mult-bounds/pull/2511)'s
224 recovered arrays with paid native frames, early-record capture and retirement,
source restoration and explicit output ownership. It composes
[PR2512](https://github.com/CrocSwap/integer-mult-bounds/pull/2512)'s current-frame
L2 maps with the actual identity-chart F0 inverse. The complete **added** local
invoice is **352 native rank mass, 480 native wrappers, 208 full-cover maps and
17,472 real scalar primitives**. The inherited F0/B1 calls retain their costs.

All 224 original logical arrays are returned in **common physical frame F_U1**,
inside 224 owned output banks. All 224 borrowed current X/Y arrays restore.
Sixteen separately owned early X-record banks are captured after F0, held
unchanged through B1 and cleared at the end. At most sixteen local owned scratch
arrays are live per owner. This supplies no net storage saving or physical
retention/tape/precision/hosting bound.

## What the composition adds

Copy the sixteen retained selected X values into their eventual X output banks
and upgrade those outputs once to F_U1. Eight of them serve as the L2 input;
the correction restores them in that frame. The complete X1 vector is now in a
common frame. The actual F0 chart has no owner maps, so a local sixteen-scratch
inverse recovers all original X. Build ordinary Y as -X2 and selected Y as the
paid current selected sum minus recovered X, directly in the final Y outputs.
There is no separate selected-sum output bank. [PROOF.md](PROOF.md) gives the
ordered word, timeline, phase justification and complete local bill.

| Added charge | Count |
|---|---:|
| Positive rank-one / rank-eight children | 224 / 16 |
| Native rank mass / monomial wrappers | 352 / 480 |
| Full-cover maps | 208 |
| Unit / quarter ADDs | 856 / 832 |
| CLEARs | 320 |
| Real scalar primitive allowance | 17,472 |
| Owned output / early-record full-cover banks | 224 / 16 |
| Peak local owned scratch arrays | 16 |

The 17,472 includes 160 scalar primitives for early capture and 32 for final
retirement. Output buffers are exclusively owned and may be cleared; no borrowed
dirty output is silently erased. The two owner-private bodies do not overlap.
R never aliases the final outputs and remains allocated through the post-B1
decoder. Its physical storage across B1 is an explicit unresolved cost.

## Evidence and reproduction

[WORD.json](WORD.json) is the complete added literal word, with a labelled
history boundary for the inherited B1 execution. [RESULT.json](RESULT.json)
contains the exact operator, frame and cost receipts. The checker tracks 240
temporal source symbols (16 earlier, 224 current) and arbitrary owned-buffer
dirt, and compares all 224 output operators to the authenticated PR2511 logical
decoder. The retained logical decoder passes both inverse orders on its actual
224-input/224-observation spaces; its machinery is reused with credit.

Native evidence includes all 104 actual current-frame maps, 281,008 complete
phase-character comparisons, 114,688 signed line-basis columns and the retained
65,536-coefficient rank-eight kernel check. Twelve semantic faults reject,
including capture after B1, missing upgrades, wrong payload shifts, F0 inverse
sign, source restoration, output dirt, borrowed clears and early-record leakage.
Six test groups cover temporal ownership, complete receipts, authenticated code
before execution, read-only Git-free export and overwrite refusal.

From the repository root, standard-library Python 3.12:

```sh
python3.12 scripts/research_package.py --package research/qq16-complete-native-decoder
python3.12 -I -B -O research/qq16-complete-native-decoder/verify.py
python3.12 -I -B -O research/qq16-complete-native-decoder/test_verify.py
```

On Windows, set TEMP/TMP to a writable directory for export tests. Default replay
is read-only; `--write` only creates absent receipts and refuses overwrite.
[SOURCES.json](SOURCES.json) and [PREDECESSORS.json](PREDECESSORS.json) contain
Git/SHA-256 pins. Retained source bytes and source-specific notices are unchanged.

## Limits

This is a complete added local decoder, not a globally admitted controller or
supplier. It neither replays all original native F0/B1 events nor charges those
calls as free. It does not return the original pre-F0 physical frames, claim
minimum children or storage, or infer a new kappa. The early records and 224
owned outputs are explicit resources. Existing helpers/private contracts remain.

## Open next questions

Can a physical caller host the sixteen retained banks, all output banks, maps,
children and local scratch with a favorable complete cost? First assign actual
owners and lifetimes to this literal word, then add stream, precision and output
consumer charges. A local rank-mass invoice does not settle that question.

Can this complete retained-record caller beat an expanded-current-read caller
that directly inverts B1 with zero early retention? Compare the two with exactly
the same output frame, restoration and physical storage contracts. PR2511's
rank-16 lower bound applies only to its fixed compressed observation interface.

## Credit

Prepared by ywz65 with substantial OpenAI Codex assistance, Apache-2.0.
PR2511 at `f40e74a27f7c8781feea06a1571dc99ed5d9a004` supplies the selected-sum
decoder, logical reconstruction and retained PR2456 operator machinery.
PR2512 at `851dd3486a2d0549b51e85978a65ccb4eec619c0` supplies the current-frame
maps and native primitives adapted here. Native methods retain PR2492/PR2468
credit. Credit thakrarsagar/PR2470 for L2, starship-s/PR2443 for the F0/cut
inverse, Ross Richardson/PR2480 for the fixed-L2 retention result, Ali Romman
for QQ16 and the retained native/geometry/supplier lineage. No predecessor
defect, new retention lower bound or independent human review is claimed.
