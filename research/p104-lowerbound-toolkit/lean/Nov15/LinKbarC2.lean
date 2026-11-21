import Nov15.LinKbarBase
open Matrix Finset LinCore LinFinal
namespace P104
open P104Data

lemma kern_id4 : ∀ j a b : Fin 8,
    (∑ r : Fin 63, if (lamM.getD (4 * 8 + j.1) 0).testBit r.1 then lab (selTf r) a * lab (selSf r) b else 0) =
      (if a = 4 ∧ b = j then 1 else 0) + Bm 4 j * (if a = 0 ∧ b = 1 then 1 else 0) := by
  decide +kernel

lemma kern_id5 : ∀ j a b : Fin 8,
    (∑ r : Fin 63, if (lamM.getD (5 * 8 + j.1) 0).testBit r.1 then lab (selTf r) a * lab (selSf r) b else 0) =
      (if a = 5 ∧ b = j then 1 else 0) + Bm 5 j * (if a = 0 ∧ b = 1 then 1 else 0) := by
  decide +kernel

end P104
