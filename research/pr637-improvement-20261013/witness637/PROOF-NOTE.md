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

## ColdThird (h4a): dim-8 cold ends and the widened forward-absorption allowlist

This section supersedes the earlier sections wherever they describe the `cold_end` allowlist. On top of the #622/#626
construction, each provider word (jp8, ck) gains 4 cold ends at the dim-8 frame U8a = [256,128,65,33,17,9,4,2]
(helpers S1.3, S3.3, S5.3, S7.3), each with 2 lifted partners, plus dead-port absorptions. Per word the paid profile
changes by {1:+4, 4:+4, 6:-4} against #622 v3, and 4 helpers go from width 9 to width 8.

### What soundness rests on
Soundness does **not** rest on the deadness condition of the allowlist. It rests on checks that re-run unchanged on
the spliced word:
- the transport's exact arbitrary-dirt **endpoint replay** in both orientations (`code/hpe_audit_and_transport.py`),
  which re-verifies the exact refactored cleanup, so every port and helper is restored exactly;
- the **`:157` guard** in `code/hpe_audit_and_transport.py`: no precondition or compensation gate touches a
  cold-ended helper;
- the frame chains / paid-profile pin and the cone pre-check, recomputed from the word.

The deadness rule ("`q` untouched by every later *input* A, cut or B gate") is an allowlist restriction on recipes,
not a load-bearing hypothesis: the independent review moved a dirt release before its port's last kernel write, the
transport replay still accepted it (the two additions commute), and only the allowlist rejected it.

### What changes
ColdBeyond allowed forward absorptions `q += a·g` in section A of the `cold_end` step, each inserted right after a distinct
input-A gate `t`. It required:
- (a) neither register is a target;
- (b) `q` is untouched by every later A, cut or B gate;
- (c) `q` and `g` both already sit at the gate frame.

ColdThird changes the allowlist in exactly two places, `code/build_cold_end.py::apply` and `verify.py::cold_end`:
1. **Several absorptions after the same input gate.** The recipe list is sorted by `t`, and gates that share a `t` run in
   recipe order.
2. **Deadness is judged against the input word.** `q` must be untouched by every later *input* A, cut or B gate. A later
   absorption may write `q` or read it.

Section B and the cut are still never modified.

Old recipes keep their meaning: all three `#622` v3 recipes rebuild to byte-identical words under the widened builder.

### Why the forward computation is unchanged
**Induction over the spliced A.** Let D be the set of registers that some absorption has already written.
- Every input gate sees exactly the operands it had before. An input gate never touches a register of D after that
  register's absorption point, by (b) against input gates.
- An absorption writes only its own `q`, which joins D.
- An absorption may read a register of D. That only changes the value of another register of D.
- Hence every register outside D has its old value at every input gate, and so do targets, centres, live helpers and
  live ports.

**What changes, and who handles it.** Only the end-of-B values of D-registers change. These are non-target ports and
helpers, whose cleanup is part of the exact refactored cleanup. That cleanup is re-verified by the transport's
arbitrary-dirt endpoint replay in both orientations.

**Frames and profile.** By (c), absorptions are at their registers' current frame. So every frame chain, and therefore
the paid profile, equals the input's. `chain_profile` recomputes the profile, and the transport's climb re-asserts
monotonicity.

### What the new absorptions do
Two kinds of absorption are new: dirt releases (K side) and L-side gates. Together they let a cold end sit at a dim-8
frame U8 = [256,128,65,33,17,9,4,2] with only 2 lifted partners per end.

- **Dirt releases (K side).** For example `p15 += -1/4·S3.3` after `p15`'s last kernel gate. A dead U_b port takes a
  live helper's value, so the new end's premix column leaves no dirt on that port. Without this, the port would have to
  be lifted to U8.
- **L-side gates.** For example `p12 += -p15; p12 += -S3.3` at one anchor. These make the row of the lifted partner
  `p12` data-free on the cold group, so the row fix needs no further partners.

Each per-word package has these parts:
- 4 new ends: S1.3, S3.3, S5.3 and S7.3, all at U8.
- Lifted partners: the dim-4 port at offset 4 and S.13 of blocks 3, 5, 7 and 9.
- 16 new absorptions: 8 releases and 8 L-side gates.

The premix is now one rank-0 factorisation over all cold units: the block units at U_b plus the U8 units. It is jointly
biorthogonal: the block rows are re-solved against the U8 columns, using block 3/5/7/9's third row dimension created by
the L-side gates.

Target writes may now combine several carriers, `t += Σ β_k y_k` with `Σ β_k M[k,·]` = e_h on the ended columns. This
is the same primitive: frame-[] target writes from cold, non-entering helpers.

### Re-verified downstream (code unchanged)
- `hpe_audit_and_transport.py`:
  - exact replay;
  - the cone pre-check for all 26 low-frame ends;
  - the paid-profile pin;
  - the `:157` guard (no precondition or compensation gate touches an ended helper).
- The local emit/replay, wrapper and phase stages, and all global stages.
- No new Lean rule is needed: both primitives are ordinary section-A gates of the native word, and the U8 ends are
  `(0, U)` cold ends of the PR599 kind.

### Negative controls
See `code/cold_end_controls.py`, COLD-THIRD block. Each control must be rejected at a pinned assertion:
- second absorption sharing an anchor dropped;
- shared-anchor coefficient changed;
- dirt-release absorption dropped;
- dirt-release coefficient changed;
- dirt-release absorption moved before the port's last kernel write (port still live);
- dim-8 end at another dim-8 frame;
- dim-8 end lower-frame gate dropped;
- dim-8 end profile pin.

These come on top of the 38 inherited controls.

### Inherited control re-pin: `ab_centre`
`code/cold_end_controls.py` changes one inherited control. When the word has dim-8 cold ends
(`any(len(helper_final[h]) == 8 for h in cold)`), the `ab_centre` mutant (the ColdBeyond U_b absorption retargeted
into a centre, a live register read by the cut) is expected to be rejected by COLDPRE ("touches a cold
hyperplane-ended helper") instead of by the arbitrary-dirt ENDPOINT replay: the retargeted absorption first leaks an
ended helper's dirt into the cut's targets, which the `:157` guard catches before the replay runs. The retarget
centre is now also chosen outside the cold set (`c not in cold`), so the mutant always targets a live centre. The
mutant is still rejected; this is a change of the pinned rejection site, not a weakening. With the 8 ColdThird
controls the `cold_end` step pins 46 rejected controls per word.

## st2: PR627's two factored jp8 ends stacked on h4a (complex-571-cold14-st2)

This section adds to the ColdThird section above; the code is h4a's reviewed code, unchanged. Only the jp8 `cold_end`
recipe changes (`data/recipes/k492-jp8-cold_end.json.gz`); ck is h4a's. H4aReviewer, Addendum 2: SOUND for the local
stages.

### What is stacked
PR627 (jeremydiviney, `complex-571-cold14-k492b`, `data/FACTORED-END.json`) ends two jp8 cold helpers, 590 and 581, at
dim-7 frames, using factored lower-frame tails. Their input HPE word is the same as h4a's. On top of h4a's jp8 recipe,
the stacked recipe adds:
- the new cold ends 590 and 581 at dim-7 frames, each with its lower-frame tail (PR627's extra tail);
- 12 rank-0 premix gates on cold, non-ended helpers at frame `[]`;
- 3 forward absorptions: P95 += −H405 and P92 += ¼·H403 after input-A gate 1665, and P87 += ½·H419 after gate 1800.
All of h4a's absorptions and cold ends are kept. Where PR627's absorptions share an anchor with h4a's, they run after
h4a's in recipe order.

### Premix re-derivation
PR627's premix was derived in PR627's basis, so it is re-derived in h4a's basis (H4aFinish `solve627.py`). The word
used is h4a's premix, followed by input A with h4a's and PR627's absorptions, then the cut, B, h4a's early tail and
PR627's extra tail. On that word the premix is solved exactly: row gates (h += x_l·l) followed by column gates
(k += y_k·h), with l and k cold non-ended helpers at frame `[]`. It is chosen so that, in the total state map, row h is
e_h and column h is e_h on every non-target row, for h = 590 and 581.

### The q92 absorption
h4a has a dirt release at anchor 1665 (q95 += −¼·S403). Stacked, that release leaks into end 581's accumulator through
port 92, which is read by 88 += 92. H4aFinish `fix581.py` searches the dead-port absorptions at that anchor by an exact
linear solve and finds a single gate, `[1665, ['add', 92, 403, 1, 4, [265, 137, 96, 6]]]`, i.e. q92 += ¼·S403. Port 92
is dead after gate 1665, and both registers are already at the gate frame, so the gate is admitted by the
ColdThird allowlist. With it the residual is empty and the solve above succeeds for 581.

### What is re-verified (unchanged code)
- The reviewed `build_cold_end.apply`, applied to the Port480 input word, rebuilds the st2 jp8 word (content 7f4c71dd…).
- The transport's exact endpoint replay is exact in all three orientations, the refactored cleanup is dyadic, and
  `:157` holds: the compensation reads no ended helper.
- The (N) wrappers for the new (0, U7) pairs pass in `hpe_adapters_local.py` (17 cold pairs in the reviewed D4 WRAPPER-CHECKS).
- The 46 `cold_end` controls are rejected.
- The paid profile changes against h4a by {1:+2, 2:+2, 5:−2} per jp8 word (rank mass −4). Ends 581 and 590 move from
  (6,9) to (6,7), and ports 80 and 88 from (4,9) to (4,7)+(7,9). The recomputed profile equals the reported one.

### Credits
PR627 (jeremydiviney) for the two factored jp8 ends and their tails. The re-derivation, the q92 fix and the stacking
are H4aFinish's.

## st2u4: CarrierBypass's premix-only dim-8 cold ends with factored row partners (complex-571-cold14-st2u4)

This section adds to the st2 section above. It reproduces CarrierBypass's proof note (`CarrierBypass/PROOF-NOTE.md`, "u4"). The code is h4a's reviewed code, except `code/cold_end_controls.py`: CarrierBypass's patched controls add an accumulator block and run the dim-8 block for every distinct cold dim-8 frame. The patched file gives 51 rejected controls on the u4 jp8 word and still 46 on h4a/st2 words, and H4aReviewer re-signed it in FINAL-REPORT.md, Addendum 3. Only the jp8 `cold_end` recipe changes against st2 (`data/recipes/k492-jp8-cold_end.json.gz`, CarrierBypass `st_u4/cold_end_recipe.json.gz`). H4aReviewer, Addendum 3: SOUND for the local stages, verified by rebuild with the reviewed `apply`, exact replay in all 3 orientations, `:157`, (N) for (0, U*), and pricing Δ = {1:+8, 2:−4, 4:+4, 5:−4} with 4 widths 9 → 8.

### Change
The build stacks on st2, which is h4a (#629) plus #627 on jp8. Four extra **cold** helpers, **233, 265, 425 and 441**, end at the dim-8 HPE hyperplane U* = [256,128,64,32,16,8,6,1] instead of at FULL. ck is unchanged.

There are no new forward gates and no new absorptions. The recipe differs from st2's in three places only:
1. **Rank-0 premix.** 16 gates with frame [] act on free cold helpers still at their start frame. They are prefixed to st2's premix, after the entry wrappers.
2. **Frame-[] target writes.** These are 40 premix target writes (ColdBeyond primitive). They cancel each new end's dirt on the targets. Each one reads a cold carrier that has unit weight on its end and zero weight on every other ended helper.
3. **The refactored cleanup.**
   - The tail is st2's tail, followed by the new lower-frame gates for each end.
   - The remainder is an exact dyadic Gauss–Jordan factorisation at FULL.

The word is `build_cold_end.apply(hpe, recipe)`. The `apply` and `hpe_audit_and_transport` code is unchanged; it is the reviewed h4a package code. **No verifier widening is needed.** The `cold_end` controls are extended (see Controls below).

### Exactness
Definitions:
- P_t is the state after main and st2's tail.
- Q_U is the set of non-target, non-ended registers whose frame after st2's tail lies in U.

For each new end h, with premix column c_h = M e_h and premix row r_h = e_h^T M^{-1}:
- **Column.** P_t c_h is zero outside Q_U on non-target rows. Its target rows are cancelled by the target writes; the guard at `:157` re-checks this.
- **Row.** r_h P_t^{-1} is zero outside Q_U.
- **Pairing.** r_i · c_j = δ_ij across the four ends. The premix group excludes every ended helper, so the rows and columns of the old ends (v3, E1, h4a, #627) are untouched.

The tail gates are at frames ⊆ U*. They make row h and column h equal to e_h exactly, for every ended helper. The constructor asserts this in exact rationals before the Gauss–Jordan step. The transport replays every arbitrary input column in both orientations, re-checks the cone, frame chains and paid profile, and passes (`aud/st_u4`).

### Factored row partners
Take end 233. Its row is supported on:
- 233 itself;
- 239, which is already lifted to U* by HPE-457's inherited tail, so reading it is free;
- ports 59 and 61. Both sit at the same dim-4 frame U_b, where the v3 block tail left them.

The tail is:
- `59 += −61` at U_b. Both registers already sit at U_b, so there is no climb. **59 is the accumulator.**
- `233 += x·59` at U*. Only 59 climbs, 4 → 8.
- Then 233's other row and column gates at U*.

The same pattern holds for the other three ends, with accumulators **19** (`19 += −21`), **83** (`83 += −85`) and **51** (`51 += −53`).

This is exact because:
- no later tail gate touches the accumulator;
- the Gauss–Jordan remainder is recomputed from the resulting state, so it restores the accumulator and its partner at FULL.

Delta per end: {1:+2, 2:−1, 4:+1, 5:−1}, width 9→8. The helper climbs 7→8 instead of 7→9, and one port climbs 4→8→9 instead of 4→9. Without factoring, two ports split their 5-climbs, and the end is LP-negative.

### Numbers
| | jp8 delta | LP (ColdThird lp, free dispatch) |
|---|---|---|
| st2 | — | 0.0016363477 |
| st2 + u4 | {1:+8, 2:−4, 4:+4, 5:−4}, widths 9→8 ×4 | 0.0016366171 (+2.69e-7) |

### Controls (`ctl/cold_end_controls.py`, patched from h4a's reviewed file)
- **Dim-8 controls per distinct terminal frame.** The three controls (another dim-8 frame, lower-frame gate dropped, profile pin) now run once for each distinct dim-8 terminal frame: U8a for h4a and U* for u4. This means h4a's family keeps its own controls in the stack.
- **New: factored accumulator gate.**
  - Zeroed → rejected at ENDPOINT.
  - Coefficient doubled → rejected at ENDPOINT.

Nothing else is changed.

### Further ends (not shipped)
The joint pairing analysis finds about 23 more dim-8 ends over 7 frames. On top of u4, every one tested lowers the LP:
- 249: 0.0016364415;
- 412: 0.0016365104;
- 428: 0.0016365104.

The reason is that h4a's absorptions into ports 29 and 93 force dim-7 partners for 249 and 409, and the remaining candidates carry dim-6 partners.

### HPE helpers at dim 7: why the carrier cannot be bypassed
Row h at end of B is e_h − e_p. Only a gate that writes h or p can change it:
- before p's last read, such a gate changes values that the targets read;
- after that read, p sits on the s-chain frames, which contain the vector 8 ∉ F_h7.

A bypass therefore needs a copy of p's value for each of the two chains, and so a third register that is dead or unborn at a frame ⊆ F_h7 ∩ F_p6 and whose value is cancellable helper dirt. `hpe3rd.py` lists every such candidate for all 34 HPE helpers on jp8, ck and atm3. Each candidate is either a dead port or a helper carrying port data (297, 329, 361, 393), so no copy is possible.
