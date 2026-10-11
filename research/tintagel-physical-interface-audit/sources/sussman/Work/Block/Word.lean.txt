import Work.Block.Split

/-!
# Block moves, part 4: the word language with block moves

(agent key: block-engine).

* `BMove α ρ`, `BWord α ρ`   words whose paid letters are BLOCKS: one role and `rk` linearly
                             independent directions;
* `BMove.flat`, `BWord.flat` the unit-move word of a block word (upstream `PWord`); the action
                             of a block word is BY DEFINITION upstream's `walk f w.flat`;
* `BMove.act`, `walk_flat_move`  the action of one block is `roleAct f l (blockMat z)`;
* `BWord.hist`               histogram of block ranks; `BWord.cost g` = sum over blocks of
                             `g (rank)`; `BWord.cost_eq_sum` relates the two;
* `BWord.Proper u`           every block has rank `1 ≤ rk < u` (needed by the program).
-/

set_option linter.unusedSectionVars false

namespace OAI
namespace PowerSaving.Binary
open Matrix Finset
noncomputable section

/-- Letters of a block word.  `localM` and `shift` are upstream's free moves; a `block` is
one role together with `rk` linearly independent directions. -/
inductive BMove (α ρ : Type*)
  | localM (g : Matrix ρ ρ ℚ)
  | shift (l : ρ) (z : Space α)
  | block (l : ρ) (rk : ℕ) (z : Fin rk → Space α) (ind : LinearIndependent F z)

abbrev BWord (α ρ : Type*) := List (BMove α ρ)

namespace BMove
variable {α ρ : Type*}

/-- The unit-move word of a letter: a block of rank `rk` is `rk` directional moves. -/
def flat : BMove α ρ → PWord α ρ
  | .localM g => [.localM g]
  | .shift l z => [.shift l z]
  | .block l _ z ind => List.ofFn (fun i => Move.dir l (z i) (ind.ne_zero i))

/-- Rank of a block; `none` for the free letters. -/
def rk? : BMove α ρ → Option ℕ
  | .block _ rk _ _ => some rk
  | _ => none

/-- Cost of a letter when a block of rank `rk` costs `g rk`. -/
def cost (g : ℕ → ℕ) (mv : BMove α ρ) : ℕ :=
  match mv.rk? with
  | some rk => g rk
  | none => 0

/-- A block the program can execute: `1 ≤ rk < u` (`u` = number of label coordinates). -/
def Proper (u : ℕ) : BMove α ρ → Prop
  | .block _ rk _ _ => 1 ≤ rk ∧ rk < u
  | _ => True

end BMove

namespace BWord
variable {α ρ : Type*}

def flat (w : BWord α ρ) : PWord α ρ := (w.map BMove.flat).flatten

@[simp] lemma flat_nil : flat ([] : BWord α ρ) = [] := rfl
@[simp] lemma flat_cons (mv : BMove α ρ) (w : BWord α ρ) :
    flat (mv :: w) = mv.flat ++ flat w := rfl
lemma flat_append (w w' : BWord α ρ) : flat (w ++ w') = flat w ++ flat w' := by
  simp [flat]

/-- Number of blocks of rank `r`. -/
def hist (w : BWord α ρ) (r : ℕ) : ℕ := w.countP (fun mv => decide (mv.rk? = some r))

@[simp] lemma hist_nil (r : ℕ) : hist ([] : BWord α ρ) r = 0 := rfl
lemma hist_cons (mv : BMove α ρ) (w : BWord α ρ) (r : ℕ) :
    hist (mv :: w) r = hist w r + if mv.rk? = some r then 1 else 0 := by
  unfold hist
  rw [List.countP_cons]
  simp
lemma hist_append (w w' : BWord α ρ) (r : ℕ) : hist (w ++ w') r = hist w r + hist w' r := by
  unfold hist; rw [List.countP_append]

/-- Total cost when a block of rank `rk` costs `g rk`. -/
def cost (g : ℕ → ℕ) (w : BWord α ρ) : ℕ := (w.map (BMove.cost g)).sum

@[simp] lemma cost_nil (g : ℕ → ℕ) : cost g ([] : BWord α ρ) = 0 := rfl
lemma cost_cons (g : ℕ → ℕ) (mv : BMove α ρ) (w : BWord α ρ) :
    cost g (mv :: w) = mv.cost g + cost g w := by simp [cost]
lemma cost_append (g : ℕ → ℕ) (w w' : BWord α ρ) :
    cost g (w ++ w') = cost g w + cost g w' := by simp [cost]

def Proper (u : ℕ) (w : BWord α ρ) : Prop := ∀ mv ∈ w, mv.Proper u

lemma Proper.tail {u : ℕ} {mv : BMove α ρ} {w : BWord α ρ} (h : Proper u (mv :: w)) :
    Proper u w := fun x hx => h x (List.mem_cons_of_mem _ hx)
lemma Proper.head {u : ℕ} {mv : BMove α ρ} {w : BWord α ρ} (h : Proper u (mv :: w)) :
    mv.Proper u := h mv List.mem_cons_self
lemma Proper.append {u : ℕ} {w w' : BWord α ρ} (h : Proper u w) (h' : Proper u w') :
    Proper u (w ++ w') := by
  intro mv hmv
  rcases List.mem_append.mp hmv with h1|h1
  · exact h mv h1
  · exact h' mv h1

/-- The cost of a proper word is determined by its histogram. -/
lemma cost_eq_sum (u : ℕ) (g : ℕ → ℕ) (w : BWord α ρ) (hw : Proper u w) :
    cost g w = ∑ r : Fin u, hist w r * g r := by
  induction w with
  | nil => simp
  | cons mv w ih =>
    rw [cost_cons, ih hw.tail]
    simp_rw [hist_cons, add_mul, Finset.sum_add_distrib]
    rw [Nat.add_comm]
    congr 1
    have hp := hw.head
    cases mv with
    | localM g' => simp [BMove.cost, BMove.rk?]
    | shift l z => simp [BMove.cost, BMove.rk?]
    | block l rk z ind =>
      obtain ⟨_, h2⟩ : 1 ≤ rk ∧ rk < u := hp
      simp only [BMove.cost, BMove.rk?, Option.some.injEq]
      rw [Finset.sum_eq_single (⟨rk,h2⟩ : Fin u)]
      · simp
      · intro b _ hb
        have : ¬ rk = b.val := fun h => hb (Fin.ext h.symm)
        simp [this]
      · intro h; exact absurd (Finset.mem_univ _) h

/-- A proper word has no block of rank `0`. -/
lemma hist_zero (u : ℕ) (w : BWord α ρ) (hw : Proper u w) : hist w 0 = 0 := by
  induction w with
  | nil => rfl
  | cons mv w ih =>
    rw [hist_cons, ih hw.tail]
    have hp := hw.head
    cases mv with
    | localM g' => simp [BMove.rk?]
    | shift l z => simp [BMove.rk?]
    | block l rk z ind =>
      obtain ⟨h1, _⟩ : 1 ≤ rk ∧ rk < u := hp
      have : ¬ rk = 0 := by omega
      simp [BMove.rk?, this]

/-- A proper word has no block of rank `≥ u`. -/
lemma hist_large (u : ℕ) (w : BWord α ρ) (hw : Proper u w) (r : ℕ) (hr : u ≤ r) :
    hist w r = 0 := by
  induction w with
  | nil => rfl
  | cons mv w ih =>
    rw [hist_cons, ih hw.tail]
    have hp := hw.head
    cases mv with
    | localM g' => simp [BMove.rk?]
    | shift l z => simp [BMove.rk?]
    | block l rk z ind =>
      obtain ⟨_, h2⟩ : 1 ≤ rk ∧ rk < u := hp
      have : ¬ rk = r := by omega
      simp [BMove.rk?, this]

end BWord

section
variable {α ρ : Type*} [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ]

lemma blockMat_wrap {rk : ℕ} (z : Fin rk → Space α) :
    blockMat z = wrap (fun x => ((List.ofFn z).map (fun y => tint (dot y x))).prod) := by
  unfold blockMat
  rw [← prod_dir_wrap, List.map_ofFn]
  rfl

lemma blockMat_comm_dir {rk : ℕ} (z : Fin rk → Space α) (y : Space α) :
    blockMat z * dir y = dir y * blockMat z := by
  rw [blockMat_wrap, dir_phase]; apply wrap_comm

lemma blockMat_succ {rk : ℕ} (z : Fin (rk+1) → Space α) :
    blockMat z = dir (z 0) * blockMat (fun i : Fin rk => z i.succ) := by
  unfold blockMat
  rw [List.ofFn_succ, List.prod_cons]

/-- The unit moves of a block, run one after the other, act as the block matrix. -/
lemma walk_ofFn_dir (f : ℕ) (l : ρ) {rk : ℕ} (z : Fin rk → Space α) (nz : ∀ i, z i ≠ 0)
    (x : Data α ρ f) :
    walk f (List.ofFn fun i => Move.dir l (z i) (nz i)) x = roleAct f l (blockMat z) x := by
  induction rk generalizing x with
  | zero =>
    rw [blockMat_zero]
    funext j; simp [walk, roleAct]
  | succ rk ih =>
    rw [List.ofFn_succ]
    change walk f (List.ofFn fun i : Fin rk => Move.dir l (z i.succ) (nz i.succ))
      (roleAct f l (dir (z 0)) x) = _
    rw [ih (fun i => z i.succ) (fun i => nz i.succ), roleAct_mul, blockMat_succ,
      blockMat_comm_dir]

/-- The action of one letter. -/
def BMove.act (f : ℕ) : BMove α ρ → Data α ρ f → Data α ρ f
  | .localM g => point f (actPoint g)
  | .shift l z => roleAct f l (Binary.shift z)
  | .block l _ z _ => roleAct f l (blockMat z)

lemma walk_flat_move (f : ℕ) (mv : BMove α ρ) (x : Data α ρ f) :
    walk f mv.flat x = mv.act f x := by
  cases mv with
  | localM g => rfl
  | shift l z => rfl
  | block l rk z ind => exact walk_ofFn_dir f l z (fun i => ind.ne_zero i) x

lemma walk_flat_cons (f : ℕ) (mv : BMove α ρ) (w : BWord α ρ) (x : Data α ρ f) :
    walk f (BWord.flat (mv :: w)) x = walk f w.flat (mv.act f x) := by
  rw [BWord.flat_cons, walk_append, walk_flat_move]

/-- The number of unit moves of a block word is its total rank. -/
lemma tally_flat (w : BWord α ρ) : tally w.flat = w.cost id := by
  induction w with
  | nil => rfl
  | cons mv w ih =>
    rw [BWord.flat_cons, tally_append, ih, BWord.cost_cons]
    congr 1
    cases mv with
    | localM g => rfl
    | shift l z => rfl
    | block l rk z ind =>
      simp [BMove.flat, BMove.cost, BMove.rk?, tally, toll, List.map_ofFn, Function.comp_def]

end
end
end PowerSaving.Binary
end OAI
