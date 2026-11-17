/-
SPECBREAK R49 formalised (lane LEAN-NEXT29, Nov 17): Ureq bounds L3_U / SYL_U (R21 B2), #9 kill, #1 at U <= 3.
Builds on Nov15/SpecTSUR.lean, SpecINV.lean, SpecCOV.lean.  See SpecKills.md.
-/
import Nov15.SpecTSUR
import Nov15.SpecINV
import Nov15.SpecCOV

open Matrix Finset SpecTSUR SpecINV

set_option linter.unusedSectionVars false

namespace SpecKills

variable {K : Type*} [Field K]

/-! ## §1. Sequences of factors: append and rotation -/
section Basics
variable {n : Type*} [Fintype n] [DecidableEq n]

theorem pp_add (x y : ℕ → n → K) (a b : ℕ) :
    pp x y (a + b) = pp x y a * pp (fun i => x (a + i)) (fun i => y (a + i)) b := by
  induction b with
  | zero => simp [pp]
  | succ b ih =>
    show pp x y (a + b + 1) = _
    simp only [pp, ih, Matrix.mul_assoc]

theorem pp_congr (x y x' y' : ℕ → n → K) (m : ℕ) (h : ∀ i < m, x i = x' i ∧ y i = y' i) :
    pp x y m = pp x' y' m := by
  induction m with
  | zero => rfl
  | succ m ih =>
    rw [pp, pp, ih (fun i hi => h i (by omega)), (h m (by omega)).1, (h m (by omega)).2]

/-- rotation: `P Q` becomes `Q P`; the rotated sequence starts with factor `p` -/
theorem pp_rot (x y : ℕ → n → K) (m p : ℕ) (hp : p ≤ m) :
    ∃ x' y' : ℕ → n → K, (∀ i, i < m - p → x' i = x (p + i) ∧ y' i = y (p + i)) ∧
      pp x y m = pp x y p * pp (fun i => x (p + i)) (fun i => y (p + i)) (m - p) ∧
      pp x' y' m = pp (fun i => x (p + i)) (fun i => y (p + i)) (m - p) * pp x y p := by
  refine ⟨fun i => if i < m - p then x (p + i) else x (i - (m - p)),
    fun i => if i < m - p then y (p + i) else y (i - (m - p)), ?_, ?_, ?_⟩
  · intro i hi; simp [hi]
  · have := pp_add x y p (m - p)
    rwa [Nat.add_sub_cancel' hp] at this
  · have := pp_add (fun i => if i < m - p then x (p + i) else x (i - (m - p)))
      (fun i => if i < m - p then y (p + i) else y (i - (m - p))) (m - p) p
    rw [Nat.sub_add_cancel hp] at this
    rw [this]
    congr 1
    · exact pp_congr _ _ _ _ _ (fun i hi => by simp [hi])
    · exact pp_congr _ _ _ _ _ (fun i hi => by
        have : ¬ (m - p + i < m - p) := by omega
        simp [this])

theorem det_pp_gen (x y : ℕ → n → K) (m : ℕ) :
    (pp x y m).det = ∏ i ∈ range m, (1 - y i ⬝ᵥ x i) := by
  induction m with
  | zero => simp [pp]
  | succ m ih => rw [pp, det_mul, ih, prod_range_succ, SpecINV.det_refl]

variable [DecidableEq K]

theorem inv_rank0 [DecidableEq K] (h2 : (2 : K) ≠ 0) (U : ℕ) (x y : ℕ → n → K)
    (hq : 0 < U → y 0 ⬝ᵥ x 0 = 0) (hg : pp x y U * pp x y U = 1) :
    (1 - pp x y U).rank ≤ U - 1 := by
  rcases Nat.eq_zero_or_pos U with rfl | hU
  · simp [pp]
  set Z := Zm x y U with hZ
  set Qm : Matrix n (Fin U) K := Matrix.of fun a (i : Fin U) => y i a with hQm
  have hA : 1 - pp x y U = Z * Qmᵀ := one_sub_pp x y U
  have hle : (1 - pp x y U).rank ≤ U := by
    rw [hA]
    exact (rank_mul_le_left _ _).trans (by simpa using Z.rank_le_card_width)
  by_contra hcon
  have hU' : (1 - pp x y U).rank = U := by omega
  have hrZ : Z.rank = U := by
    have h1 : (1 - pp x y U).rank ≤ Z.rank := by rw [hA]; exact rank_mul_le_left _ _
    have h3 : Z.rank ≤ U := by simpa using Z.rank_le_card_width
    omega
  have hrQ : Qm.rank = U := by
    have h1 : (1 - pp x y U).rank ≤ Qmᵀ.rank := by rw [hA]; exact rank_mul_le_right _ _
    rw [Matrix.rank_transpose] at h1
    have h3 : Qm.rank ≤ U := by simpa using Qm.rank_le_card_width
    omega
  obtain ⟨L, hL⟩ := exists_left_inv Z hrZ
  obtain ⟨L2, hL2⟩ := exists_left_inv Qm hrQ
  have hR : Qmᵀ * L2ᵀ = 1 := by
    rw [← Matrix.transpose_mul, hL2, Matrix.transpose_one]
  have hsq : (1 - pp x y U) * (1 - pp x y U) = (1 - pp x y U) + (1 - pp x y U) := by
    calc (1 - pp x y U) * (1 - pp x y U)
        = 1 - pp x y U - pp x y U + pp x y U * pp x y U := by noncomm_ring
      _ = _ := by rw [hg]; abel
  have hmid : Qmᵀ * Z = 1 + 1 := by
    have e1 : L * ((Z * Qmᵀ) * (Z * Qmᵀ)) * L2ᵀ = Qmᵀ * Z := by
      calc L * ((Z * Qmᵀ) * (Z * Qmᵀ)) * L2ᵀ
          = (L * Z) * (Qmᵀ * Z) * (Qmᵀ * L2ᵀ) := by simp only [Matrix.mul_assoc]
        _ = _ := by rw [hL, hR]; simp
    have e2 : L * ((Z * Qmᵀ) + (Z * Qmᵀ)) * L2ᵀ = 1 + 1 := by
      calc L * ((Z * Qmᵀ) + (Z * Qmᵀ)) * L2ᵀ
          = (L * Z) * (Qmᵀ * L2ᵀ) + (L * Z) * (Qmᵀ * L2ᵀ) := by
            simp only [Matrix.mul_add, Matrix.add_mul, Matrix.mul_assoc]
        _ = _ := by rw [hL, hR]; simp
    rw [← e1, ← e2, ← hA, hsq]
  have h00 := congrFun (congrFun hmid ⟨0, hU⟩) ⟨0, hU⟩
  have hz0 : zv x y 0 = x 0 := by simp [zv, pp]
  have hdot : (Qmᵀ * Z) ⟨0, hU⟩ ⟨0, hU⟩ = y 0 ⬝ᵥ x 0 := by
    simp only [Matrix.mul_apply, hQm, hZ, Zm, Matrix.transpose_apply, Matrix.of_apply, dotProduct]
    simp [hz0]
  rw [hdot, hq hU] at h00
  simp only [Matrix.add_apply, Matrix.one_apply_eq] at h00
  apply h2
  linear_combination -h00


/-! ## §2. L3_U (R21 B2 / R15 Lemma 3 with units)

`m = J + U` factors `I - x_i y_iᵀ`, each a job (reflection, `y_i·x_i = 2`) or a unit (transvection,
`y_i·x_i = 0`), in a fixed order; their ordered product is `D = diag s`, `s = ±1`, with `r` flipped
coordinates.  Then `r <= J + U - [U >= 1]` and `r ≡ J (mod 2)`. -/

def nJ (x y : ℕ → n → K) (m : ℕ) : ℕ := ((range m).filter fun i => y i ⬝ᵥ x i = 2).card
def nU (x y : ℕ → n → K) (m : ℕ) : ℕ := ((range m).filter fun i => y i ⬝ᵥ x i = 0).card
def nflip (s : n → K) : ℕ := (univ.filter fun a => s a = -1).card

theorem nJ_add_nU (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (m : ℕ)
    (hkind : ∀ i < m, y i ⬝ᵥ x i = 2 ∨ y i ⬝ᵥ x i = 0) : nJ x y m + nU x y m = m := by
  have h := Finset.card_filter_add_card_filter_not (s := range m) (fun i => y i ⬝ᵥ x i = 2)
  rw [card_range] at h
  have : (range m).filter (fun i => ¬ (y i ⬝ᵥ x i = 2)) = (range m).filter fun i => y i ⬝ᵥ x i = 0 := by
    apply filter_congr
    intro i hi
    rcases hkind i (mem_range.1 hi) with h | h
    · simpa [h] using h2
    · simp [h, Ne.symm h2]
  rw [this] at h
  exact h

theorem one_ne_neg_one (h2 : (2 : K) ≠ 0) : (1 : K) ≠ -1 := by
  intro h; apply h2; linear_combination h

theorem det_diag_pm (h2 : (2 : K) ≠ 0) (s : n → K) (hs : ∀ a, s a = 1 ∨ s a = -1) :
    (diagonal s).det = (-1) ^ nflip s := by
  rw [det_diagonal, nflip]
  have : ∀ a, s a = if s a = -1 then (-1 : K) else 1 := by
    intro a; rcases hs a with h | h
    · simp [h, one_ne_neg_one h2]
    · simp [h]
  rw [Finset.prod_congr rfl (fun a _ => this a), Finset.prod_ite]
  simp

theorem det_pp_pm (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (m : ℕ)
    (hkind : ∀ i < m, y i ⬝ᵥ x i = 2 ∨ y i ⬝ᵥ x i = 0) :
    (pp x y m).det = (-1) ^ nJ x y m := by
  rw [det_pp_gen]
  have : ∀ i ∈ range m, (1 - y i ⬝ᵥ x i) = if y i ⬝ᵥ x i = 2 then (-1 : K) else 1 := by
    intro i hi
    rcases hkind i (mem_range.1 hi) with h | h
    · simp [h]; norm_num
    · simp [h, Ne.symm h2]
  rw [Finset.prod_congr rfl this, Finset.prod_ite, nJ]
  simp

theorem neg_one_pow_inj (h2 : (2 : K) ≠ 0) (a b : ℕ) (h : (-1 : K) ^ a = (-1) ^ b) : a % 2 = b % 2 := by
  rw [neg_one_pow_eq_pow_mod_two, neg_one_pow_eq_pow_mod_two (n := b)] at h
  have ha : a % 2 = 0 ∨ a % 2 = 1 := by omega
  have hb : b % 2 = 0 ∨ b % 2 = 1 := by omega
  rcases ha with ha | ha <;> rcases hb with hb | hb <;> rw [ha, hb] at h ⊢ <;> first | rfl | (exfalso; simp at h; first | exact one_ne_neg_one h2 h | exact one_ne_neg_one h2 h.symm)

/-- **L3_U** (R21 B2 = R15 Lemma 3 with units; char ≠ 2).  `m` factors, each a job (`y·x = 2`) or a
unit (`y·x = 0`) in a fixed order, with ordered product `diag s`, `s = ±1`.  Then
`r ≤ J + U - [U ≥ 1]` (written `r + [U ≥ 1] ≤ J + U`) and `r ≡ J (mod 2)`.  No other hypothesis. -/
theorem L3_U (h2 : (2 : K) ≠ 0) (m : ℕ) (x y : ℕ → n → K)
    (hkind : ∀ i < m, y i ⬝ᵥ x i = 2 ∨ y i ⬝ᵥ x i = 0)
    (s : n → K) (hs : ∀ a, s a = 1 ∨ s a = -1) (hprod : pp x y m = diagonal s) :
    nflip s + (if 1 ≤ nU x y m then 1 else 0) ≤ nJ x y m + nU x y m ∧
      nflip s % 2 = nJ x y m % 2 := by
  have hr : (1 - diagonal s : Matrix n n K).rank = nflip s := rank_one_sub_diag h2 s hs
  have hJU := nJ_add_nU h2 x y m hkind
  have hle : (1 - pp x y m).rank ≤ m := by
    rw [one_sub_pp]
    exact (rank_mul_le_left _ _).trans (by simpa using (Zm x y m).rank_le_card_width)
  have hD2 : (diagonal s : Matrix n n K) * diagonal s = 1 := by
    rw [diagonal_mul_diagonal, ← diagonal_one]
    congr 1; funext a; rcases hs a with h | h <;> simp [h]
  refine ⟨?_, ?_⟩
  · by_cases hU : 1 ≤ nU x y m
    · simp only [hU, if_true]
      have hne : ((range m).filter fun i => y i ⬝ᵥ x i = 0).Nonempty := by
        rw [← card_pos]; exact hU
      obtain ⟨p, hp⟩ := hne
      rw [mem_filter, mem_range] at hp
      obtain ⟨x', y', h1, hPQ, hQP⟩ := pp_rot x y m p hp.1.le
      set P := pp x y p with hP
      set Q := pp (fun i => x (p + i)) (fun i => y (p + i)) (m - p) with hQ
      have hg : P * Q * (P * Q) = 1 := by rw [← hPQ, hprod]; exact hD2
      have hPi : P * (Q * (P * Q)) = 1 := by
        calc P * (Q * (P * Q)) = P * Q * (P * Q) := by simp only [Matrix.mul_assoc]
          _ = 1 := hg
      have hPi' : Q * (P * Q) * P = 1 := mul_eq_one_comm.1 hPi
      have hD'' : pp x' y' m * pp x' y' m = 1 := by
        rw [hQP]
        calc Q * P * (Q * P) = Q * (P * Q) * P := by simp only [Matrix.mul_assoc]
          _ = 1 := hPi'
      have h0 : y' 0 ⬝ᵥ x' 0 = 0 := by
        have := h1 0 (by omega)
        rw [this.1, this.2]; simpa using hp.2
      have hinv := inv_rank0 h2 m x' y' (fun _ => h0) hD''
      have e : (1 : Matrix n n K) - P * Q = P * (1 - Q * P) * (Q * (P * Q)) := by
        have : P * (1 - Q * P) * (Q * (P * Q)) = P * (Q * (P * Q)) - P * Q * (P * (Q * (P * Q))) := by
          noncomm_ring
        rw [this, hPi]; simp
      have hrk : (1 - pp x y m).rank ≤ (1 - pp x' y' m).rank := by
        rw [hPQ, hQP, e]
        exact (rank_mul_le_left _ _).trans (rank_mul_le_right _ _)
      have : nflip s ≤ m - 1 := by
        rw [← hr, ← hprod]; omega
      omega
    · simp only [hU, if_false]
      rw [← hr, ← hprod]; omega
  · have h3 := det_pp_pm h2 x y m hkind
    rw [hprod, det_diag_pm h2 s hs] at h3
    exact neg_one_pow_inj h2 _ _ h3

/-! ## §3. SYL_U (R21 B2 / R19): Sylvester with units, nested supports

The Sylvester step is `SpecCOV.char_syl` (`dim span x + dim span y ≤ m + rank(I - P)`, `m = J + U`).
The structural step "`s, t ≥ |R(S_μ)|`": for any sub-list `L ν` of the `m` factors whose ordered
product is `diag (s ν)`, `range(I - D_ν) ⊆ span x_i` and the row space `⊆ span y_i` (here for ANY list,
tight or not), hence `e_a ∈ span x ∩ span y` for every coordinate `a` flipped by some `D_ν`. -/

theorem rangex (x y : ℕ → n → K) (L : List ℕ) (v : n → K) :
    (1 - (L.map fun i => refl (x i) (y i)).prod) *ᵥ v ∈ Submodule.span K (x '' {i | i ∈ L}) := by
  induction L generalizing v with
  | nil => simp
  | cons i L ih =>
    have e : (1 - ((i :: L).map fun i => refl (x i) (y i)).prod) *ᵥ v =
        (1 - (L.map fun i => refl (x i) (y i)).prod) *ᵥ v +
          (y i ⬝ᵥ ((L.map fun i => refl (x i) (y i)).prod *ᵥ v)) • x i := by
      rw [List.map_cons, List.prod_cons, sub_mulVec, one_mulVec, sub_mulVec, one_mulVec,
        ← Matrix.mulVec_mulVec, refl_mulVec]
      abel
    rw [e]
    refine Submodule.add_mem _ (Submodule.span_mono ?_ (ih v)) (Submodule.smul_mem _ _
      (Submodule.subset_span ⟨i, by simp, rfl⟩))
    exact Set.image_mono fun j hj => by simp only [List.mem_cons, Set.mem_setOf_eq]; exact Or.inr hj

theorem rangey (x y : ℕ → n → K) (L : List ℕ) (v : n → K) :
    v ᵥ* (1 - (L.map fun i => refl (x i) (y i)).prod) ∈ Submodule.span K (y '' {i | i ∈ L}) := by
  induction L generalizing v with
  | nil => simp
  | cons i L ih =>
    have e : v ᵥ* (1 - ((i :: L).map fun i => refl (x i) (y i)).prod) =
        (v ⬝ᵥ x i) • y i +
          (v ᵥ* refl (x i) (y i)) ᵥ* (1 - (L.map fun i => refl (x i) (y i)).prod) := by
      rw [List.map_cons, List.prod_cons, vecMul_sub, vecMul_one, ← vecMul_vecMul, vecMul_sub,
        vecMul_one, vecMul_refl]
      abel
    rw [e]
    refine Submodule.add_mem _ (Submodule.smul_mem _ _ (Submodule.subset_span ⟨i, by simp, rfl⟩))
      (Submodule.span_mono ?_ (ih _))
    exact Set.image_mono fun j hj => by simp only [List.mem_cons, Set.mem_setOf_eq]; exact Or.inr hj

theorem single_mem_x (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (L : List ℕ) (s : n → K)
    (hprod : (L.map fun i => refl (x i) (y i)).prod = diagonal s) (a : n) (ha : s a = -1) :
    (Pi.single a 1 : n → K) ∈ Submodule.span K (x '' {i | i ∈ L}) := by
  have h := rangex x y L (Pi.single a 1)
  rw [hprod] at h
  have e : (1 - diagonal s : Matrix n n K) *ᵥ (Pi.single a 1 : n → K) = (2 : K) • Pi.single a 1 := by
    have : (1 - diagonal s : Matrix n n K) = diagonal fun b => 1 - s b := by
      ext b c; by_cases hbc : b = c <;> simp [diagonal_apply, Matrix.one_apply, hbc]
    ext b
    rw [this, mulVec_diagonal]
    by_cases hb : b = a
    · subst hb; simp [ha]; norm_num
    · simp [Pi.single_apply, hb]
  rw [e] at h
  exact (Submodule.smul_mem_iff _ h2).1 h

theorem single_mem_y (h2 : (2 : K) ≠ 0) (x y : ℕ → n → K) (L : List ℕ) (s : n → K)
    (hprod : (L.map fun i => refl (x i) (y i)).prod = diagonal s) (a : n) (ha : s a = -1) :
    (Pi.single a 1 : n → K) ∈ Submodule.span K (y '' {i | i ∈ L}) := by
  have h := rangey x y L (Pi.single a 1)
  rw [hprod] at h
  have e : (Pi.single a 1 : n → K) ᵥ* (1 - diagonal s : Matrix n n K) = (2 : K) • Pi.single a 1 := by
    have : (1 - diagonal s : Matrix n n K) = diagonal fun b => 1 - s b := by
      ext b c; by_cases hbc : b = c <;> simp [diagonal_apply, Matrix.one_apply, hbc]
    ext b
    rw [this, vecMul_diagonal]
    by_cases hb : b = a
    · subst hb; simp [ha]; norm_num
    · simp [Pi.single_apply, hb]
  rw [e] at h
  exact (Submodule.smul_mem_iff _ h2).1 h

theorem card_le_finrank_span (R : Finset n) (S : Submodule K (n → K))
    (h : ∀ a ∈ R, (Pi.single a 1 : n → K) ∈ S) : R.card ≤ Module.finrank K S := by
  let b : R → (n → K) := fun a => Pi.single a.1 1
  have li : LinearIndependent K b := by
    have := (Pi.basisFun K n).linearIndependent.comp (fun a : R => (a : n)) Subtype.val_injective
    convert this using 1
    funext a; simp [b]
  have h1 := finrank_span_eq_card li
  have h2 : Submodule.span K (Set.range b) ≤ S :=
    Submodule.span_le.2 (by rintro _ ⟨a, rfl⟩; exact h a.1 a.2)
  have := Submodule.finrank_mono h2
  simp only [Fintype.card_coe] at h1
  omega

/-- **SYL_U** (R21 B2; units are factors with `y·x = 0`; char ≠ 2).  `m` factors (jobs and units of the
character μ), full product `P`.  If sub-lists `L ν` of the factors multiply to diagonal sign matrices
`diag (s ν)` (the nested characters ν with `S_ν ⊆ S_μ`) and `R` is a set of coordinates each flipped
by some `ν`, then `2 |R| ≤ m + rank(I - P)`, i.e. `2|R(S_μ)| ≤ J + U + r`. -/
theorem SYL_U (h2 : (2 : K) ≠ 0) (m : ℕ) (x y : ℕ → n → K) {ι : Type*}
    (L : ι → List ℕ) (s : ι → n → K) (hL : ∀ ν, ∀ i ∈ L ν, i < m)
    (hprod : ∀ ν, ((L ν).map fun i => refl (x i) (y i)).prod = diagonal (s ν))
    (R : Finset n) (hR : ∀ a ∈ R, ∃ ν, s ν a = -1) :
    2 * R.card ≤ m + (1 - pp x y m).rank := by
  have hx : R.card ≤ Module.finrank K (Submodule.span K (x '' Set.Iio m)) := by
    apply card_le_finrank_span
    intro a ha
    obtain ⟨ν, hν⟩ := hR a ha
    refine Submodule.span_mono ?_ (single_mem_x h2 x y (L ν) (s ν) (hprod ν) a hν)
    exact Set.image_mono fun i hi => hL ν i hi
  have hy : R.card ≤ Module.finrank K (Submodule.span K (y '' Set.Iio m)) := by
    apply card_le_finrank_span
    intro a ha
    obtain ⟨ν, hν⟩ := hR a ha
    refine Submodule.span_mono ?_ (single_mem_y h2 x y (L ν) (s ν) (hprod ν) a hν)
    exact Set.image_mono fun i hi => hL ν i hi
  have := SpecCOV.char_syl x y m
  omega

/-- **Ureq lower bounds** (R49 item 4): at a unit character (`U ≥ 1` unit factors, `J` jobs, `m = J + U`,
full product `diag s`, `r` flips) with nested family giving `R`: `r + 1 ≤ J + U` and
`2|R| ≤ J + U + r`, i.e. `U ≥ max (r - J + 1, 2|R| - J - r)`. -/
theorem Ureq_lower (h2 : (2 : K) ≠ 0) (m : ℕ) (x y : ℕ → n → K)
    (hkind : ∀ i < m, y i ⬝ᵥ x i = 2 ∨ y i ⬝ᵥ x i = 0)
    (s : n → K) (hs : ∀ a, s a = 1 ∨ s a = -1) (hprod : pp x y m = diagonal s)
    (hU : 1 ≤ nU x y m) {ι : Type*}
    (L : ι → List ℕ) (sν : ι → n → K) (hL : ∀ ν, ∀ i ∈ L ν, i < m)
    (hLp : ∀ ν, ((L ν).map fun i => refl (x i) (y i)).prod = diagonal (sν ν))
    (R : Finset n) (hR : ∀ a ∈ R, ∃ ν, sν ν a = -1) :
    nflip s + 1 ≤ nJ x y m + nU x y m ∧ 2 * R.card ≤ nJ x y m + nU x y m + nflip s := by
  have h3 := (L3_U h2 m x y hkind s hs hprod).1
  have h4 := SYL_U h2 m x y L sν hL hLp R hR
  have h5 := nJ_add_nU h2 x y m hkind
  have hr : (1 - diagonal s : Matrix n n K).rank = nflip s := rank_one_sub_diag h2 s hs
  rw [hprod] at h4
  rw [hr] at h4
  simp only [hU, if_true] at h3
  omega

end Basics

/-! ## §4. #9 kill (R49 item 1; AUDIT49 SOUND-WITH-FIXES)

Jobs are labelled by `ℕ` (`x j`, `y j` on the target space `n₁`; they vanish on the dark/ancilla block
by Lemma TS (ii), which is what the block form `fromBlocks (pp ..) 0 0 1` of `J` records).  A tight
triple is a sequence `τ : ℕ → ℕ` of three job labels with ordered product `diag s`, 3 flips (Lemma TS
then gives Gram `2I`).  The clique at a unit character is a triple `c` of labels, every pair of which lies in
a tight triple. -/
section Kill9
variable {n₁ nd : Type*} [Fintype n₁] [Fintype nd] [DecidableEq n₁] [DecidableEq nd] [DecidableEq K]

/-- Lemma TS applied to a tight triple of job labels -/
theorem tight_gram (h2 : (2 : K) ≠ 0) (x y : ℕ → n₁ → K) (τ : ℕ → ℕ) (s : n₁ → K)
    (hs : ∀ a, s a = 1 ∨ s a = -1)
    (hprod : pp (fun i => x (τ i)) (fun i => y (τ i)) 3 = diagonal s) (hcard : nflip s = 3) :
    ∀ i < 3, ∀ j < 3, y (τ i) ⬝ᵥ x (τ j) = if i = j then 2 else 0 := by
  have := (lemmaTS 3 (fun i => x (τ i)) (fun i => y (τ i)) s h2 hs hprod hcard).1
  intro i hi j hj
  simpa using this ⟨i, hi⟩ ⟨j, hj⟩

/-- the clique `c` (three distinct labels) has Gram `2I` as soon as every ordered pair of distinct
members lies in a tight triple (`τ p = c i`, `τ q = c j`) -/
theorem clique_gram (h2 : (2 : K) ≠ 0) (x y : ℕ → n₁ → K) (c : ℕ → ℕ)
    (hinj : ∀ i < 3, ∀ j < 3, c i = c j → i = j)
    (hpair : ∀ i < 3, ∀ j < 3, i ≠ j → ∃ (τ : ℕ → ℕ) (s : n₁ → K), (∀ a, s a = 1 ∨ s a = -1) ∧
      pp (fun i => x (τ i)) (fun i => y (τ i)) 3 = diagonal s ∧ nflip s = 3 ∧
      ∃ p < 3, ∃ q < 3, τ p = c i ∧ τ q = c j) :
    ∀ i < 3, ∀ j < 3, y (c i) ⬝ᵥ x (c j) = if i = j then 2 else 0 := by
  intro i hi j hj
  by_cases hij : i = j
  · subst hij
    obtain ⟨j', hj', hne⟩ : ∃ j' < 3, i ≠ j' := by
      by_cases h : i = 0
      · exact ⟨1, by norm_num, by omega⟩
      · exact ⟨0, by norm_num, by omega⟩
    obtain ⟨τ, s, hs, hp, hc, p, hp3, q, hq3, hpi, hqj⟩ := hpair i hi j' hj' hne
    have := tight_gram h2 x y τ s hs hp hc p hp3 p hp3
    rw [hpi] at this
    simpa using this
  · obtain ⟨τ, s, hs, hp, hc, p, hp3, q, hq3, hpi, hqj⟩ := hpair i hi j hj hij
    have hpq : p ≠ q := by
      intro h; subst h; exact hij (hinj i hi j hj (hpi.symm.trans hqj))
    have := tight_gram h2 x y τ s hs hp hc p hp3 q hq3
    rw [hpi, hqj] at this
    simpa [hpq, hij] using this

/-- **#9 per unit character (R49 item 1).** Clique `c` (three jobs, each pair in a tight triple),
`D_μ = diag s₁ ⊕ diag sd` with `r₁ = 1` flipped target in `E` and no dark flip, `J_μ = clique ⊕ I`,
commuting involutions, units transvections ⇒ `U ≥ 3`. -/
theorem kill9_char (h2 : (2 : K) ≠ 0) (x y : ℕ → n₁ → K) (c : ℕ → ℕ)
    (hinj : ∀ i < 3, ∀ j < 3, c i = c j → i = j)
    (hpair : ∀ i < 3, ∀ j < 3, i ≠ j → ∃ (τ : ℕ → ℕ) (s : n₁ → K), (∀ a, s a = 1 ∨ s a = -1) ∧
      pp (fun i => x (τ i)) (fun i => y (τ i)) 3 = diagonal s ∧ nflip s = 3 ∧
      ∃ p < 3, ∃ q < 3, τ p = c i ∧ τ q = c j)
    (s₁ : n₁ → K) (sd : nd → K) (hs₁ : ∀ a, s₁ a = 1 ∨ s₁ a = -1) (hsd : ∀ a, sd a = 1 ∨ sd a = -1)
    (hr1 : nflip s₁ = 1) (hd0 : nflip sd = 0)
    (w : List ((Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ ⊕ (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n₁ ⊕ nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) = refl a b)
    (hD : ((ev w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (diagonal s₁) 0 0 (diagonal sd))
    (hJ : ((jobsP w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (pp (fun i => x (c i)) (fun i => y (c i)) 3) 0 0 1)
    (hD2 : ev w * ev w = 1) (hJ2 : jobsP w * jobsP w = 1) (hc : ev w * jobsP w = jobsP w * ev w) :
    3 ≤ ucount w := by
  have hg := clique_gram h2 x y c hinj hpair
  have := UR_inv_combined h2 3 (fun i => x (c i)) (fun i => y (c i)) hg s₁ sd hs₁ hsd w hform hD hJ
    hD2 hJ2 hc
  unfold nflip at hr1 hd0
  rw [hr1, hd0] at this
  omega

/-- **#9 DEAD.** Four unit characters (R26 forms mu = 1 ADF, 6 BCF, 10 BDE, 13 ACE), each with the
data of `kill9_char`: every replayed word has `≥ 3` units; with `U` units active at each character
(`ucount (w μ) = U`), `U ≤ 2` is impossible (mindef = 2, so no SC_Z violation at any U). -/
theorem kill9 (h2 : (2 : K) ≠ 0) (x y : ℕ → n₁ → K)
    (c : Fin 4 → ℕ → ℕ)
    (hinj : ∀ μ, ∀ i < 3, ∀ j < 3, c μ i = c μ j → i = j)
    (hpair : ∀ μ, ∀ i < 3, ∀ j < 3, i ≠ j → ∃ (τ : ℕ → ℕ) (s : n₁ → K), (∀ a, s a = 1 ∨ s a = -1) ∧
      pp (fun i => x (τ i)) (fun i => y (τ i)) 3 = diagonal s ∧ nflip s = 3 ∧
      ∃ p < 3, ∃ q < 3, τ p = c μ i ∧ τ q = c μ j)
    (s₁ : Fin 4 → n₁ → K) (sd : Fin 4 → nd → K)
    (hs₁ : ∀ μ a, s₁ μ a = 1 ∨ s₁ μ a = -1) (hsd : ∀ μ a, sd μ a = 1 ∨ sd μ a = -1)
    (hr1 : ∀ μ, nflip (s₁ μ) = 1) (hd0 : ∀ μ, nflip (sd μ) = 0)
    (w : Fin 4 → List ((Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ ⊕ (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ))
    (hform : ∀ μ t, Sum.inl t ∈ w μ → ∃ a b : n₁ ⊕ nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) = refl a b)
    (hD : ∀ μ, ((ev (w μ) : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (diagonal (s₁ μ)) 0 0 (diagonal (sd μ)))
    (hJ : ∀ μ, ((jobsP (w μ) : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (pp (fun i => x (c μ i)) (fun i => y (c μ i)) 3) 0 0 1)
    (hD2 : ∀ μ, ev (w μ) * ev (w μ) = 1) (hJ2 : ∀ μ, jobsP (w μ) * jobsP (w μ) = 1)
    (hc : ∀ μ, ev (w μ) * jobsP (w μ) = jobsP (w μ) * ev (w μ)) :
    ∀ μ, 3 ≤ ucount (w μ) := fun μ =>
  kill9_char h2 x y (c μ) (hinj μ) (hpair μ) (s₁ μ) (sd μ) (hs₁ μ) (hsd μ) (hr1 μ) (hd0 μ)
    (w μ) (hform μ) (hD μ) (hJ μ) (hD2 μ) (hJ2 μ) (hc μ)

/-- a Gram-`2I` clique of `k = dim E` jobs has product `-I_E` (paper: "`J = -I_E`") -/
theorem clique_neg_one (h2 : (2 : K) ≠ 0) (k : ℕ) (x y : ℕ → n₁ → K) (hcard : Fintype.card n₁ = k)
    (hg : ∀ i < k, ∀ j < k, y i ⬝ᵥ x j = if i = j then 2 else 0) : pp x y k = -1 := by
  rw [pp_clique k x y hg]
  let e : n₁ ≃ Fin k := Fintype.equivFinOfCardEq hcard
  let X' : Matrix n₁ n₁ K := Matrix.of fun a b => x (e b) a
  let Y' : Matrix n₁ n₁ K := Matrix.of fun a b => y (e b) a
  have h1 : Y'ᵀ * X' = (2 : K) • 1 := by
    ext b b'
    simp only [Y', X', Matrix.mul_apply, Matrix.transpose_apply, Matrix.of_apply, Matrix.smul_apply,
      Matrix.one_apply]
    have := hg (e b) (e b).2 (e b') (e b').2
    simp only [dotProduct] at this
    rw [this]
    by_cases hbb : b = b'
    · subst hbb; simp
    · have : ¬ ((e b : ℕ) = e b') := fun h => hbb (e.injective (Fin.ext h))
      simp [this, hbb]
  have h2' : X' * Y'ᵀ = (2 : K) • 1 := by
    have h2i : (2 : K)⁻¹ • Y'ᵀ * X' = 1 := by
      rw [Matrix.smul_mul, h1, smul_smul, inv_mul_cancel₀ h2, one_smul]
    have := mul_eq_one_comm.1 h2i
    have h3 : X' * Y'ᵀ = (2 : K) • (X' * ((2 : K)⁻¹ • Y'ᵀ)) := by
      rw [Matrix.mul_smul, smul_smul, mul_inv_cancel₀ h2, one_smul]
    rw [h3, this]
  have h4 : Xm x k * (Matrix.of fun a (i : Fin k) => y i a)ᵀ = X' * Y'ᵀ := by
    ext a a'
    simp only [Xm, Matrix.mul_apply, Matrix.transpose_apply, Matrix.of_apply, X', Y']
    exact (Equiv.sum_comp e fun j : Fin k => x j a * y j a').symm
  rw [h4, h2']
  ext a b
  by_cases hab : a = b <;> simp [Matrix.one_apply, hab] <;> ring

/-- **#9 per unit character, literal chain** (paper: tight pairs ⇒ Gram `2I` ⇒ `J = -I_E` ⇒
`rank(D - J) = rank(I + D|E) = 2` ⇒ INV `rank(D - J) ≤ U - 1` ⇒ `U ≥ 3`).  `dim E = 3`. -/
theorem kill9_char_literal (h2 : (2 : K) ≠ 0) (x y : ℕ → n₁ → K) (c : ℕ → ℕ)
    (hE : Fintype.card n₁ = 3)
    (hinj : ∀ i < 3, ∀ j < 3, c i = c j → i = j)
    (hpair : ∀ i < 3, ∀ j < 3, i ≠ j → ∃ (τ : ℕ → ℕ) (s : n₁ → K), (∀ a, s a = 1 ∨ s a = -1) ∧
      pp (fun i => x (τ i)) (fun i => y (τ i)) 3 = diagonal s ∧ nflip s = 3 ∧
      ∃ p < 3, ∃ q < 3, τ p = c i ∧ τ q = c j)
    (s₁ : n₁ → K) (hs₁ : ∀ a, s₁ a = 1 ∨ s₁ a = -1) (hr1 : nflip s₁ = 1)
    (w : List ((Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ ⊕ (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ))
    (hform : ∀ t, Sum.inl t ∈ w → ∃ a b : n₁ ⊕ nd → K, b ⬝ᵥ a = 0 ∧
      (t : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) = refl a b)
    (hD : ((ev w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (diagonal s₁) 0 0 1)
    (hJ : ((jobsP w : (Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K)ˣ) : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) =
      fromBlocks (pp (fun i => x (c i)) (fun i => y (c i)) 3) 0 0 1)
    (hD2 : ev w * ev w = 1) (hJ2 : jobsP w * jobsP w = 1) (hc : ev w * jobsP w = jobsP w * ev w) :
    2 ≤ (fromBlocks (diagonal s₁ + 1) 0 0 (0 : Matrix nd nd K)).rank ∧ 3 ≤ ucount w := by
  have hg := clique_gram h2 x y c hinj hpair
  have hJE := clique_neg_one h2 3 (fun i => x (c i)) (fun i => y (c i)) hE hg
  have hDJ : (fromBlocks (diagonal s₁) 0 0 1 : Matrix (n₁ ⊕ nd) (n₁ ⊕ nd) K) -
      fromBlocks (-1) 0 0 1 = fromBlocks (diagonal s₁ + 1) 0 0 (0 : Matrix nd nd K) := by
    ext (i | i) (j | j) <;> simp [Matrix.one_apply, diagonal_apply] <;> ring
  have hrk : (diagonal s₁ + 1 : Matrix n₁ n₁ K).rank = 2 := by
    have e : (diagonal s₁ + 1 : Matrix n₁ n₁ K) = diagonal fun a => s₁ a + 1 := by
      ext a b; by_cases hab : a = b <;> simp [diagonal_apply, Matrix.one_apply, hab]
    rw [e, rank_diagonal]
    have hn : Fintype.card {a // s₁ a + 1 ≠ 0} = (univ.filter fun a => ¬ (s₁ a = -1)).card := by
      rw [Fintype.card_subtype]
      congr 1
      apply filter_congr
      intro a _
      constructor
      · intro h h'; apply h; rw [h']; ring
      · intro h h'; apply h; linear_combination h'
    rw [hn]
    have := Finset.card_filter_add_card_filter_not (s := (univ : Finset n₁)) (fun a => s₁ a = -1)
    rw [Finset.card_univ, hE] at this
    unfold nflip at hr1
    omega
  have hrank : 2 ≤ (fromBlocks (diagonal s₁ + 1) 0 0 (0 : Matrix nd nd K)).rank := by
    have hge := rank_fromBlocks_diag_ge (diagonal s₁ + 1 : Matrix n₁ n₁ K) (0 : Matrix nd nd K)
    omega
  refine ⟨hrank, ?_⟩
  have hinv := inv_DJ h2 w hform hD2 hJ2 hc
  rw [hD, hJ, hJE] at hinv
  have hD1 : (fromBlocks (diagonal s₁) 0 0 (1 : Matrix nd nd K)) -
      fromBlocks (-1) 0 0 (1 : Matrix nd nd K) = fromBlocks (diagonal s₁ + 1) 0 0 0 := hDJ
  rw [hD1] at hinv
  omega

end Kill9

/-! ## §5. #1 at U ≤ 3 (R49 item 3; AUDIT49 stronger form)

Targets 1..5 and ancillas: `V = Fin 1 ⊕ (Fin 2 ⊕ (Fin 2 ⊕ nd))` = e1 ⊕ <e2,e3> ⊕ <e4,e5> ⊕ dark.
Clique BCEF: the jobs B, C act on the e23 block as reflections `JB`, `JC` with `JB JC = -I` (tight BC),
E, F on the e45 block with `JE JF = -I` (tight EF), identity elsewhere (Lemma TS).  `R2 = diag(-1,1)`
(= R_2 on e23, = R_4 on e45), `R3 = diag(1,-1)` (= R_3, = R_5).  `N23 := R2 JC` (= R3 JB), `N45 := R2 JF`
(= R3 JE); `a = rank(I - N23)`, `a' = rank(I + N23)`, `b`, `b'` likewise. -/
section Kill1
variable {nd : Type*} [Fintype nd] [DecidableEq nd] [DecidableEq K]

abbrev VV (nd : Type*) := Fin 1 ⊕ (Fin 2 ⊕ (Fin 2 ⊕ nd))

def bd4 (a : Matrix (Fin 1) (Fin 1) K) (b c : Matrix (Fin 2) (Fin 2) K) (d : Matrix nd nd K) :
    Matrix (VV nd) (VV nd) K :=
  fromBlocks a 0 0 (fromBlocks b 0 0 (fromBlocks c 0 0 d))

theorem bd4_mul (a a' : Matrix (Fin 1) (Fin 1) K) (b b' c c' : Matrix (Fin 2) (Fin 2) K)
    (d d' : Matrix nd nd K) : bd4 a b c d * bd4 a' b' c' d' = bd4 (a * a') (b * b') (c * c') (d * d') := by
  simp [bd4, fromBlocks_multiply]

theorem bd4_sub (a a' : Matrix (Fin 1) (Fin 1) K) (b b' c c' : Matrix (Fin 2) (Fin 2) K)
    (d d' : Matrix nd nd K) : bd4 a b c d - bd4 a' b' c' d' = bd4 (a - a') (b - b') (c - c') (d - d') := by
  ext (i | i | i | i) (j | j | j | j) <;> simp [bd4, Matrix.sub_apply]

theorem rank_bd4_ge (a : Matrix (Fin 1) (Fin 1) K) (b c : Matrix (Fin 2) (Fin 2) K) (d : Matrix nd nd K) :
    a.rank + b.rank + c.rank + d.rank ≤ (bd4 a b c d).rank := by
  have h1 := rank_fromBlocks_diag_ge c d
  have h2 := rank_fromBlocks_diag_ge b (fromBlocks c 0 0 d)
  have h3 := rank_fromBlocks_diag_ge a (fromBlocks b 0 0 (fromBlocks c 0 0 d))
  unfold bd4
  omega

theorem rank_le_of_inv (R C : Matrix (Fin 2) (Fin 2) K) (hR : R * R = 1) :
    (1 - R * C).rank ≤ (R - C).rank := by
  have : (1 : Matrix (Fin 2) (Fin 2) K) - R * C = R * (R - C) := by
    rw [mul_sub, hR]
  rw [this]; exact rank_mul_le_right _ _

def R2 : Matrix (Fin 2) (Fin 2) K := diagonal ![-1, 1]
def R3 : Matrix (Fin 2) (Fin 2) K := diagonal ![1, -1]

theorem R2_mul : (R2 : Matrix (Fin 2) (Fin 2) K) * R2 = 1 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [R2, diagonal_apply, Matrix.mul_apply, Fin.sum_univ_two]
theorem R3_mul : (R3 : Matrix (Fin 2) (Fin 2) K) * R3 = 1 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [R3, diagonal_apply, Matrix.mul_apply, Fin.sum_univ_two]
theorem R3_eq : (R3 : Matrix (Fin 2) (Fin 2) K) = -R2 := by
  ext i j; fin_cases i <;> fin_cases j <;> simp [R2, R3, diagonal_apply]
theorem det_R2 : (R2 : Matrix (Fin 2) (Fin 2) K).det = -1 := by
  simp [R2, det_diagonal, Fin.prod_univ_two]

theorem refl_sq (x y : Fin 2 → K) (h : y ⬝ᵥ x = 2) :
    SpecTSUR.refl x y * SpecTSUR.refl x y = 1 := by
  have hAA : vecMulVec x y * vecMulVec x y = (2 : K) • vecMulVec x y := by
    rw [vecMulVec_mul_vecMulVec, h, Matrix.vecMulVec_smul]
  rw [SpecTSUR.refl]
  calc (1 - vecMulVec x y) * (1 - vecMulVec x y)
      = 1 - vecMulVec x y - vecMulVec x y + vecMulVec x y * vecMulVec x y := by noncomm_ring
    _ = 1 := by rw [hAA, two_smul]; abel

/-! ### 2x2 facts -/
theorem det_one_sub2 (N : Matrix (Fin 2) (Fin 2) K) : (1 - N).det = 1 - (N 0 0 + N 1 1) + N.det := by
  simp [Matrix.det_fin_two]; ring

theorem det_one_add2 (N : Matrix (Fin 2) (Fin 2) K) : (1 + N).det = 1 + (N 0 0 + N 1 1) + N.det := by
  simp [Matrix.det_fin_two]; ring

theorem rank_two_of_det (M : Matrix (Fin 2) (Fin 2) K) (h : M.det ≠ 0) : M.rank = 2 := by
  have := rank_of_isUnit M ((Matrix.isUnit_iff_isUnit_det M).2 (isUnit_iff_ne_zero.2 h))
  simpa using this

theorem det_zero_of_rank (M : Matrix (Fin 2) (Fin 2) K) (h : M.rank ≤ 1) : M.det = 0 := by
  by_contra hne
  have := rank_two_of_det M hne
  omega

/-- `N ∈ SL₂`: `rank(I - N) ≤ 1 ⇒ rank(I + N) = 2` and `rank(I + N) ≤ 1 ⇒ rank(I - N) = 2` (char ≠ 2) -/
theorem sl2_dual (h2 : (2 : K) ≠ 0) (N : Matrix (Fin 2) (Fin 2) K) (hN : N.det = 1) :
    ((1 - N).rank ≤ 1 → (1 + N).rank = 2) ∧ ((1 + N).rank ≤ 1 → (1 - N).rank = 2) := by
  have h4 : (4 : K) ≠ 0 := by
    have : (4 : K) = 2 * 2 := by norm_num
    rw [this]; exact mul_ne_zero h2 h2
  constructor
  · intro h
    have h0 := det_zero_of_rank _ h
    rw [det_one_sub2, hN] at h0
    apply rank_two_of_det
    rw [det_one_add2, hN]
    intro h'
    apply h4; linear_combination h' + h0
  · intro h
    have h0 := det_zero_of_rank _ h
    rw [det_one_add2, hN] at h0
    apply rank_two_of_det
    rw [det_one_sub2, hN]
    intro h'
    apply h4; linear_combination h' + h0

theorem rank_pm2 (h2 : (2 : K) ≠ 0) : ((1 : Matrix (Fin 2) (Fin 2) K) - (-1)).rank = 2 := by
  apply rank_two_of_det
  simp [Matrix.det_fin_two]
  intro h; apply h2; linear_combination h

theorem rank_neg_two (h2 : (2 : K) ≠ 0) : ((-1 - 1 : Matrix (Fin 1) (Fin 1) K)).rank = 1 := by
  have := rank_of_isUnit (-1 - 1 : Matrix (Fin 1) (Fin 1) K) (by
    rw [Matrix.isUnit_iff_isUnit_det, isUnit_iff_ne_zero]
    simp [Matrix.det_unique]
    intro h; apply h2; linear_combination -h)
  simpa using this

/-- the clique blocks: `JB = -JC`, `N23 = R2 JC = R3 JB`, `R3 JC = -N23 = R2 JB`, `det N23 = 1` -/
theorem Nfacts (x y : Fin 2 → K) (h : y ⬝ᵥ x = 2) (JB : Matrix (Fin 2) (Fin 2) K)
    (hB : JB * SpecTSUR.refl x y = -1) :
    JB = -SpecTSUR.refl x y ∧ (R3 : Matrix (Fin 2) (Fin 2) K) * JB = R2 * SpecTSUR.refl x y ∧
      R3 * SpecTSUR.refl x y = -(R2 * SpecTSUR.refl x y) ∧
      R2 * JB = -(R2 * SpecTSUR.refl x y) ∧ (R2 * SpecTSUR.refl x y).det = 1 := by
  have hJB : JB = -SpecTSUR.refl x y := by
    calc JB = JB * (SpecTSUR.refl x y * SpecTSUR.refl x y) := by rw [refl_sq x y h, mul_one]
      _ = (JB * SpecTSUR.refl x y) * SpecTSUR.refl x y := by rw [Matrix.mul_assoc]
      _ = _ := by rw [hB]; simp
  refine ⟨hJB, ?_, ?_, ?_, ?_⟩
  · rw [hJB, R3_eq]; simp
  · rw [R3_eq]; simp
  · rw [hJB]; simp
  · rw [det_mul, det_R2, SpecINV.det_refl, h]; norm_num

/-! ### free-job steps -/
theorem rank_refl_sub_one (x y : Fin 2 → K) :
    ((SpecTSUR.refl x y : Matrix (Fin 2) (Fin 2) K) - 1).rank ≤ 1 := by
  have : (SpecTSUR.refl x y : Matrix (Fin 2) (Fin 2) K) - 1 = -vecMulVec x y := by
    rw [SpecTSUR.refl]; abel
  rw [this, rank_neg_eq]; exact rank_vecMulVec_le x y

/-- **free-job step (unit-free character)**: `D = a c d f` (jobs `a, d` free, `c, f` in the clique) gives
`rank(D - c f) ≤ 2`, and with the block forms `rank(Ri - Cc) + rank(Rj - Cf) ≤ 2`. -/
theorem unitfree_core (Dm a c d f : Matrix (VV nd) (VV nd) K) (hDm : Dm = a * c * d * f)
    (ha : (a - 1).rank ≤ 1) (hd : (d - 1).rank ≤ 1)
    (Ri Rj Cc Cf : Matrix (Fin 2) (Fin 2) K)
    (hD : Dm = bd4 1 Ri Rj 1) (hcf : c * f = bd4 1 Cc Cf 1) :
    (Ri - Cc).rank + (Rj - Cf).rank ≤ 2 := by
  have e : Dm - c * f = (a - 1) * (c * d * f) + c * (d - 1) * f := by rw [hDm]; noncomm_ring
  have h1 : (Dm - c * f).rank ≤ 2 := by
    rw [e]
    refine (rank_add_le' _ _).trans ?_
    have := rank_mul_le_left (a - 1) (c * d * f)
    have h3 : (c * (d - 1) * f).rank ≤ 1 :=
      ((rank_mul_le_left _ _).trans (rank_mul_le_right _ _)).trans hd
    omega
  have e2 : Dm - c * f = bd4 (1 - 1) (Ri - Cc) (Rj - Cf) (1 - 1) := by rw [hD, hcf, bd4_sub]
  have h4 := rank_bd4_ge (1 - 1 : Matrix (Fin 1) (Fin 1) K) (Ri - Cc) (Rj - Cf) (1 - 1 : Matrix nd nd K)
  rw [← e2] at h4
  omega

/-- **free-job step (unit character)**: `J = P d Q` with `d` a free reflection, `P Q` the clique part;
`D = bd4 (-1) Pβ Pγ 1`, `P Q = bd4 1 Mβ Mγ 1`, UR: `1 + rank(Pβ - Mβ) + rank(Pγ - Mγ) ≤ U + 1`. -/
theorem unit_core (h2 : (2 : K) ≠ 0)
    (w : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (hunits : ∀ t, Sum.inl t ∈ w → ((t : Matrix (VV nd) (VV nd) K) - 1).rank ≤ 1)
    (P d Q : Matrix (VV nd) (VV nd) K) (Pβ Pγ Mβ Mγ : Matrix (Fin 2) (Fin 2) K)
    (hD : ((ev w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = bd4 (-1) Pβ Pγ 1)
    (hJ : ((jobsP w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = P * d * Q)
    (hd : (d - 1).rank ≤ 1) (hcl : P * Q = bd4 1 Mβ Mγ 1) :
    1 + (Pβ - Mβ).rank + (Pγ - Mγ).rank ≤ ucount w + 1 := by
  have hup := UR_upper w hunits
  rw [hD, hJ] at hup
  have e : (bd4 (-1) Pβ Pγ 1 : Matrix (VV nd) (VV nd) K) - P * Q =
      (bd4 (-1) Pβ Pγ 1 - P * d * Q) + P * (d - 1) * Q := by noncomm_ring
  have h1 : (bd4 (-1) Pβ Pγ 1 - P * Q : Matrix (VV nd) (VV nd) K).rank ≤ ucount w + 1 := by
    rw [e]
    refine (rank_add_le' _ _).trans ?_
    have h3 : (P * (d - 1) * Q).rank ≤ 1 :=
      ((rank_mul_le_left _ _).trans (rank_mul_le_right _ _)).trans hd
    omega
  have e2 : (bd4 (-1) Pβ Pγ 1 - P * Q : Matrix (VV nd) (VV nd) K) =
      bd4 (-1 - 1) (Pβ - Mβ) (Pγ - Mγ) (1 - 1) := by rw [hcl, bd4_sub]
  have h4 := rank_bd4_ge (-1 - 1 : Matrix (Fin 1) (Fin 1) K) (Pβ - Mβ) (Pγ - Mγ) (1 - 1 : Matrix nd nd K)
  rw [← e2, rank_neg_two h2] at h4
  omega

/-! ### the clique jobs, character data, and the U ≤ 3 kill -/

/-- job acting as `J` on the e23 block, identity elsewhere -/
def jm23 (J : Matrix (Fin 2) (Fin 2) K) : Matrix (VV nd) (VV nd) K := bd4 1 J 1 1
/-- job acting as `J` on the e45 block, identity elsewhere -/
def jm45 (J : Matrix (Fin 2) (Fin 2) K) : Matrix (VV nd) (VV nd) K := bd4 1 1 J 1

theorem jm23_mul (J J' : Matrix (Fin 2) (Fin 2) K) :
    (jm23 J * jm23 J' : Matrix (VV nd) (VV nd) K) = bd4 1 (J * J') 1 1 := by
  simp [jm23, bd4_mul]
theorem jm45_mul (J J' : Matrix (Fin 2) (Fin 2) K) :
    (jm45 J * jm45 J' : Matrix (VV nd) (VV nd) K) = bd4 1 1 (J * J') 1 := by
  simp [jm45, bd4_mul]
theorem jm23_jm45 (J J' : Matrix (Fin 2) (Fin 2) K) :
    (jm23 J * jm45 J' : Matrix (VV nd) (VV nd) K) = bd4 1 J J' 1 := by
  simp [jm23, jm45, bd4_mul]

theorem pr_a (J J' J'' : Matrix (Fin 2) (Fin 2) K) :
    (jm23 J * jm23 J' * jm45 J'' : Matrix (VV nd) (VV nd) K) = bd4 1 (J * J') J'' 1 := by
  simp [jm23, jm45, bd4_mul]
theorem pr_b (J J' J'' : Matrix (Fin 2) (Fin 2) K) :
    (jm23 J * jm45 J' * jm45 J'' : Matrix (VV nd) (VV nd) K) = bd4 1 J (J' * J'') 1 := by
  simp [jm23, jm45, bd4_mul]

/-- character data of a UNIT character: the word `w` (units rank(t-1) ≤ 1 and jobs) multiplies to
`Dm` (`ev`), its ordered job product is `P d Q` with `d` a free reflection -/
def UC (w : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (Dm P d Q : Matrix (VV nd) (VV nd) K) : Prop :=
  (∀ t, Sum.inl t ∈ w → ((t : Matrix (VV nd) (VV nd) K) - 1).rank ≤ 1) ∧
  ((ev w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = Dm ∧
  ((jobsP w : (Matrix (VV nd) (VV nd) K)ˣ) : Matrix (VV nd) (VV nd) K) = P * d * Q ∧
  (d - 1).rank ≤ 1

/-- characters 6 (BCDF) / 14 (BCDE): free job D between the clique pairs; `U ≥ 2 + rank(Pγ - Mγ)` -/
theorem unit_gamma (h2 : (2 : K) ≠ 0) (w : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (P d Q : Matrix (VV nd) (VV nd) K) (Pγ Mγ : Matrix (Fin 2) (Fin 2) K)
    (hUC : UC w (bd4 (-1) 1 Pγ 1) P d Q) (hcl : P * Q = bd4 1 (-1) Mγ 1) :
    2 + (Pγ - Mγ).rank ≤ ucount w := by
  obtain ⟨hu, hD, hJ, hd⟩ := hUC
  have := unit_core h2 w hu P d Q 1 Pγ (-1) Mγ hD hJ hd hcl
  rw [rank_pm2 h2] at this
  omega

/-- characters 9 (ACEF) / 11 (ABEF): free job A in front; `U ≥ 2 + rank(Pβ - Mβ)` -/
theorem unit_beta (h2 : (2 : K) ≠ 0) (w : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (P d Q : Matrix (VV nd) (VV nd) K) (Pβ Mβ : Matrix (Fin 2) (Fin 2) K)
    (hUC : UC w (bd4 (-1) Pβ 1 1) P d Q) (hcl : P * Q = bd4 1 Mβ (-1) 1) :
    2 + (Pβ - Mβ).rank ≤ ucount w := by
  obtain ⟨hu, hD, hJ, hd⟩ := hUC
  have := unit_core h2 w hu P d Q Pβ 1 Mβ (-1) hD hJ hd hcl
  rw [rank_pm2 h2] at this
  omega

/-- **#1 at U ≤ 3 (AUDIT49's stronger form).** Clique blocks `JC = refl xC yC`, `JF = refl xF yF` (`y·x = 2`),
`JB JC = -I`, `JE JF = -I`.  Unit-free character 5 (ACDF: D = R2 ⊕ R2 on e23 ⊕ e45, jobs A, D free):
`a + b ≤ 2`.  Unit characters 6 (BCDF, free D), 14 (BCDE, free D), 9 (ACEF, free A), 11 (ABEF, free A) with
`D_μ` flipping e1 and one of e23/e45: `U ≥ 2 + b'` (6, 14), `U ≥ 2 + a'` (9, 11).
Conclusion: `U ≥ 4` at both chars 6, 14 or at both chars 9, 11.  In particular `U ≤ 3` is impossible. -/
theorem kill1 (h2 : (2 : K) ≠ 0) (xC yC xF yF : Fin 2 → K) (hC : yC ⬝ᵥ xC = 2) (hF : yF ⬝ᵥ xF = 2)
    (JB JE : Matrix (Fin 2) (Fin 2) K)
    (hBC : JB * SpecTSUR.refl xC yC = -1) (hEF : JE * SpecTSUR.refl xF yF = -1)
    -- unit-free character 5 = ACDF
    (a5 d5 : Matrix (VV nd) (VV nd) K)
    (hD5 : (bd4 1 R2 R2 1 : Matrix (VV nd) (VV nd) K) =
      a5 * jm23 (SpecTSUR.refl xC yC) * d5 * jm45 (SpecTSUR.refl xF yF))
    (ha5 : (a5 - 1).rank ≤ 1) (hd5 : (d5 - 1).rank ≤ 1)
    -- unit characters
    (w6 w14 w9 w11 : List ((Matrix (VV nd) (VV nd) K)ˣ ⊕ (Matrix (VV nd) (VV nd) K)ˣ))
    (d6 d14 d9 d11 : Matrix (VV nd) (VV nd) K)
    (h6 : UC w6 (bd4 (-1) 1 R3 1) (jm23 JB * jm23 (SpecTSUR.refl xC yC)) d6 (jm45 (SpecTSUR.refl xF yF)))
    (h14 : UC w14 (bd4 (-1) 1 R2 1) (jm23 JB * jm23 (SpecTSUR.refl xC yC)) d14 (jm45 JE))
    (h9 : UC w9 (bd4 (-1) R3 1 1) 1 d9 (jm23 (SpecTSUR.refl xC yC) * jm45 JE * jm45 (SpecTSUR.refl xF yF)))
    (h11 : UC w11 (bd4 (-1) R2 1 1) 1 d11 (jm23 JB * jm45 JE * jm45 (SpecTSUR.refl xF yF)))
    (U : ℕ) (hu6 : ucount w6 = U) (hu14 : ucount w14 = U) (hu9 : ucount w9 = U) (hu11 : ucount w11 = U) :
    4 ≤ U ∧ ((4 ≤ ucount w6 ∧ 4 ≤ ucount w14) ∨ (4 ≤ ucount w9 ∧ 4 ≤ ucount w11)) := by
  obtain ⟨eB, hB3, hC3, hB2, hdet23⟩ := Nfacts xC yC hC JB hBC
  obtain ⟨eE, hE3, hF3, hE2, hdet45⟩ := Nfacts xF yF hF JE hEF
  set JC := SpecTSUR.refl xC yC with hJC
  set JF := SpecTSUR.refl xF yF with hJF
  set N23 := (R2 : Matrix (Fin 2) (Fin 2) K) * JC with hN23
  set N45 := (R2 : Matrix (Fin 2) (Fin 2) K) * JF with hN45
  -- (i) free jobs, unit-free character 5
  have hab := unitfree_core (bd4 1 R2 R2 1) a5 (jm23 JC) d5 (jm45 JF) hD5 ha5 hd5 R2 R2 JC JF rfl
    (by rw [jm23_jm45])
  have ha : (1 - N23).rank ≤ (R2 - JC).rank := rank_le_of_inv R2 JC R2_mul
  have hb : (1 - N45).rank ≤ (R2 - JF).rank := rank_le_of_inv R2 JF R2_mul
  -- (ii) unit characters
  have u6 := unit_gamma h2 w6 _ d6 _ R3 JF h6 (by rw [pr_a, hBC])
  have u14 := unit_gamma h2 w14 _ d14 _ R2 JE h14 (by rw [pr_a, hBC])
  have u9 := unit_beta h2 w9 _ d9 _ R3 JC h9 (by rw [one_mul, pr_b, hEF])
  have u11 := unit_beta h2 w11 _ d11 _ R2 JB h11 (by rw [one_mul, pr_b, hEF])
  have k6 : (1 + N45).rank ≤ (R3 - JF).rank := by
    have := rank_le_of_inv R3 JF R3_mul
    rwa [hF3, sub_neg_eq_add] at this
  have k14 : (1 + N45).rank ≤ (R2 - JE).rank := by
    have := rank_le_of_inv R2 JE R2_mul
    rwa [hE2, sub_neg_eq_add] at this
  have k9 : (1 + N23).rank ≤ (R3 - JC).rank := by
    have := rank_le_of_inv R3 JC R3_mul
    rwa [hC3, sub_neg_eq_add] at this
  have k11 : (1 + N23).rank ≤ (R2 - JB).rank := by
    have := rank_le_of_inv R2 JB R2_mul
    rwa [hB2, sub_neg_eq_add] at this
  have hsl23 := sl2_dual h2 N23 hdet23
  have hsl45 := sl2_dual h2 N45 hdet45
  by_cases hA : (1 - N23).rank ≤ 1
  · have := hsl23.1 hA
    refine ⟨by omega, Or.inr ⟨by omega, by omega⟩⟩
  · have hB : (1 - N45).rank ≤ 1 := by omega
    have := hsl45.1 hB
    refine ⟨by omega, Or.inl ⟨by omega, by omega⟩⟩

/-- unit-free characters 7, 13, 15 give the same bound `a + b ≤ 2` (R49: "all four chars give the same
N23, N45"); char 7 = ABDF (D = R3 ⊕ R2, clique B, F), 13 = ACDE (R2 ⊕ R3, C, E), 15 = ABDE (R3 ⊕ R3, B, E). -/
theorem unitfree_other (xC yC xF yF : Fin 2 → K) (hC : yC ⬝ᵥ xC = 2) (hF : yF ⬝ᵥ xF = 2)
    (JB JE : Matrix (Fin 2) (Fin 2) K)
    (hBC : JB * SpecTSUR.refl xC yC = -1) (hEF : JE * SpecTSUR.refl xF yF = -1)
    (a d : Matrix (VV nd) (VV nd) K) (ha : (a - 1).rank ≤ 1) (hd : (d - 1).rank ≤ 1) :
    ((bd4 1 R3 R2 1 : Matrix (VV nd) (VV nd) K) = a * jm23 JB * d * jm45 (SpecTSUR.refl xF yF) →
      (1 - R2 * SpecTSUR.refl xC yC).rank + (1 - R2 * SpecTSUR.refl xF yF).rank ≤ 2) ∧
    ((bd4 1 R2 R3 1 : Matrix (VV nd) (VV nd) K) = a * jm23 (SpecTSUR.refl xC yC) * d * jm45 JE →
      (1 - R2 * SpecTSUR.refl xC yC).rank + (1 - R2 * SpecTSUR.refl xF yF).rank ≤ 2) ∧
    ((bd4 1 R3 R3 1 : Matrix (VV nd) (VV nd) K) = a * jm23 JB * d * jm45 JE →
      (1 - R2 * SpecTSUR.refl xC yC).rank + (1 - R2 * SpecTSUR.refl xF yF).rank ≤ 2) := by
  obtain ⟨eB, hB3, hC3, hB2, hdet23⟩ := Nfacts xC yC hC JB hBC
  obtain ⟨eE, hE3, hF3, hE2, hdet45⟩ := Nfacts xF yF hF JE hEF
  refine ⟨fun h => ?_, fun h => ?_, fun h => ?_⟩
  · have := unitfree_core _ a (jm23 JB) d (jm45 (SpecTSUR.refl xF yF)) h ha hd R3 R2 JB
      (SpecTSUR.refl xF yF) rfl (by rw [jm23_jm45])
    have h1 := rank_le_of_inv R3 JB R3_mul
    have h2' := rank_le_of_inv R2 (SpecTSUR.refl xF yF) R2_mul
    rw [hB3] at h1
    omega
  · have := unitfree_core _ a (jm23 (SpecTSUR.refl xC yC)) d (jm45 JE) h ha hd R2 R3
      (SpecTSUR.refl xC yC) JE rfl (by rw [jm23_jm45])
    have h1 := rank_le_of_inv R2 (SpecTSUR.refl xC yC) R2_mul
    have h2' := rank_le_of_inv R3 JE R3_mul
    rw [hE3] at h2'
    omega
  · have := unitfree_core _ a (jm23 JB) d (jm45 JE) h ha hd R3 R3 JB JE rfl (by rw [jm23_jm45])
    have h1 := rank_le_of_inv R3 JB R3_mul
    have h2' := rank_le_of_inv R3 JE R3_mul
    rw [hB3] at h1
    rw [hE3] at h2'
    omega

end Kill1

end SpecKills

#print axioms SpecKills.L3_U
#print axioms SpecKills.SYL_U
#print axioms SpecKills.Ureq_lower
#print axioms SpecKills.kill9_char
#print axioms SpecKills.kill9
#print axioms SpecKills.kill9_char_literal
#print axioms SpecKills.sl2_dual
#print axioms SpecKills.kill1
#print axioms SpecKills.unitfree_other
