/-!
A Lean-core certificate for the literal seven-stage .594461 endpoint.

Rates use units 10^-21. For stage i, the raw service price is C/D -
11/(8 H_i), with C/D = 287039844436133239/2^66. The ordinary limit before
its eta cap is (249*(C/D - 11/(8 H_i)) + previous)/250. `booked` is the
exact positive-denominator cross multiplication of previous < rate <
min(39/10000, limit). `one_tick` additionally checks that the first six
rates are exactly floor(10^21 * limit) - 1. No floating point is used.

The directed raw-word upper endpoint is an INPUT from the external 112-bit
source audit: this file proves its separation from the next 10^-18 tick; it
does not prove the source interpretation, the outward interval itself, the
transport or the complete multiplier. Source: pinned e264 price recurrence.
-/

set_option maxRecDepth 100000
set_option maxHeartbeats 0

namespace Endpoint461

def C : Nat := 287039844436133239
def D : Nat := 73786976294838206464  -- 2^66
def G : Nat := 1000000000000000000000 -- 10^21

def H1 : Nat := 2000000000000
def H2 : Nat := 32000000000000
def H3 : Nat := 512000000000000
def H4 : Nat := 8192000000000000
def H5 : Nat := 131072000000000000
def H6 : Nat := 2097152000000000000
def H7 : Nat := 33554432000000000000

def B1 : Nat := 3874554824763333282
def B2 : Nat := 3890053044704339740
def B3 : Nat := 3890115037624225836
def B4 : Nat := 3890115285598413010
def B5 : Nat := 3890115286590466485
def B6 : Nat := 3890115286594444495
def B7 : Nat := 3890115286594461005
def K  : Nat := 3890115286594461000

/-- All terms are nonnegative; move the debit to the left before comparing. -/
def rhs (c previous h : Nat) : Nat :=
  249*c*G*8*h + previous*D*8*h

def lhs (rate h : Nat) : Nat :=
  250*rate*D*8*h + 249*11*D*G

abbrev booked (c previous rate h : Nat) : Prop :=
  0 < h ∧ previous < rate ∧ 10000*rate < 39*G ∧ lhs rate h < rhs c previous h

abbrev one_tick (c previous rate h : Nat) : Prop :=
  lhs (rate+1) h ≤ rhs c previous h ∧ rhs c previous h < lhs (rate+2) h

/-- The uncapped price is below eta: then min(eta,price) is price. -/
abbrev eta_price (c previous h : Nat) : Prop :=
  10000*(rhs c previous h) < 39*250*G*D*8*h + 10000*249*11*D*G

theorem binary_denominator : D = 2^66 := by decide
theorem grid_denominator : G = 10^21 := by decide

theorem booked1 : booked C 0  B1 H1 := by decide
theorem booked2 : booked C B1 B2 H2 := by decide
theorem booked3 : booked C B2 B3 H3 := by decide
theorem booked4 : booked C B3 B4 H4 := by decide
theorem booked5 : booked C B4 B5 H5 := by decide
theorem booked6 : booked C B5 B6 H6 := by decide
theorem booked7 : booked C B6 B7 H7 := by decide

theorem rounded1 : one_tick C 0  B1 H1 := by decide
theorem rounded2 : one_tick C B1 B2 H2 := by decide
theorem rounded3 : one_tick C B2 B3 H3 := by decide
theorem rounded4 : one_tick C B3 B4 H4 := by decide
theorem rounded5 : one_tick C B4 B5 H5 := by decide
theorem rounded6 : one_tick C B5 B6 H6 := by decide

theorem cap1 : eta_price C 0  H1 := by decide
theorem cap2 : eta_price C B1 H2 := by decide
theorem cap3 : eta_price C B2 H3 := by decide
theorem cap4 : eta_price C B3 H4 := by decide
theorem cap5 : eta_price C B4 H5 := by decide
theorem cap6 : eta_price C B5 H6 := by decide
theorem cap7 : eta_price C B6 H7 := by decide

theorem signed_booking : B7 = K + 5 := by decide
theorem signed_strict : K + 4 < B7 := by decide

/-- hi/10^27 is the *externally certified* directed raw crossing upper. -/
def hi : Nat := 3890115286594461129996943
def nextGrid : Nat := 3890115286594462  -- denominator 10^18

theorem upper_below_next : hi < nextGrid * 10^9 := by decide
theorem current_trial_below_upper : C*10^27 < hi*D := by decide

/-- Given any positive-denominator rational upper-bounded by the external hi,
    that rational lies strictly below the next 10^-18 grid point. -/
theorem conditional_endpoint (numerator denominator : Nat) (positive : 0 < denominator)
    (directed_raw_upper : numerator*10^27 ≤ hi*denominator) :
    numerator*10^27 < (nextGrid*10^9)*denominator :=
  Nat.lt_of_le_of_lt directed_raw_upper (Nat.mul_lt_mul_of_pos_right upper_below_next positive)

/-- Corruption controls: decrementing c's numerator spoils the booked first
    stage, while raising κ by a whole 10^-18 tick spoils the final stage. -/
theorem damaged_c_rejected : ¬ booked (C-1) 0 B1 H1 := by decide
theorem next_tick_rejected : ¬ booked C B6 (K+1005) H7 := by decide

theorem all_bookings : booked C 0 B1 H1 ∧ booked C B1 B2 H2 ∧
    booked C B2 B3 H3 ∧ booked C B3 B4 H4 ∧ booked C B4 B5 H5 ∧
    booked C B5 B6 H6 ∧ booked C B6 B7 H7 :=
  ⟨booked1, booked2, booked3, booked4, booked5, booked6, booked7⟩

theorem all_roundings : one_tick C 0 B1 H1 ∧ one_tick C B1 B2 H2 ∧
    one_tick C B2 B3 H3 ∧ one_tick C B3 B4 H4 ∧
    one_tick C B4 B5 H5 ∧ one_tick C B5 B6 H6 :=
  ⟨rounded1, rounded2, rounded3, rounded4, rounded5, rounded6⟩

#print axioms binary_denominator
#print axioms grid_denominator
#print axioms all_bookings
#print axioms all_roundings
#print axioms booked1
#print axioms booked2
#print axioms booked3
#print axioms booked4
#print axioms booked5
#print axioms booked6
#print axioms booked7
#print axioms rounded1
#print axioms rounded2
#print axioms rounded3
#print axioms rounded4
#print axioms rounded5
#print axioms rounded6
#print axioms cap1
#print axioms cap2
#print axioms cap3
#print axioms cap4
#print axioms cap5
#print axioms cap6
#print axioms cap7
#print axioms signed_booking
#print axioms signed_strict
#print axioms upper_below_next
#print axioms current_trial_below_upper
#print axioms conditional_endpoint
#print axioms damaged_c_rejected
#print axioms next_tick_rejected

end Endpoint461
