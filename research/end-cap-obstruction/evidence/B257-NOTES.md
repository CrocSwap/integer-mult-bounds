# B257 NOTES: SNAPSHOT HOIST on w1018. VERDICT: NO-GO (provisional). 0 of 172 frame-feasible under hoist or slide; ship=false, no splice, no kappa (nothing to price). Bar #1087 untouched.
Tools (this dir, single process, 7-40 s): hoist.py (each x+=a*h becomes x+=a*c*s at each h-write time, window test, B249 lazy-frame sim), slide.py (same but any position tau in [last read of x, first write of s] ), cls.py, det.py. Baseline sim mass 5586 reproduced (B249 sim.py).
## Counts (B249 172 alg-OK, w1018)
- Window ok (no read of x between copy write and x read; x scale rescaled): 64/172. Fails: 108 = x is read in the window (non-commuting).
- Frame ok: 0/64 (E = write frame, reader frame, or empty/lazy: identical). 62 die at a B-section Y op (F dim 9 > end 8, or F not in parity end), 2 at "target level" (y2, y42: a hoisted op into a Y/target register before B).
- Value replay of hoisted programs (h500, h474, h472 sampled): 0 rows differ, so the algebra is exact; only frames kill it.
- Slide generalization (any tau, s unwritten since copy write, x unread after tau): 86 candidates fail position for BOTH reasons (x read AND s written in the window); 0 positions left on 86. So the "sink" half (move s's other writers/readers) is what is missing.
- First violation class (172 -> 0): Y target forced to dim 9 > end 8 in section B, 169/172 placements; 3 at target level. Same class as B249/B254.
## Mechanism (why hoist does not escape)
Joining x (frame dim 3, its own) with s (dim 3, different subspace) at the copy time already puts both at F=join (>3). From then on s carries x's frame: h474, x=456 s=279: baseline s=7 at B1432, after hoist s=8, Y139 += 279 needs F 9. The SPEC rule climbs the READ operand too, so reading s from x at ANY time after s has a lower frame than x's is a drag of s. Hoisting changes when, not whether. Only a time where x's frame is nested in s's (or vice versa) is free; none exists among the 64 (lazy sim with E=[] is the minimal frame).
## Kill protocol (provisional)
Assumptions: single-helper removal, ops order otherwise fixed, sim = B249 lazy-frame model, s unmodified for tau slides; joint set and CP-SAT not run since singles = 0 (<7 GO bar).
Escape routes: (1) hoist+sink joint: reorder s's writers so s is unwritten and x unread (86 'both'); changes op order for ~dozens of ops, fixed-multiset searches B11/B103/B108 do not transfer but frames were not the only wall; (2) slide with compensation (s written in window: x += a(s_tau - corrections), adds ops, loses mass); (3) copy at the Y-partner frame (join-frame relay, B249 route 3).
Rescue check: first violation is s-drag into Y at B1432-1728, identical across 62/64; no instance is within one frame of feasible.
No audit_local, caps.py, price1018 run (no candidate). 
