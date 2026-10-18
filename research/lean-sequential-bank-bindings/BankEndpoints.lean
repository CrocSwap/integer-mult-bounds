import BankRouting
import CoordinatePartitions
import ExactFrameTransport

/-!
Exact operator bridge for bank routing. Every bank has one common chart.
A source physical core's arbitrary-content raw endpoint remains an explicit
input; these theorems derive the projector simplification, routed conjugation,
partition product, and common-chart endpoint once that input is established.
-/
namespace CurrentMain.BankEndpoints
open Lean.Grind CurrentMain.SplitProjectors CurrentMain.FrameTransport

universe u v w

structure GroupAction {G : Type u} (A : BankRouting.GroupLaws G) (V : Type v) where
  act : G → V → V
  mul_act : ∀ g h x, act (A.mul g h) x = act g (act h x)
  one_act : ∀ x, act A.one x = x

def actionFrame {G : Type u} {V : Type v} {A : BankRouting.GroupLaws G}
    (a : GroupAction A V) (g : G) : Frame V where
  encode := a.act g
  decode := a.act (A.inv g)
  left_inverse x := by rw [← a.mul_act, A.inv_mul, a.one_act]
  right_inverse x := by rw [← a.mul_act, A.mul_inv, a.one_act]

theorem action_conjugate_product {G : Type u} {V : Type v} {A : BankRouting.GroupLaws G}
    (a : GroupAction A V) (g h : G) (op : V → V) (x : V) :
    conjugate (actionFrame a (A.mul g h)) op x =
      conjugate (actionFrame a g) (conjugate (actionFrame a h) op) x := by
  simp only [conjugate, actionFrame, BankRouting.inverse_product, a.mul_act]

/-- The routing orientation g H⁻¹ is forced by the exact operator identity. -/
theorem routed_conjugation {G : Type u} {V : Type v} {A : BankRouting.GroupLaws G}
    (a : GroupAction A V) (g H : G) (residual coordinate : V → V)
    (embedding : ∀ x, conjugate (actionFrame a H) residual x = coordinate x) (x : V) :
    conjugate (actionFrame a g) residual x =
      conjugate (actionFrame a (BankRouting.route A g H)) coordinate x := by
  have hg : g = A.mul (BankRouting.route A g H) H :=
    (BankRouting.origin_route A g H).symm
  conv => lhs; rw [hg]
  rw [action_conjugate_product]
  exact congrArg (actionFrame a (BankRouting.route A g H)).encode (embedding _)

section Additive
variable {M : Type u} [CommRing M]

/-- A genuine additive automorphism, retaining its exact inverse. -/
structure AdditiveChart (M : Type u) [CommRing M] extends Frame M where
  encode_add : ∀ x y, encode (x + y) = encode x + encode y
  encode_sub : ∀ x y, encode (x - y) = encode x - encode y

theorem chart_decode_add (C : AdditiveChart M) (x y : M) :
    C.decode (x + y) = C.decode x + C.decode y := by
  have h := C.encode_add (C.decode x) (C.decode y)
  rw [C.right_inverse, C.right_inverse] at h
  exact (congrArg C.decode h).symm.trans (C.left_inverse _)

theorem chart_decode_sub (C : AdditiveChart M) (x y : M) :
    C.decode (x - y) = C.decode x - C.decode y := by
  have h := C.encode_sub (C.decode x) (C.decode y)
  rw [C.right_inverse, C.right_inverse] at h
  exact (congrArg C.decode h).symm.trans (C.left_inverse _)

def conjugatedEnd (C : AdditiveChart M) (p : AdditiveEnd M) : AdditiveEnd M where
  map x := C.encode (p.map (C.decode x))
  map_add x y := by rw [chart_decode_add, p.map_add, C.encode_add]
  map_sub x y := by rw [chart_decode_sub, p.map_sub, C.encode_sub]

def pairChart (C : Frame M) : Frame (M × M) where
  encode z := (C.encode z.1, C.encode z.2)
  decode z := (C.decode z.1, C.decode z.2)
  left_inverse z := by simp only [C.left_inverse]
  right_inverse z := by simp only [C.right_inverse]

/-- Similarity of arbitrary split projectors transports the actual partial swap. -/
theorem partialSwap_similarity (C : AdditiveChart M) (p : AdditiveEnd M) (z : M × M) :
    conjugate (pairChart C.toFrame) (partialSwap p.map) z =
      partialSwap (conjugatedEnd C p).map z := by
  apply Prod.ext <;>
    simp only [conjugate, pairChart, partialSwap, conjugatedEnd,
      C.encode_add, C.encode_sub, C.right_inverse]

/-- Conjugation preserves idempotence, including oblique projectors. -/
theorem conjugated_idempotent (C : AdditiveChart M) (p : AdditiveEnd M)
    (hp : ∀ x, p.map (p.map x) = p.map x) (x : M) :
    (conjugatedEnd C p).map ((conjugatedEnd C p).map x) = (conjugatedEnd C p).map x := by
  simp only [conjugatedEnd, C.left_inverse, hp]

/-- C acts on the second bank only, giving the source atom-reversal convention. -/
def reversalChart (c : AdditiveEnd M) (cc : ∀ x, c.map (c.map x) = x) : Frame (M × M) where
  encode z := (z.1, c.map z.2)
  decode z := (z.1, c.map z.2)
  left_inverse z := by simp only [cc]
  right_inverse z := by simp only [cc]

/-- The literal source block operator (I-P, PC; CP, I-CPC). -/
def physicalSwap (c p : AdditiveEnd M) (z : M × M) : M × M :=
  (z.1 - p.map z.1 + p.map (c.map z.2),
   c.map (p.map z.1) + z.2 - c.map (p.map (c.map z.2)))

theorem atom_reversal_formula (c p : AdditiveEnd M)
    (cc : ∀ x, c.map (c.map x) = x) (z : M × M) :
    conjugate (reversalChart c cc) (partialSwap p.map) z = physicalSwap c p z := by
  apply Prod.ext <;>
    simp only [conjugate, reversalChart, partialSwap, physicalSwap,
      c.map_add, c.map_sub, cc] <;> grind

/-- The physical partial swap with reversal is also an involution. -/
theorem physicalSwap_involution (c p : AdditiveEnd M)
    (cc : ∀ x, c.map (c.map x) = x)
    (pp : ∀ x, p.map (p.map x) = p.map x) (z : M × M) :
    physicalSwap c p (physicalSwap c p z) = z := by
  rw [← atom_reversal_formula c p cc, ← atom_reversal_formula c p cc]
  rw [conjugate_comp]
  simp only [conjugate, partialSwap_involution p pp]
  exact (reversalChart c cc).right_inverse z

/-- Restores the full source convention in the nested raw endpoint. -/
theorem physical_nested_endpoint (c p s : AdditiveEnd M)
    (cc : ∀ x, c.map (c.map x) = x)
    (ps : ∀ x, p.map (s.map x) = s.map x) (z : M × M) :
    physicalSwap c p (physicalSwap c s z) = physicalSwap c (endSub p s) z := by
  rw [← atom_reversal_formula c p cc, ← atom_reversal_formula c s cc, conjugate_comp]
  simp only [conjugate, nested_raw_endpoint p s ps]
  exact atom_reversal_formula c (endSub p s) cc z

/-- Right-associated completed products; no live physical cores are interleaved. -/
def runCompleted {V : Type v} : List (V → V) → V → V
  | [], x => x
  | op :: ops, x => op (runCompleted ops x)

theorem common_chart_product {V : Type v} (C : Frame V) (ops : List (V → V)) (x : V) :
    runCompleted (ops.map (conjugate C)) x = conjugate C (runCompleted ops) x := by
  induction ops generalizing x with
  | nil => exact (C.right_inverse x).symm
  | cons op ops ih =>
    simp only [List.map_cons, runCompleted]
    rw [ih, conjugate_comp]

theorem run_completed_swaps (ps : List (AdditiveEnd M)) (z : M × M) :
    runCompleted (ps.map (fun p => partialSwap p.map)) z = runSwaps ps z := by
  induction ps with
  | nil => rfl
  | cons p ps ih => simp only [List.map_cons, runCompleted, runSwaps, ih]

/-- A single arbitrary common bank chart transports the complete partition.
It may include atom reversal, g, and the ancestor-dependent weight, but it
cannot depend on the fresh role being multiplied. -/
theorem weighted_partition_endpoint (C : Frame (M × M))
    (ps : List (AdditiveEnd M)) (hd : DisjointList ps)
    (hp : ∀ x, (sumEnds ps).map x = x) (z : M × M) :
    runCompleted (ps.map (fun p => conjugate C (partialSwap p.map))) z =
      C.encode ((C.decode z).2, (C.decode z).1) := by
  have h := common_chart_product C (ps.map (fun p => partialSwap p.map)) z
  simp only [List.map_map, Function.comp_def] at h
  rw [h]
  simp only [conjugate, run_completed_swaps, complete_partition_endpoint ps hd hp]

end Additive
end CurrentMain.BankEndpoints

#print axioms CurrentMain.BankEndpoints.action_conjugate_product
#print axioms CurrentMain.BankEndpoints.routed_conjugation
#print axioms CurrentMain.BankEndpoints.chart_decode_add
#print axioms CurrentMain.BankEndpoints.chart_decode_sub
#print axioms CurrentMain.BankEndpoints.partialSwap_similarity
#print axioms CurrentMain.BankEndpoints.conjugated_idempotent
#print axioms CurrentMain.BankEndpoints.atom_reversal_formula
#print axioms CurrentMain.BankEndpoints.physicalSwap_involution
#print axioms CurrentMain.BankEndpoints.physical_nested_endpoint
#print axioms CurrentMain.BankEndpoints.common_chart_product
#print axioms CurrentMain.BankEndpoints.run_completed_swaps
#print axioms CurrentMain.BankEndpoints.weighted_partition_endpoint
