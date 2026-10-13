# Proof note: two new A-gate primitives in the `cold_end` build step (ColdBeyond, final = v3)

v3 = per factory block a second cold low-frame end (S b.9 at U_b, no lifted partner; absorption p5 += -1/2 S.5) on top of
#604's S b.10 end, plus ColdSupply's E1 entering pair (608/610 at a hyperplane, published as #615), on jp8, ck and atm3.
Profile per word vs #604: {1:+20, 2:-4, 6:-14}; widths 9->4 x14, 8->7 x2.  LP screen (kscreen, #610 dispatch
jp8x71+ck): v2 0.0016345792 = +0.553% over the like-for-like screen base 0.0016255869 (the #610 literal is
0.0016253652); v3 0.0016347434; free dispatch 0.0016353016.

## What changes
#604's `cold_end` step allowed exactly one change to section A: a rank-0 premix on cold helpers at the head of A
(`y['A'] == premix + x['A']`, every premix register a helper at its start frame). This package widens that allowlist
(`code/build_cold_end.py::apply`, and independently `verify.py::cold_end`) by two primitives. No audit is weakened;
every downstream check runs unchanged on the resulting word.

1. **Premix target writes.** `['add', t, k, p, q, []]`, with `t` a target, `k` a cold helper, and frame `[]`. These are
   placed in the premix, so they run after the entry adapters and paid wrappers.
2. **Forward absorptions.** `[[i, ['add', q, g, p, s, F]]]`, inserted into A right after input-A gate `i`, with three
   conditions:
   - **(a)** neither register is a target;
   - **(b)** `q` is dead from then on: no later A, cut or B gate touches it;
   - **(c)** after gate `i`, both `q` and `g` already sit at frame `F`.

## Why the forward computation is unchanged
- **Absorption.** The gate changes only `q`'s value, and `q` is never read again in A, cut or B (condition b). So every
  register that is ever read afterwards has its old forward value. That covers targets, centres, live helpers and
  live ports. Only `q`'s end-of-B value changes, and `q` is a non-target, so the cleanup is responsible for it.
  - Condition (c) makes the gate frame equal both registers' current frame, so no climb happens.
  - The paid profile and all frame chains are therefore identical to the input's. `chain_profile` recomputes them,
    and the transport's `climb` re-asserts monotonicity.
- **Target write.** The gate reads a cold helper and writes a target. The transport assertion "no non-target register
  reads a target in A/B" still holds.
  - Targets start at level 0, which is frame `[]`, so the gate is rank 0. The transport still asserts at the start
    of B that every target sits at its level.
  - Its scalar content is the same kind of operation as a zero-frame compensation gate, `target += d·helper`.
  - The only difference is placement: it runs after the cold wrappers and the helper premix. So it can cancel,
    inside main, the dirt that an ended helper's premix column `c_h` delivers to targets. The carrier `k` has unit
    weight on `h` and zero weight on every other ended helper.
  - The verifier's own zero-frame compensation, recomputed from main, then contains no term on an ended helper. The
    transport asserts this: no precondition or compensation gate touches a cold-ended helper
    (`hpe_audit_and_transport.py:157`).
  - **That assertion is THE guard for target writes.** A doubled, dropped or retargeted target write leaves the scalar
    program exact (the compensation simply absorbs the difference), so exactness alone would accept it. It is rejected
    only because the recomputed compensation must then read the ended helper, which :157 forbids. Every target-write
    mutant below is rejected by :157 (the entering-helper one by the frame climb).

## What is re-verified on the resulting word (unchanged code)
- **Scalar replay.** `hpe_audit_and_transport.py` runs the exact arbitrary-dirt endpoint replay of precondition +
  compensation + main + tail + refactored cleanup in both orientations. It also checks dyadic primitives, the frame
  chains, the end-of-B row/column cone pre-check for every low-frame end, and the paid profile.
- **Local replay.** `hpe_emit_local.py` and `hpe_audit_local.py` run the event-level independent replay and the
  wrapper-order check: every scalar on a wrapped helper lies between its pre and post adapters.
- **Wrappers.** `hpe_adapters_local.py` checks Lemma A wrappers for `(0, U)`.
- **Phases.** `phases_full.py` checks all phase edges.
- **Global stages.** Binding, the owner audit, the invoice, both moment engines and the assembly controls all run.

## Lean coverage
Both primitives are ordinary section-A gates of the native word: frame-`[]` adds and an add at its registers' common
frame. The HPE / cold-end Lean statements (PR593, PR599) are about the helper labels, tails and terminal frames, and
none of those change. The ended helpers end at `U_b` (dim 4) with `(0, U)` wrappers exactly as in #604. No new Lean
rule is needed. The change is to the build-step allowlist only.

## Negative controls (`code/cold_end_controls.py`; all must be rejected by the transport)
#604's 14 controls, ColdSupply's 6 entering-end controls (E1), plus these 12 (32 in total):
- target writes moved into the zero-frame precondition (before the wrappers);
- one target write dropped;
- a target-write coefficient doubled;
- a target write reading an entering helper;
- a target write reading the same factory slot of another block, which carries none of the ended helper's dirt;
  - (Reading another register with the same weight on `h` is a valid variant: it is accepted, which is why this mutant
    was chosen instead.)
- absorption dropped;
- absorption coefficient doubled;
- absorption placed before the absorbed register's last kernel write;
- absorption placed while the absorbing register is still live;
- absorption into a centre (a live register read by the cut);
- absorption at a lower frame;
- absorption at a higher frame (FULL).

In addition, `verify.py::cold_end` independently checks the allowlist conditions:
- target writes are frame-`[]` adds from a cold, non-entering helper;
- each absorption satisfies conditions (a)–(c): unique, in-range insertion indices; frames compared as spans and
  seeded from the port / start_extra frame when the register has no earlier A gate;
- `y['A'] == premix + (x['A'] with the absorptions inserted)`.

## K-triangle provider words (complex-571-cold14-k492)

The provider words are produced by search-side constructors. None of them is trusted. What is trusted is the exact audits that certify every word. Every intermediate word also has its content hash pinned in `data/SPEC.json`. This note says what each constructor does, and which independent check certifies its output.

### 1. `k_triangle`: `code/construct_k_triangle.py`

**Origin.** This is PR531's `code/construct_504.py` (pinned source `direct_delivery`, file hash pinned), extended with AtomScout's leaver-read K-triangle atom. Every assertion of PR531's constructor is kept, with 504 replaced by NH = 504 − 3·|triangles|.

**The atom.** A coordinate pair p is *full* when the selected partition contains p in all three blocks containing p. Then both triangles (p, ±1) are consumed only by K-coordinates. For a scheduled triangle:
- the three face packets are never formed and never copied;
- each K-coordinate target t first reads the leaver that is its K-basis own token, `own_rows[t]`. The constructor checks this is the same register and coefficient as in the 504 word;
- t then reads the four unformed leavers (butterfly outputs) of the other two faces. Each is read with coefficient `coef·alpha`, from the 504 word's face-packet request.

The read order (`data/TRI-SCHEDULE.json`) keeps every target frame inside hyper(P_t); the constructor asserts this for each read.

**Exactness.** The constructor asserts the following, exactly as PR531 does:
- the side identity `rows[v+t] == {s: −G[t][s]/2}` for every target t;
- the clean-column replay `A + cut + B + cleanup = identity` on the 2v + NH columns;
- the rank-mass identity Σ r·H_r = 9·NH + 240·8 + 72.

**Helper map.** Each allocation advances the 504 numbering. A packet copy that the schedule never forms advances it without allocating. `HELPER-MAP.json` is therefore the 504 → NH register map: registers below 448 keep their ids, and the 12 removed packet copies [448, 458, 460, 470, 472, 482, 580, 590, 592, 602, 604, 614] have no image.

**Controls in `verify.py`.**
- PR531's unchanged constructor reproduces PR552's `RAW504.json.gz` byte for byte in content.
- This constructor with an empty schedule also reproduces it, and gives the identity map.
- With the package schedule it gives R = 492 = 504 − 3·4 and a 12-entry removed set, and the map's hash is pinned.
- Independently (AtomReviewer), the 492 raw word passes vendor531's and the generalised `audit_and_transport` (exact forward and inverse-transpose replay of every column, native frames), and an independent mod-p replay.

### 2. `port_stage`: `code/build_port_stage.py`

**What it replays.** A stage I4 → O4 of a 504-helper chain is one of:
- PR558's reconstruction raw504 → promoted;
- PR571's prefix word;
- PR568 `cold_kernel` / `multicut`;
- PR575 `joint_prefix`;
- PR569 `promote`, PR568 `greedy_kernels`, PR583 `frame_coalesce`, and this lineage's `gate_move_coalesce`.

Each stage is rebuilt in the same run from pinned sources, with its own constructor, omission controls and content pins (`build.shadows`).

**How it is replayed.** The stage is replayed onto the K-triangle word I8 at the matching chain point:
- I4 and O4 are renumbered through the helper map, dropping gates on removed registers;
- gates are aligned by scalar operation (gate without frame);
- in O4 order, matched gates come from I8, with O4's frame where the stage changed it;
- stage-introduced gates come from O4;
- the K-triangle reads, which have no 504 counterpart, stay after their I8 predecessor's image;
- start_extra and target_levels changes are replayed;
- the cleanup is rebuilt with the inherited inverse rule.

**What certifies the output.** The port is a transfer heuristic and claims nothing by itself. `verify.py` certifies every ported word in four ways:
1. It runs the generalised native audit `code/hpe_audit_and_transport.py`: status PASS_CHANGED_WORD_ALL_COLUMNS_AND_NATIVE_FRAMES, exact forward and inverse-transpose replay of all 2v+R columns with arbitrary dirt, native monotone frame chains, and the entrance and paid-profile census.
2. It checks that only A, B, cleanup, start_extra, target_levels and the report changed, and that R is unchanged.
3. It pins input, shadow input, shadow output and output by content hash.
4. Localization later re-derives everything again: native chain, independent local replay with its negative controls, wrappers, and all phase edges.

So a wrong transfer can only fail closed.

### 3. `frame_regroup`: `code/build_frame_regroup.py`

This is PR583's `build_frames.py`, with the required per-change profile delta read from the recipe instead of fixed at {1:−2, 2:+1}. The constructor checks the following:
- scalar operations, every field outside A/B/report, helper widths and all initial helper responses are unchanged;
- entering helper responses are zero;
- the cleanup already follows the inherited inverse rule, which uses only FULL frames;
- every change has the recipe's exact sequential delta, and the profile matches the recipe before and after;
- frame-chain monotonicity holds (gk_word.profile asserts it);
- the controls reject every omission and every FULL over-promotion (48 controls for 24 changes).

`verify.py` then repeats `frame_coalesce`'s independent comparison: only the recipe gates' frames change.

The recipe's 24 changes coalesce the K-read gates of the eight K-coordinate targets, each with delta {1:−3, 2:+3, 3:−1}. Port480's `frameopt.py` found them by maximising Σ d·ln d.

### 4. `hyperplane_end` and `cold_end`

These steps run the package's unchanged B3 constructors, controls and independent comparisons:
- `build_hpe.py` / `hpe_controls_atc.py`: 34 candidates, all admissible;
- `build_cold_end.py` / `cold_end_controls.py`.

The cold_end recipes come from ColdBeyond's `construct2` with single-unit blocks (Port480 `construct2b.py`). Each recipe has:
- S b.10 cold ends in all 14 blocks;
- S b.9 second cold ends with dead-port absorption in blocks 3–10 only. In blocks 0–2 and 11–13 the K-triangle words do not admit them;
- the E1 entering pair.

The allowlist and its proof are B3's `PROOF-NOTE.md`, unchanged.

### Reproduction
Every intermediate word was rebuilt outside `verify.py` (scratch `Stack492/rebuild.py`) and inside the strict run. Each one equals Port480's search word in content, for every stage of ck, jp8 and atm3.
