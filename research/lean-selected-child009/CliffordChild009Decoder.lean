import CliffordMonomialDecoder

/-!
Exact field-level decoder certificate for CLIFFORD-RECIPES children[7], key
old=0/new=9/rank=1. Apache-2.0; see NOTICE.md for source attribution.
The four low bits use bit i as 2^i. The higher five bits are unchanged by every
stored matrix and carry zero phase coefficients. Arbitrary spectator payloads
are retained. This file does not yet prove the canonical Gaussian child identity.
-/
namespace CurrentMain.CliffordChild009Decoder

abbrev Low := Bool × Bool × Bool × Bool

def leftRows : List Nat := [3, 5, 8, 1, 16, 32, 64, 128, 256]
def rightRows : List Nat := [11, 9, 10, 4, 16, 32, 64, 128, 256]
def leftQ : List Nat := [0, 0, 0, 0, 0, 0, 0, 0, 0]
def rightQ : List Nat := [3, 3, 0, 0, 0, 0, 0, 0, 0]
def leftAlpha : List Nat := [2, 0, 0, 0, 0, 0, 0, 0, 0]
def rightAlpha : List Nat := [3, 3, 0, 2, 0, 0, 0, 0, 0]

def dot4 (row : Nat) (x : Low) : Bool :=
  (((row.testBit 0 && x.1) ^^ (row.testBit 1 && x.2.1)) ^^
    (row.testBit 2 && x.2.2.1)) ^^ (row.testBit 3 && x.2.2.2)

def mv4 (rows : List Nat) (x : Low) : Low :=
  (dot4 (rows.getD 0 0) x, dot4 (rows.getD 1 0) x,
    dot4 (rows.getD 2 0) x, dot4 (rows.getD 3 0) x)

def leftMap (x : Low) : Low :=
  (x.1 ^^ x.2.1, x.1 ^^ x.2.2.1, x.2.2.2, x.1)

def leftInverse (x : Low) : Low :=
  (x.2.2.2, x.1 ^^ x.2.2.2, x.2.1 ^^ x.2.2.2, x.2.2.1)

def rightMap (x : Low) : Low :=
  ((x.1 ^^ x.2.1) ^^ x.2.2.2, x.1 ^^ x.2.2.2,
    x.2.1 ^^ x.2.2.2, x.2.2.1)

def rightInverse (x : Low) : Low :=
  (x.1 ^^ x.2.2.1, x.1 ^^ x.2.1, x.2.2.2,
    (x.1 ^^ x.2.1) ^^ x.2.2.1)

def leftEquiv : Low ≃ Low where
  toFun := leftMap
  invFun := leftInverse
  left_inv := by
    rintro ⟨a, b, c, d⟩
    cases a <;> cases b <;> cases c <;> cases d <;> rfl
  right_inv := by
    rintro ⟨a, b, c, d⟩
    cases a <;> cases b <;> cases c <;> cases d <;> rfl

def rightEquiv : Low ≃ Low where
  toFun := rightMap
  invFun := rightInverse
  left_inv := by
    rintro ⟨a, b, c, d⟩
    cases a <;> cases b <;> cases c <;> cases d <;> rfl
  right_inv := by
    rintro ⟨a, b, c, d⟩
    cases a <;> cases b <;> cases c <;> cases d <;> rfl

def offsetEquiv : Low ≃ Low where
  toFun x := (!x.1, x.2)
  invFun x := (!x.1, x.2)
  left_inv := by rintro ⟨a, b⟩; cases a <;> rfl
  right_inv := by rintro ⟨a, b⟩; cases a <;> rfl

theorem matrices_decode (x : Low) :
    mv4 leftRows x = leftEquiv x ∧ mv4 rightRows x = rightEquiv x := by
  rcases x with ⟨a, b, c, d⟩
  cases a <;> cases b <;> cases c <;> cases d <;> decide

/-- Raw fields above bit 3 are literal identity rows and zero phase fields.
The first four rows contain no high bit. -/
theorem spectator_fields :
    leftRows.drop 4 = [16, 32, 64, 128, 256] ∧
    rightRows.drop 4 = [16, 32, 64, 128, 256] ∧
    leftQ.drop 4 = List.replicate 5 0 ∧ rightQ.drop 4 = List.replicate 5 0 ∧
    leftAlpha.drop 4 = List.replicate 5 0 ∧ rightAlpha.drop 4 = List.replicate 5 0 ∧
    (∀ r ∈ leftRows.take 4, r < 16) ∧ (∀ r ∈ rightRows.take 4, r < 16) ∧
    (∀ r ∈ leftQ.take 4, r < 16) ∧ (∀ r ∈ rightQ.take 4, r < 16) := by
  decide

private def bitVal (b : Bool) : Nat := if b then 1 else 0

/-- Literal qvalue convention on the four nonzero coordinates: each row's
strict upper tail contributes its parity, multiplied by 2, before mod 4. -/
def qvalue4 (Q alpha : List Nat) (x : Low) : Nat :=
  ((if x.1 then alpha.getD 0 0 else 0) +
   (if x.2.1 then alpha.getD 1 0 else 0) +
   (if x.2.2.1 then alpha.getD 2 0 else 0) +
   (if x.2.2.2 then alpha.getD 3 0 else 0) +
   2 * ((if x.1 then bitVal (((Q.getD 0 0).testBit 1 && x.2.1) ^^
       ((Q.getD 0 0).testBit 2 && x.2.2.1) ^^ ((Q.getD 0 0).testBit 3 && x.2.2.2)) else 0) +
     (if x.2.1 then bitVal (((Q.getD 1 0).testBit 2 && x.2.2.1) ^^
       ((Q.getD 1 0).testBit 3 && x.2.2.2)) else 0) +
     (if x.2.2.1 then bitVal ((Q.getD 2 0).testBit 3 && x.2.2.2) else 0))) % 4

def leftPhase (x : Low) : Nat := if x.1 then 2 else 0

def rightPhase (x : Low) : Nat :=
  ((if x.1 then 3 else 0) + (if x.2.1 then 3 else 0) +
    (if x.2.2.2 then 2 else 0) + (if x.1 && x.2.1 then 2 else 0)) % 4

theorem phases_decode (x : Low) :
    qvalue4 leftQ leftAlpha x = leftPhase x ∧
    qvalue4 rightQ rightAlpha x = rightPhase x := by
  rcases x with ⟨a, b, c, d⟩
  cases a <;> cases b <;> cases c <;> cases d <;> decide

section Payload
variable {S K : Type*} [CommSemiring K]

/-- For the selected record S is the remaining five address bits. The theorem
keeps any spectator type and an arbitrary complete payload on Low × S. -/
def liftAddress (e : Low ≃ Low) : (Low × S) ≃ (Low × S) :=
  Equiv.prodCongr e (Equiv.refl S)

def leftDecoded (omega : Kˣ) : (Low × S → K) ≃ₗ[K] (Low × S → K) :=
  CliffordMonomialDecoder.decoded omega (fun x => qvalue4 leftQ leftAlpha x.1) 0
    (liftAddress leftEquiv) (Equiv.refl _)

def rightDecoded (omega : Kˣ) : (Low × S → K) ≃ₗ[K] (Low × S → K) :=
  CliffordMonomialDecoder.decoded omega (fun x => qvalue4 rightQ rightAlpha x.1) 1
    (liftAddress rightEquiv) (liftAddress offsetEquiv)

theorem left_decoded_apply (omega : Kˣ) (v : Low × S → K) (x : Low) (s : S) :
    leftDecoded omega v (leftEquiv x, s) =
      (↑(omega ^ ((0 + leftPhase x) % 4)) : K) * v (x, s) := by
  have h := CliffordMonomialDecoder.decoded_apply_at omega
    (fun y : Low × S => qvalue4 leftQ leftAlpha y.1) 0
    (liftAddress leftEquiv) (Equiv.refl _) v (x, s)
  simpa only [leftDecoded, liftAddress, Equiv.prodCongr_apply, Prod.map_apply, Equiv.refl_apply,
    (phases_decode x).1] using h

theorem right_decoded_apply (omega : Kˣ) (v : Low × S → K) (x : Low) (s : S) :
    rightDecoded omega v (offsetEquiv (rightEquiv x), s) =
      (↑(omega ^ ((1 + rightPhase x) % 4)) : K) * v (x, s) := by
  have h := CliffordMonomialDecoder.decoded_apply_at omega
    (fun y : Low × S => qvalue4 rightQ rightAlpha y.1) 1
    (liftAddress rightEquiv) (liftAddress offsetEquiv) v (x, s)
  simpa only [rightDecoded, liftAddress, Equiv.prodCongr_apply, Prod.map_apply, Equiv.refl_apply,
    (phases_decode x).2] using h

end Payload
end CurrentMain.CliffordChild009Decoder

#print axioms CurrentMain.CliffordChild009Decoder.leftEquiv
#print axioms CurrentMain.CliffordChild009Decoder.rightEquiv
#print axioms CurrentMain.CliffordChild009Decoder.offsetEquiv
#print axioms CurrentMain.CliffordChild009Decoder.matrices_decode
#print axioms CurrentMain.CliffordChild009Decoder.spectator_fields
#print axioms CurrentMain.CliffordChild009Decoder.phases_decode
#print axioms CurrentMain.CliffordChild009Decoder.left_decoded_apply
#print axioms CurrentMain.CliffordChild009Decoder.right_decoded_apply
