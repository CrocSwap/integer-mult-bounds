import Work.Block.Bridge

/-!
# GFrame engine, part 1: the generalised word language (agent key: eng-ram)

Letters = the letters of `BWord` (`localM`, `shift`, `block`) plus TWO FREE ADAPTER letters on
one role:

* `perm l G`      address permutation by an additive bijection `G` of the label space
                  (matrix `permMat G`, `(permMat G) x y = 1` iff `G.π x = y`);
* `phase l z c`   the diagonal phase `i^[z·x + c]` IN THE STANDARD BASIS
                  (matrix `phaseMat z c = diagonal (fun x => tint (dot z x + c))`).

Products of `phaseMat` are exactly the diagonal matrices `i^Q(x)`, `Q` a `ℤ/4`-valued quadratic
form plus a constant; with the old free letter `shift` the free letters generate every affine
address permutation times such a phase.  A "twisted block" is NOT a primitive letter: it is the
word `free adapters ++ [block] ++ free adapters` (see `Free.lean`, `gstep_of_factor`).

The semantics is `gwalk` (no unit-move word behind it: the new letters are not Walsh-diagonal).
Old words embed by `GWord.ofB`, and `gwalk f (ofB w) = walk f w.flat`.
-/

set_option linter.unusedSectionVars false

namespace OAI
namespace PowerSaving.GF
open Binary Matrix Finset
noncomputable section

/-- An additive bijection of the label space. -/
structure APerm (α : Type*) where
  π : Space α ≃ Space α
  add : ∀ x y, π (x + y) = π x + π y

section Mats
variable {α : Type*} [Fintype α] [DecidableEq α]

/-- Permutation matrix of an additive bijection: `(permMat G *ᵥ v) x = v (G.π x)`. -/
def permMat (G : APerm α) : CMat α := fun x y => if G.π x = y then 1 else 0

/-- Elementary diagonal phase in the standard basis: `i^[z·x + c]`. -/
def phaseMat (z : Space α) (c : F) : CMat α := Matrix.diagonal fun x => tint (dot z x + c)

end Mats

/-- Letters of the generalised word language. -/
inductive GMove (α ρ : Type*)
  | old (mv : BMove α ρ)
  | perm (l : ρ) (G : APerm α)
  | phase (l : ρ) (z : Space α) (c : F)

abbrev GWord (α ρ : Type*) := List (GMove α ρ)

namespace GMove
variable {α ρ : Type*}

/-- The letter of `BWord` with the same price (free adapters ↦ a free letter). -/
def shadow : GMove α ρ → BMove α ρ
  | .old mv => mv
  | .perm _ _ => .localM 0
  | .phase _ _ _ => .localM 0

/-- Rank paid by a letter (`none` = free). -/
def rk? (mv : GMove α ρ) : Option ℕ := mv.shadow.rk?
def costR (φ : ℕ → ℝ) (mv : GMove α ρ) : ℝ := mv.shadow.costR φ
def Proper (u : ℕ) (mv : GMove α ρ) : Prop := mv.shadow.Proper u

@[simp] lemma costR_perm (φ : ℕ → ℝ) (l : ρ) (G : APerm α) :
    (GMove.perm l G : GMove α ρ).costR φ = 0 := rfl
@[simp] lemma costR_phase (φ : ℕ → ℝ) (l : ρ) (z : Space α) (c : F) :
    (GMove.phase l z c : GMove α ρ).costR φ = 0 := rfl
@[simp] lemma costR_old (φ : ℕ → ℝ) (mv : BMove α ρ) : (GMove.old mv).costR φ = mv.costR φ := rfl
lemma proper_perm (u : ℕ) (l : ρ) (G : APerm α) : (GMove.perm l G : GMove α ρ).Proper u :=
  trivial
lemma proper_phase (u : ℕ) (l : ρ) (z : Space α) (c : F) :
    (GMove.phase l z c : GMove α ρ).Proper u := trivial
@[simp] lemma proper_old (u : ℕ) (mv : BMove α ρ) : (GMove.old mv).Proper u ↔ mv.Proper u :=
  Iff.rfl

end GMove

namespace GWord
variable {α ρ : Type*}

def shadow (w : GWord α ρ) : BWord α ρ := w.map GMove.shadow
def costR (φ : ℕ → ℝ) (w : GWord α ρ) : ℝ := (w.map (GMove.costR φ)).sum
def Proper (u : ℕ) (w : GWord α ρ) : Prop := ∀ mv ∈ w, mv.Proper u
def hist (w : GWord α ρ) (r : ℕ) : ℕ := w.shadow.hist r
/-- Natural-number cost when a block of rank `rk` costs `g rk`. -/
def cost (g : ℕ → ℕ) (w : GWord α ρ) : ℕ := w.shadow.cost g
/-- An old block word as a generalised word. -/
def ofB (w : BWord α ρ) : GWord α ρ := w.map GMove.old

@[simp] lemma shadow_nil : shadow ([] : GWord α ρ) = [] := rfl
@[simp] lemma shadow_cons (mv : GMove α ρ) (w : GWord α ρ) :
    shadow (mv :: w) = mv.shadow :: shadow w := rfl
@[simp] lemma shadow_ofB (w : BWord α ρ) : shadow (ofB w) = w := by
  simp [shadow, ofB, List.map_map, Function.comp_def, GMove.shadow]

lemma costR_shadow (φ : ℕ → ℝ) (w : GWord α ρ) : costR φ w = BWord.costR φ w.shadow := by
  unfold costR BWord.costR shadow
  rw [List.map_map]
  rfl
@[simp] lemma costR_nil (φ : ℕ → ℝ) : costR φ ([] : GWord α ρ) = 0 := rfl
lemma costR_cons (φ : ℕ → ℝ) (mv : GMove α ρ) (w : GWord α ρ) :
    costR φ (mv :: w) = mv.costR φ + costR φ w := by simp [costR]
lemma costR_append (φ : ℕ → ℝ) (w w' : GWord α ρ) :
    costR φ (w ++ w') = costR φ w + costR φ w' := by simp [costR]
lemma costR_ofB (φ : ℕ → ℝ) (w : BWord α ρ) : costR φ (ofB w) = BWord.costR φ w := by
  rw [costR_shadow, shadow_ofB]
@[simp] lemma cost_nil (g : ℕ → ℕ) : cost g ([] : GWord α ρ) = 0 := rfl
lemma cost_cons (g : ℕ → ℕ) (mv : GMove α ρ) (w : GWord α ρ) :
    cost g (mv :: w) = mv.shadow.cost g + cost g w := BWord.cost_cons g _ _

lemma Proper.shadow {u : ℕ} {w : GWord α ρ} (h : Proper u w) : BWord.Proper u w.shadow := by
  intro mv hmv
  obtain ⟨g, hg, rfl⟩ := List.mem_map.mp hmv
  exact h g hg
lemma Proper.tail {u : ℕ} {mv : GMove α ρ} {w : GWord α ρ} (h : Proper u (mv :: w)) :
    Proper u w := fun x hx => h x (List.mem_cons_of_mem _ hx)
lemma Proper.head {u : ℕ} {mv : GMove α ρ} {w : GWord α ρ} (h : Proper u (mv :: w)) :
    mv.Proper u := h mv List.mem_cons_self
lemma Proper.append {u : ℕ} {w w' : GWord α ρ} (h : Proper u w) (h' : Proper u w') :
    Proper u (w ++ w') := by
  intro mv hmv
  rcases List.mem_append.mp hmv with h1|h1
  · exact h mv h1
  · exact h' mv h1
lemma proper_nil (u : ℕ) : Proper u ([] : GWord α ρ) := fun _ h => by simp at h
lemma proper_ofB {u : ℕ} {w : BWord α ρ} (h : w.Proper u) : Proper u (ofB w) := by
  intro mv hmv
  obtain ⟨g, hg, rfl⟩ := List.mem_map.mp hmv
  exact h g hg

lemma costR_eq_sum (u : ℕ) (φ : ℕ → ℝ) (w : GWord α ρ) (hw : Proper u w) :
    costR φ w = ∑ r : Fin u, (w.hist r:ℝ) * φ r := by
  rw [costR_shadow]; exact BWord.costR_eq_sum u φ _ hw.shadow
lemma cost_eq_sum (u : ℕ) (g : ℕ → ℕ) (w : GWord α ρ) (hw : Proper u w) :
    cost g w = ∑ r : Fin u, hist w r * g r := BWord.cost_eq_sum u g _ hw.shadow
lemma hist_zero (u : ℕ) (w : GWord α ρ) (hw : Proper u w) : hist w 0 = 0 :=
  BWord.hist_zero u _ hw.shadow
lemma hist_large (u : ℕ) (w : GWord α ρ) (hw : Proper u w) (r : ℕ) (hr : u ≤ r) :
    hist w r = 0 := BWord.hist_large u _ hw.shadow r hr

end GWord

section Sem
variable {α ρ σ : Type*} [Fintype α] [DecidableEq α] [Fintype ρ] [DecidableEq ρ]

/-- The action of one letter. -/
def GMove.act (f : ℕ) : GMove α ρ → Data α ρ f → Data α ρ f
  | .old mv => mv.act f
  | .perm l G => roleAct f l (permMat G)
  | .phase l z c => roleAct f l (phaseMat z c)

/-- **Semantics of a generalised word.** -/
def gwalk (f : ℕ) (w : GWord α ρ) (x : Data α ρ f) : Data α ρ f :=
  w.foldl (fun y mv => mv.act f y) x

@[simp] lemma gwalk_nil (f : ℕ) (x : Data α ρ f) : gwalk f ([] : GWord α ρ) x = x := rfl
lemma gwalk_cons (f : ℕ) (mv : GMove α ρ) (w : GWord α ρ) (x : Data α ρ f) :
    gwalk f (mv :: w) x = gwalk f w (mv.act f x) := rfl
lemma gwalk_append (f : ℕ) (p q : GWord α ρ) (x : Data α ρ f) :
    gwalk f (p ++ q) x = gwalk f q (gwalk f p x) := by simp [gwalk]

/-- Old words keep their meaning. -/
lemma gwalk_ofB (f : ℕ) (w : BWord α ρ) (x : Data α ρ f) :
    gwalk f (GWord.ofB w) x = walk f w.flat x := by
  induction w generalizing x with
  | nil => rfl
  | cons mv w ih =>
    rw [walk_flat_cons, ← ih]
    rfl

/-- The scratch certificate for the generalised language (cf. `RAM.LiveKernel`). -/
def GLiveKernel (e : σ → ρ) (w : GWord α ρ) : Prop :=
  ∀ (f : ℕ) (v : Data α ρ f), (∀ s, (∀ l, e l ≠ s) → v s = 0) →
    ∀ l, gwalk f w v (e l) = matAct f (kernel α) (v (e l))

/-- Every old certificate is a generalised certificate. -/
theorem GLiveKernel.ofB {e : σ → ρ} {w : BWord α ρ} (h : RAM.LiveKernel e w.flat) :
    GLiveKernel e (GWord.ofB w) := by
  intro f v hv l
  rw [gwalk_ofB]
  exact h f v hv l

/-- One role goes from matrix `M` to `N` by a generalised word (cf. `XStep`). -/
def GStep (l : ρ) (M N : CMat α) (c : (ℕ → ℝ) → ℝ) : Prop :=
  ∃ (w : GWord α ρ) (U : CMat α), w.Proper (Fintype.card α) ∧ (∀ φ, w.costR φ = c φ) ∧
    U * M = N ∧ ∀ (f : ℕ) (x : Data α ρ f), gwalk f w x = roleAct f l U x

end Sem
end
end PowerSaving.GF
end OAI

#print axioms OAI.PowerSaving.GF.gwalk_ofB
#print axioms OAI.PowerSaving.GF.GLiveKernel.ofB
#print axioms OAI.PowerSaving.GF.GWord.costR_eq_sum
