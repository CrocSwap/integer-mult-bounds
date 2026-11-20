import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.LinearCombination
import Nov15.FutureAttr

/-!
FUTUREATTRT (lane LEANBOWTIE, part 1).  Kernel-only: no sorry / native_decide / new axioms.

TRANSPOSE for the R side (UP.md sec 4, class P).  Syntactic runs `List Op` (every chart move
records its old and new chart).  The adjoint run is `rev`: reversed order, `ADD d += l*e ↦ e += l*d`,
chart `C ↦ C^⊥` (old and new swapped), `INIT ↦ INIT` (the projection `1 - E_rr` is symmetric;
"owned start = 0 / discard at the end" is the block restriction, which transposes to itself).
Results:
 * `Runs` (legal runs, publics ascend, owned cost): `Runs.transpose`: the adjoint of a legal run is
   a legal run of the same type (same `P`), with the same cost (`dim D^⊥ - dim C^⊥ = dim D - dim C`).
 * `effect (rev ops) = (effect ops)ᵀ` : the adjoint delivers exactly the transposed operator.
 * `ARunL` = `FutureAttr.ARun` indexed by its op list; forgets to `ARun`; value law `v = effect · v0`.
 * CLASS P := the adjoint run is an `ARunL` (class F = GTD + cold intake) of the swapped problem.
 * `mass_le_R_P`: for a class P run, `mass(receipts) ≤ R`; `R_ge_of_wall_P` with `Wall` as hypothesis.
-/

set_option linter.unusedSectionVars false
set_option linter.unusedVariables false

namespace FutureAttrT
open FutureAttr Module Submodule Finset Function PriceLemma Matrix

/-! ## ops, legal runs, transposition -/
section Ops
variable {K : Type*} [Field K] {ι : Type*} [DecidableEq ι] {n : ℕ}

inductive Op (K : Type*) (ι : Type*) (n : ℕ)
  | add (d e : ι) (l : K)
  | init (r : ι)
  | down (r : ι) (C D : Chart n)
  | upOwn (r : ι) (C D : Chart n)
  | upPub (r : ι) (C D : Chart n)

/-- transposed op: `ADD d += l e ↦ e += l d`, charts to their duals with old/new swapped. -/
noncomputable def Op.tr : Op K ι n → Op K ι n
  | .add d e l => .add e d l
  | .init r => .init r
  | .down r C D => .down r (perp D) (perp C)
  | .upOwn r C D => .upOwn r (perp D) (perp C)
  | .upPub r C D => .upPub r (perp D) (perp C)

/-- the adjoint (reversed, transposed) run -/
noncomputable def rev (ops : List (Op K ι n)) : List (Op K ι n) := (ops.map Op.tr).reverse

/-- cost of a single op -/
noncomputable def opc : Op K ι n → ℕ
  | .upOwn _ C D => finrank (ZMod 2) D - finrank (ZMod 2) C
  | _ => 0

noncomputable def costOf (ops : List (Op K ι n)) : ℕ := (ops.map opc).sum

lemma costOf_append (a b : List (Op K ι n)) : costOf (a ++ b) = costOf a + costOf b := by
  simp [costOf]

/-- legal runs on charts: `P` publics (only ascend), owned registers may also descend (free);
ADD needs `d ≠ e` and `chart d ≤ chart e`; the cost counts owned ascents. -/
inductive Runs (P : Finset ι) :
    List (Op K ι n) → (ι → Chart n) → (ι → Chart n) → ℕ → Prop
  | nil (ch : ι → Chart n) : Runs P [] ch ch 0
  | add {ops ch ch' c} (d e : ι) (l : K) (hne : d ≠ e) (hch : ch' d ≤ ch' e) :
      Runs P ops ch ch' c → Runs P (ops ++ [Op.add d e l]) ch ch' c
  | init {ops ch ch' c} (r : ι) (hr : r ∉ P) :
      Runs P ops ch ch' c → Runs P (ops ++ [Op.init r]) ch ch' c
  | down {ops ch ch' c} (r : ι) (C D : Chart n) (hr : r ∉ P) (hC : ch' r = C) (h : D ≤ C) :
      Runs P ops ch ch' c → Runs P (ops ++ [Op.down r C D]) ch (update ch' r D) c
  | upOwn {ops ch ch' c} (r : ι) (C D : Chart n) (hr : r ∉ P) (hC : ch' r = C) (h : C ≤ D) :
      Runs P ops ch ch' c →
      Runs P (ops ++ [Op.upOwn r C D]) ch (update ch' r D) (c + (finrank (ZMod 2) D - finrank (ZMod 2) C))
  | upPub {ops ch ch' c} (r : ι) (C D : Chart n) (hr : r ∈ P) (hC : ch' r = C) (h : C ≤ D) :
      Runs P ops ch ch' c → Runs P (ops ++ [Op.upPub r C D]) ch (update ch' r D) c

theorem Runs.trans {P : Finset ι} {a b : List (Op K ι n)} {ch ch' ch'' : ι → Chart n} {c1 c2 : ℕ}
    (h1 : Runs P a ch ch' c1) (h2 : Runs P b ch' ch'' c2) : Runs P (a ++ b) ch ch'' (c1 + c2) := by
  revert h1
  induction h2 with
  | nil => intro h1; simpa using h1
  | add d e l hne hch _ ih => intro h1; rw [← List.append_assoc]; exact Runs.add d e l hne hch (ih h1)
  | init r hr _ ih => intro h1; rw [← List.append_assoc]; exact Runs.init r hr (ih h1)
  | down r C D hr hC h _ ih => intro h1; rw [← List.append_assoc]; exact Runs.down r C D hr hC h (ih h1)
  | upOwn r C D hr hC h _ ih =>
    intro h1; rw [← List.append_assoc, ← add_assoc]; exact Runs.upOwn r C D hr hC h (ih h1)
  | upPub r C D hr hC h _ ih => intro h1; rw [← List.append_assoc]; exact Runs.upPub r C D hr hC h (ih h1)

theorem Runs.cost_eq {P : Finset ι} {ops : List (Op K ι n)} {ch ch' : ι → Chart n} {c : ℕ}
    (h : Runs P ops ch ch' c) : c = costOf ops := by
  induction h with
  | nil => simp [costOf]
  | add d e l hne hch _ ih => rw [costOf_append]; simp [ih, costOf, opc]
  | init r hr _ ih => rw [costOf_append]; simp [ih, costOf, opc]
  | down r C D hr hC h _ ih => rw [costOf_append]; simp [ih, costOf, opc]
  | upOwn r C D hr hC h _ ih => rw [costOf_append]; simp [ih, costOf, opc]
  | upPub r C D hr hC h _ ih => rw [costOf_append]; simp [ih, costOf, opc]

/-- dimension of the dual chart -/
lemma dim_perp_sub {C D : Chart n} (h : C ≤ D) :
    finrank (ZMod 2) (perp C : Chart n) - finrank (ZMod 2) (perp D : Chart n) =
      finrank (ZMod 2) D - finrank (ZMod 2) C := by
  have h1 := finrank_perp (K := ZMod 2) (n := n) C
  have h2 := finrank_perp (K := ZMod 2) (n := n) D
  have h3 := finrank_le_n (K := ZMod 2) (n := n) D
  have h4 : finrank (ZMod 2) C ≤ finrank (ZMod 2) D := Submodule.finrank_mono h
  omega

/-- TRANSPOSITION: the adjoint of a legal run is a legal run of the same type with the same cost. -/
theorem Runs.transpose {P : Finset ι} {ops : List (Op K ι n)} {ch ch' : ι → Chart n} {c : ℕ}
    (h : Runs P ops ch ch' c) :
    Runs P (rev ops) (fun i => perp (ch' i)) (fun i => perp (ch i)) c := by
  induction h with
  | nil => exact Runs.nil _
  | @add ops ch ch' c d e l hne hch _ ih =>
    have step : Runs (K := K) P [Op.add e d l] (fun i => perp (ch' i)) (fun i => perp (ch' i)) 0 := by
      simpa using Runs.add (P := P) (ops := []) e d l (Ne.symm hne)
        (show (perp (ch' e) : Chart n) ≤ perp (ch' d) from perp_anti hch) (Runs.nil _)
    have := step.trans ih
    simpa [rev, Op.tr] using this
  | @init ops ch ch' c r hr _ ih =>
    have step : Runs (K := K) P [Op.init r] (fun i => perp (ch' i)) (fun i => perp (ch' i)) 0 := by
      simpa using Runs.init (K := K) (P := P) (ops := []) (ch := fun i => perp (ch' i))
        (ch' := fun i => perp (ch' i)) (c := 0) r hr (Runs.nil _)
    have := step.trans ih
    simpa [rev, Op.tr] using this
  | @down ops ch ch' c r C D hr hC hD _ ih =>
    have step : Runs (K := K) P [Op.down r (perp D) (perp C)] (fun i => perp (update ch' r D i))
        (fun i => perp (ch' i)) 0 := by
      have hu : (fun i => (perp (ch' i) : Chart n)) =
          update (fun i => (perp (update ch' r D i) : Chart n)) r (perp C) := by
        funext i
        by_cases hi : i = r
        · subst hi; simp [hC]
        · simp [hi]
      rw [hu]
      simpa using Runs.down (P := P) (ops := []) (ch := fun i => perp (update ch' r D i))
        (ch' := fun i => perp (update ch' r D i)) (c := 0) r (perp D) (perp C) hr
        (by simp) (perp_anti hD) (Runs.nil _)
    have := step.trans ih
    simpa [rev, Op.tr] using this
  | @upOwn ops ch ch' c r C D hr hC hD _ ih =>
    have step : Runs (K := K) P [Op.upOwn r (perp D) (perp C)] (fun i => perp (update ch' r D i))
        (fun i => perp (ch' i)) (finrank (ZMod 2) D - finrank (ZMod 2) C) := by
      have hu : (fun i => (perp (ch' i) : Chart n)) =
          update (fun i => (perp (update ch' r D i) : Chart n)) r (perp C) := by
        funext i
        by_cases hi : i = r
        · subst hi; simp [hC]
        · simp [hi]
      rw [hu]
      have := Runs.upOwn (K := K) (P := P) (ops := []) (ch := fun i => perp (update ch' r D i))
        (ch' := fun i => perp (update ch' r D i)) (c := 0) r (perp D) (perp C) hr
        (by simp) (perp_anti hD) (Runs.nil _)
      rw [dim_perp_sub hD] at this
      simpa using this
    have := step.trans ih
    rw [add_comm] at this
    simpa [rev, Op.tr] using this
  | @upPub ops ch ch' c r C D hr hC hD _ ih =>
    have step : Runs (K := K) P [Op.upPub r (perp D) (perp C)] (fun i => perp (update ch' r D i))
        (fun i => perp (ch' i)) 0 := by
      have hu : (fun i => (perp (ch' i) : Chart n)) =
          update (fun i => (perp (update ch' r D i) : Chart n)) r (perp C) := by
        funext i
        by_cases hi : i = r
        · subst hi; simp [hC]
        · simp [hi]
      rw [hu]
      simpa using Runs.upPub (P := P) (ops := []) (ch := fun i => perp (update ch' r D i))
        (ch' := fun i => perp (update ch' r D i)) (c := 0) r (perp D) (perp C) hr
        (by simp) (perp_anti hD) (Runs.nil _)
    have := step.trans ih
    simpa [rev, Op.tr] using this

end Ops


/-! ## effect operators: the adjoint delivers the transposed operator -/
section Effect
variable {K : Type*} [Field K] {ι : Type*} [DecidableEq ι] [Fintype ι] {n : ℕ}

/-- elementary matrix `l · e_{de}` -/
def E (d e : ι) (l : K) : Matrix ι ι K := Matrix.of fun r c => if r = d ∧ c = e then l else 0

lemma E_transpose (d e : ι) (l : K) : (E d e l)ᵀ = E e d l := by
  ext r c; simp [E, and_comm]

lemma E_mul_apply {ω : Type*} (d e : ι) (l : K) (V : Matrix ι ω K) (r : ι) (j : ω) :
    (E d e l * V) r j = if r = d then l * V e j else 0 := by
  simp only [Matrix.mul_apply, E, Matrix.of_apply]
  by_cases hr : r = d
  · simp [hr]
  · simp [hr]

/-- one op acting on the register space -/
noncomputable def opMat : Op K ι n → Matrix ι ι K
  | .add d e l => 1 + E d e l
  | .init r => 1 - E r r 1
  | _ => 1

lemma opMat_tr (op : Op K ι n) : opMat (Op.tr op) = (opMat op)ᵀ := by
  cases op <;> simp [opMat, Op.tr, E_transpose, Matrix.transpose_add, Matrix.transpose_sub,
    Matrix.transpose_one]

/-- the total effect of a run (last op leftmost) -/
noncomputable def effect (ops : List (Op K ι n)) : Matrix ι ι K :=
  ops.foldl (fun T op => opMat op * T) 1

lemma foldl_eff (l : List (Op K ι n)) (T : Matrix ι ι K) :
    l.foldl (fun T op => opMat op * T) T = effect l * T := by
  induction l generalizing T with
  | nil => simp [effect]
  | cons a l ih =>
    simp only [List.foldl_cons, effect]
    rw [ih, ih (opMat a * 1)]
    simp [Matrix.mul_assoc]

lemma effect_nil : effect ([] : List (Op K ι n)) = 1 := rfl

lemma effect_cons (a : Op K ι n) (l : List (Op K ι n)) : effect (a :: l) = effect l * opMat a := by
  simp only [effect, List.foldl_cons]
  rw [foldl_eff]; simp [effect]

lemma effect_append (a b : List (Op K ι n)) : effect (a ++ b) = effect b * effect a := by
  induction a with
  | nil => simp [effect_nil]
  | cons x a ih => rw [List.cons_append, effect_cons, ih, effect_cons, Matrix.mul_assoc]

lemma effect_snoc (a : List (Op K ι n)) (op : Op K ι n) :
    effect (a ++ [op]) = opMat op * effect a := by
  rw [effect_append, effect_cons, effect_nil, Matrix.one_mul]

/-- the adjoint run delivers the transposed operator -/
theorem effect_rev (ops : List (Op K ι n)) : effect (rev ops) = (effect ops)ᵀ := by
  induction ops with
  | nil => simp [rev, effect_nil]
  | cons a l ih =>
    have : rev (a :: l) = rev l ++ [Op.tr a] := by simp [rev]
    rw [this, effect_snoc, ih, opMat_tr, effect_cons, Matrix.transpose_mul]

end Effect

/-! ## `ARun` indexed by its op list -/
section ARunL
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ} [Fintype τ] [DecidableEq ι]

/-- `FutureAttr.ARun` (class F: GTD + cold intake as constructor premises) indexed by the op list. -/
inductive ARunL (P : Finset ι) (X : τ → ι) (xs ys : τ → ω) (Fy : τ → τ → K)
    (q : τ → Fin n → ZMod 2) (s0 : St K n ι ω) :
    List (Op K ι n) → St K n ι ω → Bk K τ ω ι n → ℕ → Prop
  | refl : ARunL P X xs ys Fy q s0 [] s0 Bk.init 0
  | add {ops s bk cost} (d e : ι) (l : K) (hne : d ≠ e) (hch : s.ch d ≤ s.ch e)
      (hgtd : d ∉ P → bk.dep d = false)
      (hcold : d ∉ P → ∀ u, l * eff xs ys Fy (s.v e) u ≠ 0 → ∀ a ∈ s.ch d, a ⬝ᵥ q u = 0) :
      ARunL P X xs ys Fy q s0 ops s bk cost →
      ARunL P X xs ys Fy q s0 (ops ++ [Op.add d e l])
        { s with v := fun r j => s.v r j + if r = d then l * s.v e j else 0 }
        { bk with
          W := fun r t => bk.W r t + if r = e then l * (tv X d t - bk.W d t) else 0
          A := fun r => if r = d ∧ d ∉ P then bk.A d ⊓ s.ch d else bk.A r
          B := fun r => if r = e ∧ d ∈ P ∧ e ∉ P then bk.B e ⊔ s.ch e else bk.B r
          dep := fun r => if r = e ∧ d ∈ P ∧ e ∉ P then true else bk.dep r } cost
  | init {ops s bk cost} (r : ι) (hr : r ∉ P) :
      ARunL P X xs ys Fy q s0 ops s bk cost →
      ARunL P X xs ys Fy q s0 (ops ++ [Op.init r])
        { s with v := fun r' j => if r' = r then 0 else s.v r' j }
        { W := fun r' t => if r' = r then 0 else bk.W r' t
          A := fun r' => if r' = r then ⊤ else bk.A r'
          B := fun r' => if r' = r then ⊥ else bk.B r'
          dep := fun r' => if r' = r then false else bk.dep r'
          lc := fun r' => if r' = r then 0 else bk.lc r'
          closed := ⟨bk.W r, s.v r, bk.A r, bk.B r, bk.lc r⟩ :: bk.closed } cost
  | down {ops s bk cost} (r : ι) (C D : Chart n) (hr : r ∉ P) (hC : s.ch r = C) (h : D ≤ s.ch r) :
      ARunL P X xs ys Fy q s0 ops s bk cost →
      ARunL P X xs ys Fy q s0 (ops ++ [Op.down r C D])
        { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost
  | upOwn {ops s bk cost} (r : ι) (C D : Chart n) (hr : r ∉ P) (hC : s.ch r = C) (h : s.ch r ≤ D) :
      ARunL P X xs ys Fy q s0 ops s bk cost →
      ARunL P X xs ys Fy q s0 (ops ++ [Op.upOwn r C D])
        { s with ch := fun r' => if r' = r then D else s.ch r' }
        { bk with lc := fun r' =>
            if r' = r then bk.lc r + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)) else bk.lc r' }
        (cost + (finrank (ZMod 2) D - finrank (ZMod 2) (s.ch r)))
  | upPub {ops s bk cost} (r : ι) (C D : Chart n) (hr : r ∈ P) (hC : s.ch r = C) (h : s.ch r ≤ D) :
      ARunL P X xs ys Fy q s0 ops s bk cost →
      ARunL P X xs ys Fy q s0 (ops ++ [Op.upPub r C D])
        { s with ch := fun r' => if r' = r then D else s.ch r' } bk cost

variable {P : Finset ι} {X : τ → ι} {xs ys : τ → ω} {Fy : τ → τ → K}
  {q : τ → Fin n → ZMod 2} {s0 : St K n ι ω}

/-- forget the op index: an `ARunL` is an `ARun` -/
theorem ARunL.toARun {ops : List (Op K ι n)} {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : ARunL P X xs ys Fy q s0 ops s bk cost) : ARun P X xs ys Fy q s0 s bk cost := by
  induction h with
  | refl => exact ARun.refl
  | add d e l hne hch hgtd hcold _ ih => exact ARun.add d e l hne hch hgtd hcold ih
  | init r hr _ ih => exact ARun.init r hr ih
  | down r C D hr hC h _ ih => exact ARun.down r D hr h ih
  | upOwn r C D hr hC h _ ih => exact ARun.upOwn r D hr h ih
  | upPub r C D hr hC h _ ih => exact ARun.upPub r D hr h ih

theorem ARunL.cost_eq {ops : List (Op K ι n)} {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : ARunL P X xs ys Fy q s0 ops s bk cost) : cost = costOf ops := by
  induction h with
  | refl => simp [costOf]
  | add d e l hne hch hgtd hcold _ ih => rw [costOf_append]; simp [ih, costOf, opc]
  | init r hr _ ih => rw [costOf_append]; simp [ih, costOf, opc]
  | down r C D hr hC h _ ih => rw [costOf_append]; simp [ih, costOf, opc]
  | upOwn r C D hr hC h _ ih => rw [costOf_append]; subst hC; simp [ih, costOf, opc]
  | upPub r C D hr hC h _ ih => rw [costOf_append]; simp [ih, costOf, opc]

variable [Fintype ι]

/-- value law: the register values are the run's effect applied to the start values -/
theorem ARunL.val {ops : List (Op K ι n)} {s : St K n ι ω} {bk : Bk K τ ω ι n} {cost : ℕ}
    (h : ARunL P X xs ys Fy q s0 ops s bk cost) :
    (Matrix.of s.v : Matrix ι ω K) = effect ops * Matrix.of s0.v := by
  induction h with
  | refl => simp [effect_nil]
  | @add ops s bk cost d e l hne hch hgtd hcold _ ih =>
    rw [effect_snoc, Matrix.mul_assoc, ← ih]
    ext r j
    simp [opMat, Matrix.add_mul, E_mul_apply]
  | @init ops s bk cost r hr _ ih =>
    rw [effect_snoc, Matrix.mul_assoc, ← ih]
    ext r' j
    simp [opMat, Matrix.sub_mul, E_mul_apply]
    by_cases hh : r' = r <;> simp [hh]
  | down r C D hr hC h _ ih => rw [effect_snoc]; simpa [opMat] using ih
  | upOwn r C D hr hC h _ ih => rw [effect_snoc]; simpa [opMat] using ih
  | upPub r C D hr hC h _ ih => rw [effect_snoc]; simpa [opMat] using ih

end ARunL

/-! ## transposed decoders -/
section Swap
variable {K : Type*} [Field K] {τ : Type*} {n : ℕ} [Fintype τ]

/-- swapping the two vectors of a row does not change its price (Gram transpose) -/
lemma price_swap (q : τ → Fin n → ZMod 2) (ρ : DRow K τ) :
    price q (⟨ρ.u, ρ.w⟩ : DRow K τ) = price q ρ := by
  classical
  unfold price
  have h : gram (fun s : {s // ρ.u s ≠ 0} => q s.1) (fun t : {t // ρ.w t ≠ 0} => q t.1) =
      (gram (fun t : {t // ρ.w t ≠ 0} => q t.1) (fun s : {s // ρ.u s ≠ 0} => q s.1))ᵀ := by
    ext s t; simp [gram, dotProduct_comm]
  show (gram (fun s : {s // ρ.u s ≠ 0} => q s.1) (fun t : {t // ρ.w t ≠ 0} => q t.1)).rank = _
  rw [h, Matrix.rank_transpose]

/-- a decoder of the transposed pattern gives a decoder of the pattern, same price. -/
lemma isDec_swap (q : τ → Fin n → ZMod 2) (Rec : τ → τ → K) (rows : List (DRow K τ))
    (h : IsDec q (fun t u => Rec u t) rows) :
    IsDec q Rec (rows.map fun ρ => (⟨ρ.u, ρ.w⟩ : DRow K τ)) ∧
      ((rows.map fun ρ => (⟨ρ.u, ρ.w⟩ : DRow K τ)).map (price q)).sum = (rows.map (price q)).sum := by
  constructor
  · intro t s hts
    have hst : q s ⬝ᵥ q t = 1 := by rw [dotProduct_comm]; exact hts
    have := h s t hst
    simp only [List.map_map, Function.comp_def] at this ⊢
    rw [← this]
    congr 1
    apply List.map_congr_left
    intro ρ _; ring
  · simp only [List.map_map, Function.comp_def]
    congr 1
    apply List.map_congr_left
    intro ρ _; exact price_swap q ρ

end Swap

/-! ## class P: the adjoint run is class F -/
section ClassP
variable {K : Type*} [Field K] {τ ι ω : Type*} {n : ℕ} [Fintype τ] [Fintype ι] [DecidableEq ι]

/-- forward receipts `final(X_t)[y_u] - start(X_t)[y_u]` through the run's effect operator -/
noncomputable def receipts (ops : List (Op K ι n)) (v0 : ι → ω → K) (X : τ → ι) (ys : τ → ω) :
    τ → τ → K :=
  fun t u => (effect ops * Matrix.of v0) (X t) (ys u) - v0 (X t) (ys u)

/-- CLASS P (UP.md sec 4): the adjoint run `rev ops` is a class-F run (GTD + cold intake) of the
swapped problem (targets `Yr`, symbols swapped, start charts `(final charts)^⊥`). -/
def ClassP (P : Finset ι) (X Yr : τ → ι) (xs ys : τ → ω) (Fy' : τ → τ → K)
    (q : τ → Fin n → ZMod 2) (s0' : St K n ι ω) (ops : List (Op K ι n)) : Prop :=
  ∃ (s' : St K n ι ω) (bk' : Bk K τ ω ι n) (c' : ℕ),
    ARunL P Yr ys xs Fy' q s0' (rev ops) s' bk' c'

/-- HEADLINE (transposed future attribution): a legal run of cost `c` whose adjoint is class F has a
decoder of its receipts with total price `≤ c`.  The class-F data of the adjoint (`hfx`..`hbal`,
final data of the adjoint run, i.e. the "dual-cold" conditions) and the identity start
(`hidx`, `hidy`: public `r` holds exactly the symbol of its port) are explicit hypotheses. -/
theorem decoder_of_classP (P : Finset ι) (X Yr : τ → ι) (xs ys : τ → ω) (Fy' : τ → τ → K)
    (q : τ → Fin n → ZMod 2) (v0 : ι → ω → K) (ch0 ch1 : ι → Chart n)
    (ops : List (Op K ι n)) {c : ℕ} (hrun : Runs P ops ch0 ch1 c)
    (s0' : St K n ι ω) (hs0ch : s0'.ch = fun i => perp (ch1 i)) (hs0v : s0'.v = v0)
    {s' : St K n ι ω} {bk' : Bk K τ ω ι n} {c' : ℕ}
    (hadj : ARunL P Yr ys xs Fy' q s0' (rev ops) s' bk' c')
    (hYP : ∀ t, Yr t ∈ P) (hYinj : Function.Injective Yr)
    (hYch : ∀ t, ∀ a ∈ ch1 (Yr t), a ⬝ᵥ q t = 0)
    (h0 : ∀ r ∉ P, v0 r = 0)
    (hfx : ∀ r ∈ P, ∀ u, s'.v r (ys u) = if r = Yr u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ Yr u) → ∀ u, s'.v r (xs u) ≠ 0 → ∀ a ∈ s'.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s'.v (Yr u) (xs u') = Fy' u u')
    (hbal : ∀ t u, s'.v (Yr t) (ys u) = v0 (Yr t) (ys u))
    (hidx : ∀ r u, v0 r (xs u) = if r = X u then 1 else 0)
    (hidy : ∀ r t, v0 r (ys t) = if r = Yr t then 1 else 0)
    (hXY : ∀ t u, X u ≠ Yr t) :
    c = c' ∧ ∃ rows : List (DRow K τ), IsDec q (receipts ops v0 X ys) rows ∧
      (rows.map (price q)).sum ≤ c := by
  have hcc : c = c' := by
    have h1 := hrun.transpose.cost_eq
    have h2 := hadj.cost_eq
    rw [h1, h2]
  have hq : ∀ t, q t ∈ s0'.ch (Yr t) := by
    intro t; rw [hs0ch]; exact (mem_perp.2 (hYch t))
  have h0' : ∀ r ∉ P, s0'.v r = 0 := by intro r hr; rw [hs0v]; exact h0 r hr
  have hbal' : ∀ t u, s'.v (Yr t) (ys u) = s0'.v (Yr t) (ys u) := by
    intro t u; rw [hs0v]; exact hbal t u
  obtain ⟨rows, hd, hle⟩ := attribution_decoder ys xs Fy' q P Yr s0' hYP hYinj hq h0' hadj.toARun
    hfx hfy hfyX hbal'
  -- the adjoint receipts are the transposed forward receipts
  have hval : ∀ r j, s'.v r j = ∑ r', (effect ops) r' r * v0 r' j := by
    intro r j
    have := congrFun (congrFun hadj.val r) j
    simp only [Matrix.of_apply] at this
    rw [this, effect_rev, Matrix.mul_apply]
    simp [hs0v, Matrix.transpose_apply]
  have hrec : ∀ t u, (fun t u => s'.v (Yr t) (xs u) - s0'.v (Yr t) (xs u)) t u =
      (fun t u => receipts ops v0 X ys u t) t u := by
    intro t u
    simp only [receipts, Matrix.mul_apply, Matrix.of_apply, hval, hs0v]
    have e1 : ∑ r', (effect ops) r' (Yr t) * v0 r' (xs u) = (effect ops) (X u) (Yr t) := by
      simp [hidx]
    have e2 : ∑ r', (effect ops) (X u) r' * v0 r' (ys t) = (effect ops) (X u) (Yr t) := by
      simp [hidy]
    have e3 : v0 (Yr t) (xs u) = 0 := by simp [hidx, (hXY t u).symm]
    have e4 : v0 (X u) (ys t) = 0 := by simp [hidy, hXY t u]
    rw [e1, e2, e3, e4]
  have hrecF : (fun t u => s'.v (Yr t) (xs u) - s0'.v (Yr t) (xs u)) =
      (fun t u => receipts ops v0 X ys u t) := by
    funext t u; exact hrec t u
  rw [hrecF] at hd
  obtain ⟨hd2, hp⟩ := isDec_swap q (receipts ops v0 X ys) rows hd
  refine ⟨hcc, _, hd2, ?_⟩
  rw [hp]; rw [hcc]; exact hle

/-- `R ≥ m(receipts)` for class P runs. -/
theorem mass_le_R_P (P : Finset ι) (X Yr : τ → ι) (xs ys : τ → ω) (Fy' : τ → τ → K)
    (q : τ → Fin n → ZMod 2) (v0 : ι → ω → K) (ch0 ch1 : ι → Chart n)
    (ops : List (Op K ι n)) {c : ℕ} (hrun : Runs P ops ch0 ch1 c)
    (s0' : St K n ι ω) (hs0ch : s0'.ch = fun i => perp (ch1 i)) (hs0v : s0'.v = v0)
    {s' : St K n ι ω} {bk' : Bk K τ ω ι n} {c' : ℕ}
    (hadj : ARunL P Yr ys xs Fy' q s0' (rev ops) s' bk' c')
    (hYP : ∀ t, Yr t ∈ P) (hYinj : Function.Injective Yr)
    (hYch : ∀ t, ∀ a ∈ ch1 (Yr t), a ⬝ᵥ q t = 0)
    (h0 : ∀ r ∉ P, v0 r = 0)
    (hfx : ∀ r ∈ P, ∀ u, s'.v r (ys u) = if r = Yr u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ Yr u) → ∀ u, s'.v r (xs u) ≠ 0 → ∀ a ∈ s'.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s'.v (Yr u) (xs u') = Fy' u u')
    (hbal : ∀ t u, s'.v (Yr t) (ys u) = v0 (Yr t) (ys u))
    (hidx : ∀ r u, v0 r (xs u) = if r = X u then 1 else 0)
    (hidy : ∀ r t, v0 r (ys t) = if r = Yr t then 1 else 0)
    (hXY : ∀ t u, X u ≠ Yr t) :
    mass q (receipts ops v0 X ys) ≤ c := by
  obtain ⟨_, rows, hd, hle⟩ := decoder_of_classP P X Yr xs ys Fy' q v0 ch0 ch1 ops hrun s0' hs0ch hs0v
    hadj hYP hYinj hYch h0 hfx hfy hfyX hbal hidx hidy hXY
  exact le_trans (mass_le hd) hle

/-- with the decoder wall as an explicit hypothesis (e.g. `N = 56` at Q96): `R ≥ N` for class P runs. -/
theorem R_ge_of_wall_P (N : ℕ) (P : Finset ι) (X Yr : τ → ι) (xs ys : τ → ω) (Fy' : τ → τ → K)
    (q : τ → Fin n → ZMod 2) (v0 : ι → ω → K) (ch0 ch1 : ι → Chart n)
    (ops : List (Op K ι n)) {c : ℕ} (hrun : Runs P ops ch0 ch1 c)
    (s0' : St K n ι ω) (hs0ch : s0'.ch = fun i => perp (ch1 i)) (hs0v : s0'.v = v0)
    {s' : St K n ι ω} {bk' : Bk K τ ω ι n} {c' : ℕ}
    (hadj : ARunL P Yr ys xs Fy' q s0' (rev ops) s' bk' c')
    (hYP : ∀ t, Yr t ∈ P) (hYinj : Function.Injective Yr)
    (hYch : ∀ t, ∀ a ∈ ch1 (Yr t), a ⬝ᵥ q t = 0)
    (h0 : ∀ r ∉ P, v0 r = 0)
    (hfx : ∀ r ∈ P, ∀ u, s'.v r (ys u) = if r = Yr u then 1 else 0)
    (hfy : ∀ r ∈ P, (∀ u, r ≠ Yr u) → ∀ u, s'.v r (xs u) ≠ 0 → ∀ a ∈ s'.ch r, a ⬝ᵥ q u = 0)
    (hfyX : ∀ u u', s'.v (Yr u) (xs u') = Fy' u u')
    (hbal : ∀ t u, s'.v (Yr t) (ys u) = v0 (Yr t) (ys u))
    (hidx : ∀ r u, v0 r (xs u) = if r = X u then 1 else 0)
    (hidy : ∀ r t, v0 r (ys t) = if r = Yr t then 1 else 0)
    (hXY : ∀ t u, X u ≠ Yr t)
    (hwall : Wall q (receipts ops v0 X ys) N) : N ≤ c := by
  obtain ⟨_, rows, hd, hle⟩ := decoder_of_classP P X Yr xs ys Fy' q v0 ch0 ch1 ops hrun s0' hs0ch hs0v
    hadj hYP hYinj hYch h0 hfx hfy hfyX hbal hidx hidy hXY
  exact le_trans (hwall rows hd) hle

end ClassP

/-! ## Non-vacuity: the one-port toy of `FutureAttr.Toy`, read as a class P run.
Forward: `O += Y` (cold intake at chart ⊥), `O` ascends ⊥ → ⊤ (cost 1), `X += -O`.
The adjoint is `O += -X`, `O` ascends (dual charts), `Y += O`: a class-F run of the swapped problem
(targets = the `Y` register, source = the `X` register). -/
namespace ToyP
open FutureAttr.Toy

lemma perp_bot' {n : ℕ} : (perp (⊥ : Chart n) : Chart n) = ⊤ := by
  rw [eq_top_iff]; intro x _; rw [mem_perp]; intro y hy
  rw [Submodule.mem_bot] at hy; subst hy; simp

lemma perp_top' {n : ℕ} : (perp (⊤ : Chart n) : Chart n) = ⊥ := by
  have := perp_perp (K := ZMod 2) (n := n) (⊥ : Chart n)
  rw [perp_bot'] at this; exact this

def toyOps : List (Op ℚ (Fin 3) 1) :=
  [Op.add 2 1 1, Op.upOwn 2 ⊥ ⊤, Op.add 0 2 (-1)]

noncomputable def ch1 : Fin 3 → Chart 1 := update st0.ch 2 ⊤

def Yr : Unit → Fin 3 := fun _ => 1

def Fy' : Unit → Unit → ℚ := fun _ _ => -1

/-- adjoint start state: values as the forward start, charts dual to the forward final charts -/
noncomputable def s0' : St ℚ 1 (Fin 3) (Fin 2) where
  ch := fun i => perp (ch1 i)
  v := st0.v

lemma ch1_eval : ch1 0 = ⊤ ∧ ch1 1 = ⊥ ∧ ch1 2 = ⊤ := by
  refine ⟨?_, ?_, ?_⟩ <;> simp [ch1, st0]

theorem toy_forward : Runs Pub toyOps st0.ch ch1 1 := by
  have h1 := Runs.add (K := ℚ) (P := Pub) (ops := []) (ch := st0.ch) (ch' := st0.ch) (c := 0) 2 1 1
    (by decide) (by simp [st0]) (Runs.nil _)
  have h2 := Runs.upOwn (K := ℚ) (P := Pub) 2 ⊥ ⊤ (by decide) (by simp [st0]) bot_le h1
  have h3 := Runs.add (K := ℚ) (P := Pub) 0 2 (-1) (by decide)
    (by simp [st0]) h2
  have hd : finrank (ZMod 2) (⊤ : Chart 1) - finrank (ZMod 2) (⊥ : Chart 1) = 1 := by simp
  rw [hd] at h3
  exact h3


theorem toy_classP_headline :
    mass q1 (receipts toyOps st0.v Xr ysym) ≤ 1 ∧
      receipts toyOps st0.v Xr ysym () () = -1 ∧
      ∃ (s' : St ℚ 1 (Fin 3) (Fin 2)) (bk' : Bk ℚ Unit (Fin 2) (Fin 3) 1) (c' : ℕ),
        ARunL Pub Yr ysym xsym Fy' q1 s0' (rev toyOps) s' bk' c' := by
  have hch := ch1_eval
  have e0 : (s0'.ch 0 : Chart 1) = ⊥ := by simp [s0', hch.1, perp_top']
  have e1 : (s0'.ch 1 : Chart 1) = ⊤ := by simp [s0', hch.2.1, perp_bot']
  have e2 : (s0'.ch 2 : Chart 1) = ⊥ := by simp [s0', hch.2.2, perp_top']
  -- step 1: O += -X (cold intake at chart ⊥)
  have a1 := ARunL.add (P := Pub) (X := Yr) (xs := ysym) (ys := xsym) (Fy := Fy') (q := q1)
    (s0 := s0') (ops := []) (s := s0') (bk := Bk.init) (cost := 0) 2 0 (-1 : ℚ) (by decide)
    (by rw [e0, e2]) (fun _ => rfl)
    (by
      intro _ u _ a ha
      rw [e2] at ha
      have : a = 0 := by simpa using ha
      simp [this]) ARunL.refl
  -- step 2: O ascends (dual of the forward ascent)
  have a2 := ARunL.upOwn (P := Pub) (X := Yr) (xs := ysym) (ys := xsym) (Fy := Fy') (q := q1)
    (s0 := s0') (r := 2) (perp (⊤ : Chart 1)) (perp (⊥ : Chart 1)) (by decide)
    (by simp [e2, perp_top']) (by simp [e2, perp_bot']) a1
  -- step 3: Y += O
  have a3 := ARunL.add (P := Pub) (X := Yr) (xs := ysym) (ys := xsym) (Fy := Fy') (q := q1)
    (s0 := s0') 1 2 (1 : ℚ) (by decide)
    (by simp [e1, e2, perp_bot'])
    (fun h => absurd (by decide) h) (fun h => absurd (by decide) h) a2
  refine ⟨?_, ?_, _, _, _, a3⟩
  · refine le_trans (mass_le_R_P Pub Xr Yr xsym ysym Fy' q1 st0.v st0.ch ch1 toyOps toy_forward
      s0' rfl rfl a3 ?_ ?_ ?_ ?_ ?_ ?_ ?_ ?_ ?_ ?_ ?_) le_rfl
    · intro t; simp [Yr, Pub]
    · intro a b _; exact Subsingleton.elim a b
    · intro t a ha
      have : a = 0 := by simpa [Yr, hch.2.1] using ha
      simp [this]
    · intro r hr
      fin_cases r
      · simp [Pub] at hr
      · simp [Pub] at hr
      · funext j; simp [st0]
    · intro r hr u; fin_cases r <;> simp_all [Pub, st0, s0', Yr, ysym]
    · intro r hr hne u hv a ha
      fin_cases r
      · have : a = 0 := by simpa [e0] using ha
        simp [this]
      · exact absurd rfl (hne ())
      · simp [Pub] at hr
    · intro u u'; simp [st0, s0', Yr, xsym, Fy']
    · intro t u; simp [st0, s0', Yr, ysym]
    · intro r u; fin_cases r <;> simp [st0, Xr, xsym]
    · intro r t; fin_cases r <;> simp [st0, Yr, ysym]
    · intro t u; simp [Xr, Yr]
  · simp [receipts, effect_nil, effect, toyOps, opMat, Xr, ysym, st0, Matrix.mul_apply, Fin.sum_univ_three, E, Matrix.one_apply]

end ToyP

#print axioms Runs.transpose
#print axioms effect_rev
#print axioms ARunL.toARun
#print axioms ARunL.val
#print axioms decoder_of_classP
#print axioms mass_le_R_P
#print axioms R_ge_of_wall_P
#print axioms ToyP.toy_forward
#print axioms ToyP.toy_classP_headline

end FutureAttrT
