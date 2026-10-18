# Sprint Claim — Seed 30 (Track 20–39: Complex Supplier)

- **Track & Seed:** `20–39: Complex supplier: improve one specific circuit, frame schedule, decoder, or paid recursive profile` (OS random seed: **`30`**)
- **Base Commit:** `abdc6a7002abdbcd9e21bfc5e1a795784deacfdf`
- **Submitted PR:** [`CrocSwap/integer-mult-bounds#1119`](https://github.com/CrocSwap/integer-mult-bounds/pull/1119)
- **Selected Frontier Certificate:** `certificates/selected-result.json` (conditional $\kappa = 1661960547713947 / 10^{18} = 0.001661960547713947$, PR #942 on PR #869/#870 and PR #890 / PR #858)
- **Coordination Note:** No pinned sprint coordination issue exists on `CrocSwap/integer-mult-bounds` (open issues are `#913` and `#650`). This claim is recorded locally in `CLAIM.json` and `CLAIM.md` and checked against all open PRs through `#1118` for non-overlap.

## Three Narrow Candidate Tasks Evaluated

1. **Candidate 1 (Partial $E_4 \to E_5$ entrance-promotion reversion inside one 4-helper group `[659, 661, 662, 663]` of U8 to fill T37 rank-1 idle gaps):**
   - **Hypothesis:** In PR #869 (`PROOF-NOTE-PROMO.md`), two 4-helper groups (`659, 661, 662, 663` and `666, 669, 672, 673`) had their entrance frames promoted from $E_4 = [298, 170, 102, 30]$ (dim 4) to $E_5 = [298, 170, 102, 30, 1]$ (dim 5), changing the local paid profile by $\Delta = \{2:-4, 3:-2, 4:+2\}$ per group. Since T37 (`research/complex-t37-owners`) has 2 remaining rank-1 idle slots (examined via $J$-pair unpromotion in PR #1072), we tested reverting $m \in \{1, 2, 3\}$ helpers of `[659, 661, 662, 663]` back to $E_4$.
   - **Outcome (Scoped Negative Finding):** In U8 (`native/barch/FULL-WORD.json.gz`), the 12 bipartite delivery gates `B[420..431]` (`dst in {656, 657, 658, 660}`, `src in {659, 661, 662, 663}`) find the destination helpers `656, 657, 658, 660` at frame dimension $1$. When $1 \le m \le 3$ helpers in `{659, 661, 662, 663}` are reverted to $E_4$ (dim 4) and $4-m$ remain at $E_5$ (dim 5), each of `656, 657, 658, 660` must first climb $1 \to 4$ (rank 3) for the $E_4$ sources and then climb $4 \to 5$ (rank 1) for the $E_5$ sources, splitting 4 rank-4 climbs into 4 rank-3 climbs plus 4 rank-1 climbs. This produces local profile deltas $\Delta_{\text{local}}(m=1) = \{1:+2, 2:+1, 3:+3, 4:-3\}$ and $\Delta_{\text{local}}(m=2) = \{1:+2, 2:+2, 3:+4, 4:-4\}$, strictly worsening the complex moment at $b_{\text{front}}$. Recorded and verified in `PROOF.md` and `verify.py`.

2. **Candidate 2 (Frame-0 `premix` refactorization at the head of section `A` in U8):**
   - **Outcome:** Ruled out during the Step 4 favorable-budget check because the frame-0 `premix` prefix of `A` in U8 contains only 57 scalar macros (482 real primitives per orientation) with small coefficients ($\max |\text{num}| = 2$, $\max \text{den} = 2$).

3. **Candidate 3 (Selected — Two-sided Markowitz $R^{-1} P L^{-1}$ Schur-complement refactorization with Weyl-group signed cycles for `full_frame_cleanup` on the selected U8 complex supplier word):**
   - **Object:** `cleanup` (`full_frame_cleanup` at frame `1` = `FULL`) in the selected U8 complex supplier word (`native/barch/FULL-WORD.json.gz` content sha256 `090fd574...`, `native/local/CANONICAL-WORD.json.gz` content sha256 `48b532f1...`).
   - **Mechanism & Result:** Replaces the 6,105-macro one-sided dyadic Gauss-Jordan elimination (`high_inverse = "dyadic_sparse_Gauss_Jordan"`, which suffers severe fill-in and coefficient explosion up to `131,646`) with a 3,525-macro two-sided Markowitz $R^{-1} P L^{-1}$ Schur-complement factorization with Weyl-group signed cycles (`seed = 30`, `trial = 16`, `swap_pen = 6`, `scale_pen = 0`):
     - Cuts `full_frame_cleanup` scalar macros from **6,105 to 3,525** (**$-2,580$ macros per orientation, $-42.26\%$**).
     - Cuts `full_frame_cleanup` real-component primitives from **68,714 to 31,394** per orientation (**$-37,320$ real primitives per orientation, $-54.31\%$**).
     - Cuts full U8 local program real-component primitives from **193,306 to 155,986** (forward) and **193,354 to 156,034** (backward), saving **74,640 real primitives per forward+backward invocation pair** (**$-19.30\%$** of the entire U8 local program).
     - Cuts maximum `cleanup` numerator magnitude from **131,646 to 8** ($16,455.75\times$ reduction) and maximum denominator from **64 to 8**.
     - Cuts the backward orientation's peak prefix $L_1$ coefficient norm (`prefix_l1_upper`) from `48299247708521178587951/16` (`72` bits) to **`57316408753392281/4`** (**`54` bits**, **$-18$ bits**, a **$210,704\times$ reduction**), and the forward peak prefix $L_1$ norm from `6812058044968180837/256` (`55` bits) to **`1938756620440273`** (**`51` bits**, **$-4$ bits**, a **$13.7\times$ reduction**).
     - Preserves all 728 exact columns in both orientations, all 1,005 native frames, all 2,949 directed frame edges, the paid recursive child profile `{1: 2548, 2: 338, 3: 446, 4: 162, 5: 72, 8: 8}`, and byte-identical `RESIDUAL-ADAPTERS.json` (`8b06181f...`). Does not claim a new $\kappa$.
