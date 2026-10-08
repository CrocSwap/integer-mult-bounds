import DirtyComplementSafety

/-!
Kernel-row clearing is a reversible operation, even when its fresh input
image becomes zero. These are logical coefficient contracts; they do not
license a zero physical dirty carrier or an uncharged frame relabeling.
-/
namespace FreshKernelReclaim
open DirtyComplementSafety

variable {I X : Type} [DecidableEq I]

def providerXor : List I → Vec I → Bool
  | [],_ => false
  | i::is,s => s i ^^ providerXor is s

def clearCarrier (target : I) (providers : List I) (s : Vec I) : Vec I :=
  fun i => if i=target then s target ^^ providerXor providers s else s i

omit [DecidableEq I] in
theorem providerXor_congr (providers : List I) (s t : Vec I)
    (h : ∀ i ∈ providers, s i = t i) : providerXor providers s = providerXor providers t := by
  induction providers with
  | nil => rfl
  | cons i is ih =>
    have hi := h i (by simp)
    have hrest : ∀ j ∈ is, s j=t j := by intro j hj; exact h j (by simp [hj])
    simp only [providerXor,hi,ih hrest]

theorem clear_other_coordinate (target i : I) (providers : List I)
    (h : i ≠ target) (s : Vec I) : clearCarrier target providers s i = s i := by
  simp only [clearCarrier,if_neg h]

theorem providers_unchanged (target : I) (providers : List I)
    (h : ∀ i ∈ providers, i ≠ target) (s : Vec I) :
    providerXor providers (clearCarrier target providers s) = providerXor providers s := by
  apply providerXor_congr
  intro i hi
  exact clear_other_coordinate target i providers (h i hi) s

/-- Clearing cannot erase arbitrary dirty information: it is an involution. -/
theorem clearing_involution (target : I) (providers : List I)
    (h : ∀ i ∈ providers, i ≠ target) (s : Vec I) :
    clearCarrier target providers (clearCarrier target providers s) = s := by
  funext i
  by_cases hi : i=target
  · subst i
    simp only [clearCarrier,ite_true]
    change (s target ^^ providerXor providers s ^^
      providerXor providers (clearCarrier target providers s)) = s target
    rw [providers_unchanged target providers h s]
    cases s target <;> cases providerXor providers s <;> rfl
  · simp only [clearCarrier,if_neg hi]

/-- A checked fresh linear dependency creates a quiet coordinate for every
fresh source value, while the reversible transform still retains dirty data. -/
theorem fresh_kernel_coordinate (target : I) (providers : List I)
    (fresh : Vec X → Vec I)
    (hkernel : ∀ x, fresh x target = providerXor providers (fresh x))
    (x : Vec X) : clearCarrier target providers (fresh x) target = false := by
  simp only [clearCarrier,ite_true,hkernel]
  exact Bool.xor_self _

/-- All non-target fresh outputs are preserved by kernel clearing. -/
theorem fresh_mandatory_coordinate_preserved (target i : I) (providers : List I)
    (hi : i ≠ target) (fresh : Vec X → Vec I) (x : Vec X) :
    clearCarrier target providers (fresh x) i = fresh x i :=
  clear_other_coordinate target i providers hi _

/-- An actual dirty carrier need not be zero after a fresh-zero certificate.
At one coordinate, clearing with no providers preserves a dirty true bit. -/
theorem dirty_zero_counterexample :
    clearCarrier (0 : Nat) [] (fun _ => true) 0 = true := by rfl

end FreshKernelReclaim

#print axioms FreshKernelReclaim.clearing_involution
#print axioms FreshKernelReclaim.fresh_kernel_coordinate
#print axioms FreshKernelReclaim.fresh_mandatory_coordinate_preserved
#print axioms FreshKernelReclaim.dirty_zero_counterexample
