# Characteristic-2 shadows of rank-3 decoders: the anti-Fano bound by first-order jets, with a Lean-checked core (no κ claim)

> **What is claimed, and what is not.** This package studies the three-total (T = 3) pairing-cost problem of #2111 through *characteristic 2*: a realisation of the incidence pattern over a field of characteristic 2 (Lemma CR2), its multiplicative version (Theorem B2), and a valued version, the *first-order jet* (Lemma VCR2, Corollary J, Theorem T′).
> **Claimed.**
> (1) PROVEN (statements and proofs below; the core lemma, Lemma B and Lemma CR2 are also machine-checked in Lean, §7): Lemma CR2 with its tropical / 2-adic corollary; Theorem B2 (the map φ; cost ≥ v − |H| − |F| + MAS(W[F])); Lemma VCR2 and Corollary J (a B-independent jet test); **Theorem T′: the 12-line configuration `tied_min` of #2111 (the anti-Fano configuration) has cost ≥ 12 for every admissible B, by a first-order jet, with no SAT call and no enumeration**; Lemma F (the first-order obstruction is a binary flow); Lemma A (T ≤ 2) as a one-line corollary of CR2.
> (2) PROVEN, with one quoted step: the generic-rank / split bound (Lemma GR, Lemma Split). That the split bound is *complete* (equivalent to (A)) uses a standard min-max that is quoted, not proved here, and is checked on instances.
> (3) CHECKED: the data of §4 (exact, by `verify.sh`, or recorded with the script named).
> (4) Three counterexamples to "the first-order jet always works" (jf0, jf1, jf2) in which the jet fails at order 1 and order 2, but (A) still holds (exact costs 12, 14, ≥ 16 against v = 9, 9, 11).
>
> **Not claimed.** No κ gain, no word, no new window. **(A) at T = 3 — cost ≥ v for every exact three-total decoder over Q — is neither proved nor refuted here.** The "2-adic shadow" conjecture (§6) is a conjecture. T′ is a bound for one configuration (and for the 4095 sub-configurations of it, by the same test), not for all configurations.

## 0. Reading this package

Every result has one of three statuses:

- **PROVEN**: a proof is in this README (short ones in full; the longer ones in `evidence/PROOF-working-notes.md`, a verbatim snapshot of our working card, section numbers cited as "WN §k"). The scripts only sanity-check proofs on instances.
- **CHECKED**: recomputed by `verify.sh` in exact arithmetic (integers, F2, GF(2^k), exhaustive enumeration), the check group named; or **CHECKED (recorded)**: a result of our own working scripts that `verify.sh` does **not** repeat. The script is in `scripts/` and the count is stated.
- **OPEN**: a precisely stated question, or an argument that is not a proof.

```sh
python3 -m pip install -r research/char2-jets/requirements.txt     # python-sat and numpy; a C compiler (cc) is also needed
bash research/char2-jets/verify.sh /fresh/output/dir                  # from a checkout or `git archive` of the whole repository; no Lean needed
LEAN=1 bash research/char2-jets/verify.sh /fresh/output/dir            # optional extra step: `lake build` of lean/ (needs Mathlib at the pinned revision)
```

Step 0 checks every file against `MANIFEST.sha256` and stops with exit 1 on any mismatch; then `c/enumall.c` is compiled and five check groups run one after the other, one PASS/FAIL line per assertion (about one minute). `scripts/` holds the exploratory scripts of the working card with their paths fixed; `verify.sh` does not run them. `scripts/make_data.py` regenerates `data/tied_min_B.json` and `data/cr2_realisations.json`.

## 1. Model (as in #595, #446 Theorem C, #1590, #2111)

A configuration is a list of lines t = 1…v, each with a point p(t) ∈ Q³ and a line q(t) ∈ Q³ with p(t)·q(t) ≠ 0. A **pairing** B is a 0/1 matrix over F2 with unit diagonal and B_ts = 1 (s ≠ t) only where p(t)·q(s) = 0 (*admissible*). An exact decoder with T = 3 totals is M = Σ_{j≤3} p_j q_jᵀ over Q with M_tt ≠ 0 and M_ts = 0 wherever B_ts = 1. Write R_j = supp p_j, A_j = supp q_j, π(t) = {j : p_j(t) ≠ 0}, σ(t) = {j : q_j(t) ≠ 0}, D(t) = π(t) ∩ σ(t) ≠ ∅, and

**cost(B) := Σ_j rank_F2 B[R_j, A_j]**

(the floor w of Theorem C is dropped, so a lower bound on this sum is the stronger statement). Let E = {(t, s) : t ≠ s, B_ts = 1}. An incidence (t, s) matters only if it lies inside some block, i.e. π(t) ∩ σ(s) ≠ ∅; `free` in the code is the list of these incidences for the full pattern.

**Target (A).** cost(B) ≥ v for every exact decoder and every admissible B. Known: T ≤ 2 (Lemma A of #1590); fails for T ≥ 7 (#1590 ERR1). Open at T = 3 (#2111). **Lemma B** (#1590): for every rational B′ with supp B′ ⊆ supp B and B′_tt ≠ 0, v ≤ Σ_j rank_Q B′[R_j, A_j]. `tied_min` is the 12-line configuration of #2111 §4 (all entries ±1 or 0; cost exactly 12 = v, 217 optima); `cex_min_1`, `gad`, `aff14`, `cex_joint_v7`, … are the other configurations of #2111, copied to `data/`. (The package is self-contained: it reads nothing outside `research/char2-jets/`; #2111 and #2125 are cited for context.)

The statements below use **Lemma GR** (§3): for any field K ⊇ F2 and support-compatible vectors P~(t), Q~(s) ∈ K³ (supp P~(t) ⊆ π(t), supp Q~(s) ⊆ σ(s); nothing else assumed), cost(B) ≥ rank_K (B ∘ P~Q~ᵀ). *Proof.* B ∘ P~Q~ᵀ = Σ_j D(p~_j) B D(q~_j) (p~_j the j-th coordinate over the lines), and rank_K D(p~_j) B D(q~_j) ≤ rank_K B[R_j, A_j] ≤ rank_F2 B[R_j, A_j] since p~_j vanishes off R_j and q~_j off A_j. ∎ This is the same one-field-extension argument as Lemma B, and its diagonal case (B ∘ P~Q~ᵀ diagonal with nonzero diagonal) is the core lemma formalised in Lean (§7); Lean does not prove the general bound rank N ≤ cost.

## 2. PROVEN

### 2.1 Lemma CR2 (characteristic-2 realisation) and its corollaries

**Lemma CR2.** Suppose a field K of characteristic 2 and vectors P~(t), Q~(s) ∈ K³ satisfy (i) supp P~(t) ⊆ π(t), supp Q~(s) ⊆ σ(s); (ii) P~(t)·Q~(s) = 0 for every (t, s) ∈ E; (iii) P~(t)·Q~(t) ≠ 0 for every t. Then **cost(B) ≥ v**.
*Proof.* N := B ∘ P~Q~ᵀ has N_ts = B_ts P~(t)·Q~(s), so N = diag(P~(t)·Q~(t)) has rank v; by Lemma GR, cost(B) ≥ rank N = v. ∎
CR2 depends only on E and is down-closed (a realisation of E realises every E′ ⊆ E; extra incidences, coinciding points and zero coordinates are allowed). So **if the full pattern `free` of a configuration is CR2, (A) holds for it for every B at once.**

**Lemma A (T ≤ 2) as a corollary.** For T = 2 the objects live in P¹: p(t)·q(s) = 0 iff p(t) = perp q(s). Map the finitely many used points of P¹(Q) (the p(t) and the perp q(s)) injectively into P¹(F̄2), fixing [1:0] and [0:1]; the image vectors realise the full pattern (incidence = equality, preserved; diagonal = inequality, preserved by injectivity; supports preserved by fixing the two coordinate points). By CR2, cost ≥ v. CHECKED: group d (60 random T = 2 configurations, explicit injection into GF(2⁶)).

**Corollary (2-adic / tropical reduction).** Let ν be a valuation on K ⊇ Q extending v₂, and suppose a ∈ ((1/n)Z)³ satisfies, for every t, ν(p(t)·q(t)) = min_{j∈π(t)}(ν p_j(t) + a_j) + min_{j∈σ(t)}(ν q_j(t) − a_j). Then the full pattern is CR2. *Proof.* Replace p_j ← ϖ^{a_j} p_j, q_j ← ϖ^{−a_j} q_j: all products p(t)·q(s), hence incidences and supports, are unchanged. Scale each vector to minimum valuation 0 and reduce to the residue field (characteristic 2): incidences reduce to incidences, supports can only shrink, and the hypothesis says the diagonal product has valuation exactly 0, so it reduces to a nonzero element. ∎ (a = 0: if every primitive integer p(t)·q(t) is odd, (A) holds for every B.) For `tied_min`, p·q = ±1 ± 1 = ±2 on every line and no a works.

### 2.2 Theorem B2 (the multiplicative map φ)

Call an incidence (t, s) *binomial* if |π(t) ∩ σ(s)| = 2 and *wild* if |π(t) ∩ σ(s)| = 3. Call a line t *harmonic* if |D(t)| = 2 and the two terms of p(t)·q(t) are equal (p(t)·q(t) = 2 p_i(t) q_i(t)). H = harmonic lines, W = wild incidences, F = lines with p(t) and q(t) both of full support (F ∩ H = ∅). Let K = F2(z_p : p prime) and φ : Q* → K* the homomorphism with φ(−1) = 1, φ(p) = z_p (φ(0) = 0). Apply φ entrywise: P~ = φ(p), Q~ = φ(q); supports are preserved.

- A binomial incidence x_i y_i + x_j y_j = 0 means x_i y_i = −x_j y_j, so φ(x_i)φ(y_i) = φ(x_j)φ(y_j) and P~(t)·Q~(s) = 0 in characteristic 2: every binomial incidence is preserved.
- P~(t)·Q~(t) = Σ_{j∈D(t)} φ(p_j q_j) is a sum of |D(t)| monomials, zero iff they cancel in pairs: never for |D| ∈ {1, 3}; for |D| = 2 iff |p_i q_i| = |p_j q_j|, i.e. iff t is harmonic. **The diagonal vanishes exactly on H.**

**Theorem B2.** Let X ⊆ [v] \ H contain no directed cycle of wild incidences. Then cost(B) ≥ |X| for every admissible B. Consequently: (i) no wild incidence and no harmonic line ⇒ the full pattern is CR2 ⇒ (A) for every B; (ii) no wild incidence ⇒ cost ≥ v − |H|; (iii) in general cost ≥ v − |H| − |F| + MAS(W[F]) (a wild edge joins a full point to a full line, so a wild cycle lies inside F; MAS(W[F]) = the maximum size of an induced acyclic vertex set, i.e. of a set Y ⊆ F of lines whose induced wild subgraph W[Y] has no directed cycle; it is applied with X = ([v] \ (H ∪ F)) ∪ Y. It is not the maximum acyclic edge set: that reading is false, see #2334 and #2340).
*Proof.* N := B ∘ P~Q~ᵀ has rank ≤ cost (Lemma GR). Off the diagonal, N_ts ≠ 0 only if B_ts = 1 and the incidence is not preserved, i.e. wild; N[X, X] is triangular in a topological order of W[X] with nonzero diagonal. ∎
`tied_min` is no-wild with all 12 lines harmonic; the anti-Fano obstruction *is* the harmonic-conjugate configuration ("1 + 1 = 0" is "harmonic conjugate = itself").

### 2.3 Lemma VCR2, Corollary J, Theorem T′

**Lemma VCR2 (valuative CR2).** Let K be a field of characteristic 2 with a valuation ν (e.g. F((ε))), P~, Q~ support-compatible, w_ts := ν(P~(t)·Q~(s)). If every directed cycle C of E satisfies Σ_{(t,s)∈C} w_ts > Σ_{t∈C} w_tt and all w_tt < ∞ (a separate hypothesis), then cost(B) ≥ v for every B with off-diagonal support in E.
*Proof.* N = B ∘ P~Q~ᵀ has rank ≤ cost (Lemma GR). det N = Σ_σ Π_t N_{tσ(t)}; a permutation σ ≠ id splits into fixed points and cycles of E, so its term has valuation > Σ_t w_tt, the valuation of the identity term. No cancellation: det N ≠ 0. ∎ (CR2 is the case w = ∞ on E.)

**Corollary J (first-order jets; B-independent).** Let the configuration be no-wild, φ as above, and suppose support-compatible X, Y over K satisfy
 (J1) φp(t)·Y(s) + X(t)·φq(s) = 0 for every incidence (t, s) of the full pattern;
 (J2) δ′_t := φp(t)·Y(t) + X(t)·φq(t) ≠ 0 for every harmonic t.
Then with P~ = φP + εX, Q~ = φQ + εY over K((ε)) the valuations are w = ∞ or ≥ 2 on incidences, w_tt = 0 on non-harmonic and 1 on harmonic lines, so every cycle has Σ_edges ≥ 2|C| > |C| ≥ Σ_vertices, and (A) holds for the configuration for every B (Lemma VCR2).
(J1) is a homogeneous linear system; (J2) asks the v functionals δ′_t to be nonzero *simultaneously* on its solution space. Over an infinite field it suffices that **each** δ′_t is not identically zero on the solution space (a vector space is not a finite union of proper subspaces); the solution space is defined over the field of the data, and the test is run over GF(2¹⁶) and extended to its algebraic closure. So Corollary J is a B-independent linear-algebra certificate. The proof uses only a homomorphism φ : Q* → K* with φ(−1) = 1 whose diagonal vanishes exactly on H (K need not be F2(z_p)); the checks take z_p ↦ random elements of GF(2¹⁶)* and verify these order-0 conditions exactly for each configuration. T′ is unaffected (φ ≡ 1 over F2).

**Theorem T′ (cost(`tied_min`) ≥ 12 for every admissible B).** `tied_min` has four points (1, ±1, ±1) forming a complete quadrangle with diagonal points e₁, e₂, e₃, and 12 lines (u, k): the point u together with the line of class k (q_k = 0, so it passes through e_k) that is a side of the quadrangle *not* containing u. For each k the four points split into two pairs, M_k, the two sides of class k. Here φ(`tied_min`) is the Fano collapse: all entries are ±1, so every point becomes the Fano centre c = (1,1,1) and every class-k line becomes the Fano line ℓ_k through c and e_k (ℓ₀ = (0,1,1), ℓ₁ = (1,0,1), ℓ₂ = (1,1,0)). Write f_k(t) = X(t)·ℓ_k and g(s) = c·Y(s). Since ℓ₀ + ℓ₁ + ℓ₂ = 0 in characteristic 2, f₀ + f₁ + f₂ = 0 at each point t, and (X(t) of full support) any such triple occurs; g(s) is arbitrary (Y(s) has two free entries). (J1) for an incidence t → s, s of class k, reads f_k(t) = g(s). The class-k lines carrying a side {x, y} of M_k are the two lines (u, k), u in the other pair; so every line t whose point lies on a side S of M_k needs f_k(t) = G_k(S), the common g-value of the lines carrying S. (J2) for line (u, k): f_k = G_k(side ∋ u) ≠ g(u, k) = G_k(side ∌ u), i.e. h_k := G_k(S) + G_k(S′) ≠ 0 for the two sides S, S′ of M_k. The constraint f₀ + f₁ + f₂ = 0 at the four quadrangle points reads: at a, Σ_k G_k(side_k(a)) = 0; at the vertex b paired with a in M₀ the same sum plus h₁ + h₂ = 0, so h₁ = h₂; likewise h₀ = h₂ and h₀ = h₁. **Solution: h₀ = h₁ = h₂ = h ≠ 0**, any G with Σ_k G_k(side_k(a)) = 0. So (J1) and (J2) are solvable already over F2, Corollary J applies, and cost(B) ≥ 12 for every admissible B; with an optimum of #2111, = 12. ∎ (`checks/a_tprime.py` builds the jet from this hand formula.)
CHECKED (group a, exact over F2): the explicit jet (h = 1) satisfies (J1) on all 72 incidences and (J2) on all 12 lines; order 0 holds on all incidences and diagonals; and N = B ∘ P~Q~ᵀ at a fixed ε ∈ GF(2¹⁶) has rank 12 for the 217 optima, the full B and 300 random admissible B (518/518 stored matrices, `data/tied_min_B.json`; for the optima the exact cost Σ rank is also recomputed and equals 12; for the full B it is 24).

*Reading.* `tied_min` = anti-Fano is not realisable in characteristic 2 (§4), but it is realisable to first order around its Fano collapse: the equal-characteristic shadow of its 2-adic picture (diagonal products of valuation ν(2) = 1 ↔ diagonal of ε-order 1; incidences of valuation ∞ ↔ ε-order ≥ 2). The tightness of `tied_min` (cost = v) is the statement that the jet has order exactly 1 on every line.

### 2.4 Lemma F (the first-order obstruction is a binary flow)

Write X(t) = φp(t) ∘ ξ(t), Y(s) = φq(s) ∘ η(s) (every support-compatible tangent has this form). On a binomial incidence over the pair {i, j}, (J1) becomes Δ_ij ξ(t) = Δ_ij η(s), with Δ_ij ξ = ξ_i + ξ_j; for harmonic t with D(t) = {i, j}, (J2) is Δ_ij ξ(t) ≠ Δ_ij η(t). Hence **the jet test fails at t iff the harmonic equation at t is an F2-combination of incidence equations**: a set Z of incidence edges plus the harmonic edge, with, at each object whose support has size 2, an even number of Z-edges, and at each object of full support, equal parities of Z-edges over the three pairs {01}, {02}, {12}. Any such Z has an *even* number of incidence edges (evaluate at the sign labels ξ_j(t) = [p_j(t) < 0], η_j(s) = [q_j(s) < 0], which give 1 on every incidence and 0 on every harmonic diagonal). On objects with two-element supports only (a cycle in P¹) Z would be a cycle with an odd number of incidences, so **no obstruction exists there**: the Q-geometry (−1 ≠ 1) enters exactly through this parity. With full-support objects the parity condition is "Fano-like" (Δ₀₁ + Δ₀₂ + Δ₁₂ = 0) and flows of even incidence count can exist (jf0, jf1, jf2, §5).

## 3. The generic-rank / split bound

By Lemma GR the best bound of this kind is GR(B) := rank over F2(X, Y) of B ∘ XYᵀ (X_tj, j ∈ π(t), Y_sj, j ∈ σ(s), indeterminates). **PROVEN (Lemma Split).** Mod 2, det(B ∘ XYᵀ) = Σ_σ Π_t B_{tσ(t)} x(t)·y(σ(t)); the coefficient of the monomial Π_t x_{a(t)}(t) Π_s y_{b(s)}(s) is per(B ∘ K_ab) = det_F2(B ∘ K_ab), with K_ab[t, s] = [a(t) = b(s)], and after permuting B ∘ K_ab = ⊕_c B[R′_c, A′_c] with R′_c = a⁻¹(c) ⊆ R_c, A′_c = b⁻¹(c) ⊆ A_c. The same argument on minors gives
 **GR(B) = SPL(B) := max over row-partitions {R′_c ⊆ R_c} and column-partitions {A′_c ⊆ A_c} of Σ_c rank B[R′_c, A′_c]**,
and GR(B) = v iff a *perfect split* exists (three square nonsingular submatrices, one inside each block, whose row sets partition the lines and whose column sets partition the lines); a perfect split gives cost(B) ≥ v directly.
**Quoted, not proved here:** the independent-matching (Rado–Edmonds type) min-max SPL(B) = min_{S,T ⊆ [v]} (v − |S|) + (v − |T|) + Σ_c rank_F2 B[S ∩ R_c, T ∩ A_c]. "≤" is elementary; equality is cited from the matroid-union / linking-system literature from memory. CHECKED (recorded, `scripts/t9.py`): 300 random instances, v = 3–6, 92 of them with SPL < v, 0 mismatches. **Conditional corollary:** if (A) holds for every sub-configuration, then Σ_c rank B[S ∩ R_c, T ∩ A_c] ≥ |S ∩ T| ≥ |S| + |T| − v, so SPL(B) = v; hence, *given the min-max*, (A) at T = 3 ⟺ every admissible B on every configuration has a perfect split. The anti-Fano obstruction of §4 is an obstruction to the *diagonal* (CR2) form only, never to the generic form (GR = v for 100 random B at each of four densities on `tied_min`, `cex_min_1`, `gad`, `aff14`, `cex_joint_v7`: recorded, `scripts/t7.py`).

## 4. CHECKED

| Statement | Status | Where |
|---|---|---|
| T′: jet exact over F2 for `tied_min` ((J1) on 72 incidences, (J2) on 12 lines); 518 stored matrices have rank N = 12; the 217 optima have exact cost 12 | CHECKED (verify.sh) | group a |
| The 217 optima themselves (SAT enumeration of all B with block ranks ≤ (4,4,4)) | CHECKED (recorded); the stored list is what group a uses | `scripts/make_data.py`, `lib/satlib.py` |
| Lemma CR2 on 21 stored configurations: stored realisation vectors (not re-searched) are verified exactly (supports, all incidences, all diagonals, 40 random B each: N diagonal and cost ≥ v). All realise over GF(2) except `cex_min_1` (v = 19, 114 incidences) over GF(4) (none over GF(2)). So (A) holds on all of them for every B, by CR2 alone; in particular cost(`cex_min_1`) ≥ 19 for every B, where every order/label certificate of #2111 stops at 18 | CHECKED (verify.sh) | group b |
| `tied_min` full 72-incidence pattern is **not** CR2 over GF(2), GF(4), GF(8), GF(16) (exhaustive DFS) | CHECKED (verify.sh) | group b |
| 44 minimal non-CR2 sub-configurations of `tied_min` (32 of 6 lines, 12 of 7 lines; non-realisable over GF(2), GF(4), GF(8); every one-line deletion is realisable); the 32 six-line ones are tight (exhaustive minimum cost 6 = v) | CHECKED (verify.sh); minimum cost 8 for the seven-line ones is recorded (2²⁶ matrices each), `scripts/t4.py`, `scripts/t5.py` | group b |
| All 217 optima of `tied_min` are CR2 over GF(2) (off-diagonal supports of size 12, 14, 16, 18, 24); all minimisers and cost-(min+1) matrices of `cex_joint_v7`, `cech_v8`, `supmin_fail_v8`, `cex_wholeTS_v9`, `nojoint_21_1..4` are CR2 over GF(2) | CHECKED (recorded) | `scripts/t1.py`, `scripts/t2.py` |
| Corollary J holds on **all 4095** sub-configurations of `tied_min` and on **1500/1500** random all-harmonic configurations (v = 4–14, entries ±r^a, r ∈ {2,3,5}); exact order-0 conditions are re-checked for each | CHECKED (verify.sh) | group c |
| Corollary J holds on 1889 of 1892 random no-wild configurations with harmonic lines (mixed supports), failing on exactly the three jf0..2 | CHECKED (recorded) | `scripts/t16.py`, `scripts/t17.py` |
| Theorem B2: on random no-wild configurations φ preserves every block incidence and its zero diagonals are exactly H (80/80 re-run; 400/400 recorded); exhaustive minimum cost ≥ v − \|H\| (79 re-run, 379 recorded) | CHECKED | group d; `scripts/t11.py` |
| Lemma A, T = 2: explicit injection realisation, 60 random configurations | CHECKED (verify.sh) | group d |
| 300 random configurations containing a directed cycle of wild incidences (v = 6–12, entries ≤ 3): full pattern CR2 for all (293 over GF(2), 7 over GF(4)), so (A) holds on each by CR2 | CHECKED (recorded) | `scripts/t24.py` |
| Split min-max on 300 instances; GR = v on the stored configurations | CHECKED (recorded) | `scripts/t9.py`, `scripts/t7.py` |
| End-to-end CR2 (N = Σ_j D(p~_j) B D(q~_j) diagonal, nonzero diagonal, for 200 random B on each of four configurations) | CHECKED (recorded; group b repeats it with 40 B on all 21) | `scripts/verify_cr2.py` |

## 5. The three jet failures jf0, jf1, jf2

The random run of §4 (1892 no-wild configurations with harmonic lines) produced three configurations, stored in `data/jf0.json`, `jf1.json`, `jf2.json` (v = 11, 9, 9; 41, 27, 20 free incidences), in which a harmonic line is *immovable* at first order: δ′_t vanishes on the whole tangent space of (J1) (immovable lines: jf0: line 0; jf1: line 7; jf2: lines 0 and 2). The first-order jet does not exist, and this is independent of z_p (the full collapse φ₀ with all nonzero entries ↦ 1 fails at the same lines). None of the three is CR2 (GF(2), GF(4), GF(8)). They are not counterexamples to (A):

- **Order 2 fails structurally.** With P~ = φ₀P + εX₁ + ε²X₂ (same for Q~), the order-2 diagonal of an immovable line is the constant Q_t = X₁(t)·Y₁(t) + Σ c_e b_e (δ′_t = Σ c_e A_e a combination of the incidence functionals A_e, b_e = X₁(t_e)·Y₁(s_e)), independent of (X₂, Y₂). **CHECKED (verify.sh, group e; exact): Q_t is identically zero as a polynomial on the first-order tangent space V** for all four immovable lines, so the order-2 diagonal vanishes for every jet over every characteristic-2 field. (The Lemma F flow kills the quadratic term too.) Order ≥ 3 was not tested.
- **(A) holds, with slack.** jf1: v = 9, exact minimum cost **12** (exhaustive over 2²⁷ admissible B; 192 minimisers). jf2: v = 9, exact minimum cost **14** (2²⁰; 12 928 minimisers). jf0: v = 11, 41 free incidences (too many to enumerate): the CNF "cost ≤ K" (CaDiCaL, `lib/satlib.py`) is UNSAT for K ≤ 15 — group e re-runs K = 15 — so **cost(jf0) ≥ 16 > 11**; the exact value is unknown.
- **The B-dependent test works on the optima.** jf1: 186 of the 192 minimisers pass the first-order jet test on E = supp B (group e re-runs this) and are CR2 (recorded: `scripts/t23.py`); the other 6 pass neither test, but cost ≥ v holds there anyway. jf2: every one of the 12 928 minimisers passes the jet test on E = supp B and is CR2 (recorded: `scripts/t23.py`).

## 6. OPEN

1. **(A) at T = 3.** Nothing here proves it for all configurations.
2. **The "2-adic shadow" conjecture.** Every configuration over Q admits a characteristic-2 valued realisation (over F̄2((ε))) whose diagonal is strictly dominant on every directed cycle of incidences (Lemma VCR2); this would prove (A). It cannot hold at T ≥ 7 (E7/E8; (A) fails there), which is a consistency check only. The B-independent form is likely false (jf0..2 admit no jet certificate of order 1 or 2, and whether any order works is item 3); the B-dependent form (for every B, or for some minimiser, a cycle-dominant realisation of supp B) is open.
3. **Does the Lemma F flow obstruct at every order** on jf0..2 (orders ≥ 3 untested)?
4. **Wild cycles** (three-term incidences x_i y_i + x_j y_j + x_k y_k = 0), which φ breaks: no theorem here. All 300 recorded random wild-cycle configurations are CR2 (§4).
5. Completeness of the split min-max (§3): standard, quoted, not proved here.

## 7. Formal verification (Lean 4 + Mathlib)

`lean/DecoderDuality.lean` (about 230 lines; `lean/README.md` has the statements) formalises:

- **`hadamard_diag_rank_sum`** (the core lemma): over a field F, if the Hadamard product B_ts · Σ_j p_j(t) q_j(s) is diagonal with nonzero diagonal and supp p_j ⊆ S_j, supp q_j ⊆ U_j, then |ι| ≤ Σ_j rank B[S_j, U_j];
- **`lemmaB`**: Lemma B of #1590 in the form "B over K, B_tt ≠ 0, B_ts ≠ 0 ∧ t ≠ s ⇒ M_ts = 0, M_tt ≠ 0 ⇒ v ≤ Σ_j rank_K B[R_j, A_j]";
- **`lemmaCR2`**: Lemma CR2 above (B over F2 = ZMod 2, P~, Q~ over a field L of characteristic 2).

No `sorry`; the three `#print axioms` lines show only `propext`, `Classical.choice`, `Quot.sound`. Auxiliary results proved there: subadditivity of rank, `rank_diag_mul_mul_diag_le`, and `rank_map_le` for a ring hom of fields. The Lean file does **not** formalise Theorem B2, Lemma VCR2 (valuations), Corollary J, Theorem T′, Lemma F or the split bound; those rest on the proofs in §2 and the exact checks of §4. Build: `cd lean && LEAN_NUM_THREADS=4 lake build` (toolchain `leanprover/lean4:v4.33.0-rc1`; Mathlib at the revision pinned in `lean/lake-manifest.json`; `lake exe cache get` first on a fresh checkout). `verify.sh` does not need Lean; `LEAN=1 bash verify.sh` runs the build on a copy as an optional step. A successful build confirms the proof terms; it does not check that the statements match the prose above, which is for the reader to compare with `lean/README.md`.

## 8. Layout

`README.md`, `NOTICE.md`, `LICENSE`, `MANIFEST.sha256`, `requirements.txt`, `verify.sh`; `checks/` (`a_tprime.py` … `e_jetfail.py`, `provenance.py`, `common.py`); `lib/` (`kit.py`, `satlib.py`, `gr.py`, `cr2.py`, `phi.py`, `gen.py`, `tangent.py`, `jet2.py`, `col.py`); `c/enumall.c`; `data/` (configurations, `jf0..2.json`, `tm_noncr2.json`, `tied_min_B.json`, `cr2_realisations.json`); `scripts/` (exploratory scripts `t1`–`t24`, `tied_min_jet_cert.py`, `verify_cr2.py`, `make_data.py`, paths fixed); `lean/`; `evidence/PROOF-working-notes.md` (verbatim snapshot of the working notes, cited as "WN §k"; its §7 is the status list this README follows).
