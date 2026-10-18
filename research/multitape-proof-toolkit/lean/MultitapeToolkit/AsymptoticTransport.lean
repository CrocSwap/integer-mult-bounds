import MultitapeToolkit.Complexity
import Mathlib.Analysis.Asymptotics.Ring
import MultitapeToolkit.TM2HeterogeneousCompiler

/-!
# Universal transport of actual source computations and asymptotic costs

A concrete heterogeneous finite TM2 program is compiled into a fixed finite-control
multitape machine. Source hypotheses describe actual completed executions, never
an unknown subroutine. The cost is exactly bounded by the published syntactic
overhead. A uniformly bounded syntax-depth family obtains an explicit common bound;
this does not replace the requirement to fix a machine before its input quantifiers.
-/

namespace MultitapeToolkit.Transport

open Turing Filter Asymptotics

variable {K Λ σ : Type} {Γ : K → Type} {X : Type*}
  [Fintype K] [DecidableEq K] [∀ k, Fintype (Γ k)] [Fintype Λ] [Fintype σ]

/-- A source cost contract quantifies over actual complete executions and output. -/
def SourceComputesInTime (M : Λ → TM2.Stmt Γ Λ σ)
    (input : X → TM2.Cfg Γ Λ σ) (output : X → TM2.Cfg Γ Λ σ → Prop)
    (size : X → ℕ) (T : ℕ → ℕ) : Prop :=
  ∀ x, ∃ t final, t ≤ T (size x) ∧
    ((fun s : Option (TM2.Cfg Γ Λ σ) => s.bind (TM2.step M))^[t]) (some (input x)) = some final ∧
    final.l = none ∧ output x final

/-- Preserve all actual source output while charging every elementary tape step. -/
theorem compiled_computesInTime (M : Λ → TM2.Stmt Γ Λ σ)
    {input : X → TM2.Cfg Γ Λ σ} {output : X → TM2.Cfg Γ Λ σ → Prop}
    {size : X → ℕ} {T : ℕ → ℕ} (h : SourceComputesInTime M input output size T) :
    ComputesInTime (MultitapeToolkit.TM2HeterogeneousCompiler.compile M)
      (fun x => MultitapeToolkit.TM2HeterogeneousCompiler.encode M (input x))
      (fun x final => ∃ sourceFinal, final = MultitapeToolkit.TM2HeterogeneousCompiler.encode M sourceFinal ∧ output x sourceFinal)
      size (fun n => MultitapeToolkit.TM2HeterogeneousCompiler.overhead M * T n) := by
  intro x
  rcases h x with ⟨t, final, ht, hr, hh, ho⟩
  rcases MultitapeToolkit.TM2HeterogeneousCompiler.compile_run M t (input x) final hr with ⟨physical, hp, hrun⟩
  refine ⟨physical, MultitapeToolkit.TM2HeterogeneousCompiler.encode M final,
    hp.trans (Nat.mul_le_mul_left _ ht), hrun, ?_, final, rfl, ho⟩
  rcases final with ⟨l, v, S⟩
  change l = none at hh
  subst l
  exact MultitapeToolkit.TM2HeterogeneousCompiler.encode_halts M v S

omit [Fintype K] [DecidableEq K] [∀ k, Fintype (Γ k)] [Fintype σ] in
/-- Every finite uniformly bounded-depth family has an explicit common simulation overhead. -/
theorem overhead_le_of_depth_bound {P : Type*} (M : P → Λ → TM2.Stmt Γ Λ σ) (D : ℕ)
    (h : ∀ p l, MultitapeToolkit.TM2HeterogeneousCompiler.depth (M p l) ≤ D) (p : P) :
    MultitapeToolkit.TM2HeterogeneousCompiler.overhead (M p) ≤ 2 * D := by
  apply Nat.mul_le_mul_left 2
  apply Finset.sup_le
  intro l _
  exact h p l

/-- Actual source computations with a common depth bound receive a common physical budget. -/
theorem compiled_computesInTime_depth (M : Λ → TM2.Stmt Γ Λ σ) (D : ℕ)
    (hd : ∀ l, MultitapeToolkit.TM2HeterogeneousCompiler.depth (M l) ≤ D)
    {input : X → TM2.Cfg Γ Λ σ} {output : X → TM2.Cfg Γ Λ σ → Prop}
    {size : X → ℕ} {T : ℕ → ℕ} (h : SourceComputesInTime M input output size T) :
    ComputesInTime (MultitapeToolkit.TM2HeterogeneousCompiler.compile M)
      (fun x => MultitapeToolkit.TM2HeterogeneousCompiler.encode M (input x))
      (fun x final => ∃ sourceFinal, final = MultitapeToolkit.TM2HeterogeneousCompiler.encode M sourceFinal ∧ output x sourceFinal)
      size (fun n => 2 * D * T n) := by
  intro x
  rcases compiled_computesInTime M h x with ⟨t, final, ht, hr, hh, ho⟩
  refine ⟨t, final, ht.trans ?_, hr, hh, ho⟩
  exact Nat.mul_le_mul_right _ (overhead_le_of_depth_bound (fun _ : Unit => M) D (fun _ => hd) ())

/-- A literal pointwise natural cost bound establishes standard asymptotic domination. -/
theorem cost_bound_isBigO (actual budget : ℕ → ℕ) (A : ℕ)
    (h : ∀ n, actual n ≤ A * budget n) :
    (fun n : ℕ => (actual n : ℝ)) =O[atTop] (fun n : ℕ => (budget n : ℝ)) := by
  refine isBigO_iff.mpr ⟨(A : ℝ), Filter.Eventually.of_forall ?_⟩
  intro n
  simp only [Real.norm_natCast]
  exact_mod_cast h n

/-- Fixed compilation factors preserve any established real asymptotic time target. -/
theorem fixed_overhead_isBigO (actual source : ℕ → ℕ) (A : ℕ) (target : ℕ → ℝ)
    (hcost : ∀ n, actual n ≤ A * source n)
    (hsource : (fun n : ℕ => (source n : ℝ)) =O[atTop] target) :
    (fun n : ℕ => (actual n : ℝ)) =O[atTop] target :=
  (cost_bound_isBigO actual source A hcost).trans hsource

/-- Compiler work plus separately proved adapter work preserves the same target. -/
theorem compiled_and_adapter_isBigO (actual source adapter : ℕ → ℕ) (A : ℕ)
    (target : ℕ → ℝ) (hcost : ∀ n, actual n ≤ A * source n + adapter n)
    (hsource : (fun n : ℕ => (source n : ℝ)) =O[atTop] target)
    (hadapter : (fun n : ℕ => (adapter n : ℝ)) =O[atTop] target) :
    (fun n : ℕ => (actual n : ℝ)) =O[atTop] target := by
  have hdom := cost_bound_isBigO actual (fun n => A * source n + adapter n) 1
    (fun n => by simpa using hcost n)
  have hsum := (hsource.const_mul_left (A : ℝ)).add hadapter
  apply hdom.trans
  simpa only [Nat.cast_add, Nat.cast_mul] using hsum

end MultitapeToolkit.Transport





