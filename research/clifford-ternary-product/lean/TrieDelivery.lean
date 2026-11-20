import TrieProduct

/-! The worker expands a three-child prefix once and sends its resulting
chart to each suffix. No independent per-leaf Gaussian solve is needed. -/
namespace TrieDelivery
open Finset TernaryCollect BooleanGauss BellBoundary TrieProduct SignedEvents
open scoped BigOperators

theorem three_roots {m} (f : TritWord (m+1) → ℤ) :
    (∑ x, f x) = (∑ t : TritWord m, f (Fin.snoc t (some false))) +
      (∑ t : TritWord m, f (Fin.snoc t none)) + (∑ t : TritWord m, f (Fin.snoc t (some true))) := by
  rw [← (Fin.snocEquiv (fun _ : Fin (m+1) ↦ Trit)).sum_comp,Fintype.sum_prod_type,
    Fintype.sum_option,Fintype.sum_bool]
  ac_rfl

theorem high_exponent {m} (t : TritWord m) (d : Trit) :
    exponent (Fin.snoc t d) = exponent t + digitValue d*3^m := by
  rw [exponent,Fin.sum_univ_castSucc]
  simp [exponent]

theorem branch_snoc {m} (t : TritWord m) (d : Trit) (M : Model (Fin (slots 0 (m+1)))) :
    output (Fin.snoc t d) M = (2:ℤ)^(project d M).1 * output t (project d M).2 := by
  simp only [output,branch,Fin.snoc_last, Fin.init_snoc,pow_add,mul_assoc]

def traverse : (m : ℕ) → Model (Fin (slots 0 m)) → ℕ → Bool → List Event
  | 0,M,j,neg => encode j (flip neg (weight M Fin.elim0))
  | m+1,M,j,neg =>
    let child (d : Trit) :=
      let c := project d M
      traverse m c.2 (j+digitValue d*3^m+c.1) neg
    child (some false) ++ child none ++ child (some true)

theorem terminal_power (M : Model (Fin 0)) (b : Bool) : signedPower (flip b (weight M Fin.elim0)) := by
  have h : signedPower (weight M Fin.elim0) := by
    rcases weight_values M Fin.elim0 with h|h|h
    · exact Or.inl h
    · exact Or.inr ⟨0,Or.inl (by simpa using h)⟩
    · exact Or.inr ⟨0,Or.inr (by simpa using h)⟩
  cases b with
  | false => exact h
  | true => exact neg_power _ h

theorem shifted_child {m} (M : Model (Fin (slots 0 (m+1)))) (d : Trit) (j : ℕ) (neg : Bool) :
    (∑ t : TritWord m, (2:ℤ)^(j+digitValue d*3^m+(project d M).1+exponent t) *
      flip neg (output t (project d M).2)) =
    ∑ t : TritWord m, (2:ℤ)^(j+exponent (Fin.snoc t d))*flip neg (output (Fin.snoc t d) M) := by
  apply Finset.sum_congr rfl
  intro t _
  rw [branch_snoc,high_exponent]
  cases neg <;> simp only [SignedEvents.flip,Bool.false_eq_true,↓reduceIte,pow_add] <;> ring

theorem traversal_score (m : ℕ) (M : Model (Fin (slots 0 m))) (j : ℕ) (neg : Bool) :
    ((traverse m M j neg).map score).sum = ∑ t : TritWord m, (2:ℤ)^(j+exponent t)*flip neg (output t M) := by
  induction m generalizing j with
  | zero =>
    change Model (Fin 0) at M
    change ((encode j (flip neg (weight M Fin.elim0))).map score).sum = _
    rw [encode_value j _ (terminal_power M neg),Fintype.sum_unique]
    simp [output,branch,exponent]
  | succ m ih =>
    simp only [traverse,List.map_append,List.sum_append,ih,shifted_child]
    exact (three_roots (fun t : TritWord (m+1) ↦ (2:ℤ)^(j+exponent t)*flip neg (output t M))).symm

def fourTraversals {m} (A B : Model (Fin m)) : List Event :=
  traverse m (joint A B false false) 0 false ++ traverse m (joint A B true false) 0 true ++
    traverse m (joint A B false true) 0 true ++ traverse m (joint A B true true) 0 false

theorem trie_total {m} (A B : Model (Fin m)) :
    ((fourTraversals A B).map score).sum = ((fourPasses A B).map score).sum := by
  simp only [fourTraversals,fourPasses,List.map_append,List.sum_append,traversal_score,pass_value,
    Nat.zero_add,term,trie_gauss,Bool.true_xor,Bool.false_xor,Bool.not_true,Bool.not_false]

theorem from_literals {m} (a b : Fin (3^m) → Bool) (A B : Model (Fin m))
    (ha : PhysicalInput.Valid A a) (hb : PhysicalInput.Valid B b) :
    BinaryDelivery.binary (finish (fourTraversals A B)) =
    BinaryDelivery.binary (List.ofFn a) * BinaryDelivery.binary (List.ofFn b) := by
  apply event_delivery
  rw [trie_total,four_pass_value,PhysicalInput.literal_value _ _ ha,PhysicalInput.literal_value _ _ hb]
  simp only [QuadraticProduct.numerator,QuadraticProduct.gauss_eq_mass,QuadraticProduct.energy_leaf]
  exact (four_product _ _ _ _).symm

theorem complete_mixture {h n : ℕ} (A B : Bits h → Model (Fin n))
    (a b : Fin (3^h) → Fin (3^n) → Bool) (ah : PhysicalBlocks.HighHoles a) (bh : PhysicalBlocks.HighHoles b)
    (av : ∀ x, PhysicalInput.Valid (A x) (PhysicalBlocks.block a x))
    (bv : ∀ y, PhysicalInput.Valid (B y) (PhysicalBlocks.block b y)) :
    PrefixBlocks.deliver (2^(3^n)) (PrefixBlocks.binCoeffs (fun x y ↦ BinaryDelivery.binary
      (finish (fourTraversals (A x) (B y))))) =
    BinaryDelivery.binary (PhysicalBlocks.strip a) * BinaryDelivery.binary (PhysicalBlocks.strip b) := by
  rw [PhysicalBlocks.strip_pack _ ah,PhysicalBlocks.strip_pack _ bh]
  apply PrefixBlocks.delivered
  exact fun x y ↦ from_literals _ _ _ _ (av x) (bv y)

theorem emitted_count (m : ℕ) (M : Model (Fin (slots 0 m))) (j : ℕ) (neg : Bool) :
    (traverse m M j neg).length ≤ 3^m := by
  induction m generalizing j with
  | zero =>
    change (encode j (flip neg (weight M Fin.elim0))).length ≤ 1
    unfold encode
    split <;> simp
  | succ m ih =>
    simp only [traverse,List.length_append,pow_succ]
    have hb (d : Trit) := ih (project d M).2 (j+digitValue d*3^m+(project d M).1)
    have h₀ := hb (some false)
    have h₁ := hb none
    have h₂ := hb (some true)
    omega

theorem total_ripple {m} (A B : Model (Fin m)) :
    SignedCarry.totalCarry (fourTraversals A B) ⟨[],[]⟩ ≤ 4*3^m := by
  apply (SignedCarry.linear_ripple _).trans
  simp only [fourTraversals,List.length_append]
  have h₀ := emitted_count m (joint A B false false) 0 false
  have h₁ := emitted_count m (joint A B true false) 0 true
  have h₂ := emitted_count m (joint A B false true) 0 true
  have h₃ := emitted_count m (joint A B true true) 0 false
  omega

#print axioms total_ripple
#print axioms traversal_score
#print axioms trie_total
#print axioms from_literals
#print axioms complete_mixture
end TrieDelivery
