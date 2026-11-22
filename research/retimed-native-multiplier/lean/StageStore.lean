import Mathlib.Tactic

namespace StageStore

/-- A fixed physical role has an ordered list of open suffix lengths and the
    greatest position reached so far. Closing a sibling preserves that high. -/
structure Tape where
  slots : List ℕ
  high : ℕ

def reserved (D W : ℕ) (t : Tape) : Prop :=
  t.slots.length ≤ D ∧ (∀ v ∈ t.slots,v≤W) ∧ t.high ≤ D*W

theorem intervalTotal (W : ℕ) (vs : List ℕ) (h : ∀ x ∈ vs, x≤W) :
    vs.sum ≤ vs.length*W := by
  induction vs with
  | nil => simp
  | cons x xs ih =>
    have head := h x (by simp)
    have tail := ih (by intro y hy; exact h y (by simp [hy]))
    simp only [List.sum_cons,List.length_cons,Nat.succ_mul]
    omega

/-- push allocates a delimited reusable suffix. replace accounts an opened
    interval's new own extent. remove erases it and restores its parent end. -/
inductive Step (D W : ℕ) : Tape → Tape → Prop
  | push (vs : List ℕ) (h k : ℕ) (hd : vs.length < D) (hw : k≤W) :
      Step D W ⟨vs,h⟩ ⟨k::vs,max h (k+vs.sum)⟩
  | replace (vs : List ℕ) (h old k : ℕ) (hw : k≤W) :
      Step D W ⟨old::vs,h⟩ ⟨k::vs,max h (k+vs.sum)⟩
  | remove (vs : List ℕ) (h old : ℕ) :
      Step D W ⟨old::vs,h⟩ ⟨vs,h⟩

theorem oneStep (D W : ℕ) {u v : Tape} (h : reserved D W u) (step : Step D W u v) :
    reserved D W v := by
  cases step with
  | push vs hist k hd hw =>
    obtain ⟨_,bounds,past⟩ := h
    have ht := intervalTotal W vs bounds
    have hd' : (vs.length+1)*W≤D*W := Nat.mul_le_mul_right W hd
    simp only [Nat.add_mul,one_mul] at hd'
    refine ⟨by simpa using hd,by simpa [hw] using And.intro hw bounds,?_⟩
    change max hist (k+vs.sum) ≤ D*W
    exact max_le past (by omega)
  | replace vs hist old k hw =>
    obtain ⟨hd,bounds,past⟩ := h
    have hb : ∀ x ∈ vs,x≤W := by intro x hx; exact bounds x (by simp [hx])
    have ht := intervalTotal W vs hb
    change vs.length+1≤D at hd
    have hd' := Nat.mul_le_mul_right W hd
    simp only [Nat.add_mul,one_mul] at hd'
    refine ⟨hd,by simpa using And.intro hw hb,?_⟩
    change max hist (k+vs.sum) ≤ D*W
    exact max_le past (by omega)
  | remove vs hist old =>
    obtain ⟨hd,bounds,past⟩ := h
    change vs.length+1≤D at hd
    exact ⟨by change vs.length≤D; omega,by intro x hx; exact bounds x (by simp [hx]),past⟩

theorem historical (D W : ℕ) {t : Tape}
    (path : Relation.ReflTransGen (Step D W) ⟨[],0⟩ t) : t.high ≤ D*W := by
  suffices reserved D W t from this.2.2
  induction path with
  | refl => simp [reserved]
  | tail _ step ih => exact oneStep D W ih step

#print axioms historical
end StageStore
