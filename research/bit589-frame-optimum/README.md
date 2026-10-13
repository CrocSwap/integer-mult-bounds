# PR589's bit word is exactly frame-optimal (scoped negative result, no new kappa)

**Claim.** Keep PR589's gate sequence, scalar program, start/final frames and the retained totals' COPY frames
(decoder constant 63) fixed. Then no reassignment of gate frames, however many gates change at once, raises the
nine-stage bit saving c = 0.001733427039589844234749. The same holds for PR555's base word. PR589's tuner reached
its word by greedy single-gate moves and makes no optimality claim. This closes the frame-only part of that question exactly.

## Method (`frameopt.py`, standard library only)

1. **Bounds.** A forward pass gives each gate's least legal frame (closure of its operands' current frames).
   A backward pass gives its greatest legal frame (intersection of what its operands may hold later): the final
   frames, targets at frame 0 before the scatter, and pinned COPY frames. Every legal assignment lies between the two.
   The word's own frames do.
2. **Freedom.** Only **159 of 5,472 gates** have any slack. Of those, 155 have exactly two options and the rest have
   5, 6 or 17. Free gates couple only when they are consecutive on a register; a fixed gate in between pins the frame.
   They form **133 independent components** of sizes 1 (119), 2 (4), 3 (9) and 5 (1).
3. **Exact objective.** At z = c the moment is linear in the paid profile:
   Σ_d n_d (d/(mW)) (m/d)^c with m = 64, and the global profile is 288 × local plus a fixed idle remainder.
   So a change raises c only if it lowers Σ_d n_d·d·(64/d)^c. Each component is enumerated exhaustively
   (398 assignments; 55 fail nesting) and scored by a full replay.

## Result

| word | start profile | improving components | smallest strict loss | same-profile alternatives |
|---|---|---|---|---|
| PR589 (`tune/bitE8mut-p111-tuned`) | `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` | **0** | 9.11e−4 | 10 |
| PR555 (`data/bitE8mut-p111`) | `{1:1321,2:1342,3:80,4:47,5:102,6:10,7:18}` | **0** | 9.11e−4 | 9 |
| **positive control**: PR589 with every free gate at its least frame | `{1:1446,2:1326,3:49,…}` | 37 | — | 8 |

The replayed start profiles equal the recorded local histograms. The positive control recovers **exactly** PR589's
profile. PR555 also being frame-optimal is consistent with PR589's gain coming from its two transports (gate-order
changes), not from reframing alone.

## Reproduce

```sh
bash research/bit589-frame-optimum/verify.sh     # ~16 s; last line PASS_BIT589_FRAME_OPTIMUM
```

Python 3.11+, standard library only (CPython 3.12.13 used). Base commit `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The inputs are the committed words `research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz` (PR589) and
`research/e8-bit-p111-tuned/data/bitE8mut-p111.json.gz` (PR555). `verify.log` is the run's output.

## Scope

- **Search class: frame-only.** Gate order, gate operands, the scatter and the COPY frames are fixed.
  Transports, Steinberg rewrites, new helpers, or different retained-total frames are outside this result.
- **Model.** Frames are closed sets of live E8 lines, ranks are computed mod 2^31−1 over integer root-line
  coordinates, as PR589's own tuner does, and the paid profile is PR589's (climbs plus COPY ranks). C gates may take
  any legal frame here, although interface hypothesis H4 fixes them at the full frame. Relaxing that rule only enlarges
  the search, so the negative result holds a fortiori. Hosting and record legality are not modelled for the same reason.
- **κ.** The bit side does not bind the selected κ (complex b ≈ 0.0016644 < c), so this changes no κ.
  It says that future bit headroom on this word must come from gate-order or structural changes.
- This is a finite exhaustive computation on two words, not a statement about other bit words.

## Credit

The PR589 word and tuner are by DreamingOfClouds, on eumemic's PR555 and the PR543/545/510 lineage. Exact
frame-optimality certificates for complex providers exist in #815 and #864; this is the bit-side counterpart with a
different, component-enumeration method. Assignment seed 16 (bit-supplier track). Prepared with substantial AI
assistance (Claude Code, Anthropic). Apache-2.0.

## Maintainer integration refinement

The submitted enumeration compared floating-point moment values. Integration
replaces every decision with outward rational bounds from the pinned base-two
engine and checks the selected minimum against every legal alternative. A
Hadamard bound verifies that the integer root-line minors are smaller than the
rank modulus, so these modular ranks equal rational ranks. The same two optima
and degraded positive control pass. Decimal deltas are display values only.
