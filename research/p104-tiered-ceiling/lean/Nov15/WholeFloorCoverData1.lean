import Nov15.NumCertK

/-!
WholeFloorCoverData1 : discharges the interval-cover hypothesis of WholeFloorNest.kappa_whole_floor_nested
with kernel interval library (NumCertK): the fixed #7113 caller C(8|9) = caller 6 7 at 17 calls on the
floor native `natFloor` has F(s) < 0 for every s in [0, 1 - .0204110964]. Kernel only; no native_decide.
-/
namespace WholeFloorCover
open NumCertK

/-- F of (caller 6 7) + 17 * natFloor, merged by rank. -/
def cfW : CF := [(1, -3648), (2, 1496), (8, -7456), (9, 384),
  (16, -416), (17, 416), (24, -416), (25, 416), (32, -416), (33, 416), (40, -416), (41, 416), (48, -416),
  (49, 416), (56, -416), (57, 416), (64, -208), (65, 416), (73, 208), (137, 208)]

theorem cfW_ok : okR cfW := by decide +kernel
theorem cfW_p1 : Fup cfW 0 (73/250) < 0 := by decide +kernel
theorem cfW_p2 : Fup cfW (73/250) (59/125) < 0 := by decide +kernel
theorem cfW_p3 : Fup cfW (59/125) (301/500) < 0 := by decide +kernel
theorem cfW_p4 : Fup cfW (301/500) (87/125) < 0 := by decide +kernel
theorem cfW_p5 : Fup cfW (87/125) (763/1000) < 0 := by decide +kernel

end WholeFloorCover
