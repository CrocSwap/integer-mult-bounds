# Hyperplane ends past a commuting cleanup prefix (46 helpers per call)

Status: for independent review. Code: `scratch/MultiHPEScout/pipe/` (a copy of `scratch/Pipeline`; only
`code/build_hpe.py` and `code/hpe_controls_atc.py` differ). Lean: PR #593 (`research/hyperplane-end-lean`, Tail.lean /
Main.lean / Labels.lean) and PR #599 (Multi.lean), archived at `scratch/MultiHPEScout/research/hyperplane-end-lean`.

## 0. The change

`build_hpe.py` (#596) admitted an early cleanup gate `g = cleanup[i] = h -= p` only when `g` was the **first** cleanup
gate on both `h` and `p`. The relaxed rule admits `g` when it **commutes with every earlier cleanup gate on its registers**
(`commute()` in build_hpe.py: neither gate writes a register the other touches, or both are additions into one target
and neither reads the other's target). All other conditions are unchanged: `h` is an entering helper with exactly one
cleanup gate, `U` = join of the last A/B frames of `h` and `p` (dim 8), early gates share no register.

On #596's ck, atm3 and jp8 words this admits 8 more helpers per word (38 → 46): `h ∈ {496, 497, 520, 521, 544, 545,
568, 569}`. In each case the partner `p` (299, 33, 331, 105, 363, 41, 395, 97) has exactly one earlier cleanup gate,
`x -= p` (x = 283, 9, 315, 65, 347, 1, 379, 73; cleanup 440–447), which only **reads** `p`. `h` has no earlier cleanup
gate. E is dim 1 ((24) or (30)), the last frames of h / p have dim 7 / 5 and U has dim 8.

Per helper: width 8 → 7; paid `{1:+2, 2:−1, 3:+1, 4:−1}` (h 7→9 becomes 7→8; p 5→9 becomes 5→8→9). Rank mass −1 with
hosted width −1, so total mass and the 2560 deficit are unchanged. The constructor's profile is reproduced by an
independent build of coldk-hpe with the same rule (`coldk-multi.exe info`).

Multi-gate tails and cold E = ⊥ helpers (#599) admit nothing further on these words; see `CENSUS.md`.

## 1. Why #593's hypotheses still hold

#593's theorems are about the word **as executed**, `a ++ tail ++ b ++ [post]`. Nothing in them refers to the original
cleanup order: the order matters only through the scalar hypothesis `hS` (unit helper row, zero column), which the
tools check on the reordered program.

1. **Labels** — `hpe_labels` (Tail.lean:44; equally `hpe_labels_multi`, Multi.lean:195, as the one-gate instance via
   `tail_eq_mtail`). Hypotheses:
   * `ha`: `a` = precondition + compensation + A + cut + B is the inherited part, unchanged.
   * `tail h p Ah Ap U q` is well labelled by `tail_labels` (Tail.lean:30): h and p climb to U, the gate runs at U (G0).
   * `hb`: `b` = the final climbs + the remaining FULL cleanup. The skipped gate `x -= p` now runs in `b` after `p` has
     climbed U → FULL in the final phase, so both operands are at FULL (G0). `b` is well labelled exactly as for the 38
     (the partner of each of the 38 likewise continues U → FULL).
   * `hmv`: no event of `b` moves `h`. True because `h` has exactly one cleanup gate (constructor assert; audit assert
     `cleanup on non-FULL end`, hpe_audit_and_transport.py:216).
   The skipped gate touches `p` and `x`, never `h`, so the relaxation does not affect `hmv`.
2. **Scalars** — `hS` and the endpoint (E). `hpe_audit_and_transport.py:116-124` replays `precondition + compensation +
   A + cut + B + tail + rest` exactly (forward and inverse-transpose, all 728 columns) and asserts the inherited scalar
   identity. Why it passes: as matrices, `t += a·s` is `I + a·E_ts`, and
   `(I + a E_ts)(I + b E_uv) = I + a E_ts + b E_uv + ab·[s = u]·E_tv`. For `x -= p` (t = x, s = p) and `h -= p`
   (u = h, v = p): `s = p ≠ h = u` and `v = p ≠ x = t`, so both products equal `I − E_xp − E_hp`; the gates commute and the
   reordered program is the same linear map as the original. A skipped gate that **writes** `p` (`p += c·y`: t = p = v)
   or touches `h` fails this and is refused by the constructor; any such move that reached the audit is rejected by the
   replay (control below).
3. **(N)** — the new helpers use (E, U) pairs `((24), U₂₄)` and `((30), U₃₀)`. The wrapper check
   (`hpe_adapters_local.py`, `WRAPPER-CHECKS.json`) checks T_U T_E⁻¹ = L (C_[7] ⊗ I) R exactly with phase for **every**
   (E, U) pair of the emitted word; #593's `factor_of_exact` then gives (F), and `hpe_word` (Main.lean:86) gives the
   endpoint `χ⁻¹ (C_[7] ⊗ I₂) χ`. `code/check_hpe_pairs.py` (#593 §4) re-checks the shape on the emitted local run.
4. **Accounting** — unchanged rules: width = |final| − |E| at the emit/audit/invoice sites, mass neutrality as in
   `HostingShapeScout/PROOF-HYPERPLANE-END.md` §2 (the partner pays last → U → FULL, h pays last → U).

No verifier rule changes: the audit, emitter, adapters, invoice and global stage already accept any exact reordering.
Only the constructor's admissibility rule (a sufficient condition for the replay to pass) is widened.

## 2. Negative controls (`code/hpe_controls_atc.py`, run by verify.py's hyperplane_end step)

Inherited raw-word controls (8), all rejected; the first is the audit-level one for this change: an early gate that does
not commute with its skipped prefix (a gate whose source was written by an earlier cleanup gate) is rejected by the
exact replay.

New controls (13; PrefixReviewer fixes applied). Every constructor control must fail with a **pinned** assertion message
(`NONCOMMUTE` = "cleanup gate does not commute with the skipped cleanup gates on its registers", `ONEGATE` = "helper must
have exactly this one cleanup gate"); a different failure aborts the control run. Helpers are paired with their early
gate through the gate's target `cleanup[i][1]` (checked against `helper_final`), not through dict order.
* Synthetic, gate inserted at the head of the cleanup (skipped by the first early gate `h -= p`):
  positive `x -= p` (only reads p) accepted; `p -= x` → NONCOMMUTE; `p *= −1` → NONCOMMUTE;
  an extra gate reading `h` → ONEGATE; an extra gate adding into `h` → ONEGATE (these two exercise the one-gate rule,
  not the commutation check).
* Real helpers: for each helper admitted only by the commutation rule (496, 497, 520, 521, 544, 545, 568, 569 on ck),
  its actual skipped gate `x -= p` (cleanup 447 … 440) is flipped in place to `p -= x` → NONCOMMUTE (8 controls). The
  unflipped word's own changes are re-built (positive).
* Raw word (audit): `local_profile['1'] −= 8` (the 8 new partners' U → FULL climbs not charged) → rejected by the
  audit's paid-profile assert.

Result on `w_ck`: `PASS 21 HPE raw-word mutations rejected` (9 raw-word + 12 constructor).

## 3. Evidence from the strict build (`prop_m46/build`, pipe/propose.py --until build, dev reuse of baseline558 only)

* `{ck,atm3,jp8}-step*-hyperplane_end-construction.log`: `PASS 46 hyperplane-ended helpers` each.
* `{ck,atm3,jp8}-step*-hyperplane_end-controls.log`: `PASS 12 HPE raw-word mutations rejected` each (8 inherited + 4
  constructor; the positive reader case built).
* `{ck,atm3,jp8}-local/WRAPPER-CHECKS.json`: `PASS_RESIDUAL_WRAPPERS_ARE_EXACT`; plus the local native checks
  (all-columns-native-frames = exact replay of the reordered program, phase edges, reflected ledgers, independent local
  controls) that the build runs on every provider.
* #593's independent instance check `code/check_hpe_pairs.py RUN --mutants` on each local: PASS, 46 helpers, 3 distinct
  (E, U) pairs (24 / 12 / 10 helpers; #596 had 24 / 8 / 6 — the same three pairs), 6/6 mutants rejected.
