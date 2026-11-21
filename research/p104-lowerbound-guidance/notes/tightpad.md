# TIGHTPAD (Nov 20, Opus, theory + Lean). Files: lean/decoder-duality/Nov15/CallerTightDeg.lean, CallerTightNeed.lean (copies here).
Both built with runlean.sh, rc=0, 6 s / 17 s, peak 2.5 GB. No sorry or native_decide. Every headline's axioms are propext, Classical.choice, Quot.sound.
Not a retread: CALLERWORD/CALLERASM left these two hypotheses open. Item (2) closes one. Item (1) shows the other cannot be closed.

## Item (2): D >= 2 for Q = 0, now DERIVED [P Lean]
- `deg_ge_two` (frame level): take a CallerBridge.Host with |iota| = 2k (no thin columns) and char != 2. Then every role has |mask| >= 2.
  Proof. Suppose |mask r| <= 1. Pick s0 with mask r ⊆ {s0}. Every column is a host column. Off slot pos s0, a column belongs to a stage s with s ∉ mask r, so hB gives B r . = 0.
  Apply LEAF-RANK (CallerThin.leaf_rank) with F = {r} and Th = ∅. It gives 1 <= 0. The mask = ∅ case is the same argument.
- `word_hp_B_nodeg` / `word_hp_A_nodeg`: these are word_hp_B / word_hp_A with `hdeg` dropped.
  - The Host comes from CallerBridge.hostOf (type B) and CallerJA.hostA (type A, merged slots). Both need only Legal, schema, odd targets and hlam.
  - `word_deg_B` / `word_deg_A` state the degree law itself (k >= 1).
- Non-vacuity: `hostK2` is an explicit Q = 0 Host over Q with k = 2, n = 2 (V0 = 2, V1 = -1/2, K-blocks 3I and I/2).
- Necessity of Q = 0: CallerThin's A1/B1 Host (one thin column) has a degree-1 role (`thin_needed`).
- The generic-`Sch` word_hp keeps hdeg, because Sch has no slot data. Both existing schemas (JB, JA) are covered.
- word_hpq's D >= 1 (Q >= 1) is not addressed.

## Item (1): TIGHTNESS cannot be removed. The PADDING lemma is FALSE.
### Frame level [P Lean, CallerTightNeed]
- The direct sum of two copies of hostK2's frame has k = 4, n = 4 and |iota| = 8 = 2k.
- It satisfies: P = -1 (`sumD_prod`), every diagonal K-block invertible (`sumD_diag`), and n + 2 = 6 <= 8 (the role_count_lam form).
- But stages 0 and 2 share no role (`sumD_not_cover`), and G_{0,2} = 0 (`sumD_G_singular`).
- `pairCoverage_needs_tight`: sgPairCoverage (= CROSS / RC2's hG) with tightness weakened to n + m <= km is false.
- Control: inside one copy the law holds (`sumD_cover_inside`).
### Word level [P paper; one input is C1's hlam, [C] exact dets 2, -4, -5 from QZERO]
- Direct sum of legal words.
  - Construction: copy c gets registers 4c + r and stages 3c + s; the copies' events are concatenated; ex = 1; masks are shifted.
  - Legality: each relabelled event matrix is block-diagonal (identity off its copy; D enters through D ∘ shift). So the replay is blockdiag(replay_c) = blockdiag(target_c) = target. WF holds.
  - Schema: JB carries over (pos increasing).
  - Columns: terms depend only on coefficients, so |Iota| = 2k.
  - Frame: P1 restricted to copy c is copy c's own prefix, because earlier copies sit at target(q=1, D=1) = I. So Aw and Bw are the block direct sum of the copies' frames. The K-blocks equal C1's, so hlam holds.
  - Degrees >= 2. cHat is the k-weighted mean of the copies' cHat.
- m copies of CallerQZero.C1W (n = 4m, k = 3m, n + 2 = 4m + 2 < 6m for m >= 2) satisfy every hypothesis of word_hp_B except hn.
  - cHat = 107.910089 (invoice 3.112791).
  - HP(3m) < 107.910089 first at m = 109: HP(327) = 107.902838 [C, 50-digit Decimal]. HP(324) is not below it.
  - At m = 200: HP(600) = 98.886.
  - So "word_hp_B without tightness" is FALSE.
- word_hpq without tightness is also false. 26 copies give k = 78 >= 77 and cHatQ = 174.58 > 128.891 [C]. The excess term -(n - (2k-2)) turns positive.
- PADDING is false [P]. Take W = 109 copies of C1. A tight legal Q = 0 extension W' with the same k, with hlam, and with invoice(W') >= invoice(W) would have cHat(W') >= 107.91 > HP(327). That contradicts word_hp_B, which is proved in Lean.
- Consequence: tightness is a genuine branch hypothesis, like lambda != -1. It is not a removable artifact. The four headlines keep hn. CLAIMAUDIT's move of C10/C14 to CONDITIONAL stands for this hypothesis.

## Salvage / next
- [CONJ DECOMP] Every non-tight Q = 0 frame with all K-blocks invertible is a direct sum of tight frames (rank K = 2 + e' with e' = 2(#summands - 1)).
  - If true: cHat <= max over components of HP(k_i) <= 143.273 for EVERY Q = 0 word, with no tightness hypothesis. A uniform-in-k law replaces HP(k).
  - Test: the rank of K versus the connected components of the role–stage incidence graph.
