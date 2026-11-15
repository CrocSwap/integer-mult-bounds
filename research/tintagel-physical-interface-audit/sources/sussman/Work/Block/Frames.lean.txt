import Work.Block.Bridge

/-!
# Block moves, part 9: changing the frame of one role by a whole block

(agent key: block-engine).  Upstream changes a frame one line at a time
(`Path.change_one`, DirectionalWords.lean:132: one `dir` per line).  Here a role whose frame
changes by a set `d` of lines of its orthonormal basis `A` pays ONE block of rank `|d|`:

* `OBase.fam`, `OBase.fam_indep`     the lines of `d` as a legal block;
* `OBase.frame_union`, `OBase.deltas_eq`, `OBase.deltas_inv`
                                     `frame A (c ∪ d) = shift _ * blockMat (A.fam d) * frame A c`
                                     and the inverse step, also one block plus free shifts;
* `RoleStep φ l M N cst`             a block word on the single role `l` taking the matrix `M`
                                     to `N` at cost `cst` (`refl`, `trans`);
* `splitCost φ m q`                  cost of a residual of rank `q`: `0`, `φ q`, or
                                     `φ (m-1) + φ 1` when `q = m` (the `(m-1)+1` split);
* `OBase.up_step`, `OBase.down_step`, `OBase.reframe_step`
                                     one role from frame `s` to frame `t`: one down-block of rank
                                     `|s \ t|` and one up-block of rank `|t \ s|`.
-/

set_option linter.unusedSectionVars false

namespace OAI
namespace PowerSaving.Binary
open Matrix Finset Complex
noncomputable section

section
variable {α ρ : Type*} [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ]

lemma dot_sum_left {β : Type*} (s : Finset β) (g : β → Space α) (x : Space α) :
    dot (∑ j ∈ s, g j) x = ∑ j ∈ s, dot (g j) x := by
  rw [dot_symm, dot_sum]
  exact Finset.sum_congr rfl (fun j _ => dot_symm _ _)

/-- `0` if the unit vector `z` has phase `lum z = I`, `1` if `lum z = -I`. -/
def eps (z : Space α) : F := if lum z = I then 0 else 1

lemma lum_smul_unit (z : Space α) (hz : dot z z = 1) (b : F) :
    lum (b • z) = tint b * sign (b * eps z) := by
  rcases bit_cases b with rfl|rfl
  · simp [tint, sign]
  · rw [one_smul, one_mul]
    rcases lum_of_unit z hz with h|h
    · simp [eps, h, tint, sign]
    · have hne : ¬ ((-I : ℂ) = I) := by
        intro h'
        have h'' := congrArg Complex.im h'
        norm_num at h''
      simp [eps, h, tint, sign, hne]

namespace OBase
variable (A : OBase α)

/-- The lines `d` of the basis `A`, enumerated: the directions of one block. -/
def fam (d : Finset α) : Fin d.card → Space α := fun i => A.v (d.equivFin.symm i).1

lemma fam_orthonormal (d : Finset α) (i j : Fin d.card) :
    dot (A.fam d i) (A.fam d j) = if i = j then 1 else 0 := by
  unfold fam
  rw [A.rows]
  by_cases h : i = j
  · subst h; simp
  · have h' : ¬ (d.equivFin.symm i).1 = (d.equivFin.symm j).1 :=
      fun h' => h (d.equivFin.symm.injective (Subtype.ext h'))
    rw [if_neg h', if_neg h]

lemma fam_indep (d : Finset α) : LinearIndependent F (A.fam d) :=
  linearIndependent_of_orthonormal _ (A.fam_orthonormal d)

lemma blockMat_fam (d : Finset α) :
    blockMat (A.fam d) = wrap (fun x => ∏ i ∈ d, tint (dot (A.v i) x)) := by
  rw [blockMat_wrap]
  congr 1
  funext x
  rw [List.map_ofFn, List.prod_ofFn, ← Finset.prod_coe_sort d (fun i => tint (dot (A.v i) x))]
  exact Equiv.prod_comp d.equivFin.symm (fun j : {y // y ∈ d} => tint (dot (A.v j.1) x))

/-- Sum of the lines of `d` with negative phase: the free shift accompanying an up-block. -/
def corr (d : Finset α) : Space α := ∑ i ∈ d, eps (A.v i) • A.v i
/-- Sum of all lines of `d`: the extra free shift of a down-block. -/
def tot (d : Finset α) : Space α := ∑ i ∈ d, A.v i

/-- Product of the one-line frame changes (`delta`) of the lines in `d`. -/
def deltas (d : Finset α) : CMat α := wrap (fun x => ∏ i ∈ d, lum (dot (A.v i) x • A.v i))

/-- Adding the lines `d` to a frame multiplies it by `deltas d`. -/
lemma frame_union (c d : Finset α) (h : Disjoint c d) :
    frame A (c ∪ d) = A.deltas d * frame A c := by
  induction d using Finset.induction_on with
  | empty => simp [deltas, wrap_one]
  | insert i d hi ih =>
    have hic : i ∉ c := fun hc => (Finset.disjoint_left.mp h hc) (Finset.mem_insert_self i d)
    have hd : Disjoint c d := h.mono_right (Finset.subset_insert i d)
    have hu : c ∪ insert i d = insert i (c ∪ d) := Finset.union_insert i c d
    have hni : i ∉ c ∪ d := by
      rw [Finset.mem_union, not_or]; exact ⟨hic, hi⟩
    rw [hu, frame_ins A _ i hni, ih hd, ← mul_assoc]
    congr 1
    unfold deltas delta
    rw [wrap_mul]
    congr 1
    funext x
    rw [Finset.prod_insert hi]

/-- **The frame change by a set of lines is one block and a free shift.** -/
lemma deltas_eq (d : Finset α) : A.deltas d = shift (A.corr d) * blockMat (A.fam d) := by
  rw [A.blockMat_fam, shift_phase, wrap_mul]
  unfold deltas
  congr 1
  funext x
  have h1 : ∀ i ∈ d, lum (dot (A.v i) x • A.v i) =
      tint (dot (A.v i) x) * sign (dot (A.v i) x * eps (A.v i)) :=
    fun i _ => lum_smul_unit _ (A.self i) _
  have hcorr : dot (A.corr d) x = ∑ i ∈ d, dot (A.v i) x * eps (A.v i) := by
    unfold corr
    rw [dot_sum_left]
    apply Finset.sum_congr rfl
    intro i _
    rw [dot_smul_left, mul_comm]
  calc ∏ i ∈ d, lum (dot (A.v i) x • A.v i)
      = ∏ i ∈ d, (tint (dot (A.v i) x) * sign (dot (A.v i) x * eps (A.v i))) :=
        Finset.prod_congr rfl h1
    _ = (∏ i ∈ d, tint (dot (A.v i) x)) * sign (∑ i ∈ d, dot (A.v i) x * eps (A.v i)) := by
        rw [Finset.prod_mul_distrib, sign_sum]
    _ = sign (dot (A.corr d) x) * ∏ i ∈ d, tint (dot (A.v i) x) := by
        rw [hcorr, mul_comm]

/-- The inverse frame change is `deltas d` again, up to the free shift by `tot d`. -/
lemma deltas_inv (d : Finset α) : (shift (A.tot d) * A.deltas d) * A.deltas d = 1 := by
  unfold deltas
  rw [shift_phase, wrap_mul, wrap_mul, ← wrap_one]
  congr 1
  funext x
  have h2 : (∏ i ∈ d, lum (dot (A.v i) x • A.v i)) * (∏ i ∈ d, lum (dot (A.v i) x • A.v i))
      = sign (dot (A.tot d) x) := by
    rw [← Finset.prod_mul_distrib]
    have h3 : ∀ i ∈ d, lum (dot (A.v i) x • A.v i) * lum (dot (A.v i) x • A.v i) =
        sign (dot (A.v i) x) := by
      intro i _
      rw [lum_sq, dot_smul_left, dot_smul_right, A.self, mul_one]
      rcases bit_cases (dot (A.v i) x) with h|h <;> simp [h]
    rw [Finset.prod_congr rfl h3, ← sign_sum]
    congr 1
    unfold tot
    rw [dot_sum_left]
  rw [mul_assoc, h2, sign_sq]

end OBase

/-- A block word acting on the single role `l`, carrying the matrix `M` of that role to `N`,
with cost `cst` (`φ rk` per block of rank `rk`). -/
def RoleStep (φ : ℕ → ℝ) (l : ρ) (M N : CMat α) (cst : ℝ) : Prop :=
  ∃ (w : BWord α ρ) (U : CMat α), w.Proper (Fintype.card α) ∧ w.costR φ = cst ∧ U * M = N ∧
    ∀ (f : ℕ) (x : Data α ρ f), walk f w.flat x = roleAct f l U x

namespace RoleStep
variable {φ : ℕ → ℝ} {l : ρ} {M N K : CMat α} {c c' : ℝ}

theorem refl (φ : ℕ → ℝ) (l : ρ) (M : CMat α) : RoleStep φ l M M 0 := by
  refine ⟨[], 1, fun mv h => by simp at h, rfl, one_mul _, fun f x => ?_⟩
  funext j
  simp [walk, roleAct]

theorem trans (a : RoleStep φ l M N c) (b : RoleStep φ l N K c') :
    RoleStep φ l M K (c + c') := by
  obtain ⟨w, U, hw, hc, hU, hwalk⟩ := a
  obtain ⟨w', V, hw', hc', hV, hwalk'⟩ := b
  refine ⟨w ++ w', V * U, hw.append hw', by rw [BWord.costR_append, hc, hc'],
    by rw [mul_assoc, hU, hV], fun f x => ?_⟩
  rw [BWord.flat_append, walk_append, hwalk, hwalk', roleAct_mul]

end RoleStep

/-- Cost of a residual of rank `q` in a label space of `m` coordinates: nothing for `q = 0`,
one block for `0 < q < m`, the `(m-1)+1` split for `q = m`. -/
def splitCost (φ : ℕ → ℝ) (m q : ℕ) : ℝ :=
  if q = 0 then 0 else if q < m then φ q else φ (m-1) + φ 1

namespace OBase
variable (A : OBase α)

lemma up_small (φ : ℕ → ℝ) (l : ρ) (c d : Finset α) (h : Disjoint c d)
    (h1 : 1 ≤ d.card) (h2 : d.card < Fintype.card α) :
    RoleStep φ l (frame A c) (frame A (c ∪ d)) (φ d.card) := by
  refine ⟨[BMove.block l d.card (A.fam d) (A.fam_indep d), BMove.shift l (A.corr d)],
    shift (A.corr d) * blockMat (A.fam d), ?_, ?_, ?_, ?_⟩
  · intro mv hmv
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hmv
    rcases hmv with rfl|rfl
    · exact ⟨h1, h2⟩
    · trivial
  · simp [BWord.costR, BMove.costR, BMove.rk?]
  · rw [← A.deltas_eq, ← A.frame_union c d h]
  · intro f x
    rw [walk_flat_cons, walk_flat_cons]
    change roleAct f l (shift (A.corr d)) (roleAct f l (blockMat (A.fam d)) x) = _
    rw [roleAct_mul]

lemma down_small (φ : ℕ → ℝ) (l : ρ) (c d : Finset α) (h : Disjoint c d)
    (h1 : 1 ≤ d.card) (h2 : d.card < Fintype.card α) :
    RoleStep φ l (frame A (c ∪ d)) (frame A c) (φ d.card) := by
  refine ⟨[BMove.block l d.card (A.fam d) (A.fam_indep d), BMove.shift l (A.corr d),
      BMove.shift l (A.tot d)],
    shift (A.tot d) * (shift (A.corr d) * blockMat (A.fam d)), ?_, ?_, ?_, ?_⟩
  · intro mv hmv
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hmv
    rcases hmv with rfl|rfl|rfl
    · exact ⟨h1, h2⟩
    · trivial
    · trivial
  · simp [BWord.costR, BMove.costR, BMove.rk?]
  · rw [A.frame_union c d h, ← A.deltas_eq, ← mul_assoc, A.deltas_inv, one_mul]
  · intro f x
    rw [walk_flat_cons, walk_flat_cons, walk_flat_cons]
    change roleAct f l (shift (A.tot d)) (roleAct f l (shift (A.corr d))
      (roleAct f l (blockMat (A.fam d)) x)) = _
    rw [roleAct_mul, roleAct_mul, mul_assoc]

private lemma erase_union (c d : Finset α) (i : α) (hi : i ∈ d) :
    c ∪ d.erase i ∪ {i} = c ∪ d := by
  ext j
  simp only [Finset.mem_union, Finset.mem_erase, Finset.mem_singleton]
  constructor
  · rintro ((hj|⟨_, hj⟩)|rfl)
    · exact Or.inl hj
    · exact Or.inr hj
    · exact Or.inr hi
  · rintro (hj|hj)
    · exact Or.inl (Or.inl hj)
    · by_cases hji : j = i
      · exact Or.inr hji
      · exact Or.inl (Or.inr ⟨hji, hj⟩)

/-- One role moves UP by the lines `d`: one block of rank `|d|` (two blocks if `|d| = m`). -/
lemma up_step (φ : ℕ → ℝ) (hm : 2 ≤ Fintype.card α) (l : ρ) (c d : Finset α)
    (h : Disjoint c d) :
    RoleStep φ l (frame A c) (frame A (c ∪ d)) (splitCost φ (Fintype.card α) d.card) := by
  unfold splitCost
  by_cases h0 : d.card = 0
  · rw [if_pos h0]
    have hd : d = ∅ := Finset.card_eq_zero.mp h0
    subst hd
    rw [Finset.union_empty]
    exact RoleStep.refl φ l _
  · rw [if_neg h0]
    by_cases h2 : d.card < Fintype.card α
    · rw [if_pos h2]
      exact A.up_small φ l c d h (Nat.pos_of_ne_zero h0) h2
    · rw [if_neg h2]
      have hfull : d.card = Fintype.card α :=
        le_antisymm (Finset.card_le_univ d) (Nat.le_of_not_lt h2)
      obtain ⟨i, hi⟩ : d.Nonempty := Finset.card_pos.mp (Nat.pos_of_ne_zero h0)
      have hcard : (d.erase i).card = Fintype.card α - 1 := by
        rw [Finset.card_erase_of_mem hi, hfull]
      have hd1 : Disjoint c (d.erase i) := h.mono_right (Finset.erase_subset i d)
      have hd2 : Disjoint (c ∪ d.erase i) {i} := by
        rw [Finset.disjoint_singleton_right, Finset.mem_union, not_or]
        exact ⟨fun hc => Finset.disjoint_left.mp h hc hi, fun he => (Finset.mem_erase.mp he).1 rfl⟩
      have e1 := A.up_small φ l c (d.erase i) hd1 (by rw [hcard]; omega) (by rw [hcard]; omega)
      have e2 := A.up_small φ l (c ∪ d.erase i) {i} hd2 (by simp)
        (by rw [Finset.card_singleton]; omega)
      have e := e1.trans e2
      rw [erase_union c d i hi, hcard, Finset.card_singleton] at e
      exact e

/-- One role moves DOWN by the lines `d`: one block of rank `|d|` (two if `|d| = m`). -/
lemma down_step (φ : ℕ → ℝ) (hm : 2 ≤ Fintype.card α) (l : ρ) (c d : Finset α)
    (h : Disjoint c d) :
    RoleStep φ l (frame A (c ∪ d)) (frame A c) (splitCost φ (Fintype.card α) d.card) := by
  unfold splitCost
  by_cases h0 : d.card = 0
  · rw [if_pos h0]
    have hd : d = ∅ := Finset.card_eq_zero.mp h0
    subst hd
    rw [Finset.union_empty]
    exact RoleStep.refl φ l _
  · rw [if_neg h0]
    by_cases h2 : d.card < Fintype.card α
    · rw [if_pos h2]
      exact A.down_small φ l c d h (Nat.pos_of_ne_zero h0) h2
    · rw [if_neg h2]
      have hfull : d.card = Fintype.card α :=
        le_antisymm (Finset.card_le_univ d) (Nat.le_of_not_lt h2)
      obtain ⟨i, hi⟩ : d.Nonempty := Finset.card_pos.mp (Nat.pos_of_ne_zero h0)
      have hcard : (d.erase i).card = Fintype.card α - 1 := by
        rw [Finset.card_erase_of_mem hi, hfull]
      have hd1 : Disjoint c (d.erase i) := h.mono_right (Finset.erase_subset i d)
      have hd2 : Disjoint (c ∪ d.erase i) {i} := by
        rw [Finset.disjoint_singleton_right, Finset.mem_union, not_or]
        exact ⟨fun hc => Finset.disjoint_left.mp h hc hi, fun he => (Finset.mem_erase.mp he).1 rfl⟩
      have e1 := A.down_small φ l c (d.erase i) hd1 (by rw [hcard]; omega) (by rw [hcard]; omega)
      have e2 := A.down_small φ l (c ∪ d.erase i) {i} hd2 (by simp)
        (by rw [Finset.card_singleton]; omega)
      have e := e2.trans e1
      rw [erase_union c d i hi, hcard, Finset.card_singleton, add_comm] at e
      exact e

/-- **One role from frame `s` to frame `t`**: a down-block of rank `|s \ t|` and an up-block of
rank `|t \ s|` (upstream `Path.reframe` charges `|s \ t| + |t \ s|` unit moves for this role). -/
lemma reframe_step (φ : ℕ → ℝ) (hm : 2 ≤ Fintype.card α) (l : ρ) (s t : Finset α) :
    RoleStep φ l (frame A s) (frame A t)
      (splitCost φ (Fintype.card α) (s \ t).card + splitCost φ (Fintype.card α) (t \ s).card) := by
  have hs : (s ∩ t) ∪ (s \ t) = s := by
    ext j; simp only [Finset.mem_union, Finset.mem_inter, Finset.mem_sdiff]; tauto
  have ht : (s ∩ t) ∪ (t \ s) = t := by
    ext j; simp only [Finset.mem_union, Finset.mem_inter, Finset.mem_sdiff]; tauto
  have hd1 : Disjoint (s ∩ t) (s \ t) :=
    Finset.disjoint_left.mpr (fun j hj hj' => (Finset.mem_sdiff.mp hj').2 (Finset.mem_inter.mp hj).2)
  have hd2 : Disjoint (s ∩ t) (t \ s) :=
    Finset.disjoint_left.mpr (fun j hj hj' => (Finset.mem_sdiff.mp hj').2 (Finset.mem_inter.mp hj).1)
  have e1 := A.down_step φ hm l (s ∩ t) (s \ t) hd1
  have e2 := A.up_step φ hm l (s ∩ t) (t \ s) hd2
  rw [hs] at e1
  rw [ht] at e2
  exact e1.trans e2

end OBase

end
end
end PowerSaving.Binary
end OAI

#print axioms OAI.PowerSaving.Binary.OBase.deltas_eq
#print axioms OAI.PowerSaving.Binary.OBase.reframe_step
