# AUDIT: D5 T=3 caps (4,4,4) UNSAT => D5 T3 window (h7-8) closed   (independent read-only auditor, Oct 13)

**Verdict: SOUND-WITH-CAVEATS** (caveats are scope, not flaws; no encoding error found).

## Checks
0. Provenance. `gen.py D5 3 4,4,4 OUT --sb --C7 --zero --rref` regenerates a byte-identical file
   (sha256 f5e75d3b1a48...7796, 11131 vars / 39835 clauses). ade.D(5) = 20 lines e_i +- e_j.
1. Model fidelity. Every clause is implied by a genuine decoder:
   - C1 (cover) from M_tt != 0; x = r AND a is exactly D_j = R_j cap A_j.
   - C2 is imposed on the whole of R_j x A_j, off-D entries included: B_ts = U_t.W_s for orthogonal t != s,
     0 = U_t.W_s for non-orthogonal t != s, and 1 on the diagonal only when t in D_j (t in R_j and t in A_j means t in D_j).
     This is exactly "rank_F2 B[R_j,A_j] <= c_j". B is a single shared variable set, and B = 0 off the orthogonal pairs.
   - max(w, r_j) with w = 4 gives sum <= 12 iff every r_j <= 4. So UNSAT means some r_j >= 5, i.e. cost >= 13 = N(h7), N(h8).
2. Lemmas. Each proof is correct, and each encoding is no stronger than its lemma.
   - L3: clause over every ordering of a mutually orthogonal 4-set. M[S,S] is triangular with nonzero diagonal, so rank 4 > 3.
   - L4: the T-set must be mutually orthogonal with all 6 ordered B = 1. Then sum_t omega_j(t) = (P^-1 P)_jj = 1.
   - L5: y_j = r_tj AND a_sj; B_ts => not exactly one y_j. A single nonzero product cannot vanish.
   - L6/C7: t, t', s, s' are distinct (s in N_B(t) excludes s = t). eP forces B_tt' = B_t't = 0 and pi(t) = pi(t')
     (p(t) = lam p(t'), so M_tt' = lam M_t't' != 0, and the supports match). eL is the dual. p(t), q(t) != 0 because M_tt != 0.
     The lemma needs the projective plane, so it holds for T = 3 only, which is the case here.
3. SB. Weyl-group line permutations, computed from reflections, are transitive on the 20 lines (|W image| = 1920; also checked for D4).
   They preserve +-Gram, hence orthogonality, admissibility and every clause, and they preserve |D_j|.
   Caps are equal, so permuting the totals is a symmetry. Order: sort totals first, then move a line of D_0 to line 0.
   The two breakings are jointly sound. The seqcounter clause encodes |D_j| >= |D_j+1| as sum x_j + sum(not x_j+1) >= v,
   which is correct. |D_0| >= 7 is implied.
4. --zero + --rref. Start from any factorisation on R_j x A_j and pad U and W with zeros outside R_j and A_j.
   Left-multiplying W^T by g in GL(c,2) to reach RREF keeps the zero columns (s not in A_j). U g^-1 keeps the zero rows.
   Zeroing the U-columns that pair with zero RREF rows leaves U W^T unchanged. So a joint canonical form always exists,
   and there is no interaction problem. The RREF clauses (prefix-OR, pivot-column clearing, strictly increasing pivots,
   zero rows last) all hold for true RREF. A collision of 'xr' aux-var keys would only merge identical XOR gates, which is harmless.
5. Sanity test (scratchpad sanity.py). I built 14 genuine rational T=3 decoders: random p, q in {-1,0,1(,2)}^3 with M_tt != 0,
   R_j != A_j in general, and B = orthogonal pairs with M_ts = 0, either all of them or a random 60%. There were 11 on D4 and 3 on D5.
   For each I canonicalised the totals and lines exactly as --sb does, fixed B, pi and sigma as units, and set the caps to the true F2 ranks.
   **14/14 SAT** with the same flags, so no genuine decoder was excluded. **14/14 UNSAT** with the largest cap lowered by 1,
   so the caps bind exactly. The ranks were high (4-17), and I found no easy genuine decoder near cost 12 to test.

## Caveats
- C1. The DRAT/drat-trim check is still pending. Until it finishes, the result rests on a single kissat run.
- C2. The following are taken as given and were not audited: Thm C itself (beta_j >= max(w, rank_F2 B[R_j,A_j])), and the
  window arithmetic N(h7) = N(h8) = 13.
- C3. The sanity decoders are random and high-cost. They exercise C2, rref, zero, SB and the lemma clauses on genuine data,
  but they do not test a near-extremal dense-B decoder.
