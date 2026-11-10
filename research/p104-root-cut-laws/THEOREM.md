# Proof note: root cut laws for two-chain words (no kappa)

Tags: **[P]** hand proof written below; **[C]** exact computation reproduced by `check.py` (one PASS line per claim); **[P+C]** both; **[Q]** quoted, not re-proved here. No kappa claim and no word are made. Status of the whole note is in section 7.

## 0. Setting

Fields are Q or F_p with char not 2 unless stated. A **root** has n coordinates and N units u = 0..N-1 in word order, with vectors x_u, y_u (y_u x_u = 0) and labels k = 0..L-1. Label k has LOCAL units (consecutive apart from thin units, no scalar between them) and a mask M_k, a set of coordinates; a scalar D_k multiplies the coordinates of M_k after the LOCAL units of k. Units outside every label are thin. M(D) is the product, in word order, of the maps v -> v - 2 x_u (y_u . v) and the scalings. The **contract** is M(D) = -diag(prod_k D_k^[c in M_k]) for all D. **H-R**: x_u, y_u of every LOCAL unit are supported in the mask of its label. rho = N - n. Put E_k = 1/D_k, Lam_u[c] = product of D_k over labels k with c in M_k whose scalar precedes unit u, and

 Z_uu = 2, Z_uv = 2 sgn(u - v) sum_c y_u[c] x_v[c] Lam_u[c] / Lam_v[c] (u != v).

**(R) hub rank law.** rank Z(D) <= rho for every D with all D_k nonzero. This is the rank statement of PR #6881 (conditional there on its grammar); here it is a hypothesis, and `check.py` verifies it exactly on every instance used (rank Z = 2 at D = 1, -1, alternating, 2 and 1/2, and random D).

**Data.** `data/root_h.json` (n = 38, N = 40, 18 labels of two LOCAL units, 4 thin units, hosted, t = -1/2; the root of PR #6889, inherited from #6883) and `data/root_t0_dsum.json` (n = 40, N = 42, the t = 0 direct sum of two chain roots; the root of PR #6902, whose chains come from PR #6833). Both satisfy the contract, H-R and (R) [C]. Mask incidence is 216 on both.

## 1. Rectangle law and packing [P+C]

**Lemma 1 (rectangle law).** Let K be a field of char not 2, A_d, A_e, B_c, B_f rho x rho matrices over K, and signs s_dc, s_ec, s_ef, s_df in {+1, -1} with product -1. Put R_xy = rank(s_xy I - A_x B_y). Then R_dc + R_ec + R_ef + R_df >= min(rho, 2); for rho = 2 it is >= 2.

*Proof.* If two of the four cells have positive rank the sum is at least 2. Otherwise at least three cells are exact, A_x B_y = s_xy I, and any three cells of the 4-cycle (A_d B_c, A_e B_c, A_e B_f, A_d B_f) involve all four matrices, so all four are invertible. Say the exact cells are the first three; then A_d B_f = (A_d B_c)(A_e B_c)^-1 (A_e B_f) = s_dc s_ec s_ef I = -s_df I, so the fourth cell is s_df I - A_d B_f = 2 s_df I, of rank rho since 2 is a unit. The other triples are the same with the roles rotated. For rho = 2 the sum is then 2. QED

**Lemma 2 (packing, L = 18).** With s_dc = sgn(d - c) on indices 1..18, the 72 quadruples {(i,j), (i+9,j), (i+9,j+9), (i,j+9)} and {(j,i), (j+9,i), (j+9,i+9), (j,i+9)}, 1 <= i < j <= 9, are rectangles of odd sign product; no cell lies in two of them; they use 288 of the 306 off-diagonal cells, and the 18 unused cells are (i+9, i) and (i, i+9). *Proof.* Direct: the sign product is (-)(+)(-)(-) = -1 for the first form and (+)(+)(+)(-) = -1 for the second; the cells are distinct by inspection of the index pairs. [P+C: `check.py` enumerates all of it.]

Controls [C]: the lemma holds on 39,961 random and structured draws over F_1000003 (3,920 tight) and exhaustively for rho = 1 over F_3, F_5, F_7, F_11 (minimum 1); an even sign quadruple and the odd quadruple in characteristic 2 both reach sum 0.

## 2. Theorem S [P+C]

**Hypothesis (S).** L stages d = 1..L of rho = 2 LOCAL units each, the units of stage d preceding those of stage c when d < c; Gamma_dc = (y_u . x_v) over all coordinates, u in d, v in c; and for d != c, sgn(d - c) Gamma_dc = Xi_d H_c with Xi_d, H_c invertible 2 x 2.

**Theorem S.** Under (S) with L = 18 and char not 2, for any two coordinates a, b taken as hubs, let R_dc be the rank of Gamma_dc with the contribution of coordinates a, b removed. Then sum over d != c of R_dc >= 144.

*Proof.* Let Xi'_d (2 x 2) be the entries of the y_u, u in d, at coordinates a, b, and H'_c the entries of the x_v, v in c. The removed contribution is Xi'_d H'_c, so the residual cell is s Xi_d H_c - Xi'_d H'_c = Xi_d (s I - A_d B_c) H_c with A_d = Xi_d^-1 Xi'_d, B_c = H'_c H_c^-1, s = sgn(d - c), and R_dc = rank(s I - A_d B_c). Each of the 72 rectangles of Lemma 2 contributes at least 2 by Lemma 1, and they share no cell. QED

[C] Both data roots satisfy (S) (the factorisation is constructed and verified on all 306 cells, and fails if every sign is +1). Over **all** hub pairs (703 on root_h, 780 on root_t0) the sum is at least 144; it equals 144 at the hub pair (0, 1) only on root_h (histogram: rank 2 on 72 cells, 0 on 234) and at (0, 20) only on root_t0; the next smallest sum on root_h is 370, the largest 612. A family with Gamma = +Xi H and no sign pattern has residual 0, so the sign pattern is what the bound uses.

Not claimed: any statement for stages of more than two units, or for rho > 2 beyond Lemma 1.

## 3. Theorem H and H' [P+C]

Hypotheses: contract, H-R, (R), char not 2, infinite field, D formal (all D_k nonzero). A label with exactly rho LOCAL units and invertible Z restricted to them is a **pivot**; Z restricted to the LOCAL units U_j of label j is D-free, with rank r_j = rank Z_UU(j).

**Facts.** (i) A rank-rho matrix Z with an invertible rho x rho block m satisfies Z_ab = Z_am Z_mm^-1 Z_mb for all rows a and columns b. (ii) For labels a < b, Z_{ab}(E) is a multilinear polynomial in E whose terms are sum_c (+-2) y_u[c] x_v[c] prod_{k in [a,b), c in M_k} E_k, and by H-R every term contains E_a. (iii) For a pivot l, Z_ff = Z_fl Z_ll^-1 Z_lf, so Z_fl is invertible at every D.

**Theorem H.** For pivots f < l, at least rho coordinates lie in every pivot mask in [f, l].

*Proof.* Chain the pivots f = p_0 < ... < p_r = l with (i): Z_fl = Z_{p0 p1} Z_{p1 p1}^-1 ... Z_{p_{r-1} p_r}, a polynomial identity in E. By (ii) every entry is divisible by E_{p_0} ... E_{p_{r-1}}. Write Z_fl(E) = sum_c A_c E^{S_c}, A_c = +-2 y_f[c] x_l[c] (rank at most 1), S_c = {k in [f,l) : c in M_k}. Divisibility says the coefficients of monomials E^S with S not containing P = {p_0..p_{r-1}} vanish, so Z_fl(1) = sum over c with S_c containing P of A_c, which is invertible by (iii) and has rank rho; hence at least rho such c with A_c != 0. Each lies in the masks of all pivots p_i and, as x_l[c] != 0, in M_l. QED

**Theorem H' (exact form; one author).** Under the same hypotheses let f < j < l with f, l pivots and j any label. Then at least r_j coordinates lie in M_j and in every pivot mask of [f, l]. In particular, when exactly rho coordinates lie in every pivot mask (as on both data roots), a label with rank 1 and rho = 2 cannot omit both of them, and a pivot (r_j = rho) cannot omit any.

*Proof.* Let N(E) be the submatrix of Z with rows U_j and U_f, columns U_j and U_l. Its rank is at most rho for all E in (F*)^L, hence for all E in F^L (minors are polynomials, F infinite). Its blocks: Z_{U_j U_j} constant of rank r_j; Z_{U_j U_l} divisible by E_j by (ii); Z_{U_f U_j} contains no E_j (it involves labels in [f, j)). At E_j = 0 (others 1) N is block lower triangular [[Z_UU, 0],[Z_fU, Z_fl^0]], and a block lower triangular matrix has rank at least the sum of the ranks of its diagonal blocks, so rank Z_fl^0 <= rho - r_j. Now Z_fl(1) - Z_fl^0 equals the sum of A_c over c with S_c containing P and containing j, has rank at least rho - (rho - r_j) = r_j, and each A_c has rank at most 1. QED

**Withdrawn form.** The statement with "every pivot mask" replaced by "every mask in [f, l]" (equivalently, that an interior stage never lets a hub skip) is false, by the exact instance below.

**Counterexample [C], scope stated plainly.** Take root_t0_dsum. On chain A put the LOCAL units of stages J and J+1 at one label (D_J specialised to 1), and on chain B put the last two stages at one label and let chain B skip label J; thin units stay outside every label. For J = 4 and J = 7 the word satisfies the contract exactly at D = 1, -1 and random D, H-R holds, and rank Z = 2 at every tested D. Labels J and 17 have rank r = 1 (t = -1); 16 labels are pivots. The coordinates in every pivot mask are {0, 20} (both hubs); the coordinates in every mask of the hull are {0}: hub 20 is absent from the interior mask M_J. H' holds with equality there (r_J = 1, one hub). Total mask incidence is 208 (J = 4) and 205 (J = 7), below 216. **Scope:** the base root is a direct sum of two chains, which is reducible; the counterexample lives on that family. In the connected hosted family (t = -1/2) no such interior skip is known, and nothing here says that an interior stage saves incidence or cost in any connected root. No consequence for kappa is claimed.

Controls [C]: deleting hub 0 from M_J as well, or hub 20 from a pivot mask, breaks the contract; a LOCAL unit outside its mask is flagged by the H-R check; a Z with one entry sign-flipped has rank above rho. The proof ingredients are checked on all four words: Z_fl(1) invertible, Z_fl = 0 at E_k = 0 for each pivot k in [f, l), the Schur identity at a pivot on all N x N entries, and rank Z_fl(E_j = 0) <= rho - r_j at every interior label.

## 4. Root cut closed form [P arithmetic, C; law conditional]

Let f(x) = x ln x. Take the following cost expression, a convention fixed here as an input (built from the field rank 8m+1, the idle part 8(m-1) and the body 8; its hub form is not verbatim in any cited PR and is not derived here), that a hub field of incidence L and an own field of incidence m cost, with body 8,

 hub(L) = f(8L + 1) - L f(8), own(m) = f(8m + 1) - f(8(m - 1)) - f(8),

and a chain has one hub with L = 18 and two arms of own fields m = 1..9.

**Proposition.** The cut per chain is 8[f(18) + 2 f(9)] + 87.353 = 819.967 (hub part 422.187, arm part 397.780; entropy part 732.614). *Proof.* f(8a) = a f(8) + 8 f(a) gives sum_{m<=g}[f(8m) - f(8(m-1)) - f(8)] = 8 f(g) and hub(L) = 8 f(L) + [f(8L+1) - f(8L)]; adding the remainders gives 87.353 = [f(145) - f(144)] + 2 sum_{m=1}^{9}[f(8m+1) - f(8m)]. QED

[C] The incidences of both data roots are two hubs of 18 and four fields of each of 1..9; the sum over fields is 1639.93 = 2 x 819.967 (50-digit arithmetic). **Scope: all-pivot words.** Roots at t = -1/2 and t = 0 have the same incidence multiset, hence the same cut, so t is not an input among them. The words of section 3 have a different multiset (total below 216), so the formula does not apply to them. The body 8, the stage count and the cost expression are inputs: body 7 or 9 and L = 17 change the value (controls).

## 5. Theorem C (crossings) [P+C]

Registers 0..n-1 are public, further registers owned and zero at the start. Each register has a frame label; events are hops (a register changes label) and ADDs (d += c s). A word is **flat** if every ADD joins registers with equal labels. For a set U of labels split the public registers by (start in U, end in U) into A (in, in), D (in, out), C (out, in), E (out, out); n_down and n_up count all hops (public and owned) leaving and entering U; T is the n x n map of public outputs on public inputs.

**Theorem C.** For a flat word and any U: (a) rank T[D+E, A+D] <= n_down; (b) if T is invertible, rank T^-1[A+D, D+E] <= n_up - |C| + |D|.

*Proof.* (a) Restrict to inputs in A+D (the others set to 0). Let W be the span of the current rows (as functions of those inputs) of the registers whose label is outside U. At the start W = 0, since registers starting outside U are C+E public registers (zero on A+D) or owned. A hop from inside to outside U adds one row, so dim W grows by at most 1; other hops do not add rows. A flat ADD joins registers on the same side of U: inside, the set is unchanged; outside, d += c s with both rows in the set leaves the span unchanged. At the end the rows of D+E lie in W, so the rank is at most n_down. (b) Apply (a) to the complement of U: hops leaving it are n_up, its classes are (E, C, D, A) for (A, D, C, E), so rank T[A+C, C+E] <= n_up. The nullity theorem for invertible T, nullity T[I, J] = nullity T^-1[J^c, I^c] (nullity = number of columns minus rank), gives rank T^-1[A+D, D+E] = rank T[A+C, C+E] + |D| - |C|. *Proof of the nullity theorem:* x in ker T[I,J] extended by zero has T x = (0, w) with w supported on I^c, and x = T^-1 (0, w) vanishes on J^c, so S[J^c, I^c] w = 0 with S = T^-1; x -> w is injective, and the converse map w -> T^-1 (0, w) is its inverse. QED

**Corollary ((f, r) cut law).** Suppose T is invertible and T = I_D + T'' (identity on D, no other entries in the rows and columns of D), f = rank T[E, A], r = rank T^-1[A, E]. Then (a) gives |D| + f <= n_down and (b) gives r <= n_up - |C|. Put e = pub_down - |D| = pub_up - |C| (equal because a flat public register leaves U exactly [start in U] - [end in U] more times than it enters), o_down, o_up the owned crossings. Then f <= e + o_down, r <= e + o_up, and the crossings beyond the |C| + |D| required are 2e + o_down + o_up >= f + r; with owned crossings allowed the bound is **at least f + r** (the value of the inequality system at e <= min(f, r); achievability is not shown), without owned **at least 2 max(f, r)**, so the owned discount in the bound is |f - r|. If every hop has mass at least 1 these are mass bounds. [P; the minimisation and the inequalities are checked on 1,076 random cuts and a small grid, with planted bounds that fail.]

**Non-flat words.** With a_down the number of ADDs whose destination is outside U and source inside, rank T[D+E, A+D] <= n_down + a_down. *Proof.* As (a): such an ADD adds one row to the outside span, others none. [P+C on 4,000 random cuts.]

**Scope limit: the non-flat toy [C].** Frames are elements of F_2^4, Delta = 1, m = 2, a = 4, b = 8; public x1, x2, y1, y2 start at 0, Delta, m, m+Delta, owned w, z1, z2 at 0, Delta, 0; the word is `w+=x1; w+=x2; z1+=x2; z2+=x1; hop w by m; hop z1 by m+a, z2 by m+b; y1+=w; y2+=w; hop y1 by a, y2 by b; y1-=z1; y2-=z2`. It computes y1 += x1, y2 += x2 exactly. With U = {0, Delta, m+Delta+a, m+b}, A = {x1, x2}, E = {y1, y2}, rank T[E, A] = 2 but only one hop (w) leaves U, so (a) fails without flatness; 4 of the 8 ADDs join different labels, a_down = 2 and n_down + a_down = 3 >= 2. Controls: the bound n_down alone fails on 954 of 4,000 random non-flat cuts, and planted bounds one lower fail on flat cuts (6,389 and 6,382 times of 9,000).

## 6. Hypothesis ledger

| item | needs | status |
|---|---|---|
| Lemma 1, Lemma 2 | char not 2 | [P+C] |
| Theorem S | (S): Xi, H invertible, two-unit stages, L = 18 | [P+C] |
| Theorem H | contract, H-R, (R), pivots | [P+C], (R) quoted from #6881 |
| Theorem H' | same, any label j | [P], new, one author; [C] on four words |
| counterexample | direct sum root | [C], reducible base, scope above |
| root cut formula | cost expression, all-pivot incidences | arithmetic [P+C]; as a law conditional |
| Theorem C (a), (b), corollary | flat words | [P+C] |
| non-flat form | any word | [P+C] |

## 7. Status and review

Written by one model session; a second model session read the statements and proofs once. No human has reviewed them. Proved by hand (and also checked numerically): Lemmas 1 and 2, Theorem S, Theorems H and H', the closed-form identity, Theorem C and its corollary and non-flat form, the nullity step. Computed only: the data facts (contract, H-R, rank Z, the factorisation, all hub-pair sums, incidences), the counterexample, the toy, and the random-word and exhaustive small-field tests. Hypothesis (R) and the cost expression of section 4 (a fixed convention) are inputs, not re-derived. Nothing here prices a supplier or bounds kappa.
