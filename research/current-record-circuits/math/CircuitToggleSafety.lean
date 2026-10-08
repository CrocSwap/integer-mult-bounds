import FreshKernelReclaim

/-!
Alternative clearing relations from zero-signal circuits. A provider circuit
that vanishes on the fresh source image may be toggled into a clearing relation
without changing its fresh result. Both provider lists must exclude the target
for reversible dirty arithmetic. Eligibility, pending next-use containment and
all literal XOR/frame costs must be checked separately. No zero dirty carrier,
global optimizer, or physical compilation theorem is inferred here.
-/
namespace CircuitToggleSafety
open DirtyComplementSafety FreshKernelReclaim

variable {I X : Type} [DecidableEq I]

omit [DecidableEq I] in
theorem providerXor_append (xs ys : List I) (s : Vec I) :
    providerXor (xs++ys) s = (providerXor xs s ^^ providerXor ys s) := by
  induction xs with
  | nil => simp only [List.nil_append,providerXor,Bool.false_xor]
  | cons i is ih =>
    simp only [List.cons_append,providerXor,ih]
    exact (Bool.xor_assoc _ _ _).symm

theorem zero_circuit_preserves_fresh_clear
    (target : I) (providers circuit : List I) (fresh : Vec X → Vec I)
    (hzero : ∀ x, providerXor circuit (fresh x)=false) (x : Vec X) :
    clearCarrier target (providers++circuit) (fresh x) =
      clearCarrier target providers (fresh x) := by
  funext i
  simp only [clearCarrier,providerXor_append,hzero,Bool.xor_false]

omit [DecidableEq I] in
theorem zero_circuit_preserves_dependency
    (target : I) (providers circuit : List I) (fresh : Vec X → Vec I)
    (hdep : ∀ x, fresh x target=providerXor providers (fresh x))
    (hzero : ∀ x, providerXor circuit (fresh x)=false) (x : Vec X) :
    fresh x target = providerXor (providers++circuit) (fresh x) := by
  simp only [providerXor_append,hzero,Bool.xor_false]
  exact hdep x

theorem toggled_clearing_is_involution
    (target : I) (providers circuit : List I)
    (hp : ∀ i ∈ providers, i ≠ target)
    (hc : ∀ i ∈ circuit, i ≠ target) (dirty : Vec I) :
    clearCarrier target (providers++circuit)
      (clearCarrier target (providers++circuit) dirty) = dirty := by
  apply clearing_involution
  intro i hi
  rcases List.mem_append.mp hi with hi | hi
  · exact hp i hi
  · exact hc i hi

end CircuitToggleSafety

#print axioms CircuitToggleSafety.providerXor_append
#print axioms CircuitToggleSafety.zero_circuit_preserves_fresh_clear
#print axioms CircuitToggleSafety.zero_circuit_preserves_dependency
#print axioms CircuitToggleSafety.toggled_clearing_is_involution
