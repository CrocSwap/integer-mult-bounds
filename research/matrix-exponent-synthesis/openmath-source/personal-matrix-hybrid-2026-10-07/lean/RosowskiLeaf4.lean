import BlockComposition
import RosowskiEven
import Mathlib.Logic.Equiv.Fin.Basic
import Mathlib.Tactic.FinCases

namespace PersonalMatrix.Leaf46
open PersonalMatrix.Hybrid
open scoped BigOperators
variable {K : Type*} [CommRing K]
set_option maxHeartbeats 2000000
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
abbrev G := RosowskiEven.Gates (Fin 4) (Fin 2) (Fin 3)

def boolNumber : Bool ≃ Fin 2 where
  toFun x := if x then 1 else 0
  invFun i := i.val == 1
  left_inv := by intro x; cases x <;> rfl
  right_inv := by intro i; fin_cases i <;> rfl

def rowMap : Fin 2 × Bool ≃ Fin 4 :=
  ((Equiv.refl (Fin 2)).prodCongr boolNumber).trans finProdFinEquiv

def colMap : Option (Fin 3) ≃ Fin 4 := (finSuccEquiv 3).symm

def pairNumber : Fin 4 × Fin 2 ≃ Fin 8 := finProdFinEquiv
def qNumber : Fin 2 × Fin 3 ≃ Fin 6 := finProdFinEquiv
def mNumber : (Fin 4 × Fin 2) × Fin 3 ≃ Fin 24 :=
  (pairNumber.prodCongr (Equiv.refl (Fin 3))).trans finProdFinEquiv

def gateNumber : G ≃ Fin 46 :=
  (Equiv.sumCongr
    ((Equiv.sumCongr pairNumber pairNumber).trans finSumFinEquiv)
    ((Equiv.sumCongr qNumber mNumber).trans finSumFinEquiv)).trans finSumFinEquiv

def atom (p : Input 4) : Input 4 → K := fun q => if q=p then 1 else 0

theorem atom_value (p : Input 4) (X Y : Square (K := K) 4) :
    scalarLinear (atom p) X Y = inputValue X Y p := by
  simp [scalarLinear,atom]

theorem linear_add (c d : Input 4 → K) (X Y : Square (K := K) 4) :
    scalarLinear (c+d) X Y = scalarLinear c X Y + scalarLinear d X Y := by
  simp [scalarLinear,add_mul,Finset.sum_add_distrib]

theorem linear_sub (c d : Input 4 → K) (X Y : Square (K := K) 4) :
    scalarLinear (c-d) X Y = scalarLinear c X Y - scalarLinear d X Y := by
  simp [scalarLinear,sub_mul,Finset.sum_sub_distrib]

def ax (i : Fin 4) (h : Fin 2) (side : Bool) : Input 4 → K := atom (.inl (i,rowMap (h,side)))
def byy (h : Fin 2) (side : Bool) (j : Option (Fin 3)) : Input 4 → K :=
  atom (.inr (rowMap (h,side),colMap j))

def leftCoeff : G → Input 4 → K
  | .inl (.inl (i,h)) => ax i h false
  | .inl (.inr (i,h)) => ax i h true
  | .inr (.inl (h,j)) => byy h true (some j)
  | .inr (.inr ((i,h),j)) => ax i h false + byy h true (some j)

def rightCoeff : G → Input 4 → K
  | .inl (.inl (i,h)) => byy h false none + ax i h true
  | .inl (.inr (i,h)) => byy h true none - ax i h false
  | .inr (.inl (h,j)) => byy h false none + byy h false (some j)
  | .inr (.inr ((i,h),j)) => ax i h true + byy h false none + byy h false (some j)

def weight (i : Fin 4) (j : Option (Fin 3)) : G → K
  | .inl (.inl (i',_h)) => if i'=i then (if j=none then 1 else -1) else 0
  | .inl (.inr (i',_h)) => if i'=i ∧ j=none then 1 else 0
  | .inr (.inl (_h,j')) => if j=some j' then -1 else 0
  | .inr (.inr ((i',_h),j')) => if i'=i ∧ j=some j' then 1 else 0

def leaf : Leaf K 4 46 where
  left g := leftCoeff (gateNumber.symm g)
  right g := rightCoeff (gateNumber.symm g)
  output i j g := weight i (colMap.symm j) (gateNumber.symm g)

def pairedA (X : Square (K := K) 4) : Matrix (Fin 4) (Fin 2×Bool) K :=
  X.submatrix id rowMap

def pairedB (Y : Square (K := K) 4) : Matrix (Fin 2×Bool) (Option (Fin 3)) K :=
  Y.submatrix rowMap colMap

theorem products_match (X Y : Square (K := K) 4) (g : Fin 46) :
    leafProducts (leaf (K := K)) X Y g =
      RosowskiEven.products (pairedA X) (pairedB Y) (gateNumber.symm g) := by
  simp only [leafProducts,leaf]
  generalize gateNumber.symm g = t
  rcases t with (p | q)
  · rcases p with (⟨i,h⟩ | ⟨i,h⟩) <;>
      simp [leftCoeff,rightCoeff,linear_add,linear_sub,ax,byy,atom_value,
        pairedA,pairedB,Matrix.submatrix,inputValue,RosowskiEven.products]
  · rcases q with (⟨h,j⟩ | ⟨⟨i,h⟩,j⟩) <;>
      simp [leftCoeff,rightCoeff,linear_add,linear_sub,ax,byy,atom_value,
        pairedA,pairedB,Matrix.submatrix,inputValue,RosowskiEven.products]

theorem sum_row_selector {H : Type*} [Fintype H] (f : Fin 4 → H → K) (i : Fin 4) :
    (∑ x : Fin 4, ∑ h : H, if x=i then f x h else 0) = ∑ h : H, f i h := by
  rw [Finset.sum_comm]
  simp

theorem weighted_reconstruction (v : G → K) (i : Fin 4) (j : Option (Fin 3)) :
    (∑ t : G, weight i j t * v t) = RosowskiEven.reconstruct v i j := by
  cases j <;>
    simp [weight,RosowskiEven.reconstruct,RosowskiEven.Gates,Fintype.sum_sum_type,
      Fintype.sum_prod_type,ite_and,ite_mul,Finset.sum_add_distrib,Finset.sum_sub_distrib,Finset.sum_ite_irrel]
  all_goals simp_rw [sum_row_selector] <;> simp only [Finset.sum_neg_distrib] <;> ring

theorem valid : LeafValid (leaf (K := K)) := by
  intro X Y
  ext i j
  calc
    leafEval (leaf (K := K)) X Y i j =
        ∑ g : Fin 46, weight i (colMap.symm j) (gateNumber.symm g) *
          RosowskiEven.products (pairedA X) (pairedB Y) (gateNumber.symm g) := by
      unfold leafEval leafReconstruct
      apply Finset.sum_congr rfl
      intro g _
      rw [products_match]
      rfl
    _ = ∑ t : G, weight i (colMap.symm j) t * RosowskiEven.products (pairedA X) (pairedB Y) t :=
      gateNumber.symm.sum_comp (fun t : G => weight i (colMap.symm j) t *
        RosowskiEven.products (pairedA X) (pairedB Y) t)
    _ = RosowskiEven.reconstruct (RosowskiEven.products (pairedA X) (pairedB Y)) i (colMap.symm j) :=
      weighted_reconstruction _ _ _
    _ = (pairedA X * pairedB Y) i (colMap.symm j) :=
      congrArg (fun M => M i (colMap.symm j)) (RosowskiEven.sound (pairedA X) (pairedB Y))
    _ = (X*Y) i j := by
      unfold pairedA pairedB
      rw [Matrix.submatrix_mul_equiv X Y id rowMap colMap]
      simp [Matrix.submatrix]

#print axioms products_match
#print axioms weighted_reconstruction
#print axioms valid
#check @valid
end PersonalMatrix.Leaf46
