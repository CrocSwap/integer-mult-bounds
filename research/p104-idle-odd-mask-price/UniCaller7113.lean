/-
UniCaller7113 (lane UNI-L2L3, Nov 19).  L3: exact certificates for the #7113 17-stage caller block at excess levels X = 0 / 28 / 56 / 112.
Generated rungs (UniCaller7113X*.lean, UNIMODEL/gen_cert7113.py): Cert of  cdat Tcal - cdat Pcal - 17 (400 8^s + X (9^s - 8^s) [+ 104 (1 + 7^s - 8^s) if HS]).
X0   : kappa < 227042846/10^10  (= .0227042846;  P0_real root .02270428456994, interval .02270428456894-.02270428457094; SafeRungsPrice.CertP0 .0227043)
X28  : < .0194453119 (flag);  X28HS : < .0187384875;  X56HS : < .0156053191;  X112HS : < .0093453742  (roots .019445312, .018738487, .015605319, .009345374).
Kernel only.
-/
import Nov15.UniCaller7113Facts
import Nov15.UniCaller7113X0
import Nov15.UniCaller7113X28
import Nov15.UniCaller7113X28HS
import Nov15.UniCaller7113X56HS
import Nov15.UniCaller7113X112HS

namespace UniCaller7113
open SafeRungsPrice

theorem cert7113_X0 : Cert (fun s => cdat s Tcal - cdat s Pcal - 17 * (400 * 8 ^ s + 0 * (9 ^ s - 8 ^ s))) (227042846 / 10000000000) := by
  intro t h1 h2
  have := UniCaller7113X0.cert t (by linarith) h2
  unfold UniCaller7113X0.FceilBank at this
  rw [show UniCaller7113X0.TB = Tcal from rfl, show UniCaller7113X0.PB = Pcal from rfl] at this
  exact this

theorem cert7113_X28 : Cert (fun s => cdat s Tcal - cdat s Pcal - 17 * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s))) (194453119 / 10000000000) := by
  intro t h1 h2
  have := UniCaller7113X28.cert t (by linarith) h2
  unfold UniCaller7113X28.FceilBank at this
  rw [show UniCaller7113X28.TB = Tcal from rfl, show UniCaller7113X28.PB = Pcal from rfl] at this
  exact this

theorem cert7113_X56HS : Cert (fun s => cdat s Tcal - cdat s Pcal - 17 * (400 * 8 ^ s + 56 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) (156053191 / 10000000000) := by
  intro t h1 h2
  have := UniCaller7113X56HS.cert t (by linarith) h2
  unfold UniCaller7113X56HS.FceilBank at this
  rw [show UniCaller7113X56HS.TB = Tcal from rfl, show UniCaller7113X56HS.PB = Pcal from rfl] at this
  exact this

theorem cert7113_X28HS : Cert (fun s => cdat s Tcal - cdat s Pcal - 17 * (400 * 8 ^ s + 28 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) (187384875 / 10000000000) := by
  intro t h1 h2
  have := UniCaller7113X28HS.cert t (by linarith) h2
  unfold UniCaller7113X28HS.FceilBank at this
  rw [show UniCaller7113X28HS.TB = Tcal from rfl, show UniCaller7113X28HS.PB = Pcal from rfl] at this
  exact this

theorem cert7113_X112HS : Cert (fun s => cdat s Tcal - cdat s Pcal - 17 * (400 * 8 ^ s + 112 * (9 ^ s - 8 ^ s) + 104 * (1 + 7 ^ s - 8 ^ s))) (93453742 / 10000000000) := by
  intro t h1 h2
  have := UniCaller7113X112HS.cert t (by linarith) h2
  unfold UniCaller7113X112HS.FceilBank at this
  rw [show UniCaller7113X112HS.TB = Tcal from rfl, show UniCaller7113X112HS.PB = Pcal from rfl] at this
  exact this

end UniCaller7113
#print axioms UniCaller7113.cert7113_X0
#print axioms UniCaller7113.cert7113_X28
#print axioms UniCaller7113.cert7113_X28HS
#print axioms UniCaller7113.cert7113_X56HS
#print axioms UniCaller7113.cert7113_X112HS
