# Root-unit decoders (partial, no κ claim): two lemmas, an erratum to #595, and open cases

> **What is claimed, and what is not.** This package is deliberately partial.
> **Claimed.** (A, PROVEN) Under the cost formula of #446 Theorem C, every exact decoder with at most two totals on a unit of v root lines costs at least v, for **every** admissible pairing B (not only B0), for decoders over the rationals. (B, PROVEN) A lift identity: for every rational B′ on the support of B, v ≤ Σ_j rank_Q B′[R_j, A_j]; so a decoder cheaper than v needs blocks that no common rational re-weighting brings down to their F2 ranks. (ERR1, CHECKED) An erratum to #595: dyadic exact decoders use rank_Q G totals, E8 8 < 9 and E6 6 < 7 = rank_F2 B0, so the count of totals through the F2 minimum rank (#595 row quoted in §4) does not hold for decoders over Q. (D5, RECORDED) A kissat UNSAT result with a drat-trim VERIFIED proof says that no exact three-total decoder on D5 has all three block ranks ≤ 4, which closes the D5 T = 3 windows h7-8. Only the regeneration of the CNF and its sha256 are CHECKED here; the solver runs are not repeated by `verify.sh`.
> **Not claimed.** No κ gain, no word, no claim that any other unit or window is closed. For three or more totals on D6-D8, E6 and E7 the question is **open**; the table in §6 states exactly what would close each window. Nothing here says the E8 frontier cannot be improved.

## Reading this package

Every result has a status:

- **PROVEN**: a proof in this README (the proof is the claim; the scripts only sanity-check it on instances);
- **CHECKED**: `verify.sh` recomputes it (exact arithmetic, or a SAT regeneration pinned by sha256); a solver result is the status of the recorded run, and the 1.7 GB DRAT proof is not shipped;
- **ARGUED / OPEN**: an argument that is not a full proof here, or a stated problem.

```sh
python3 -m pip install -r research/root-unit-decoder-lemmas/requirements.txt
bash research/root-unit-decoder-lemmas/verify.sh /fresh/output/dir     # from a checkout or `git archive` of the whole repository
```

Python ≥ 3.11 (numpy, python-sat; `PYTHON` chooses the interpreter). `pip` resolves `python-sat==1.9.dev15`; the CNF digest depends on that version's sequential-counter encoding, and a different version can change the CNF and fail the hash check of group G5. Step 0 checks every file against `MANIFEST.sha256` and every pin of `SOURCES.json` (including the D5 CNF digest that this README states) and stops with exit 1 on any mismatch. No solver is needed. Single process, about one to two minutes.

## Setting (as in #446 Theorem C and #595 C.6)

A unit is a set of v root lines with Gram matrix G. A *pairing* B is a 0/1 matrix over F2 with unit diagonal, zero on non-orthogonal pairs and free on orthogonal pairs (*admissible*). An *exact decoder* with T totals is M = Σ_{j≤T} p_j q_jᵀ over Q with M_tt ≠ 0 and M_ts = 0 wherever B_ts = 1 (s ≠ t). Write R_j = supp p_j, A_j = supp q_j, D_j = R_j ∩ A_j, r_j = rank_F2 B[R_j, A_j]. Theorem C prices the decoder at **cost = Σ_j max(w, r_j)**, with w the unit's per-total floor (the Gram rank of a largest clique of mutually non-orthogonal lines). Both are inputs here (taken from #446 and #595), not re-derived. A window (unit, T, h) is *closed* when every such decoder has cost ≥ N(h) = ⌈v·x\*(h)⌉, where x\*(h) is the break-even ratio against the E8 ceiling at window h (`lib/fx.py`).

## 1. Where to look instead (condensed escape map; ARGUED, from our own analysis, not recomputed here)

The room under #595's ceiling is real: #595 bounds κ ≤ 5.1595e-3; the best conditional κ among the open pull requests is **0.001676855229071321** (#1424, rohanarun; #1485, #1536, #1578 and others refine the endpoints of the same value), 3.08× under the bound (5.1595e-3 / 1.676855e-3 = 3.077). That figure is cited, not analysed.

Hypotheses that are still live for a root-line unit, with the threshold at which each would pay (ceiling level, not word level):

| hypothesis | kind | threshold |
|---|---|---|
| H3 non-star decoders for the sub-8 stages | convention | combined x lower by ≥ 0.167, about 20 copy-rank units on the 120 ports; +2.8% per copy-rank unit and stage |
| H6 non-root units, E8² norm-4 Pauli | scope | ×1.538 paper ceiling; blocked by the I−K compensation circuit: needs ≥ 0.384 delivered rank per helper (E8 achieves ≤ 0.153), at most 80,558 helpers |
| H2 a window-8 E8-quality unit | recorded (SAT, no proof logs; not rechecked here) | x ≤ 0.611 makes the best step vector break even (+0.838% LP, uncalibrated) |
| H4/H5 port subsets per stage, larger m | convention | H4 is negative unless the x gain exceeds 1; H5 only with a tiling gain larger than the cost of the larger m |
| H10 sparse low-rank Pauli kernel | convention | rank ≲ 1,350 (width 15) or ≤ 1,192 (width 17) |

Three numeric targets to aim at: (1) **≈ 20 copy-rank units** saved on the 120 ports by a non-star decoder (H3); (2) a unit at window 8 with **x ≤ 0.611**, or at window 9 with x < 0.600 (E8's own 72/120); (3) **≥ 0.384** delivered rank per compensation helper for the E8² Pauli unit, against ≤ 0.153 today.

## 2. Lemma A (T ≤ 2): cost ≥ v for every admissible pairing — PROVEN

> **Lemma A.** For every admissible B and every exact decoder over Q with T ≤ 2 totals, r_1 + r_2 ≥ v, hence cost ≥ Σ_j r_j ≥ v.

*Proof.* T = 1 is the case p_2 = q_2 = 0. Since M_tt ≠ 0, every line lies in D_1 or D_2. Put X = D_1 ∩ D_2 and P_j = D_j \ X.

*Private lines peel.* Let t ∈ P_1. Then p_2(t) = 0 or q_2(t) = 0. If p_2(t) = 0, row t of M is p_1(t) q_1ᵀ with p_1(t) ≠ 0, so B_ts = 1 (s ≠ t) forces q_1(s) = 0, i.e. s ∉ A_1: row t of B[R_1, A_1] is the unit vector e_t. If q_2(t) = 0, column t of M is q_1(t) p_1, and column t of B[R_1, A_1] is e_t likewise. A unit row (column) lets one delete that row and column and lose exactly 1 from the rank; the other private lines keep their unit rows and columns after the deletion. The matrix that remains contains B[X, X]. Hence r_1 ≥ |P_1| + rank B[X, X], and symmetrically r_2 ≥ |P_2| + rank B[X, X].

*The shared part is triangular.* For t ∈ X all of p_1(t), p_2(t), q_1(t), q_2(t) are nonzero. Put α(t) = p_1(t)/p_2(t) and β(s) = −q_2(s)/q_1(s). Then M_ts = p_2(t) q_1(s) (α(t) − β(s)), so M_ts = 0 iff α(t) = β(s), and exactness at t says α(t) ≠ β(t). Let X_< = {α < β} and X_> = {α > β}, a partition of X (Q is ordered). For t, s ∈ X_< with B_ts = 1 (s ≠ t): α(t) = β(s) > α(s), so α(s) < α(t) strictly; ordering X_< by α makes B[X_<, X_<] unit triangular, of rank |X_<|. On X_> the same argument with β: α(t) = β(s) and α(t) > β(t) give β(s) > β(t). So rank B[X, X] ≥ max(|X_<|, |X_>|) ≥ |X|/2.

Summing, r_1 + r_2 ≥ |P_1| + |P_2| + |X| = v. ∎

*Remarks.* (i) The proof uses an ordered coefficient field; it is stated for decoders over Q. (ii) Over a field of characteristic 2 any T gives cost ≥ v: Lemma B below with K = F2 and B′ = B.

**Consequence (CHECKED arithmetic).** With the per-total floor c_j ≥ w for the cost c_j of the j-th total, a decoder that beats the E8 ceiling has at most ⌊c/w⌋ totals, where c is the largest cost with c/v < x\*(h_0), h_0 = max(ω, 5). `checks/lemma_a.py` recomputes this table; for A3-A8 and D4 it is ≤ 2, so Lemma A **closes A3-A8 and D4 for every admissible pairing**:

| unit | A3 | A4 | A5 | A6 | A7 | A8 | D4 | D5 | D6 | D7 | D8 | E6 | E7 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T_max | 1 | 1 | 2 | 2 | 2 | 2 | 2 | 3 | 4 | 4 | 5 | 5 | 5 |

D5-E7 have T_max ≥ 3 and stay open under Lemma A alone. **Scope of this table: windows h ≥ 5 throughout** (h_0 = max(ω, 5)). This covers every window of a unit: B is the identity on a clique of mutually non-orthogonal lines, so every window satisfies h ≥ rank_F2 B ≥ ω, and x\*(h) is nonincreasing in h (checked for h = 5…40), so the budget at h_0 covers every window h ≥ 5. D4 at windows 3 and 4 is outside it: at window 3 the budget is cst ≤ 9, which admits three totals (x\*(3) = 0.7956, x\*(4) = 0.7482), so Lemma A alone does not close D4 there; that case is not covered by this package.

**Instance check (CHECKED, sanity of the proof).** `checks/lemma_a.py` draws 2,100 random exact T ≤ 2 decoders and random admissible pairings (A3, A4, A5, D4, D5, D6, E6; 238 of them tight, r_1 + r_2 = v) and recomputes the three inequalities of the proof (r_1 + r_2 ≥ v; r_j ≥ |P_j| + rank B[X, X]; rank B[X, X] ≥ max(|X_<|, |X_>|)): no violation.

## 3. Lemma B (lift identity) — PROVEN

> **Lemma B.** Let B′ be any rational matrix with supp(B′) ⊆ supp(B) and nonzero diagonal. For any exact decoder with T totals, **v ≤ Σ_j rank_Q B′[R_j, A_j].**

*Proof.* Off the diagonal, B′_ts ≠ 0 implies B_ts = 1 implies M_ts = 0. So the Hadamard product B′ ∘ M = diag(B′_tt M_tt), which has rank v. On the other hand M = Σ_j p_j q_jᵀ gives B′ ∘ M = Σ_j D(p_j) B′ D(q_j), where D(·) is the diagonal matrix of a vector; the j-th term vanishes outside R_j × A_j and is B′[R_j, A_j] with rows and columns scaled by nonzero numbers, so its rank is rank_Q B′[R_j, A_j]. Rank is subadditive. ∎

The same proof works over any field K with B′ over K supported on supp(B). With K = F2 and B′ = B it gives Σ_j r_j ≥ v for every decoder over F2: no F2 decoder is cheaper than v.

**Corollary (what a cheap decoder must look like).** Suppose cost < v. Then Σ_j r_j < v, and Lemma B says that for **every** rational B′ on the support of B the Q-ranks Σ_j rank_Q B′[R_j, A_j] are at least v, above the F2 ranks. So the blocks B[R_j, A_j] are *jointly non-liftable*: no common rational re-weighting of the ones of B brings every block's Q-rank down to its F2 rank. Conversely, if some B′ on the support has rank_Q B′[R_j, A_j] ≤ r_j for every j (for instance when all blocks are all-ones J-blocks, unimodular, or carry a common sign lift), then Σ_j r_j ≥ v and the cost is at least v. A cost below v therefore needs characteristic-2 cancellation that no re-weighting of the same support removes.

**Instance check (CHECKED).** `checks/lemma_b.py` (i) verifies the identity B′ ∘ M = diag(B′_tt M_tt) = Σ_j D(p_j) B′ D(q_j) exactly and the inequality on 720 random decoder-and-lift pairs (A3, D4, D5, A4; T = 3, 4); (ii) on the dyadic decoders of ERR1 below (E6 with 6 totals, E7 with 7, E8 with 8) checks the identity exactly for B′ = B0 and for random signed and positive integer weightings and prints the Q-rank sums (computed modulo the prime 2^61−1, which never exceeds rank_Q, so each printed sum is a valid lower bound): on E8, Σ_j rank_F2 B0[R_j, A_j] = 72 < 120 = v while the 0/1 lift B0 already has Σ_j rank_Q ≥ 426 ≥ v, and so does every sampled weighting; this is the corollary seen on real data (the E8 decoder is a cost-below-v decoder, and it is not liftable).

**Illustration only (not used anywhere).** The 7 × 7 point-line incidence matrix of the Fano plane has F2-rank 4 and Q-rank 7 (printed by `lemma_b.py`); this is the standard source of an F2/Q rank gap and has the shape the corollary demands. We have **not** derived the E7/E8 blocks from this picture.

## 4. Erratum to #595 (ERR1) — CHECKED

#595 (`research/format-limits/README.md`, line 205, the bit 120/72 row) states: "proved given #446 Theorem C: the F2 decoder of the E8 pattern needs 9 totals (its F2 minrank is 9; c = 8 is UNSAT, checked in `c6`), and each star total costs β = 8 ...". The restriction to F2 decoders is not justified for decoders over Q: the count of totals through rank_F2 B0 **fails over Q.** For a unit with Gram matrix G, choose n = rank_Q G independent lines, let P be the coordinates of all lines in that basis and Q = P·C with C the basis Gram matrix; then P·Qᵀ = G exactly, all entries are dyadic, M = G has M_tt ≠ 0 and M_ts = 0 wherever B0_ts = 1. `checks/err1.py` rebuilds these decoders in exact rationals and checks it: **E8 uses 8 < 9 = rank_F2 B0 totals and E6 uses 6 < 7 = rank_F2 B0** (also A4 4 < 5, A6 6 < 7, A8 8 < 9, each against rank_F2 B0). For E8 the eight block ranks are 9 each, sum 72: the cost 72 of #595 is attained by the 8-total decoder too, so the erratum concerns the count premise (the number of totals), not the E8 cost. Exact 8-term decoders of the E8 pattern already appear in #717, #968 and #1077; the point here is the correction to the #595 row. The count bound that survives over every field is a clique bound (#totals ≥ the largest clique of the pairing's one-pattern), not the F2 minimum rank; we do not prove it here (see §5).

This is a second erratum to #595; the one in #717 (E1, the ρ-family multipliers) is a different statement.

## 5. Scope, exactly

1. *Clique count result (ARGUED elsewhere; not proved here).* A bound on the **number** of totals by an orthogonal clique of the pairing holds for pairings with B = 1 on the clique (B0-type). It is not used below.
2. *All pairings, T ≤ 2:* Lemma A (§2): PROVEN.
3. *All pairings, T = 3:* only **D5** is closed, by SAT (§6). D6-D8, E6 and E7 at T = 3, and T = 4, 5 anywhere, are **open**.
4. *Everything else is open.* No transfer from D5 to D6 or E6 is claimed: their floors are w = 5, so a statement at block ranks ≤ 4 does not bear on them.

## 6. D5 at T = 3 — CNF regeneration CHECKED; kissat UNSAT and drat-trim VERIFIED RECORDED; and the open windows

**Result.** No exact rank-3 decoder on D5 has all r_j ≤ 4. Hence on D5 the cost is at least 13 = N(h7) = N(h8), which closes the D5 T = 3 windows h7-8. Status: the CNF regeneration is CHECKED here; the kissat refutation and its DRAT verification are the recorded status of one run (the 1.71 GB proof is not shipped).

| item | value |
|---|---|
| CNF | 11131 variables, 39835 clauses, sha256 `f5e75d3b1a484e02b3a832b6b5de6705cd47f3a22c2f92bdb7899875a7c17796` |
| solver | kissat 4.0.4, `s UNSATISFIABLE`, 892 s, exit 20 (`evidence/d5_kissat.txt`) |
| proof | `d5_zr_p.drat`, 1,710,338,687 bytes, sha256 `1b0e28b8b1d6abf36d6b66900594a4ba3fcbb8d3d4b1b329bd4e89aaca3cfaf3` (of our run; not shipped) |
| checker | drat-trim (`drat-trim.c` sha256 `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`): `s VERIFIED`, 1254.8 s (`evidence/d5_drat-trim.txt`) |
| audit | independent read-only audit, SOUND-WITH-CAVEATS (`evidence/D5-AUDIT.md`): regenerates the CNF byte-identically; 14 genuine rational decoders are all SAT at their true F2 ranks and all UNSAT with the largest cap lowered by one; Theorem C and the window arithmetic were taken as given; its caveat C1 (DRAT check pending) has since been discharged by `evidence/d5_drat-trim.txt` |

**Encoding** (`sat/gen.py`). Variables: the shared pairing B (zero off orthogonal pairs), the supports of the p_j and q_j, and three rank-≤ 4 factorisations B[R_j, A_j] = U_j W_jᵀ over F2 on the whole R_j × A_j, off-D entries included (the D-only version is satisfiable at once, so the spill of a private pair into the other totals is essential). Clauses, each implied by a genuine decoder: cover (every line is in some D_j); no transitive 4-tournament of orthogonal lines with B = 1 (M[S,S] would be triangular of rank 4 > 3); a mutually paired 3-set meets every D_j (with M[S,S] diagonal invertible and P_S invertible, Σ_{t∈S} p_j(t) q_j(t)/M_tt = (P_S⁻¹ P_S)_jj = 1); a single nonzero product p_j(t) q_j(s) cannot cancel; the K_{2,2} condition (two distinct points do not lie on two distinct lines; T = 3 only). Symmetry breaking: totals sorted by |D_j|, a line of the largest D_j moved to line 0 (the Weyl group is transitive on the 20 lines), zero padding and reduced row echelon form of W^T. Monotone restriction: an exact decoder restricted to a sub-system is exact there.

**Rerun** (from `research/root-unit-decoder-lemmas/sat/`; solvers are not part of `verify.sh`):

```sh
python3 gen.py D5 3 4,4,4 OUT.cnf --sb --C7 --zero --rref                 # sha256 of OUT.cnf must equal the CNF digest above (verify.sh does exactly this)
kissat -q --no-binary OUT.cnf OUT.drat                                  # exit 20, s UNSATISFIABLE
drat-trim OUT.cnf OUT.drat -t 50000                                     # s VERIFIED
```

`verify.sh` regenerates the CNF and compares the hash and the header (`p cnf 11131 39835`); it does not solve.

**The windows that remain open.** N(h) is the least cost that rules the window h out (`checks/windows.py` recomputes it; at the exact tie x\*(9) = 3/5 a cost of 18 on D6 is a tie, so N = 18 there). D5 T = 3 windows h7-8 are closed above; the rest of the T = 3 range is open:

| unit | v | w | 3w | N(h) over the open T = 3 range |
|---|---|---|---|---|
| D5 | 20 | 4 | 12 | T = 3 windows h7-8 closed (was 13) |
| D6 | 30 | 5 | 15 | h7 20, h8 19, h9-10 18, h11-13 17, h14-17 16 |
| D7 | 42 | 6 | 18 | h7 28, h8 27, h9 26, h10 25, h11-12 24, h13-14 23, h15-17 22, h18-19 21, h20-21 20, h22-24 19 |
| D8 | 56 | 7 | 21 | h7 37, h8 35, h9 34, h10 33, h11 32, h12-13 31, h14-15 30, h16-17 29, h18 28, h19-20 27, h21-22 26, h23-24 25, h25-26 24, h27 23, h28-29 22 |
| E6 | 36 | 5 | 15 | h8 23, h9 22, h10-11 21, h12-14 20, h15-17 19, h18-19 18, h20-22 17, h23-25 16 |
| E7 | 63 | 7 | 21 | h8 40, h9 38, h10 37, h11 36, h12-13 35, h14 34, h15-16 33, h17 32, h18-19 31, h20-21 30, h22 29, h23-24 28, h25 27, h26-27 26, h28-29 25, h30 24, h31-32 23, h33 22 |

The h-ranges are the ranges left open by earlier facts (T ≤ 2 by Lemma A; E6 and E7 at h = 7 by the unique rank-7 pairing; counting arguments at h ≤ 6), which are recorded in our notes and not recomputed here. Open T = 4, 5 windows also exist (D7 T4 h7-10; D8 T4 h7-17, T5 h7; E6 T4 h8-11; E7 T4 h8-22, T5 h8-11).

## 7. Open problem (F′) — OPEN

**Definition.** For a rational T-decoder M with supports π (rows) and σ (columns), an *L8 labelling* is a choice of F2 vectors a(t) ⊆ π(t), b(s) ⊆ σ(s), put K_ts = a(t)·b(s) mod 2. Define cert(M) as the largest |S| for which there is an order on S with K_tt = 1 on S and K_ts = 0 for every incidence M_ts = 0 with t before s (t, s ∈ S). It does not depend on B.

**Lemma (PROVEN).** cost ≥ Σ_j r_j ≥ cert(M) for every admissible B. *Proof.* With x_j(t) = a(t)_j, y_j(s) = b(s)_j one has B ∘ K = Σ_j D(x_j) B D(y_j), and each term is a sub-block of B[R_j, A_j] (x_j(t) ≠ 0 forces t ∈ R_j, as a(t) ⊆ π(t)), so rank_F2(B ∘ K) ≤ Σ_j r_j. Then (B ∘ K)[S, S] has unit diagonal (B_tt = K_tt = 1), and for t before s in the order, B_ts = 1 forces M_ts = 0 (an incidence), hence K_ts = 0; so all entries of (B ∘ K)[S, S] on one side of the diagonal vanish, the matrix is unit triangular, and its rank is |S|. Altogether cost ≥ Σ_j r_j ≥ rank_F2(B ∘ K) ≥ |S|. ∎ (Lemma A is the case a = b = e_1 on X_<, a = b = e_2 on X_>.)

> **(F′)** For every exact rank-3 decoder on a root unit with v lines, **cert(M) ≥ ⌈2v/3⌉.**

*Consequence (PROVEN given F′).* By the window table, N(h) ≤ ⌈2v/3⌉ for every open T = 3 window (`windows.py`: max N(h)/v = 2/3, at D6 h7 and D7 h7), so F′ would close **every** open T = 3 window at once; no window needs more. (For T = 4: the same statement in PG(3,2) with a constant covering the T = 4 windows.) A constant below 1 is used on purpose; see Follow-ups.

**The obstruction (ARGUED).** Rescaling the totals by powers of 2 and reducing a primitive 2-integral p(t), q(s) modulo 2 gives F2 labels with a(t)·b(s) = 0 for every incidence. The lines t with a(t)·b(t) = 1 and the lines that can be repaired on one side by a label inside their support can be ordered; what resists are the *isotropic* lines whose minimal 2-adic valuations among the products p_k(t) q_k(t) are attained twice (two tied minima), where no one-sided repair exists. A structure theorem for these tied lines, or a rescaling that orders them mutually (as α versus β does for T = 2), would prove F′. Neither is known.

**Evidence, not proof.** On random rational T = 3 configurations (v = 6-12) the 2-adic bound gave at least 0.75v in every sampled case, and a search found cert = v on about 90 sampled configurations (recorded, not reproduced here).

## 8. Follow-ups

The 2-adic certificate theorem (cost ≥ |G| + |F|), its sharp B3/C3 example (certificate 18 of 19 lines) and further SAT closures (D6/E6 at caps (5,5,5), D7, D8, E7) are intended as separate follow-ups; none is claimed here.

## 9. Index

| id | result | status |
|---|---|---|
| R1 | condensed escape map and three numeric targets | ARGUED (from our analysis; not recomputed) |
| A1 | Lemma A: T ≤ 2 gives cost ≥ v for every admissible pairing | PROVEN |
| A2 | T_max table; A3-A8, D4 closed; 2,100 instance checks of the proof's inequalities | CHECKED |
| B1 | Lemma B: v ≤ Σ_j rank_Q B′[R_j, A_j]; corollary: jointly non-liftable blocks | PROVEN |
| B2 | identity and inequality on 720 random pairs and on the E6/E7/E8 dyadic decoders (E8: F2 sum 72 < 120 ≤ Q sums) | CHECKED |
| B3 | Fano 7 × 7: F2 rank 4, Q rank 7 | CHECKED; illustration only |
| E1 | ERR1 erratum to #595: dyadic exact decoders with rank_Q G totals (E8 8 < 9, E6 6 < 7) | CHECKED |
| S1 | D5, T = 3, caps (4,4,4): UNSAT; cost ≥ 13; D5 T = 3 windows h7-8 closed | CNF regeneration CHECKED; kissat and drat-trim runs RECORDED |
| W1 | window table N(h) of the open T = 3 cases and N(h) ≤ ⌈2v/3⌉ | CHECKED |
| L8 | cost ≥ cert(M) | PROVEN |
| F′ | cert ≥ ⌈2v/3⌉ for every rank-3 exact decoder | OPEN |

## Credits and overlap

Builds on **#595** (format limits; Theorem C pricing and C.6), **#446** (closed, not merged; Theorem C and the window/deficit theorems), **#717** and **#899** (invoice prices and package format), **#968** (themilkman216) and **#1077**, **#1180** (woklerx) and **#1171** (3xcalibur-tech) for the E8 decoder floors that the H3 row builds on, **#1238** (verification format). Overlap check (decoder / lift / minrank / T ≤ 2 searches of the open and merged list): **#1177** (RossRichardson, five-cube three-total masks) is consistent with Lemma A in its F2 setting and is a different object; **#1471** (field-specific tensor rank of the P112 graph) is the same kind of F2/Q gap for a different object; **#669** (star-decoder hierarchies) and **#1386** (P120 shared-total pairs) treat star decoders of the E8 unit, not root-unit decoders under Theorem C. We found no pull request that states Lemma A or Lemma B or the D5 closure.
