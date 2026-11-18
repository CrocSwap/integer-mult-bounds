import Nov15.NumCertK

/-!
CONGESTION-I3 numeric half C1 : own56 ceiling data, part 1.  With the decoder's descent mass >= 56 charged (LIFT1 sec. 3:
cheapest F form 6 * 9^s + 2 * 1 plus 8 rises), the 17-call base is F_base = F(caller 6 7) - 17 (400 * 8^s + 6 * 9^s + 10)  (`cfC`).  `cfC88`
adds R3's 88 forced stops (-17 * 88 * (2 - 2^s): (1, -2992), (2, +1496)); F < 0 on s in [0, .9] (t >= .1) is covered here and in C2.
-/
namespace CongestionI3
open NumCertK

def cfC : CF := [(1, -554), (8, -7456), (9, 282), (16, -416), (17, 416), (24, -416), (25, 416), (32, -416), (33, 416),
  (40, -416), (41, 416), (48, -416), (49, 416), (56, -416), (57, 416), (64, -208), (65, 416), (73, 208), (137, 208)]
def cfC88 : CF := [(1, -3546), (2, 1496), (8, -7456), (9, 282), (16, -416), (17, 416), (24, -416), (25, 416), (32, -416), (33, 416),
  (40, -416), (41, 416), (48, -416), (49, 416), (56, -416), (57, 416), (64, -208), (65, 416), (73, 208), (137, 208)]
theorem cfC_ok : okR cfC := by decide +kernel
theorem cfC88_ok : okR cfC88 := by decide +kernel
theorem cfC88_p1 : Fup cfC88 (0) (22/100) < 0 := by decide +kernel
theorem cfC88_p2 : Fup cfC88 (22/100) (39/100) < 0 := by decide +kernel
theorem cfC88_p3 : Fup cfC88 (39/100) (51/100) < 0 := by decide +kernel
theorem cfC88_p4 : Fup cfC88 (51/100) (6/10) < 0 := by decide +kernel
theorem cfC88_p5 : Fup cfC88 (6/10) (67/100) < 0 := by decide +kernel

end CongestionI3
