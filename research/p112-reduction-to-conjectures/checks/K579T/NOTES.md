# K579T (P112-PUSH theory killer) — row 579 [7^8,4,4,4,3], d=8
STATE: K579T: DONE. Row 579 KILLED CONDITIONAL on 'every h_ab is a root' (then A7 pattern by SEVEN S1/KILL-A8 §3(b)); 2 impls agree, controls pass. Root premise is NOT covered by neighbours: D7R needs small-flat labels spanning <=7 dims (4+4+4+3 can span all 9), KILL-A8 §3(a) had a six-flat exempt. Residual = conjecture R579 below.

## Premise (from caller / SEVEN S1, KILL-A8 §3)
8 sevens, pair roots h_ab with the K8-graphic (A7) pattern; Lemma F: Off(h_ab) ⊆ L_a ∪ L_b ∪ E, E = union of the 4 small flats (F4,F4,F4,F3), |E| <= 8+8+8+4 = 28.
Off(h) = lines t with <r_t,h> != 0 (57 lines, h included; same convention as KILL-A8 gen.py). L_a WLOG maximal 7-flat masks (43180).

## Theorem K5 (A4 pair cover, |E| <= 28): no 5 sevens with an A4 pair pattern have |∪_{a<b<=4} Off(h_ab)∖(L_a∪L_b)| <= 28.
Size alone kills it: the shape of E (3 F4 + F3) is not needed. Since any 5 of the 8 sevens carry an A4 sub-pattern, row 579 dies (both A7 classes: the
argument uses only one A4, and all 16 chain extensions of the fixed A3 are enumerated). Reduction: W(E8) is transitive on ordered A3 chains (one A3 class;
reversal = -w0(A3)·(-1)); L_0 reduced mod W(D5) = pointwise stabiliser of the chain (20 perp roots, 619 orbits; masks closed under the reflections, checked).
 - A3 stage (4 sevens, 6 pairs, |U|<=28): 958 (rep-level) quadruples; 291 of them have U coverable by 3 F4 + 1 F3. Both impls give exactly 958 / 291.
 - A4 stage: 0 (both impls; with and without the cover test).
 impl A: base.py (doubled-coord E8, lattice basis as KILL-A8 gen.py) + genA3.py -> a3.txt; a3e.c (DFS L0 rep -> L1 -> L2 -> L3, |U| cap) -> surv_28_*_2.txt,
         run28_*.out; cover.py (affine-span cover in F2^8); ext.py (append chain root c4, scan all masks): ext28.out (cover) and ext28_sizeonly.out: A4 states 0.
 impl B: b5.c (own E8 from Bourbaki Cartan matrix, simple-root labels, own masks/orbits, explicit F4 (1896435) / F3 (184450) line-set cover, DFS order
         L0 -> L3 -> L1 -> L2 -> L4): b5_28.out "A3 quads 958, coverable 291, A4 solutions 0"; b5_28_nc.out (size only) "958, A4 0".
 Controls: random 28-label sets coverable 0/20, unions of 3 cubes+plane coverable (cover.py); extension relaxed cap 40 -> 7968 A4 states (min |U| 36),
         cap 48 -> 4315200 (ext28_ctl40/48.out); impl B size-only cap 31 -> 102 A4 solutions (b5_31_nc.out, min |U| 30). So the A4 minimum of |U| is 29–30 > 28.
 Runtime: a3e < 1 min (2 procs), ext.py ~3 min, b5 ~3 min.

## Root premise check (typA.py / typB.c, 2 impls agree): min over (L_a,L_b) of |Off(omega_i)∖(L_a∪L_b)| per maximal non-root perp type:
D7 14, A7 25, E6A1 23, A1A6 31, D5A2 31, A4A3 36, A1A2A4 38 (root E7: 1). So with |E|<=28, A1A6/D5A2/A4A3/A1A2A4 (and every type whose Off contains one)
are excluded by size; D7, A7, E6A1 (and E6, D-sub-types with Off containing only these) are NOT excluded by size.
CONJECTURE R579: in row 579 no h_ab has perp type D7, A7 or E6A1(/E6), i.e. for those h no (L_a,L_b, 3 F4 + F3) covers Off(h) — or, if one does, it is
incompatible with the pair pattern. Closing it (e.g. P=2 cover test of the ≤28-leftover pairs for these 3 types, as KILL-A8 types.py) makes 579 unconditional.
Reuse: Theorem K5 (size-only, 5 sevens, |E|<=28) applies to any row with >=5 sevens, |E|<=28 and the root premise (check KILL-SMALL rows 262, 596-601).

## Side results (not needed for the kill)
- A3 with E exempt is NOT enough (291 coverable survivors): the 5th seven is what kills.
- Counting route (level sets in A-coordinates) fails: A8-class A7 has Σ_t (8 - maxlevel_t) = 288 = 8·36 exactly (tight), E7-class 308; canonical sets M_a
  have deficit >= 15 (A8 class) / 6 (E7 class) to every 7-flat, but E (c-weight <= 84, a 4-flat can carry weight 24) absorbs it (phi.py, deficit.py, flatw.c).
Files: base.py stats.py deficit.py phi.py flatw.c dump.py genA3.py a3e.c cover.py ext.py b5.c masks.npy a3.txt surv_* *.out
