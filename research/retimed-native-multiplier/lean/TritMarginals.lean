import Mathlib.Tactic
import Mathlib.Data.ZMod.Basic
import Mathlib.Data.Fin.Tuple.Basic

namespace TritMarginals

abbrev F := ZMod 3
abbrev V (n : ℕ) := Fin n → F

/-- The nonzero first coordinate and the free tail give the entire event. -/
def firstEquiv (n : ℕ) :
    ({a : F // a ≠ 0} × V n) ≃ {x : V (n+1) // x 0 ≠ 0} where
  toFun p := ⟨Fin.cons p.1.val p.2, by simpa using p.1.prop⟩
  invFun p := (⟨p.1 0, p.2⟩, Fin.tail p.1)
  left_inv p := by rcases p with ⟨⟨a, ha⟩, r⟩; simp
  right_inv p := by apply Subtype.ext; exact Fin.cons_self_tail _

theorem nonzeroTrits : Fintype.card {a : F // a ≠ 0} = 2 := by
  rw [Fintype.card_subtype_compl, Fintype.card_subtype_eq, ZMod.card]

theorem firstCount (n : ℕ) : Fintype.card {x : V (n+1) // x 0 ≠ 0} = 2*3^n := by
  rw [← Fintype.card_congr (firstEquiv n), Fintype.card_prod, nonzeroTrits]
  simp [V, ZMod.card]

theorem nonzeroCount (n : ℕ) : Fintype.card {x : V n // x ≠ 0} = 3^n-1 := by
  rw [Fintype.card_subtype_compl, Fintype.card_subtype_eq]
  simp [V, ZMod.card]

/-- An exceptional line contains only its two nonzero scalar multiples. -/
def onlyEquiv (n : ℕ) :
    {a : F // a ≠ 0} ≃ {x : V (n+1) // x 0 ≠ 0 ∧ Fin.tail x = 0} where
  toFun a := ⟨Fin.cons a.val (0 : V n), by simp [a.prop]⟩
  invFun p := ⟨p.1 0, p.2.1⟩
  left_inv _ := by apply Subtype.ext; simp
  right_inv p := by
    apply Subtype.ext
    change Fin.cons (p.1 0) (0 : V n) = p.1
    calc
      Fin.cons (p.1 0) (0 : V n) = Fin.cons (p.1 0) (Fin.tail p.1) :=
        congrArg (fun t : V n => (Fin.cons (p.1 0) t : V (n+1))) p.2.2.symm
      _ = p.1 := Fin.cons_self_tail p.1

theorem onlyCount (n : ℕ) :
    Fintype.card {x : V (n+1) // x 0 ≠ 0 ∧ Fin.tail x = 0} = 2 := by
  rw [← Fintype.card_congr (onlyEquiv n), nonzeroTrits]

/-- Left multiplication gives an explicit bijection between fibers of a transitive orbit. -/
def actionFibers {G X : Type*} [Group G] [MulAction G X] (x y z : X)
    (g : G) (hyz : g • y = z) :
    {h : G // h • x = y} ≃ {h : G // h • x = z} where
  toFun h := ⟨g * h.1, by rw [mul_smul, h.2, hyz]⟩
  invFun h := ⟨g⁻¹ * h.1, by rw [mul_smul, h.2, ← hyz, inv_smul_smul]⟩
  left_inv h := by apply Subtype.ext; exact inv_mul_cancel_left g _
  right_inv h := by apply Subtype.ext; exact mul_inv_cancel_left g _

/-- Equal subgroup or stabilizer fibers preserve exact event counts up to
    their common integer cardinal. -/
theorem uniformCount {X Y : Type*} [Fintype X] [Fintype Y] [DecidableEq Y]
    (f : X → Y) (p : Y → Prop) [DecidablePred p] (k : ℕ)
    (fiber : ∀ y, Fintype.card {x : X // f x = y} = k) :
    Fintype.card {x : X // p (f x)} = Fintype.card {y : Y // p y} * k := by
  let e : {x : X // p (f x)} ≃ ((y : {v : Y // p v}) × {x : X // f x = y.val}) :=
    { toFun := fun x => ⟨⟨f x.val, x.prop⟩, ⟨x.val, rfl⟩⟩
      invFun := fun ⟨y, x⟩ => ⟨x.val, Eq.mpr (congrArg p x.prop) y.prop⟩
      left_inv := fun _ => rfl
      right_inv := by
        rintro ⟨⟨y, py⟩, ⟨x, hx⟩⟩
        change f x = y at hx
        subst y
        rfl }
  rw [Fintype.card_congr e, Fintype.card_sigma]
  simp [fiber]

#print axioms firstCount
#print axioms nonzeroCount
#print axioms onlyCount
#print axioms actionFibers
#print axioms uniformCount

end TritMarginals
