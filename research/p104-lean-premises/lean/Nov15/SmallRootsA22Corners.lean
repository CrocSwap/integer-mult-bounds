/-
the 16 corner evaluations of the symbolic endpoint M(D) for the 2|2 A root (own file: kernel memory per file).
Kernel only.
-/
import Nov15.SmallRootsData
namespace SmallRoots
namespace A22c
theorem corner0 : Mend 10 A22_X A22_Y A22_st ([0, 0, 0, 0] : List ℚ) = tgtD 10 A22_st ([0, 0, 0, 0] : List ℚ) := by decide +kernel
theorem corner1 : Mend 10 A22_X A22_Y A22_st ([1, 0, 0, 0] : List ℚ) = tgtD 10 A22_st ([1, 0, 0, 0] : List ℚ) := by decide +kernel
theorem corner2 : Mend 10 A22_X A22_Y A22_st ([0, 1, 0, 0] : List ℚ) = tgtD 10 A22_st ([0, 1, 0, 0] : List ℚ) := by decide +kernel
theorem corner3 : Mend 10 A22_X A22_Y A22_st ([1, 1, 0, 0] : List ℚ) = tgtD 10 A22_st ([1, 1, 0, 0] : List ℚ) := by decide +kernel
theorem corner4 : Mend 10 A22_X A22_Y A22_st ([0, 0, 1, 0] : List ℚ) = tgtD 10 A22_st ([0, 0, 1, 0] : List ℚ) := by decide +kernel
theorem corner5 : Mend 10 A22_X A22_Y A22_st ([1, 0, 1, 0] : List ℚ) = tgtD 10 A22_st ([1, 0, 1, 0] : List ℚ) := by decide +kernel
theorem corner6 : Mend 10 A22_X A22_Y A22_st ([0, 1, 1, 0] : List ℚ) = tgtD 10 A22_st ([0, 1, 1, 0] : List ℚ) := by decide +kernel
theorem corner7 : Mend 10 A22_X A22_Y A22_st ([1, 1, 1, 0] : List ℚ) = tgtD 10 A22_st ([1, 1, 1, 0] : List ℚ) := by decide +kernel
theorem corner8 : Mend 10 A22_X A22_Y A22_st ([0, 0, 0, 1] : List ℚ) = tgtD 10 A22_st ([0, 0, 0, 1] : List ℚ) := by decide +kernel
theorem corner9 : Mend 10 A22_X A22_Y A22_st ([1, 0, 0, 1] : List ℚ) = tgtD 10 A22_st ([1, 0, 0, 1] : List ℚ) := by decide +kernel
theorem corner10 : Mend 10 A22_X A22_Y A22_st ([0, 1, 0, 1] : List ℚ) = tgtD 10 A22_st ([0, 1, 0, 1] : List ℚ) := by decide +kernel
theorem corner11 : Mend 10 A22_X A22_Y A22_st ([1, 1, 0, 1] : List ℚ) = tgtD 10 A22_st ([1, 1, 0, 1] : List ℚ) := by decide +kernel
theorem corner12 : Mend 10 A22_X A22_Y A22_st ([0, 0, 1, 1] : List ℚ) = tgtD 10 A22_st ([0, 0, 1, 1] : List ℚ) := by decide +kernel
theorem corner13 : Mend 10 A22_X A22_Y A22_st ([1, 0, 1, 1] : List ℚ) = tgtD 10 A22_st ([1, 0, 1, 1] : List ℚ) := by decide +kernel
theorem corner14 : Mend 10 A22_X A22_Y A22_st ([0, 1, 1, 1] : List ℚ) = tgtD 10 A22_st ([0, 1, 1, 1] : List ℚ) := by decide +kernel
theorem corner15 : Mend 10 A22_X A22_Y A22_st ([1, 1, 1, 1] : List ℚ) = tgtD 10 A22_st ([1, 1, 1, 1] : List ℚ) := by decide +kernel
end A22c
end SmallRoots
