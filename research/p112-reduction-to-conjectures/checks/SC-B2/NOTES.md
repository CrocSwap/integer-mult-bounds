# SC-B2 -- all 47 class-B rows killed by a RELATIVE root-counting lemma (CARRIER Circuit Lemma applied inside R_K)
python = W/venv/bin/python. Deliverables: killed.csv (47 rows, certificate per row), residue.csv (empty: header only).
Verdict: 47/47 dead (43 rows s=7 under ClassI; 4 rows s=6 under CARRIER s1.3 scenarios). No ClassI replacement was needed: the s=7 rows are ClassI anyway
(43 of the 47 have s=7: 6 with d=7, 37 with d=8); SC-S7B's lemma only used K of size d-1 / the whole R. Using ANY K with |K|=d-j, j>=2 gives a sub-space R_K of dim >= j
in which the same count applies with N_j instead of N_d. For j=2 this is plain arithmetic.

## Lemma RRC (relative root counting) -- PROVEN given CARRIER s1.3 (ClassI), s2 (Circuit Lemma, E8 version), s3 G1
Setting (ClassI, E8 version): pieces y_1..y_a, weights w_i, Lambda_E(F_i) with |Lambda_E(F_i)| <= g(w_i) (g(1..7)=1,2,4,8,12,20,36), R <= K^a dim d,
h: R -> K^8 injective linear, sum c_i y_i^E = p_{h(c)}^E exactly for c in R. K = Q or R (infinite, char 0).
Statement. Let K0 <= [a], |K0| = d-j (j>=2), comp = [a]\K0, cap(S) := sum_{i in S} g(w_i). Suppose a family F of (j-1)-subsets M of comp satisfies
 (i) cap(comp\M) <= 77 for M in F;  (ii) cap(comp\(M u M')) <= 56 for distinct M,M' in F;  (iii) |F| > N_j, N_2=3, N_3=6, N_4=12, N_5=20, N_6=36.
(Also: if some (j-1)-subset M has cap(comp\M) < 57 the configuration is dead at once.) Then no such S with cost_w(S) <= 71 exists.
Proof. R_K0 := {c in R : c|K0 = 0} has dim >= d-|K0| = j; fix R' <= R_K0 with dim R' = j.
1. For M in F: {c in R' : c|M = 0} has dim >= 1; pick c_M != 0. Its support lies in comp\M, so Off_E(h(c_M)) <= U_{i in comp\M} Lambda_E(F_i), |Off_E| <= cap(comp\M) <= 77.
2. G1 (CARRIER s3, classical): |Off_E(h)| = 57 if h is parallel to a root, else >= 78 (largest proper rank<=7 root subsystem after E7 is D7: 42 lines). So h(c_M) is a root direction.
3. Distinct: if h(c_M) || h(c_M') (M != M'), injectivity gives c_M || c_M', so the common vector vanishes on K0 u M u M': Off_E <= cap(comp\(M u M')) <= 56 < 57, impossible.
4. The |F| distinct root lines lie in the j-dim space h(R'). Phi n h(R') is closed under its own reflections, a simply-laced root system of rank <= j, with at most N_j positive roots
   (A2 for j=2: 3; D4 12, D5 20, E6 36 ...). |F| > N_j contradicts. QED
For j=2 it needs only: >= 4 pieces i in comp with cap(comp)-g_i <= 77 and every pair cap(comp)-g_i-g_i' <= 56.
(SC-S7B is the special case K0 = empty, j = d.)

## Application (killed.csv; script final.py, arithmetic only)
Take K0 = the d-2 largest pieces, comp = the e+2 smallest. All 47 rows have cap(comp) in 80..92 and give a family of 4 (or 5) pieces (three or four 6-pieces, sometimes a 5):
cap(comp)<=96 with >=4 sixes in comp suffices (cap-20<=77, cap-40<=56). 4 > N_2 = 3. Example: [7,7,6^6,5,5,1,1,1]: comp (6,6,6,5,5,1,1,1), cap 87, family {6,6,6,5}.
Rows with fewer sixes in comp still produce 4 pieces via 5-pieces.
s = 6 rows (4 rows, d=8; CARRIER s1.3 scenarios (alpha),(beta1..3), PROVEN-pa there): need robustness. Variants tested (rrc6.py, j=2 each, all dead):
 base (beta1, beta3-B: comp unchanged, K0 loses one 7), +1 extra line f (alpha: add 1 to every cap), and for every weight x present in comp the dropping/heavier piece b* (beta2, beta3-i):
 either 'up' (x -> x+1 in comp) or 'swap' (put b* into K0, K0's smallest piece moves to comp) is dead; every x has at least one dead option.
 Details per row in `python rrc6.py`. So these 4 rows are dead modulo the same dependency as CARRIER's s=6 cells.

## Independent second proofs (not needed; CHECKED, single implementation each)
(a) Count lemma ("dim-cap"): U = h(R_K0) has dim >= j, Psi := Phi n U^perp is parabolic of rank <= 8-j, Phi\Psi <= U Lambda(F_i), so cap(comp) >= 120 - N'_{8-j}
    (N' = 63,36,20,12,6,3,1 = max parabolic sizes, computed). Kills 17 rows (all s=7) by cap(comp) < 84 at j=2. (count.py)
(b) Dim-Cover lemma: same but replace the count by an exact covering test: Phi\Phi_I (I = 6-subset of simple roots; W(E8)-conjugates) must be covered by flats of dimensions
    w_i (i in comp) in F_2^9 labels. Tools: sub.c (all w-dim subspaces, masks restricted to target), srch.c (DFS, leaf residuals checked with CARRIER can_cover), cov4.py (orbit reduction of the first flat
    under Stab_W(E6) from GAP, 311040 elements). Validated: reproduces CARRIER G3 (7,7)=no, (7,7)+1=yes, (7,6)+4 lines=no, (7,5,5)=no, (7,6,3)=no, (7,5,4)+1=no, (6,6,6)=no, (6,6,6)+1=yes;
    orbit version agrees with plain version. Result: 27 of 30 remaining rows dead (all 4 s=6 rows under ClassI); 3 rows (d=8, comp (6,6,6,6,4,1,1,1,1),(..2,1,1),(..2,2), cap 92) have the E6-type covering;
    those die by RRC. Covering is NOT needed for the proof; it is the cross-check that the picture (Psi = E6, U = A2 plane, 3 root lines) is consistent.

## Bonus (not claimed beyond ClassI): RRC with K0 = top d-j (j=2..6) on all 603 d>=4 rows (allrows.py, allrows6.py, allrows_rrc.json)
 s=7 rows (ClassI forced): 295 of 404 dead (previous S7a+S7b: 60). s=6 rows with the variants above: 88 of 153 dead. s<=5: not treated (scenario list needed). This should shrink the SPANCOVER residue a lot; needs the audit below.

## What must be audited before use
 * Dependencies are those of SC-S7B: CARRIER s1.3 (ClassI forced for s=7, uses L120 s1 peeling identity), s2 Circuit Lemma E8 version, G1. The only new step is 'relative': R_K0 has dim >= d-|K0| (linear algebra) and a j-subspace of R contains <= N_j root lines.
 * g(w) values (SC-S7B gcheck.py, exhaustive).  * Field K infinite (used for dim counts and N_j; E8 over Q).
 * s=6 reduction: the scenario list of CARRIER s1.3 (alpha, beta1-3) is assumed complete; 'swap' uses that K0 may be any d-j subset.
Files: count.py, cov.py/cov2.py/cov3.py/cov4.py, sub.c, srch.c, run*.py, rrc.py, rrc6.py, final.py, *.jsonl (cover logs), old/ (intermediate count result).
