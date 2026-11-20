import SignedEvents

/-! Independent operand blocks can use different affine spaces and phases.
High ternary addresses group all pairs before an ordinary radix carry. -/
namespace PrefixBlocks
open Finset TernaryCollect
open scoped BigOperators

/-- Positions are in units of one whole low block. -/
noncomputable def pack {h : ℕ} (B : ℕ) (a : Bits h → ℕ) : ℕ :=
  ∑ x, a x * B^(spread x)

theorem collect_blocks {h : ℕ} (B : ℕ) (a b : Bits h → ℕ) :
    pack B a * pack B b =
      ∑ t : TritWord h, B^(exponent t)*leaf t (fun x y ↦ a x*b y) := by
  rw [pack,pack,Finset.sum_mul]
  simp_rw [Finset.mul_sum]
  rw [← collect_joint (fun x y ↦ a x*b y) (fun j ↦ B^j)]
  apply Finset.sum_congr rfl
  intro x _
  apply Finset.sum_congr rfl
  intro y _
  rw [pow_add]
  ring

/-- Each step emits its low radix digit and passes the quotient upward. -/
def carry (B : ℕ) : List ℕ → ℕ → List ℕ × ℕ
  | [], k => ([],k)
  | a::as, k =>
    let r := carry B as ((a+k)/B)
    ((a+k)%B :: r.1,r.2)

def radix (B : ℕ) : List ℕ → ℕ
  | [] => 0
  | a::as => a + B*radix B as

theorem carry_length (B : ℕ) (as : List ℕ) (k : ℕ) : (carry B as k).1.length = as.length := by
  induction as generalizing k with
  | nil => rfl
  | cons a as ih => simp [carry,ih]

theorem carry_value (B : ℕ) (as : List ℕ) (k : ℕ) :
    radix B (carry B as k).1 + B^as.length*(carry B as k).2 = radix B as + k := by
  induction as generalizing k with
  | nil => simp [carry,radix]
  | cons a as ih =>
    simp only [carry,radix,List.length_cons,pow_succ]
    have hh := ih ((a+k)/B)
    have hd := Nat.mod_add_div (a+k) B
    linear_combination B*hh + hd

theorem carries_are_digits (B : ℕ) (hb : 0 < B) (as : List ℕ) (k : ℕ) :
    ∀ d ∈ (carry B as k).1, d < B := by
  induction as generalizing k with
  | nil => simp [carry]
  | cons a as ih =>
    intro d hd
    rcases List.mem_cons.mp hd with hh|hh
    · rw [hh]
      exact Nat.mod_lt _ hb
    · exact ih _ _ hh

theorem radix_record (B n : ℕ) (f : Fin n → ℕ) :
    radix B (List.ofFn f) = ∑ i, B^i.val * f i := by
  induction n with
  | zero => simp [radix]
  | succ n ih =>
    rw [List.ofFn_succ,radix,ih,Fin.sum_univ_succ,Finset.mul_sum]
    simp only [Fin.val_zero,pow_zero,one_mul,Fin.val_succ,pow_succ]
    congr 1
    exact Finset.sum_congr rfl fun i _ ↦ by ring

noncomputable def binCoeffs {h : ℕ} (f : Bits h → Bits h → ℕ) : List ℕ :=
  List.ofFn (fun j : Fin (3^h) ↦ leaf ((PhysicalInput.address h).symm j) f)

theorem bin_value {h : ℕ} (B : ℕ) (f : Bits h → Bits h → ℕ) :
    radix B (binCoeffs f) = ∑ t : TritWord h, B^(exponent t)*leaf t f := by
  rw [binCoeffs,radix_record,←(PhysicalInput.address h).sum_comp]
  simp only [Equiv.symm_apply_apply]
  rfl

/-- This is the ordered block output with the final carry as a high block. -/
def deliver (B : ℕ) (as : List ℕ) : ℕ :=
  let r := carry B as 0
  radix B r.1 + B^r.1.length*r.2

theorem delivered {h : ℕ} (S : ℕ) (a b : Bits h → ℕ) (piece : Bits h → Bits h → ℕ)
    (hl : ∀ x y, piece x y = a x*b y) :
    deliver (2^S) (binCoeffs piece) = pack (2^S) a * pack (2^S) b := by
  dsimp only [deliver]
  rw [carry_length,carry_value,Nat.add_zero,bin_value,collect_blocks]
  simp only [funext (fun x ↦ funext (hl x))]

/-- Every prefix has its own literal low bit word and its own independently
checked affine-quadratic fit. The high prefix choice has no promise. -/
theorem literal_mixture {h n : ℕ} (A B : Bits h → BooleanGauss.Model (Fin n))
    (a b : Bits h → Fin (3^n) → Bool)
    (ha : ∀ x, PhysicalInput.Valid (A x) (a x)) (hb : ∀ y, PhysicalInput.Valid (B y) (b y)) :
    deliver (2^(3^n)) (binCoeffs (fun x y ↦ BinaryDelivery.binary
      (SignedEvents.finish (SignedEvents.fourPasses (A x) (B y))))) =
    pack (2^(3^n)) (fun x ↦ BinaryDelivery.binary (List.ofFn (a x))) *
      pack (2^(3^n)) (fun y ↦ BinaryDelivery.binary (List.ofFn (b y))) := by
  apply delivered
  exact fun x y ↦ SignedEvents.literal_multiplication _ _ _ _ (ha x) (hb y)

#print axioms collect_blocks
#print axioms carry_value
#print axioms carries_are_digits
#print axioms literal_mixture
end PrefixBlocks
