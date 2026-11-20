import Nov15.LinKbarBase
open Matrix Finset LinCore LinFinal
namespace P104
open P104Data

lemma kern_id2 : ∀ j a b : Fin 8,
    (∑ r : Fin 63, if (lamM.getD (2 * 8 + j.1) 0).testBit r.1 then lab (selTf r) a * lab (selSf r) b else 0) =
      (if a = 2 ∧ b = j then 1 else 0) + Bm 2 j * (if a = 0 ∧ b = 1 then 1 else 0) := by
  decide +kernel

lemma kern_id3 : ∀ j a b : Fin 8,
    (∑ r : Fin 63, if (lamM.getD (3 * 8 + j.1) 0).testBit r.1 then lab (selTf r) a * lab (selSf r) b else 0) =
      (if a = 3 ∧ b = j then 1 else 0) + Bm 3 j * (if a = 0 ∧ b = 1 then 1 else 0) := by
  decide +kernel

end P104
