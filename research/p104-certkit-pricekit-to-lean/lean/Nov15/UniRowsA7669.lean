/-
UniRowsA7669 (lane ROWS2, Nov 19).  KERNEL-CERTIFIED final rows of ALL 1501 public registers of the concrete word
t7669 under the #7113 caller:  `rows7669 : Rows7669`  (no premises).
From the generated PACKED reverse-mode certificate UniRowsA* (gen_rowsp.py SEEDS=all: one big Nat per co-row,
UniRowsPSound.prows_from_run) via `UniRows.A.rows_seeded`.  Kernel only: no sorry, no native_decide, no axioms
beyond propext / Classical.choice / Quot.sound.
-/
import Nov15.UniRowsAMain

namespace UniRows.A
open UniInhabit UniRows WordModel Uni UniFold7113

theorem seedsAll : ∀ r : R7, pub caller7113 r = true → Nat.testBit SMASK (idxOf r) = true := by decide +kernel

theorem rows7669 : Rows7669 := fun r hp => rows_seeded r hp (seedsAll r hp)

end UniRows.A

#print axioms UniRows.A.rows7669
