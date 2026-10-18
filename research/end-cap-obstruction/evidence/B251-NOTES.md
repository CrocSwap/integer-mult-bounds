# B251 NOTES: DECOUPLER bound on k8 word #1018. VERDICT: frame conflicts ALONE force only 111 of 480 helpers (model-UB 113); NO class is shown closed. ship=false, no word built, nothing pushed.
Honest reading: the frame-conflict structure is real but weak. It pins ONE helper per Y target (111 ~ 112 targets), not the 480. The remaining gap (369) is not excluded by frames-of-delivery; B249's per-helper cascade (0/172 remat-removable feasible, 308 algebraically locked) is a 1-removal result, NOT a global bound.
## Statement proved (computed, exact on word1018; tools in this dir, all <3 s, CP-SAT 1 worker 60 s)
Scope: fixed targets/ports/Y end caps (hyperplane parity, dim 8); op frames E of the word taken as intrinsic (SYN-23); Y/src register identity fixed; section-B deliveries (926 Y+=carrier events, ev.py); value content = carrier row projected to non-helper+centre columns (proj.py; dropping helper dirt columns, 280 pure-gauge reads excluded = sound); a carrier keeps its value from first to last read of that incarnation (no rewrite inside); target-history lower frame L = join(E, earlier target frames); only the op's TARGET chain caps (carrier identity is replaceable, caps do not propagate through carriers).
Theorem (inc.py, mis.py): two read-incarnations a<b can share one register only if time-disjoint and post(a)=join(L_e) lies in pre(b)=intersection of the end caps of b's targets. Then helpers >= max set of pairwise-incompatible incarnations among the 350 value-incarnations with no non-helper holder = 111 (CP-SAT OPTIMAL, bound 111). Greedy chain cover of the same set = 113, so the model is tight (111..113). Incl. non-helper holders: 124 registers (OPTIMAL) for all 592 incarnations.
Sub-results: (i) per projected value class the frame-conflict chromatic number is 1 for 548 classes, 2 for 22: frames force at most 22 value duplications (these are the S4-copy pins; B248's 112 S4 copies come from the 22 + singletons per target). (ii) conflict graph over 926 Y events has omega = chi = 112 = #Y targets, because carriers of different targets' dim>=7 reads cannot be shared (L_i not in hyper(P_j)), but same-target events chain.
## Per-class table (B235R classes; 480 helpers incl. 3 centres inside cold0/endFULL=240)
| class | actual | carries a real Y delivery | never read by Y in B | frame-FORCED (single-class-only incarnations) | bound | gap | gap x0.15% (paper) |
| cold0/endFULL | 237 | 164 | 73 | 0 | 111 total shared across classes (clique is hostable by cold0/endFULL, enter1, enter4/5) | 237 | - |
| cold0/endU | 48 | 0 | 48 | 0 | 0 | 48 | 7.2% |
| enter1/endFULL | 106 | 66 | 40 | 0 | 0 forced | 106 | - |
| enter1/endU | 30 | 30 | 0 | 0 | 0 | 30 | - |
| enter4/endFULL | 32 | 32 | 0 | 0 | 0 | 32 | - |
| enter5/endFULL | 24 | 24 | 0 | 0 | 0 | 24 | - |
| TOTAL | 477 (+3 centres) | 316 | 161 | 0 | 111 | 366-369 | 55% paper ceiling (not achievable; B248 bit-cap 3.52% for all 112 S4) |
Class-wise forcing is zero because every clique member is hostable by plain cold0/endFULL helpers (hostability = start in pre, post in end). Only the TOTAL bound (111) is meaningful; the 0.15%/helper value of the gap is a paper figure (B248: freed mass needs a re-planned owner map).
## Where the gap lives
- 161 helpers (73+48+40) are never read by a Y in B: A-phase scaffolding/rotations; delivery frame conflicts say nothing about them (bound 0, gap = all).
- 316 carriers serve 350+ helper-only incarnations; the model would let ~3 incarnations share a register (111-113 registers) but sharing needs a rewrite of the register between reads (ops not priced here, rotations/H+=H in B: 736 ops) and climbs frames monotonically: that is the real cost B249 saw, outside this relaxation.
- Frames-forced part sits in section B, high-frame (dim 7/8) Y reads, one pinned helper per target (111 of 112), plus 22 duplicated values.
## Not proved / caveats
No-rewrite and L=join(E,target history) assumptions (an alternative program could shorten E); 54 colour classes had pairwise-only compat but chain semantic (pre/post) was used in the final bound; section A and cleanup have no caps (all FULL) so they contribute 0; gauge (dirt) reads excluded. The bound is a LB on helpers, not on climb shape/mass: paid-climb LB not computed.
## Consequence
An op-multiset change at fixed targets/ports cannot go below ~111 helpers via frames, so frames do NOT close the remaining ~369; closing them needs the value/algebra side (rotation lock 305, remat cascade B249). Next test (not run): ILP over incarnation merging priced with the real rewrite-op frames (B249 sim) to see if >111 is forced.
Files: ev.py graph.py vals.py proj.py inc.py mis.py cls2.py fin.py (+ copied prog/feas/sim/scan/census).
