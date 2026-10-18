# Fleet brief: prove cost >= v at T = 3 (theorem (A))

**Read first:** ../PROOF.md §0–2 (model, L1–L8), §7 (Theorem M1), §9 (multi-copy certificate), and §11–12. §12 covers tied_min: cost 12 = v, the exchange proof, the 217 optima, and the fact that all of them lift to Q.

## Model
- Lines t = 1..v. For each t: a point p(t) ∈ Q³ and a line q(t) ∈ Q³ with p(t)·q(t) ≠ 0.
- The decoder is M = PQᵀ with rank ≤ 3 and totals j = 1, 2, 3.
- R_j = {t : p_j(t) ≠ 0}, A_j = {t : q_j(t) ≠ 0}.
- B is an F2 matrix: unit diagonal, B_ts = 1 allowed only where p(t)·q(s) = 0. (Root-system admissibility only removes options, so a proof for all B suffices.)
- cost = Σ_j rank_F2 B[R_j, A_j]. We drop the max(w, ·) floor; proving cost ≥ v is the strong form.

## Theorem (A), the target
cost ≥ v for every such configuration and every such B.

## Known facts
- **Lemma A:** (A) holds with ≤ 2 totals.
- **Lemma B, lift identity:** for any rational B′ with the same support as B (B′_tt ≠ 0), v ≤ Σ_j rank_Q B′[R_j, A_j].
  - So if some cost-minimising B has a **joint Q-lift** with rank_Q B′[R_j, A_j] = rank_F2 B[R_j, A_j] for all j, then (A) holds for that configuration.
- **Liftability conjecture (LC):** at T = 3, some cost-minimising B is jointly Q-liftable.
  - It is false at T ≥ 7 (E7/E8, Fano-type cancellation). It holds on all 217 optima of tied_min.
- **Theorem M1:** if every point has a zero coordinate, cost ≥ v/2.
- **Sharp example:** tied_min.json, 12 lines, points (1,±1,±1) against the B3 two-support lines. Cost 12 exactly. Ordering/label certificates provably stop at 11.

## Possible routes
- **Matroid route.** A binary matroid is representable over Q iff it is regular (no Fano F7 or F7* minor; Tutte). A block whose column matroid over F2 is regular admits a signing, so a Q-lift of the same rank exists (totally unimodular).
  - So LC would follow from: some optimal B has every block regular, and the per-block signings can be chosen *compatibly* on shared entries.
  - The rank ≤ 3 (P²) geometry of the decoder may forbid Fano minors in optimal blocks.
- **Exchange route.** Generalise §12.3: a block of unusually low rank forces its neighbours up.
- **Direct rank route.** Bound Σ rank_F2 by a single F2 rank of an assembled matrix, using incidence structure in P².

## Rules
- Write your findings to fleet/<yourname>.md, short and precise: statements, proofs, counterexamples.
- Every claim must be machine-checked on tied_min.json, cex_min_1 (../cex/), and random small configurations, in exact arithmetic.
- Compute: at most 1 process each, no SAT solvers (math focus), CP-SAT only if tiny (num_workers 1, ≤ 2 min). No git.
