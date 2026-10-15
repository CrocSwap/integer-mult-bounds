import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.FiniteDimensional.Basic
import Lean.Elab.Tactic.Omega

/-!
Chronological one-array transcript cuts. The source-side state may read the
entire target-side state freely; every update of target-side state from source
information must use `receive`, which transmits one element of D.
-/
set_option maxHeartbeats 1000000

namespace TransportCut

variable {K X L R D : Type*} [Field K]
  [AddCommGroup X] [Module K X] [AddCommGroup L] [Module K L]
  [AddCommGroup R] [Module K R] [AddCommGroup D] [Module K D]

/-- Source-dependent blocks of a finite two-side linear execution.
Independent dirty inputs have been fixed to zero when taking these blocks.
`source` grants arbitrary local work AND return traffic at no counted cost.
`receive` is the sole constructor importing source information to the right.
-/
inductive Runs : Nat → (X →ₗ[K] L) → (X →ₗ[K] R) → Prop
  | init (s : X →ₗ[K] L) : Runs 0 s 0
  | source {n s t} (h : Runs n s t) (a : L × R →ₗ[K] L) :
      Runs n (a.comp (s.prod t)) t
  | target {n s t} (h : Runs n s t) (a : R →ₗ[K] R) :
      Runs n s (a.comp t)
  | receive {n s t} (h : Runs n s t)
      (read : L × R →ₗ[K] D) (keep : L × R →ₗ[K] L)
      (a : R →ₗ[K] R) (b : D →ₗ[K] R) :
      Runs (n + 1) (keep.comp (s.prod t))
        (a.comp t + b.comp (read.comp (s.prod t)))

/-- Positive constructor fixture: one whole-array message attains identity.
This uses arbitrary input D, with no special clean-source restriction. -/
theorem one_receive_attains :
    Runs (K := K) (D := D) 1 (LinearMap.id : D →ₗ[K] D)
      (LinearMap.id : D →ₗ[K] D) := by
  have h0 : Runs (D := D) 0 (LinearMap.id : D →ₗ[K] D) (0 : D →ₗ[K] D) :=
    Runs.init _
  have h1 := Runs.receive h0 (LinearMap.fst K D D) (LinearMap.fst K D D)
    (0 : D →ₗ[K] D) (LinearMap.id : D →ₗ[K] D)
  simpa using h1

/-- A record contains n whole arrays, not n times a native child rank. -/
def Factors (n : Nat) (t : X →ₗ[K] R) : Prop :=
  ∃ (encode : X →ₗ[K] (Fin n → D)) (decode : (Fin n → D) →ₗ[K] R),
    t = decode.comp encode

private def tailMap (n : Nat) : (Fin (n+1) → D) →ₗ[K] (Fin n → D) :=
  LinearMap.pi (fun i => LinearMap.proj i.succ)

private def consMap {n : Nat} (z : X →ₗ[K] D)
    (e : X →ₗ[K] (Fin n → D)) : X →ₗ[K] (Fin (n+1) → D) :=
  LinearMap.pi (Fin.cases z (fun i => (LinearMap.proj i).comp e))

theorem factors_postcompose {Y : Type*} [AddCommGroup Y] [Module K Y]
    {n : Nat} {t : X →ₗ[K] R}
    (h : Factors (D := D) n t) (a : R →ₗ[K] Y) :
    Factors (D := D) n (a.comp t) := by
  obtain ⟨e, d, rfl⟩ := h
  exact ⟨e, a.comp d, by ext x; rfl⟩

/-- One receive appends exactly one whole-array position to the transcript. -/
theorem factors_receive {n : Nat} {t : X →ₗ[K] R}
    (h : Factors (D := D) n t) (a : R →ₗ[K] R)
    (b : D →ₗ[K] R) (z : X →ₗ[K] D) :
    Factors (D := D) (n+1) (a.comp t + b.comp z) := by
  obtain ⟨e, d, rfl⟩ := h
  refine ⟨consMap z e, (a.comp d).comp (tailMap n) + b.comp (LinearMap.proj 0), ?_⟩
  ext x
  have ht : tailMap (K := K) n (consMap z e x) = e x := by
    funext i
    rfl
  change a (d (e x)) + b (z x) =
    a (d (tailMap n (consMap z e x))) + b (consMap z e x 0)
  rw [ht]
  rfl

/-- Universal factorization, for arbitrary finite traces and feedback. -/
theorem runs_factor {n : Nat} {s : X →ₗ[K] L} {t : X →ₗ[K] R}
    (h : Runs (D := D) n s t) : Factors (D := D) n t := by
  induction h with
  | init s => exact ⟨0, 0, by simp⟩
  | source h a ih => exact ih
  | target h a ih => exact factors_postcompose ih a
  | receive h read keep a b ih =>
      exact factors_receive ih a b _

/-- The output block's dimension is bounded by the transcript dimension. -/
theorem factors_rank [FiniteDimensional K D] {n : Nat} {t : X →ₗ[K] R}
    (h : Factors (D := D) n t) :
    Module.finrank K (LinearMap.range t) ≤ n * Module.finrank K D := by
  obtain ⟨e, d, rfl⟩ := h
  calc
    Module.finrank K (LinearMap.range (d.comp e))
        ≤ Module.finrank K (LinearMap.range d) :=
      Submodule.finrank_mono (LinearMap.range_comp_le_range e d)
    _ ≤ Module.finrank K (Fin n → D) := LinearMap.finrank_range_le d
    _ = n * Module.finrank K D := by simp [Module.finrank_pi_fintype]

/-- Complete cut-capacity theorem: one d-vector per counted receive. -/
theorem runs_rank [FiniteDimensional K D] {n : Nat}
    {s : X →ₗ[K] L} {t : X →ₗ[K] R} (h : Runs (D := D) n s t) :
    Module.finrank K (LinearMap.range t) ≤ n * Module.finrank K D :=
  factors_rank (runs_factor h)

/-- Exact recovery of m independent arrays requires at least m receives.
The final readout is linear and may use all right-side storage. -/
theorem recovery_requires_receives [FiniteDimensional K D]
    (hd : 0 < Module.finrank K D) {m n : Nat}
    {s : (Fin m → D) →ₗ[K] L} {t : (Fin m → D) →ₗ[K] R}
    (h : Runs (D := D) n s t) (out : R →ₗ[K] (Fin m → D))
    (correct : out.comp t = LinearMap.id) : m ≤ n := by
  have hr := factors_rank (factors_postcompose (runs_factor h) out)
  rw [correct] at hr
  have hh : m * Module.finrank K D ≤ n * Module.finrank K D := by
    rw [LinearMap.range_id, finrank_top, Module.finrank_pi_fintype] at hr
    simpa using hr
  exact Nat.le_of_mul_le_mul_right hh hd

/-- PR2127's numerical conclusion, conditional on its source/cut translation. -/
theorem p104_unsplit_floor [FiniteDimensional K D]
    (hd : 0 < Module.finrank K D) {k n : Nat}
    {s : (Fin 104 → D) →ₗ[K] L} {t : (Fin 104 → D) →ₗ[K] R}
    (h : Runs (D := D) n s t) (budget : n ≤ 8+k)
    (out : R →ₗ[K] (Fin 104 → D))
    (correct : out.comp t = LinearMap.id) : 96 ≤ k := by
  have hh := recovery_requires_receives hd h out correct
  omega

/-- PR2148's numerical conclusion, conditional on its refined separator. -/
theorem p104_refined_floor [FiniteDimensional K D]
    (hd : 0 < Module.finrank K D) {b n : Nat}
    {s : (Fin 56 → D) →ₗ[K] L} {t : (Fin 56 → D) →ₗ[K] R}
    (h : Runs (D := D) n s t) (budget : n ≤ 8+b)
    (out : R →ₗ[K] (Fin 56 → D))
    (correct : out.comp t = LinearMap.id) : 48 ≤ b := by
  have hh := recovery_requires_receives hd h out correct
  omega

#print axioms one_receive_attains
#print axioms factors_receive
#print axioms runs_factor
#print axioms runs_rank
#print axioms recovery_requires_receives
#print axioms p104_unsplit_floor
#print axioms p104_refined_floor

end TransportCut
