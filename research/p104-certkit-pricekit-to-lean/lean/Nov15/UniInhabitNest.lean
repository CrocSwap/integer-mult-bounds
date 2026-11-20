/- UniInhabitNest (lane UNI-INHABIT, Nov 19): every MOVE chart pair of t7669 is nested (frame-mask ⊊ either way),
and every helper's json index is public.  decide +kernel, core Lean only. -/
import Nov15.UniInhabitHist

namespace UniInhabit

theorem mv_nest : mvAll.all (fun p => Tabs.P.ssub p.1 p.2 || Tabs.P.ssub p.2 p.1) = true := by decide +kernel
theorem hI_lt : (List.range 1101).all (fun i => Nat.blt (lk Tabs.hI i) 1501) = true := by decide +kernel

end UniInhabit
