# S1: E8 over extension rings and other line systems (stopped early because the budget ran out; no kappa claim)

Scripts are in $SP/s1/ and run with $SP/venv/bin/python -B from inside that directory. The package/ directory was not written.

## Reduction (argued)
- **Bit side.** The cost is rank_Q of the frame changes. A Q(i)-line costs 2 Q-ranks, so a K-linear unit is a rank-k unit with k = [K:Q] and h = k·w_K.
- **The ceiling under this scaling.** X depends only on (s, w = h/k, x/k) (§A.2, general k). The window does "halve" (8 -> 4), but v falls by the same factor: 120 real lines become 60 Q(i)-lines.
- **What decides the comparison.** It comes down to (w_K, x_K = Σ rank_K / v), with the F2 decoder pattern taken from K-orthogonality.
- **Q(i) is free on the bit side.** No ring rule (Lemma λ) blocks Q(i) there: the payload is F2 and the frames are Q-linear.

## Numbers (exact)
- **Gaussian E8** (J = i on coordinate pairs; preserves E8; checked)
  - 60 lines, w = 4.
  - Each line is non-orthogonal to 44 others.
  - α (largest pairwise non-orthogonal set) = 12.
  - F2 minrank (asymmetric allowed, SAT with clique gauge) = 15: c = 13 and 14 are UNSAT, c = 15 is SAT. 15 = v/w, the frame-partition decoder.
  - Hyperplane flats: 60 of size 15, 480 of size 6, 960 of size 4.
- **Eisenstein E8** (fixed-point-free order-3 element from 4 orthogonal A2's; Witting configuration)
  - 40 lines, w = 4, non-orthogonal degree 27, α = 7.
  - F2 minrank = 10: c = 7, 8, 9 are UNSAT, c = 10 is SAT. 10 = v/w.
- **Hurwitz E8** (left multiplication by i, j)
  - 10 lines in H^2, w = 2, each line orthogonal to exactly one other, α = 5, minrank 5 = v/w.
- **Copy cost.** Symmetric decoders, exact CP-SAT with cost = dim span A_j, searched 900 s (not proven optimal):
  - Gaussian (c ≤ 20): best found 60, so x_K = 1.0. Proven lower bound only 9 (x_K ≥ 0.15).
  - Eisenstein (c ≤ 16): best found 40, so x_K = 1.0. Lower bound 9 (x_K ≥ 0.225).
  - Hurwitz:
    - Symmetric optimum is 10 (x_K = 1.0, proven OPTIMAL).
    - The asymmetric D_j-relaxation gives only 2, and that relaxation is too weak.
    - The exact SAT run with the Theorem-C cost (costs 8/9/10) did not finish, so the Hurwitz asymmetric case is **open**.
- **Under the README's own E8 premise** (cst = minrank × full in-cap clique rank, the same premise as E8's 72): Gaussian, Eisenstein and Hurwitz all have x_K = minrank·w/v = **1.0**. Then D/k = (s−1)v − s·v < 0 at every s, so there is **no saving at all**.
- **Threshold to beat bit E8** (X* = 6.0005e-3, float screen fx.py): x_K < ~0.71 at w = 4, < ~0.86 at w = 2, < ~0.64 at w = 6.
- **Structural finding.** The cross-field gain of E8 (minrank 9 < v/w = 15) disappears over Q(i), Q(ω) and H: in every extension view minrank = v/w exactly.
- **G34 / Coxeter–Todd K12.** Built exactly as {x ∈ Z[ω]^6 : x_i ≡ x_j mod θ, Σ x_i ≡ 0 mod 3}: 756 minimal vectors, 126 lines.
  - w = 6, non-orthogonal degree 80, α = 15.
  - Even at minrank = α, x_K ≥ 90/126 = 0.714 > 0.64, so it loses under the premise. The minrank itself was not run.
- **Complex side** (argued). Rules out F4/Eisenstein F2-labels and Gaussian F2-labels:
  - **F4 / Eisenstein labels.** A Hermitian form over F4 has an alternating F2 trace form (Tr h(x,x) = 0), so there are no odd-norm residuals. This breaks the phase calculus (orthonormal kernel basis; Lemma λ consequence). It is the first broken rule.
  - **Gaussian labels.** Z[i]/(1+i) = F2, so there is no extension.
  - **A Q(i)-valued decoder** (Hermitian Gram, 4 centres) forces F2 window = the Gaussian-pattern minrank = 15 on 60 ports, or ≥ 24 on the 120 real ports (clique of r, ir pairs). Not evaluated further.
- **Side finding (b), checked with the float screen only.** The upstream Alon triple family (v = C(h,3), cst = h² bit / h(h+1) complex) has a higher **ceiling** than E8:
  - X* = 7.39e-3 (bit, h = 24) and 7.16e-3 (complex, h = 24), at s = 3.
  - Generalised Alon sets (7-subsets, λ = 3) would push the ceiling higher still.
  - So X* alone does not rank unit families; helper cost decides (per-target neighbour count z = 3·C(h−3,2) = 630 at h = 24, against 63 for E8).
  - This was the pre-E8 family (h = 23/25/28 audits in docs/research).
  - Task (c), the helper-floor estimate, was not done.

## Reproduce
- explore4.py: v, degree, α for the three views.
- minrank_any.py {Gauss|Eisen|Hurwitz|K12} [cmin]: minrank SAT.
- costexact.py {Gauss|Eisen} cmax 1 secs: exact cost CP-SAT (needs flats_*.pkl, built by costlb.py).
- k12.py: G34.
- fx.py: float X screen (certify with skel.X before publishing).

## Open and next steps
1. A real lower bound Σ_j dim span A_j ≥ 0.71·v (Gaussian) for decoders with more than minrank totals. CP-SAT bounds stay at 9; a structural argument is needed. Same open status as E8's 72.
2. Finish the Hurwitz asymmetric SAT (hurwitz_exact.py, cost ≤ 8/9/10).
3. Certify the triple-family X* with skel.X, and estimate helpers via d1 cover numbers. The triple cover number is 2 by the argued two-hyperplane cover.
