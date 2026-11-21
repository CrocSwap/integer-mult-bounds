import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.GroupTheory.Index
import Mathlib.FieldTheory.Finiteness
import Mathlib.NumberTheory.Padics.RingHoms

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

/-! # HalvingLaw: the Z/4 halving law (CARRYPOT §1)
Part A (copied defs from TensorPot, F2 layer). Part B: Z/4 potential. -/
namespace HalvingLaw
open Module

section dims
variable {K V T : Type*} [Field K] [AddCommGroup V] [Module K V] [FiniteDimensional K V]
  [AddCommGroup T] [Module K T] [FiniteDimensional K T]

lemma map_dim_le (f : V →ₗ[K] T) {C D : Submodule K V} (h : C ≤ D) :
    finrank K (D.map f) + finrank K C ≤ finrank K (C.map f) + finrank K D := by
  have hD := LinearMap.finrank_range_add_finrank_ker (f.domRestrict D)
  have hC := LinearMap.finrank_range_add_finrank_ker (f.domRestrict C)
  rw [LinearMap.range_domRestrict] at hD hC
  have hk : finrank K (LinearMap.ker (f.domRestrict C)) ≤ finrank K (LinearMap.ker (f.domRestrict D)) := by
    have e1 := Submodule.finrank_map_subtype_eq C (LinearMap.ker (f.domRestrict C))
    have e2 := Submodule.finrank_map_subtype_eq D (LinearMap.ker (f.domRestrict D))
    rw [← e1, ← e2]
    apply Submodule.finrank_mono
    rintro x ⟨y, hy, rfl⟩
    refine ⟨⟨y.1, h y.2⟩, ?_, rfl⟩
    simpa [LinearMap.mem_ker] using hy
  omega

/-- ascent lemma -/
lemma ascent_dim (f : V →ₗ[K] T) {C D : Submodule K V} (h : C ≤ D) (S : Submodule K T)
    (hS : C.map f ≤ S) :
    finrank K (S ⊔ D.map f : Submodule K T) + finrank K C ≤ finrank K S + finrank K D := by
  have h1 := Submodule.finrank_sup_add_finrank_inf_eq S (D.map f)
  have h2 := Submodule.finrank_mono (le_inf hS (Submodule.map_mono h) : C.map f ≤ S ⊓ D.map f)
  have h3 := map_dim_le f h
  omega
end dims

section model
open Finset Function
variable {K : Type*} [Field K] {ν ω ι : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι]

/-- `c ↦ c ⊗ w`, as the outer-product matrix `c wᵀ` (V ⊗ W ≅ Matrix ν ω K). -/
def outer (w : ω → K) : (ν → K) →ₗ[K] Matrix ν ω K where
  toFun c := Matrix.vecMulVec c w
  map_add' a b := by ext i j; simp [Matrix.vecMulVec, add_mul]
  map_smul' a b := by ext i j; simp [Matrix.vecMulVec, mul_assoc]

lemma outer_apply (w : ω → K) (c : ν → K) : outer w c = Matrix.vecMulVec c w := rfl

/-- `C ⊗ w`. -/
def pot (C : Submodule K (ν → K)) (w : ω → K) : Submodule K (Matrix ν ω K) := C.map (outer w)

lemma pot_zero (C : Submodule K (ν → K)) : pot C (0 : ω → K) = ⊥ := by
  unfold pot
  rw [eq_bot_iff]; rintro _ ⟨c, -, rfl⟩
  ext i j; simp [outer_apply, Matrix.vecMulVec]

lemma pot_mono {C D : Submodule K (ν → K)} (h : C ≤ D) (w : ω → K) : pot C w ≤ pot D w :=
  Submodule.map_mono h

structure St (K ν ω ι : Type*) [Field K] where
  ch : ι → Submodule K (ν → K)
  v : ι → (ω → K)


/-- Start / final potentials of the publics. -/
def S0 (P : Finset ι) (s : St K ν ω ι) : Submodule K (Matrix ν ω K) :=
  ⨆ r ∈ P, pot (s.ch r) (s.v r)


lemma finrank_biSup_le {T : Type*} [AddCommGroup T] [Module K T] [FiniteDimensional K T]
    (f : ι → Submodule K T) (F : Finset ι) :
    finrank K (⨆ r ∈ F, f r : Submodule K T) ≤ ∑ r ∈ F, finrank K (f r) := by
  induction F using Finset.induction_on with
  | empty => simp
  | insert a F ha ih =>
    rw [Finset.iSup_insert, Finset.sum_insert ha]
    exact le_trans (Submodule.finrank_add_le_finrank_add_finrank _ _) (by omega)

lemma finrank_S0_le (P : Finset ι) (s : St K ν ω ι) :
    finrank K (S0 P s) ≤ ∑ r ∈ P, finrank K (s.ch r) :=
  le_trans (finrank_biSup_le _ P) (Finset.sum_le_sum fun r _ => Submodule.finrank_map_le _ _)

section toy
variable {Q J O : Type*} [Fintype Q] [Fintype J] [Fintype O]
  [DecidableEq Q] [DecidableEq J] [DecidableEq O]

/-- value coordinates: `x`-block, `y`-block, relay block -/
abbrev Wd (Q J : Type*) := Q ⊕ Q ⊕ J
/-- registers: publics `X_t`, `Y_t`, relays, then owned -/
abbrev Rg (Q J O : Type*) := (Q ⊕ Q ⊕ J) ⊕ O

def eX (t : Q) : Wd Q J → K := Sum.elim (Pi.single t 1) 0
def eY (t : Q) : Wd Q J → K := Sum.elim 0 (Sum.elim (Pi.single t 1) 0)
def eZ (j : J) : Wd Q J → K := Sum.elim 0 (Sum.elim 0 (Pi.single j 1))
/-- final value of `X_t`: `x_t + Σ_s M t s · y_s` -/
def finX (M : Matrix Q Q K) (t : Q) : Wd Q J → K := Sum.elim (Pi.single t 1) (Sum.elim (M t) 0)
/-- the `y`-part `Σ_s M t s · y_s` -/
def mY (M : Matrix Q Q K) (t : Q) : Wd Q J → K := Sum.elim 0 (Sum.elim (M t) 0)

def dotLin (q : ν → K) : (ν → K) →ₗ[K] K where
  toFun v := q ⬝ᵥ v
  map_add' a b := dotProduct_add _ _ _
  map_smul' a b := by simp [dotProduct_smul]

/-- `q^⊥` for the standard dot product -/
def perp (q : ν → K) : Submodule K (ν → K) := LinearMap.ker (dotLin q)

lemma mem_perp {q c : ν → K} : c ∈ perp q ↔ q ⬝ᵥ c = 0 := Iff.rfl

/-- Start state: `X_t : ⟨q_t⟩, x_t`; `Y_t : {0}, y_t`; relay `j : S_j, z_j`; owned: any chart, value 0. -/
def toyStart (q : Q → ν → K) (Sj : J → Submodule K (ν → K)) (A0 : O → Submodule K (ν → K)) :
    St K ν (Wd Q J) (Rg Q J O) where
  ch := Sum.elim (Sum.elim (fun t => Submodule.span K {q t}) (Sum.elim (fun _ => ⊥) Sj)) A0
  v := Sum.elim (Sum.elim eX (Sum.elim eY eZ)) (fun _ => 0)

/-- Final state: `X_t : V, x_t + M_t y`; `Y_t : q_t^⊥, y_t`; relay `j : F_j, z_j`; owned arbitrary. -/
def toyFinal (q : Q → ν → K) (M : Matrix Q Q K) (Fj : J → Submodule K (ν → K))
    (A1 : O → Submodule K (ν → K)) (V1 : O → Wd Q J → K) : St K ν (Wd Q J) (Rg Q J O) where
  ch := Sum.elim (Sum.elim (fun _ => ⊤) (Sum.elim (fun s => perp (q s)) Fj)) A1
  v := Sum.elim (Sum.elim (finX M) (Sum.elim eY eZ)) V1

/-- the public registers -/
def pubs (Q J O : Type*) [Fintype Q] [Fintype J] : Finset (Rg Q J O) :=
  Finset.univ.map Function.Embedding.inl

lemma mem_pubs {r : Rg Q J O} : r ∈ pubs Q J O ↔ ∃ a, r = Sum.inl a := by
  simp [pubs, eq_comm]

lemma mem_S0 {P : Finset ι} {s : St K ν ω ι} {r : ι} (hr : r ∈ P) {x : Matrix ν ω K}
    (hx : x ∈ pot (s.ch r) (s.v r)) : x ∈ S0 P s :=
  Submodule.mem_iSup_of_mem r (Submodule.mem_iSup_of_mem hr hx)

lemma mem_pot {C : Submodule K (ν → K)} {w : ω → K} {c : ν → K} (hc : c ∈ C) :
    outer w c ∈ pot C w := ⟨c, hc, rfl⟩

/-- projection onto the `x`-columns -/
def piX : Matrix ν (Wd Q J) K →ₗ[K] Matrix ν Q K where
  toFun m := Matrix.of fun i t => m i (Sum.inl t)
  map_add' a b := rfl
  map_smul' a b := rfl

lemma piX_apply (m : Matrix ν (Wd Q J) K) (i : ν) (t : Q) : piX m i t = m i (Sum.inl t) := rfl

/-- `ψ m = (q_s · (y_s-column of m))_s` -/
def psiY (q : Q → ν → K) : Matrix ν (Wd Q J) K →ₗ[K] (Q → K) where
  toFun m := fun s => ∑ i, q s i * m i (Sum.inr (Sum.inl s))
  map_add' a b := by funext s; simp [mul_add, Finset.sum_add_distrib]
  map_smul' a b := by funext s; simp [Finset.mul_sum, mul_left_comm]

/-- the injection of `Π_s q_s^⊥ × Π_j F_j` into the `y`- and relay-columns -/
def Phi (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) :
    ((s : Q) → perp (q s)) × ((j : J) → Fj j) →ₗ[K] Matrix ν (Wd Q J) K :=
  LinearMap.coprod
    (∑ s, (outer (eY s)).comp ((perp (q s)).subtype.comp (LinearMap.proj s)))
    (∑ j, (outer (eZ j)).comp ((Fj j).subtype.comp (LinearMap.proj j)))

lemma Phi_inl (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) (i : ν) (t : Q) :
    Phi q Fj x i (Sum.inl t) = 0 := by
  simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply, Matrix.sum_apply, outer_apply,
    Matrix.vecMulVec, eY, eZ]

lemma Phi_y (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) (i : ν) (t : Q) :
    Phi q Fj x i (Sum.inr (Sum.inl t)) = (x.1 t : ν → K) i := by
  simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply, Matrix.sum_apply, outer_apply,
    Matrix.vecMulVec, eY, eZ, Pi.single_apply]

lemma Phi_z (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) (i : ν) (j : J) :
    Phi q Fj x i (Sum.inr (Sum.inr j)) = (x.2 j : ν → K) i := by
  simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply, Matrix.sum_apply, outer_apply,
    Matrix.vecMulVec, eY, eZ, Pi.single_apply]

lemma Phi_inj (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) : Function.Injective (Phi q Fj) := by
  rintro ⟨c, f⟩ ⟨c', f'⟩ h
  refine Prod.ext (funext fun s => Subtype.ext (funext fun i => ?_))
    (funext fun j => Subtype.ext (funext fun i => ?_))
  · have := congrFun (congrFun h i) (Sum.inr (Sum.inl s))
    simpa [Phi_y] using this
  · have := congrFun (congrFun h i) (Sum.inr (Sum.inr j))
    simpa [Phi_z] using this

lemma psi_Phi (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) : psiY q (Phi q Fj x) = 0 := by
  funext s
  have h : q s ⬝ᵥ (x.1 s : ν → K) = 0 := (mem_perp).1 (x.1 s).2
  simp only [psiY, LinearMap.coe_mk, AddHom.coe_mk, Phi_y, Pi.zero_apply]
  exact h

lemma piX_Phi (q : Q → ν → K) (Fj : J → Submodule K (ν → K)) (x) : piX (Phi q Fj x) = 0 := by
  ext i t; exact Phi_inl q Fj x i t


variable (q : Q → ν → K) (M : Matrix Q Q K) (Sj Fj : J → Submodule K (ν → K))
  (A0 A1 : O → Submodule K (ν → K)) (V1 : O → Wd Q J → K)

/-- Hadamard product `Q ∘ M`, `Q_ts = q_t · q_s`. -/
def had : Matrix Q Q K := Matrix.of fun t s => (q t ⬝ᵥ q s) * M t s

/-- the span `S0 + T` of the toy -/
def toyA : Submodule K (Matrix ν (Wd Q J) K) :=
  S0 (pubs Q J O) (toyStart q Sj A0) ⊔ S0 (pubs Q J O) (toyFinal q M Fj A1 V1)

/-- **Toy lower bound.** `dim(S0 + T) ≥ |ν||Q| + Σ_s dim q_s^⊥ + Σ_j dim F_j + rank(Q∘M)`. -/
theorem toy_lower :
    Fintype.card ν * Fintype.card Q + (∑ s, finrank K (perp (q s))) + (∑ j, finrank K (Fj j)) + (had q M).rank
      ≤ finrank K (toyA q M Sj Fj A0 A1 V1) := by
  set A := toyA q M Sj Fj A0 A1 V1 with hA
  have hmemF : ∀ a : Q ⊕ Q ⊕ J, ∀ x, x ∈ pot ((toyFinal q M Fj A1 V1).ch (Sum.inl a))
      ((toyFinal q M Fj A1 V1).v (Sum.inl a)) → x ∈ A := fun a x hx =>
    Submodule.mem_sup_right (mem_S0 (mem_pubs.2 ⟨a, rfl⟩) hx)
  have hmemS : ∀ a : Q ⊕ Q ⊕ J, ∀ x, x ∈ pot ((toyStart q Sj A0).ch (Sum.inl a))
      ((toyStart q Sj A0).v (Sum.inl a)) → x ∈ A := fun a x hx =>
    Submodule.mem_sup_left (mem_S0 (mem_pubs.2 ⟨a, rfl⟩) hx)
  -- generators of A
  have hX : ∀ t v, outer (finX M t) v ∈ A := fun t v =>
    hmemF (Sum.inl t) _ (mem_pot (C := ⊤) Submodule.mem_top)
  have hX0 : ∀ t, outer (eX t) (q t) ∈ A := fun t =>
    hmemS (Sum.inl t) _ (mem_pot (Submodule.mem_span_singleton_self (q t)))
  have hY : ∀ s c, c ∈ perp (q s) → outer (eY s) c ∈ A := fun s c hc =>
    hmemF (Sum.inr (Sum.inl s)) _ (mem_pot hc)
  have hZ : ∀ j c, c ∈ Fj j → outer (eZ j) c ∈ A := fun j c hc =>
    hmemF (Sum.inr (Sum.inr j)) _ (mem_pot hc)
  -- K' = range Φ ⊔ Kc
  set Kb := LinearMap.range (Phi q Fj) with hKb
  set Kc : Submodule K (Matrix ν (Wd Q J) K) :=
    Submodule.span K (Set.range fun t => Matrix.vecMulVec (q t) (mY M t)) with hKc
  have hKcA : Kc ≤ A := by
    rw [hKc, Submodule.span_le]
    rintro _ ⟨t, rfl⟩
    have : Matrix.vecMulVec (q t) (mY (J := J) M t) =
        outer (finX (J := J) M t) (q t) - outer (eX (J := J) t) (q t) := by
      ext i w; rcases w with x | y | z <;> simp [outer_apply, Matrix.vecMulVec, finX, eX, mY, Pi.single_apply]
    show Matrix.vecMulVec (q t) (mY M t) ∈ A
    rw [this]; exact A.sub_mem (hX t (q t)) (hX0 t)
  have hKbA : Kb ≤ A := by
    rintro _ ⟨⟨c, f⟩, rfl⟩
    have : Phi q Fj (c, f) = ∑ s, outer (eY s) (c s : ν → K) + ∑ j, outer (eZ j) (f j : ν → K) := by
      simp [Phi, LinearMap.coprod_apply, LinearMap.sum_apply]
    rw [this]
    exact A.add_mem (A.sum_mem fun s _ => hY s _ (c s).2) (A.sum_mem fun j _ => hZ j _ (f j).2)
  obtain ⟨K', hK'⟩ : ∃ K' : Submodule K (Matrix ν (Wd Q J) K), K' = Kb ⊔ Kc := ⟨_, rfl⟩
  have hKb' : Kb ≤ K' := hK' ▸ le_sup_left
  have hKc' : Kc ≤ K' := hK' ▸ le_sup_right
  have hK'A : K' ≤ A := hK' ▸ sup_le hKbA hKcA
  -- Step 1: A.map piX = ⊤
  have hpi : A.map piX = ⊤ := by
    rw [eq_top_iff]; intro m _
    have hm : m = ∑ t : Q, piX (outer (finX (J := J) M t) (fun i => m i t)) := by
      ext i t'
      simp [Matrix.sum_apply, piX_apply, outer_apply, Matrix.vecMulVec, finX, Pi.single_apply]
    rw [hm]
    exact Submodule.sum_mem _ fun t _ => ⟨outer (finX (J := J) M t) (fun i => m i t), hX t _, rfl⟩
  have hker : K' ≤ LinearMap.ker piX := by
    rw [hK']
    refine sup_le ?_ ?_
    · rintro _ ⟨x, rfl⟩; exact piX_Phi q Fj x
    · rw [hKc, Submodule.span_le]
      rintro _ ⟨t, rfl⟩
      show piX _ = 0
      ext i t'
      show q t i * mY (J := J) M t (Sum.inl t') = 0
      simp [mY]
  have hmapbot : K'.map piX = ⊥ := eq_bot_iff.2 (Submodule.map_le_iff_le_comap.2 hker)
  have d1 := map_dim_le piX hK'A
  rw [hpi, hmapbot, finrank_top, Module.finrank_matrix, finrank_bot, Module.finrank_self, mul_one] at d1
  -- Step 2
  have hker2 : Kb ≤ LinearMap.ker (psiY q) := by
    rintro _ ⟨x, rfl⟩; exact psi_Phi q Fj x
  have hmapbot2 : Kb.map (psiY q) = ⊥ := eq_bot_iff.2 (Submodule.map_le_iff_le_comap.2 hker2)
  have d2 := map_dim_le (psiY q) hKb'
  rw [hmapbot2, finrank_bot] at d2
  have hrows : Submodule.span K (Set.range (had q M).row) ≤ K'.map (psiY q) := by
    rw [Submodule.span_le]
    rintro _ ⟨t, rfl⟩
    refine ⟨Matrix.vecMulVec (q t) (mY M t),
      hKc' (Submodule.subset_span ⟨t, rfl⟩), ?_⟩
    funext s
    simp only [psiY, LinearMap.coe_mk, AddHom.coe_mk, Matrix.row, had, Matrix.of_apply]
    simp only [Matrix.vecMulVec, Matrix.of_apply, mY, Sum.elim_inr, Sum.elim_inl, dotProduct]
    rw [Finset.sum_mul]
    exact Finset.sum_congr rfl fun i _ => by ring
  have d3 := Submodule.finrank_mono hrows
  rw [← Matrix.rank_eq_finrank_span_row] at d3
  have d4 : finrank K Kb = (∑ s, finrank K (perp (q s))) + ∑ j, finrank K (Fj j) := by
    rw [hKb, LinearMap.finrank_range_of_inj (Phi_inj q Fj), Module.finrank_prod,
      Module.finrank_pi_fintype, Module.finrank_pi_fintype]
  omega


end toy
end model

/-! # Part B: the Z/4 layer -/
section Z4
open Finset Function

variable {ν ω ι : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι]

instance fin_mat4 : Finite (Matrix ν ω (ZMod 4)) := inferInstanceAs (Finite (ν → ω → ZMod 4))

lemma natcard_pi (m : ℕ) [NeZero m] : Nat.card (ν → ZMod m) = m ^ Fintype.card ν := by
  rw [Nat.card_fun, Nat.card_zmod, Nat.card_eq_fintype_card (α := ν)]

lemma natcard_F2 {V : Type*} [AddCommGroup V] [Module (ZMod 2) V] [Module.Finite (ZMod 2) V]
    (C : Submodule (ZMod 2) V) :
    Nat.card C.toAddSubgroup = 2 ^ finrank (ZMod 2) C := by
  have h := Module.natCard_eq_pow_finrank (K := ZMod 2) (V := C)
  rw [Nat.card_zmod] at h
  exact h

/-! ## cardinality lemmas for additive groups -/
section card
variable {V T : Type*} [AddCommGroup V] [AddCommGroup T] [Finite V] [Finite T]

/-- ascent lemma, multiplicative form (the Z/4 analogue of `ascent_dim`):
`|S + f D| · |C| ≤ |S| · |D|` when `f C ⊆ S`, `C ≤ D`. -/
lemma ascent_card (f : V →+ T) {C D : AddSubgroup V} (h : C ≤ D) (S : AddSubgroup T)
    (hS : C.map f ≤ S) :
    Nat.card (S ⊔ D.map f : AddSubgroup T) * Nat.card C ≤ Nat.card S * Nat.card D := by
  have e1 : Nat.card S * S.relIndex (S ⊔ D.map f) = Nat.card (S ⊔ D.map f : AddSubgroup T) := by
    have := AddSubgroup.relIndex_mul_relIndex ⊥ S (S ⊔ D.map f) bot_le le_sup_left
    simpa only [AddSubgroup.relIndex_bot_left] using this
  have e2 : S.relIndex (S ⊔ D.map f) = (S.comap f).relIndex D := by
    rw [AddSubgroup.relIndex_sup_left, AddSubgroup.relIndex_comap]
  have e4 : (S.comap f).relIndex D ∣ C.relIndex D :=
    AddSubgroup.relIndex_dvd_of_le_left D (AddSubgroup.map_le_iff_le_comap.1 hS)
  have e5 : Nat.card C * C.relIndex D = Nat.card D := by
    have := AddSubgroup.relIndex_mul_relIndex ⊥ C D bot_le h
    simpa only [AddSubgroup.relIndex_bot_left] using this
  have hpos : 0 < C.relIndex D := by
    rcases Nat.eq_zero_or_pos (C.relIndex D) with h0 | h0
    · have : Nat.card D = 0 := by rw [← e5, h0]; simp
      exact absurd this (Nat.card_pos (α := D)).ne'
    · exact h0
  have hle := Nat.le_of_dvd hpos e4
  rw [← e1, e2, ← e5]
  calc Nat.card S * (S.comap f).relIndex D * Nat.card C
      ≤ Nat.card S * C.relIndex D * Nat.card C := by gcongr
    _ = Nat.card S * (Nat.card C * C.relIndex D) := by ring

end card

end Z4

section Z4b
open Finset Function
variable {ν ω ι : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι]

/-- reduction mod 2 of a vector over `Z/4` -/
def redH : (ν → ZMod 4) →+ (ν → ZMod 2) where
  toFun x i := ZMod.castHom (show 2 ∣ 4 by norm_num) (ZMod 2) (x i)
  map_zero' := by ext; simp
  map_add' a b := by ext; simp

lemma redH_apply (x : ν → ZMod 4) (i : ν) :
    redH x i = ZMod.castHom (show 2 ∣ 4 by norm_num) (ZMod 2) (x i) := rfl

lemma redH_surj : Function.Surjective (redH (ν := ν)) := by
  intro y
  refine ⟨fun i => ((y i).val : ZMod 4), ?_⟩
  funext i
  rw [redH_apply, map_natCast, ZMod.natCast_zmod_val]

/-- the canonical lift `Ĉ` = preimage of an `F₂`-chart `C` in `(Z/4)^ν` -/
def hat (C : Submodule (ZMod 2) (ν → ZMod 2)) : AddSubgroup (ν → ZMod 4) :=
  C.toAddSubgroup.comap redH

lemma hat_mono {C D : Submodule (ZMod 2) (ν → ZMod 2)} (h : C ≤ D) : hat C ≤ hat D :=
  AddSubgroup.comap_mono h

lemma mem_hat {C : Submodule (ZMod 2) (ν → ZMod 2)} {x : ν → ZMod 4} :
    x ∈ hat C ↔ redH x ∈ C := Iff.rfl

/-- `|Ĉ| = 2^(dim C + n)`. -/
lemma card_hat (C : Submodule (ZMod 2) (ν → ZMod 2)) :
    Nat.card (hat C) = 2 ^ (finrank (ZMod 2) C + Fintype.card ν) := by
  have h1 := AddSubgroup.card_mul_index (hat C)
  have h2 := AddSubgroup.card_mul_index C.toAddSubgroup
  have h3 : (hat C).index = C.toAddSubgroup.index :=
    AddSubgroup.index_comap_of_surjective C.toAddSubgroup redH_surj
  rw [natcard_pi 4, h3] at h1
  rw [natcard_pi 2, natcard_F2] at h2
  have hi : 0 < C.toAddSubgroup.index := by
    rcases Nat.eq_zero_or_pos C.toAddSubgroup.index with h0 | h0
    · exfalso
      rw [h0] at h2
      have : 0 < 2 ^ Fintype.card ν := by positivity
      omega
    · exact h0
  have h4 : (4 : ℕ) ^ Fintype.card ν = 2 ^ Fintype.card ν * 2 ^ Fintype.card ν := by
    rw [← mul_pow]; norm_num
  have : Nat.card (hat C) * C.toAddSubgroup.index =
      2 ^ (finrank (ZMod 2) C + Fintype.card ν) * C.toAddSubgroup.index := by
    rw [h1, h4, pow_add]
    calc 2 ^ Fintype.card ν * 2 ^ Fintype.card ν
        = 2 ^ Fintype.card ν * (2 ^ finrank (ZMod 2) C * C.toAddSubgroup.index) := by rw [h2]
      _ = _ := by ring
  exact Nat.eq_of_mul_eq_mul_right hi this

def outer4 (w : ω → ZMod 4) : (ν → ZMod 4) →+ Matrix ν ω (ZMod 4) where
  toFun c := Matrix.vecMulVec c w
  map_zero' := by ext i j; simp [Matrix.vecMulVec]
  map_add' a b := by ext i j; simp [Matrix.vecMulVec, add_mul]

lemma outer4_apply (w : ω → ZMod 4) (c : ν → ZMod 4) (i j) : outer4 w c i j = c i * w j := rfl

/-- `Ĉ ⊗ [w]` -/
def pot4 (C : Submodule (ZMod 2) (ν → ZMod 2)) (w : ω → ZMod 4) :
    AddSubgroup (Matrix ν ω (ZMod 4)) := (hat C).map (outer4 w)

lemma pot4_zero (C : Submodule (ZMod 2) (ν → ZMod 2)) : pot4 C (0 : ω → ZMod 4) = ⊥ := by
  unfold pot4
  rw [eq_bot_iff]; rintro _ ⟨c, -, rfl⟩
  ext i j; simp [outer4_apply]

lemma pot4_mono {C D : Submodule (ZMod 2) (ν → ZMod 2)} (h : C ≤ D) (w : ω → ZMod 4) :
    pot4 C w ≤ pot4 D w := AddSubgroup.map_mono (hat_mono h)

lemma mem_pot4 {C : Submodule (ZMod 2) (ν → ZMod 2)} {w : ω → ZMod 4} {c : ν → ZMod 4}
    (hc : c ∈ hat C) : outer4 w c ∈ pot4 C w := ⟨c, hc, rfl⟩

lemma smul_mem4 {T : Type*} [AddCommGroup T] [Module (ZMod 4) T] (S : AddSubgroup T) (z : ZMod 4)
    {x : T} (hx : x ∈ S) : z • x ∈ S := by
  have : z • x = z.val • x := by
    conv_lhs => rw [← ZMod.natCast_zmod_val z]
    exact Nat.cast_smul_eq_nsmul (ZMod 4) _ _
  rw [this]; exact S.nsmul_mem hx _

/-- **Halving lemma (cost ≤ n).** If `θ(2a) ∈ S` for every `a` in `A ≤ (Z/4)^n` then
adjoining `θ(A)` to `S` at most multiplies `|S|` by `2^n`. -/
lemma halve_card (θ : (ν → ZMod 4) →+ Matrix ν ω (ZMod 4)) (A : AddSubgroup (ν → ZMod 4))
    (S : AddSubgroup (Matrix ν ω (ZMod 4))) (hθ : ∀ a ∈ A, θ (a + a) ∈ S) :
    Nat.card (S ⊔ A.map θ : AddSubgroup _) ≤ Nat.card S * 2 ^ Fintype.card ν := by
  let m : (ν → ZMod 4) →+ (ν → ZMod 4) := AddMonoidHom.mk' (fun x => x + x) (by intros; abel)
  have e1 : Nat.card S * S.relIndex (S ⊔ A.map θ) = Nat.card (S ⊔ A.map θ : AddSubgroup _) := by
    have := AddSubgroup.relIndex_mul_relIndex ⊥ S (S ⊔ A.map θ) bot_le le_sup_left
    simpa only [AddSubgroup.relIndex_bot_left] using this
  have e2 : S.relIndex (S ⊔ A.map θ) = (S.comap θ).relIndex A := by
    rw [AddSubgroup.relIndex_sup_left, AddSubgroup.relIndex_comap]
  have hT : A.map m ≤ S.comap θ := by
    rintro _ ⟨a, ha, rfl⟩
    exact hθ a ha
  have e4 : (S.comap θ).relIndex A ∣ (A.map m).relIndex A :=
    AddSubgroup.relIndex_dvd_of_le_left A hT
  have hTA : A.map m ≤ A := by
    rintro _ ⟨a, ha, rfl⟩
    exact A.add_mem ha ha
  have e5 : Nat.card (A.map m) * (A.map m).relIndex A = Nat.card A := by
    have := AddSubgroup.relIndex_mul_relIndex ⊥ (A.map m) A bot_le hTA
    simpa only [AddSubgroup.relIndex_bot_left] using this
  have e6 : Nat.card (m.ker ⊓ A : AddSubgroup _) * Nat.card (A.map m) = Nat.card A := by
    have := AddSubgroup.relIndex_mul_relIndex ⊥ (m.ker ⊓ A) A bot_le inf_le_right
    simp only [AddSubgroup.relIndex_bot_left, AddSubgroup.inf_relIndex_right,
      AddSubgroup.relIndex_ker] at this
    exact this
  have hposT : 0 < Nat.card (A.map m) := Nat.card_pos
  have e7 : (A.map m).relIndex A = Nat.card (m.ker ⊓ A : AddSubgroup _) := by
    apply Nat.eq_of_mul_eq_mul_left hposT
    rw [e5, ← e6, mul_comm]
  have e8 : Nat.card (m.ker ⊓ A : AddSubgroup _) ≤ 2 ^ Fintype.card ν := by
    let g : (m.ker ⊓ A : AddSubgroup _) → (ν → Bool) := fun x i => decide (x.1 i = 2)
    have hg : Function.Injective g := by
      intro x y hxy
      apply Subtype.ext; funext i
      have hx : x.1 i + x.1 i = 0 := congrFun (AddMonoidHom.mem_ker.1 x.2.1) i
      have hy : y.1 i + y.1 i = 0 := congrFun (AddMonoidHom.mem_ker.1 y.2.1) i
      have hb := congrFun hxy i
      simp only [g] at hb
      generalize x.1 i = a at *
      generalize y.1 i = b at *
      revert a b; decide
    have := Nat.card_le_card_of_injective g hg
    simpa [Nat.card_fun, Nat.card_eq_fintype_card (α := ν)] using this
  have hle := Nat.le_of_dvd (by rw [e7]; exact Nat.card_pos) e4
  rw [← e1, e2]
  calc Nat.card S * (S.comap θ).relIndex A ≤ Nat.card S * 2 ^ Fintype.card ν := by
        apply Nat.mul_le_mul_left
        rw [e7] at hle
        exact hle.trans e8

end Z4b

section Z4c
open Finset Function
variable {ν ω ι Λ : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι] [CommRing Λ]

/-- Dyadic register state. Charts are `F₂`-subspaces of `F₂^ν`; the value of register `r` is
`w_r = a_r / 2` (so `den ≤ 2`), stored as the *doubled* vector `a_r ∈ Λ^ω`
(`Λ = ℤ` or `ℤ_[2]`, with a ring map `ρ : Λ → Z/4`); its encoding is `[w_r] = ρ(a_r) = 2 w_r mod 4`. -/
structure St4 (ν ω ι Λ : Type*) where
  ch : ι → Submodule (ZMod 2) (ν → ZMod 2)
  a : ι → ω → Λ

variable (ρ : Λ →+* ZMod 4)

/-- the encoded value `[w_r] = ρ(a_r)` -/
def enc (s : St4 ν ω ι Λ) (r : ι) : ω → ZMod 4 := fun j => ρ (s.a r j)

/-- potential of a state: `Σ_r Ĉ_r ⊗ [w_r]` (a subgroup of `(Z/4)^{ν×ω}`) -/
def potOf4 (s : St4 ν ω ι Λ) : AddSubgroup (Matrix ν ω (ZMod 4)) :=
  ⨆ r, pot4 (s.ch r) (enc ρ s r)

lemma potOf4_le_iff (s : St4 ν ω ι Λ) (S : AddSubgroup (Matrix ν ω (ZMod 4))) :
    potOf4 ρ s ≤ S ↔ ∀ r, pot4 (s.ch r) (enc ρ s r) ≤ S := iSup_le_iff

/-- Moves. `add`: integral (`Λ`) scalar; includes every carry. `halve`: `w_d += (u/2) w_e` where
the source value `w_e = b` is integral (`a_e = 2 b`); the result is again dyadic (`a_d += u b`).
The last index counts halvings. Publics never descend; discard = descent to `⊥` (owned only). -/
inductive Mv4 (P : Finset ι) (s : St4 ν ω ι Λ) : St4 ν ω ι Λ → ℕ → ℕ → ℕ → Prop
  | add (d e : ι) (l : Λ) (h : s.ch d ≤ s.ch e) :
      Mv4 P s { s with a := update s.a d (fun j => s.a d j + l * s.a e j) } 0 0 0
  | halve (d e : ι) (b : ω → Λ) (u : Λ) (hb : ∀ j, s.a e j = 2 * b j) (h : s.ch d ≤ s.ch e) :
      Mv4 P s { s with a := update s.a d (fun j => s.a d j + u * b j) } 0 0 1
  | init (r : ι) : Mv4 P s { s with a := update s.a r 0 } 0 0 0
  | down (r : ι) (D : Submodule (ZMod 2) (ν → ZMod 2)) (hr : r ∉ P) (h : D ≤ s.ch r) :
      Mv4 P s { s with ch := update s.ch r D } 0 0 0
  | upOwn (r : ι) (D : Submodule (ZMod 2) (ν → ZMod 2)) (hr : r ∉ P) (h : s.ch r ≤ D) :
      Mv4 P s { s with ch := update s.ch r D }
        (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) 0 0
  | upPub (r : ι) (D : Submodule (ZMod 2) (ν → ZMod 2)) (hr : r ∈ P) (h : s.ch r ≤ D) :
      Mv4 P s { s with ch := update s.ch r D }
        0 (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) 0

/-- A run: `S` cumulative potential, `c` owned climbs, `p` public climbs, `k` halvings. -/
inductive Run4 (P : Finset ι) (s0 : St4 ν ω ι Λ) :
    St4 ν ω ι Λ → AddSubgroup (Matrix ν ω (ZMod 4)) → ℕ → ℕ → ℕ → Prop
  | refl : Run4 P s0 s0 (potOf4 ρ s0) 0 0 0
  | step {s s' S c p k dc dp dk} : Run4 P s0 s S c p k → Mv4 P s s' dc dp dk →
      Run4 P s0 s' (S ⊔ potOf4 ρ s') (c + dc) (p + dp) (k + dk)

lemma enc_upd_same (s : St4 ν ω ι Λ) (d : ι) (f : ω → Λ) :
    enc ρ { s with a := update s.a d f } d = fun j => ρ (f j) := by
  funext j; simp [enc]

lemma enc_upd_ne (s : St4 ν ω ι Λ) {d r : ι} (hd : r ≠ d) (f : ω → Λ) :
    enc ρ { s with a := update s.a d f } r = enc ρ s r := by
  funext j; simp [enc, update_of_ne hd]

lemma outer4_add (w v : ω → ZMod 4) (c) : outer4 (ν := ν) (w + v) c = outer4 w c + outer4 v c := by
  ext i j; simp [outer4_apply, mul_add]

lemma outer4_smul (z : ZMod 4) (w : ω → ZMod 4) (c : ν → ZMod 4) :
    outer4 (fun j => z * w j) c = z • outer4 w c := by
  ext i j; simp [outer4_apply]; ring

/-- ascent lemma for the Z/4 potential: climb `k` costs at most `2^k` in cardinality. -/
lemma asc_step {S : AddSubgroup (Matrix ν ω (ZMod 4))} (w : ω → ZMod 4)
    {C D : Submodule (ZMod 2) (ν → ZMod 2)} (h : C ≤ D) (hS : pot4 C w ≤ S) :
    Nat.card (S ⊔ pot4 D w : AddSubgroup _) ≤ Nat.card S * 2 ^ (finrank (ZMod 2) D - finrank (ZMod 2) C) := by
  have key := ascent_card (outer4 w) (hat_mono h) S hS
  rw [card_hat, card_hat] at key
  have hk : finrank (ZMod 2) C ≤ finrank (ZMod 2) D := Submodule.finrank_mono h
  have e : 2 ^ (finrank (ZMod 2) D + Fintype.card ν) =
      2 ^ (finrank (ZMod 2) D - finrank (ZMod 2) C) * 2 ^ (finrank (ZMod 2) C + Fintype.card ν) := by
    rw [← pow_add]; congr 1; omega
  rw [e] at key
  have hp : 0 < 2 ^ (finrank (ZMod 2) C + Fintype.card ν) := by positivity
  refine Nat.le_of_mul_le_mul_right ?_ hp
  calc Nat.card (S ⊔ pot4 D w : AddSubgroup _) * 2 ^ (finrank (ZMod 2) C + Fintype.card ν)
      ≤ Nat.card S * (2 ^ (finrank (ZMod 2) D - finrank (ZMod 2) C) *
          2 ^ (finrank (ZMod 2) C + Fintype.card ν)) := key
    _ = _ := by ring

/-- **Step bound (CARRYPOT §1).** ADD (incl. carries), INIT, descent, discard: cost 0;
any ascent: cost ≤ climb; a halving add: cost ≤ n (multiplicatively `2^n`). -/
theorem step_bound4 {P : Finset ι} {s s' : St4 ν ω ι Λ} {dc dp dk : ℕ}
    (hm : Mv4 P s s' dc dp dk) (S : AddSubgroup (Matrix ν ω (ZMod 4))) (hS : potOf4 ρ s ≤ S) :
    Nat.card (S ⊔ potOf4 ρ s' : AddSubgroup _) ≤ Nat.card S * 2 ^ (dc + dp + Fintype.card ν * dk) := by
  have hr : ∀ r, pot4 (s.ch r) (enc ρ s r) ≤ S := fun r =>
    le_trans (le_iSup (fun r => pot4 (s.ch r) (enc ρ s r)) r) hS
  cases hm with
  | add d e l h =>
    have : potOf4 ρ { s with a := update s.a d (fun j => s.a d j + l * s.a e j) } ≤ S := by
      rw [potOf4_le_iff]; intro r'
      by_cases hd : r' = d
      · subst hd
        simp only [enc_upd_same]
        rintro _ ⟨c, hc, rfl⟩
        have h1 := hr r' (mem_pot4 hc)
        have h2 := hr e (mem_pot4 (hat_mono h hc))
        have : outer4 (fun j => ρ (s.a r' j + l * s.a e j)) c =
            outer4 (enc ρ s r') c + ρ l • outer4 (enc ρ s e) c := by
          have hw : (fun j => ρ (s.a r' j + l * s.a e j)) =
              enc ρ s r' + fun j => ρ l * enc ρ s e j := by
            funext j; simp [enc]
          rw [hw, outer4_add, outer4_smul]
        rw [this]; exact S.add_mem h1 (smul_mem4 S _ h2)
      · simp only [enc_upd_ne ρ s hd]; exact hr r'
    rw [sup_eq_left.2 this]; simp
  | halve d e b u hb h =>
    set A := hat (s.ch d) with hA
    set θ := outer4 (ν := ν) (fun j => ρ u * ρ (b j)) with hθdef
    have hle : potOf4 ρ { s with a := update s.a d (fun j => s.a d j + u * b j) } ≤
        S ⊔ A.map θ := by
      rw [potOf4_le_iff]; intro r'
      by_cases hd : r' = d
      · subst hd
        simp only [enc_upd_same]
        rintro _ ⟨c, hc, rfl⟩
        have h1 := hr r' (mem_pot4 hc)
        have : outer4 (fun j => ρ (s.a r' j + u * b j)) c = outer4 (enc ρ s r') c + θ c := by
          have hw : (fun j => ρ (s.a r' j + u * b j)) =
              enc ρ s r' + fun j => ρ u * ρ (b j) := by
            funext j; simp [enc]
          rw [hθdef, hw, outer4_add]
        rw [this]
        exact (S ⊔ A.map θ).add_mem (AddSubgroup.mem_sup_left h1) (AddSubgroup.mem_sup_right ⟨c, hc, rfl⟩)
      · simp only [enc_upd_ne ρ s hd]; exact le_sup_of_le_left (hr r')
    have hθ : ∀ a ∈ A, θ (a + a) ∈ S := by
      intro a ha
      have h2 := hr e (mem_pot4 (hat_mono h ha))
      have : θ (a + a) = ρ u • outer4 (enc ρ s e) a := by
        ext i j
        simp [hθdef, outer4_apply, enc, hb j, map_mul, map_ofNat]
        ring
      rw [this]; exact smul_mem4 S _ h2
    have h3 := halve_card θ A S hθ
    have h4 : Nat.card (S ⊔ potOf4 ρ { s with a := update s.a d (fun j => s.a d j + u * b j) } :
        AddSubgroup _) ≤ Nat.card (S ⊔ A.map θ : AddSubgroup _) :=
      AddSubgroup.card_le_of_le (sup_le le_sup_left hle)
    simpa using h4.trans h3
  | init r' =>
    have : potOf4 ρ { s with a := update s.a r' 0 } ≤ S := by
      rw [potOf4_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd
        have : enc ρ { s with a := update s.a r 0 } r = 0 := by
          funext j; simp [enc]
        simp only [this, pot4_zero]; exact bot_le
      · simp only [enc_upd_ne ρ s hd]; exact hr r
    rw [sup_eq_left.2 this]; simp
  | down r' D _ h =>
    have : potOf4 ρ { s with ch := update s.ch r' D } ≤ S := by
      rw [potOf4_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd; simp only [update_self]; exact le_trans (pot4_mono h _) (hr r)
      · simp only [update_of_ne hd]; exact hr r
    rw [sup_eq_left.2 this]; simp
  | upOwn r' D _ h =>
    have key := asc_step (enc ρ s r') h (hr r')
    have hle : potOf4 ρ { s with ch := update s.ch r' D } ≤ S ⊔ pot4 D (enc ρ s r') := by
      rw [potOf4_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd; simp only [update_self]; exact le_sup_right
      · simp only [update_of_ne hd]; exact le_sup_of_le_left (hr r)
    have h4 : Nat.card (S ⊔ potOf4 ρ { s with ch := update s.ch r' D } : AddSubgroup _) ≤
        Nat.card (S ⊔ pot4 D (enc ρ s r') : AddSubgroup _) :=
      AddSubgroup.card_le_of_le (sup_le le_sup_left hle)
    simpa using h4.trans key
  | upPub r' D _ h =>
    have key := asc_step (enc ρ s r') h (hr r')
    have hle : potOf4 ρ { s with ch := update s.ch r' D } ≤ S ⊔ pot4 D (enc ρ s r') := by
      rw [potOf4_le_iff]; intro r
      by_cases hd : r = r'
      · subst hd; simp only [update_self]; exact le_sup_right
      · simp only [update_of_ne hd]; exact le_sup_of_le_left (hr r)
    have h4 : Nat.card (S ⊔ potOf4 ρ { s with ch := update s.ch r' D } : AddSubgroup _) ≤
        Nat.card (S ⊔ pot4 D (enc ρ s r') : AddSubgroup _) :=
      AddSubgroup.card_le_of_le (sup_le le_sup_left hle)
    simpa using h4.trans key

end Z4c

section Z4d
open Finset Function
variable {ν ω ι Λ : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι] [CommRing Λ]
variable (ρ : Λ →+* ZMod 4)

lemma sum_update_chart4 (P : Finset ι) (ch : ι → Submodule (ZMod 2) (ν → ZMod 2)) (r : ι)
    (D : Submodule (ZMod 2) (ν → ZMod 2)) (hr : r ∈ P) :
    ∑ x ∈ P, finrank (ZMod 2) (update ch r D x) + finrank (ZMod 2) (ch r) =
      ∑ x ∈ P, finrank (ZMod 2) (ch x) + finrank (ZMod 2) D := by
  rw [← Finset.add_sum_erase P _ hr, ← Finset.add_sum_erase P (fun x => finrank (ZMod 2) (ch x)) hr]
  have : ∑ x ∈ P.erase r, finrank (ZMod 2) (update ch r D x) =
      ∑ x ∈ P.erase r, finrank (ZMod 2) (ch x) :=
    Finset.sum_congr rfl fun x hx => by rw [update_of_ne (Finset.ne_of_mem_erase hx)]
  rw [this, update_self]; ring

lemma sum_update_chart_out4 (P : Finset ι) (ch : ι → Submodule (ZMod 2) (ν → ZMod 2)) (r : ι)
    (D : Submodule (ZMod 2) (ν → ZMod 2)) (hr : r ∉ P) :
    ∑ x ∈ P, finrank (ZMod 2) (update ch r D x) = ∑ x ∈ P, finrank (ZMod 2) (ch x) :=
  Finset.sum_congr rfl fun x hx => by rw [update_of_ne (fun h : x = r => hr (h ▸ hx))]

/-- Invariants of a run: cumulative potential `S` has `|S| ≤ |pot s0| · 2^(c + p + n k)`. -/
theorem run_inv4 {P : Finset ι} {s0 s : St4 ν ω ι Λ} {S : AddSubgroup (Matrix ν ω (ZMod 4))}
    {c p k : ℕ} (h : Run4 ρ P s0 s S c p k) :
    potOf4 ρ s ≤ S ∧ potOf4 ρ s0 ≤ S ∧
      Nat.card S ≤ Nat.card (potOf4 ρ s0) * 2 ^ (c + p + Fintype.card ν * k) := by
  induction h with
  | refl => exact ⟨le_rfl, le_rfl, by simp⟩
  | @step s1 s2 S1 c1 p1 k1 dc dp dk hr hm ih =>
    obtain ⟨h1, h2, h3⟩ := ih
    refine ⟨le_sup_right, le_trans h2 le_sup_left, ?_⟩
    have := step_bound4 ρ hm _ h1
    refine this.trans ?_
    have e : c1 + dc + (p1 + dp) + Fintype.card ν * (k1 + dk) =
        (c1 + p1 + Fintype.card ν * k1) + (dc + dp + Fintype.card ν * dk) := by ring
    calc Nat.card S1 * 2 ^ (dc + dp + Fintype.card ν * dk)
        ≤ (Nat.card (potOf4 ρ s0) * 2 ^ (c1 + p1 + Fintype.card ν * k1)) *
            2 ^ (dc + dp + Fintype.card ν * dk) := Nat.mul_le_mul_right _ h3
      _ = _ := by rw [e, mul_assoc, ← pow_add]

/-- Public climbs telescope. -/
theorem run_pub_climb4 {P : Finset ι} {s0 s : St4 ν ω ι Λ} {S : AddSubgroup (Matrix ν ω (ZMod 4))}
    {c p k : ℕ} (h : Run4 ρ P s0 s S c p k) :
    p + ∑ r ∈ P, finrank (ZMod 2) (s0.ch r) = ∑ r ∈ P, finrank (ZMod 2) (s.ch r) := by
  induction h with
  | refl => simp
  | step hr hm ih =>
    cases hm with
    | add d e l h => simpa using ih
    | halve d e b u hb h => simpa using ih
    | init r => simpa using ih
    | down r D hr' h => simpa [sum_update_chart_out4 P _ r D hr'] using ih
    | upOwn r D hr' h => simpa [sum_update_chart_out4 P _ r D hr'] using ih
    | upPub r D hr' h =>
      rename_i s1 S1 c1 p1 k1
      have := sum_update_chart4 P (s1.ch) r D hr'
      have hm := Submodule.finrank_mono h
      simp only
      omega

/-! ## The F₂ shadow of public (integral) values -/

/-- `x ↦ 2x`, the embedding `F₂ ↪ Z/4` of the 2-torsion. -/
def ε1 : ZMod 2 →+ ZMod 4 := AddMonoidHom.mk' (fun x => 2 * ((x.val : ℕ) : ZMod 4)) (by decide)

lemma ε1_inj : Function.Injective ε1 := by
  intro a b h; revert a b; decide

lemma ε1_key : ∀ (c : ZMod 4) (w : ZMod 2),
    c * ε1 w = ε1 (ZMod.castHom (show 2 ∣ 4 by norm_num) (ZMod 2) c * w) := by decide

def eps : Matrix ν ω (ZMod 2) →+ Matrix ν ω (ZMod 4) := AddMonoidHom.mapMatrix ε1

lemma eps_inj : Function.Injective (eps (ν := ν) (ω := ω)) :=
  Matrix.map_injective ε1_inj

lemma eps_apply (x : Matrix ν ω (ZMod 2)) (i j) : eps x i j = ε1 (x i j) := rfl

/-- `Ĉ ⊗ (2 w̄)` is the `ε`-image of the `F₂` potential `C ⊗ w̄`. -/
lemma pot4_eq (C : Submodule (ZMod 2) (ν → ZMod 2)) (w : ω → ZMod 2) :
    pot4 C (fun j => ε1 (w j)) = (pot C w).toAddSubgroup.map eps := by
  ext x
  constructor
  · rintro ⟨c, hc, rfl⟩
    refine ⟨outer w (redH c), ⟨redH c, hc, rfl⟩, ?_⟩
    ext i j
    simp only [eps_apply, outer4_apply, outer_apply, Matrix.vecMulVec_apply, redH_apply]
    exact (ε1_key (c i) (w j)).symm
  · rintro ⟨y, ⟨c, hc, rfl⟩, rfl⟩
    refine ⟨fun i => ((c i).val : ZMod 4), ?_, ?_⟩
    · show redH _ ∈ C
      have : redH (fun i => ((c i).val : ZMod 4)) = c := by
        funext i; rw [redH_apply, map_natCast, ZMod.natCast_zmod_val]
      rw [this]; exact hc
    · ext i j
      simp only [eps_apply, outer4_apply, outer_apply, Matrix.vecMulVec_apply]
      rw [ε1_key, map_natCast, ZMod.natCast_zmod_val]

/-- public part of the Z/4 potential -/
def S04 (P : Finset ι) (s : St4 ν ω ι Λ) : AddSubgroup (Matrix ν ω (ZMod 4)) :=
  ⨆ r ∈ P, pot4 (s.ch r) (enc ρ s r)

/-- `s2` is the F₂ shadow of `s` on the publics: same charts, and `[w_r] = 2 w̄_r`
(i.e. public values are integral and reduce mod 2 to `w̄_r`). -/
def Shadow (P : Finset ι) (s : St4 ν ω ι Λ) (s2 : St (ZMod 2) ν ω ι) : Prop :=
  ∀ r ∈ P, s.ch r = s2.ch r ∧ ∀ j, enc ρ s r j = ε1 (s2.v r j)

lemma shadow_pot {P : Finset ι} {s : St4 ν ω ι Λ} {s2 : St (ZMod 2) ν ω ι}
    (hsh : Shadow ρ P s s2) {r : ι} (hr : r ∈ P) :
    pot4 (s.ch r) (enc ρ s r) = (pot (s2.ch r) (s2.v r)).toAddSubgroup.map eps := by
  rw [← pot4_eq, (hsh r hr).1]
  congr 1; funext j; exact (hsh r hr).2 j

lemma S04_le {P : Finset ι} {s : St4 ν ω ι Λ} {s2 : St (ZMod 2) ν ω ι}
    (hsh : Shadow ρ P s s2) : S04 ρ P s ≤ (S0 P s2).toAddSubgroup.map eps := by
  refine iSup₂_le fun r hr => ?_
  rw [shadow_pot ρ hsh hr]
  exact AddSubgroup.map_mono (Submodule.toAddSubgroup_mono
    (le_biSup (fun r => pot (s2.ch r) (s2.v r)) hr))

lemma S0_sup_le {P : Finset ι} {s0 s : St4 ν ω ι Λ} {s02 s2 : St (ZMod 2) ν ω ι}
    (hsh0 : Shadow ρ P s0 s02) (hsh : Shadow ρ P s s2) :
    ((S0 P s02 ⊔ S0 P s2).toAddSubgroup).map eps ≤ S04 ρ P s0 ⊔ S04 ρ P s := by
  let X : AddSubgroup (Matrix ν ω (ZMod 4)) := S04 ρ P s0 ⊔ S04 ρ P s
  let T : Submodule (ZMod 2) (Matrix ν ω (ZMod 2)) :=
    { carrier := {y | eps y ∈ X}
      add_mem' := fun {a b} ha hb => by
        show eps (a + b) ∈ X
        rw [map_add]; exact X.add_mem ha hb
      zero_mem' := by show eps 0 ∈ X; rw [map_zero]; exact X.zero_mem
      smul_mem' := fun a y hy => by
        show eps (a • y) ∈ X
        have : a = 0 ∨ a = 1 := by revert a; decide
        rcases this with rfl | rfl
        · simp only [zero_smul]; rw [map_zero]; exact X.zero_mem
        · simpa using hy }
  have h0 : S0 P s02 ≤ T := by
    refine iSup₂_le fun r hr => ?_
    rintro y hy
    show eps y ∈ X
    have : eps y ∈ pot4 (s0.ch r) (enc ρ s0 r) := by
      rw [shadow_pot ρ hsh0 hr]; exact ⟨y, hy, rfl⟩
    exact AddSubgroup.mem_sup_left (le_biSup (fun r => pot4 (s0.ch r) (enc ρ s0 r)) hr this)
  have h1 : S0 P s2 ≤ T := by
    refine iSup₂_le fun r hr => ?_
    rintro y hy
    show eps y ∈ X
    have : eps y ∈ pot4 (s.ch r) (enc ρ s r) := by
      rw [shadow_pot ρ hsh hr]; exact ⟨y, hy, rfl⟩
    exact AddSubgroup.mem_sup_right (le_biSup (fun r => pot4 (s.ch r) (enc ρ s r)) hr this)
  rw [AddSubgroup.map_le_iff_le_comap]
  intro y hy
  exact (sup_le h0 h1) hy

end Z4d

section Z4e
open Finset Function
variable {ν ω ι Λ : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι] [CommRing Λ]
variable (ρ : Λ →+* ZMod 4)

/-- **HALVING LAW, general headline.** Owned registers start at value 0, publics never descend,
public start/final values are integral with F₂ shadow `s02`, `s2`. For every dyadic run (den ≤ 2,
integral scalars on ADD, halving adds counted by `k`):
`dim_F2(S0 ⊔ T) ≤ R + n·k + Σ_P dim(final chart)`, i.e. `R + H ≥ E` with `H = n·k`
(each halving charged at most `n = |ν|`). -/
theorem halving_headline {P : Finset ι} {s0 s : St4 ν ω ι Λ} {S : AddSubgroup (Matrix ν ω (ZMod 4))}
    {c p k : ℕ} (h0 : ∀ r, r ∉ P → ∀ j, ρ (s0.a r j) = 0) (h : Run4 ρ P s0 s S c p k)
    {s02 s2 : St (ZMod 2) ν ω ι} (hsh0 : Shadow ρ P s0 s02) (hsh : Shadow ρ P s s2) :
    finrank (ZMod 2) (S0 P s02 ⊔ S0 P s2 : Submodule (ZMod 2) (Matrix ν ω (ZMod 2))) ≤
      c + Fintype.card ν * k + ∑ r ∈ P, finrank (ZMod 2) (s.ch r) := by
  obtain ⟨h1, h2, h3⟩ := run_inv4 ρ h
  have hclimb := run_pub_climb4 ρ h
  have hU : S04 ρ P s0 ⊔ S04 ρ P s ≤ S := sup_le
    (iSup₂_le fun r hr => le_trans (le_iSup (fun r => pot4 (s0.ch r) (enc ρ s0 r)) r) h2)
    (iSup₂_le fun r hr => le_trans (le_iSup (fun r => pot4 (s.ch r) (enc ρ s r)) r) h1)
  have hpot0 : potOf4 ρ s0 ≤ S04 ρ P s0 := by
    refine iSup_le fun r => ?_
    by_cases hr : r ∈ P
    · exact le_biSup (fun r => pot4 (s0.ch r) (enc ρ s0 r)) hr
    · have : enc ρ s0 r = 0 := funext (h0 r hr)
      rw [this, pot4_zero]; exact bot_le
  -- start potential has size ≤ 2^(Σ start dims)
  have c1 : Nat.card (potOf4 ρ s0) ≤ 2 ^ ∑ r ∈ P, finrank (ZMod 2) (s0.ch r) := by
    have a1 := AddSubgroup.card_le_of_le hpot0
    have a2 := AddSubgroup.card_le_of_le (S04_le ρ hsh0)
    rw [AddSubgroup.card_map_of_injective eps_inj, natcard_F2] at a2
    have a3 : finrank (ZMod 2) (S0 P s02) ≤ ∑ r ∈ P, finrank (ZMod 2) (s0.ch r) := by
      refine le_trans (finrank_S0_le P s02) (le_of_eq ?_)
      exact Finset.sum_congr rfl fun r hr => by rw [(hsh0 r hr).1]
    exact a1.trans (a2.trans (Nat.pow_le_pow_right (by norm_num) a3))
  -- the public span has size 2^dim
  have c2 : 2 ^ finrank (ZMod 2) (S0 P s02 ⊔ S0 P s2 : Submodule (ZMod 2) _) ≤ Nat.card S := by
    have a1 := AddSubgroup.card_le_of_le (S0_sup_le ρ hsh0 hsh)
    rw [AddSubgroup.card_map_of_injective eps_inj, natcard_F2] at a1
    exact a1.trans (AddSubgroup.card_le_of_le hU)
  have c3 : 2 ^ finrank (ZMod 2) (S0 P s02 ⊔ S0 P s2 : Submodule (ZMod 2) _) ≤
      2 ^ ((∑ r ∈ P, finrank (ZMod 2) (s0.ch r)) + (c + p + Fintype.card ν * k)) := by
    rw [pow_add]
    exact c2.trans (h3.trans (Nat.mul_le_mul c1 le_rfl))
  have := (Nat.pow_le_pow_iff_right (by norm_num : 1 < 2)).1 c3
  omega

end Z4e

section toy4
variable {ν Q J O Λ : Type*} [Fintype ν] [Fintype Q] [Fintype J] [Fintype O]
  [DecidableEq Q] [DecidableEq J] [DecidableEq O] [CommRing Λ]
variable (ρ : Λ →+* ZMod 4)

/-- **HEADLINE (toy form, Z/4 halving law).** For a dyadic run (values `w = a/2`, ADD with integral
scalars, any number of halvings) from the toy start to the toy final state (publics integral; owned
registers start at value 0, publics never descend; relays arbitrary on fresh coordinates), with
`M̄` the mod-2 reduction of the integral transfer matrix `M` (encoded in the shadow hypothesis `hsh`):
`R + n·k ≥ rank_F2 (Q ∘ M̄)`. With `k = 0` this is the earlier integral-scalar bound. -/
theorem toy_rank_le4 (q : Q → ν → ZMod 2) (M : Matrix Q Q (ZMod 2)) (Sj Fj : J → Submodule (ZMod 2) (ν → ZMod 2))
    (A0 A1 : O → Submodule (ZMod 2) (ν → ZMod 2)) (V1 : O → Wd Q J → ZMod 2)
    {s0 s : St4 ν (Wd Q J) (Rg Q J O) Λ} {S : AddSubgroup (Matrix ν (Wd Q J) (ZMod 4))} {c p k : ℕ}
    (h0 : ∀ r, r ∉ pubs Q J O → ∀ j, ρ (s0.a r j) = 0)
    (hsh0 : Shadow ρ (pubs Q J O) s0 (toyStart q Sj A0))
    (hsh : Shadow ρ (pubs Q J O) s (toyFinal q M Fj A1 V1))
    (h : Run4 ρ (pubs Q J O) s0 s S c p k) :
    (had q M).rank ≤ c + Fintype.card ν * k := by
  have h1 := halving_headline ρ h0 h hsh0 hsh
  have h2 := toy_lower q M Sj Fj A0 A1 V1
  have h3 : ∑ r ∈ pubs Q J O, finrank (ZMod 2) (s.ch r) =
      Fintype.card Q * Fintype.card ν + (∑ s, finrank (ZMod 2) (perp (q s))) +
        ∑ j, finrank (ZMod 2) (Fj j) := by
    rw [Finset.sum_congr rfl fun r hr => by rw [(hsh r hr).1]]
    rw [pubs, Finset.sum_map]
    change ∑ a : Wd Q J, finrank (ZMod 2) ((toyFinal q M Fj A1 V1).ch (Sum.inl a)) = _
    have hfin : finrank (ZMod 2) (⊤ : Submodule (ZMod 2) (ν → ZMod 2)) = Fintype.card ν := by
      rw [finrank_top, Module.finrank_fintype_fun_eq_card]
    have hX : ∀ t : Q, finrank (ZMod 2) ((toyFinal q M Fj A1 V1).ch (Sum.inl (Sum.inl t))) =
        Fintype.card ν := fun t => hfin
    have hY : ∀ s : Q, finrank (ZMod 2) ((toyFinal q M Fj A1 V1).ch (Sum.inl (Sum.inr (Sum.inl s)))) =
        finrank (ZMod 2) (perp (q s)) := fun _ => rfl
    have hZ : ∀ j : J, finrank (ZMod 2) ((toyFinal q M Fj A1 V1).ch (Sum.inl (Sum.inr (Sum.inr j)))) =
        finrank (ZMod 2) (Fj j) := fun _ => rfl
    rw [Fintype.sum_sum_type, Fintype.sum_sum_type]
    simp only [hX, hY, hZ, Finset.sum_const, Finset.card_univ, smul_eq_mul]
    ring
  unfold toyA at h2
  rw [h3] at h1
  rw [mul_comm (Fintype.card ν)] at h2
  omega

end toy4

section inst0
open Function
/-- the odd ports `1, 2, 7` as bit-vectors in `𝔽₂³` -/
def q127 : Fin 3 → Fin 3 → ZMod 2 := ![![1, 0, 0], ![0, 1, 0], ![1, 1, 1]]
abbrev Sj0 : Fin 0 → Submodule (ZMod 2) (Fin 3 → ZMod 2) := fun j => j.elim0
abbrev Mid : Matrix (Fin 3) (Fin 3) (ZMod 2) := 1
abbrev A00 : Unit → Submodule (ZMod 2) (Fin 3 → ZMod 2) := fun _ => ⊥
abbrev V00 : Unit → Wd (Fin 3) (Fin 0) → ZMod 2 := fun _ => 0

lemma q127_ne (t : Fin 3) : q127 t ≠ 0 := by revert t; decide

theorem had_q127 : had q127 Mid = 1 := by
  ext t s
  fin_cases t <;> fin_cases s <;> simp [had, q127, dotProduct, Fin.sum_univ_three] <;> decide

theorem rank_q127 : (had q127 Mid).rank = 3 := by
  rw [had_q127, Matrix.rank_one]; simp


abbrev P3 : Finset (Rg (Fin 3) (Fin 0) Unit) := pubs (Fin 3) (Fin 0) Unit
abbrev St3 := St (ZMod 2) (Fin 3) (Wd (Fin 3) (Fin 0)) (Rg (Fin 3) (Fin 0) Unit)
abbrev T0 : St3 := toyStart q127 Sj0 A00
def oR : Rg (Fin 3) (Fin 0) Unit := Sum.inr ()
def xR (t : Fin 3) : Rg (Fin 3) (Fin 0) Unit := Sum.inl (Sum.inl t)
def yR (t : Fin 3) : Rg (Fin 3) (Fin 0) Unit := Sum.inl (Sum.inr (Sum.inl t))

lemma ne_oy (t : Fin 3) : oR ≠ yR t := by simp [oR, yR]
lemma ne_ox (t : Fin 3) : oR ≠ xR t := by simp [oR, xR]
lemma ne_xy (t t' : Fin 3) : xR t ≠ yR t' := by simp [xR, yR]
lemma ne_xx {t t' : Fin 3} (h : t' ≠ t) : xR t' ≠ xR t := by simp [xR, h]
lemma ne_yy {t t' : Fin 3} (h : t' ≠ t) : yR t' ≠ yR t := by simp [yR, h]
end inst0

/-! # Non-vacuity -/
section inst4
open Function

/-- `Λ = ℤ`: `ρ` = reduction mod 4 -/
abbrev ρZ : ℤ →+* ZMod 4 := Int.castRingHom (ZMod 4)

/-- doubled integral value of an `F₂` vector (`w ↦ a = 2w`) -/
def dbl {ω : Type*} (v : ω → ZMod 2) : ω → ℤ := fun j => 2 * ((v j).val : ℤ)

def lift4 {ν ω ι : Type*} (s : St (ZMod 2) ν ω ι) : St4 ν ω ι ℤ := ⟨s.ch, fun r => dbl (s.v r)⟩

lemma shadow_lift {ν ω ι : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι] (P : Finset ι)
    (s : St (ZMod 2) ν ω ι) : Shadow ρZ P (lift4 s) s := fun r _ =>
  ⟨rfl, fun j => by simp [enc, lift4, dbl, ε1]⟩

lemma St4.ext' {ν ω ι Λ : Type*} (a b : St4 ν ω ι Λ) (h1 : a.ch = b.ch) (h2 : a.a = b.a) : a = b := by
  cases a; cases b; simp_all

lemma Run4.step_to {ν ω ι Λ : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι] [CommRing Λ]
    {ρ : Λ →+* ZMod 4} {P : Finset ι} {s0 s s' : St4 ν ω ι Λ}
    {S : AddSubgroup (Matrix ν ω (ZMod 4))} {c p k dc dp dk : ℕ}
    (h : Run4 ρ P s0 s S c p k) (hm : Mv4 P s s' dc dp dk) :
    ∃ S', Run4 ρ P s0 s' S' (c + dc) (p + dp) (k + dk) := ⟨_, h.step hm⟩

lemma Run4.cast {ν ω ι Λ : Type*} [Fintype ν] [Fintype ω] [DecidableEq ι] [CommRing Λ]
    {ρ : Λ →+* ZMod 4} {P : Finset ι} {s0 s s' : St4 ν ω ι Λ}
    {S : AddSubgroup (Matrix ν ω (ZMod 4))} {c p k : ℕ}
    (e : s = s') (h : Run4 ρ P s0 s S c p k) : Run4 ρ P s0 s' S c p k := e ▸ h

abbrev St43 := St4 (Fin 3) (Wd (Fin 3) (Fin 0)) (Rg (Fin 3) (Fin 0) Unit) ℤ
abbrev T04 : St43 := lift4 (toyStart q127 Sj0 A00)
abbrev Tf4 : St43 := lift4 (toyFinal q127 Mid Sj0 A00 V00)

def Own4 (s : St43) : Prop := s.ch oR = ⊥ ∧ s.a oR = 0
def Todo4 (t : Fin 3) (s : St43) : Prop :=
  s.ch (yR t) = ⊥ ∧ s.a (yR t) = dbl (eY t) ∧ s.ch (xR t) = Submodule.span (ZMod 2) {q127 t} ∧
    s.a (xR t) = dbl (eX t)
def Done4 (t : Fin 3) (s : St43) : Prop :=
  s.ch (yR t) = perp (q127 t) ∧ s.a (yR t) = dbl (eY t) ∧ s.ch (xR t) = ⊤ ∧
    s.a (xR t) = dbl (finX Mid t)

lemma dbl_eX_add_eY (t : Fin 3) :
    (fun j => dbl (eX (J := Fin 0) t) j + dbl (eY t) j) = dbl (finX Mid t) := by
  funext w
  rcases w with x | y | z
  · simp [dbl, eX, eY, finX, Pi.single_apply]
  · simp [dbl, eX, eY, finX, Pi.single_apply, Matrix.one_apply, eq_comm]
  · exact z.elim0

lemma Own40 : Own4 T04 := ⟨rfl, by funext j; simp [lift4, dbl, toyStart, oR]⟩
lemma Todo40 (t : Fin 3) : Todo4 t T04 := ⟨rfl, rfl, rfl, rfl⟩

lemma port_step4 (t : Fin 3) {s : St43} {S : AddSubgroup (Matrix (Fin 3) (Wd (Fin 3) (Fin 0)) (ZMod 4))}
    {c p k : ℕ} (hrun : Run4 ρZ P3 T04 s S c p k) (hown : Own4 s) (ht : Todo4 t s) :
    ∃ (s' : St43) (S' : AddSubgroup (Matrix (Fin 3) (Wd (Fin 3) (Fin 0)) (ZMod 4))) (c' p' k' : ℕ),
      Run4 ρZ P3 T04 s' S' c' p' k' ∧ c' = c + 1 ∧ k' = k ∧ Own4 s' ∧ Done4 t s' ∧
      (∀ t', t' ≠ t → Todo4 t' s → Todo4 t' s') ∧ (∀ t', t' ≠ t → Done4 t' s → Done4 t' s') := by
  obtain ⟨ho1, ho2⟩ := hown
  obtain ⟨hy1, hy2, hx1, hx2⟩ := ht
  have hown' : oR ∉ P3 := by rw [mem_pubs]; simp [oR]
  have e1 : oR ≠ yR t := ne_oy t
  have e2 : yR t ≠ oR := (ne_oy t).symm
  have e3 : oR ≠ xR t := ne_ox t
  have e4 : xR t ≠ oR := (ne_ox t).symm
  have e5 : xR t ≠ yR t := ne_xy t t
  have e6 : yR t ≠ xR t := (ne_xy t t).symm
  obtain ⟨_, r1⟩ := hrun.step_to (Mv4.add oR (yR t) 1 (by rw [ho1, hy1]))
  obtain ⟨_, r2⟩ := r1.step_to (Mv4.upOwn oR (Submodule.span (ZMod 2) {q127 t}) hown'
    (by simp [ho1]))
  obtain ⟨_, r3⟩ := r2.step_to (Mv4.add (xR t) oR 1
    (by simp [ho1, hx1, update_apply, e1, e2, e3, e4, e5, e6]))
  obtain ⟨_, r4⟩ := r3.step_to (Mv4.down oR ⊥ hown' bot_le)
  obtain ⟨_, r5⟩ := r4.step_to (Mv4.init oR)
  obtain ⟨_, r6⟩ := r5.step_to (Mv4.upPub (xR t) ⊤ (mem_pubs.2 ⟨_, rfl⟩) le_top)
  obtain ⟨_, r7⟩ := r6.step_to (Mv4.upPub (yR t) (perp (q127 t)) (mem_pubs.2 ⟨_, rfl⟩)
    (by simp [hy1, update_apply, e1, e2, e3, e4, e5, e6]))
  refine ⟨_, _, _, _, _, r7, ?_, ?_, ?_, ?_, ?_, ?_⟩
  · simp [finrank_span_singleton (q127_ne t), update_apply, e1, e2, e3, e4, e5, e6]
    rw [ho1]; simp
  · simp
  · refine ⟨?_, ?_⟩
    · simp [update_apply, e1, e2, e3, e4, e5, e6]
    · funext j; simp [update_apply, e1, e2, e3, e4, e5, e6]
  · refine ⟨?_, ?_, ?_, ?_⟩
    · simp [update_apply, e1, e2, e3, e4, e5, e6]
    · funext j; simp [update_apply, e1, e2, e3, e4, e5, e6, hy2]
    · simp [update_apply, e1, e2, e3, e4, e5, e6]
    · funext j
      have := congrFun (dbl_eX_add_eY t) j
      simp [update_apply, e1, e2, e3, e4, e5, e6, hy2, hx2, ho2, this]
  · intro t' ht' ⟨a, b, c, d⟩
    have f1 : yR t' ≠ yR t := ne_yy ht'
    have f2 : yR t' ≠ xR t := (ne_xy t t').symm
    have f3 : yR t' ≠ oR := (ne_oy t').symm
    have f4 : xR t' ≠ oR := (ne_ox t').symm
    have f5 : xR t' ≠ yR t := ne_xy t' t
    have f6 : xR t' ≠ xR t := ne_xx ht'
    refine ⟨?_, ?_, ?_, ?_⟩ <;> simp [update_apply, f1, f2, f3, f4, f5, f6, a, b, c, d]
  · intro t' ht' ⟨a, b, c, d⟩
    have f1 : yR t' ≠ yR t := ne_yy ht'
    have f2 : yR t' ≠ xR t := (ne_xy t t').symm
    have f3 : yR t' ≠ oR := (ne_oy t').symm
    have f4 : xR t' ≠ oR := (ne_ox t').symm
    have f5 : xR t' ≠ yR t := ne_xy t' t
    have f6 : xR t' ≠ xR t := ne_xx ht'
    refine ⟨?_, ?_, ?_, ?_⟩ <;> simp [update_apply, f1, f2, f3, f4, f5, f6, a, b, c, d]

/-- the `{1,2,7}` run in the Z/4 model: `R = 3`, no halvings. -/
theorem inst4_run : ∃ S p, Run4 ρZ P3 T04 Tf4 S 3 p 0 := by
  have r0 : Run4 ρZ P3 T04 T04 _ 0 0 0 := Run4.refl
  obtain ⟨s1, S1, c1, p1, k1, r1, hc1, hk1, hO1, hD1, hT1, hP1⟩ := port_step4 0 r0 Own40 (Todo40 0)
  obtain ⟨s2, S2, c2, p2, k2, r2, hc2, hk2, hO2, hD2, hT2, hP2⟩ :=
    port_step4 1 r1 hO1 (hT1 1 (by decide) (Todo40 1))
  obtain ⟨s3, S3, c3, p3, k3, r3, hc3, hk3, hO3, hD3, hT3, hP3⟩ :=
    port_step4 2 r2 hO2 (hT2 2 (by decide) (hT1 2 (by decide) (Todo40 2)))
  have hD : ∀ x, Done4 x s3 := by
    intro x
    fin_cases x
    · exact hP3 0 (by decide) (hP2 0 (by decide) hD1)
    · exact hP3 1 (by decide) hD2
    · exact hD3
  have e : s3 = Tf4 := by
    refine St4.ext' _ _ (funext fun r => ?_) (funext fun r => ?_)
    · rcases r with (x | y | z) | u
      · exact (hD x).2.2.1
      · exact (hD y).1
      · exact z.elim0
      · exact hO3.1
    · rcases r with (x | y | z) | u
      · exact (hD x).2.2.2
      · exact (hD y).2.1
      · exact z.elim0
      · exact hO3.2
  have hc : c3 = 3 := by omega
  have hk : k3 = 0 := by omega
  exact ⟨_, _, hc ▸ hk ▸ Run4.cast e r3⟩

lemma q127_start_zero : ∀ r, r ∉ P3 → ∀ j, ρZ (T04.a r j) = 0 := by
  intro r hr j
  rcases r with a | o
  · exact absurd (mem_pubs.2 ⟨a, rfl⟩) hr
  · simp [T04, lift4, dbl, toyStart]

/-- **Z/4 halving law on the `{1,2,7}` toy, any run, any halvings:** `R + 3k ≥ 3`. -/
theorem inst4_bound {S : AddSubgroup (Matrix (Fin 3) (Wd (Fin 3) (Fin 0)) (ZMod 4))} {c p k : ℕ}
    (h : Run4 ρZ P3 T04 Tf4 S c p k) : 3 ≤ c + 3 * k := by
  have := toy_rank_le4 ρZ q127 Mid Sj0 Sj0 A00 A00 V00 q127_start_zero
    (shadow_lift _ _) (shadow_lift _ _) h
  rw [rank_q127] at this
  simpa using this

/-- the toy `{1,2,7}`: lower bound `rank = 3` and a run with `R = 3`, `H = 0`: tight. -/
theorem inst4_tight : (had q127 Mid).rank = 3 ∧ ∃ S p, Run4 ρZ P3 T04 Tf4 S 3 p 0 :=
  ⟨rank_q127, inst4_run⟩

end inst4

/-! ## Non-vacuity of the halving move: `n = 1`, one public `w = 1`, one owned register that
receives `w/2 = 1/2`. Run with `R = 0`, one halving; the potential strictly grows (an element of
additive order 4 appears), as it must, since `[w/2]` is not determined by `[w] = 2 mod 4`. -/
section inst_half
open Function

abbrev Sh0 : St4 (Fin 1) (Fin 1) (Fin 2) ℤ := ⟨fun _ => ⊤, fun r _ => if r = 0 then 2 else 0⟩
abbrev Ph : Finset (Fin 2) := {0}
def Sh1 : St4 (Fin 1) (Fin 1) (Fin 2) ℤ :=
  { Sh0 with a := update Sh0.a 1 (fun j => Sh0.a 1 j + 1 * (fun _ => (1 : ℤ)) j) }

theorem halve_run :
    Run4 ρZ Ph Sh0 Sh1 (potOf4 ρZ Sh0 ⊔ potOf4 ρZ Sh1) (0 + 0) (0 + 0) (0 + 1) :=
  Run4.step Run4.refl (Mv4.halve 1 0 (fun _ => 1) 1 (by intro j; simp) le_rfl)

theorem halve_strict : ¬ potOf4 ρZ Sh1 ≤ potOf4 ρZ Sh0 := by
  intro hle
  let f : Matrix (Fin 1) (Fin 1) (ZMod 4) →+ ZMod 4 :=
    AddMonoidHom.mk' (fun M => M 0 0 + M 0 0) (by intros; simp; abel)
  have h1 : potOf4 ρZ Sh0 ≤ f.ker := by
    refine iSup_le fun r => ?_
    rintro _ ⟨c, hc, rfl⟩
    rw [AddMonoidHom.mem_ker]
    fin_cases r
    · simp only [f, AddMonoidHom.mk'_apply, outer4_apply, enc]
      show c 0 * ρZ 2 + c 0 * ρZ 2 = 0
      generalize c 0 = z; revert z; decide
    · simp [f, outer4_apply, enc]
  have hx : (Matrix.of fun _ _ => (1 : ZMod 4)) ∈ potOf4 ρZ Sh1 := by
    refine le_iSup (fun r => pot4 (Sh1.ch r) (enc ρZ Sh1 r)) 1 ⟨fun _ => 1, ?_, ?_⟩
    · exact mem_hat.2 Submodule.mem_top
    · ext i j
      fin_cases i; fin_cases j
      simp [outer4_apply, enc, Sh1]
  have := h1 (hle hx)
  rw [AddMonoidHom.mem_ker] at this
  revert this; simp [f]; decide

theorem halving_nonvacuous :
    (∃ S, Run4 ρZ Ph Sh0 Sh1 S 0 0 1) ∧ ¬ potOf4 ρZ Sh1 ≤ potOf4 ρZ Sh0 :=
  ⟨⟨_, halve_run⟩, halve_strict⟩

end inst_half

end HalvingLaw

open HalvingLaw in
#print axioms HalvingLaw.step_bound4
open HalvingLaw in
#print axioms HalvingLaw.halve_card
open HalvingLaw in
#print axioms HalvingLaw.asc_step
open HalvingLaw in
#print axioms HalvingLaw.run_inv4
open HalvingLaw in
#print axioms HalvingLaw.halving_headline
open HalvingLaw in
#print axioms HalvingLaw.toy_rank_le4
open HalvingLaw in
#print axioms HalvingLaw.inst4_tight
open HalvingLaw in
#print axioms HalvingLaw.inst4_bound
open HalvingLaw in
#print axioms HalvingLaw.halving_nonvacuous
