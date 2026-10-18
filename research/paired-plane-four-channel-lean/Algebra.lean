import Std
set_option maxRecDepth 100000
set_option maxHeartbeats 40000000
namespace Four
open Lean.Grind
structure M (K : Type) where
  e00 : K
  e01 : K
  e02 : K
  e03 : K
  e10 : K
  e11 : K
  e12 : K
  e13 : K
  e20 : K
  e21 : K
  e22 : K
  e23 : K
  e30 : K
  e31 : K
  e32 : K
  e33 : K
variable {K : Type} [CommRing K]
def mul (a b : M K) : M K := ⟨a.e00*b.e00+a.e01*b.e10+a.e02*b.e20+a.e03*b.e30, a.e00*b.e01+a.e01*b.e11+a.e02*b.e21+a.e03*b.e31, a.e00*b.e02+a.e01*b.e12+a.e02*b.e22+a.e03*b.e32, a.e00*b.e03+a.e01*b.e13+a.e02*b.e23+a.e03*b.e33, a.e10*b.e00+a.e11*b.e10+a.e12*b.e20+a.e13*b.e30, a.e10*b.e01+a.e11*b.e11+a.e12*b.e21+a.e13*b.e31, a.e10*b.e02+a.e11*b.e12+a.e12*b.e22+a.e13*b.e32, a.e10*b.e03+a.e11*b.e13+a.e12*b.e23+a.e13*b.e33, a.e20*b.e00+a.e21*b.e10+a.e22*b.e20+a.e23*b.e30, a.e20*b.e01+a.e21*b.e11+a.e22*b.e21+a.e23*b.e31, a.e20*b.e02+a.e21*b.e12+a.e22*b.e22+a.e23*b.e32, a.e20*b.e03+a.e21*b.e13+a.e22*b.e23+a.e23*b.e33, a.e30*b.e00+a.e31*b.e10+a.e32*b.e20+a.e33*b.e30, a.e30*b.e01+a.e31*b.e11+a.e32*b.e21+a.e33*b.e31, a.e30*b.e02+a.e31*b.e12+a.e32*b.e22+a.e33*b.e32, a.e30*b.e03+a.e31*b.e13+a.e32*b.e23+a.e33*b.e33⟩
def one : M K := ⟨1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1⟩
def scale (c : K) (a : M K) : M K := ⟨c*a.e00, c*a.e01, c*a.e02, c*a.e03, c*a.e10, c*a.e11, c*a.e12, c*a.e13, c*a.e20, c*a.e21, c*a.e22, c*a.e23, c*a.e30, c*a.e31, c*a.e32, c*a.e33⟩
def det (a : M K) : K := a.e00*a.e11*a.e22*a.e33 - a.e00*a.e11*a.e23*a.e32 - a.e00*a.e12*a.e21*a.e33 + a.e00*a.e12*a.e23*a.e31 + a.e00*a.e13*a.e21*a.e32 - a.e00*a.e13*a.e22*a.e31 - a.e01*a.e10*a.e22*a.e33 + a.e01*a.e10*a.e23*a.e32 + a.e01*a.e12*a.e20*a.e33 - a.e01*a.e12*a.e23*a.e30 - a.e01*a.e13*a.e20*a.e32 + a.e01*a.e13*a.e22*a.e30 + a.e02*a.e10*a.e21*a.e33 - a.e02*a.e10*a.e23*a.e31 - a.e02*a.e11*a.e20*a.e33 + a.e02*a.e11*a.e23*a.e30 + a.e02*a.e13*a.e20*a.e31 - a.e02*a.e13*a.e21*a.e30 - a.e03*a.e10*a.e21*a.e32 + a.e03*a.e10*a.e22*a.e31 + a.e03*a.e11*a.e20*a.e32 - a.e03*a.e11*a.e22*a.e30 - a.e03*a.e12*a.e20*a.e31 + a.e03*a.e12*a.e21*a.e30
def adj (a : M K) : M K := ⟨(a.e11*a.e22*a.e33 - a.e11*a.e23*a.e32 - a.e12*a.e21*a.e33 + a.e12*a.e23*a.e31 + a.e13*a.e21*a.e32 - a.e13*a.e22*a.e31), -(a.e01*a.e22*a.e33 - a.e01*a.e23*a.e32 - a.e02*a.e21*a.e33 + a.e02*a.e23*a.e31 + a.e03*a.e21*a.e32 - a.e03*a.e22*a.e31), (a.e01*a.e12*a.e33 - a.e01*a.e13*a.e32 - a.e02*a.e11*a.e33 + a.e02*a.e13*a.e31 + a.e03*a.e11*a.e32 - a.e03*a.e12*a.e31), -(a.e01*a.e12*a.e23 - a.e01*a.e13*a.e22 - a.e02*a.e11*a.e23 + a.e02*a.e13*a.e21 + a.e03*a.e11*a.e22 - a.e03*a.e12*a.e21), -(a.e10*a.e22*a.e33 - a.e10*a.e23*a.e32 - a.e12*a.e20*a.e33 + a.e12*a.e23*a.e30 + a.e13*a.e20*a.e32 - a.e13*a.e22*a.e30), (a.e00*a.e22*a.e33 - a.e00*a.e23*a.e32 - a.e02*a.e20*a.e33 + a.e02*a.e23*a.e30 + a.e03*a.e20*a.e32 - a.e03*a.e22*a.e30), -(a.e00*a.e12*a.e33 - a.e00*a.e13*a.e32 - a.e02*a.e10*a.e33 + a.e02*a.e13*a.e30 + a.e03*a.e10*a.e32 - a.e03*a.e12*a.e30), (a.e00*a.e12*a.e23 - a.e00*a.e13*a.e22 - a.e02*a.e10*a.e23 + a.e02*a.e13*a.e20 + a.e03*a.e10*a.e22 - a.e03*a.e12*a.e20), (a.e10*a.e21*a.e33 - a.e10*a.e23*a.e31 - a.e11*a.e20*a.e33 + a.e11*a.e23*a.e30 + a.e13*a.e20*a.e31 - a.e13*a.e21*a.e30), -(a.e00*a.e21*a.e33 - a.e00*a.e23*a.e31 - a.e01*a.e20*a.e33 + a.e01*a.e23*a.e30 + a.e03*a.e20*a.e31 - a.e03*a.e21*a.e30), (a.e00*a.e11*a.e33 - a.e00*a.e13*a.e31 - a.e01*a.e10*a.e33 + a.e01*a.e13*a.e30 + a.e03*a.e10*a.e31 - a.e03*a.e11*a.e30), -(a.e00*a.e11*a.e23 - a.e00*a.e13*a.e21 - a.e01*a.e10*a.e23 + a.e01*a.e13*a.e20 + a.e03*a.e10*a.e21 - a.e03*a.e11*a.e20), -(a.e10*a.e21*a.e32 - a.e10*a.e22*a.e31 - a.e11*a.e20*a.e32 + a.e11*a.e22*a.e30 + a.e12*a.e20*a.e31 - a.e12*a.e21*a.e30), (a.e00*a.e21*a.e32 - a.e00*a.e22*a.e31 - a.e01*a.e20*a.e32 + a.e01*a.e22*a.e30 + a.e02*a.e20*a.e31 - a.e02*a.e21*a.e30), -(a.e00*a.e11*a.e32 - a.e00*a.e12*a.e31 - a.e01*a.e10*a.e32 + a.e01*a.e12*a.e30 + a.e02*a.e10*a.e31 - a.e02*a.e11*a.e30), (a.e00*a.e11*a.e22 - a.e00*a.e12*a.e21 - a.e01*a.e10*a.e22 + a.e01*a.e12*a.e20 + a.e02*a.e10*a.e21 - a.e02*a.e11*a.e20)⟩
theorem mul_assoc (a b c : M K) : mul (mul a b) c = mul a (mul b c) := by
  cases a; cases b; cases c
  simp only [mul, M.mk.injEq]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> grind
theorem mul_one (a : M K) : mul a one = a := by
  cases a
  simp only [mul, one, M.mk.injEq]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> grind
theorem one_mul (a : M K) : mul one a = a := by
  cases a
  simp only [mul, one, M.mk.injEq]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> grind
theorem scale_mul (t : K) (a b : M K) : mul (scale t a) b = scale t (mul a b) := by
  cases a; cases b
  simp only [mul, scale, M.mk.injEq]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> grind
theorem scale_scale (t u : K) (a : M K) : scale t (scale u a) = scale (t*u) a := by
  cases a
  simp only [scale, M.mk.injEq]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> grind
theorem scale_one (a : M K) : scale 1 a = a := by
  cases a
  simp only [scale, M.mk.injEq]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> grind
theorem adj_left (a : M K) : mul (adj a) a = scale (det a) one := by
  cases a
  simp only [adj, mul, det, scale, one, M.mk.injEq]
  refine ⟨?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_, ?_⟩ <;> grind
theorem det_one : det (one : M K) = 1 := by simp only [det, one]; grind
theorem det_mul (a b : M K) : det (mul a b) = det a * det b := by
  cases a; cases b
  simp only [det, mul]
  grind
end Four
#print axioms Four.det_mul
#print axioms Four.adj_left
