# SpecJordan.lean: SPECBREAK R51 JORDAN-U + item 2, R53 order-free kill of #1 (Nov 17)
Kernel-only: no sorry, no native_decide; all 13 printed theorems use [propext, Classical.choice, Quot.sound]. 10 s / 2.2 GB. Imports SpecKills (+SpecTSUR, SpecINV); SpecKills.olean built for this.
Source: (internal notes){RESULT51,AUDIT51}.md, R53/{RESULT53,AUDIT53}.md.

## Verdict: one paper clause FALSE as written (already flagged by AUDIT51); nothing else false.
- **FALSE (odd U):** R51 item 1(b) "m = U-1 => single 2-block at -1 and rank(I-g) = U" fails for odd U. `odd_counterexample` (kernel-checked, U = 3, n = 3, over Q):
  x0=(-1,-1,-1) y0=(-1,1,0); x1=(-1,1,-1) y1=(1,1,0); x2=(0,2,-1) y2=(2,0,0) (all y_i.x_i = 0), g = T0T1T2 = diag(-1,-1,1): m = 2 = U-1, g^2 = I, rank(I-g) = 2 != U. Corrected statement = `jordan_even` (EVEN U only).
- Strengthening, not an error: m <= U-1 ALWAYS (`jordan_le`), so m = U never occurs for U >= 1; "m = U => g^2 = I" (`jordan_a`) is true and its INV consequence is the same contradiction (`jordan_le` is proved that way; `jordan_ne_U` is the direct diagonal proof, `H_ne_two`).

## 1. JORDAN-U (g = pp x y U = I - A B, A = Zm, B = Qm, H = B A)
- `nullity M = dim ker M`; `nullity_add_rank`; `nullity_le_card` (m <= U); `H_eq_two` (m = U => B A = 2 I); `jordan_a` (=> g^2 = I); `nullity_le_rank` (ker(g+I) in im(I-g), so m <= rank(I-g)); `jordan_le` (m <= U-1 via INV).
- `jordan_even` (even U, m = U-1, so rank(H-2) <= 1, H-2 = u v^T, det(I-H) = det g = 1 forces v.u = 0, (H-2)^2 = 0): rank Z = U, rank((g+I)Z) = 1, (g+I)^2 Z = 0 (on the g-invariant U-dim subspace im Z, g+I is nilpotent of type (2,1^(U-2)): ONE block of size 2 at -1), rank(I-g) = U, (g+I)^2 (g-I) = 0. `jordan_even_abs` is the abstract A,B form.
- AUDIT51 fix honoured: the evenness enters exactly at det(-(1+M)) = (-1)^U det(1+M); "P,Q full rank" is derived (H invertible), not assumed.

## 2. R51 item 2, order-free (`unit_core2`, `unit_gamma2`, `unit_beta2`)
Word w with TRANSVECTION units (hform; rank(t-1) <= 1 alone is NOT enough, JORDAN needs q.p = 0), ev w = D_mu, jobsP w = P d Q (d a free reflection, P Q only through P Q = S, the commuting clique product; no letter order), U >= 1: moving units left, D = g J, rank(g+I) = rank(D+J) <= rank(D+S) + 1 and JORDAN gives m <= U-1, so `5 <= U + rank(Pb+Mb) + rank(Pg+Mg)`. Chars 6/14: 5 <= U + b; chars 9/11: 5 <= U + a (`rank_R_add`: rank(R+J) = rank(I-N) when R^2 = I, R J = -N). Equivalent to the paper's m >= 4-b (U = 4: b = 0 or a = 0 dead), and stronger: b = 0 needs U >= 5. (Paper's "MG = -2I vs zero diagonal" is `H_ne_two`.) Needs `rank_fromBlocks_diag_le`, `rank_bd4_le` (new upper bound on block-diagonal rank).

## 3. R53 order-free kill
- `conj_refl`, `orderfree_form`: c0 P c1 Q' c2 = sigma1 sigma2 (c0 c1 c2) with sigma1 = P^{c0}, sigma2 = Q'^{c0c1} reflections (pure group identity `group`, GENERAL reflections, no sampled shapes).
- `kill_word` (one character): J^2 = I (K^-1 = K), Z := D K = sigma1 sigma2 = I + (Db Jb) + (Dg Jg) + I; Z23 = Db Jb, Z45 = Dg Jg for GENERAL reflections (AUDIT53 fix 2: used `refl_sq`/J^2 = I, not the two triangular shapes). `Z_four`: chars 5, 7, 13, 15 all give N23 (R2 JC = R3 JB) and N45 (R2 JF = R3 JE).
- `sub_one_sq_zero`: det N = 1, rank(I-N) <= 1 => (N-I)^2 = 0 (Cayley-Hamilton, tr N = 2). `two_refl_kill`: sigma1 sigma2 - I =: n with n^2 = 0, rank n >= 2 impossible (char != 2): im n in <x1,x2>, so equality and x1,x2 independent, n x1 = 0, i.e. sigma1 sigma2 x1 = x1, which reads (cs-2) x1 - c x2 = 0 (c = y2.x1, s = y1.x2), so c = 0 and 2 = 0. (Slightly shorter than the paper: only x1 is used; "sigma1|V = sigma2|V" is not needed.) `kill_core`: Z = I+N23+N45+I with rank(I-N) = 1 each is impossible.
- **`kill1_all`**: hypotheses = clique blocks (JB JC = -I, JE JF = -I), char 5 in order-free form, unit chars 6 and 9 (transvection units, ucount = 4, ev = D_mu, jobsP = P d Q, P Q = clique product). a + b <= 2 comes from rank(Z-I) <= 2 (order-free, replaces R49's order-specific free-job step), chars 6/9 give b >= 1, a >= 1, so a = b = 1, contradiction. Conclusion: #1 has no realisation at U = 4 for any job order (conditional on char != 2, the TS block forms, D = +1 on ancillas, as in the cards); with SpecKills.kill1 (U <= 3), #1 is dead at every U <= 4.
Not formalised: the TS/R49 derivations of the block forms and the flip tables (taken as hypotheses, as in SpecKills); U >= 5 is handled by R48 (mindef 4), not here.
