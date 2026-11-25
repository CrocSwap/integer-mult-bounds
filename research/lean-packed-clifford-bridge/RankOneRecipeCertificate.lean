import CliffordChild009Canonical

/-!
Thin, phase-sensitive rank-one certificate interface for the pinned f19
Clifford recipes. Apache-2.0; prepared with OpenAI assistance. See NOTICE.md.

This reuses the accepted monomial decoder, Gaussian coefficients and PR509
child interface. A finite source supplier must bind every raw field, inverse,
canonical basis/Q, and all address cases. No selected certificate is assumed.
-/
namespace CurrentMain.RankOneRecipeCertificate

open CliffordMonomialDecoder
open CliffordChild009Canonical (imagUnit)

noncomputable section
variable {X : Type*}

def ca : ℂ := GaussianPhaseNormalization.a Complex.I ((2 : ℂ)⁻¹)
def cb : ℂ := GaussianPhaseNormalization.b Complex.I ((2 : ℂ)⁻¹)

/-- Retains the source input-coordinate phase, separate global phase, and both
actual affine address factors. Equivalences must be certified by the caller. -/
structure Monomial (X : Type*) where
  linear : X ≃ X
  offset : X ≃ X
  quadraticPhase : X → Nat
  globalPhase : Nat

def Monomial.preimage (M : Monomial X) (y : X) : X :=
  (M.linear.trans M.offset).symm y

def Monomial.exponent (M : Monomial X) (y : X) : Nat :=
  (M.globalPhase + M.quadraticPhase (M.preimage y)) % 4

def Monomial.operator (M : Monomial X) : (X → ℂ) ≃ₗ[ℂ] (X → ℂ) :=
  decoded imagUnit M.quadraticPhase M.globalPhase M.linear M.offset

theorem Monomial.operator_apply (M : Monomial X) (v : X → ℂ) (y : X) :
    M.operator v y = Complex.I ^ M.exponent y * v (M.preimage y) := by
  have h := decoded_apply_at imagUnit M.quadraticPhase M.globalPhase
    M.linear M.offset v (M.preimage y)
  change M.operator v ((M.linear.trans M.offset)
    ((M.linear.trans M.offset).symm y)) = _ at h
  rw [Equiv.apply_symm_apply] at h
  simpa only [Monomial.exponent, Units.val_pow_eq_pow_val] using h

/-- Source K is D_Q after P_G. The canonical phase is evaluated at its output. -/
def canonicalK (G : X ≃ X) (c : X → Nat) : (X → ℂ) ≃ₗ[ℂ] (X → ℂ) :=
  (push G).trans (diagonal imagUnit c)

theorem canonicalK_apply (G : X ≃ X) (c : X → Nat) (v : X → ℂ) (y : X) :
    canonicalK G c v y = Complex.I ^ c y * v (G.symm y) := rfl

/-- The XOR direction formula requires actual linearity and the exact first
column. An arbitrary address permutation is insufficient. -/
theorem transport_from_linearity (xor : X → X → X) (G : X ≃ X) (e0 u : X)
    (hlinear : ∀ x z, G (xor x z) = xor (G x) (G z)) (hfirst : G e0 = u)
    (y : X) : G (xor (G.symm y) e0) = xor y u := by
  rw [hlinear, Equiv.apply_symm_apply, hfirst]

def source0 (L R : Monomial X) (y : X) : X := R.preimage (L.preimage y)
def source1 (L R : Monomial X) (t : X → X) (y : X) : X :=
  R.preimage (t (L.preimage y))
def phase0 (L R : Monomial X) (y : X) : Nat :=
  L.exponent y + R.exponent (L.preimage y)
def phase1 (L R : Monomial X) (t : X → X) (y : X) : Nat :=
  L.exponent y + R.exponent (t (L.preimage y))

/-- Two finite alternatives, with the Gaussian a/b branch choice retained.
All congruences include the stored global and preimage phases. The swapped
alternative uses a=i*b. A finite checker must cover every address. -/
def Certificate (L R : Monomial X) (t out : X → X) (c : X → Nat) : Prop :=
  ∀ y,
    (source0 L R y = y ∧ source1 L R t y = out y ∧
      phase0 L R y % 4 = 0 ∧
      (phase1 L R t y + c (out y)) % 4 = c y % 4) ∨
    (source0 L R y = out y ∧ source1 L R t y = y ∧
      (phase0 L R y + c (out y) + 1) % 4 = c y % 4 ∧
      phase1 L R t y % 4 = 1)

private theorem phase_equal (n m : Nat) (h : n % 4 = m % 4) :
    Complex.I ^ n = Complex.I ^ m := by
  calc
    Complex.I ^ n = Complex.I ^ (n % 4) := pow_eq_pow_mod n Complex.I_pow_four
    _ = Complex.I ^ (m % 4) := congrArg (fun k => Complex.I ^ k) h
    _ = Complex.I ^ m := (pow_eq_pow_mod m Complex.I_pow_four).symm

private theorem ca_eq : ca = Complex.I * cb :=
  (GaussianPhaseNormalization.phase_coefficients Complex.I ((2 : ℂ)⁻¹)
    Complex.I_mul_I).1.symm

private theorem ca_phase (n : Nat) : ca * Complex.I ^ n = cb * Complex.I ^ (n + 1) := by
  rw [ca_eq, pow_succ]
  ring

private theorem cb_one_phase (n : Nat) : cb * Complex.I ^ (1 + n) = ca * Complex.I ^ n := by
  rw [ca_eq, pow_add, pow_one]
  ring

/-- The accepted monomial and Gaussian formulas reduce an arbitrary payload
to exactly two reads. No basis vector or zero-state restriction is used. -/
theorem sandwich_expand (L R : Monomial X) (G : X ≃ X) (c : X → Nat)
    (t : X → X) (C : (X → ℂ) ≃ₗ[ℂ] (X → ℂ))
    (hC : ∀ v y, C v y = ca * v y + cb * v (t y)) (v : X → ℂ) (y : X) :
    L.operator (C (R.operator (canonicalK G c v))) y =
      ca * Complex.I ^ (phase0 L R y + c (source0 L R y)) *
        v (G.symm (source0 L R y)) +
      cb * Complex.I ^ (phase1 L R t y + c (source1 L R t y)) *
        v (G.symm (source1 L R t y)) := by
  simp only [Monomial.operator_apply, hC, canonicalK_apply,
    source0, source1, phase0, phase1, pow_add]
  ring

/-- A finite two-branch certificate yields the entire interpreted rank-one
identity. The transport premise must come from the actual canonical basis;
`transport_from_linearity` gives the explicit XOR/first-column interface. -/
theorem sandwich_on_canonical (L R : Monomial X) (G : X ≃ X) (c : X → Nat)
    (t out : X → X) (C : (X → ℂ) ≃ₗ[ℂ] (X → ℂ))
    (hC : ∀ v y, C v y = ca * v y + cb * v (t y))
    (htransport : ∀ y, G (t (G.symm y)) = out y)
    (hcert : Certificate L R t out c) (v : X → ℂ) :
    L.operator (C (R.operator (canonicalK G c v))) = canonicalK G c (C v) := by
  funext y
  rw [sandwich_expand L R G c t C hC, canonicalK_apply, hC]
  have ht : G.symm (out y) = t (G.symm y) := by
    rw [← htransport y, Equiv.symm_apply_apply]
  rcases hcert y with ⟨hs0, hs1, he0, he1⟩ | ⟨hs0, hs1, he0, he1⟩
  · have h0 : Complex.I ^ (phase0 L R y + c y) = Complex.I ^ c y := by
      apply phase_equal
      rw [Nat.add_mod, he0, Nat.zero_add, Nat.mod_mod]
    have h1 := phase_equal _ _ he1
    rw [hs0, hs1, ht, h0, h1]
    ring
  · have h0 := phase_equal _ _ he0
    have h1 : Complex.I ^ (phase1 L R t y + c y) = Complex.I ^ (1 + c y) := by
      apply phase_equal
      calc
        (phase1 L R t y + c y) % 4 =
            (phase1 L R t y % 4 + c y % 4) % 4 := Nat.add_mod _ _ _
        _ = (1 + c y % 4) % 4 := by rw [he1]
        _ = (1 + c y) % 4 := (Nat.add_mod 1 (c y) 4).symm
    rw [hs0, hs1, ht, ca_phase, h0, h1, cb_one_phase]
    ring

/-- Direct old=[]→new singleton orientation. Cancelling the certified K gives
the all-payload operator equation consumed by DirectedChildRecipes. -/
theorem sandwich_operator (L R : Monomial X) (G : X ≃ X) (c : X → Nat)
    (t out : X → X) (C : (X → ℂ) ≃ₗ[ℂ] (X → ℂ))
    (hC : ∀ v y, C v y = ca * v y + cb * v (t y))
    (htransport : ∀ y, G (t (G.symm y)) = out y)
    (hcert : Certificate L R t out c) (v : X → ℂ) :
    L.operator (C (R.operator v)) =
      canonicalK G c (C ((canonicalK G c).symm v)) := by
  have h := sandwich_on_canonical L R G c t out C hC htransport hcert
    ((canonicalK G c).symm v)
  simpa only [LinearEquiv.apply_symm_apply] using h

end
end CurrentMain.RankOneRecipeCertificate

#print axioms CurrentMain.RankOneRecipeCertificate.Monomial.operator_apply
#print axioms CurrentMain.RankOneRecipeCertificate.canonicalK_apply
#print axioms CurrentMain.RankOneRecipeCertificate.transport_from_linearity
#print axioms CurrentMain.RankOneRecipeCertificate.sandwich_expand
#print axioms CurrentMain.RankOneRecipeCertificate.sandwich_on_canonical
#print axioms CurrentMain.RankOneRecipeCertificate.sandwich_operator
