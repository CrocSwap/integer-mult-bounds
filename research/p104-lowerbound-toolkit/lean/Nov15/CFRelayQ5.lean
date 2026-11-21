import Nov15.CFRelay

/-!
CFRELAYQ5 (lane LEANCF).  The Q5 carrier run of REUSE96 / CARRIER8 (ports in `F2^4`; cleaner `O0`, hot taker `O1`, public
carrier `Y1`), as `CFChain.Life` runs:
 `O0`: init at `<13>`, two cold intakes at `<13>`, output at `<13>` (into `Y1`), ascent `<13> -> <1,12>` (cost 1), clean output;
       so `A'_0 = <13>`, `B_0 = <1,12>`, drop 1.
 `O1`: init at `<12>`, HOT intake of `Y1` at `<12>`, intake of `Y0`, ascent `<12> -> <11,12>` (cost 1), output;
       so `A'_1 = <12>`, `B_1 = <11,12>`, drop 1.
 Proved: both lives are valid `Life`s with `R = 1 + 1 = 2`; the hot pickup is a LEGAL relay `A'_1 <= B_0` (`hot_relay_legal`,
 the public `Y1` only ascends and the cleaning write comes after the pickup); acyclic (`lam = (0,1)`); the level cut gives
 `Σ_l rank M_l = 2 = Σ drops = R` (equality, only level 3 contributes).
-/

open Module Submodule Finset FutureAttr CFChain CFRelay Matrix

namespace CFRelayQ5

def v1 : Fin 4 → ZMod 2 := ![1, 0, 0, 0]
def v12 : Fin 4 → ZMod 2 := ![0, 0, 1, 1]
def v13 : Fin 4 → ZMod 2 := ![1, 0, 1, 1]
def v11 : Fin 4 → ZMod 2 := ![1, 1, 0, 1]
def y0 : Fin 4 → ZMod 2 := ![1, 0, 1, 0]

/-- port labels: `w`-ports 0, 1, `c`-ports 2, 3. -/
def q : Fin 4 → Fin 4 → ZMod 2 := ![v1, v11, y0, v1]

noncomputable def C13 : Chart 4 := Submodule.span (ZMod 2) {v13}
noncomputable def C12 : Chart 4 := Submodule.span (ZMod 2) {v12}
noncomputable def S : Chart 4 := Submodule.span (ZMod 2) (Set.range ![v1, v12])
noncomputable def T : Chart 4 := Submodule.span (ZMod 2) (Set.range ![v11, v12])

theorem v13_eq : v13 = v1 + v12 := by
  funext i; fin_cases i <;> decide

theorem li_S : LinearIndependent (ZMod 2) ![v1, v12] := by
  rw [LinearIndependent.pair_iff]
  decide

theorem li_T : LinearIndependent (ZMod 2) ![v11, v12] := by
  rw [LinearIndependent.pair_iff]
  decide

theorem fS : finrank (ZMod 2) S = 2 := by rw [S, finrank_span_eq_card li_S]; simp
theorem fT : finrank (ZMod 2) T = 2 := by rw [T, finrank_span_eq_card li_T]; simp

theorem v13_ne : v13 ≠ 0 := by
  intro h; have := congrFun h 0; revert this; decide
theorem v12_ne : v12 ≠ 0 := by
  intro h; have := congrFun h 2; revert this; decide

theorem fC13 : finrank (ZMod 2) C13 = 1 := finrank_span_singleton v13_ne
theorem fC12 : finrank (ZMod 2) C12 = 1 := finrank_span_singleton v12_ne

theorem v1_S : v1 ∈ S := Submodule.subset_span ⟨0, rfl⟩
theorem v12_S : v12 ∈ S := Submodule.subset_span ⟨1, rfl⟩
theorem v11_T : v11 ∈ T := Submodule.subset_span ⟨0, rfl⟩
theorem v12_T : v12 ∈ T := Submodule.subset_span ⟨1, rfl⟩

theorem C13_S : C13 ≤ S := by
  rw [C13, Submodule.span_singleton_le_iff_mem, v13_eq]
  exact Submodule.add_mem _ v1_S v12_S
theorem C12_S : C12 ≤ S := by
  rw [C12, Submodule.span_singleton_le_iff_mem]; exact v12_S
theorem C12_T : C12 ≤ T := by
  rw [C12, Submodule.span_singleton_le_iff_mem]; exact v12_T

theorem dot_C13 : ∀ a ∈ C13, a ⬝ᵥ y0 = 0 := by
  intro a ha
  obtain ⟨c, rfl⟩ := Submodule.mem_span_singleton.1 ha
  have : v13 ⬝ᵥ y0 = 0 := by decide
  simp [smul_dotProduct, this]
theorem dot_C12 : ∀ a ∈ C12, a ⬝ᵥ v1 = 0 := by
  intro a ha
  obtain ⟨c, rfl⟩ := Submodule.mem_span_singleton.1 ha
  have : v12 ⬝ᵥ v1 = 0 := by decide
  simp [smul_dotProduct, this]

def w0 : Fin 4 → ℚ := fun t => if t = 0 then 1 else 0
def w1 : Fin 4 → ℚ := fun t => if t = 1 then 1 else 0
def u0 : Fin 4 → ℚ := fun t => if t = 2 then 1 else 0
def u1 : Fin 4 → ℚ := fun t => if t = 3 then 1 else 0

/-! ### the two traces -/

theorem stepUp (A B Z D : Chart 4) (h : Z ≤ D) :
    Step (⟨A, B, Z⟩ : ES 4) (Ev.up D) ⟨A, B, D⟩ (finrank (ZMod 2) D - finrank (ZMod 2) Z) :=
  Step.up _ D h

noncomputable def pre0 : List (Ev 4) := [Ev.intake, Ev.intake, Ev.output, Ev.up S]
noncomputable def start0 : ES 4 := ⟨⊤, ⊥, C13⟩
noncomputable def X0 : Chart 4 := ⊤ ⊓ C13 ⊓ C13
noncomputable def B0 : Chart 4 := ⊥ ⊔ C13 ⊔ S

theorem tr_pre0 : ∃ c, Tr start0 pre0 ⟨X0, ⊥ ⊔ C13, S⟩ c ∧ c = 1 := ⟨_,
  Tr.cons (Step.intake _ rfl) (Tr.cons (Step.intake _ rfl) (Tr.cons (Step.output _)
    (Tr.cons (stepUp X0 (⊥ ⊔ C13) C13 S C13_S) (Tr.nil _)))), by have := fS; have := fC13; omega⟩

noncomputable def start1 : ES 4 := ⟨⊤, ⊥, C12⟩
noncomputable def X1 : Chart 4 := ⊤ ⊓ C12 ⊓ C12
noncomputable def B1 : Chart 4 := ⊥ ⊔ T

theorem tr_body1 : ∃ c, Tr start1 (Ev.intake :: [Ev.intake, Ev.up T, Ev.output]) ⟨X1, B1, T⟩ c ∧ c = 1 := ⟨_,
  Tr.cons (Step.intake _ rfl) (Tr.cons (Step.intake _ rfl)
    (Tr.cons (stepUp X1 ⊥ C12 T C12_T) (Tr.cons (Step.output _) (Tr.nil _)))),
  by have := fT; have := fC12; omega⟩

theorem tr_body0 : ∃ c, Tr start0 (pre0 ++ Ev.output :: []) ⟨X0, B0, S⟩ c ∧ c = 1 := by
  obtain ⟨c, h, hc⟩ := tr_pre0
  exact ⟨_, h.append (Tr.cons (Step.output _) (Tr.nil _)), by omega⟩

/-! ### the two lives, `R = 2` -/

theorem w0_supp : ∀ t, w0 t ≠ 0 → t = 0 := by
  intro t h; by_contra hne; simp [w0, hne] at h
theorem w1_supp : ∀ t, w1 t ≠ 0 → t = 1 := by
  intro t h; by_contra hne; simp [w1, hne] at h
theorem u0_supp : ∀ t, u0 t ≠ 0 → t = 2 := by
  intro t h; by_contra hne; simp [u0, hne] at h
theorem u1_supp : ∀ t, u1 t ≠ 0 → t = 3 := by
  intro t h; by_contra hne; simp [u1, hne] at h

theorem life0 : ∃ cb, Life q C13 [(⟨X0, B0, cb, w0, u0⟩ : Epoch ℚ (Fin 4) 4)] (0 + cb + 0) ∧ cb = 1 := by
  obtain ⟨c, h, hc⟩ := tr_body0
  refine ⟨c, ?_, hc⟩
  refine Life.cons C13 [] (pre0 ++ Ev.output :: []) ⊤ ⟨⊤, ⊥, C13⟩ ⟨X0, B0, S⟩ 0 c 0 w0 u0 [] (Tr.nil _)
    le_top h ?_ ?_ (Life.nil _)
  · intro t ht
    rw [w0_supp t ht]
    exact Submodule.mem_sup_right v1_S
  · intro t ht a ha
    rw [u0_supp t ht]
    exact dot_C13 a (Submodule.mem_inf.1 ha).2

theorem life1 : ∃ cb, Life q C12 [(⟨X1, B1, cb, w1, u1⟩ : Epoch ℚ (Fin 4) 4)] (0 + cb + 0) ∧ cb = 1 := by
  obtain ⟨c, h, hc⟩ := tr_body1
  refine ⟨c, ?_, hc⟩
  refine Life.cons C12 [] (Ev.intake :: [Ev.intake, Ev.up T, Ev.output]) ⊤ ⟨⊤, ⊥, C12⟩ ⟨X1, B1, T⟩ 0 c 0
    w1 u1 [] (Tr.nil _) le_top h ?_ ?_ (Life.nil _)
  · intro t ht
    rw [w1_supp t ht]
    exact Submodule.mem_sup_right v11_T
  · intro t ht a ha
    rw [u1_supp t ht]
    exact dot_C12 a (Submodule.mem_inf.1 ha).2

/-! ### the hot pickup is a legal relay -/

theorem q5_relay : X1 ≤ B0 := by
  obtain ⟨c0, h0, _⟩ := tr_body0
  obtain ⟨c1, h1, _⟩ := tr_body1
  obtain ⟨cp, hp, _⟩ := tr_pre0
  have hmono : Monotone (fun i : ℕ => if i = 0 then C12 else S) := by
    intro i j hij
    by_cases hi : i = 0
    · by_cases hj : j = 0
      · simp [hi, hj]
      · simp [hi, hj, C12_S]
    · have hj : j ≠ 0 := by omega
      simp [hi, hj]
  exact hot_relay_legal (chartP := fun i : ℕ => if i = 0 then C12 else S) hmono (τ := 0) (σ := 1)
    (by norm_num) (pre := []) (post := [Ev.intake, Ev.up T, Ev.output]) h1 (pre' := pre0) (post' := []) h0
    (by
      intro t c h
      cases h
      simp [start1])
    (by
      intro t c h
      have := (Tr.det h hp).1
      rw [this]
      simp)

/-! ### finranks and the level cut -/

theorem fX0 : finrank (ZMod 2) X0 = 1 := by
  have a : finrank (ZMod 2) X0 ≤ finrank (ZMod 2) C13 := Submodule.finrank_mono (inf_le_right)
  have b : finrank (ZMod 2) C13 ≤ finrank (ZMod 2) X0 :=
    Submodule.finrank_mono (le_inf (le_inf le_top le_rfl) le_rfl)
  have := fC13; omega

theorem fX1 : finrank (ZMod 2) X1 = 1 := by
  have a : finrank (ZMod 2) X1 ≤ finrank (ZMod 2) C12 := Submodule.finrank_mono (inf_le_right)
  have b : finrank (ZMod 2) C12 ≤ finrank (ZMod 2) X1 :=
    Submodule.finrank_mono (le_inf (le_inf le_top le_rfl) le_rfl)
  have := fC12; omega

theorem fX0B0 : finrank (ZMod 2) (X0 ⊔ B0 : Chart 4) = 2 := by
  have hX : X0 ≤ S := (inf_le_right : X0 ≤ C13).trans C13_S
  have a : finrank (ZMod 2) (X0 ⊔ B0 : Chart 4) ≤ finrank (ZMod 2) S :=
    Submodule.finrank_mono (sup_le hX (sup_le (sup_le bot_le C13_S) le_rfl))
  have b : finrank (ZMod 2) S ≤ finrank (ZMod 2) (X0 ⊔ B0 : Chart 4) :=
    Submodule.finrank_mono (le_sup_right.trans le_sup_right)
  have := fS; omega

theorem fX1B1 : finrank (ZMod 2) (X1 ⊔ B1 : Chart 4) = 2 := by
  have hX : X1 ≤ T := (inf_le_right : X1 ≤ C12).trans C12_T
  have a : finrank (ZMod 2) (X1 ⊔ B1 : Chart 4) ≤ finrank (ZMod 2) T :=
    Submodule.finrank_mono (sup_le hX (sup_le bot_le le_rfl))
  have b : finrank (ZMod 2) T ≤ finrank (ZMod 2) (X1 ⊔ B1 : Chart 4) :=
    Submodule.finrank_mono (le_sup_right.trans' (le_sup_right : T ≤ ⊥ ⊔ T))
  have := fT; omega

/-- both epochs: `dim A' = 1`, `dim (A' ⊔ B) = 2`, so `da = 4 - 1 = 3`, `db = 4 - 2 = 2`. -/
theorem q5_levelcut :
    ∑ l ∈ Finset.Icc 1 4, (N8.Mnode (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H (1 : Matrix (Fin 2) (Fin 2) ℚ)
      (fun _ => 3) (fun _ => 2) l).rank = 2 ∧
    ∑ l ∈ Finset.Icc 1 4, (N8.Mnode (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H (1 : Matrix (Fin 2) (Fin 2) ℚ)
      (fun _ => 3) (fun _ => 2) l).rank ≤ ∑ k : Fin 2, ((fun _ : Fin 2 => 3) k - (fun _ : Fin 2 => 2) k) := by
  have hz : ∀ l, (¬ (2 < l) ∨ ¬ (l ≤ 3)) → N8.Mnode (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H
      (1 : Matrix (Fin 2) (Fin 2) ℚ) (fun _ => 3) (fun _ => 2) l = 0 := by
    intro l hl
    unfold N8.Mnode N8.lowD N8.highD
    rcases hl with h | h
    · simp [h]
    · simp [h]
  have h3 : N8.Mnode (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H (1 : Matrix (Fin 2) (Fin 2) ℚ)
      (fun _ => 3) (fun _ => 2) 3 = !![1, 0; 1, 1] := by
    unfold N8.Mnode N8.lowD N8.highD
    simp [N8.Toy.N_eq]
  have hr : (!![1, 0; 1, 1] : Matrix (Fin 2) (Fin 2) ℚ).rank = 2 := by
    rw [Matrix.rank_of_isUnit]
    · simp
    · rw [Matrix.isUnit_iff_isUnit_det]; simp [Matrix.det_fin_two]
  have hI : Finset.Icc 1 4 = {1, 2, 3, 4} := by decide
  have hsum : ∑ l ∈ Finset.Icc 1 4, (N8.Mnode (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H
      (1 : Matrix (Fin 2) (Fin 2) ℚ) (fun _ => 3) (fun _ => 2) l).rank = 2 := by
    rw [hI]
    simp [Finset.sum_insert, hz 1 (by decide), hz 2 (by decide), hz 4 (by decide), h3, hr]
  refine ⟨hsum, ?_⟩
  rw [hsum]; simp

theorem q5_cf_cut :
    ∑ l ∈ Finset.Icc 1 4, (N8.Mnode (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H (1 : Matrix (Fin 2) (Fin 2) ℚ)
      (fun _ => 3) (fun _ => 2) l).rank ≤ ∑ k : Fin 2, ((fun _ : Fin 2 => 3) k - (fun _ : Fin 2 => 2) k) :=
  cf_level_cut (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H (1 : Matrix (Fin 2) (Fin 2) ℚ)
    (fun _ => 3) (fun _ => 2) ![0, 1]
    (by intro a b h; fin_cases a <;> fin_cases b <;> simp_all)
    (by intro k j h; fin_cases k <;> fin_cases j <;> simp_all [N8.Toy.H])
    (by intro k j _; norm_num) _

/-- **THE Q5 CARRIER RUN, kernel-checked:** two valid lives with `R = 1 + 1 = 2`; drops `1 + 1`; the hot intake of `O1` is
a legal relay `A'_1 <= B_0`; level cut `Σ_l rank M_l = 2 = R`. -/
theorem q5_summary :
    ∃ (e0 e1 : Epoch ℚ (Fin 4) 4) (c0 c1 : ℕ), Life q C13 [e0] c0 ∧ Life q C12 [e1] c1 ∧ c0 + c1 = 2 ∧
      e0.drop = 1 ∧ e1.drop = 1 ∧ e1.A ≤ e0.B ∧
      ∑ l ∈ Finset.Icc 1 4, (N8.Mnode (1 : Matrix (Fin 2) (Fin 2) ℚ) N8.Toy.H (1 : Matrix (Fin 2) (Fin 2) ℚ)
        (fun _ => 3) (fun _ => 2) l).rank = 2 := by
  obtain ⟨cb0, hl0, hc0⟩ := life0
  obtain ⟨cb1, hl1, hc1⟩ := life1
  refine ⟨⟨X0, B0, cb0, w0, u0⟩, ⟨X1, B1, cb1, w1, u1⟩, 0 + cb0 + 0, 0 + cb1 + 0, hl0, hl1, by omega, ?_, ?_, q5_relay,
    q5_levelcut.1⟩
  · unfold Epoch.drop; simp only []; have := fX0B0; have := fX0; omega
  · unfold Epoch.drop; simp only []; have := fX1B1; have := fX1; omega

end CFRelayQ5

#print axioms CFRelayQ5.life0
#print axioms CFRelayQ5.life1
#print axioms CFRelayQ5.q5_relay
#print axioms CFRelayQ5.q5_levelcut
#print axioms CFRelayQ5.q5_cf_cut
#print axioms CFRelayQ5.q5_summary
