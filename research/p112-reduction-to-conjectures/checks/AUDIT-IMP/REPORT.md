# AUDIT-IMP (relayed by main; auditor's write blocked). 0 FALSE.
1. WALL 8.2/8.3 PROVEN (pc2.c: no root / 70-line target covered by two <=7-flats; all 8 frame targets covered, parts exactly 7; 8.3 r<=2 any m).
2. G2-BUDGET P2: GAP. P0 (delete cost-0 terms) leaves exact-N0; restoring re-merges (circular). P2 overcounts by 1 per cost-0 term with deficiencies (8,1)/(1,8) (p=e_t, A ⊆ Off(r_t)\{t}, w=8). Sound: cost >= 7m − Λ_P − Λ_Q − n01 (n01<=2 at s=t=1). BUD-A 65 -> 63 at m=11 (>=70 for m>=12). Open cell: m=11 (1,1), one (8,1)+one (1,8) cost-0 + 9 cost-7 terms. Recheck O4-2 7m−6(s+t), AUDIT-BX "mod P2" items, O4-2 tight-m conclusions.
3. #2832 S0 (§2.2 + Lemma 2.3) PROVEN.
4. WALL catalogue Thm 6.1 + L3.1 PROVEN (ind_e8.py, ind_coloop.py independent).
5. #2816 R4 as K1-T2 L3 PROVEN (caveat: R4's Δ<=1 ⇒ ρ0<=Δ does not transfer to virtual v′; no effect on L5); L4 PROVEN mod #2816's CHECKED DP/LP.
Impact on shipped PRs: none (#2854 is m=10 and does not use P2; #3029 marks P2-dependent C2 CONDITIONAL).
