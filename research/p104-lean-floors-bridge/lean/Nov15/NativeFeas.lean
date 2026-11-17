/-
NativeFeas (lane LEAN-NEXT15, Nov 16): the native #7623 is feasible for the FloorCert support sub-LP.
The native's x (Nov15/NativeFeasData.lean, from Nov15/floorcert/export_native.py, which applies
rsnative.py's map: y_c = hd(c), z/a = native first hops, fresh minimal heads for hops into non-Nat
charts) satisfies x ≥ 0 and A·x ≥ b on all 892 kept rows, with cᵀx = 1,964 ≤ 3,432 paid stops.
So "floor ≤ native" (780 ≤ 1,964) holds inside Lean: the certificate is consistent with the frontier word.

Integer checks: NativeFeasCheck.lean (kernel `decide +kernel`). This file is the field-level bridge.
Build (one at a time, after the FloorCert oleans):
  lake env lean -o .lake/build/lib/lean/Nov15/NativeFeasData.olean Nov15/NativeFeasData.lean   (10 s, 0.9 GB)
  lake env lean -o .lake/build/lib/lean/Nov15/NativeFeasCheck.olean Nov15/NativeFeasCheck.lean (41 s)
  lake env lean -o .lake/build/lib/lean/Nov15/NativeFeas.olean Nov15/NativeFeas.lean
-/
import Nov15.NativeFeasCheck
import Nov15.FloorCert

open Finset

set_option linter.unusedSectionVars false

namespace FloorCert

/-! ## Tree and accumulator semantics -/

@[simp] lemma get_leaf (j : Nat) : ITree.leaf.get j = 0 := by simp [ITree.get]

lemma get_node (l : ITree) (v : Int) (r : ITree) (j : Nat) :
    (ITree.node l v r).get j = if j = 0 then v else if j % 2 = 1 then l.get (j / 2) else r.get (j / 2 - 1) := by
  simp [ITree.get]

/-- `upd fuel t i d` adds d at index i, when i < fuel. -/
theorem get_upd (fuel : Nat) : ∀ (t : ITree) (i j : Nat) (d : Int), i < fuel →
    (ITree.upd fuel t i d).get j = t.get j + if j = i then d else 0 := by
  induction fuel with
  | zero => intro t i j d h; omega
  | succ n ih =>
    intro t i j d hi
    -- the shared index facts
    have hodd : i ≠ 0 → i % 2 = 1 → (i / 2 < n ∧ (j % 2 = 1 → (j / 2 = i / 2 ↔ j = i))) := by
      intro h0 h1; refine ⟨by omega, fun hj => ⟨fun h => by omega, fun h => by omega⟩⟩
    have hev : i ≠ 0 → i % 2 ≠ 1 → (i / 2 - 1 < n ∧ (j ≠ 0 → j % 2 ≠ 1 → (j / 2 - 1 = i / 2 - 1 ↔ j = i))) := by
      intro h0 h1; refine ⟨by omega, fun hj0 hj => ⟨fun h => by omega, fun h => by omega⟩⟩
    cases t with
    | leaf =>
      simp only [ITree.upd]
      by_cases h0 : i = 0
      · subst h0; rw [if_pos rfl, get_node]; split_ifs <;> simp_all
      · rw [if_neg h0]
        by_cases h1 : i % 2 = 1
        · rw [if_pos h1, get_node]
          obtain ⟨hlt, hiff⟩ := hodd h0 h1
          by_cases hj0 : j = 0
          · subst hj0; simp [Ne.symm h0]
          by_cases hj1 : j % 2 = 1
          · rw [if_neg hj0, if_pos hj1, ih _ _ _ _ hlt]
            simp [(hiff hj1)]
          · have : j ≠ i := by omega
            simp [hj0, hj1, this]
        · rw [if_neg h1, get_node]
          obtain ⟨hlt, hiff⟩ := hev h0 h1
          by_cases hj0 : j = 0
          · subst hj0; simp [Ne.symm h0]
          by_cases hj1 : j % 2 = 1
          · have : j ≠ i := by omega
            simp [hj0, hj1, this]
          · rw [if_neg hj0, if_neg hj1, ih _ _ _ _ hlt]
            simp [(hiff hj0 hj1)]
    | node l v r =>
      simp only [ITree.upd]
      by_cases h0 : i = 0
      · subst h0; rw [if_pos rfl, get_node, get_node]; split_ifs <;> simp_all
      · rw [if_neg h0]
        by_cases h1 : i % 2 = 1
        · rw [if_pos h1, get_node, get_node]
          obtain ⟨hlt, hiff⟩ := hodd h0 h1
          by_cases hj0 : j = 0
          · subst hj0; simp [Ne.symm h0]
          by_cases hj1 : j % 2 = 1
          · rw [if_neg hj0, if_pos hj1, if_neg hj0, if_pos hj1, ih _ _ _ _ hlt]
            simp [(hiff hj1)]
          · have : j ≠ i := by omega
            simp [hj0, hj1, this]
        · rw [if_neg h1, get_node, get_node]
          obtain ⟨hlt, hiff⟩ := hev h0 h1
          by_cases hj0 : j = 0
          · subst hj0; simp [Ne.symm h0]
          by_cases hj1 : j % 2 = 1
          · have : j ≠ i := by omega
            simp [hj0, hj1, this]
          · rw [if_neg hj0, if_neg hj1, if_neg hj0, if_neg hj1, ih _ _ _ _ hlt]
            simp [(hiff hj0 hj1)]

/-- the entries of a sparse column in row j -/
def entAt (j : Nat) (l : List (Nat × Int)) : Int := (l.map fun p => if p.1 = j then p.2 else 0).sum

theorem get_addEnts (x : Int) : ∀ (l : List (Nat × Int)) (t : ITree) (j : Nat),
    (addEnts x t l).get j = t.get j + x * entAt j l := by
  intro l
  induction l with
  | nil => intro t j; simp [addEnts, entAt]
  | cons p l ih =>
    intro t j
    rw [addEnts, ih, get_upd _ _ _ _ _ (Nat.lt_succ_self _)]
    simp only [entAt, List.map_cons, List.sum_cons]
    by_cases h : j = p.1
    · subst h; simp; ring
    · have : p.1 ≠ j := fun e => h e.symm
      simp [h, this]

theorem get_accum : ∀ (cs : List (Int × List (Nat × Int))) (xs : List Int) (t : ITree) (j : Nat),
    (accum t cs xs).get j = t.get j + ((cs.zip xs).map fun p => p.2 * entAt j p.1.2).sum := by
  intro cs
  induction cs with
  | nil => intro xs t j; cases xs <;> simp [accum]
  | cons c cs ih =>
    intro xs t j
    cases xs with
    | nil => simp [accum]
    | cons x xs =>
      rw [accum, ih]
      simp only [List.zip_cons_cons, List.map_cons, List.sum_cons]
      split_ifs with hx
      · subst hx; simp
      · rw [get_addEnts]; ring

theorem get_costAcc : ∀ (cs : List (Int × List (Nat × Int))) (xs : List Int) (t : ITree),
    (costAcc t cs xs).get 0 = t.get 0 + ((cs.zip xs).map fun p => p.1.1 * p.2).sum := by
  intro cs
  induction cs with
  | nil => intro xs t; cases xs <;> simp [costAcc]
  | cons c cs ih =>
    intro xs t
    cases xs with
    | nil => simp [costAcc]
    | cons x xs =>
      rw [costAcc, ih]
      simp only [List.zip_cons_cons, List.map_cons, List.sum_cons]
      split_ifs with hx
      · subst hx; simp
      · rw [get_upd _ _ _ _ _ Nat.one_pos]; simp; ring

theorem rowsGe_spec : ∀ (bs : List Int) (t : ITree) (i0 : Nat), rowsGe t bs i0 = true →
    ∀ k < bs.length, bs.getD k 0 ≤ t.get (i0 + k) := by
  intro bs
  induction bs with
  | nil => intro t i0 _ k hk; simp at hk
  | cons b bs ih =>
    intro t i0 h k hk
    simp only [rowsGe, Bool.and_eq_true, decide_eq_true_eq] at h
    cases k with
    | zero => simpa using h.1
    | succ k =>
      have := ih t (i0 + 1) h.2 k (by simpa using hk)
      simpa [Nat.add_assoc, Nat.add_comm 1 k] using this

/-! ## From list sums to Fin sums -/

section Field
variable {𝕜 : Type*} [Field 𝕜] [LinearOrder 𝕜] [IsStrictOrderedRing 𝕜]

lemma sum_fin_zip {α : Type*} (F : α → Int → 𝕜) (d : α) : ∀ (cs : List α) (xs : List Int) (n : Nat),
    cs.length = n → xs.length = n →
    ∑ j : Fin n, F (cs.getD j d) (xs.getD j 0) = ((cs.zip xs).map fun p => F p.1 p.2).sum := by
  intro cs
  induction cs with
  | nil => intro xs n h1 _; subst h1; simp
  | cons c cs ih =>
    intro xs n h1 h2
    cases xs with
    | nil => simp at h1 h2; omega
    | cons x xs =>
      obtain ⟨m, rfl⟩ : ∃ m, n = m + 1 := ⟨cs.length, by simp at h1; omega⟩
      simp only [List.length_cons, Nat.add_right_cancel_iff] at h1 h2
      rw [Fin.sum_univ_succ]
      simp only [Fin.val_zero, List.getD_cons_zero, Fin.val_succ, List.getD_cons_succ,
        List.zip_cons_cons, List.map_cons, List.sum_cons]
      rw [ih xs m h1 h2]

lemma cast_list_sum {β : Type*} (l : List β) (f : β → Int) :
    (((l.map f).sum : Int) : 𝕜) = (l.map fun a => (f a : 𝕜)).sum := by
  induction l with
  | nil => simp
  | cons a l ih => simp [ih]

/-- the native's point, as a vector over the support columns -/
def xN (j : Fin nCols) : 𝕜 := (xList.getD j 0 : 𝕜)

theorem native_nonneg (j : Fin nCols) : 0 ≤ (xN j : 𝕜) := by
  have hj : (j : Nat) < xList.length := by rw [xlen_ok]; exact j.2
  have hmem : xList.getD j 0 ∈ xList := by
    simp only [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hj, Option.getD_some]
    exact List.getElem_mem hj
  have := List.all_eq_true.1 x_nonneg_ok _ hmem
  simp only [decide_eq_true_eq] at this
  unfold xN; exact_mod_cast this

/-- generic: Σ_j (column j's entries in row i) · x_j is the accumulator's value at i. -/
theorem gen_Ax (cs : List (Int × List (Nat × Int))) (xs : List Int) (n : Nat) (hc : cs.length = n)
    (hx : xs.length = n) (i : Nat) :
    ∑ j : Fin n, ((cs.getD j (0, [])).2.map fun p => if p.1 = i then (p.2 : 𝕜) else 0).sum * (xs.getD j 0 : 𝕜)
      = (((accum .leaf cs xs).get i : Int) : 𝕜) := by
  have h := sum_fin_zip (𝕜 := 𝕜) (fun c x => ((entAt i c.2 : Int) : 𝕜) * (x : 𝕜)) ((0 : Int), []) cs xs n hc hx
  have hE : ∀ l : List (Nat × Int), (l.map fun p => if p.1 = i then (p.2 : 𝕜) else 0).sum = ((entAt i l : Int) : 𝕜) := by
    intro l; rw [entAt, cast_list_sum]; congr 1; apply List.map_congr_left; intro p _; split_ifs <;> simp
  simp only [hE]
  rw [h, get_accum, get_leaf, zero_add, cast_list_sum]
  congr 1; apply List.map_congr_left; intro p _; push_cast; ring

/-- generic: Σ_j c_j x_j is the cost accumulator's value. -/
theorem gen_obj (cs : List (Int × List (Nat × Int))) (xs : List Int) (n : Nat) (hc : cs.length = n)
    (hx : xs.length = n) :
    ∑ j : Fin n, ((cs.getD j (0, [])).1 : 𝕜) * (xs.getD j 0 : 𝕜) = (((costAcc .leaf cs xs).get 0 : Int) : 𝕜) := by
  have h := sum_fin_zip (𝕜 := 𝕜) (fun c x => (c.1 : 𝕜) * (x : 𝕜)) ((0 : Int), []) cs xs n hc hx
  rw [h, get_costAcc, get_leaf, zero_add, cast_list_sum]
  congr 1; apply List.map_congr_left; intro p _; push_cast; ring

theorem Ax_eq (i : Fin nRows) :
    ∑ j, A i j * (xN j : 𝕜) = ((nativeAx.get i : Int) : 𝕜) :=
  gen_Ax colList xList nCols len_ok.1 xlen_ok i

/-- **Native feasibility**: the native's x meets every kept row. -/
theorem native_feasible (i : Fin nRows) : b i ≤ ∑ j, A i j * (xN j : 𝕜) := by
  rw [Ax_eq]
  have hk : (i : Nat) < bList.length := by rw [len_ok.2]; exact i.2
  have := rowsGe_spec bList nativeAx 0 rows_ok i hk
  rw [zero_add] at this
  unfold b; exact_mod_cast this

/-- **Native objective**: cᵀx = 1,964 (the kept columns of the full-LP value 1,999). -/
theorem native_obj : ∑ j, c j * (xN j : 𝕜) = 1964 := by
  have h : ∑ j, c j * (xN j : 𝕜) = (((costAcc .leaf colList xList).get 0 : Int) : 𝕜) :=
    gen_obj colList xList nCols len_ok.1 xlen_ok
  rw [h, obj_ok]; norm_num [nativeObj]

/-- **Floor ≤ native**, inside Lean: the certificate's bound (780) applied to the native's own point,
whose objective is 1,964 ≤ 3,432 paid stops. -/
theorem floor_le_native : (780 : 𝕜) ≤ ∑ j, c j * (xN j : 𝕜) ∧ ∑ j, c j * (xN j : 𝕜) ≤ 3432 := by
  refine ⟨lp_floor _ native_nonneg native_feasible, ?_⟩
  rw [native_obj]; norm_num

end Field

end FloorCert

#print axioms FloorCert.native_nonneg
#print axioms FloorCert.native_feasible
#print axioms FloorCert.native_obj
#print axioms FloorCert.floor_le_native
