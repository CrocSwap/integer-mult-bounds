import Nov15.CFRelay

/-!
CFRELAYE8 (lane LEANCF).  Non-vacuity for `rendezvous_lemma_A_run`: 8 owned registers, each ONE cold epoch
(`dim A' = 1`, `dim B = 8` inside `F2^9`, cost 7), identity decoder factors (`rank M = 8`), no relays.
All hypotheses of the lemma are *proved* for this instance and `R = 56` is attained (so `56 <= R` is an equality here).
-/

open Module Submodule Finset FutureAttr CFChain CFRelay Matrix

namespace CFRelayE8

/-- coordinate subspace `<e_0, ..., e_{r-1}>` of `F2^9`. -/
noncomputable def coord (r : ℕ) (h : r ≤ 9) : Chart 9 :=
  Submodule.span (ZMod 2) (Set.range ((Pi.basisFun (ZMod 2) (Fin 9)) ∘ Fin.castLE h))

theorem finrank_coord (r : ℕ) (h : r ≤ 9) : finrank (ZMod 2) (coord r h) = r := by
  have hli : LinearIndependent (ZMod 2) ((Pi.basisFun (ZMod 2) (Fin 9)) ∘ Fin.castLE h) :=
    (Pi.basisFun (ZMod 2) (Fin 9)).linearIndependent.comp _ (Fin.castLE_injective h)
  rw [coord, finrank_span_eq_card hli]
  simp

theorem coord_mono {r s : ℕ} (hr : r ≤ 9) (hs : s ≤ 9) (hrs : r ≤ s) : coord r hr ≤ coord s hs := by
  apply Submodule.span_mono
  rintro _ ⟨i, rfl⟩
  exact ⟨Fin.castLE hrs i, by simp⟩

noncomputable abbrev C1 : Chart 9 := coord 1 (by norm_num)
noncomputable abbrev C8 : Chart 9 := coord 8 (by norm_num)

/-- all ports carry the label `e_1`. -/
def q : Fin 8 → Fin 9 → ZMod 2 := fun _ => Pi.single 1 1

def ind (j : Fin 8) : Fin 8 → ℚ := fun t => if t = j then 1 else 0

noncomputable def body : List (Ev 9) := [Ev.intake, Ev.up C8, Ev.output]

theorem C1_le_C8 : C1 ≤ C8 := coord_mono _ _ (by norm_num)

noncomputable def cb : ℕ := 0 + ((finrank (ZMod 2) C8 - finrank (ZMod 2) C1) + (0 + 0))

theorem cb_eq : cb = 7 := by
  have h8 := finrank_coord 8 (by norm_num)
  have h1 := finrank_coord 1 (by norm_num)
  unfold cb; simp only [C1, C8]; omega

theorem tr_body : Tr (⟨⊤, ⊥, C1⟩ : ES 9) body ⟨⊤ ⊓ C1, ⊥ ⊔ C8, C8⟩ cb :=
  Tr.cons (Step.intake _ rfl) (Tr.cons (Step.up _ C8 C1_le_C8) (Tr.cons (Step.output _) (Tr.nil _)))

theorem q_mem : q 0 ∈ C8 := by
  apply Submodule.subset_span
  exact ⟨⟨1, by norm_num⟩, by simp [q, Pi.basisFun_apply]⟩

theorem dot_zero_of_C1 (t : Fin 8) : ∀ a ∈ C1, a ⬝ᵥ q t = 0 := by
  intro a ha
  induction ha using Submodule.span_induction with
  | mem x hx =>
    obtain ⟨i, rfl⟩ := hx
    have hi : i = 0 := Subsingleton.elim _ _
    subst hi
    simp [q, Pi.basisFun_apply, dotProduct_single]
  | zero => simp
  | add x y _ _ hx hy => simp [add_dotProduct, hx, hy]
  | smul c x _ hx => simp [smul_dotProduct, hx]

noncomputable def ep (j : Fin 8) : Epoch ℚ (Fin 8) 9 := ⟨⊤ ⊓ C1, ⊥ ⊔ C8, cb, ind j, ind j⟩

theorem life1 (j : Fin 8) : Life q C1 [ep j] (0 + cb + 0) :=
  Life.cons C1 [] body ⊤ ⟨⊤, ⊥, C1⟩ ⟨⊤ ⊓ C1, ⊥ ⊔ C8, C8⟩ 0 cb 0 (ind j) (ind j) []
    (Tr.nil _) le_top tr_body
    (fun t _ => Submodule.mem_sup_right q_mem)
    (fun t _ a ha => dot_zero_of_C1 t a (Submodule.mem_inf.1 ha).2)
    (Life.nil _)

theorem mat_w : (Matrix.of (fun (s : Fin 8) (k : Fin 8) => (ep k).w s) : Matrix (Fin 8) (Fin 8) ℚ) = 1 := by
  ext s k
  simp [ep, ind, Matrix.one_apply]

theorem mat_u : (Matrix.of (fun (k : Fin 8) (p : Fin 8) => (ep k).u p) : Matrix (Fin 8) (Fin 8) ℚ) = 1 := by
  ext s k
  simp [ep, ind, Matrix.one_apply, eq_comm]

theorem Nmat_zero : N8.Nmat (0 : Matrix (Fin 8) (Fin 8) ℚ) = 1 := by
  unfold N8.Nmat
  rw [Finset.sum_eq_single 0]
  · simp
  · intro b _ hb; simp [zero_pow hb]
  · simp

/-- **non-vacuity of Rendezvous Lemma A (run form):** all hypotheses hold; `R = Σ c_r = 56` is attained. -/
theorem e8_instance :
    ∃ (c : Fin 8 → ℕ), (∀ r : Fin 8, Life q C1 [ep r] (c r)) ∧ 56 ≤ ∑ r, c r ∧ ∑ r, c r = 56 := by
  have hl : ∀ r : Fin 8, Life q C1 [ep r] (0 + cb + 0) := life1
  have h8 := finrank_coord 8 (by norm_num)
  have h1 := finrank_coord 1 (by norm_num)
  have hsum : ∀ f : Epoch ℚ (Fin 8) 9 → ℕ, ∑ k : Fin 8, f (ep k) = ∑ r : Fin 8, (([ep r] : List _).map f).sum := by
    intro f; simp
  have key := rendezvous_lemma_A_run (m := 8) q (fun _ => C1) (fun r => [ep r]) (fun _ => 0 + cb + 0) hl
    ep hsum 0 (fun k => k.val) Fin.val_injective (by intro k j h; simp at h) (by intro k j h; simp at h)
    (by
      intro k p _
      have : finrank (ZMod 2) (⊤ ⊓ C1 : Chart 9) ≤ finrank (ZMod 2) C1 :=
        Submodule.finrank_mono inf_le_right
      show finrank (ZMod 2) (⊤ ⊓ C1 : Chart 9) ≤ 1
      simp only [C1] at this ⊢; omega)
    (by
      intro s k _
      have : finrank (ZMod 2) C8 ≤ finrank (ZMod 2) (⊥ ⊔ C8 : Chart 9) :=
        Submodule.finrank_mono le_sup_right
      show 8 ≤ finrank (ZMod 2) (⊥ ⊔ C8 : Chart 9)
      simp only [C8] at this ⊢; omega)
    (by
      show 8 ≤ (Matrix.of (fun (s : Fin 8) (k : Fin 8) => (ep k).w s) *
        N8.Nmat (0 : Matrix (Fin 8) (Fin 8) ℚ) *
        Matrix.of (fun (k : Fin 8) (p : Fin 8) => (ep k).u p)).rank
      rw [mat_w, mat_u, Nmat_zero]
      simp)
  refine ⟨fun _ => 0 + cb + 0, hl, key, ?_⟩
  simp [cb_eq]

end CFRelayE8

#print axioms CFRelayE8.finrank_coord
#print axioms CFRelayE8.life1
#print axioms CFRelayE8.e8_instance
