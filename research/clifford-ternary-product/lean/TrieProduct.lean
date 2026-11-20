import BellBoundary
import PhysicalBlocks

/-! This connects the high-pair-first traversal with the signed events used
in the complete literal product. The equality holds separately at every leaf. -/
namespace TrieProduct
open Finset TernaryCollect BooleanGauss BellBoundary QuadraticProduct
open scoped BigOperators

theorem tested_leaf {m : ℕ} (t : TritWord m) (f : Bits m → Bits m → ℤ) :
    (∑ x : Bits m, ∑ y : Bits m, if classify x y = t then f x y else 0) = leaf t f := by
  classical
  let g (p : Bits m × Bits m) := if classify p.1 p.2 = t then f p.1 p.2 else 0
  change (∑ x : Bits m, ∑ y : Bits m, g (x,y)) = _
  rw [← Fintype.sum_prod_type,← (pairChart m).sum_comp,Fintype.sum_sigma]
  change (∑ r : TritWord m, ∑ u : Free r → Bool,
    if classify (left r u) (right r u) = t then f (left r u) (right r u) else 0) = _
  simp [classify_expand,Finset.sum_ite_irrel,leaf]

theorem classify_snoc {m} (x y : Bits m) (a b : Bool) :
    classify (Fin.snoc x a) (Fin.snoc y b) = Fin.snoc (classify x y) (trit a b) := by
  funext i
  refine Fin.lastCases ?_ (fun j ↦ ?_) i <;> simp [classify]

theorem snoc_eq {m} (s t : TritWord m) (a b : Trit) :
    ((Fin.snoc s a : TritWord (m+1)) = (Fin.snoc t b : TritWord (m+1))) ↔ (s=t ∧ a=b) := by
  constructor
  · intro h
    exact ⟨by simpa using congrArg Fin.init h,by simpa using congrFun h (Fin.last m)⟩
  · rintro ⟨rfl,rfl⟩
    rfl

theorem high_pair_sum {m} (f : Bits (m+1) → ℤ) :
    (∑ x, f x) = (∑ y : Bits m, f (Fin.snoc y false)) + (∑ y : Bits m, f (Fin.snoc y true)) := by
  rw [← (Fin.snocEquiv (fun _ : Fin (m+1) ↦ Bool)).sum_comp,Fintype.sum_prod_type,Fintype.sum_bool]
  rw [add_comm]
  rfl

def pairDigit {m} : Trit → (Bits (m+1) → Bits (m+1) → ℤ) → Bits m → Bits m → ℤ
  | some b,f,x,y => f (Fin.snoc x b) (Fin.snoc y b)
  | none,f,x,y => f (Fin.snoc x true) (Fin.snoc y false) + f (Fin.snoc x false) (Fin.snoc y true)

theorem leaf_snoc {m} (d : Trit) (t : TritWord m) (f : Bits (m+1) → Bits (m+1) → ℤ) :
    leaf (Fin.snoc t d) f = leaf t (pairDigit d f) := by
  classical
  rw [← tested_leaf,←tested_leaf]
  rw [high_pair_sum]
  have hy (x : Bits (m+1)) := high_pair_sum (fun y ↦ if classify x y = Fin.snoc t d then f x y else 0)
  simp_rw [hy,classify_snoc,snoc_eq]
  cases d with
  | none =>
    simp only [trit,Bool.true_eq_false,Bool.false_eq_true,reduceCtorEq,↓reduceIte,
      and_false,and_true,Finset.sum_const_zero,zero_add,add_zero,pairDigit]
    simp only [←Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro x _
    apply Finset.sum_congr rfl
    intro y _
    split <;> simp_all
    ring
  | some b =>
    cases b <;> simp [trit,pairDigit]

def weave : (m : ℕ) → Bits m → Bits m → Bits (slots 0 m)
  | 0,_,_ => Fin.elim0
  | m+1,x,y => pairBits (x (Fin.last m)) (y (Fin.last m)) (weave m (Fin.init x) (Fin.init y))

theorem weave_snoc {m} (x y : Bits m) (a b : Bool) :
    weave (m+1) (Fin.snoc x a) (Fin.snoc y b) = pairBits a b (weave m x y) := by
  simp [weave]
  rfl

theorem digit_weave {m} (d : Trit) (f : Bits (slots 0 (m+1)) → ℤ) (x y : Bits m) :
    pairDigit d (fun a b ↦ f (weave (m+1) a b)) x y = bell d f (weave m x y) := by
  cases d <;> simp [pairDigit,bell,weave_snoc]

def branch : (m : ℕ) → TritWord m → Model (Fin (slots 0 m)) → ℕ × Model (Fin 0)
  | 0,_,M => (0,M)
  | m+1,t,M =>
    let step := project (t (Fin.last m)) M
    let tail := branch m (Fin.init t) step.2
    (step.1+tail.1,tail.2)

def output {m} (t : TritWord m) (M : Model (Fin (slots 0 m))) : ℤ :=
  (2:ℤ)^(branch m t M).1 * weight (branch m t M).2 Fin.elim0

theorem output_leaf {m} (t : TritWord m) (M : Model (Fin (slots 0 m))) :
    output t M = leaf t (fun x y ↦ weight M (weave m x y)) := by
  induction m with
  | zero =>
    unfold output
    simp only [branch,pow_zero,one_mul,leaf,Fintype.sum_unique,weave]
    rfl
  | succ m ih =>
    have tf := Fin.snoc_init_self t
    let d := t (Fin.last m)
    let q := project d M
    have h (x y : Bits m) : pairDigit d (fun a b ↦ weight M (weave (m+1) a b)) x y =
        (2:ℤ)^q.1 * weight q.2 (weave m x y) :=
      (digit_weave d (weight M) x y).trans (project_exact d M _)
    have hh := ih (Fin.init t) q.2
    change (2:ℤ)^(q.1+(branch m (Fin.init t) q.2).1) * weight (branch m (Fin.init t) q.2).2 Fin.elim0 = _
    rw [pow_add,mul_assoc]
    change (2:ℤ)^q.1*output (Fin.init t) q.2 = _
    rw [hh,←tf,leaf_snoc,Fin.init_snoc]
    change (2:ℤ)^q.1*leaf (Fin.init t) (fun x y ↦ weight q.2 (weave m x y)) =
      leaf (Fin.init t) (pairDigit d (fun a b ↦ weight M (weave (m+1) a b)))
    simp only [leaf, h, Finset.mul_sum]

def site (side : Bool) : (m : ℕ) → Fin m → Fin (slots 0 m)
  | 0 => Fin.elim0
  | m+1 => Fin.lastCases (motive := fun _ : Fin (m+1) ↦ Fin (slots 0 m + 2))
      (if side then 1 else 0) (fun i ↦ (site side m i).succ.succ)

theorem weave_site {m} (side : Bool) (x y : Bits m) (i : Fin m) :
    weave m x y (site side m i) = if side then y i else x i := by
  induction m with
  | zero => exact Fin.elim0 i
  | succ m ih =>
    refine Fin.lastCases ?_ (fun j ↦ ?_) i
    · cases side <;> simp only [site,Fin.lastCases_last,weave,pairBits,Bool.false_eq_true,↓reduceIte] <;> rfl
    · simpa only [site, Fin.lastCases_castSucc, weave, pairBits,Fin.cons_succ,Fin.init] using
        ih (Fin.init x) (Fin.init y) j

def joint {m} (A B : Model (Fin m)) (a b : Bool) : Model (Fin (slots 0 m)) :=
  let L := A.sub (fun j ↦ .var (site false m j))
  let R := B.sub (fun j ↦ .var (site true m j))
  ⟨L.rows++R.rows,.plus (takePhase a L.phase) (takePhase b R.phase)⟩

theorem joint_value {m} (A B : Model (Fin m)) (a b : Bool) (x y : Bits m) :
    weight (joint A B a b) (weave m x y) =
      gated (support A.rows x && support B.rows y) ((a && A.phase.eval x) ^^ (b && B.phase.eval y)) := by
  have he {ι} (f : Bool) (q : Quad ι) (u : ι → Bool) : (takePhase f q).eval u = (f && q.eval u) := by
    cases f <;> simp [takePhase,Quad.eval,Aff.eval]
  have hh {ι} (r s : List (Aff ι)) (u : ι → Bool) :
      support (r++s) u = (support r u && support s u) := by simp [support,List.all_append]
  simp only [joint,weight,Model.sub,hh,support_sub,Quad.eval,Quad.eval_sub,he,Aff.eval,weave_site,
    Bool.false_eq_true,↓reduceIte]

theorem trie_gauss {m} (A B : Model (Fin m)) (a b : Bool) (t : TritWord m) :
    output t (joint A B a b) = gauss (restricted t A B a b) := by
  rw [output_leaf,gauss_eq_mass,energy_leaf]
  simp only [joint_value,signedLeaf]

#print axioms leaf_snoc
#print axioms output_leaf
#print axioms trie_gauss
end TrieProduct
