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
