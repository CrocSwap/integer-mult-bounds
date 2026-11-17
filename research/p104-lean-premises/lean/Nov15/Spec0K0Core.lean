/-
core definitions for the k = 0 radical checks of SPECBREAK survivor #0 (RB6 step 4).
4x4 matrices as explicit 16-field structures (no Mathlib Matrix), jobs M_c = [[1,p,pq/2],[0,j,-q],[0,0,1]],
j = [[a,b],[c,-a]], E = diag(1,jE,1), F = diag(1,-jE,1).
-/
import Mathlib.Tactic.Ring
import Mathlib.Tactic.LinearCombination
import Mathlib.Algebra.Field.Defs
import Mathlib.Algebra.GroupWithZero.Basic

namespace Spec0K0

@[ext] structure M4 (K : Type*) where
  (m11 m12 m13 m14 : K)
  (m21 m22 m23 m24 : K)
  (m31 m32 m33 m34 : K)
  (m41 m42 m43 m44 : K)

variable {K : Type*} [Field K]

/-- matrix product, written out entrywise -/
def mm (A B : M4 K) : M4 K where
  m11 := A.m11*B.m11 + A.m12*B.m21 + A.m13*B.m31 + A.m14*B.m41
  m12 := A.m11*B.m12 + A.m12*B.m22 + A.m13*B.m32 + A.m14*B.m42
  m13 := A.m11*B.m13 + A.m12*B.m23 + A.m13*B.m33 + A.m14*B.m43
  m14 := A.m11*B.m14 + A.m12*B.m24 + A.m13*B.m34 + A.m14*B.m44
  m21 := A.m21*B.m11 + A.m22*B.m21 + A.m23*B.m31 + A.m24*B.m41
  m22 := A.m21*B.m12 + A.m22*B.m22 + A.m23*B.m32 + A.m24*B.m42
  m23 := A.m21*B.m13 + A.m22*B.m23 + A.m23*B.m33 + A.m24*B.m43
  m24 := A.m21*B.m14 + A.m22*B.m24 + A.m23*B.m34 + A.m24*B.m44
  m31 := A.m31*B.m11 + A.m32*B.m21 + A.m33*B.m31 + A.m34*B.m41
  m32 := A.m31*B.m12 + A.m32*B.m22 + A.m33*B.m32 + A.m34*B.m42
  m33 := A.m31*B.m13 + A.m32*B.m23 + A.m33*B.m33 + A.m34*B.m43
  m34 := A.m31*B.m14 + A.m32*B.m24 + A.m33*B.m34 + A.m34*B.m44
  m41 := A.m41*B.m11 + A.m42*B.m21 + A.m43*B.m31 + A.m44*B.m41
  m42 := A.m41*B.m12 + A.m42*B.m22 + A.m43*B.m32 + A.m44*B.m42
  m43 := A.m41*B.m13 + A.m42*B.m23 + A.m43*B.m33 + A.m44*B.m43
  m44 := A.m41*B.m14 + A.m42*B.m24 + A.m43*B.m34 + A.m44*B.m44

infixl:70 " ⊗ " => mm

def diag4 (a b c d : K) : M4 K := ⟨a,0,0,0, 0,b,0,0, 0,0,c,0, 0,0,0,d⟩
def Z4 : M4 K := diag4 1 (-1) (-1) 1
def I4 : M4 K := diag4 1 1 1 1
def zero4 : M4 K := diag4 0 0 0 0
/-- generic element of the unitriangular-block shape (1 | * * * ; 0 | 2x2 | * ; 0 0 0 1) -/
def nd (x12 x13 x14 x22 x23 x24 x32 x33 x34 : K) : M4 K :=
  ⟨1,x12,x13,x14, 0,x22,x23,x24, 0,x32,x33,x34, 0,0,0,1⟩

/-- job letter A..D -/
def MJ (a b c p1 p2 q1 q2 : K) : M4 K :=
  ⟨1,p1,p2,(p1*q1+p2*q2)/2, 0,a,b,-q1, 0,c,-a,-q2, 0,0,0,1⟩
def MEm (e1 e2 e3 : K) : M4 K := ⟨1,0,0,0, 0,e1,e2,0, 0,e3,-e1,0, 0,0,0,1⟩
def MFm (e1 e2 e3 : K) : M4 K := ⟨1,0,0,0, 0,-e1,-e2,0, 0,-e3,e1,0, 0,0,0,1⟩

/-- the five defining relations of a job (j² = 1, p(I+j)=0, (I+j)q=0), as polynomial = 0 -/
def JobOK (a b c p1 p2 q1 q2 : K) : Prop :=
  a^2 + b*c - 1 = 0 ∧ p1*(1+a) + p2*c = 0 ∧ p1*b + p2*(1-a) = 0 ∧
  (1+a)*q1 + b*q2 = 0 ∧ c*q1 + (1-a)*q2 = 0
def EpsOK (e1 e2 e3 : K) : Prop := e1^2 + e2*e3 - 1 = 0

/-- ω_μ = 2 U₁₄ − d₁ U₁₂ U₂₄ − d₂ U₁₃ U₃₄ -/
def omega (d1 d2 : K) (U : M4 K) : K := 2*U.m14 - d1*U.m12*U.m24 - d2*U.m13*U.m34
/-- (D U)² − I with D = diag(−1,d₁,d₂,−1) -/
def LLm (d1 d2 : K) (U : M4 K) : M4 K :=
  mm (mm (mm (diag4 (-1) d1 d2 (-1)) U) (diag4 (-1) d1 d2 (-1))) U |> fun X => ⟨X.m11-1,X.m12,X.m13,X.m14, X.m21,X.m22-1,X.m23,X.m24, X.m31,X.m32,X.m33-1,X.m34, X.m41,X.m42,X.m43,X.m44-1⟩

/-- the four unit-block relations: lower-right 2x2 block of U equals diag(d1,d2) -/
def UnitRel (d1 d2 : K) (U : M4 K) : Prop := U.m22 = d1 ∧ U.m23 = 0 ∧ U.m32 = 0 ∧ U.m33 = d2

/-- relations of a class: W3 = diag(1,-1,-1,1), W7 = I, units μ=1,2,5,6 -/
def Rel (w3 w7 u1 u2 u5 u6 : M4 K) : Prop :=
  w3 = Z4 ∧ w7 = I4 ∧ UnitRel (-1) 1 u1 ∧ UnitRel 1 (-1) u2 ∧ UnitRel 1 (-1) u5 ∧ UnitRel (-1) 1 u6

/-- kill conclusion for one unit: ω = 0 and (DU)² = I -/
def KU (d1 d2 : K) (U : M4 K) : Prop := omega d1 d2 U = 0 ∧ LLm d1 d2 U = zero4
def Kill (u1 u2 u5 u6 : M4 K) : Prop :=
  KU (-1) 1 u1 ∧ KU 1 (-1) u2 ∧ KU 1 (-1) u5 ∧ KU (-1) 1 u6

end Spec0K0
