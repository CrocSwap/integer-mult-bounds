import Nov15.CongestionI3Cfg
import Nov15.CongestionI3Mu
import Nov15.CongestionI3NumA
import Nov15.CongestionI3NumC4
import Nov15.WholeFloorCover
import Mathlib.Analysis.Convex.SpecificFunctions.Pow
import Mathlib.Analysis.Convex.SpecificFunctions.Basic
import Mathlib.Analysis.SpecialFunctions.Log.Base

/-!
CONGESTION-I3 : the I3 congestion bound and F1's restricted-class ceilings (internal notes: F1.md,
AUDIT.md, LIFT1.md, AUDIT-LIFT.md, LIFT2.md; JUNKINT I3).  See CongestionI3.md for the scope list.  Kernel only: no sorry, no native_decide.

Sections: 1 per-pair bound (I3 is a HYPOTHESIS `I3Path`, in model M_V; the shape-DAG minimum is a data hypothesis), 2 forced junk >= 1936
(kernel-checked configurations + census; per-chain flag-DP minima are a data hypothesis), 3 combination with R3 by MAX, 4 the ceilings.
-/
namespace CongestionI3
open NumCertK JointCeiling CallerCost

/-! ### 1. I3: public excess >= per-pair distance, summed over supp J -/

/-- JUNKINT I3 (F1.md sec. 1): in model M_V (every public register except the Y mains ends at V; owned code fixed; X_q born at A_q) the public
excess `E` over R3's per-register floors is at least the sum over the junk pairs of the shortest-path distance.  NOT derived here (the
telescoping I1/I2 and the path bound are not formalised): it is the hypothesis `I3Path`, always taken together with its scope. -/
def I3Path (J : Finset (ℕ × ℕ)) (dist : ℕ × ℕ → ℝ) (E : ℝ) : Prop := ∑ p ∈ J, dist p ≤ E

/-- per-pair minimum => E >= delta * |J| -/
theorem pair_bound {J : Finset (ℕ × ℕ)} {dist : ℕ × ℕ → ℝ} {E δ : ℝ} (hd : ∀ p ∈ J, δ ≤ dist p) (h : I3Path J dist E) :
    δ * J.card ≤ E := by
  have := Finset.card_nsmul_le_sum J dist δ hd
  rw [nsmul_eq_mul] at this
  unfold I3Path at h
  linarith

/-- D0 currency: shape-DAG minimum 0.541495 per even pair (F1 sec. 1, reproduced by the auditor); 1936 pairs give >= 1048.33 D0 per call. -/
theorem i3_D0_per_call {J : Finset (ℕ × ℕ)} {dist : ℕ × ℕ → ℝ} {E : ℝ} (hd : ∀ p ∈ J, (0.541495 : ℝ) ≤ dist p)
    (h : I3Path J dist E) (hJ : 1936 ≤ J.card) : (1048.33 : ℝ) ≤ E := by
  have h1 := pair_bound hd h
  have h2 : (1936 : ℝ) ≤ J.card := by exact_mod_cast hJ
  nlinarith

/-! ### 2. forced junk >= 1936 pairs per call for rank-8 C = 56 decoders -/

def mu (i k : ℕ) : ℕ := (muTab.getD i []).getD k 0
/-- every configuration's per-chain minima sum to >= 1936 (kernel) -/
theorem mu_sum : ∀ i < 8, 1936 ≤ ∑ k ∈ Finset.range 8, mu i k := by decide +kernel

/-- **forced junk >= 1936 pairs** for a rank-8, C = 56 decoder (one of the 8 configurations `i` of `cfgs`).  Scope/hypotheses, all explicit:
* `hsub`: the chain-k forced cells `F k` are unique cells of chain k (exactly one chain can touch them; kernel-defined `uniqCells`);
* `hJ`: forced cells lie in supp J (a product forced non-zero on a cell no other chain touches cannot be cancelled);
* `hDP`: the per-chain flag-DP minimum (data, internal notes, python exact DP over the subspace lattice, NOT kernel-checked).
The decoder class itself (rank-8 on P104 labels, C = 56, rigidity M^ = D1 G D2 quoted numerically, enumeration exhaustive = 12,870 subsets) is the
hypothesis `i < 8`. -/
theorem forced_junk_ge (i : ℕ) (hi : i < 8) (J : Finset (ℕ × ℕ)) (F : ℕ → Finset (ℕ × ℕ))
    (hsub : ∀ k < 8, F k ⊆ uniqCells (cfgs.getD i []) k) (hJ : ∀ k < 8, F k ⊆ J)
    (hDP : ∀ k < 8, mu i k ≤ (F k).card) : 1936 ≤ J.card := by
  have hdisj : ∀ k ∈ Finset.range 8, ∀ k' ∈ Finset.range 8, k ≠ k' → Disjoint (F k) (F k') := by
    intro k hk k' hk' hne
    exact (uniqCells_disjoint (cfgs.getD i []) hne).mono (hsub k (Finset.mem_range.mp hk)) (hsub k' (Finset.mem_range.mp hk'))
  have h1 : (Finset.range 8).biUnion F ⊆ J := by
    intro p hp
    obtain ⟨k, hk, hp⟩ := Finset.mem_biUnion.mp hp
    exact hJ k (Finset.mem_range.mp hk) hp
  have h2 : ((Finset.range 8).biUnion F).card = ∑ k ∈ Finset.range 8, (F k).card :=
    Finset.card_biUnion (fun k hk k' hk' hne => hdisj k hk k' hk' hne)
  have h3 : ∑ k ∈ Finset.range 8, mu i k ≤ ∑ k ∈ Finset.range 8, (F k).card :=
    Finset.sum_le_sum fun k hk => hDP k (Finset.mem_range.mp hk)
  have h4 := mu_sum i hi
  calc 1936 ≤ ∑ k ∈ Finset.range 8, (F k).card := le_trans h4 h3
    _ = ((Finset.range 8).biUnion F).card := h2.symm
    _ ≤ J.card := Finset.card_le_card h1

/-! ### 3. combination with R3: by MAX, not sum -/

/-- **F1 floor in F currency (max rule).**  The word's public overpay `E` (F currency) is priced by BOTH R3's forced stops (E >= (2 - 2^s) st,
st + mp >= 104 with lat = 0, nested words) and by I3 (E >= I).  Both bound the SAME quantity, so the floor is R1/R2's owned 16 plus
`max (88 (2 - 2^s)) I`.  I = 0 recovers R3's `-Nfl`. -/
theorem f1_floor (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (mp st : ℕ) (Fn E I : ℝ)
    (hF : Fn ≤ -400 * (8 : ℝ) ^ s - mp - E) (hmp : 16 ≤ mp) (hY : 104 ≤ st + mp)
    (hst : (2 - (2 : ℝ) ^ s) * st ≤ E) (hI : I ≤ E) :
    Fn ≤ -400 * (8 : ℝ) ^ s - 16 - max (88 * (2 - (2 : ℝ) ^ s)) I := by
  have hu1 : (1 : ℝ) ≤ (2 : ℝ) ^ s := Real.one_le_rpow (by norm_num) hs0
  have hu2 : (2 : ℝ) ^ s ≤ 2 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 2 by norm_num) hs1
    simpa using this
  set c : ℝ := 2 - (2 : ℝ) ^ s with hc
  have hc0 : 0 ≤ c := by linarith
  have hc1 : c ≤ 1 := by linarith
  have hm : (16 : ℝ) ≤ mp := by exact_mod_cast hmp
  have hY' : (104 : ℝ) ≤ st + mp := by exact_mod_cast hY
  have hst0 : (0 : ℝ) ≤ st := Nat.cast_nonneg _
  have hE0 : 0 ≤ E := le_trans (mul_nonneg hc0 hst0) hst
  suffices h : (16 : ℝ) + max (88 * c) I ≤ mp + E by linarith
  rcases le_total (88 * c) I with h | h
  · rw [max_eq_right h]; linarith
  · rw [max_eq_left h]
    rcases le_or_gt (mp : ℝ) 104 with h2 | h2
    · have h3 : c * (104 - mp) ≤ c * st := mul_le_mul_of_nonneg_left (by linarith) hc0
      nlinarith
    · nlinarith

/-- the max rule is not a sum rule: both hypotheses hold with E = max and fail for the sum (so `max` is all the two bounds give). -/
theorem sum_not_implied : ∃ E I R : ℝ, I ≤ E ∧ R ≤ E ∧ ¬ (I + R ≤ E) := ⟨1, 1, 1, le_refl _, le_refl _, by norm_num⟩

/-! ### 4. the ceiling kappa <= .0183952347 (8|9) -/

/-- the native of F1's relaxation: owned floor `400 * 8^s + 16`, no stops -/
def natBase : Inv := ⟨[], [(8, 400), (1, 16)]⟩
theorem natBase_F (s : ℝ) : Finv s natBase = -(400 * (8 : ℝ) ^ s + 16) := by
  simp [Finv, natBase, Fh]

theorem base_eq (s : ℝ) : Finv s (invoice (caller 6 7) natBase 17) = Fc cfB s := by
  simp only [Finv, Fh, invoice, caller, callerT, callerP, armT, armP, natBase, scale, Fc, cfB,
    List.range_succ, List.range_zero]
  norm_num
  ring

/-- tbar = .0183952347 -/
def tbarA : ℚ := 183952347 / 10 ^ 10
theorem sA_eq : sA = 1 - tbarA := by unfold sA tbarA; norm_num

/-- **F1 ceiling, 8|9 (kappa <= .0183952347)** for words in the restricted class, with every hypothesis explicit:
* scope (propositions the caller must supply): `MV` (model M_V), `Rank8C56` (rank-8 decoder, C = 56 on P104 labels, one of the 8 configurations `i`),
  `PlaneSep` (no second-plane carrier of plane-1 content) -- under `PlaneSep` fails the junk bound collapses to 0 (F1 f1k2); LIFT1 replaces it by
  the public-provenance direction law (see `ceiling_A_noSep`).  `nested`: lat = 0 (verifier rule, WholeFloorNest).
* `hI3`: I3 in F currency, `E s >= sum of per-pair F-distances` (hypothesis `I3Path`, valid under the scope);
* `hdist`: per-pair shape-DAG minimum `sigma0 <= sp_F(t)` for t in [tbar, .1] (DATA: f1ceil.spF at tbar; monotone in t numerically, AUDIT: the
  convex/superadditive proof of monotonicity was not re-derived);
* `hforced`/`hDP`: section 2 (|J| >= 1936).
Conclusion: F < 0 on the 17-call invoice of the #7113 caller for every t in [tbar, 1] -- the ceiling convention of JointCeiling/WholeFloorCover. -/
theorem ceiling_A (MV Rank8C56 PlaneSep : Prop) (hMV : MV) (hR : Rank8C56) (hP : PlaneSep)
    (n : Inv) (mp st : ℕ) (E : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - mp - E s)
    (hmp : 16 ≤ mp) (hY : 104 ≤ st + mp)
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hI3 : MV → Rank8C56 → PlaneSep → ∀ s, 0 ≤ s → s ≤ 1 → I3Path J (distF s) (E s))
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ ((sA : ℚ) : ℝ) → ∀ p ∈ J, ((sigma0 : ℚ) : ℝ) ≤ distF s p)
    (hJ : 1936 ≤ J.card) :
    ∀ t : ℝ, ((tbarA : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  intro t ht ht1
  have hsA : ((sA : ℚ) : ℝ) = 1 - ((tbarA : ℚ) : ℝ) := by rw [sA_eq]; push_cast; ring
  have htb0 : (0 : ℝ) ≤ ((tbarA : ℚ) : ℝ) := by unfold tbarA; norm_num
  have hs0 : (0 : ℝ) ≤ 1 - t := by linarith
  have htb1 : ((tbarA : ℚ) : ℝ) ≤ 1 / 10 := by unfold tbarA; norm_num
  have hs1 : 1 - t ≤ 1 := by linarith
  have hu1 : (1 : ℝ) ≤ (2 : ℝ) ^ (1 - t) := Real.one_le_rpow (by norm_num) hs0
  have hu2 : (2 : ℝ) ^ (1 - t) ≤ 2 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 2 by norm_num) hs1; simpa using this
  have hE0 : 0 ≤ E (1 - t) :=
    le_trans (mul_nonneg (by linarith) (Nat.cast_nonneg st)) (hst _ hs0 hs1)
  rcases le_or_gt (1 / 10 : ℝ) t with h10 | h10
  · -- t >= .1: R3 (I = 0), then the WholeFloorCover cover
    have h1 := f1_floor (1 - t) hs0 hs1 mp st (Finv (1 - t) n) (E (1 - t)) 0 (hF _ hs0 hs1) hmp hY (hst _ hs0 hs1) hE0
    have hc0 : (0 : ℝ) ≤ 88 * (2 - (2 : ℝ) ^ (1 - t)) := by linarith
    rw [max_eq_left hc0] at h1
    have h2 := invoice_F (1 - t) (caller 6 7) n 17
    have h3 := invoice_F (1 - t) (caller 6 7) natFloor 17
    have h4 := natFloor_F (1 - t)
    have h5 := WholeFloorCover.cover t (by linarith) ht1
    have h6 : Nfl (1 - t) = 400 * (8 : ℝ) ^ (1 - t) + 16 + 88 * (2 - (2 : ℝ) ^ (1 - t)) := rfl
    push_cast at h2 h3
    nlinarith
  · -- t in [tbar, .1): I3 lift
    have hsl : (9 / 10 : ℝ) ≤ 1 - t := by linarith
    have hsr : 1 - t ≤ ((sA : ℚ) : ℝ) := by rw [hsA]; linarith
    have hsum := pair_bound (hdist _ hsl hsr) (hI3 hMV hR hP _ hs0 hs1)
    have hE : (1936 : ℝ) * ((sigma0 : ℚ) : ℝ) ≤ E (1 - t) := by
      have : (1936 : ℝ) ≤ J.card := by exact_mod_cast hJ
      have h0 : (0 : ℝ) ≤ ((sigma0 : ℚ) : ℝ) := by unfold sigma0; norm_num
      nlinarith
    have h1 := f1_floor (1 - t) hs0 hs1 mp st (Finv (1 - t) n) (E (1 - t)) (1936 * ((sigma0 : ℚ) : ℝ)) (hF _ hs0 hs1) hmp hY
      (hst _ hs0 hs1) hE
    have h1' : Finv (1 - t) n ≤ -400 * (8 : ℝ) ^ (1 - t) - 16 - 1936 * ((sigma0 : ℚ) : ℝ) := by
      have := le_max_right (88 * (2 - (2 : ℝ) ^ (1 - t))) (1936 * ((sigma0 : ℚ) : ℝ))
      linarith
    have h2 := invoice_F (1 - t) (caller 6 7) n 17
    have h3 := invoice_F (1 - t) (caller 6 7) natBase 17
    have h4 := natBase_F (1 - t)
    have h5 := cfB_neg (1 - t) hsl hsr
    have h6 := base_eq (1 - t)
    have h7 : ((liftA : ℚ) : ℝ) = 17 * 1936 * ((sigma0 : ℚ) : ℝ) := by unfold liftA; push_cast; ring
    push_cast at h2 h3
    nlinarith


/-! ### 5. descent-mass >= 56 charge and the own56 ceiling (kappa <= .0134769139) -/

/-- F price of a descent list (owned MOVEs of ranks `k`): sum of k^s -/
noncomputable def dprice (ks : List ℕ) (s : ℝ) : ℝ := (ks.map fun k : ℕ => ((k : ℕ) : ℝ) ^ s).sum

/-- concavity chord on [1, 9] -/
theorem chord_k (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (k : ℝ) (hk1 : 1 ≤ k) (hk9 : k ≤ 9) :
    1 + ((9 : ℝ) ^ s - 1) / 8 * (k - 1) ≤ k ^ s := by
  have hc := (Real.concaveOn_rpow hs0 hs1).2 (show (1 : ℝ) ∈ Set.Ici 0 by simp) (show (9 : ℝ) ∈ Set.Ici 0 by simp)
    (show 0 ≤ (9 - k) / 8 by linarith) (show 0 ≤ (k - 1) / 8 by linarith) (show (9 - k) / 8 + (k - 1) / 8 = 1 by ring)
  simp only [smul_eq_mul, Real.one_rpow] at hc
  have e : (9 - k) / 8 * 1 + (k - 1) / 8 * 9 = k := by ring
  rw [e] at hc
  nlinarith

theorem dprice_ge (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (ks : List ℕ) (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) :
    ks.length + ((9 : ℝ) ^ s - 1) / 8 * ((ks.sum : ℕ) - ks.length) ≤ dprice ks s := by
  induction ks with
  | nil => simp [dprice]
  | cons a l ih =>
    have ha := hk a (by simp)
    have hl : ∀ k ∈ l, 1 ≤ k ∧ k ≤ 9 := fun k hk' => hk k (by simp [hk'])
    have ih := ih hl
    have h1 := chord_k s hs0 hs1 (a : ℝ) (by exact_mod_cast ha.1) (by exact_mod_cast ha.2)
    simp only [dprice, List.map_cons, List.sum_cons, List.length_cons] at ih ⊢
    simp only [Nat.cast_add, Nat.cast_one]
    nlinarith

/-- 9^s <= 8 * 2^s - 7 on [0,1]  (convexity of u -> u^p, p = log_2 9, on [1,2]; equality at s = 0, 1). It gives
`(9 - 9^s)/8 >= 2 - 2^s`: an extra descent move is never cheaper than a forced stop it replaces. -/
theorem nine_chord (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) : (9 : ℝ) ^ s ≤ 8 * (2 : ℝ) ^ s - 7 := by
  set p : ℝ := Real.logb 2 9 with hp
  have h2p : (2 : ℝ) ^ p = 9 := Real.rpow_logb (by norm_num) (by norm_num) (by norm_num)
  have hp1 : 1 ≤ p := by
    have : (2 : ℝ) ^ (1 : ℝ) ≤ (2 : ℝ) ^ p := by rw [Real.rpow_one, h2p]; norm_num
    exact (Real.rpow_le_rpow_left_iff (by norm_num : (1 : ℝ) < 2)).mp this
  have hu1 : (1 : ℝ) ≤ (2 : ℝ) ^ s := Real.one_le_rpow (by norm_num) hs0
  have hu2 : (2 : ℝ) ^ s ≤ 2 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 2 by norm_num) hs1; simpa using this
  have hc := (convexOn_rpow hp1).2 (show (1 : ℝ) ∈ Set.Ici 0 by simp) (show (2 : ℝ) ∈ Set.Ici 0 by simp)
    (show 0 ≤ 2 - (2 : ℝ) ^ s by linarith) (show 0 ≤ (2 : ℝ) ^ s - 1 by linarith)
    (show (2 - (2 : ℝ) ^ s) + ((2 : ℝ) ^ s - 1) = 1 by ring)
  simp only [smul_eq_mul, Real.one_rpow] at hc
  have e : (2 - (2 : ℝ) ^ s) * 1 + ((2 : ℝ) ^ s - 1) * 2 = (2 : ℝ) ^ s := by ring
  rw [e, h2p] at hc
  have e2 : ((2 : ℝ) ^ s) ^ p = (9 : ℝ) ^ s := by
    rw [← Real.rpow_mul (by norm_num), mul_comm, Real.rpow_mul (by norm_num), h2p]
  rw [e2] at hc
  nlinarith

/-- **own56 floor (F currency, max rule)**: a rank-8 C = 56 decoder has descent mass >= 56 (hypothesis `hmass`, the F1 premise; descents are owned
MOVEs of rank k in 1..9), at least 8 descents and 8 rises (R1/R2).  Charging the descents at their true F price `sum k^s` (>= 6 * 9^s + 2) and the 8
rises at 1 each gives the floor `-400 8^s - (6 9^s + 10) - max (88 (2 - 2^s)) I`; extra moves beyond 8 + 8 cost at least what the stops they remove
save (`nine_chord`). -/
theorem own56_floor (s : ℝ) (hs0 : 0 ≤ s) (hs1 : s ≤ 1) (ks : List ℕ) (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9)
    (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (mr st : ℕ) (hmr : 8 ≤ mr) (Fn E I : ℝ)
    (hF : Fn ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E) (hY : 104 ≤ st + (ks.length + mr))
    (hst : (2 - (2 : ℝ) ^ s) * st ≤ E) (hI : I ≤ E) :
    Fn ≤ -400 * (8 : ℝ) ^ s - (6 * (9 : ℝ) ^ s + 10) - max (88 * (2 - (2 : ℝ) ^ s)) I := by
  have hu1 : (1 : ℝ) ≤ (2 : ℝ) ^ s := Real.one_le_rpow (by norm_num) hs0
  have hu2 : (2 : ℝ) ^ s ≤ 2 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 2 by norm_num) hs1; simpa using this
  have h9a : (1 : ℝ) ≤ (9 : ℝ) ^ s := Real.one_le_rpow (by norm_num) hs0
  have h9b : (9 : ℝ) ^ s ≤ 9 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 9 by norm_num) hs1; simpa using this
  have hch := nine_chord s hs0 hs1
  have hdp := dprice_ge s hs0 hs1 ks hk
  set c : ℝ := 2 - (2 : ℝ) ^ s with hc
  have hc0 : 0 ≤ c := by linarith
  have hc1 : c ≤ 1 := by linarith
  set b : ℝ := ((9 : ℝ) ^ s - 1) / 8 with hb
  have hb0 : 0 ≤ b := by rw [hb]; linarith
  have hcb : c ≤ 1 - b := by rw [hb, hc]; linarith
  have hm : (8 : ℝ) ≤ ks.length := by exact_mod_cast hmd
  have hmr' : (8 : ℝ) ≤ mr := by exact_mod_cast hmr
  have hmass' : (56 : ℝ) ≤ ((ks.sum : ℕ) : ℝ) := by exact_mod_cast hmass
  have hY' : (104 : ℝ) ≤ st + (ks.length + mr) := by exact_mod_cast hY
  have hst0 : (0 : ℝ) ≤ st := Nat.cast_nonneg _
  have hE0 : 0 ≤ E := le_trans (mul_nonneg hc0 hst0) hst
  have hA : (ks.length : ℝ) + b * (56 - ks.length) ≤ dprice ks s := by
    have : b * (56 - ks.length) ≤ b * (((ks.sum : ℕ) : ℝ) - ks.length) := mul_le_mul_of_nonneg_left (by linarith) hb0
    linarith
  have e9 : (9 : ℝ) ^ s = 8 * b + 1 := by rw [hb]; ring
  rw [e9]
  suffices h : (6 * (8 * b + 1) + 10) + max (88 * c) I ≤ dprice ks s + mr + E by linarith
  have hx : 0 ≤ ((ks.length : ℝ) - 8) * (1 - b - c) := mul_nonneg (by linarith) (by linarith)
  have hy : 0 ≤ ((mr : ℝ) - 8) * (1 - c) := mul_nonneg (by linarith) (by linarith)
  have hxb : 0 ≤ ((ks.length : ℝ) - 8) * b := mul_nonneg (by linarith) hb0
  rcases le_total (88 * c) I with h | h
  · rw [max_eq_right h]
    have hx2 : 0 ≤ ((ks.length : ℝ) - 8) * (1 - b) := mul_nonneg (by linarith) (by linarith)
    nlinarith
  · rw [max_eq_left h]
    have h3 : c * (104 - ks.length - mr) ≤ c * st := mul_le_mul_of_nonneg_left (by linarith) hc0
    nlinarith

/-- the cap/correction form of I3 without plane separation (LIFT1 sec. 1; HYPOTHESIS, valid under the public-provenance direction law only):
transport by owned rank caps each pair's contribution at `cap` and the 8 relaxation rises save at most `corr`. -/
def I3Cap (J : Finset (ℕ × ℕ)) (dist : ℕ × ℕ → ℝ) (cap corr E : ℝ) : Prop := ∑ p ∈ J, min (dist p) cap - corr ≤ E

def tbarC : ℚ := 134769139 / 10 ^ 10
theorem sC_eq : sC = 1 - tbarC := by unfold sC tbarC; norm_num

def natBaseC : Inv := ⟨[], [(8, 400), (9, 6), (1, 10)]⟩
theorem natBaseC_F (s : ℝ) : Finv s natBaseC = -(400 * (8 : ℝ) ^ s + (6 * (9 : ℝ) ^ s + 10)) := by
  simp [Finv, natBaseC, Fh]
theorem baseC_eq (s : ℝ) : Finv s (invoice (caller 6 7) natBaseC 17) = Fc cfC s := by
  simp only [Finv, Fh, invoice, caller, callerT, callerP, armT, armP, natBaseC, scale, Fc, cfC,
    List.range_succ, List.range_zero]
  norm_num
  ring
theorem base88_eq (s : ℝ) :
    Finv s (invoice (caller 6 7) natBaseC 17) - 17 * (88 * (2 - (2 : ℝ) ^ s)) = Fc cfC88 s := by
  rw [baseC_eq]
  simp only [Fc, cfC, cfC88, List.map_cons, List.sum_cons, List.map_nil, List.sum_nil]
  push_cast
  simp only [Real.one_rpow]
  ring

/-- **own56 ceiling, 8|9 (kappa <= .0134769139)**: as `ceiling_A` but (i) the descent mass >= 56 of the rank-8 C = 56 decoder is charged
(`own56_floor`), and (ii) plane separation is NOT assumed: the junk lift is the capped, corrected one (`I3Cap`, LIFT1), valid under the
public-provenance direction law `Prov` (LIFT1 (i) junk reflux, (ii) non-monotone owned lifetimes, (iii) >= 9-row/network decoders are OPEN and are
exactly what `Prov`/`Rank8C56` stand for here; rank-8 decoders with C = 57 do not exist and C >= 58 is not covered by the junk bound 1936).
Data hypotheses: `hdist` (per-pair `ell s <= min dist cap`, from sp_F and unit/48), `hLc` (1936 * ell - corr >= 13.64105 on [tbarC, .1], python,
monotone numerically). -/
theorem ceiling_C (MV Rank8C56 Prov : Prop) (hMV : MV) (hR : Rank8C56) (hP : Prov)
    (n : Inv) (ks : List ℕ) (mr st : ℕ) (E cap corr ell : ℝ → ℝ) (J : Finset (ℕ × ℕ)) (distF : ℝ → ℕ × ℕ → ℝ)
    (hk : ∀ k ∈ ks, 1 ≤ k ∧ k ≤ 9) (hmass : 56 ≤ ks.sum) (hmd : 8 ≤ ks.length) (hmr : 8 ≤ mr) (hcorr0 : ∀ s, 0 ≤ corr s)
    (hF : ∀ s, 0 ≤ s → s ≤ 1 → Finv s n ≤ -400 * (8 : ℝ) ^ s - dprice ks s - mr - E s)
    (hY : 104 ≤ st + (ks.length + mr))
    (hst : ∀ s, 0 ≤ s → s ≤ 1 → (2 - (2 : ℝ) ^ s) * st ≤ E s)
    (hI3 : MV → Rank8C56 → Prov → ∀ s, 0 ≤ s → s ≤ 1 → I3Cap J (distF s) (cap s) (corr s) (E s))
    (hdist : ∀ s, 9 / 10 ≤ s → s ≤ ((sC : ℚ) : ℝ) → ∀ p ∈ J, ell s ≤ min (distF s p) (cap s))
    (hLc : ∀ s, 9 / 10 ≤ s → s ≤ ((sC : ℚ) : ℝ) → ((LcC : ℚ) : ℝ) ≤ 1936 * ell s - corr s)
    (hJ : 1936 ≤ J.card) :
    ∀ t : ℝ, ((tbarC : ℚ) : ℝ) ≤ t → t ≤ 1 → Finv (1 - t) (invoice (caller 6 7) n 17) < 0 := by
  intro t ht ht1
  have hsC : ((sC : ℚ) : ℝ) = 1 - ((tbarC : ℚ) : ℝ) := by rw [sC_eq]; push_cast; ring
  have htb0 : (0 : ℝ) ≤ ((tbarC : ℚ) : ℝ) := by unfold tbarC; norm_num
  have htb1 : ((tbarC : ℚ) : ℝ) ≤ 1 / 10 := by unfold tbarC; norm_num
  have hs0 : (0 : ℝ) ≤ 1 - t := by linarith
  have hs1 : 1 - t ≤ 1 := by linarith
  have hu1 : (1 : ℝ) ≤ (2 : ℝ) ^ (1 - t) := Real.one_le_rpow (by norm_num) hs0
  have hu2 : (2 : ℝ) ^ (1 - t) ≤ 2 := by
    have := Real.rpow_le_rpow_of_exponent_le (show (1 : ℝ) ≤ 2 by norm_num) hs1; simpa using this
  have hE0 : 0 ≤ E (1 - t) :=
    le_trans (mul_nonneg (by linarith) (Nat.cast_nonneg st)) (hst _ hs0 hs1)
  have h2 := invoice_F (1 - t) (caller 6 7) n 17
  have h3 := invoice_F (1 - t) (caller 6 7) natBaseC 17
  have h4 := natBaseC_F (1 - t)
  push_cast at h2 h3
  rcases le_or_gt (1 / 10 : ℝ) t with h10 | h10
  · have h1 := own56_floor (1 - t) hs0 hs1 ks hk hmass hmd mr st hmr (Finv (1 - t) n) (E (1 - t)) 0 (hF _ hs0 hs1) hY
      (hst _ hs0 hs1) hE0
    have hc0 : (0 : ℝ) ≤ 88 * (2 - (2 : ℝ) ^ (1 - t)) := by linarith
    rw [max_eq_left hc0] at h1
    have h5 := cfC88_neg (1 - t) hs0 (by linarith)
    have h6 := base88_eq (1 - t)
    nlinarith
  · have hsl : (9 / 10 : ℝ) ≤ 1 - t := by linarith
    have hsr : 1 - t ≤ ((sC : ℚ) : ℝ) := by rw [hsC]; linarith
    have hcap := hI3 hMV hR hP _ hs0 hs1
    unfold I3Cap at hcap
    have hLc' := hLc _ hsl hsr
    have hLcpos : (0 : ℝ) < ((LcC : ℚ) : ℝ) := by unfold LcC; norm_num
    have hell : 0 ≤ ell (1 - t) := by have := hcorr0 (1 - t); nlinarith
    have hsum : (1936 : ℝ) * ell (1 - t) ≤ ∑ p ∈ J, min (distF (1 - t) p) (cap (1 - t)) := by
      have := Finset.card_nsmul_le_sum J (fun p => min (distF (1 - t) p) (cap (1 - t))) (ell (1 - t)) (hdist _ hsl hsr)
      rw [nsmul_eq_mul] at this
      have hj : (1936 : ℝ) ≤ J.card := by exact_mod_cast hJ
      nlinarith
    have hE : ((LcC : ℚ) : ℝ) ≤ E (1 - t) := by linarith
    have h1 := own56_floor (1 - t) hs0 hs1 ks hk hmass hmd mr st hmr (Finv (1 - t) n) (E (1 - t)) ((LcC : ℚ) : ℝ) (hF _ hs0 hs1) hY
      (hst _ hs0 hs1) hE
    have h1' : Finv (1 - t) n ≤ -400 * (8 : ℝ) ^ (1 - t) - (6 * (9 : ℝ) ^ (1 - t) + 10) - ((LcC : ℚ) : ℝ) := by
      have := le_max_right (88 * (2 - (2 : ℝ) ^ (1 - t))) ((LcC : ℚ) : ℝ)
      linarith
    have h5 := cfC_neg (1 - t) hsl hsr
    have h6 := baseC_eq (1 - t)
    have h7 : ((liftC : ℚ) : ℝ) = 17 * ((LcC : ℚ) : ℝ) := by unfold liftC; push_cast; ring
    nlinarith

end CongestionI3

#print axioms CongestionI3.forced_junk_ge
#print axioms CongestionI3.f1_floor
#print axioms CongestionI3.ceiling_A
#print axioms CongestionI3.chord_k
#print axioms CongestionI3.dprice_ge
#print axioms CongestionI3.nine_chord
#print axioms CongestionI3.own56_floor
#print axioms CongestionI3.ceiling_C
