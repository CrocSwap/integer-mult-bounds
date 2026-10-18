# B179 borrowed-target plane jump. VERDICT: KILL PROVEN [scope: shipped #656, all 88 plane stoppers (11 S1 blocks), early-A/B jump, 5-op gadget and its point-holder variant]. ship=false, no oracle/kappa.
Tools (single process, seconds): gate.py (exact Fraction replay of A, validated: end rows == rows0, 0 mismatches), gate2.py (jump op of each stopper, holder search).
## Gate (main risk checked first) - risk is real, total
- All 88 stoppers: jump op found (z is target; z frame before = 2 points, partner row = 2 columns). The partner u is the courier (lines 20/37/110.. or scratch).
- Holders of the l2 piece (row proportional to u's row, any register != z,u, any frame, at the jump moment): 0 of 88. Escape 2 (each l2 column held by a pure point register): 0 of 88 (inside plane 0, no-climb 0). (i)&(ii) = 0 in every block.
## Second, independent frame objection (SPEC, audit_local 'scalar': both operands at common frame f)
- Card step (2) t += a*y happens with t already at z's frame P1 (step 1). y holds l2 (support in Pi\P1), so f(y) does not contain P1: y climbs to join = Pi. So "y is only read, frame stays l2" is false; y would need bound >= Pi = be a courier. Reordering (t += a*y first, t at ()) keeps y low but then z += k*t puts pollution a*l2 into t at Pi; removing it needs an l2 holder at frame >= Pi (again a courier). Lemma B167 extends to borrowed partners: every route needs a second Pi-frame l2 holder besides z,t.
## Price / escapes
- Prize 0 (no fusable stoppers); no splice. Remaining escape only: interface change (B175 fewer planes / B180 other hyperplanes).
