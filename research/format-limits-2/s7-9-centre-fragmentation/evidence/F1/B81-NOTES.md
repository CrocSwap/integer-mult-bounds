# B81 NOTES: carrier ladder via Etzion coverings. VERDICT: KILL at the gate (PROVEN for covers of fixed reader sets, ck word; LOCAL-PRICE for hub-sum designs). ship=false
Tools: cards/B81/gate.py, hub.py (single process, <2 min, venv python). Inputs: ck CANONICAL-WORD ports (112, cap verified: 0 pairs XOR into the set), R.npy (readers: G=R R^T/2, 52 readers/source).
Assumption: target index t <-> port[t] (B11 convention). B80 NOTES not present, so the join rule is taken in the model's FAVOUR (all target savings granted, 905 psi/call).

## Gate 1: cover numbers (per source, 52 readers)
- Etzion t=1 recipe at n=9: a plane SPREAD exists (3|9; 73 F8-lines partition PG(8,2)), so the lifted-MRD/recursion part is not needed. Intersected with the reader port set (200 random bases): 38.3 planes per source, 1.36 readers/plane (needs <=4; useless: a basis-blind cover ignores the cap).
- Cap-aware greedy cover with actual port quads (4 ports XOR 0 = the only 4-reader planes; ~1061 quads among each source's readers): 14.3 carriers/source (min 14, max 15), 3.64 readers/flat.
- Lower bound 52/4 = 13 per source. So single-source carriers: 112 x 14.3 = 1601 carriers.

## Gate 2: price (psi/call; hosting 12.5 per quad carrier, 13.5 per pair carrier)
- Single-source ladder: 1601 x 12.5 = 20,000 hosting alone vs max target saving 905 (even all fragmentation of targets is 1342). Net ~ -19,000. Far below 65 psi GO. KILL.
- Generous hub-sum variant (one carrier = SUM of sources whose coefficient rows agree up to sign on the carrier's readers, the J37-H hub idea): pair (t,u) carriers share ~17.6 sources each, quads only 3.4 (24,276 quads). Greedy incidence cover (5824 (source,target) incidences): 139 pair hubs + 1 quad cover 5427 (397 left), hosting 1889 psi > 905 saving. Net < -980 before the hubs' own climbs, before the left-overs, and with saving over-counted.
- Over-count reasons for the saving: a target sits in ~2.5 pair hubs with DIFFERENT partners, i.e. different dim-7 frames, so its climb cannot be (7,1) (monotone, one frame at a time). (7,1) needs a global pairing of targets where every source's reader set is a union of pairs (twin vertices); none exists (reader sets differ).

## How a carrier ladder escapes J38-U? It does NOT.
- A source s feeding a carrier at dim 7 (pair {t,u}) must itself be at frame perp(p_t,p_u), i.e. all its other readers already served, so a source can feed ONE dim-7 carrier (the last) and ONE dim-6 carrier before it. Feeding order is forced to be a nested chain V1>V2>... of reader spans. A flat ladder where a source feeds many pair carriers is illegal (same reader-cap that killed the dim-3 hubs, J38-U, from the other end). Only chain-nested levels are legal: ~log levels, each carrier serving the readers in V_i \ V_{i+1}, not a flat cover.

## Escapes / rescue (kill protocol)
1. Chain-nested carriers (legal) serve readers in V_i\V_{i+1}: sizes are set by the cap geometry, not by flats; B80's slack measure prices that (not done here).
2. Carriers shared across calls/blocks (amortised): changes hosting to per word; no mechanism known (J30-F fusion neutral).
3. Descents (frame-lowering) for hubs: R39-H LOCAL-PRICE -2.9% b.
Rescue check: replace 12.5 hosting by 0 (free carriers): hub-sum net = 905 - own climbs(139 x >=7 psi ~ 1000) ~ 0; still < 65. Free single carriers: 1601 climbs. Still KILL.

## TRANSFER (one line)
Survives: the spread idea (PG(8,2) = 73 disjoint planes = F8-lines) as a tiling of ports into reader-blind blocks; the cap-aware quad count (24,276 rank-3 flats, 3.4 sources shared) as a bound for any rank-3 hub design. MRD lifting / recursion not needed and do not help (cover must be cap-aware, not point-covering).
