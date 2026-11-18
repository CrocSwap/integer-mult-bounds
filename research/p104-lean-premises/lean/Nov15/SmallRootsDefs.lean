/-
(Nov 17): definitions for the SMALLCALLER root conditions (algebraic core).  See SmallRoots.md.
Matrices are lists of rows over ℚ; every condition is a decidable Prop, so `decide +kernel` checks it.
Source of truth for the list of conditions: internal notes (check), cited per definition,
which AUDIT1.md:(1)-(2) verified against root_check_h.py (SPEC-level lines).
-/
import Mathlib.Data.Rat.Defs
import Mathlib.Algebra.BigOperators.Group.List.Basic
namespace SmallRoots

abbrev Mat := List (List ℚ)

/-- one stage = a consecutive pair of units (u0, u0+1) inside a coordinate mask (rc.py:ST[i]['units'],['mask']). -/
structure Stage where
  u0 : ℕ
  mask : List ℕ

def dotv (a b : List ℚ) : ℚ := (List.zipWith (· * ·) a b).sum
def idMat (n : ℕ) : Mat := (List.range n).map fun i => (List.range n).map fun j => if i = j then 1 else 0
def negIdMat (n : ℕ) : Mat := (List.range n).map fun i => (List.range n).map fun j => if i = j then -1 else 0
def col (W : Mat) (j : ℕ) : List ℚ := W.map fun r => r.getD j 0
/-- left action of the unit T = I - 2 x yᵀ:  W ↦ T W = W - 2 x (yᵀ W)  (rc.py lines "W = [[W[i][j] - 2*X[k][i]*d[j]"). -/
def applyUnit (n : ℕ) (x y : List ℚ) (W : Mat) : Mat :=
  let d := (List.range n).map fun j => dotv y (col W j)
  (List.zipWith (fun xi row => List.zipWith (fun w dj => w - 2 * xi * dj) row d) x W)
/-- prefix product T_{k-1} ⋯ T_0 (rc.py `pre[k]`). -/
def pref (n : ℕ) (X Y : Mat) (k : ℕ) : Mat :=
  ((List.zip X Y).take k).foldl (fun W p => applyUnit n p.1 p.2 W) (idMat n)

/-- W commutes with the coordinate projector onto `mask` (rc.py `comm`). -/
def commMask (n : ℕ) (mask : List ℕ) (W : Mat) : Prop :=
  ∀ i ∈ List.range n, ∀ j ∈ List.range n, (i ∈ mask ↔ ¬ j ∈ mask) → (W.getD i []).getD j 0 = 0
instance (n mask W) : Decidable (commMask n mask W) := by unfold commMask; infer_instance

/-- rc.py 'units inside mask'. -/
def inMask (n : ℕ) (X Y : Mat) (s : Stage) : Prop :=
  ∀ u ∈ [s.u0, s.u0 + 1], ∀ c ∈ List.range n, ¬ c ∈ s.mask → (X.getD u []).getD c 0 = 0 ∧ (Y.getD u []).getD c 0 = 0
instance (n X Y s) : Decidable (inMask n X Y s) := by unfold inMask; infer_instance

/-- All 0/1 assignments to `L` stage variables. -/
def bits : ℕ → List (List ℚ)
  | 0 => [[]]
  | L + 1 => (bits L).flatMap fun b => [0 :: b, 1 :: b]

/-- Symbolic endpoint M(D) evaluated at a numeric D: run the units in time order; right after the second unit of
stage i, multiply the rows of the coordinates in mask_i by D_i (rc.py section "symbolic endpoint"). -/
def scaleAfter (idx : ℕ) (st : List Stage) (D : List ℚ) (V : Mat) : Mat :=
  (List.zip st D).foldl (fun V p => if p.1.u0 + 1 = idx then
        (V.zipIdx.map fun rd => if rd.2 ∈ p.1.mask then rd.1.map (· * p.2) else rd.1) else V) V
def Mend (n : ℕ) (X Y : Mat) (st : List Stage) (D : List ℚ) : Mat :=
  (List.range X.length).foldl (fun W idx =>
    scaleAfter idx st D (applyUnit n (X.getD idx []) (Y.getD idx []) W)) (idMat n)
/-- target  -diag(∏_{i : r ∈ mask_i} D_i)  (rc.py `tgt`). -/
def tgtD (n : ℕ) (st : List Stage) (D : List ℚ) : Mat :=
  (List.range n).map fun r => (List.range n).map fun c =>
    if r = c then -((List.zip st D).map fun p => if r ∈ p.1.mask then p.2 else 1).prod else 0

/-- Certificate that a matrix A has rank ≥ n: rows rs, columns cs (n each, distinct) and an exact inverse B of the minor. -/
def rankCert (n : ℕ) (A : Mat) (c : List ℕ × List ℕ × Mat) : Prop :=
  c.1.length = n ∧ c.2.1.length = n ∧ c.1.Nodup ∧ c.2.1.Nodup ∧
  (c.1.map fun i => ((c.2.1.map fun j => (A.getD i []).getD j 0))).map
      (fun r => (List.range n).map fun j => dotv r (col c.2.2 j)) = idMat n
instance (n A c) : Decidable (rankCert n A c) := by unfold rankCert; infer_instance

def gram (X Y : Mat) : Mat := Y.map fun y => X.map fun x => dotv y x
/-- Reachability from vertex 0 in the Gram digraph (edge u→v iff G[v][u] ≠ 0 when fw, else G[u][v] ≠ 0): N rounds of closure. -/
def reach (G : Mat) (fw : Bool) : List ℕ :=
  let N := G.length
  (List.range N).foldl (fun S _ => (List.range N).filter fun v =>
      v ∈ S ∨ ∃ u ∈ S, (if fw then (G.getD v []).getD u 0 else (G.getD u []).getD v 0) ≠ 0) [0]

/-- The root conditions of SMALLCALLER rc.py `check`, for a k-stage two-arm root with N = n+2 units. -/
structure IsRoot (n : ℕ) (X Y : Mat) (st : List Stage) (pair : ℚ × ℚ) : Prop where
  shape : X.length = n + 2 ∧ Y.length = n + 2 ∧ (∀ r ∈ X, r.length = n) ∧ ∀ r ∈ Y, r.length = n
  isotropy : ∀ p ∈ List.zip X Y, dotv p.2 p.1 = 0                              -- rc.py 'isotropy'
  nonzero : ∀ p ∈ List.zip X Y, (∃ v ∈ p.1, v ≠ 0) ∧ ∃ v ∈ p.2, v ≠ 0           -- 'nonzero'
  product : pref n X Y (n + 2) = negIdMat n                                      -- 'product=-I'
  stages_ordered : (st.map (·.u0)).Pairwise (fun a b => a + 1 < b) ∧ ∀ s ∈ st, s.u0 + 1 < n + 2
                                                                                  -- 'stage units disjoint/consecutive/ordered'
  inside : ∀ s ∈ st, inMask n X Y s                                              -- 'units inside mask'
  mask_before : ∀ s ∈ st, commMask n s.mask (pref n X Y s.u0)                    -- 'mask|prefix before'
  mask_after : ∀ s ∈ st, commMask n s.mask (pref n X Y (s.u0 + 2))               -- 'mask|prefix after'
  symbolic : ∀ D ∈ bits st.length, Mend n X Y st D = tgtD n st D                 -- 'symbolic M(D)=-diag(prod D^eps)' (corners)
  pairs : ∀ s ∈ st, (dotv (Y.getD s.u0 []) (X.getD (s.u0 + 1) []), dotv (Y.getD (s.u0 + 1) []) (X.getD s.u0 [])) = pair
                                                                                  -- 'pair (alpha,beta)'
  rankG : ∃ c, rankCert n (gram X Y) c                                           -- 'rank G=n' (lower bound; ≤ n since G = Y Xᵀ)
  spanX : ∃ c, rankCert n X c                                                    -- 'x span' (rank X = n)
  spanY : ∃ c, rankCert n Y c                                                    -- 'y span'
  connected : (reach (gram X Y) true).length = n + 2 ∧ (reach (gram X Y) false).length = n + 2
                                                                                  -- 'Gram strongly connected'

end SmallRoots
