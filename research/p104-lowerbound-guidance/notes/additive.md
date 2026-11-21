# ADDITIVE (Nov 20, Opus, theory). Own code ad1.py (DP with the hosted free edge, t-scan, exact Fraction), ad2.py (rung ceilings), ad3.py (shape of the DP optimum). ls5/rg1 imported read-only. 1 process, < 15 min CPU. No Lean build (reasons in sec. 5).
How this differs: LC1/INT/LS priced S_spec; nobody checked S_spec's premises against the verifier source or against the Lean Word, and nobody built the stay molecule that puts S into the rung.

## VERDICT
No ceiling below .008 is proved, even modulo D+R. The quoted .0078006 / .0075768 are **unsound as stated**. There are two premise failures, and one of them is violated by t7669 itself.
1. **Hosted free edge (soundness bug, fixed) [C].** Word.y2_final (WordModelDefs l.248): for the 96 D ports, Y2_p ends at Hq(lab p) = P_t, the same chart as Y_t. t7669 [C]: 96/96 Y2 share their final chart with a Y. ls5 frees only ONE top edge (Y_t), but Y2_t's arrival is also final, so it is not a stop. With 2 free edges at the 96 D ports: **S_fix = 799.0102 (t=.0075) / 799.4421 (t=.01)**, down from 865.58 [C exact Fraction: weights floor, p8 ceil; ls5 control 865.5795 reproduced]. Whether Y2 can actually carry content is undecided. 799.01 is the valid value without deciding it.
2. **"Deaths at V" is NOT a verifier clause [READ + C].** independent.py (imb-c56 shared-wire-split-composition) l.90-93 requires only frames[initial] < frames[final] for helpers. The Lean Word has no helper-final clause either. **t7669 has 249 helpers ending below V** (final dims 1:8, 2:9, 3:33, 4:105, 5:47, 6:15, 7:7, 8:25; 852 at V). ls5 uses the premise twice: every hub arrival is a stop, and the origin price climb ≥ 9 − dim C. LS/CS labelled it [V]. It is actually the inherited compiler convention (BANK-PROOF.md l.7). DL sec.4 already noted that the CLA count collapses without it.
3. Rank-8 decoder sector (LS premise): the frontier natives are rank 11 (CS). So t7669 lies outside S_spec's scope on two counts. LC1's check "4089.6 ≥ 865.58" is a numeric comparison, not a soundness test of the floor.

## (1) Max form: what puts S into the rung
- **Unit [P, from definitions].** The rung is per call. word_rung takes tr : Fin 17 → Trace, and hV sums wordPaid per trace. rung_port has PortInvX ≤ spec_i − cred_i for each call i. ls5's S = NT·vin is one native trace, i.e. 104 port trees. t7669 is one trace, and word_rung_inhabited uses 17 copies of it. LC1's "S per whole word" means per trace, which is per call. Consistent.
- **Stay molecule [P, paper proof].** Per call: wordPaid − Σ_helpers gc(climb) ≥ 400·8^s + ψ·X_owned + Σ_public Σ_stops p(e_r).
  - Public paths ascend (l.51), so latD = Δdim, and a path with k stops and climb e costs ≥ min over compositions of e into k+1 parts of Σx^s = k + (e−k)^s.
  - g_e(k) = k + (e−k)^s − e^s is concave with g_e(0) = 0 and g_e(e−1) = (e−1)p_e, so g_e(k) ≥ k·p_e.
  - Mains: e = 8, so a main pays 8^s plus its surplus. Helpers: credit e^s, then the surplus.
  - Owned moves: d^s = ψd + mix(d) with mix ≥ 0 on 1..9, and Σ_owned |Δ| = excess = D + R (fold: Fld = public, banks = all moves).
  - Mass sits on owned registers and stops on public ones, so they are additive across registers. The 104h term is simply DROPPED. S·p8 ≥ 104h pointwise, so the max form = the S form.
  - Each DP stop price p(min(8, 9 − dim origin)) ≤ p(e_r) because p_R increases in R. This needs DEATHS AT V for helpers (see above).
- **t-uniformity [P].** p_R/p_8 = (R/(R−1))·(7/8)·(1−e^{−t ln R})/(1−e^{−t ln 8}). Its log-derivative is a/(e^{at}−1) − b/(e^{bt}−1) > 0 for a < b, since u/(e^u−1) is decreasing. So S(t) = min over structures of Σ c_R p_R/p_8 is nondecreasing in t. S at t_lo = .0075 is therefore valid on all of [t_lo, 1). [C] S(t): 865.06 (.0075), 865.58 (.01), 873.88 (.05).
- **Missing for a proof:** S ≥ S_fix as a theorem of the word model. It needs deaths at V (false as SPEC), the rank-8 sector, CLA shared-tree, J0 for descended content, and the U104/#7113 geometry.
- **Corrected class-restricted ceilings [C, rg1 covers OK; rung #7113, X=112]:**

| S | max form | + HS additive [CONJ] |
|---|---|---|
| 865.58 (ls5 as quoted) | .0078006 | .0075768 (both UNSOUND: hosted edge) |
| 865.058 (ls5 at t_lo) | .0078015 | .0075776 |
| **799.010 (S_fix at t_lo .0075)** | **.0079190** | **.0076884** |

  Class: #7113 legal words in the rank-8 sector whose helpers all end at V, plus D,R ≥ 56. t7669 is NOT in this class.

## (2) Additivity S vs HS: the two floors charge OVERLAPPING stops [P]; additive form stays [CONJ]
- HS (BankFitHS1 cut_hs) counts bank crossings of separating height cuts: {1,9} | {0,8}, other heights free.
- An x-type main (1→9) with a stop at height 8 crosses EVERY separating cut twice, whatever its other stops. So 104 such stops supply all 208 extras. The HS molecule is tight there: surplus 104·g_8(1) = 104h.
- ad3 [C]: the ls5 optimum has exactly ONE paid top edge per tree, an arrival from a dim-7 hub into P_t (then →V). Let those 104 arrivals be x/x2 mains (200 available; u_s ∈ hub). Then the HS extras come from S-charged stops. So no disjoint-stop-set proof exists.
- t7669 [C]: 57 X/X2 mains stop at height 8; 28 of them stop at some Y final chart P_t.
- Any additive gain has to come from register-level concavity slack: g_e(k) > k·p_e. An example: x main 1→7→8→9 has surplus g_8(2) = .058 at s = .99, while the DP charges ~p2 = .014 at the top. That needs a joint register-identity LP (DP + cut rows). Not done. The gap between max and additive is .0079190 vs .0076884.

## (3) Cleanest provable ceiling
- Lean word_rung: **κ < .0093454** for every legal #7113 word given D ≥ 56 and R ≥ 56 per call. Nothing lower is proved modulo D+R.
- "Wall56 only" does not yet give even this: D ≥ 56 for networks and R ≥ 56 for all runs are both open beyond Wall56.
- S-based ceilings additionally need deaths at V plus the rank-8 sector. Both are NOT SPEC, and t7669 violates both.

## 4. Next
A helper floor WITHOUT deaths at V. INT's C1 gives ≥ 1 stop per content-receiving chart under (O),(B),(I), with no deaths premise. Rerun the shared-tree DP with "≥ 1 stop per receiving hub, price ≥ p2 (any stopping register climbs ≥ 2)" in place of per-edge stops and origin pricing. That is the honest SPEC-side S. Expect it to be small; size it before building on it.

## 5. Why no Lean
The stay molecule is elementary and would compile. But the DP premise it feeds (deaths at V) is false on SPEC, so a Lean max-form rung would be a class theorem that excludes the frontier. It is not shippable as a ceiling.
