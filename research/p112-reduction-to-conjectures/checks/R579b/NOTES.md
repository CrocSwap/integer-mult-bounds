# R579b (P112-PUSH): non-root pair directions in row 579 [7^8,4,4,4,3], d=8
STATE: R579b: DONE (budget). NOT killed. New 2-impl lemmas K5^- and K5^-2 (5 sevens with exactly 1, or exactly 2 vertex-sharing, non-root pairs die) => >= 6 non-root pairs; minimal remaining conjecture DEG2 below.

Notation: sevens 0..7, pair directions h_ab (Lemma F, graphic K8 pattern: h_ab || u_a - u_b), Lo_ab = Off(h_ab)\(L_a u L_b) subset of E, |E| <= 28 (3F4+F3).
G = graph of ROOT pairs, N = complement (non-root pairs). Not used anywhere: coverability of E (all results below are size-only, hence stronger).

## R1. Complete list of non-root types that fit (types.c, impl A; maximal ones agree with K579T typA/typB = 2nd impl)
Every non-root h is W-conjugate to a dominant sum of fundamental weights with support S and Off(h) = U_{i in S} Off(omega_i); min_{La,Lb}|Lo| for all |S|<=2:
  D7 (S={1}) 14, E6A1 ({7}) 23, E6 ({7,8}: generic point of an A2-plane) 24, A7 ({2}) 25, D6 ({1,8}: generic point of an A1A1-plane) 26; every other S >= 31
  (|S|=3 supersets of the only <=28 pairs {1,8},{7,8} contain {1,7}: >= 33). Root ({8}) 1.  => only D7, E6A1, E6, A7, D6 can be pair directions.
  NB K579T listed only maximal types; E6/D6 are Off-supersets (covered for coverability) but are distinct directions (a continuum per plane) in pattern arguments.
## R2. Lemma K5^- (CHECKED, 2 impls): no 5 sevens with 9 root pairs + 1 non-root pair have |U| <= 28.
Rigidity: the A3 on the 4 sevens != new seven k, and root triangles (a,a',k) are A2's => u_a - u_k = s_a + x are ROOTS (chain scaling) for a != m,
h_mk = s_m + x = sum of two roots (non-root). Enumerated x over +-root - s_a0: 40 extensions (all |h_mk|^2 = 4, i.e. D7; norm 6 never occurs).
  impl A km_a.py (K579T base.py E8 + its 958 A3 states surv_28_*_2.txt, numpy over all 43180 masks for L_k): km_a28.out: 0 solutions, min |U| 36.
  impl B b5m.c (= K579T b5.c, own Bourbaki E8/masks/W(D5) orbits, A3 stage recomputed: 958 quads; K5^- extension code new): b5m_28_nc.out: 40 ext, 0, min |U| 36.
  Controls: km_a36_ctl.out 2732 solutions at cap 36, km_a38_ctl.out 8196 (path counts; min 36 matches impl B).
## R3. Consequence (PROVEN mod R2 + K579T K5): G has no K5 and no K5^-, so every 5 sevens contain >= 2 non-root pairs; averaging over the 56 5-sets
  (each pair in 20): 20 e_N >= 112 => e_N >= 6 non-root pairs, each with |Lo| >= 14 inside E (|E| <= 28).
## R4. Step B size-only (stepb.c, impl A only): two distinct non-root directions at one seven (h_ab, h_ac, any L_b, L_c, all 10 L_a orbits) CAN share:
  min |Lo_ab u Lo_ac| = 21 (D7,D7); 252895 (rep-level) pairs <= 28. So 2 non-root pairs at a seven are not excluded by size alone.
## R5. Lemma K5^-2 (CHECKED, 2 impls): no 5 sevens whose non-root pairs are exactly two sharing a vertex k (8 roots) have |U| <= 28.
  Rigid as R2 (4 sevens != k form an A3; one root triangle at k fixes scaling). km_a2.py 28 2 -> km2_n2.out: 0, min |U| 36 (norm 4: 38, norm 6: 36);
  b5m2.c (NNR=2) -> b5m2_n2.out: 108 extensions (102 norm 4, 6 norm 6), 0 solutions, min 36. Regression: km2_n1.out / b5m2_n1.out reproduce R2.
## Logic chain. K5 (K579T) alone gives e_N >= ceil(56/20) = 3 (a perfect matching survives); K5^- lifts it to e_N >= 6, which forces a seven of N-degree >= 2.
## Minimal remaining conjecture DEG2 (closes 579): no seven carries two non-root pair directions (=> N matching => e_N <= 4 < 6).
  Equivalently enough: the triangle check for sevens a,b,c with h_ab, h_ac non-root and h_bc in span(h_ab,h_ac) (any type), extended by the other sevens
  as needed, has no configuration with |U| <= 28. This IS finite: on a plane Off(h) is piecewise constant (root lines cut it into finitely many sectors;
  open sectors carry the plane-generic Off, the largest), so D6/E6 members = one generic Off per plane + special lattice directions. Not yet coded.
  stepb (R4) omits Lo_bc and the 3F4+F3 shape of E (impl A only, size-only, two sides) — the closing check must add both; R4 shows 3 sevens alone
  fit (21), so 4th/5th sevens will likely be needed (non-rigid patterns: no A3 base, which R2/R5 relied on).
Files: e8.h types.c types.out stepb.c stepb28.out km_a.py km_a2.py km_a28.out km2_n1.out km2_n2.out km_a36_ctl.out km_a38_ctl.out b5m.c b5m2.c b5m_28_nc.out b5m2_n1.out b5m2_n2.out
