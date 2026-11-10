# The port window of P104 is 9 in characteristic 2 (no kappa)

**No new kappa.** No word is built and nothing is priced. This package proves that every block-mask pattern on the ports of P104 has rank at least 9k over every field, so the window w(P104;F) is at least 9 for every field and exactly 9 in characteristic 2. Statements and proofs are in `THEOREM.md`.

Tags (as in `THEOREM.md`): **[C]** exact computation reproduced by `check.py` (one PASS line per claim); **[P]** hand proof; **[P+C]** a proof whose inequalities `check.py` also evaluates on explicit representations; **[R]** a solver run recorded in `data/sat_rows.json`, not repeated by the checks; **[Q]** quoted from another source.

## Setting

Ports, odd graph, k-block patterns and the window w = inf_k rank/k are those of `research/p104-port-window-haemers` (#6933): ports are vectors of F_2^9, orthogonal pairs get zero k x k blocks, diagonal blocks are invertible. P104 is the port set in `data/ports_p104.json`; P120 is the 120 vectors of weight 3 mod 4; P112 is P104 plus one of the two odd 8-cliques that P120 deletes.

## Results

1. **Edge inequality (E') [P+C].** The proof of #6933 Theorem 3 has a double count: the part of the block X_TT that is not new already lies inside the column space of gamma_T(c) (its Step 2 containment). Using the containment itself gives k <= g_T(c) + g_T(d) + min(Y_c, Y_d) for every edge port.
2. **Theorem 3' [P+C].** If the edge ports of an orthogonal 8-set can be charged so that every non-isolated vertex gets charge at least 2 (for instance minimum degree at least 4 with weights 1/2), every k-block pattern of rank 8k + j has j >= k, over every field.
3. **Values [P+C].** Every orthogonal 8-set of P104 has minimum degree 5 (P112: 6, P120: 7), so rank >= 9k for every k and every field. **w(P104;F) >= 9 for every field; w = 9 in characteristic 2** (Gram matrix). P112 and P120 are recovered without weights. With #7014 (13 disjoint 8-cliques, rank 13 over every field) and #6933 Theorem 4: **w(P104) is 9 in characteristic 2 and 13 otherwise** (P112: 9 and 14; P120: 9 and 15) [Q].
4. **Second proof [P+C].** A star inequality (LR) proves j >= k for minimum degree at least 4 by a radical dimension count.
5. **Corollaries [P+C].** H_f(G_{K_n}) = n+1 for n >= 5 over every field; H_f(Petersen;F) >= 9/2 over every field (**not checked against the literature**).
6. **Field-only dependence [P+C].** w(V;F) depends only on the characteristic of F.
7. **Solver rows [R].** F_2 instances inside P104 (Petersen k = 2 and 4; G_{K_5} k = 3) agree with the theorem, with same-size controls; no DRAT proofs. A k = 6 rank-53 run on 30 ports was undecided at 20 minutes and is not used.

## Scope and what is not claimed

No bound on kappa and no word. The window is defined by the uniform whole-block mask; sub-block masks, port-dependent block sizes and nonlinear labels are different models and are not covered. Whether a physical construction realises a k-block window with exactly this mask for k > 1 is not derived. No human has reviewed the proofs: two model sessions proved the result by different routes and a third read the first proof line by line (`THEOREM.md`, section 12).

## Exact checks

`python3.12 -I -B research/p104-port-window-nine/check.py` (about 6 s); it prints one PASS line per claim and ends with `PASS_P104_PORT_WINDOW_NINE`. Standard library only. The checks include planted violations that must be flagged. The solver rows are recorded, not repeated.

## Open next questions

1. Is there a pattern on P104 below ratio 9 in a model other than the uniform whole-block mask (port-dependent block sizes, sub-block masks)?
2. What is H_f(Petersen;F) between 9/2 and 5, and is 9/2 known or refuted in the literature?
3. Can the recorded UNSAT rows be certified with DRAT proofs, and can the k = 6 rank-53 run on 30 ports be decided?

The structured form with first steps and blockers is in `TASK.json`.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.
