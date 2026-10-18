# B101: full centre delivery (0 packets, S3+S4 268 helpers gone?) VERDICT: KILL, PROVEN at the frame gate [scope: #656/B76 PROTOTYPE.json geometry, frame rules of B11/B82; no build, no price]. ship=false
Tool: gate.py (run in B76/work/in_h, <1 s, single process). Prior kills agree: B1 (centre = clean scratch, rank-8 frame, read only at cut), R40-C (centre descents only at barrier), B10 (centre span weights 56/64), B16 (fan-out).
## Gate (frame numbers)
- Centre i holds c_i = sum_s R[s,i] y_s: 57 sources. Minimal frame = span of their start ports = rank 9 (FULL) by direct count; shipped word keeps it at rank 8 = hyper(P[f_i]) (f_i = the coordinate source of axis i; borrowed-basis trick), i.e. dim 8, a FIXED hyperplane.
- Target t allowed frame (every frame in its monotone chain, end = perp(port)) is hyper(P[t]), dim 8. ADD t += c_i forces the common frame to contain the centre frame.
- Centre frame dim 8 vs target frame dim 8: contained only if hyper(P[f_i]) = hyper(P[t]), i.e. t = f_i. True for 8 targets (the shipped cut = 8 coordinate reads, c82 assert e[1]-120==e[2]<8) and FALSE for the other 112 (each (t,i in supp t) pair: 28/57 source ports have odd parity with P[t]; 448/456 pairs violate, the 8 survivors are t=f_i).
- A target reading its 4 supp(t) centres needs a frame containing 4 distinct hyperplanes: span = 9 (FULL) > 8 for all 112 targets (4 distinct centre frames each). Frame 9 > 8 => KILL PROVEN. Gram-parity legality (p_s.p_t=0) is a VALUE condition; it does not give frame legality.
- Centre descent cannot rescue: a centre's frame is bounded below by its content (>= 8) and chains only climb; serving 56 readers (112*4/8) would need frame <= intersection of 56 target hyperplanes (dim <= 8-ceil(log2 56)=2), far below content rank (B82 same bound).
## Consequence
Packets/block: 12 (shipped); 4 or 0 only at full centre delivery, which is frame-illegal. B96's "unpriced" point is now closed: S3+S4 = 268 stay. No price needed.
## Escapes (>= 3), none promising
1. Targets re-based so P[t] in {P[f_i]} (changes geometry: only 8 hyperplanes available; skeleton redesign).
2. Per-target copies of centres at reduced frame: content rank forces >= 8 (copy of FULL-rank content).
3. Split centre content by block (block totals, rank ~ 4-5 frames): that IS the shipped packet architecture (12/block).
TRANSFER: a register's min frame = span of its source ports (>= 8 for any 57-source centre); legal readers of it need hyper(P[t]) = that frame, so only the 8 coordinate targets.
