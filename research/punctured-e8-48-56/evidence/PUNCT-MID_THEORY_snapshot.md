# PUNCT-MID — 48 ≤ p ≤ 56, m ≤ 7 (Opus, Oct 15)
Labels: PROVEN · CHECKED (exact; SAT = kissat + drat-trim VERIFIED; never CaDiCaL) · OPEN. Setting = PUNCT4/5, PUNCTTHEORY (dense B,
column-space factors, Model C). Scope (coordinator re-scope 09:10): m ≥ 8 is PUNCTTHEORY's Theorem M8; here only m ≤ 7.

## §0 Status
- **Reduction (PROVEN, §1):** the whole remaining m ≤ 7 obligation of the band is two SAT families (8 flat types each):
  (I-a) P = 53, all q_γ ≥ 6; (I-b) P = 56, all q_γ ≥ 17 — Lemma-G-failure CNF (rkdirect.py semantics) + these lower bounds
  (+ q_α ≥ 16 at the normal α for the E7 type). UNSAT of (I-a) closes m ≤ 7 for 48 ≤ p ≤ 53; UNSAT of (I-b) for 54 ≤ p ≤ 56.
- **Case-B census (M8 at 54–56): UNSAT-VERIFIED (§2) ⇒ Theorem M8 complete for 48–56.**
- **(I-b) P = 56, q ≥ 17: UNSAT-VERIFIED all 8 types (§4) ⇒ p = 54, 55, 56 CLOSED (all m).**
- (I-a) P = 53, q ≥ 6: running (§5).

## §1 Reduction (PROVEN from PUNCTTHEORY E7q, Lemma R, Lemma H, Theorem M8 and PUNCT5 Lemma G + monotonicity)
Let 48 ≤ p ≤ 53 and a decoder with m ≤ 7 terms. If some root has q_γ := |S ∩ γ^⊥| ≤ 5 ≤ Q(p) (Q = 5,5,5,6,6,6), E7q closes
it (every m). Otherwise every q_γ ≥ 6. m ≤ 7 needs rank N ≤ 7, so Lemma G fails: some rank-7 flat F* (WLOG the type rep, W acts
on everything W-invariantly) has every live outside line bad and every orthogonal 8-frame hit — exactly rkdirect.py's CNF for
(type, P = p). For the E7 type, Lemma H gives q_α ≤ p − 50 ≤ 3 (excluded) or q_α ≥ 16 at the normal α of F*.
54 ≤ p ≤ 56: if some q_γ ≤ 16, Lemma R gives m ≥ 7 (q ≤ 20) and cost ≥ 35 ≥ need(p) (35, 35, 34) for m = 7; so the residue
is all q_γ ≥ 17 (Lemma H's branch is then automatic, q_α ≥ 17).
Monotonicity in P (PUNCT5 §RUNS2, PROVEN): P enters only through |S| ≤ P and the option filter |e| ≤ P (options inclusion-
minimal); the added lower bounds q_γ ≥ k involve S only and not P. A model at P′ < P with option e yields one at P with a
minimal e′ ⊆ e. So UNSAT at (P = 53, k = 6) covers every 48 ≤ p ≤ 53, and UNSAT at (P = 56, k = 17) every 54 ≤ p ≤ 56.
Then Lemma G holds, rank N = 8, m ≥ 8, and Theorem M8 closes (54–56: modulo PUNCTTHEORY's Case-B census).

## §2 Case-B census for Theorem M8 at 54 ≤ p ≤ 56 (taken over from PUNCTTHEORY) — CHECKED
Claim: no S with |S| ≤ 56, q_γ ≥ 17 for all 120 roots, and ≥ 6 roots with d ≥ 3 (⇒ |Q| ≤ 5 in Case B, closing M8 at 54–56).
censusB4.py (encoding = PUNCTTHEORY censusB3.py: y_g → OR of the W-transported root-0 d ≥ 3 kernels of size ≤ P − QB = 39, i.e. the
336 kernels of size 37; |S| ≤ P seqcounter; q_γ ≥ 17 pysat atleast; ≥ 6 y's). Symmetry: root 0 ∈ Q (W transitive); the 336 kernels are ONE
Stab(0)-orbit (computed; Stab(0) = ⟨reflections in 0 and in lines ⊥ 0⟩, kernel family asserted Stab(0)-invariant) ⇒ K0 fixed as units;
second Q-root b over orbit reps of a subgroup of Stab(0, K0) (Schreier generators; a subgroup only coarsens the WLOG, never invalidates it):
5 reps (orbit sizes 15, 36, 20, 45, 3; sum 119). Cubes b = 1, 2, 8, 26: kissat UNSAT + drat-trim VERIFIED (3–8 s each). b = 27: kissat
UNSAT in ~680 s but drat-trim timed out (600 s cap) ⇒ split by b's kernel (head y_b → OR z_bj, so complete) over orbit reps under the
Schreier stabiliser of b: 7 reps, all UNSAT + VERIFIED (1–45 s). **RESULT: UNSAT-VERIFIED (all 11 leaves).** Monotone in P (|S| ≤ P only),
so it covers p = 54, 55, 56. Logs cB4_56_17_6.log, cB4_56_17_6_b27.log. Positive control (censusB4.py 56 12 2): SAT at once (b = 1: |S| = 56, b = 2: |S| = 54); both models re-checked independently (labels: d_0 = d_b = 3 by F2 rank of live labels in N(γ), min q = 15 resp. 12, exactly 2 roots with d ≥ 3), so the encoding is not vacuous.
**⇒ Theorem M8 is complete for 48 ≤ p ≤ 56** (PUNCTTHEORY §4.4 + this census).

## §3 The m ≤ 7 SAT families — method (middrv.py; options opts.py → opts56_T.npz)
- Options: for each outside line s, the inclusion-minimal sets e = s^⊥ ∖ F′ (F′ rank-7 flat ∋ s) are exactly the complements of the
  8,821 rank-6 sections of the E7 s^⊥ (sizes 27–53, all ≤ 56). Counts with |e| ≤ 47 equal rkdirect.py's at P = 47 for all 8 types.
- Orbit tree as PUNCT5 cubedrv3 (W_J-orbits of outside lines largest first; rep live; option rep mod Stab_{W_J}(s)), but each leaf CNF is
  written DIRECTLY: units T (forced orbits ∪ e), ¬S_s, |S| ≤ P, frames not hit by T, own sequential counters q_γ ≥ k (+ q_α ≥ 16 for
  type 7), heads only with options |T ∪ e′| ≤ P (sound: T ∪ e′ ⊆ S). kissat --no-binary + drat-trim against exactly that leaf CNF
  (≤ 540 s each; every heavy run ≤ 20 min wall, resumable state st/T{t}_P{P}_k{k}.json). |T| > P leaves: counting.
- Hard leaves (an E6-type option, |e| = 27, > 8,000 surviving options) are split symmetrically under H = Stab_{W_J}(s) ∩ Stab(e)
  (Schreier generators; a subgroup only coarsens the WLOG): largest H-orbit O of remaining outside lines; branch O ⊆ S, or WLOG
  s′ = min O live with option rep mod Stab_H(s′); recursive (depth ≤ 4). Chunk split fallback when H is trivial.
- Checks: chkmid.py (leaf CNF with all 120 S fixed vs direct numpy test incl. q's; P = 50, k = 0 no-α: 440 sets incl. the 40
  N′(α)∖C SAT family sets, ALL AGREE; P = 56, k = 17: 440 agree), chkq.py (counter: 1,800 assignments agree). Independent Sonnet audit of
  middrv.py + censusB4.py: no soundness bug; hygiene fix applied (cached leaf reused only if T and live set match).

## §4 (I-b) P = 56, all q_γ ≥ 17 — CLOSED (CHECKED; every leaf kissat UNSAT + drat-trim VERIFIED, or counting)
| type | verified entries | counting leaves | split nodes | max single entry s | total CPU |
|---|---|---|---|---|---|
| 0 | 125 | 0 | 2 | 582 | 26 min |
| 1 | 305 | 83 | 3 | 119 | 9 min |
| 2 | 561 | 187 | 5 | 181 | 18 min |
| 3 | 1373 | 544 | 8 | 269 | 36 min |
| 4 | 1027 | 375 | 6 | 157 | 35 min |
| 5 | 575 | 183 | 5 | 227 | 23 min |
| 6 | 238 | 56 | 4 | 135 | 11 min |
| 7 | 60 | 7 | 2 | 712 | 24 min |
("verified entries" include split parents, which are verified through all their children; a failed first attempt before a split is
included in the max time.) No SAT leaf anywhere. Driver middrv.py (md5 at close e6b785ee…), state files st/T{t}_P56_k17.json, lanes
lane3.sh (PUNCT-MID) + helper_lane.sh (main's helper, mutually exclusive by type).
**⇒ For 54 ≤ p ≤ 56 (dense B, column-space factors): every S with all q_γ ≥ 17 has rank N = 8 (Lemma G), so m ≥ 8 and Theorem M8
(with §2's census) closes it; every S with some q_γ ≤ 16 is closed by Lemma R (m = 7: cost ≥ 35 ≥ need) / M8 (m ≥ 8). p = 54, 55, 56
CLOSED for every m.**
