import Std

/-!
Restricted operator domain for the commutative matrix leaf.
Raw phase numerators have one common charged (1+i) denominator.
After two phases, both orders have the same two-factor denominator.
Physical eligibility and transport/tape costs are separate contracts.
-/
namespace MatrixParityBridge

def phaseAdd (x y : Int × Int) : Int × Int := (x.1+y.1,x.2+y.2)
def phaseRotate (x : Int × Int) : Int × Int := (-x.2,x.1)
def translate (u : Nat) (f : Nat → α) (x : Nat) : α := f (x ^^^ u)
def rawPhase (u : Nat) (f : Nat → Int × Int) (x : Nat) : Int × Int :=
  phaseAdd (phaseRotate (f x)) (f (x ^^^ u))

theorem xor_translation_commutes (u v : Nat) (f : Nat → α) :
    translate u (translate v f) = translate v (translate u f) := by
  funext x
  simp only [translate]
  rw [Nat.xor_assoc, Nat.xor_assoc, Nat.xor_comm u v]

theorem raw_phase_commutes (u v : Nat) (f : Nat → Int × Int) :
    rawPhase u (rawPhase v f) = rawPhase v (rawPhase u f) := by
  have hx (x : Nat) : (x ^^^ u) ^^^ v = (x ^^^ v) ^^^ u := by
    rw [Nat.xor_assoc, Nat.xor_assoc, Nat.xor_comm u v]
  funext x
  apply Prod.ext <;> simp only [rawPhase,phaseAdd,phaseRotate] <;> rw [hx x] <;> omega

theorem raw_phase_translation_commutes (u v : Nat) (f : Nat → Int × Int) :
    rawPhase u (translate v f) = translate v (rawPhase u f) := by
  have hx (x : Nat) : (x ^^^ u) ^^^ v = (x ^^^ v) ^^^ u := by
    rw [Nat.xor_assoc, Nat.xor_assoc, Nat.xor_comm u v]
  funext x
  simp only [rawPhase,translate]
  rw [hx x]

def firstAxisGauge (f : Nat → Int × Int) (x : Nat) : Int × Int :=
  if x % 2 = 0 then f x else (-(f x).1,-(f x).2)
def zeroImpulse (x : Nat) : Int × Int := if x = 0 then (1,0) else (0,0)

theorem gauge_phase_noncommuting_witness :
    rawPhase 1 (firstAxisGauge zeroImpulse) 1 ≠
      firstAxisGauge (rawPhase 1 zeroImpulse) 1 := by
  decide

end MatrixParityBridge
