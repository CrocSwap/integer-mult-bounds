import TransitiveTrits

namespace TritMarginals

abbrev Aut (n : ℕ) := V n ≃ₗ[F] V n
abbrev NZ (n : ℕ) := {x : V n // x ≠ 0}

noncomputable instance autFintype (n : ℕ) : Fintype (Aut n) :=
  Fintype.ofInjective (fun T : Aut n => (T : V n → V n)) (by
    intro A B eq
    exact LinearEquiv.ext (congrFun eq))

def placed {n : ℕ} (x : NZ n) (T : Aut n) : NZ n :=
  ⟨T x.val, fun hz => x.prop (T.injective (hz.trans T.map_zero.symm))⟩

def targetFibers {n : ℕ} (x y z : NZ n) (T : Aut n) (hy : T y.val = z.val) :
    {A : Aut n // placed x A = y} ≃ {A : Aut n // placed x A = z} where
  toFun A := ⟨A.val.trans T, by
    apply Subtype.ext
    change T (A.val x.val) = z.val
    exact (congrArg T (congrArg Subtype.val A.prop)).trans hy⟩
  invFun A := ⟨A.val.trans T.symm, by
    apply Subtype.ext
    change T.symm (A.val x.val) = y.val
    apply T.injective
    rw [T.apply_symm_apply]
    exact (congrArg Subtype.val A.prop).trans hy.symm⟩
  left_inv A := by
    apply Subtype.ext
    apply LinearEquiv.ext
    intro v
    exact T.symm_apply_apply _
  right_inv A := by
    apply Subtype.ext
    apply LinearEquiv.ext
    intro v
    exact T.apply_symm_apply _

/-- A fixed native nonzero factor has the exact uniform marginal over all invertible matrices. -/
theorem marginal {n : ℕ} (x : NZ (n+1)) (p : NZ (n+1) → Prop) [DecidablePred p] :
    Fintype.card {T : Aut (n+1) // p (placed x T)} * Fintype.card (NZ (n+1)) =
      Fintype.card (Aut (n+1)) * Fintype.card {y : NZ (n+1) // p y} := by
  classical
  let k := Fintype.card {T : Aut (n+1) // placed x T = x}
  have hf (y : NZ (n+1)) : Fintype.card {T : Aut (n+1) // placed x T = y} = k := by
    obtain ⟨T,hT⟩ := transitiveNonzero y.val x.val y.prop x.prop
    exact Fintype.card_congr (targetFibers x y x T hT)
  have all := uniformCount (placed x) (fun _ => True) k hf
  have size : Fintype.card (Aut (n+1)) = Fintype.card (NZ (n+1))*k := by
    simpa only [Fintype.card_subtype_true] using all
  rw [uniformCount (placed x) p k hf, size]
  ring

/-- Remove the extra nonzero witness when membership already implies it. -/
def flatten {n : ℕ} (p : V n → Prop) (nz : ∀ v, p v → v ≠ 0) :
    {y : NZ n // p y.val} ≃ {y : V n // p y} where
  toFun y := ⟨y.val.val, y.prop⟩
  invFun y := ⟨⟨y.val, nz y.val y.prop⟩, y.prop⟩
  left_inv _ := rfl
  right_inv _ := rfl

theorem firstMarginal {n : ℕ} (x : NZ (n+1)) :
    Fintype.card {T : Aut (n+1) // T x.val 0 ≠ 0} * (3^(n+1)-1) =
      Fintype.card (Aut (n+1)) * (2*3^n) := by
  let p (y : NZ (n+1)) := y.val 0 ≠ 0
  have h := marginal x p
  have nz : ∀ v : V (n+1), v 0 ≠ 0 → v ≠ 0 :=
    fun _ hv hz => hv (congrFun hz 0)
  have c := Fintype.card_congr (flatten (fun v : V (n+1) => v 0 ≠ 0) nz)
  rw [nonzeroCount, c, firstCount] at h
  exact h

theorem lineMarginal {n : ℕ} (x : NZ (n+1)) :
    Fintype.card {T : Aut (n+1) // T x.val 0 ≠ 0 ∧ Fin.tail (T x.val) = 0} * (3^(n+1)-1) =
      Fintype.card (Aut (n+1)) * 2 := by
  let p (y : NZ (n+1)) := y.val 0 ≠ 0 ∧ Fin.tail y.val = 0
  have h := marginal x p
  have nz : ∀ v : V (n+1), (v 0 ≠ 0 ∧ Fin.tail v = 0) → v ≠ 0 :=
    fun _ hv hz => hv.1 (congrFun hz 0)
  have c := Fintype.card_congr
    (flatten (fun v : V (n+1) => v 0 ≠ 0 ∧ Fin.tail v = 0) nz)
  rw [nonzeroCount, c, onlyCount] at h
  exact h

#print axioms marginal
#print axioms firstMarginal
#print axioms lineMarginal

end TritMarginals
