/-
Nonvacuous instances and hypothesis-boundary witnesses for PrefixNorm.
Gareth Davidson, with substantial OpenAI Codex assistance. Apache-2.0.
-/
import PrefixNorm
import Mathlib.Tactic.FinCases

open scoped BigOperators
open LemmaG LemmaG.Stream

noncomputable section

namespace PrefixNorm.Examples

abbrev Reg := Fin 2

def labels (_ : Reg) : Bool := false

def input (r : Reg) : ℝ := if r = 0 then 1 else 0

def phases : Bool → ℝ ≃ₗ[ℝ] ℝ
  | false => LinearEquiv.refl ℝ ℝ
  | true => LinearEquiv.neg ℝ

def recipe (a b : Bool) (x : ℝ) : ℝ := phases b ((phases a).symm x)

theorem phases_norm (a : Bool) (x : ℝ) : ‖phases a x‖ = ‖x‖ := by
  cases a <;> simp [phases]

theorem recipe_exact (es : List (Event Reg Bool ℝ)) : RecipesExact phases recipe es := by
  intro r A B hm x
  rfl

def goodWord : List (Event Reg Bool ℝ) :=
  [.copy 1 0 false, .relabel 0 false true, .relabel 1 false true,
   .add 0 1 (-1), .add 0 1 1, .relabel 0 true false, .clear 1 false]

theorem good_labelled : WellLabelled goodWord labels := by
  norm_num [goodWord, WellLabelled, Event.Admissible, Event.lab, labels, Function.update_apply]

/-- The new all-prefix theorem actually applies to a word with nonidentity labels. -/
theorem good_prefix_bound (k : ℕ) (r : Reg) :
    ‖physRun recipe (goodWord.take k) input r‖ ≤ ‖S (goodWord.take k) r 0‖ := by
  have hx : ∀ j ∈ ({0} : Finset Reg), ‖input j‖ ≤ (1 : ℝ) := by
    intro j hj
    have h : j = 0 := by simpa using hj
    subst j
    norm_num [input]
  have hz : ∀ j ∉ ({0} : Finset Reg), input j = 0 := by
    intro j hj
    simp_all [input]
  simpa using supported_prefix phases recipe goodWord labels input {0} 1 phases_norm
    (recipe_exact goodWord) good_labelled hx hz k r

theorem good_cancellation_cut : physRun recipe (goodWord.take 4) input 0 = 0 := by
  norm_num [goodWord, physRun, Event.phys, input, recipe, phases, Function.update_apply]

def badWord : List (Event Reg Bool ℝ) :=
  [.copy 1 0 false, .relabel 1 false true, .add 0 1 (-1),
   .add 0 1 1, .relabel 1 true false, .clear 1 false]

theorem bad_not_labelled : ¬ WellLabelled badWord labels := by
  norm_num [badWord, WellLabelled, Event.Admissible, Event.lab, labels, Function.update_apply]

/-- Unitary exact recipes and a restored endpoint do not replace label admissibility. -/
theorem bad_cut : physRun recipe (badWord.take 3) input 0 = 2 ∧
    S (badWord.take 3) (0 : Reg) 0 = 0 := by
  norm_num [badWord, S, scalRun, physRun, Event.scal, Event.phys, input, recipe, phases,
            Function.update_apply, Pi.single_apply]

theorem bad_endpoint : physRun recipe badWord input = input := by
  funext r
  fin_cases r <;>
    norm_num [badWord, physRun, Event.phys, input, recipe, phases, Function.update_apply]

/-- Each actual recipe preserves norms, but one reverse edge is not the labelled inverse. -/
def asymmetricRecipe (a b : Bool) (x : ℝ) : ℝ :=
  if a = false ∧ b = true then -x else x

def wrongRecipeWord : List (Event Reg Bool ℝ) :=
  [.copy 1 0 false, .relabel 1 false true, .relabel 1 true false, .add 0 1 (-1)]

theorem asymmetric_preserves_norm (a b : Bool) (x : ℝ) :
    ‖asymmetricRecipe a b x‖ = ‖x‖ := by
  cases a <;> cases b <;> simp [asymmetricRecipe]

theorem wrong_recipe_labelled : WellLabelled wrongRecipeWord labels := by
  norm_num [wrongRecipeWord, WellLabelled, Event.Admissible, Event.lab, labels, Function.update_apply]

theorem wrong_recipe_not_exact : ¬ RecipesExact phases asymmetricRecipe wrongRecipeWord := by
  intro h
  have bad := h 1 true false (by simp [wrongRecipeWord]) (1 : ℝ)
  norm_num [asymmetricRecipe, phases] at bad

theorem wrong_recipe_cut : physRun asymmetricRecipe wrongRecipeWord input 0 = 2 ∧
    S wrongRecipeWord (0 : Reg) 0 = 0 := by
  norm_num [wrongRecipeWord, physRun, Event.phys, S, scalRun, Event.scal, input,
            asymmetricRecipe, Function.update_apply, Pi.single_apply]

/-- An exact invertible label can nevertheless amplify norms. -/
def eight : ℝ ≃ₗ[ℝ] ℝ where
  toFun x := 8 * x
  invFun x := x / 8
  left_inv x := by dsimp; ring
  right_inv x := by dsimp; ring
  map_add' x y := by ring
  map_smul' x y := by simp only [RingHom.id_apply, smul_eq_mul]; ring

def largeLabels : Bool → ℝ ≃ₗ[ℝ] ℝ
  | false => LinearEquiv.refl ℝ ℝ
  | true => eight

def largeRecipe (a b : Bool) (x : ℝ) : ℝ := largeLabels b ((largeLabels a).symm x)

def loop : List (Event Reg Bool ℝ) := [.relabel 0 false true, .relabel 0 true false]

theorem loop_labelled : WellLabelled loop labels := by
  norm_num [loop, WellLabelled, Event.Admissible, Event.lab, labels, Function.update_apply]

theorem loop_exact : RecipesExact largeLabels largeRecipe loop := by
  intro r A B hm x
  rfl

theorem eight_not_norm_preserving : ‖largeLabels true (1 : ℝ)‖ ≠ ‖(1 : ℝ)‖ := by
  norm_num [largeLabels, eight]

theorem loop_cut : physRun largeRecipe (loop.take 1) input 0 = 8 ∧
    S (loop.take 1) (0 : Reg) 0 = 1 := by
  norm_num [loop, physRun, Event.phys, S, scalRun, Event.scal, input,
            largeRecipe, largeLabels, eight, Function.update_apply, Pi.single_apply]

theorem loop_endpoint : physRun largeRecipe loop input = input := by
  funext r
  fin_cases r <;>
    norm_num [loop, physRun, Event.phys, input, largeRecipe, largeLabels, eight, Function.update_apply]

def oldVector : EuclideanSpace ℂ Unit := WithLp.toLp 2 (fun _ => ⟨3/5, 4/5⟩)
def newVector : EuclideanSpace ℂ Unit := WithLp.toLp 2 (fun _ => 1)

/-- Both endpoints have unit norm; a real-first store has squared norm 41/25. -/
theorem half_store_overshoot : ‖oldVector‖ ^ 2 = 1 ∧ ‖newVector‖ ^ 2 = 1 ∧
    ‖components Finset.univ ∅ oldVector newVector‖ ^ 2 = 41/25 := by
  norm_num [PiLp.norm_sq_eq_of_L2, oldVector, newVector, components,
            Complex.sq_norm, Complex.normSq_apply, PiLp.toLp_apply]

/-- Only a conditional numerical corollary: source row bounds are not assumed proved by Lean. -/
theorem forward_bits_if {ν : Type*} [Fintype ν] [DecidableEq ν]
    (reDone imDone : Finset ν) (old new : EuclideanSpace ℂ ν)
    (ho : ‖old‖ ≤ 131088) (hn : ‖new‖ ≤ 131088) :
    ‖components reDone imDone old new‖ < (2 : ℝ) ^ 18 := by
  exact components_bits reDone imDone old new 131088 18 (by norm_num) ho hn (by norm_num)

theorem backward_bits_if {ν : Type*} [Fintype ν] [DecidableEq ν]
    (reDone imDone : Finset ν) (old new : EuclideanSpace ℂ ν)
    (ho : ‖old‖ ≤ 1154896) (hn : ‖new‖ ≤ 1154896) :
    ‖components reDone imDone old new‖ < (2 : ℝ) ^ 21 := by
  exact components_bits reDone imDone old new 1154896 21 (by norm_num) ho hn (by norm_num)

end PrefixNorm.Examples
