/-
V2FloorKernelLemmas (lane LEAN-KERNEL, Nov 16): generic, data-free lemmas for the kernel-only FLAG-cover proof.
See V2FloorKernel.md.

* bit masks ↔ vectors of F₂⁹ (`vec`): injectivity on [0,512), surjectivity, xor = addition, parity checks (`chk`)
  decide membership in `Usub`, the span of two masks, every proper subspace lies in a hyperplane `Usub [h]`;
* dimensions from biorthogonal witnesses (`biorth`): `fdim (Lsub B) = |B|`, `fdim (Usub H) = 9 − |H|`;
* the COUNT LEMMA: at most `Mt b d = [9−b choose d−b]₂` subspaces of dimension d contain a b-dimensional Y
  (double counting pairs (U, v), v ∈ U \ Y, induction on d − b);
* the τ-bound: for any thresholds τ, the per-U weights of the pairs over an edge are bounded by
  Σ_U (W_U − τ_{dim U}) + Σ_d Mt b d · τ_d   (this is the Gaussian top-M rule of check.c / flagcheck.c).
-/
import Nov15.V2FloorBound
import Mathlib.LinearAlgebra.Basis.VectorSpace
import Mathlib.Combinatorics.Enumerative.DoubleCounting
import Mathlib.FieldTheory.Finiteness

namespace V2Floor
open Finset Module

/-! ### parity and masks -/

/-- parity of the low 9 bits of x (kernel-cheap: shifts and xors). -/
def par9 (x : ℕ) : ℕ :=
  let y := x ^^^ (x >>> 3) ^^^ (x >>> 6)
  (y ^^^ (y >>> 1) ^^^ (y >>> 2)) &&& 1

/-- all parity checks h ∈ H vanish on the mask v. -/
def chk (H : List ℕ) (v : ℕ) : Bool := H.all (fun h => par9 (h &&& v) == 0)

theorem sum_vec_eq_par9 : ∀ x < 512, (∑ j : Fin 9, vec x j) = ((par9 x : ℕ) : ZMod 2) := by
  simp only [Fin.sum_univ_succ, Fin.sum_univ_zero]
  decide +kernel

theorem par9_le_one (x : ℕ) : par9 x ≤ 1 := by
  unfold par9; exact Nat.and_le_right

theorem vec_mul_vec (h v : ℕ) (j : Fin 9) : vec h j * vec v j = vec (h &&& v) j := by
  unfold vec; rw [Nat.testBit_and]
  by_cases a : h.testBit j <;> by_cases b : v.testBit j <;> simp [a, b]

theorem vec_xor (a b : ℕ) : vec (a ^^^ b) = vec a + vec b := by
  funext j; unfold vec; simp only [Pi.add_apply, Nat.testBit_xor]
  by_cases x : a.testBit j <;> by_cases y : b.testBit j <;> simp [x, y] <;> decide

theorem vec_zero : vec 0 = 0 := by funext j; simp [vec]

/-- the F₂ inner product of two masks is their parity. -/
theorem dot_vec (h v : ℕ) (hv : v < 512) :
    (∑ j : Fin 9, vec h j * vec v j) = ((par9 (h &&& v) : ℕ) : ZMod 2) := by
  simp only [vec_mul_vec]
  exact sum_vec_eq_par9 _ (lt_of_le_of_lt Nat.and_le_right hv)

theorem natCast_par9_eq_zero (x : ℕ) : ((par9 x : ℕ) : ZMod 2) = 0 ↔ par9 x = 0 := by
  have := par9_le_one x
  interval_cases h : par9 x <;> decide

theorem testBit_of_ge {v i : ℕ} (hv : v < 512) (hi : 9 ≤ i) : v.testBit i = false :=
  Nat.testBit_lt_two_pow (lt_of_lt_of_le hv (by
    calc 512 = 2 ^ 9 := by norm_num
      _ ≤ 2 ^ i := Nat.pow_le_pow_right (by norm_num) hi))

theorem vec_inj {u v : ℕ} (hu : u < 512) (hv : v < 512) (h : vec u = vec v) : u = v := by
  apply Nat.eq_of_testBit_eq; intro i
  by_cases hi : i < 9
  · have := congrFun h ⟨i, hi⟩
    unfold vec at this
    by_cases a : u.testBit i <;> by_cases b : v.testBit i <;> simp_all
  · rw [testBit_of_ge hu (by omega), testBit_of_ge hv (by omega)]

theorem card_Vec : Fintype.card Vec = 512 := by simp [Vec, Fintype.card_fun, ZMod.card]

theorem vec_surj (x : Vec) : ∃ v < 512, vec v = x := by
  let f : Fin 512 → Vec := fun i => vec i.val
  have hinj : Function.Injective f := fun a b h => Fin.ext (vec_inj a.isLt b.isLt h)
  have hbij : Function.Bijective f := (Fintype.bijective_iff_injective_and_card f).mpr ⟨hinj, by simp [card_Vec]⟩
  obtain ⟨i, hi⟩ := hbij.2 x
  exact ⟨i.val, i.isLt, hi⟩

theorem vec_eq_zero {v : ℕ} (hv : v < 512) : vec v = 0 ↔ v = 0 := by
  constructor
  · intro h; exact vec_inj hv (by norm_num) (h.trans vec_zero.symm)
  · rintro rfl; exact vec_zero

/-- parity checks decide membership in `Usub`. -/
theorem mem_Usub_iff (H : List ℕ) {v : ℕ} (hv : v < 512) : vec v ∈ Usub H ↔ chk H v = true := by
  unfold Usub chk
  rw [LinearMap.mem_ker, Matrix.mulVecLin_apply, List.all_eq_true]
  constructor
  · intro h x hx
    obtain ⟨i, rfl⟩ := List.get_of_mem hx
    have := congrFun h i
    simp only [Matrix.mulVec, dotProduct, Matrix.of_apply, Pi.zero_apply] at this
    rw [dot_vec _ _ hv, natCast_par9_eq_zero] at this
    simpa using this
  · intro h; funext i
    simp only [Matrix.mulVec, dotProduct, Matrix.of_apply, Pi.zero_apply]
    rw [dot_vec _ _ hv, natCast_par9_eq_zero]
    have := h _ (List.get_mem H i)
    simpa using this

/-- membership in the span of two masks. -/
theorem mem_span_pair_iff {l w m : ℕ} (hl : l < 512) (hw : w < 512) (hm : m < 512) :
    vec m ∈ Submodule.span (ZMod 2) ({vec l, vec w} : Set Vec) ↔ (m = 0 ∨ m = l ∨ m = w ∨ m = l ^^^ w) := by
  have hx : l ^^^ w < 512 := Nat.xor_lt_two_pow (n := 9) hl hw
  rw [Submodule.mem_span_pair]
  constructor
  · rintro ⟨a, b, hab⟩
    have z2 : ∀ c : ZMod 2, c = 0 ∨ c = 1 := by decide
    rcases z2 a with rfl | rfl <;> rcases z2 b with rfl | rfl <;> simp only [zero_smul, one_smul, zero_add, add_zero] at hab
    · left; exact vec_inj hm (by norm_num) (by rw [← hab, vec_zero])
    · right; right; left; exact vec_inj hm hw hab.symm
    · right; left; exact vec_inj hm hl hab.symm
    · right; right; right; exact vec_inj hm hx (by rw [← hab, vec_xor])
  · rintro (rfl | rfl | rfl | rfl)
    · exact ⟨0, 0, by simp [vec_zero]⟩
    · exact ⟨1, 0, by simp⟩
    · exact ⟨0, 1, by simp⟩
    · exact ⟨1, 1, by simp [vec_xor]⟩

/-! ### hyperplanes -/

theorem exists_hyperplane (X : Sub) (hX : X ≠ ⊤) : ∃ h, 0 < h ∧ h < 512 ∧ X ≤ Usub [h] := by
  obtain ⟨f, hf0, hle⟩ := Submodule.exists_le_ker_of_lt_top X (lt_top_iff_ne_top.mpr hX)
  obtain ⟨h, hh, hvec⟩ := vec_surj (fun i => f (Pi.single i 1))
  have hfx : ∀ x : Vec, f x = ∑ j : Fin 9, vec h j * x j := by
    intro x; rw [LinearMap.pi_apply_eq_sum_univ f x, hvec]
    refine Finset.sum_congr rfl fun j _ => ?_
    simp only [smul_eq_mul, mul_comm]
    congr 2; funext i; simp [Pi.single_apply, eq_comm]
  refine ⟨h, ?_, hh, ?_⟩
  · rcases Nat.eq_zero_or_pos h with h0 | h0
    · exfalso; apply hf0; apply LinearMap.ext; intro x; rw [hfx]; simp [h0, vec_zero]
    · exact h0
  · intro x hx
    have hk : f x = 0 := hle hx
    unfold Usub
    rw [LinearMap.mem_ker, Matrix.mulVecLin_apply]
    funext i
    simp only [Matrix.mulVec, dotProduct, Matrix.of_apply, Pi.zero_apply]
    have : (([h] : List ℕ).get i) = h := by
      have hi : i.val = 0 := by have := i.isLt; simp only [List.length_singleton] at this; omega
      simp [List.get_eq_getElem, hi]
    rw [this, ← hfx, hk]

/-! ### dimensions from biorthogonal witnesses -/

/-- A and C are biorthogonal: |A| = |C| and par9(C_i ∧ A_j) = δ_ij. -/
def biorth (A C : List ℕ) : Bool :=
  (A.length == C.length) &&
  (List.range A.length).all (fun i => (List.range A.length).all (fun j =>
    par9 (C.getD i 0 &&& A.getD j 0) == if i == j then 1 else 0))

def allLt (A : List ℕ) : Bool := A.all (fun a => decide (a < 512))

theorem biorth_spec {A C : List ℕ} (h : biorth A C = true) :
    A.length = C.length ∧ ∀ i j, i < A.length → j < A.length →
      par9 (C.getD i 0 &&& A.getD j 0) = if i = j then 1 else 0 := by
  unfold biorth at h
  simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true, List.mem_range] at h
  refine ⟨h.1, fun i j hi hj => ?_⟩
  have := h.2 i hi j hj
  by_cases e : i = j <;> simp_all

theorem lin_indep_of_biorth {A C : List ℕ} (hA : allLt A = true) (h : biorth A C = true) :
    LinearIndependent (ZMod 2) (fun j : Fin A.length => vec (A.get j)) := by
  obtain ⟨hlen, hb⟩ := biorth_spec h
  have hA' : ∀ j : Fin A.length, A.get j < 512 := by
    intro j; unfold allLt at hA; rw [List.all_eq_true] at hA
    simpa using hA _ (List.get_mem A j)
  rw [linearIndependent_iff']
  intro s g hs i hi
  have key := congrArg (fun x : Vec => ∑ k : Fin 9, vec (C.getD i.val 0) k * x k) hs
  simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply, mul_zero, Finset.sum_const_zero, Finset.mul_sum] at key
  rw [Finset.sum_comm] at key
  have e : ∀ j : Fin A.length, (∑ k : Fin 9, vec (C.getD i.val 0) k * (g j * vec (A.get j) k)) =
      g j * (if i = j then 1 else 0) := by
    intro j
    have : (∑ k : Fin 9, vec (C.getD i.val 0) k * (g j * vec (A.get j) k)) =
        g j * ∑ k : Fin 9, vec (C.getD i.val 0) k * vec (A.get j) k := by
      rw [Finset.mul_sum]; refine Finset.sum_congr rfl fun k _ => by ring
    rw [this, dot_vec _ _ (hA' j)]
    have hb' := hb i.val j.val i.isLt j.isLt
    have hg : A.getD j.val 0 = A.get j := by rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem j.isLt]; rfl
    rw [hg] at hb'; rw [hb']
    by_cases e : i = j
    · subst e; simp
    · have : i.val ≠ j.val := fun h' => e (Fin.ext h'); simp [this, e]
  simp only [e, mul_ite, mul_one, mul_zero] at key
  rw [Finset.sum_ite_eq] at key
  simpa [hi] using key

theorem Lsub_eq_span (A : List ℕ) : Lsub A = Submodule.span (ZMod 2) (Set.range (fun j : Fin A.length => vec (A.get j))) := by
  unfold Lsub; congr 1; ext x
  simp only [Set.mem_setOf_eq, List.mem_map, Set.mem_range]
  constructor
  · rintro ⟨a, ha, rfl⟩; obtain ⟨j, rfl⟩ := List.get_of_mem ha; exact ⟨j, rfl⟩
  · rintro ⟨j, rfl⟩; exact ⟨_, List.get_mem A j, rfl⟩

theorem fdim_Lsub {A C : List ℕ} (hA : allLt A = true) (h : biorth A C = true) : fdim (Lsub A) = A.length := by
  unfold fdim; rw [Lsub_eq_span, finrank_span_eq_card (lin_indep_of_biorth hA h)]; simp

theorem fdim_Usub {H W : List ℕ} (hW : allLt W = true) (h : biorth W H = true) : fdim (Usub H) = 9 - H.length := by
  obtain ⟨hlen, hb⟩ := biorth_spec h
  have hW' : ∀ j, j < W.length → W.getD j 0 < 512 := by
    intro j hj; unfold allLt at hW; rw [List.all_eq_true] at hW
    rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj, Option.getD_some]; exact of_decide_eq_true (hW _ (List.getElem_mem hj))
  unfold fdim Usub
  set f := (Matrix.of fun (i : Fin H.length) j => vec (H.get i) j).mulVecLin
  have hsing : ∀ j : Fin H.length, f (vec (W.getD j.val 0)) = Pi.single j 1 := by
    intro j; funext i
    simp only [f, Matrix.mulVecLin_apply, Matrix.mulVec, dotProduct, Matrix.of_apply]
    rw [dot_vec _ _ (hW' j.val (by omega))]
    have := hb i.val j.val (by omega) (by omega)
    have hg : H.getD i.val 0 = H.get i := by rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem i.isLt]; rfl
    rw [hg] at this; rw [this]
    by_cases e : i = j
    · subst e; simp
    · have : i.val ≠ j.val := fun h' => e (Fin.ext h'); simp [this, Pi.single_apply, e]
  have hsurj : LinearMap.range f = ⊤ := by
    rw [LinearMap.range_eq_top]; intro y
    refine ⟨∑ j, y j • vec (W.getD j.val 0), ?_⟩
    rw [map_sum]; simp only [map_smul, hsing]
    funext i; simp [Finset.sum_apply, Pi.single_apply]
  have hrn := LinearMap.finrank_range_add_finrank_ker (K := ZMod 2) (V := Vec) f
  rw [hsurj] at hrn
  simp only [finrank_top, finrank_fin_fun] at hrn
  omega

/-! ### the count lemma -/

instance : Finite Sub := Finite.of_injective (fun U : Sub => (U : Set Vec)) SetLike.coe_injective
noncomputable instance : Fintype Sub := Fintype.ofFinite _

/-- Gaussian binomials [9−b choose d−b]₂, rows b = 0..9, columns d = 0..9. -/
def MT : List (List ℕ) :=
  [[1, 511, 43435, 788035, 3309747, 3309747, 788035, 43435, 511, 1],
   [0, 1, 255, 10795, 97155, 200787, 97155, 10795, 255, 1],
   [0, 0, 1, 127, 2667, 11811, 11811, 2667, 127, 1],
   [0, 0, 0, 1, 63, 651, 1395, 651, 63, 1],
   [0, 0, 0, 0, 1, 31, 155, 155, 31, 1],
   [0, 0, 0, 0, 0, 1, 15, 35, 15, 1],
   [0, 0, 0, 0, 0, 0, 1, 7, 7, 1],
   [0, 0, 0, 0, 0, 0, 0, 1, 3, 1],
   [0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
   [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]]

def Mt (b d : ℕ) : ℕ := (MT.getD b []).getD d 0

theorem Mt_diag : ∀ b < 10, Mt b b = 1 := by decide

/-- the q-Pascal step, as a strict inequality usable for an integer upper bound. -/
theorem Mt_step : ∀ b < 10, ∀ d < 10, b < d →
    (512 - 2 ^ b) * Mt (b + 1) d < (Mt b d + 1) * (2 ^ d - 2 ^ b) := by decide

attribute [local instance 10] Classical.propDecidable

theorem card_mem (U : Sub) : (univ.filter (fun v : Vec => v ∈ U)).card = 2 ^ fdim U := by
  have h := Module.card_eq_pow_finrank (K := ZMod 2) (V := U)
  rw [ZMod.card] at h
  unfold fdim
  rw [← h, Fintype.card_subtype]

theorem fdim_le_nine (U : Sub) : fdim U ≤ 9 := by
  have := Submodule.finrank_le U; simpa [fdim] using this

theorem fdim_sup_singleton {Y : Sub} {v : Vec} (hv : v ∉ Y) :
    fdim (Y ⊔ Submodule.span (ZMod 2) {v}) = fdim Y + 1 := by
  have hv0 : v ≠ 0 := fun h => hv (h ▸ Y.zero_mem)
  have hd : Disjoint Y (Submodule.span (ZMod 2) {v}) := (Submodule.disjoint_span_singleton' hv0).mpr hv
  have h := Submodule.finrank_sup_add_finrank_inf_eq Y (Submodule.span (ZMod 2) {v})
  rw [disjoint_iff.mp hd, finrank_bot, finrank_span_singleton hv0] at h
  unfold fdim; omega

theorem count_le (g : ℕ) : ∀ (Y : Sub) (d : ℕ), fdim Y + g = d →
    (univ.filter (fun U : Sub => Y ≤ U ∧ fdim U = d)).card ≤ Mt (fdim Y) d := by
  induction g with
  | zero =>
    intro Y d hd
    have hY := fdim_le_nine Y
    rw [← hd, add_zero, Mt_diag _ (by omega)]
    apply Finset.card_le_one.mpr
    intro U hU V hV
    simp only [mem_filter, mem_univ, true_and] at hU hV
    have e1 : Y = U := Submodule.eq_of_le_of_finrank_eq hU.1 (by unfold fdim at hU; omega)
    have e2 : Y = V := Submodule.eq_of_le_of_finrank_eq hV.1 (by unfold fdim at hV; omega)
    rw [← e1, ← e2]
  | succ g ih =>
    intro Y d hd
    set b := fdim Y with hb
    set A := univ.filter (fun U : Sub => Y ≤ U ∧ fdim U = d) with hA
    by_cases hd9 : d ≤ 9
    swap
    · -- no subspace of dim > 9
      have : A = ∅ := by
        apply Finset.filter_false_of_mem; intro U _ hU; have := fdim_le_nine U; omega
      rw [this]; simp
    set t := univ.filter (fun v : Vec => v ∉ Y) with ht
    have hcardY := card_mem Y
    have htc : t.card = 512 - 2 ^ b := by
      rw [ht, Finset.filter_not, Finset.card_sdiff_of_subset (Finset.filter_subset _ _), Finset.card_univ, card_Vec,
        hcardY]
    have hm : ∀ U ∈ A, 2 ^ d - 2 ^ b ≤ (t.bipartiteAbove (fun U v => v ∈ U) U).card := by
      intro U hU
      simp only [hA, mem_filter, mem_univ, true_and] at hU
      have hcU := card_mem U
      have hsub : univ.filter (fun v : Vec => v ∈ Y) ⊆ univ.filter (fun v : Vec => v ∈ U) := by
        intro v; simp only [mem_filter, mem_univ, true_and]; exact fun h => hU.1 h
      have e2 : t.bipartiteAbove (fun U v => v ∈ U) U = univ.filter (fun v : Vec => v ∈ U) \ univ.filter (fun v : Vec => v ∈ Y) := by
        ext v; simp only [Finset.bipartiteAbove, ht, mem_filter, mem_univ, true_and, mem_sdiff]; tauto
      rw [e2, Finset.card_sdiff_of_subset hsub, hcU, hcardY, hU.2]
    have hn : ∀ v ∈ t, (A.bipartiteBelow (fun U v => v ∈ U) v).card ≤ Mt (b + 1) d := by
      intro v hv
      simp only [ht, mem_filter, mem_univ, true_and] at hv
      have hY' := fdim_sup_singleton hv
      have := ih (Y ⊔ Submodule.span (ZMod 2) {v}) d (by rw [hY']; omega)
      rw [hY'] at this
      refine le_trans (Finset.card_le_card ?_) this
      intro U hU
      simp only [Finset.bipartiteBelow, hA, mem_filter, mem_univ, true_and] at hU ⊢
      exact ⟨sup_le hU.1.1 ((Submodule.span_singleton_le_iff_mem _ _).mpr hU.2), hU.1.2⟩
    have hdc := Finset.card_mul_le_card_mul (fun U v => v ∈ U) hm hn
    rw [htc] at hdc
    have hstep := Mt_step b (by omega) d (by omega) (by omega)
    by_contra hc
    push Not at hc
    have : (Mt b d + 1) * (2 ^ d - 2 ^ b) ≤ A.card * (2 ^ d - 2 ^ b) := Nat.mul_le_mul_right _ hc
    exact absurd (lt_of_le_of_lt (le_trans this hdc) hstep) (lt_irrefl _)

theorem count_le' (Y : Sub) (d : ℕ) :
    (univ.filter (fun U : Sub => Y ≤ U ∧ fdim U = d)).card ≤ Mt (fdim Y) d := by
  by_cases h : fdim Y ≤ d
  · exact count_le (d - fdim Y) Y d (by omega)
  · have : univ.filter (fun U : Sub => Y ≤ U ∧ fdim U = d) = ∅ := by
      apply Finset.filter_false_of_mem; intro U _ hU
      have := Submodule.finrank_mono hU.1; unfold fdim at h hU; omega
    rw [this]; simp

end V2Floor
