# Frame reassignment cannot raise the selected X4 complex supplier

**Scoped negative result. No new κ.** Base `f567884aeb8851b6e794af1184119a3bfbe1e631`, where the selected κ = 0.001661634653669567 comes from #799 with #589 on #555 and the complex side binds. Complex-supplier sprint track, OS seed 28 (see `CLAIM.md`).

## Claim

Fix the scalar program of the selected complex word, PR799's X4 word (decompressed content `1e1d99ba…`), which serves all 72 complex calls. Keep its gate list and order, registers, coefficients, start and end frames (so every helper width), cut, centres, target levels, precondition, FULL cleanup and the set of early-cleanup (tail) gates. Let each of its 6,364 A, B and tail gate frames be any subspace of F₂⁹ allowed by the frame contract that `research/gauge44-frames-x/independent/audit_local.py` checks:

- frames are nested along every register, from its start frame to its end frame;
- centres and targets sit at their centre frame and target level at the start of B;
- for each of the 126 low-end helpers, every register in its inverse-row or dirt-column cone ends B inside that helper's end frame.

No such assignment admits the native complex saving

    b_next = 832200139425241163957/500000000000000000000000 = 0.001664400278850482327914,

the next 10⁻²⁴ grid point above the selected endpoint `0.001664400278850482327913`. Every child rank is below 73, so no larger b is admitted either. The pinned outer engine (`outer.py`) requires κ < ε·q = (1−η)q/(1+q) with q = a(1−2η) (`compact_phase_layer`) and a < b (`complex_above_bit`), so κ < b/(1+b). Since b_next/(1+b_next) = 0.0016616346536695670758… lies below the next κ tick 0.001661634653669568, frame reassignment alone cannot raise the selected κ.

## Proof outline

1. **Domains.** Forward joins from fixed starts and start-of-B pins give a lower frame `lo`. Backward meets from fixed ends, pins and cone ceilings give an upper frame `hi`. By induction every legal frame lies in `[lo, hi]`. Here `dim(hi/lo) ≤ 3`: 5,163 gates are forced and 1,201 have 2, 5 or 16 choices (965, 206 and 30 gates). The verifier enumerates each interval and checks its size against the Gaussian-binomial count.
2. **Cost.** A strict climb of dimension d along a register is one paid child of rank d (the `audit_local.py` rule). Climbs telescope along each register, so rank mass is fixed. The native moment then depends on the assignment only through C_d = M_d − d·M₁ with M_d = d·(73/d)^b, and C₀ = C₁ = 0.
3. **LP.** Free gates linked along register chains form 140 components. Each component's local-polytope LP has a variable for every (gate, frame) and for every nested frame pair on each merged register edge: 9,483 rows and 12,019 columns in total. Every legal assignment is a 0/1 point.
4. **Exact duals.** Each dual entry is a linear form in C₂…C₉ with integer coefficients. The verifier rebuilds every row, column and cost from the word, then checks every reduced cost. 8,582 are identically zero, and 3,437 are strictly positive under outward rational bounds from both pinned engines (`moment.py`, Mercator series, and `base_two_moment.py`, atanh series). In every component the dual objective equals the selected assignment's cost as an exact coefficient identity. By weak duality the selected frames minimise the local moment.
5. **Global step.** 72 times the local profile plus the remainder {1:1, 3:1, 44:1, 48:2396} reproduces the pinned global profile. Both engines put the global moment strictly above 1 at b_next and strictly below 1 at the selected endpoint. Each call costs at least the selected word, so any reassignment, even a different one in each call, has moment above 1 at b_next.

The model relaxes the centre equality at the start of B to a charged climb, and it omits native-chain conditions beyond `audit_local.py`. Both choices only enlarge the feasible set, so the bound also covers the stricter native contract.

## Cross-check against the independent auditor

`crosscheck.py` draws 12 random legal reassignments (40 frame changes each, seed 28), writes each into the word with the profile the model predicts, and runs the pinned `audit_local.py` unchanged. All 12 pass its exact two-orientation scalar replay and its frame, centre, target and cone checks with the predicted profile. All 12 are strictly costlier at b_next. The auditor refuses a frame below the forward join and a mismatched profile. Receipt: `data/CROSSCHECK.json`.

## Reproduce

Python 3.11 or newer, standard library only, assertions on, from the repository root:

```sh
python3 -B research/complex-x4-frame-bound/verify.py --controls
```

Expected final line: `PASS_X4_FRAME_ASSIGNMENT_EXCLUSION controls=6/6`, in about 5 seconds. The six controls must each be rejected: a dropped component, an inflated dual, an omitted frame choice, the accepted endpoint in place of b_next, a legal but costlier baseline, and a changed word. `RESULT.json` is the receipt of this command.

Optional commands:

```sh
python3 -B research/complex-x4-frame-bound/crosscheck.py      # about 1 minute
python3 -B research/complex-x4-frame-bound/verify.py --word /tmp/x4/jx/FULL-WORD.json.gz
```

The second form checks a freshly rebuilt word from `research/gauge44-frames-x/README.md`; the content hash must match. By default the verifier reads the retained replay archive `research/community-frontier799-audit/pr799-replay.tar.gz`, whose hash the maintainer's integration receipt records.

`gen_duals.py` nominated the duals with HiGHS (highspy 1.15.1, SciPy 1.18.1, NumPy 2.5.4, Python 3.12.14). Two runs wrote byte-identical `data/DUALS.json.gz`. The generator is not part of the proof: `verify.py` imports no solver and trusts no floating-point value.

Checked on Windows 11 with CPython 3.12.14 and 3.14.7.

## What this leaves for the complex track

Per call, 1,745 of the 2,548 rank-1 children, all 56 rank-5 children and the eight centre descents lie on register edges between forced frames. Any κ gain from this supplier needs a scalar change (read sets, gate order, tail membership), new start or end frames (entrances, low ends, widths), or a change to owners and hosting. Frame re-choice on X4 is closed at b_next.

## Scope

Not covered: scalar rewrites, gate reordering or read-set exchanges; moving gates into or out of the early cleanup; entrance promotions or any other start or end frame change; owners, hosting and the finite invoice; the bit supplier; other outer theorems. The exclusion holds at b_next for the fixed word. It does not replay the native construction chain. The inherited all-size compiler, common-label and mutable-source realization, whole-call hosting, precision and tape, and analytic hypotheses remain. This is a finite certificate, not a Lean proof.

## Prior work

- chafreaky's #557 (`research/frame-domain-ceiling`) introduced complete F₂ domains, this LP relaxation and symbolic exact duals, for the PR551 word.
- ntedvs's #776 (open) applies the method to #626's jp8 and ck words, with tail frames outside its scope.
- Rohansguliani's #815 (open) solves PR699's SW4 word and #626's words with floating-point LP and CP-SAT, with tail frames fixed, and rediscovers #741.
- JointXF reported in #799 that FrameCoal's optimiser reaches the X4 profile. The #799 review keeps that as a search report. This package corroborates it with an exact certificate.

This package is a new implementation for the native gauge44 word format. Unlike the earlier packages, it frees the 163 early-cleanup frames and derives the low-end cone ceilings from the exact prefix map.

The X4 word is Jeremy Kothe's #799 construction on chafreaky's #741 frames, BRoute's SW4 exchange, BlockInvert's promotions, the p6n and no-triangle layers and icekylinx's #645 gauge44 factory, with the lineage recorded in `research/gauge44-frames-x/README.md` and `CONTRIBUTORS.md`.

Prepared for @navinor with substantial assistance from Claude Code. Apache-2.0. No independent human review.
