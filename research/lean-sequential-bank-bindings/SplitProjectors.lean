import Lean

/-!
Algebraic partial-swap identities used by BANK-SCHEDULE. M is a commutative ring, including a coordinate-vector ring with pointwise
products; no projector is required to preserve multiplication. This permits oblique split projectors: no symmetry, positivity,
inner product, characteristic restriction, or coordinate-projector hypothesis.
The displayed swap uses aligned atom coordinates (H,C_n D); atom reversal is
restored by the exact change of coordinates in AtomReversal below.
-/
namespace CurrentMain.SplitProjectors
open Lean.Grind

universe u
variable {M : Type u} [CommRing M]

structure AdditiveEnd (M : Type u) [CommRing M] where
  map : M → M
  map_add : ∀ x y, map (x + y) = map x + map y
  map_sub : ∀ x y, map (x - y) = map x - map y

theorem AdditiveEnd.map_zero (p : AdditiveEnd M) : p.map 0 = 0 := by
  have hh := p.map_sub (0 : M) 0
  simpa only [Ring.sub_self] using hh

/-- In aligned atom coordinates, D_P=(I-P,P;P,I-P). -/
def partialSwap (p : M → M) (z : M × M) : M × M :=
  (z.1 - p z.1 + p z.2, z.2 - p z.2 + p z.1)

def endSub (p s : AdditiveEnd M) : AdditiveEnd M where
  map x := p.map x - s.map x
  map_add x y := by simp only [p.map_add, s.map_add]; grind
  map_sub x y := by simp only [p.map_sub, s.map_sub]; grind

def endAdd (p s : AdditiveEnd M) : AdditiveEnd M where
  map x := p.map x + s.map x
  map_add x y := by simp only [p.map_add, s.map_add]; grind
  map_sub x y := by simp only [p.map_sub, s.map_sub]; grind

def endZero : AdditiveEnd M where
  map _ := 0
  map_add _ _ := by grind
  map_sub _ _ := by grind

def endId : AdditiveEnd M where
  map x := x
  map_add _ _ := rfl
  map_sub _ _ := rfl

/-- Every additive idempotent gives an involution on arbitrary dirty contents. -/
theorem partialSwap_involution (p : AdditiveEnd M)
    (idempotent : ∀ x, p.map (p.map x) = p.map x) (z : M × M) :
    partialSwap p.map (partialSwap p.map z) = z := by
  apply Prod.ext <;>
    simp only [partialSwap, p.map_add, p.map_sub, idempotent] <;> grind

/-- The nested raw endpoint is D_(P_A-P_S), with no symmetry assumption. -/
theorem nested_raw_endpoint (p s : AdditiveEnd M)
    (nested : ∀ x, p.map (s.map x) = s.map x) (z : M × M) :
    partialSwap p.map (partialSwap s.map z) = partialSwap (endSub p s).map z := by
  apply Prod.ext <;>
    simp only [partialSwap, endSub, p.map_add, p.map_sub, nested] <;> grind

/-- A nested difference is itself an idempotent. -/
theorem nested_difference_idempotent (p s : AdditiveEnd M)
    (pp : ∀ x, p.map (p.map x) = p.map x)
    (ss : ∀ x, s.map (s.map x) = s.map x)
    (ps : ∀ x, p.map (s.map x) = s.map x)
    (sp : ∀ x, s.map (p.map x) = s.map x) (x : M) :
    (endSub p s).map ((endSub p s).map x) = (endSub p s).map x := by
  simp only [endSub, p.map_sub, s.map_sub, pp, ss, ps, sp]
  grind

/-- Disjoint projector contributions add under completed partial swaps. -/
theorem disjoint_product (p q : AdditiveEnd M)
    (pq : ∀ x, p.map (q.map x) = 0) (z : M × M) :
    partialSwap p.map (partialSwap q.map z) = partialSwap (endAdd p q).map z := by
  apply Prod.ext <;>
    simp only [partialSwap, endAdd, p.map_add, p.map_sub, pq] <;> grind

theorem disjoint_commute (p q : AdditiveEnd M)
    (pq : ∀ x, p.map (q.map x) = 0)
    (qp : ∀ x, q.map (p.map x) = 0) (z : M × M) :
    partialSwap p.map (partialSwap q.map z) =
      partialSwap q.map (partialSwap p.map z) := by
  rw [disjoint_product p q pq, disjoint_product q p qp]
  apply Prod.ext <;> simp only [partialSwap, endAdd] <;> grind

def sumEnds : List (AdditiveEnd M) → AdditiveEnd M
  | [] => endZero
  | p :: ps => endAdd p (sumEnds ps)

def runSwaps : List (AdditiveEnd M) → (M × M) → (M × M)
  | [], z => z
  | p :: ps, z => partialSwap p.map (runSwaps ps z)

/-- Pairwise annihilation, including exactly the pairs in the actual list. -/
def DisjointList : List (AdditiveEnd M) → Prop
  | [] => True
  | p :: ps => (∀ q, q ∈ ps → ∀ x, p.map (q.map x) = 0) ∧ DisjointList ps

theorem annihilates_sum (p : AdditiveEnd M) (ps : List (AdditiveEnd M))
    (h : ∀ q, q ∈ ps → ∀ x, p.map (q.map x) = 0) (x : M) :
    p.map ((sumEnds ps).map x) = 0 := by
  induction ps with
  | nil => exact p.map_zero
  | cons q qs ih =>
    simp only [sumEnds, endAdd, p.map_add]
    rw [h q (by simp), ih (fun t ht => h t (by simp [ht]))]
    exact Semiring.zero_add 0

theorem disjoint_list_product (ps : List (AdditiveEnd M))
    (h : DisjointList ps) (z : M × M) :
    runSwaps ps z = partialSwap (sumEnds ps).map z := by
  induction ps with
  | nil => simp only [runSwaps, sumEnds, endZero, partialSwap]; apply Prod.ext <;> grind
  | cons p ps ih =>
    rw [runSwaps, ih h.2]
    exact disjoint_product p (sumEnds ps) (annihilates_sum p ps h.1) z

/-- A complete disjoint partition has the full-bank interchange endpoint. -/
theorem complete_partition_endpoint (ps : List (AdditiveEnd M))
    (h : DisjointList ps) (partition : ∀ x, (sumEnds ps).map x = x)
    (z : M × M) : runSwaps ps z = (z.2, z.1) := by
  rw [disjoint_list_product ps h]
  apply Prod.ext <;> simp only [partialSwap, partition] <;> grind

end CurrentMain.SplitProjectors

#print axioms CurrentMain.SplitProjectors.AdditiveEnd.map_zero
#print axioms CurrentMain.SplitProjectors.partialSwap_involution
#print axioms CurrentMain.SplitProjectors.nested_raw_endpoint
#print axioms CurrentMain.SplitProjectors.nested_difference_idempotent
#print axioms CurrentMain.SplitProjectors.disjoint_product
#print axioms CurrentMain.SplitProjectors.disjoint_commute
#print axioms CurrentMain.SplitProjectors.annihilates_sum
#print axioms CurrentMain.SplitProjectors.disjoint_list_product
#print axioms CurrentMain.SplitProjectors.complete_partition_endpoint
