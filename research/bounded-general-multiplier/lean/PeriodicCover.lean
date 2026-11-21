import Mathlib.Logic.Equiv.Fin.Basic
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Fintype.Fin
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Sigma
import Mathlib.Algebra.BigOperators.Fin
import Mathlib.GroupTheory.Submonoid.Centralizer
import Mathlib.Basic.Complex.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.IntervalCases

namespace PeriodicCover

def axis (x z : ℕ) : ℕ := if z < 5 * x then z / 5 else z - 4 * x

theorem axis_eq_iff {x z i : ℕ} :
    axis x z = i ↔ (i < x ∧ 5 * i ≤ z ∧ z < 5 * i + 5) ∨
      (x ≤ i ∧ z = i + 4 * x) := by
  unfold axis
  split <;> omega

theorem axis_bound {x u z : ℕ} (hx : x ≤ u) (hz : z < u + 4 * x) :
    axis x z < u := by
  have h := (axis_eq_iff (x := x) (z := z) (i := axis x z)).mp rfl
  omega

theorem geometry {m h s : ℕ} (hm : 0 < m) (hs : s ≤ m)
    (lo : 4 * m ≤ 4 * h * s) (hi : 4 * h * s < 2 * (4 * m)) :
    let x := h * s - m
    4 * h * s = 4 * m + 4 * x ∧ x < m ∧ (5 ≤ 4 * h ∨ x = 0) := by
  dsimp
  rw [Nat.mul_assoc] at lo hi ⊢
  by_cases hh : h ≤ 1
  · interval_cases h <;> simp_all
    omega
  · omega

def degree (x i : ℕ) : ℕ := if i < x then 5 else 1

/-- Each coordinate below x has five literal tickets. All others have one. -/
def ticketFiber (u x : ℕ) (hx : x ≤ u) (i : Fin u) :
    Fin (degree x i.val) ≃ { z : Fin (u + 4 * x) // axis x z.val = i.val } where
  toFun j := by
    have hi := i.isLt
    by_cases h : i.val < x
    · have hj : j.val < 5 := calc
        j.val < degree x i.val := j.isLt
        _ = 5 := by simp [degree, h]
      exact ⟨⟨5 * i.val + j.val, by omega⟩, (axis_eq_iff (z := 5 * i.val + j.val)).mpr (Or.inl ⟨h, by omega, by omega⟩)⟩
    · exact ⟨⟨i.val + 4 * x, by omega⟩, (axis_eq_iff (z := i.val + 4 * x)).mpr (Or.inr ⟨by omega, rfl⟩)⟩
  invFun z := by
    have hz := axis_eq_iff.mp z.property
    by_cases h : i.val < x
    · exact ⟨z.val.val - 5 * i.val, by simp only [degree, ite_eq_left h]; omega⟩
    · exact ⟨0, by simp only [degree, ite_eq_right h]; omega⟩
  left_inv j := by
    apply Fin.ext
    by_cases h : i.val < x
    · simp [h]
    · have hj : j.val < 1 := calc
        j.val < degree x i.val := j.isLt
        _ = 1 := by simp [degree, h]
      simp [h]
      omega
  right_inv z := by
    apply Subtype.ext
    apply Fin.ext
    have hz := axis_eq_iff.mp z.property
    by_cases h : i.val < x <;> simp [h] <;> omega

theorem row_injective {k s x b : ℕ} (hk : 0 < k) (hfive : 5 ≤ k ∨ x = 0) :
    Function.Injective (fun j : Fin s => axis x (b + k * j.val)) := by
  intro j l heq
  have hj := (axis_eq_iff (x := x) (z := b + k * j.val)
    (i := axis x (b + k * j.val))).mp rfl
  have hl := (axis_eq_iff (x := x) (z := b + k * l.val)
    (i := axis x (b + k * j.val))).mp heq.symm
  apply Fin.ext
  by_contra hdiff
  rcases Nat.lt_or_gt_of_ne hdiff with h | h
  · have hgap := Nat.mul_le_mul_left k (Nat.succ_le_of_lt h)
    rw [Nat.mul_succ] at hgap
    omega
  · have hgap := Nat.mul_le_mul_left k (Nat.succ_le_of_lt h)
    rw [Nat.mul_succ] at hgap
    omega

/-- Every ticket has one row and one index within that row. -/
theorem ticket_rows {k s z : ℕ} (hk : 0 < k) (hz : z < k * s) :
    z % k < k ∧ z / k < s ∧ z % k + k * (z / k) = z := by
  exact ⟨Nat.mod_lt z hk, (Nat.div_lt_iff_lt_mul hk).mpr (by simpa [Nat.mul_comm] using hz),
    Nat.mod_add_div z k⟩

theorem row_unique {k r j : ℕ} (hr : r < k) :
    (r + k * j) % k = r ∧ (r + k * j) / k = j := by
  have hk : 0 < k := by omega
  simp [Nat.add_mul_mod_self_left, Nat.add_mul_div_left, Nat.mod_eq_of_lt hr,
    Nat.div_eq_of_lt hr, hk]

/-- A round repeats the old integral child batch z times and keeps b live lanes. -/
theorem batch_copies {m b : ℕ} (hm : 0 < m) (small : 15 * m ≤ b) (big : b < 30 * m) :
    ∃ z : ℕ, z ≤ 30 ∧ b ≤ z * m ∧ z * m < b + m ∧ 15 * (z * m) < 16 * b := by
  have ht := Nat.mod_add_div b m
  have hr := Nat.mod_lt b hm
  have hz : b / m * m = m * (b / m) := Nat.mul_comm _ _
  have hz1 : (b / m + 1) * m = m * (b / m) + m := by rw [Nat.add_mul, Nat.one_mul, hz]
  by_cases h : b % m = 0
  · refine ⟨b / m, ?_, ?_, ?_, ?_⟩
    · have hh : m * (b / m) < m * 30 := by omega
      exact Nat.le_of_lt (Nat.lt_of_mul_lt_mul_left hh)
    all_goals omega
  · refine ⟨b / m + 1, ?_, ?_, ?_, ?_⟩
    · have hh : m * (b / m) < m * 30 := by omega
      have := Nat.lt_of_mul_lt_mul_left hh
      omega
    all_goals omega

noncomputable def quarter (v : ℂ × ℂ) : ℂ × ℂ :=
  (((1 + Complex.I) * v.1 + (1 - Complex.I) * v.2) / 2,
   ((1 - Complex.I) * v.1 + (1 + Complex.I) * v.2) / 2)

theorem quarter_sq (v : ℂ × ℂ) : quarter (quarter v) = (v.2, v.1) := by
  apply Prod.ext <;> dsimp [quarter] <;> ring_nf <;>
    simp [Complex.I_sq] <;> ring

theorem quarter_four (v : ℂ × ℂ) : quarter (quarter (quarter (quarter v))) = v := by
  rw [quarter_sq, quarter_sq]

theorem degree_action {M : Type*} [Monoid M] {a : M} (h : a ^ 4 = 1) (x i : ℕ) :
    a ^ degree x i = a := by
  unfold degree
  split
  · rw [show (5 : ℕ) = 4 + 1 by decide, pow_succ, h, one_mul]
  · exact pow_one a

open scoped BigOperators

def coordinate {u : ℕ} (x : ℕ) (hx : x ≤ u) (z : Fin (u + 4 * x)) : Fin u :=
  ⟨axis x z.val, axis_bound hx z.isLt⟩

/-- Compose the actual ticket operations in the commutative coordinate action. -/
theorem ticket_product {M : Type*} [CommMonoid M] (u x : ℕ) (hx : x ≤ u)
    (a : Fin u → M) (ord : ∀ i, a i ^ 4 = 1) :
    ∏ z : Fin (u + 4 * x), a (coordinate x hx z) = ∏ i, a i := by
  classical
  rw [← Fintype.prod_fiberwise' (coordinate x hx) a]
  apply Finset.prod_congr rfl
  intro i _
  let e := (ticketFiber u x hx i).trans (Equiv.subtypeEquivRight fun z =>
    show axis x z.val = i.val ↔ coordinate x hx z = i from
      ⟨fun h => Fin.ext h, fun h => congrArg Fin.val h⟩)
  have hcard := Fintype.card_congr e
  rw [Fintype.card_fin] at hcard
  simpa only [Finset.prod_const, Finset.card_univ, ← hcard] using
    degree_action (ord i) x i.val

/-- The transposed enumeration converts the actual (round, slot) to a ticket. -/
def rowTicket {k s u x : ℕ} (size : s * k = u + 4 * x) :
    Fin k × Fin s ≃ Fin (u + 4 * x) :=
  ((Equiv.prodComm _ _).trans finProdFinEquiv).trans (finCongr size)

theorem rowTicket_formula {k s u x : ℕ} (size : s * k = u + 4 * x)
    (b : Fin k) (j : Fin s) :
    (rowTicket size (b, j)).val = b.val + k * j.val := rfl

def ordered {M : Type*} [Monoid M] {k s u x : ℕ}
    (size : s * k = u + 4 * x) (hx : x ≤ u) (a : Fin u → M) : M :=
  (List.ofFn fun b : Fin k =>
    (List.ofFn fun j : Fin s => a (coordinate x hx (rowTicket size (b, j)))).prod).prod

theorem ordered_prod {M : Type*} [CommMonoid M] {k s u x : ℕ}
    (size : s * k = u + 4 * x) (hx : x ≤ u) (a : Fin u → M)
    (ord : ∀ i, a i ^ 4 = 1) : ordered size hx a = (List.ofFn a).prod := by
  simp only [ordered, Fin.prod_ofFn]
  rw [← Fintype.prod_prod_type (fun z : Fin k × Fin s => a (coordinate x hx (rowTicket size z)))]
  exact (Fintype.prod_equiv (rowTicket size) _ _ (fun _ => rfl)).trans
    (ticket_product u x hx a ord)

open scoped IsMulCommutative in
theorem ordered_actions {M : Type*} [Monoid M] {k s u x : ℕ}
    (size : s * k = u + 4 * x) (hx : x ≤ u) (a : Fin u → M)
    (comm : ∀ i j, Commute (a i) (a j)) (ord : ∀ i, a i ^ 4 = 1) :
    ordered size hx a = (List.ofFn a).prod := by
  classical
  let S := Submonoid.closure (Set.range a)
  have hr : (Set.range a).Pairwise Commute := by
    intro y hy z hz _
    obtain ⟨i, rfl⟩ := hy
    obtain ⟨j, rfl⟩ := hz
    exact comm i j
  let _ : IsMulCommutative S := Submonoid.isMulCommutative_closure _ hr
  let g (i : Fin u) : S := ⟨a i, Submonoid.subset_closure ⟨i, rfl⟩⟩
  have h := ordered_prod size hx g fun i => Subtype.ext (ord i)
  have hlist (l : List S) : (l.prod : M) = (l.map Subtype.val).prod := by
    induction l with
    | nil => rfl
    | cons y ys ih =>
      change (y : M) * (ys.prod : M) = (y : M) * (ys.map Subtype.val).prod
      rw [ih]
  have hcoe {m : ℕ} (f : Fin m → S) :
      (((List.ofFn f).prod : S) : M) = (List.ofFn fun i => (f i : M)).prod := by
    simpa only [List.map_ofFn, Function.comp_def] using hlist (List.ofFn f)
  have he := congrArg Subtype.val h
  simpa only [ordered, hcoe] using he

#print axioms geometry
#print axioms batch_copies
#print axioms ticketFiber
#print axioms row_injective
#print axioms ticket_rows
#print axioms row_unique
#print axioms quarter_four
#print axioms degree_action
#print axioms ticket_product
#print axioms ordered_actions
end PeriodicCover
