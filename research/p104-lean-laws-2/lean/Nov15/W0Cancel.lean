/-
NEWARCH law W0-CANCEL BELOW V (cards/WILD/NEWARCH/SPEC3.md s3, SPEC4 s4, SPEC5), lane LEAN-NEXT30, Nov 17.
See W0Cancel.md. Reuses TokenCancel's op model (Ev/St/step/LegalEv/Legal) and RankLaw's VMixM.

Setting.  `S : Submodule K (Reg → K)` plays S_V (span of V-ending helper directions and X/X2 finals);
`S.mkQ` is the "off-S_V part" (W0 junk).  A V-resident register keeps its row forever (no MOVE leaves V),
and only V-chart ops (add/scale/clear/copy at V) can write it (co-presence).  Hence, with no entry into V
after `s0`, every V-resident's row stays in the span of the rows V-residents had at `s0`.
-/
import Nov15.RankLaw

set_option linter.unusedSectionVars false
namespace W0Cancel
open TokenCancel Submodule

variable {K Reg C : Type*} [Field K] [DecidableEq Reg] [DecidableEq C]
variable (z V : C)

/-- No register enters V: no MOVE/BORN/INIT lands at V. -/
def NoEntry : Ev K Reg C → Prop
  | .born _ c => c ≠ V
  | .init _ c => c ≠ V
  | .move _ c => c ≠ V
  | _ => True

/-- Row span of the V-residents of `s`. -/
def resSpan (s : St K Reg C) : Submodule K (Reg → K) :=
  span K (Set.range fun j : {j // s.loc j = some V} => s.row j.1)

/-- Invariant: the V-resident set is that of `s0`, and its rows lie in `resSpan s0`. -/
structure Inv0 (s0 s : St K Reg C) : Prop where
  res : ∀ i, s.loc i = some V ↔ s0.loc i = some V
  row : ∀ i, s.loc i = some V → s.row i ∈ resSpan V s0

theorem inv0_refl (s0 : St K Reg C) : Inv0 V s0 s0 :=
  ⟨fun _ => Iff.rfl, fun i hi => subset_span ⟨⟨i, hi⟩, rfl⟩⟩

theorem inv0_step (s0 s : St K Reg C) (e : Ev K Reg C) (h : Inv0 V s0 s)
    (hL : LegalEv z V s e) (hn : NoEntry V e) : Inv0 V s0 (step s e) := by
  have hres := h.res
  have hrow := h.row
  cases e with
  | born i c =>
    simp only [LegalEv] at hL
    simp only [NoEntry] at hn
    refine ⟨fun j => ?_, fun j hj => ?_⟩
    · by_cases hji : j = i
      · subst hji
        constructor
        · intro h; simp [step] at h; exact absurd h hn
        · intro h0; exact absurd ((hres j).2 h0) (by simp [hL])
      · simpa [step, Function.update_of_ne hji] using hres j
    · by_cases hji : j = i
      · subst hji; simp [step] at hj; exact absurd hj hn
      · simp only [step, Function.update_of_ne hji] at hj ⊢
        exact hrow j hj
  | init i c =>
    simp only [LegalEv] at hL
    simp only [NoEntry] at hn
    refine ⟨fun j => ?_, fun j hj => ?_⟩
    · by_cases hji : j = i
      · subst hji
        constructor
        · intro h; simp [step] at h; exact absurd h hn
        · intro h0; exact absurd ((hres j).2 h0) (by simp [hL])
      · simpa [step, Function.update_of_ne hji] using hres j
    · by_cases hji : j = i
      · subst hji; simp [step] at hj; exact absurd hj hn
      · simp only [step, Function.update_of_ne hji] at hj ⊢
        exact hrow j hj
  | move i c =>
    obtain ⟨c0, hc0, hc0V, hcz⟩ := hL
    simp only [NoEntry] at hn
    refine ⟨fun j => ?_, fun j hj => ?_⟩
    · by_cases hji : j = i
      · subst hji
        constructor
        · intro h; simp [step] at h; exact absurd h hn
        · intro h0; have := (hres j).2 h0; rw [hc0] at this; exact absurd (Option.some.inj this) hc0V
      · simpa [step, Function.update_of_ne hji] using hres j
    · by_cases hji : j = i
      · subst hji; simp [step] at hj; exact absurd hj hn
      · simp only [step, Function.update_of_ne hji] at hj ⊢
        exact hrow j hj
  | add i j' a c =>
    obtain ⟨hij, hi, hj⟩ := hL
    refine ⟨fun k => by simpa [step] using hres k, fun k hk => ?_⟩
    simp only [step] at hk ⊢
    by_cases hki : k = i
    · subst hki
      have hcV : c = V := by simpa [hi] using hk
      subst hcV
      simp only [Function.update_self]
      exact add_mem (hrow k hk) (smul_mem _ _ (hrow j' hj))
    · simp only [Function.update_of_ne hki]; exact hrow k hk
  | scale i u c =>
    refine ⟨fun k => by simpa [step] using hres k, fun k hk => ?_⟩
    simp only [step] at hk ⊢
    by_cases hki : k = i
    · subst hki; simp only [Function.update_self]
      exact smul_mem _ _ (hrow k hk)
    · simp only [Function.update_of_ne hki]; exact hrow k hk
  | clear i c =>
    refine ⟨fun k => by simpa [step] using hres k, fun k hk => ?_⟩
    simp only [step] at hk ⊢
    by_cases hki : k = i
    · subst hki; simp only [Function.update_self]; exact zero_mem _
    · simp only [Function.update_of_ne hki]; exact hrow k hk
  | copy i j' c =>
    obtain ⟨hi, hj⟩ := hL
    refine ⟨fun k => by simpa [step] using hres k, fun k hk => ?_⟩
    simp only [step] at hk ⊢
    by_cases hki : k = i
    · subst hki
      have hcV : c = V := by simpa [hi] using hk
      subst hcV
      simp only [Function.update_self]
      exact hrow j' hj
    · simp only [Function.update_of_ne hki]; exact hrow k hk

/-- **W0-CANCEL, core (V-blindness).**  In a legal run in which nothing enters V, the V-residents'
rows at the end lie in the span of the V-residents' rows at the start. Ops at charts below V (indeed at
any chart ≠ V) never write a V-resident (co-presence), and V ops only combine V-residents. -/
theorem vblind (s0 : St K Reg C) (evs : List (Ev K Reg C)) :
    ∀ (s : St K Reg C), Inv0 V s0 s → Legal z V s evs → (∀ e ∈ evs, NoEntry V e) →
      Inv0 V s0 (run s evs) := by
  induction evs with
  | nil => intro s h _ _; exact h
  | cons e es ih =>
    intro s h hL hn
    simp only [Legal] at hL
    simp only [List.mem_cons, forall_eq_or_imp] at hn
    exact ih (step s e) (inv0_step z V s0 s e h hL.1 hn.1) hL.2 hn.2

theorem vblind_run (s0 : St K Reg C) (evs : List (Ev K Reg C)) (hL : Legal z V s0 evs)
    (hn : ∀ e ∈ evs, NoEntry V e) (i : Reg) (hi : (run s0 evs).loc i = some V) :
    (run s0 evs).row i ∈ resSpan V s0 :=
  (vblind z V s0 evs s0 (inv0_refl V s0) hL hn).row i hi

/-- Off-S_V parts: the junk of a V-ender at the end is a combination of the arrival junks. -/
theorem vblind_mod (S : Submodule K (Reg → K)) (s0 : St K Reg C) (evs : List (Ev K Reg C))
    (hL : Legal z V s0 evs) (hn : ∀ e ∈ evs, NoEntry V e) (i : Reg)
    (hi : (run s0 evs).loc i = some V) :
    S.mkQ ((run s0 evs).row i) ∈
      span K (Set.range fun j : {j // s0.loc j = some V} => S.mkQ (s0.row j.1)) := by
  have h := vblind_run z V s0 evs hL hn i hi
  have h2 := Submodule.mem_map_of_mem (f := S.mkQ) h
  rw [resSpan, Submodule.map_span, ← Set.range_comp] at h2
  exact h2

/-- **W0-CANCEL BELOW V (corrected, joint form).**  If the off-S_V parts of the V-residents at arrival
are linearly independent (each carries its own W0 junk), then a V-resident whose off-S_V part is zero at
the end has row zero: the junk cannot be removed by anything done at V (nothing enters V, and below-V
ops cannot touch it).  Contrapositive: to end with a nonzero in-S_V row, an independent junk must be
cancelled before arrival at V. -/
theorem w0_cancel (S : Submodule K (Reg → K)) (s0 : St K Reg C) (evs : List (Ev K Reg C))
    (hL : Legal z V s0 evs) (hn : ∀ e ∈ evs, NoEntry V e)
    (hind : LinearIndependent K fun j : {j // s0.loc j = some V} => S.mkQ (s0.row j.1))
    (i : Reg) (hi : (run s0 evs).loc i = some V)
    (h0 : S.mkQ ((run s0 evs).row i) = 0) : (run s0 evs).row i = 0 := by
  have h := vblind_run z V s0 evs hL hn i hi
  unfold resSpan at h
  obtain ⟨c, hc⟩ := (Finsupp.mem_span_range_iff_exists_finsupp).1 h
  have hmap : S.mkQ (Finsupp.linearCombination K (fun j : {j // s0.loc j = some V} => s0.row j.1) c)
      = Finsupp.linearCombination K (fun j : {j // s0.loc j = some V} => S.mkQ (s0.row j.1)) c := by
    simpa [Function.comp_def] using
      Finsupp.apply_linearCombination (R := K) S.mkQ (fun j : {j // s0.loc j = some V} => s0.row j.1) c
  have hlc : Finsupp.linearCombination K (fun j : {j // s0.loc j = some V} => s0.row j.1) c
      = (run s0 evs).row i := by
    rw [Finsupp.linearCombination_apply]; exact hc
  have hz : Finsupp.linearCombination K (fun j : {j // s0.loc j = some V} => S.mkQ (s0.row j.1)) c
      = Finsupp.linearCombination K (fun j : {j // s0.loc j = some V} => S.mkQ (s0.row j.1)) 0 := by
    rw [← hmap, hlc, h0]; simp
  have := hind hz
  rw [← hlc, this, map_zero]

/-! ### R3 corollary: deferring a stop to V -/

/-- A V-only suffix (add/scale/clear/copy at V). -/
def VOp : Ev K Reg C → Prop
  | .add _ _ _ c => c = V
  | .scale _ _ c => c = V
  | .clear _ c => c = V
  | .copy _ _ c => c = V
  | _ => False

theorem vonly_const (s : St K Reg C) (evs : List (Ev K Reg C)) (hL : Legal z V s evs)
    (hv : ∀ e ∈ evs, VOp V e) :
    (run s evs).loc = s.loc ∧ ∀ i, s.loc i ≠ some V → (run s evs).row i = s.row i := by
  induction evs generalizing s with
  | nil => exact ⟨rfl, fun _ _ => rfl⟩
  | cons e es ih =>
    simp only [Legal] at hL
    simp only [List.mem_cons, forall_eq_or_imp] at hv
    obtain ⟨h1, h2⟩ := ih (step s e) hL.2 hv.2
    have hLe := hL.1
    have hve := hv.1
    have hloc : (step s e).loc = s.loc := by
      cases e <;> simp_all [VOp, step]
    have hr : run s (e :: es) = run (step s e) es := rfl
    rw [hr]
    refine ⟨by rw [h1, hloc], fun i hi => ?_⟩
    rw [h2 i (by rwa [hloc])]
    cases e with
    | add i' j' a c =>
      obtain ⟨_, hi', _⟩ := hLe
      have : c = V := hve
      subst this
      have hne : i ≠ i' := fun h => hi (h ▸ hi')
      simp [step, Function.update_of_ne hne]
    | scale i' u c =>
      have hi' := hLe
      have : c = V := hve
      subst this
      have hne : i ≠ i' := fun h => hi (h ▸ hi')
      simp [step, Function.update_of_ne hne]
    | clear i' c =>
      have hi' := hLe
      have : c = V := hve
      subst this
      have hne : i ≠ i' := fun h => hi (h ▸ hi')
      simp [step, Function.update_of_ne hne]
    | copy i' j' c =>
      obtain ⟨hi', _⟩ := hLe
      have : c = V := hve
      subst this
      have hne : i ≠ i' := fun h => hi (h ▸ hi')
      simp [step, Function.update_of_ne hne]
    | born _ _ => exact absurd hve (by simp [VOp])
    | init _ _ => exact absurd hve (by simp [VOp])
    | move _ _ => exact absurd hve (by simp [VOp])

/-- **R3 corollary (rows).**  If the V mix is an invertible combination `C * X' = R` (HubSettle's `VMixM`)
and every target row lies in `S` (= S_V), then so does every pre-V row `X'`.  Hence deferring a stop to V
(replacing the working pre-V rows `X` ∈ S by `X' = X + Δ`) is legal only if every perturbation row Δ_g
lies in S_V. -/
theorem defer_rows_in_S {G : Type*} [Fintype G] [DecidableEq G] (S : Submodule K (Reg → K))
    (X' R : Matrix G Reg K) (hR : ∀ g, R g ∈ S) (hmix : RankLaw.VMixM X' R) : ∀ g, X' g ∈ S := by
  obtain ⟨M, hM, hMX⟩ := hmix
  intro g
  have h1 : X' = M⁻¹ * R := by rw [← hMX, ← Matrix.mul_assoc, Matrix.nonsing_inv_mul _ hM, Matrix.one_mul]
  rw [h1]
  have : (M⁻¹ * R) g = ∑ k, M⁻¹ g k • R k := by
    funext r; simp [Matrix.mul_apply]
  rw [this]
  exact S.sum_mem fun k _ => S.smul_mem _ (hR k)

theorem defer_perturbation_in_S {G : Type*} [Fintype G] [DecidableEq G] (S : Submodule K (Reg → K))
    (X X' R : Matrix G Reg K) (hX : ∀ g, X g ∈ S) (hR : ∀ g, R g ∈ S)
    (hmix : RankLaw.VMixM X' R) : ∀ g, X' g - X g ∈ S :=
  fun g => S.sub_mem (defer_rows_in_S S X' R hR hmix g) (hX g)

/-- **R3 corollary (non-V rows).**  If the deferred and the working programs end with the same rows and
both end in a V-only suffix, every register off V has the same row before the suffix in both. -/
theorem defer_nonV_unchanged (s s' : St K Reg C) (evs evs' : List (Ev K Reg C))
    (hL : Legal z V s evs) (hL' : Legal z V s' evs') (hv : ∀ e ∈ evs, VOp V e)
    (hv' : ∀ e ∈ evs', VOp V e) (hloc : s.loc = s'.loc)
    (hend : ∀ i, (run s evs).row i = (run s' evs').row i) (i : Reg) (hi : s.loc i ≠ some V) :
    s'.row i = s.row i := by
  have a := (vonly_const z V s evs hL hv).2 i hi
  have b := (vonly_const z V s' evs' hL' hv').2 i (by rwa [← hloc])
  rw [← b, ← a, hend]

/-! ### The statement "as written" is false: a V-resident's junk can be cancelled AT V against
another V-resident carrying the same junk. -/

section Counter
open Ev

abbrev R3 := Fin 3
/-- charts: 0 = z, 1 = V, 2 = a chart below V. -/
def evsC : List (Ev ℚ R3 (Fin 3)) :=
  [born 0 2, born 1 2, born 2 2, add 1 0 1 2, add 2 0 1 2, move 1 1, move 2 1, add 1 2 (-1) 1]

def evsPre : List (Ev ℚ R3 (Fin 3)) := evsC.take 7

lemma legalC : Legal (0 : Fin 3) 1 (start : St ℚ R3 (Fin 3)) evsC := by
  simp [evsC, Legal, LegalEv, step, start, Function.update_apply]

/-- S_V := span{e_1, e_2}; the junk direction is e_0 (a W0 direction, not in S_V). -/
def SC : Submodule ℚ (R3 → ℚ) := span ℚ {Pi.single 1 1, Pi.single 2 1}

/-- Counterexample to the individual statement: register 1's arrival row `e_1 + e_0` has junk e_0 ∉ S_V,
no op at a chart below V follows its arrival, yet its final row `e_1 - e_2` is in S_V (cancelled at V
against register 2, whose own row keeps the junk). -/
theorem counter_individual :
    (run start evsPre : St ℚ R3 (Fin 3)).row 1 = Pi.single 1 1 + Pi.single 0 1 ∧
    (run start evsPre : St ℚ R3 (Fin 3)).row 2 = Pi.single 2 1 + Pi.single 0 1 ∧
    (run start evsC : St ℚ R3 (Fin 3)).row 1 = Pi.single 1 1 - Pi.single 2 1 ∧
    (run start evsC : St ℚ R3 (Fin 3)).row 1 ∈ SC ∧
    (run start evsC : St ℚ R3 (Fin 3)).row 2 ∉ SC := by
  have e1 : (run start evsPre : St ℚ R3 (Fin 3)).row 1 = Pi.single 1 1 + Pi.single 0 1 := by
    funext k; fin_cases k <;> simp [evsPre, evsC, run, step, start, Function.update_apply]
  have e2 : (run start evsPre : St ℚ R3 (Fin 3)).row 2 = Pi.single 2 1 + Pi.single 0 1 := by
    funext k; fin_cases k <;> simp [evsPre, evsC, run, step, start, Function.update_apply]
  have e3 : (run start evsC : St ℚ R3 (Fin 3)).row 1 = Pi.single 1 1 - Pi.single 2 1 := by
    funext k; fin_cases k <;> simp [evsC, run, step, start, Function.update_apply]
  have e4 : (run start evsC : St ℚ R3 (Fin 3)).row 2 = Pi.single 2 1 + Pi.single 0 1 := by
    funext k; fin_cases k <;> simp [evsC, run, step, start, Function.update_apply]
  refine ⟨e1, e2, e3, ?_, ?_⟩
  · rw [e3, SC]
    exact sub_mem (subset_span (by simp)) (subset_span (by simp))
  · rw [e4, SC]
    intro h
    obtain ⟨a, b, hab⟩ : ∃ a b : ℚ, a • (Pi.single 1 1 : R3 → ℚ) + b • Pi.single 2 1 =
        Pi.single 2 1 + Pi.single 0 1 := by
      have := (Submodule.mem_span_pair).1 h
      obtain ⟨a, b, h⟩ := this
      exact ⟨a, b, h⟩
    have := congrFun hab 0
    simp [Pi.single_apply] at this

end Counter

end W0Cancel
