/-
BankWireB .  
Net-level wiring of the flag cuts D_j to the d-mass:
  out_cut / in_cut : per cut j, #banks with d_j(src) < d_j(dst) (resp. >) >= |C|+|E| (resp. |E|), E = counted extras with
                    the chart model of the main contract (OUT: [v]->top, partner []->ker phi; IN: []->ker phi, partner [v]->top)
  bank_sum         : sum_j (out_j + in_j) = sum_k dh(dim src, dim dst)    (NESTED banks, BankWireA.cross_nested_lt)
  field_sum        : sum_j |C_j| = 8 |Fld|                                (fields nested, climb exactly 8)
  hE9              : with n = 9 cuts (window L = 9, all dh <= 9):  field mass + X <= bank mass at L = 9, X = xo + xi.
Premises named (not proved): P-NEST (banks nested), P-CONTRACT (row support {self, partner}, chart model,
partner coefficient nonzero, in-degree 1), principal minors.
Kernel only: no sorry, no native_decide, no new axioms.
-/
import Nov15.BankWireA
import Nov15.BankFlagC2
import Nov15.BankMassF

namespace BankWire
open Finset Module Submodule BankFlag BankNC0 BankFlagC

variable {K L M : Type} {Fld Bank : Type} [Field K] [Field L] [AddCommGroup M] [Module L M] [FiniteDimensional L M]
  [Fintype Fld] [DecidableEq Fld] [Fintype Bank] [LinearOrder Bank]

/-- fields crossing cut j outward -/
noncomputable def Cj (F : ℕ → Submodule L M) (N : Net K (Submodule L M) Fld Bank) (j : ℕ) : Finset Fld :=
  Finset.univ.filter (fun f => d F (N.A f) j < d F (N.B f) j)

theorem out_cut (F : ℕ → Submodule L M) (hmono : ∀ j, F j ≤ F (j+1)) (n : ℕ)
    (hstep : ∀ j, j < n → finrank L (F (j+1)) = finrank L (F j) + 1)
    (N : Net K (Submodule L M) Fld Bank)
    (hminor : ∀ C : Finset Fld,
      (N.O.submatrix (fun c : C => (c : Fld)) (fun c : C => (c : Fld))).det ≠ 0)
    (j : ℕ) (hj : j < n) (E : Finset Fld) (π : Fld → Fld)
    (hE : ∀ e ∈ E, ∃ (v : M) (φ : M →ₗ[L] L), v ∈ F (j+1) ∧ v ∉ F j ∧ F j ≤ LinearMap.ker φ ∧
        ¬ F (j+1) ≤ LinearMap.ker φ ∧ N.A e = span L {v} ∧ N.B e = ⊤ ∧
        N.A (π e) = ⊥ ∧ N.B (π e) = LinearMap.ker φ)
    (hnz : ∀ e ∈ E, N.O e (π e) ≠ 0)
    (hsupp : ∀ f g, N.O f g ≠ 0 → g = f ∨ g = π f)
    (hinj : ∀ e ∈ E, ∀ r ∈ Cj F N j ∪ E, π r = π e → r = e) :
    (Cj F N j).card + E.card ≤
      (Finset.univ.filter (fun k => d F (N.src k) j < d F (N.dst k) j)).card := by
  classical
  have h1 := d_le_one_lt F hmono n hstep
  have key := cut_extras N (fun c => d F c j = 0) (Cj F N j) E π
    (by
      intro c hc
      have hc' := (Finset.mem_filter.mp hc).2
      have := h1 (N.B c) j hj
      exact ⟨by omega, by omega⟩)
    (hminor _)
    (by
      intro e he
      obtain ⟨v, φ, hv1, hv0, hle, hnle, hA, hB, -, -⟩ := hE e he
      rw [hA, hB, d_span F hmono j v hv1 hv0, d_top F hmono j (hstep j hj)]; simp)
    (by
      intro e he
      obtain ⟨v, φ, hv1, hv0, hle, hnle, -, -, hA, hB⟩ := hE e he
      rw [hA, hB, d_bot, d_ker F hmono j (hstep j hj) φ hle hnle]; simp)
    hnz hsupp hinj
  refine le_trans key (le_of_eq ?_)
  congr 1
  apply Finset.filter_congr
  intro k _
  have := h1 (N.dst k) j hj
  constructor
  · rintro ⟨a, b⟩; omega
  · intro h; exact ⟨by omega, by omega⟩

theorem in_cut (F : ℕ → Submodule L M) (hmono : ∀ j, F j ≤ F (j+1)) (n : ℕ)
    (hstep : ∀ j, j < n → finrank L (F (j+1)) = finrank L (F j) + 1)
    (N : Net K (Submodule L M) Fld Bank)
    (j : ℕ) (hj : j < n) (E : Finset Fld) (π : Fld → Fld)
    (hE : ∀ e ∈ E, ∃ (v : M) (φ : M →ₗ[L] L), v ∈ F (j+1) ∧ v ∉ F j ∧ F j ≤ LinearMap.ker φ ∧
        ¬ F (j+1) ≤ LinearMap.ker φ ∧ N.A e = ⊥ ∧ N.B e = LinearMap.ker φ ∧
        N.A (π e) = span L {v} ∧ N.B (π e) = ⊤)
    (hnz : ∀ e ∈ E, N.O e (π e) ≠ 0)
    (hsupp : ∀ f g, N.O f g ≠ 0 → g = f ∨ g = π f)
    (hinj : ∀ e ∈ E, ∀ r ∈ E, π r = π e → r = e) :
    E.card ≤ (Finset.univ.filter (fun k => d F (N.dst k) j < d F (N.src k) j)).card := by
  classical
  have h1 := d_le_one_lt F hmono n hstep
  have key := cut_extras N (fun c => d F c j = 1) (∅ : Finset Fld) E π
    (by intro c hc; simp at hc)
    (by simp)
    (by
      intro e he
      obtain ⟨v, φ, hv1, hv0, hle, hnle, hA, hB, -, -⟩ := hE e he
      rw [hA, hB, d_bot, d_ker F hmono j (hstep j hj) φ hle hnle]; simp)
    (by
      intro e he
      obtain ⟨v, φ, hv1, hv0, hle, hnle, -, -, hA, hB⟩ := hE e he
      rw [hA, hB, d_span F hmono j v hv1 hv0, d_top F hmono j (hstep j hj)]; simp)
    hnz hsupp (by intro e he r hr; exact hinj e he r (by simpa using hr))
  simp only [Finset.card_empty, zero_add] at key
  refine le_trans key (le_of_eq ?_)
  congr 1
  apply Finset.filter_congr
  intro k _
  have := h1 (N.dst k) j hj
  have := h1 (N.src k) j hj
  constructor
  · rintro ⟨a, b⟩; omega
  · intro h; exact ⟨by omega, by omega⟩

/-- sum over cuts of in+out crossings of a nested bank = its height distance. -/
theorem bank_sum (F : ℕ → Submodule L M) (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥) (n : ℕ)
    (hstep : ∀ j, j < n → finrank L (F (j+1)) = finrank L (F j) + 1) (hFn : F n = ⊤)
    (N : Net K (Submodule L M) Fld Bank)
    (hnest : ∀ k, N.src k ≤ N.dst k ∨ N.dst k ≤ N.src k) :
    ∑ j ∈ range n, ((Finset.univ.filter (fun k => d F (N.src k) j < d F (N.dst k) j)).card +
        (Finset.univ.filter (fun k => d F (N.dst k) j < d F (N.src k) j)).card)
      = ∑ k, dh (finrank L (N.src k)) (finrank L (N.dst k)) := by
  rw [Finset.sum_add_distrib]
  simp_rw [Finset.card_filter]
  rw [Finset.sum_comm, Finset.sum_comm (s := range n) (t := (Finset.univ : Finset Bank))]
  rw [← Finset.sum_add_distrib]
  refine Finset.sum_congr rfl (fun k _ => ?_)
  rw [← Finset.sum_add_distrib]
  have hle : ∀ c : Submodule L M, c ≤ F n := fun c => hFn ▸ le_top
  rcases hnest k with h | h
  · obtain ⟨a, b⟩ := cross_nested_lt F hmono h0 n hstep _ _ h (hle _)
    rw [Finset.card_filter] at a b
    have := Submodule.finrank_mono h
    have e : ∀ j ∈ range n, ((if d F (N.src k) j < d F (N.dst k) j then 1 else 0) +
        (if d F (N.dst k) j < d F (N.src k) j then 1 else 0)) =
        (if d F (N.src k) j < d F (N.dst k) j then 1 else 0) + 0 := by
      intro j _
      have : ¬ d F (N.dst k) j < d F (N.src k) j := fun hh => by
        have := d_mono F _ _ h j; omega
      simp [this]
    rw [Finset.sum_congr rfl e, Finset.sum_add_distrib, a]
    unfold dh; simp; omega
  · obtain ⟨a, b⟩ := cross_nested_lt F hmono h0 n hstep _ _ h (hle _)
    rw [Finset.card_filter] at a b
    have := Submodule.finrank_mono h
    have e : ∀ j ∈ range n, ((if d F (N.src k) j < d F (N.dst k) j then 1 else 0) +
        (if d F (N.dst k) j < d F (N.src k) j then 1 else 0)) =
        0 + (if d F (N.dst k) j < d F (N.src k) j then 1 else 0) := by
      intro j _
      have : ¬ d F (N.src k) j < d F (N.dst k) j := fun hh => by
        have := d_mono F _ _ h j; omega
      simp [this]
    rw [Finset.sum_congr rfl e, Finset.sum_add_distrib, a]
    unfold dh; simp; omega

/-- fields (nested, climbing exactly c) cross exactly c cuts each. -/
theorem field_sum (F : ℕ → Submodule L M) (hmono : ∀ j, F j ≤ F (j+1)) (h0 : F 0 = ⊥) (n : ℕ)
    (hstep : ∀ j, j < n → finrank L (F (j+1)) = finrank L (F j) + 1) (hFn : F n = ⊤)
    (N : Net K (Submodule L M) Fld Bank) (c : ℕ)
    (hclimb : ∀ f, N.A f ≤ N.B f ∧ finrank L (N.B f) = finrank L (N.A f) + c) :
    ∑ j ∈ range n, (Cj F N j).card = c * Fintype.card Fld := by
  have hle : ∀ x : Submodule L M, x ≤ F n := fun x => hFn ▸ le_top
  unfold Cj
  simp_rw [Finset.card_filter]
  rw [Finset.sum_comm]
  have : ∀ f ∈ (Finset.univ : Finset Fld),
      ∑ j ∈ range n, (if d F (N.A f) j < d F (N.B f) j then 1 else 0) = c := by
    intro f _
    obtain ⟨a, -⟩ := cross_nested_lt F hmono h0 n hstep _ _ (hclimb f).1 (hle _)
    rw [Finset.card_filter] at a
    rw [a]; have := (hclimb f).2; omega
  rw [Finset.sum_congr rfl this]; simp [mul_comm]

end BankWire
