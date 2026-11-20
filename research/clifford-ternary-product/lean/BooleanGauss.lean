import TernaryCollect

/-!
Affine forms use constants, variables and addition over the two-element
field. Quadratic forms add products of two affine forms. Substitution
in this language cannot increase the degree of a quadratic form.
-/
namespace BooleanGauss
open Finset
open scoped BigOperators

inductive Aff (ι : Type) where
  | const (b : Bool)
  | var (i : ι)
  | plus (a b : Aff ι)

inductive Quad (ι : Type) where
  | affine (a : Aff ι)
  | times (a b : Aff ι)
  | plus (a b : Quad ι)

def Aff.eval {ι} (x : ι → Bool) : Aff ι → Bool
  | .const b => b
  | .var i => x i
  | .plus a b => a.eval x ^^ b.eval x

def Quad.eval {ι} (x : ι → Bool) : Quad ι → Bool
  | .affine a => a.eval x
  | .times a b => a.eval x && b.eval x
  | .plus a b => a.eval x ^^ b.eval x

def Aff.sub {ι κ} (v : ι → Aff κ) : Aff ι → Aff κ
  | .const b => .const b
  | .var i => v i
  | .plus a b => .plus (a.sub v) (b.sub v)

def Quad.sub {ι κ} (v : ι → Aff κ) : Quad ι → Quad κ
  | .affine a => .affine (a.sub v)
  | .times a b => .times (a.sub v) (b.sub v)
  | .plus a b => .plus (a.sub v) (b.sub v)

theorem Aff.eval_sub {ι κ} (v : ι → Aff κ) (a : Aff ι) (x : κ → Bool) :
    (a.sub v).eval x = a.eval (fun i ↦ (v i).eval x) := by
  induction a with
  | const => rfl
  | var => rfl
  | plus a b ha hb => simp only [sub,eval,ha,hb]

theorem Quad.eval_sub {ι κ} (v : ι → Aff κ) (a : Quad ι) (x : κ → Bool) :
    (a.sub v).eval x = a.eval (fun i ↦ (v i).eval x) := by
  induction a with
  | affine a => simp only [sub,eval,Aff.eval_sub]
  | times a b => simp only [sub,eval,Aff.eval_sub]
  | plus a b ha hb => simp only [sub,eval,ha,hb]

structure Model (ι : Type) where
  rows : List (Aff ι)
  phase : Quad ι

def support {ι} (rows : List (Aff ι)) (x : ι → Bool) : Bool :=
  rows.all fun a ↦ !(a.eval x)

def weight {ι} (M : Model ι) (x : ι → Bool) : ℤ :=
  TernaryCollect.gated (support M.rows x) (M.phase.eval x)

noncomputable def mass {ι} [Fintype ι] [DecidableEq ι] (M : Model ι) : ℤ := ∑ x, weight M x

def insertHead {n} (a : Aff (Fin n)) : Fin (n+1) → Aff (Fin n) :=
  Fin.cases a Aff.var

theorem eval_insert {n} (a : Aff (Fin n)) (x : Fin n → Bool) :
    (fun i ↦ (insertHead a i).eval x) = Fin.cons (a.eval x) x := by
  funext i
  refine Fin.cases ?_ (fun j ↦ ?_) i <;> rfl

def Aff.head {n} : Aff (Fin (n+1)) → Bool
  | .const _ => false
  | .var i => decide (i=0)
  | .plus a b => a.head ^^ b.head

def off {n} : Fin (n+1) → Aff (Fin n) := insertHead (.const false)

theorem Aff.head_split {n} (a : Aff (Fin (n+1))) (b : Bool) (x : Fin n → Bool) :
    a.eval (Fin.cons b x) = ((a.sub off).eval x ^^ (b && a.head)) := by
  induction a with
  | const v => simp [sub,eval,head]
  | var i =>
    refine Fin.cases ?_ (fun j ↦ ?_) i
    · simp [sub,eval,off,head,insertHead]
    · simp [sub,eval,off,head,insertHead]
  | plus f g hf hg =>
    simp only [eval, sub, head, hf, hg]
    cases b <;> cases (f.sub off).eval x <;> cases (g.sub off).eval x <;>
      cases f.head <;> cases g.head <;> decide

def chooseScale {ι} (b : Bool) (a : Aff ι) : Aff ι := if b then a else .const false

def Quad.derivative {n} : Quad (Fin (n+1)) → Aff (Fin n)
  | .affine a => .const a.head
  | .times a b => .plus (.plus (chooseScale a.head (b.sub off)) (chooseScale b.head (a.sub off)))
      (.const (a.head && b.head))
  | .plus a b => .plus a.derivative b.derivative

theorem Quad.head_split {n} (q : Quad (Fin (n+1))) (b : Bool) (x : Fin n → Bool) :
    q.eval (Fin.cons b x) = ((q.sub off).eval x ^^ (b && q.derivative.eval x)) := by
  induction q with
  | affine a => exact a.head_split b x
  | times a c =>
    simp only [eval, sub, derivative, Aff.eval, Aff.head_split]
    cases b <;> cases ha : a.head <;> cases hc : c.head <;>
      cases hu : (a.sub off).eval x <;> cases hv : (c.sub off).eval x <;>
      simp [hu,hv,chooseScale,Aff.eval]
  | plus a c ha hc =>
    simp only [eval, sub, derivative, Aff.eval, ha, hc]
    cases b <;> cases (a.sub off).eval x <;> cases (c.sub off).eval x <;>
      cases a.derivative.eval x <;> cases c.derivative.eval x <;> decide

def Model.sub {ι κ} (M : Model ι) (v : ι → Aff κ) : Model κ :=
  ⟨M.rows.map (Aff.sub v), M.phase.sub v⟩

theorem support_sub {ι κ} (rows : List (Aff ι)) (v : ι → Aff κ) (x : κ → Bool) :
    support (rows.map (Aff.sub v)) x = support rows (fun i ↦ (v i).eval x) := by
  simp [support, List.all_map, Aff.eval_sub, Function.comp_def]

theorem weight_sub {ι κ} (M : Model ι) (v : ι → Aff κ) (x : κ → Bool) :
    weight (M.sub v) x = weight M (fun i ↦ (v i).eval x) := by
  simp only [weight, Model.sub, support_sub, Quad.eval_sub]

/-- Rebuild each affine form with at most one term per remaining variable.
This prevents repeated substitution from growing an unreduced expression. -/
def Aff.compact : (n : ℕ) → Aff (Fin n) → Aff (Fin n)
  | 0, a => .const (a.eval Fin.elim0)
  | n+1, a => .plus (chooseScale a.head (.var 0))
      ((compact n (a.sub off)).sub (fun j ↦ .var j.succ))

theorem Aff.compact_eval (n : ℕ) (a : Aff (Fin n)) (x : Fin n → Bool) :
    (a.compact n).eval x = a.eval x := by
  induction n with
  | zero =>
    rw [compact, eval]
    exact congrArg (fun z ↦ a.eval z) (Subsingleton.elim _ _)
  | succ n ih =>
    have ht : (fun j : Fin n ↦ (Aff.var j.succ).eval x) = Fin.tail x := rfl
    rw [compact, eval, eval_sub, ht, ih]
    have h := a.head_split (x 0) (Fin.tail x)
    rw [Fin.cons_self_tail] at h
    rw [h]
    cases ha : a.head <;> cases hb : x 0 <;>
      cases (a.sub off).eval (Fin.tail x) <;> simp [chooseScale,eval,hb]

def Aff.nodes {ι} : Aff ι → ℕ
  | .const _ | .var _ => 1
  | .plus a b => a.nodes + b.nodes + 1

theorem Aff.rename_nodes {ι κ} (f : ι → κ) (a : Aff ι) :
    (a.sub (fun j ↦ .var (f j))).nodes = a.nodes := by
  induction a with
  | const => rfl
  | var => rfl
  | plus a b ha hb => simp only [sub,nodes,ha,hb]

theorem Aff.compact_nodes (n : ℕ) (a : Aff (Fin n)) : (a.compact n).nodes = 2*n+1 := by
  induction n with
  | zero => rfl
  | succ n ih =>
    rw [compact,nodes,rename_nodes,ih]
    cases ha : a.head <;> simp [chooseScale,nodes] <;> omega

def Quad.compact {n} : Quad (Fin n) → Quad (Fin n)
  | .affine a => .affine (a.compact n)
  | .times a b => .times (a.compact n) (b.compact n)
  | .plus a b => .plus a.compact b.compact

theorem Quad.compact_eval {n} (q : Quad (Fin n)) (x : Fin n → Bool) :
    q.compact.eval x = q.eval x := by
  induction q with
  | affine a => simp [compact,eval,Aff.compact_eval]
  | times a b => simp [compact,eval,Aff.compact_eval]
  | plus a b ha hb => simp [compact,eval,ha,hb]

def Model.compact {n} (M : Model (Fin n)) : Model (Fin n) :=
  ⟨M.rows.map (Aff.compact n), M.phase.compact⟩

theorem mass_compact {n} (M : Model (Fin n)) : mass M.compact = mass M := by
  unfold mass
  apply Finset.sum_congr rfl
  intro x _
  simp [weight, Model.compact, support, List.all_map, Function.comp_def, Aff.compact_eval, Quad.compact_eval]

def eliminateLoose {n} (M : Model (Fin (n+1))) : Model (Fin n) :=
  ⟨M.phase.derivative :: M.rows.map (Aff.sub off), M.phase.sub off⟩

/-- If a constraint contains the head variable, it sets its value in
terms of the remaining variables. Otherwise the derivative becomes a
new affine constraint and the summation contributes a factor of two. -/
def evaluate : (n : ℕ) → Model (Fin n) → ℤ
  | 0, M => weight M Fin.elim0
  | n+1, M =>
    match M.rows.find? Aff.head with
    | some a => evaluate n (M.sub (insertHead (a.sub off))).compact
    | none => 2 * evaluate n (eliminateLoose M).compact

theorem sum_head {n} (M : Model (Fin (n+1))) :
    mass M = ∑ x : Fin n → Bool, (weight M (Fin.cons true x) + weight M (Fin.cons false x)) := by
  unfold mass
  rw [← (Fin.consEquiv _).sum_comp, Fintype.sum_prod_type, Fintype.sum_bool, ← Finset.sum_add_distrib]
  rfl

theorem pivot_weight {n} (M : Model (Fin (n+1))) (a : Aff (Fin (n+1)))
    (ha : a ∈ M.rows) (hh : a.head = true) (x : Fin n → Bool) :
    weight M (Fin.cons true x) + weight M (Fin.cons false x) =
      weight (M.sub (insertHead (a.sub off))) x := by
  have vanish (b : Bool) (hb : b ≠ (a.sub off).eval x) : weight M (Fin.cons b x) = 0 := by
    have hap : a.eval (Fin.cons b x) = true := by
      rw [Aff.head_split, hh]
      cases b <;> cases he : (a.sub off).eval x <;> simp_all
    have hs : support M.rows (Fin.cons b x) = false := by
      apply Bool.eq_false_iff.mpr
      intro h
      have hr := (List.all_eq_true.mp h) a ha
      simp [hap] at hr
    simp [weight,hs,TernaryCollect.gated]
  rw [weight_sub, eval_insert]
  cases he : (a.sub off).eval x with
  | false => rw [vanish true (by simp [he]), zero_add]
  | true => rw [vanish false (by simp [he]), add_zero]

theorem loose_weight {n} (M : Model (Fin (n+1))) (hn : ∀ a ∈ M.rows, a.head = false)
    (x : Fin n → Bool) : weight M (Fin.cons true x) + weight M (Fin.cons false x) =
      2 * weight (eliminateLoose M) x := by
  have hsupport (b : Bool) : support M.rows (Fin.cons b x) = support (M.rows.map (Aff.sub off)) x := by
    simp only [support, List.all_map]
    apply Bool.eq_iff_iff.mpr
    rw [List.all_eq_true, List.all_eq_true]
    have eq (a : Aff (Fin (n+1))) (ha : a ∈ M.rows) : a.eval (Fin.cons b x) = (a.sub off).eval x := by
      rw [Aff.head_split, hn a ha]
      simp
    constructor <;> intro h a ha
    · simpa only [Function.comp_apply, ← eq a ha] using h a ha
    · simpa only [Function.comp_apply, eq a ha] using h a ha
  simp only [weight]
  rw [hsupport true, hsupport false]
  simp only [eliminateLoose, Quad.head_split, Bool.true_and, Bool.false_and,
    Bool.xor_false, support, List.all_cons]
  cases M.phase.derivative.eval x <;> cases (M.phase.sub off).eval x <;>
    cases (M.rows.map (Aff.sub off)).all (fun a ↦ !(a.eval x)) <;> decide

theorem evaluate_correct (n : ℕ) (M : Model (Fin n)) : evaluate n M = mass M := by
  induction n with
  | zero =>
    rw [evaluate, mass, Fintype.sum_unique]
    exact congrArg (weight M) (Subsingleton.elim _ _)
  | succ n ih =>
    rw [sum_head, evaluate]
    split
    next a hv =>
      rw [ih, mass_compact, mass]
      exact Finset.sum_congr rfl (fun x _ ↦ (pivot_weight M a (List.mem_of_find?_eq_some hv)
        (List.find?_some hv) x).symm)
    next hv =>
      rw [ih, mass_compact, mass, Finset.mul_sum]
      have hn : ∀ a ∈ M.rows, a.head = false := by simpa using List.find?_eq_none.mp hv
      exact Finset.sum_congr rfl (fun x _ ↦ (loose_weight M hn x).symm)

theorem weight_values {ι} (M : Model ι) (x : ι → Bool) : weight M x = 0 ∨ weight M x = 1 ∨ weight M x = -1 := by
  unfold weight TernaryCollect.gated TernaryCollect.sign
  cases support M.rows x <;> cases M.phase.eval x <;> decide

theorem signed_power (n : ℕ) (M : Model (Fin n)) :
    evaluate n M = 0 ∨ ∃ k ≤ n, evaluate n M = (2:ℤ)^k ∨ evaluate n M = -(2:ℤ)^k := by
  induction n with
  | zero =>
    rcases weight_values M Fin.elim0 with h|h|h
    · exact Or.inl h
    · exact Or.inr ⟨0,le_rfl,Or.inl (by simpa [evaluate] using h)⟩
    · exact Or.inr ⟨0,le_rfl,Or.inr (by simpa [evaluate] using h)⟩
  | succ n ih =>
    rw [evaluate]
    split
    next a _ =>
      rcases ih (M.sub (insertHead (a.sub off))).compact with h|⟨k,hk,h⟩
      · exact Or.inl h
      · exact Or.inr ⟨k,by omega,h⟩
    next _ =>
      rcases ih (eliminateLoose M).compact with h|⟨k,hk,h|h⟩
      · exact Or.inl (by rw [h,mul_zero])
      · exact Or.inr ⟨k+1,by omega,Or.inl (by rw [h,pow_succ,mul_comm])⟩
      · exact Or.inr ⟨k+1,by omega,Or.inr (by rw [h,pow_succ]; ring)⟩

#print axioms evaluate_correct
#print axioms signed_power
end BooleanGauss
