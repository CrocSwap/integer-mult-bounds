import PrefixBlocks

/-! The high strip contains all physical blocks in order. The input may
use a different verified low operand model at every live high address. -/
namespace PhysicalBlocks
open Finset TernaryCollect PrefixBlocks BinaryDelivery
open scoped BigOperators

theorem binary_append (a b : List Bool) :
    binary (a++b) = binary a + 2^a.length*binary b := by
  induction a with
  | nil => simp [binary]
  | cons c cs ih => simp only [List.cons_append,binary,List.length_cons,ih,pow_succ]; ring

theorem blocks_value (S : ℕ) (ws : List (List Bool)) (hlen : ∀ w ∈ ws, w.length = S) :
    binary ws.flatten = radix (2^S) (ws.map binary) := by
  induction ws with
  | nil => rfl
  | cons w ws ih =>
    have hh := hlen w (by simp)
    have ht := ih (fun x hx ↦ hlen x (List.mem_cons_of_mem _ hx))
    simp only [List.flatten_cons,List.map_cons,radix,binary_append,hh,ht]

def strip {h S : ℕ} (f : Fin (3^h) → Fin S → Bool) : List Bool :=
  (List.ofFn (fun j ↦ List.ofFn (f j))).flatten

theorem strip_value {h S : ℕ} (f : Fin (3^h) → Fin S → Bool) :
    binary (strip f) = ∑ j, (2^S)^j.val * binary (List.ofFn (f j)) := by
  unfold strip
  rw [blocks_value S _ (by simp)]
  rw [List.map_ofFn,radix_record]
  rfl

/-- Every high address with a ternary digit two contains a zero word. -/
def HighHoles {h S : ℕ} (f : Fin (3^h) → Fin S → Bool) : Prop :=
  ∀ t, (¬ ∃ x, PhysicalInput.ternary x = t) → ∀ j, f (PhysicalInput.address h t) j = false

noncomputable def block {h S : ℕ} (f : Fin (3^h) → Fin S → Bool) (x : Bits h) : Fin S → Bool :=
  f (PhysicalInput.address h (PhysicalInput.ternary x))

theorem strip_pack {h S : ℕ} (f : Fin (3^h) → Fin S → Bool) (hh : HighHoles f) :
    binary (strip f) = pack (2^S) (fun x ↦ binary (List.ofFn (block f x))) := by
  classical
  rw [strip_value,←(PhysicalInput.address h).sum_comp]
  let L := Finset.univ.image (PhysicalInput.ternary (m := h))
  let g (t : TritWord h) := (2^S)^(PhysicalInput.address h t).val * binary (List.ofFn (f (PhysicalInput.address h t)))
  change (∑ t, g t) = _
  have hsum : (∑ t ∈ L, g t) = ∑ t, g t := by
    apply Finset.sum_subset (Finset.subset_univ L)
    intro t _ ht
    have hn : ¬ ∃ x, PhysicalInput.ternary x = t := by simpa [L] using ht
    have hzero := funext (hh t hn)
    simp [g,hzero,List.ofFn_const,SignedEvents.zeros]
  rw [← hsum,Finset.sum_image (fun x _ y _ e ↦ PhysicalInput.ternary_injective h e)]
  apply Finset.sum_congr rfl
  intro x _
  change (2^S)^exponent (PhysicalInput.ternary x)*binary (List.ofFn (block f x)) = _
  rw [PhysicalInput.spread_address,mul_comm]

/-- Each side is one complete physical binary stream. Each low product
comes from the four signed Gaussian passes of its own two charts. -/
theorem complete_mixture {h n : ℕ} (A B : Bits h → BooleanGauss.Model (Fin n))
    (a b : Fin (3^h) → Fin (3^n) → Bool) (ah : HighHoles a) (bh : HighHoles b)
    (av : ∀ x, PhysicalInput.Valid (A x) (block a x)) (bv : ∀ y, PhysicalInput.Valid (B y) (block b y)) :
    deliver (2^(3^n)) (binCoeffs (fun x y ↦ binary
      (SignedEvents.finish (SignedEvents.fourPasses (A x) (B y))))) = binary (strip a) * binary (strip b) := by
  rw [strip_pack _ ah,strip_pack _ bh]
  exact literal_mixture A B (block a) (block b) av bv

#print axioms strip_value
#print axioms strip_pack
#print axioms complete_mixture
end PhysicalBlocks
