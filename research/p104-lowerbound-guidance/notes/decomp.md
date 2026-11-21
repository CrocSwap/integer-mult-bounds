# DECOMP DC (Nov 20, Opus; theory + exact + Lean). Files: dc1.py / dc1.log (own exact word checker, Fractions, no sympy),
lean/decoder-duality/Nov15/CallerDecomp.lean (copy here). runlean rc=0, 7 s, peak 2.0 GB, no sorry/native_decide;
axioms of k1_n0, k1_tight, decomp_false, decomp_false_min = propext, Classical.choice, Quot.sound.
Not a retread: TIGHTPAD posed DECOMP as a CONJ, and EXTRATHIN classified e = 1 rank patterns for Q >= 1 (thins). Nobody tested whether
non-tightness forces a split for Q = 0 frames or words.

## 0. Verdict: DECOMP is FALSE (frame level [P Lean], word level [C exact] + [P paper] family)
The tightness-free SUP statement does NOT follow. Indecomposable non-tight components exist at every k >= 2 (frames) and k >= 3 (Q = 0 words).

## 1. Frame level [P Lean, CallerDecomp]
- `Splittable` = a nontrivial stage 2-colouring plus a role colouring with every role meeting only stages of its own colour. A direct sum of >= 2
  frames needs one. A non-tight frame with no split refutes DECOMP.
- MINIMAL witness `decomp_false_min`: k = 2, n = 1, e = 2k-n-2 = 1. V = 2, -1/2, one role on both stages, K-block dets 6, 1.
- Minimality `k1_n0`/`k1_tight`: k = 1 with lambda != -1 forces n = 0, which is tight. So k = 2 is minimal. At k = 2, n = 0 splits into two empty
  stages and n = 2 is tight, so n = 1 is the only non-tight case.
- EVEN witness `decomp_false`: k = 3, n = 2, e = 2. V_t = lambda_t I with lambda = (2, 2, -1/4). It satisfies P = -1, all diagonal K-blocks
  invertible, n + 2 = 4 < 6, and has no split (every role meets every stage). EVERY off-diagonal K-block is also invertible.

## 2. Gauge-split lemma [P paper]: the right notion of "component"
- Statement. Suppose the stages split S1 | S2 with every cross block K_st = 0 (equivalently G_st = 0, since K_st = ±G_st off the diagonal).
  Then the frame is a direct sum up to a role-basis change, and e = e1 + e2 + 2.
- Proof.
  - G is block-diagonal, so Low(G) is too, H = H1 (+) H2, and P = 1 + X1 + X2 with X_i = A_i H_i B_i^T.
  - P = -1 gives X1 + X2 = -2. Also X1 X2 = A1 H1 G12 H2 B2^T = 0, and likewise X2 X1 = 0.
  - So E_i = -X_i/2 are complementary idempotents. E2 A1 = 0 and B1^T E2 = 0.
  - In a basis adapted to Im E1 (+) Im E2 (T A, T^-T B, which keeps G and K), A_i and B_i live on block i. Each part then satisfies
    P_i = -1, and rank K_i = |iota_i| - n_i (D_i^2 = -2 D_i, so rank K = |iota| - n exactly, for any frame).
- Hence frames decompose uniquely along the connected components of the K-block support graph. "Indecomposable" (gauge-invariant)
  = K-block-connected.
- The w2 witness and the word below have ALL K-blocks invertible. They are indecomposable in the strongest sense, not just in the
  role-support sense.
- Caveat. The gauge mixes roles, and cHat is computed on the word's fixed roles. The k-weighted-mean formula for cHat needs a
  literal role split.

## 3. Word level
### [C exact, dc1.log] a legal Q = 0 word (k = 3, n = 2)
- Construction.
  - 25 events: three J stages, each LAMBDA-wrapped HOST(0,1,a,b) + IDLE contacts on both registers, with (a,b) = (1,1), (1,-21), (1,2).
  - q-free ADD/SCALE conjugators sit between the stages. Final LAMBDA(+1) on both registers.
  - Target q * D0 D1 D2 on both rows (ex = 1, masks {0,1,2}).
- Checks.
  - replay == target at q = 1, -1, i, -i with symbolic D (polynomial arithmetic over Q(i)). This is equivalent to Legal by QZERO's CRT remark.
  - Frame: |Iota| = 6 = 2k (Q = 0), n + 2 = 4 (non-tight), rank G = 2, rank K = 4 = 2 + e, prod V = -I.
  - Diagonal K-block dets 8, -80, 12 (lambda != -1). Off-diagonal block dets -92, -8, 168/23 (all invertible). Both roles meet all stages.
- So the word is legal, Q = 0, odd targets, lambda != -1, D >= 2, NOT tight, and indecomposable. word_hp_B's hn fails, and DECOMP fails for it.
- Why it cannot be a direct sum of tight words. Tight parts have n_i = 2k_i - 2. Then sum n_i = 2 and sum k_i = 3 force two parts,
  (n,k) = (0,1) + (2,2). The (0,1) part is a stage with V = I. Here every V_t != I.

### [P paper] family for every k >= 3 (n = 2, e = 2k - 4)
- Recipe.
  - Stage j has V_j = P_j^-1 N_j P_j with N_j = H_j(1)^-1 H_j(-1), trace 2 + 4 a_j b_j. Free prefixes P_j come from the q-free conjugators,
    and LIFT (QZERO) handles the q^4 layer. IDLE contacts on both registers are scalar D_t I, so D-exactness is automatic.
  - Pick V_0..V_{k-2} freely and set V_{k-1} = -(V_{k-2}...V_0)^-1.
  - If tr V_{k-1} is not ±2, it is non-scalar. It is then Q-conjugate to N_{k-1} with a b = (tr - 2)/4, which is not 0 or -1. Non-scalar 2x2
    matrices with the same characteristic polynomial are conjugate over Q.
- So legal, indecomposable, non-tight Q = 0 words exist at every k >= 3. PARITY makes n even, so k = 3, n = 2 is the minimal word-level case.

## 4. What it means
- The k-weighted-mean argument only reduces the problem to INDECOMPOSABLE components. It does not reduce it to tight ones.
- A tightness-free SUP law "cHat <= sup_k HP(k)" needs a direct bound for indecomposable non-tight components. Q = 0 has even e = 2k - n - 2
  by PARITY, so the e = 2, 4, ... Q = 0 analogues of EXTRATHIN's DEFICIT / SET-RC2 / LEAF-CHANNEL rows are needed.
- In P^3 language, rank K_hh <= 4: each stage gives a pair (p_s, L_s) of 2-planes in K^4 with p_s ∩ L_s = 0.
  rank G_{s,T} = dim(p_s + sum L_t) - 2.
- The witnesses here have only 2 roles, so their cHat is presumably tiny (not computed). They kill the structure theorem, not the bound.
- EXTRATHIN's Q >= 1 e = 1 TRIANGLE shows type-level escapes can beat sup HQ. Whether an indecomposable e = 2 Q = 0 pattern beats sup HP
  = 143.273 is OPEN [CONJ either way].
- Next step: an e = 2 Q = 0 pattern LP (line-pair classes in P^3, with DEFICIT-e, SET-RC2, leaf rows) at k <= 24.
  - If it stays <= 143.273, a tightness-free SUP theorem is plausible via the gauge-split lemma plus per-pattern laws.
  - If it goes above, the caller bar must also carry e.
