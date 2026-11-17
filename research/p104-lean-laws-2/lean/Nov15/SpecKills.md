# SpecKills.lean: SPECBREAK R49 paper-only steps formalised, kernel-only (Nov 17)
No sorry, no native_decide; all 9 printed theorems use [propext, Classical.choice, Quot.sound]. 8 s / 2.2 GB. Imports SpecTSUR, SpecINV, SpecCOV (SpecCOV.olean built for this).
Source: (internal notes){RESULT49,AUDIT49}.md, R21/THEORY.md B2, R15/THEORY.md Lemma 3.

## Verdict: NO paper statement is false as written. Differences in form only (below).

## 1. Ureq lower bounds (R21 B2)
Setting: m factors `I - x_i y_iᵀ` in a fixed order, job = `y·x = 2`, unit (transvection) = `y·x = 0`; `J = nJ`, `U = nU`, `r = nflip s`.
- `L3_U` (char != 2): ordered product = `diag s` (s = +-1) => `r + [U >= 1] <= J + U` and `r ≡ J (mod 2)`. Proof: rotate a transvection to the front (`pp_rot`, `pp_add`; conjugation by P, P invertible from g^2 = 1), then INV (`inv_rank0` = SpecINV.inv_rank with the hypothesis weakened to the first factor only, as SpecINV.md already noted); parity by det (`det_pp_pm`, `det_diag_pm`). Different proof from R15 (rotation of -I + fixed-space), same statement. No hypothesis beyond char != 2.
- `SYL_U`: sub-lists `L ν` of the m factors with ordered products `diag(s ν)` (the nested characters), `R` = coordinates flipped by some ν => `2|R| <= m + rank(I - P)` i.e. `2|R(S_μ)| <= J + U + r`. Sylvester step = `SpecCOV.char_syl`; structural step `rangex/rangey` (range and row space of `I - prod L` lie in span x_L, span y_L, for ANY list, tight or not) + `single_mem_x/y` (e_a in both spans, char != 2) + `card_le_finrank_span`. R49's "image(I-D_ν) in span x (resp y)" is exactly this.
- `Ureq_lower`: the two combined = `U >= max(r - J + 1, 2|R| - J - r)`.
Not formalised: the bookkeeping "units are in S_μ iff μ(Q) = 1", and the enumeration of Ureq over the pickle.

## 2. #9 kill (R49 item 1)
- `tight_gram` (Lemma TS on a tight triple of job labels), `clique_gram`: every ordered pair of a 3-clique lies in a tight triple => Gram `2I` on the clique (`hinj`: distinct labels).
- `kill9_char`: Gram-2I clique, D = diag s1 ⊕ diag sd with r1 = 1, d = 0, J = clique ⊕ I, D,J commuting involutions, units transvections => `3 <= U` (UR_inv_combined with d + |k - r1| = 2).
- `clique_neg_one`: a Gram-2I clique of k = dim E jobs has product `-1` (the paper's "J = -I_E"); `kill9_char_literal` (dim E = 3): literal chain `rank(D - J) = rank(diag s1 + 1 ⊕ 0) >= 2` (= 2; only >= is needed) then `inv_DJ` => `U >= 3`.
- `kill9`: four unit characters (1 ADF, 6 BCF, 10 BDE, 13 ACE) each with this data => every replayed word has >= 3 units. With `ucount = U` at each, U <= 2 is impossible; mindef = 2, so #9 has no SC_Z violation at any U (AUDIT49's reading of "dead").
Hypotheses (character data, as in the cards): the tight triples, which pairs lie in them, flip counts (r1 = 1, d = 0), block forms of D and J (jobs vanish on dark: TS (ii)), D^2 = J^2 = 1, [D,J] = 0 (J = clique ⊕ I involution by Gram 2I), units transvections.

## 3. #1 at U <= 3 (R49 item 3, AUDIT49's stronger form)
Blocks `VV nd = Fin 1 ⊕ Fin 2 ⊕ Fin 2 ⊕ nd` (e1, e23, e45, dark), `bd4` (block diagonal, `bd4_mul`, `bd4_sub`, `rank_bd4_ge`), jobs `jm23 J`, `jm45 J`, `R2 = diag(-1,1)`, `R3 = diag(1,-1)`.
Clique data: `JC = refl xC yC`, `JF = refl xF yF` (y·x = 2), `JB JC = -1`, `JE JF = -1` (tight BC, EF). `Nfacts`: `JB = -JC`, `N23 := R2 JC = R3 JB`, `R3 JC = -N23 = R2 JB`, `det N23 = 1` (same for N45). `sl2_dual` (char != 2): `rank(I-N) <= 1 => rank(I+N) = 2` and vice versa.
- Free-job step, unit-free (`unitfree_core`): D = a c d f with a, d reflections => `rank(D - c f) <= 2`; with block forms `rank(Ri - Cc) + rank(Rj - Cf) <= 2`; converted to `a + b <= 2` via `rank_le_of_inv` (1 - R C = R (R - C)). Char 5 in `kill1`; chars 7, 13, 15 in `unitfree_other` (same bound).
- Free-job step, unit (`unit_core` = UR_upper + `J - P Q = P (d-1) Q` of rank <= 1): `1 + rank(Pβ - Mβ) + rank(Pγ - Mγ) <= U + 1`; `unit_gamma` (chars 6 BCDF, 14 BCDE: free D inside) gives `U >= 2 + b'`, `unit_beta` (9 ACEF, 11 ABEF: free A first) gives `U >= 2 + a'`; `a' = rank(I+N23)`, `b' = rank(I+N45)`.
- `kill1`: from the five characters' data: `4 <= U` and (both chars 6, 14 have >= 4 units) or (both chars 9, 11 do). So U <= 3 impossible; U = 4 NOT killed (as AUDIT49).
No inverses used in the free-job steps (they work with `D - P d Q` differences), so no invertibility or commutation of the clique is needed beyond the block forms.
Not formalised: that tight BC/EF/BCEF give the block forms and `JB JC = -1` (Lemma TS, taken as hypotheses), the flip sets of D_μ per character (table data from the pickle: char 5 flips {2,4}, 6 {1,5}, 14 {1,4}, 9 {1,3}, 11 {1,2}), and that the free jobs are conjugate reflections (rank(d-1) <= 1 hypothesis).
