import PhysicalInput
import Mathlib.Tactic.Positivity

/-! Each nonzero signed leaf is one signed event. This file composes
the four passes and binary event delivery. -/
namespace SignedEvents
open Finset TernaryCollect QuadraticProduct BinaryDelivery
open scoped BigOperators

abbrev Event := SignedCarry.Event
abbrev score := SignedCarry.Event.value

def encode (j : ℕ) (v : ℤ) : List Event :=
  if v = 0 then [] else [⟨decide (0<v),j+v.natAbs.log2⟩]

def signedPower (v : ℤ) : Prop := v = 0 ∨ ∃ k : ℕ, v = (2:ℤ)^k ∨ v = -(2:ℤ)^k

theorem neg_power (v : ℤ) (h : signedPower v) : signedPower (-v) := by
  rcases h with rfl|⟨k,rfl|rfl⟩
  · exact Or.inl (by simp)
  · exact Or.inr ⟨k,Or.inr rfl⟩
  · exact Or.inr ⟨k,Or.inl (neg_neg _)⟩

theorem encode_value (j : ℕ) (v : ℤ) (h : signedPower v) :
    ((encode j v).map score).sum = (2:ℤ)^j*v := by
  rcases h with rfl|⟨k,rfl|rfl⟩
  · simp [encode]
  · have hp : 0 < (2:ℤ)^k := by positivity
    simp [encode,SignedCarry.Event.value,hp,hp.ne',Int.natAbs_pow,Nat.log2_two_pow,pow_add]
  · have hp : 0 < (2:ℤ)^k := by positivity
    simp [encode,SignedCarry.Event.value,hp.ne',Int.natAbs_pow,Nat.log2_two_pow,pow_add]

def paired : List Bool → List Bool → List (Bool×Bool)
  | [], bs => bs.map (fun b ↦ (false,b))
  | a::as, [] => (a,false)::(as.map (fun b ↦ (b,false)))
  | a::as, b::bs => (a,b)::paired as bs

theorem zeros (n : ℕ) : binary (List.replicate n false) = 0 := by
  induction n with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ,binary,value,ih]

theorem paired_values (a b : List Bool) :
    binary ((paired a b).map Prod.fst) = binary a ∧ binary ((paired a b).map Prod.snd) = binary b := by
  induction a generalizing b with
  | nil => simp [paired,List.map_map,Function.comp_def,zeros,binary]
  | cons c cs ih =>
    cases b with
    | nil => simp [paired,List.map_map,Function.comp_def,zeros,binary,value]
    | cons d ds => simp [paired,binary,(ih ds).1,(ih ds).2]

def finish (es : List Event) : List Bool :=
  let z := SignedCarry.finish es ⟨[],[]⟩
  ((subtract false (paired z.positive z.negative)).1).drop 2

theorem event_delivery (es : List Event) (v : ℕ) (he : (es.map score).sum = 4*(v:ℤ)) :
    binary (finish es) = v := by
  let z := SignedCarry.finish es ⟨[],[]⟩
  apply (exact_finish (paired z.positive z.negative) v _).2
  rw [(paired_values _ _).1,(paired_values _ _).2, numeral_eq, numeral_eq]
  change (SignedCarry.finish es ⟨[],[]⟩).value = _
  rw [SignedCarry.signed_numeral]
  change (0:ℤ) + (es.map score).sum = _
  rw [zero_add,he]

def flip (b : Bool) (v : ℤ) := if b then -v else v

noncomputable def term {m} (A B : BooleanGauss.Model (Fin m)) (a b : Bool) (t : TritWord m) : ℤ :=
  flip (a ^^ b) (gauss (restricted t A B a b))

theorem term_power {m} (A B : BooleanGauss.Model (Fin m)) (a b : Bool) (t : TritWord m) :
    signedPower (term A B a b t) := by
  have h : signedPower (gauss (restricted t A B a b)) := by
    rcases leaf_outputs t A B a b with h|⟨k,_,h⟩
    · exact Or.inl h
    · exact Or.inr ⟨k,h⟩
  unfold term flip
  split
  · exact neg_power _ h
  · exact h

noncomputable def pass {m} (A B : BooleanGauss.Model (Fin m)) (a b : Bool) : List Event :=
  (Finset.univ : Finset (TritWord m)).toList.flatMap fun t ↦ encode (exponent t) (term A B a b t)

theorem pass_value {m} (A B : BooleanGauss.Model (Fin m)) (a b : Bool) :
    ((pass A B a b).map score).sum = ∑ t : TritWord m, (2:ℤ)^(exponent t)*term A B a b t := by
  let g (t : TritWord m) := encode (exponent t) (term A B a b t)
  have lsum (xs : List (TritWord m)) : ((xs.flatMap g).map score).sum =
      (xs.map (fun t ↦ (2:ℤ)^(exponent t)*term A B a b t)).sum := by
    induction xs with
    | nil => rfl
    | cons t ts ih => simp [g,ih,encode_value _ _ (term_power A B a b t)]
  exact (lsum _).trans (Finset.sum_map_toList _ _)

noncomputable def fourPasses {m} (A B : BooleanGauss.Model (Fin m)) : List Event :=
  pass A B false false ++ pass A B true false ++ pass A B false true ++ pass A B true true

theorem four_pass_value {m} (A B : BooleanGauss.Model (Fin m)) :
    ((fourPasses A B).map score).sum = ∑ t : TritWord m, (2:ℤ)^(exponent t)*numerator t A B := by
  simp only [fourPasses, List.map_append,List.sum_append,pass_value,← Finset.sum_add_distrib]
  apply Finset.sum_congr rfl
  intro t _
  simp only [term,flip,numerator,Bool.false_xor,Bool.true_xor,Bool.not_false,Bool.not_true,
    Bool.false_eq_true,↓reduceIte]
  ring

/-- Both inputs are complete literal binary words. The conclusion is
the value of the binary output of the four signed event passes. -/
theorem literal_multiplication {m} (a b : Fin (3^m) → Bool) (A B : BooleanGauss.Model (Fin m))
    (ha : PhysicalInput.Valid A a) (hb : PhysicalInput.Valid B b) :
    binary (finish (fourPasses A B)) = binary (List.ofFn a) * binary (List.ofFn b) := by
  apply event_delivery
  rw [four_pass_value,PhysicalInput.literal_value _ _ ha,PhysicalInput.literal_value _ _ hb]
  simp only [numerator,gauss_eq_mass,energy_leaf]
  exact (four_product _ _ _ _).symm

#print axioms encode_value
#print axioms SignedCarry.linear_ripple
#print axioms event_delivery
#print axioms literal_multiplication
end SignedEvents
