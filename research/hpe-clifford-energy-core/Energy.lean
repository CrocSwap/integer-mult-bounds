/- Apache-2.0. Prepared for ywz65 with substantial OpenAI Codex assistance.
   Standalone integer energy law. This does not import the retained Mathlib
   HPE development; source correspondence is checked externally. -/
import Std

namespace HPEEnergy

abbrev Gaussian := Int × Int
def norm2 (z : Gaussian) : Int := z.1*z.1 + z.2*z.2
def energy : List Gaussian → Int
  | [] => 0
  | z :: zs => norm2 z + energy zs

def rotate (p : Fin 4) (z : Gaussian) : Gaussian :=
  match p.val with
  | 0 => z
  | 1 => (-z.2, z.1)
  | 2 => (-z.1, -z.2)
  | _ => (z.2, -z.1)

-- Same integer formula as HyperplaneEnd.Clifford.cgz, without the 1/2.
def cg (s : Bool) (a c : Gaussian) : Gaussian :=
  if s then (a.1-a.2+c.1+c.2, a.2+a.1+c.2-c.1)
  else (a.1+a.2+c.1-c.2, a.2-a.1+c.2+c.1)

theorem norm2_nonneg (z : Gaussian) : 0 ≤ norm2 z := by
  have h1 := Int.sq_nonneg z.1
  have h2 := Int.sq_nonneg z.2
  simp [Int.pow_succ] at h1 h2
  unfold norm2
  omega

theorem energy_nonneg (v : List Gaussian) : 0 ≤ energy v := by
  induction v with
  | nil => simp [energy]
  | cons z zs ih => have := norm2_nonneg z; simp only [energy]; omega

theorem rotate_energy (p : Fin 4) (z : Gaussian) : norm2 (rotate p z) = norm2 z := by
  rcases p with ⟨p, hp⟩
  have cases : p = 0 ∨ p = 1 ∨ p = 2 ∨ p = 3 := by omega
  rcases cases with h | h | h | h <;> subst p <;> simp [rotate, norm2] <;> grind

theorem cg_pair_energy (s : Bool) (a b : Gaussian) :
    norm2 (cg s a b) + norm2 (cg s b a) = 4*(norm2 a + norm2 b) := by
  cases s <;> simp [cg, norm2] <;> grind

theorem cg_fixed_energy (s : Bool) (a : Gaussian) :
    norm2 (cg s a a) = 4*norm2 a := by
  cases s <;> simp [cg, norm2] <;> grind

theorem perm_energy {v w : List Gaussian} (h : v.Perm w) : energy v = energy w := by
  induction h with
  | nil => rfl
  | cons a h ih => simp [energy, ih]
  | swap a b l => simp [energy]; grind
  | trans h1 h2 ih1 ih2 => exact ih1.trans ih2

-- Coordinate phases may vary; diagonal and global phases are both instances.
inductive Phases : List Gaussian → List Gaussian → Prop
  | nil : Phases [] []
  | cons (p : Fin 4) (z : Gaussian) {v w} :
      Phases v w → Phases (z::v) (rotate p z::w)

theorem phases_energy {v w : List Gaussian} (h : Phases v w) : energy w = energy v := by
  induction h with
  | nil => rfl
  | cons p z h ih => simp [energy, rotate_energy, ih]

-- An involution decomposes into fixed points and disjoint two-cycles.
-- The list must cover every coordinate; no coordinate may be dropped/copied.
inductive CMapped (s : Bool) : List Gaussian → List Gaussian → Prop
  | nil : CMapped s [] []
  | fixed (z : Gaussian) {v w} :
      CMapped s v w → CMapped s (z::v) (cg s z z::w)
  | pair (a b : Gaussian) {v w} :
      CMapped s v w → CMapped s (a::b::v) (cg s a b::cg s b a::w)

theorem cmapped_energy {s v w} (h : CMapped s v w) : energy w = 4*energy v := by
  induction h with
  | nil => simp [energy]
  | fixed z h ih => simp only [energy, cg_fixed_energy, ih]; grind
  | pair a b h ih =>
      have hp := cg_pair_energy s a b
      simp only [energy, ih]
      grind

inductive Step : Nat → List Gaussian → List Gaussian → Prop
  | perm {v w} : v.Perm w → Step 0 v w
  | phase {v w} : Phases v w → Step 0 v w
  | cgate {s v grouped mapped w} :
      v.Perm grouped → CMapped s grouped mapped → mapped.Perm w → Step 1 v w

theorem step_energy {k v w} (h : Step k v w) : energy w = (4:Int)^k * energy v := by
  cases h with
  | perm hp => simp [← perm_energy hp]
  | phase hp => simp [phases_energy hp]
  | cgate hp hc hq =>
      have h1 := perm_energy hp
      have h2 := cmapped_energy hc
      have h3 := perm_energy hq
      simp
      omega

inductive Run : Nat → List Gaussian → List Gaussian → Prop
  | nil (v) : Run 0 v v
  | cons {k n v w u} : Step k v w → Run n w u → Run (k+n) v u

theorem run_energy {k v w} (h : Run k v w) : energy w = (4:Int)^k * energy v := by
  induction h with
  | nil v => simp
  | cons hs hr ih =>
      rw [ih, step_energy hs, Int.pow_add]
      grind

theorem member_energy {z : Gaussian} {v : List Gaussian} (h : z ∈ v) : norm2 z ≤ energy v := by
  induction v with
  | nil => simp at h
  | cons a vs ih =>
      have ha := norm2_nonneg a
      have hv := energy_nonneg vs
      simp only [List.mem_cons] at h
      rcases h with h | h
      · subst z; simp only [energy]; omega
      · have := ih h; simp only [energy]; omega

-- For a basis input (energy 1), every real and imaginary integer coefficient
-- has square at most 4^k. Normalization by 2^k is not performed in this file.
theorem column_squared_bound {k v w} (h : Run k v w) (hv : energy v = 1)
    {z : Gaussian} (hz : z ∈ w) : z.1*z.1 ≤ (4:Int)^k ∧ z.2*z.2 ≤ (4:Int)^k := by
  have he := run_energy h
  have hm := member_energy hz
  have h1 := Int.sq_nonneg z.1
  have h2 := Int.sq_nonneg z.2
  simp [Int.pow_succ] at h1 h2
  rw [hv] at he
  simp only [Int.mul_one] at he
  unfold norm2 at hm
  omega

#print axioms cg_pair_energy
#print axioms cg_fixed_energy
#print axioms perm_energy
#print axioms phases_energy
#print axioms cmapped_energy
#print axioms step_energy
#print axioms run_energy
#print axioms column_squared_bound

end HPEEnergy
