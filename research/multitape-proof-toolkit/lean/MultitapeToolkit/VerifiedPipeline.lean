import MultitapeToolkit.AsymptoticTransport
import MultitapeToolkit.FrameRule

/-!
# Checked compiler, physical cost, and completed dirty frames in one theorem

For each fixed finite heterogeneous TM2 program, every actual halted source run
has a genuine local multitape implementation. Its full transition count is
bounded by the fixed syntax depth, every source stack is retained in the physical
encoding, and an actual finite observation footprint guarantees identical
completed runtimes for arbitrary alternative dirt outside that footprint.
-/

namespace MultitapeToolkit.VerifiedPipeline

open Turing Absolute Absolute.FrameRule

variable {K Λ σ : Type} {Γ : K → Type}
  [Fintype K] [DecidableEq K] [∀ k, Fintype (Γ k)] [Fintype Λ] [Fintype σ]

/-- Universal sufficient assembly of the actual compiler, completed physical run,
exact encoded output, fixed syntax-depth charge, and completed trace frame. -/
theorem compile_completed_frame (M : Λ → TM2.Stmt Γ Λ σ) (D n : ℕ)
    (hd : ∀ l, MultitapeToolkit.TM2HeterogeneousCompiler.depth (M l) ≤ D)
    (c d : TM2.Cfg Γ Λ σ)
    (hr : ((fun s : Option (TM2.Cfg Γ Λ σ) => s.bind (TM2.step M))^[n]) (some c) = some d)
    (hh : d.l = none) :
    ∃ (t : ℕ) (heads : K → ℤ) (observed : K → Finset ℤ),
      t ≤ 2 * D * n ∧
      Absolute.Runs (ofMachine (MultitapeToolkit.TM2HeterogeneousCompiler.compile M)) t
        (realize (MultitapeToolkit.TM2HeterogeneousCompiler.encode M c) (fun _ => 0))
        (realize (MultitapeToolkit.TM2HeterogeneousCompiler.encode M d) heads) ∧
      Absolute.Halts (ofMachine (MultitapeToolkit.TM2HeterogeneousCompiler.compile M))
        (realize (MultitapeToolkit.TM2HeterogeneousCompiler.encode M d) heads) ∧
      (∀ i, (observed i).card ≤ t + 1) ∧
      (∀ i x, x ∉ observed i →
        (realize (MultitapeToolkit.TM2HeterogeneousCompiler.encode M d) heads).cell i x =
        (realize (MultitapeToolkit.TM2HeterogeneousCompiler.encode M c) (fun _ => 0)).cell i x) ∧
      (∀ other, MatchesOn (fun i => (observed i : Set ℤ))
        (realize (MultitapeToolkit.TM2HeterogeneousCompiler.encode M c) (fun _ => 0)) other →
        ∃ otherFinal,
          Absolute.Runs (ofMachine (MultitapeToolkit.TM2HeterogeneousCompiler.compile M)) t other otherFinal ∧
          Absolute.Halts (ofMachine (MultitapeToolkit.TM2HeterogeneousCompiler.compile M)) otherFinal ∧
          MatchesOn (fun i => (observed i : Set ℤ))
            (realize (MultitapeToolkit.TM2HeterogeneousCompiler.encode M d) heads) otherFinal ∧
          ∀ i x, x ∉ observed i → otherFinal.cell i x = other.cell i x) := by
  rcases MultitapeToolkit.TM2HeterogeneousCompiler.compile_run M n c d hr with ⟨t, ht, hphysical⟩
  have hbound : t ≤ 2 * D * n := ht.trans
    (Nat.mul_le_mul_right n
      (Transport.overhead_le_of_depth_bound (fun _ : Unit => M) D (fun _ => hd) ()))
  have hhalt : MultitapeToolkit.Halts (MultitapeToolkit.TM2HeterogeneousCompiler.compile M)
      (MultitapeToolkit.TM2HeterogeneousCompiler.encode M d) := by
    rcases d with ⟨label, v, sourceStacks⟩
    change label = none at hh
    subst label
    exact MultitapeToolkit.TM2HeterogeneousCompiler.encode_halts M v sourceStacks
  rcases Absolute.runs_simulation (MultitapeToolkit.TM2HeterogeneousCompiler.compile M) hphysical
    (fun _ => 0) with ⟨heads, habsolute⟩
  have hhaltAbsolute := (Absolute.halts_iff (MultitapeToolkit.TM2HeterogeneousCompiler.compile M)
    (MultitapeToolkit.TM2HeterogeneousCompiler.encode M d) heads).2 hhalt
  rcases completed_runs_finite_frame habsolute hhaltAbsolute with
    ⟨observed, hcard, hframe, hdirty⟩
  exact ⟨t, heads, observed, hbound, habsolute, hhaltAbsolute, hcard, hframe, hdirty⟩

end MultitapeToolkit.VerifiedPipeline


