# Rounded division for a native word: a defect theorem (second version)

Tags. **[P]** proved or computed here. **[Q]** read in the named source. **[judgement]** judgement. Sections 1 to 7 are written to go into a package note as they stand. Readers so far: the author, one second reading, one numerical run. All are AI sessions of ours. No maintainer has seen this.

**Result.** Rounded division fits. With no checks and no odd root scale, the word's output differs from its exact action by at most an explicit defect, on any child that meets a norm contract, including nonlinear children. Through the whole recursion the defect stays inside the guard budget of #6901: `F = p+D`, `W = p+h+2D+3` for `D >= 19`, 5 more bits below that. Temporaries are `W+18`. Exactness becomes approximation, so the outer Proposition needs one extra scan and new constants (section 6). Everything from the Lemma of `06-transforms.tex` onward then fits with no change to `p` or any parameter. `kappa`, `T`, `P`, `S` do not move. Rounded mode does need the caller rewrite of #6912 if the conservative raw reading is kept (section 7).

**Conditional on:** the compiler structure statements S1 to S5, quoted from #6901, FINITE-PRECOMPILATION and p7-TENSOR and not re-derived; the all-`f` native equalities on the per-port word, as for the exact theorem.

## 1. Definitions

**Format.** `u = 2^-F`. A stored component is `u` times a signed integer. Format `(F,J)` means every stored component has absolute value below `2^J`.

**Rounded division.** For an integer numerator `m` and a scalar `a/b` in lowest terms with `b > 0`,

    RDiv_{a/b}(m) = floor( (a*m + floor(b/2)) / b ),

applied separately to real and imaginary components. For a C pair it is applied to the complete four-term numerators, never to separate summands. Integer `q` needs no division and stays exact.

**Two fibre norms.** Let `D = q + R` be the selected axes of #6901: `q` individually preprocessed, `R` kept as the one reference factor of all later pieces. For a field `y`, an `X`-fibre (`X` = `D` or `R`) is the set of `2^X` coordinates with every label other than those `X` selected bits fixed (external row, spectators, polynomial index). Then

    ||y||_X = max over X-fibres of ( sum over the fibre of |y_i|^2 )^(1/2).

An `R`-fibre lies inside a `D`-fibre, so `||y||_R <= ||y||_D`. The site unit is `eta_X = 2^((X-1)/2) * u`, and `eta_R <= eta_D`. When `q = 0` the two coincide. Unmarked `||.||` below means `||.||_R`, the recursion's norm.

**Word.** Registers carry a field and a chart. Events are:
- MOVE `a -> b` on register `s`: exact operator `D_b D_a^-1`, realized by a child;
- ADD or COPY `t += q s`, with `s` and `t` in a common chart (COPY is an ADD into an owned zero);
- SCALE `t *= q`;
- INIT and CLEAR, which set an owned register to exact zero.

`R_{r,k}` is the exact row matrix: the ideal output of public row `r` is `T_r x = sum_k R_{r,k} D_{final(r)} D_{init(k)}^-1 x_k`.

**Suffix coefficients.** `rho^(j)_{r,s}` is the coefficient of register `s`, taken just after event `j`, in final public row `r`, computed by running the scalar word backward from the identity on public rows and zero on owned rows. A CLEAR or INIT zeroes that register's column.

**Sites.** A site is a MOVE, or an ADD, COPY or SCALE with non-integer `q`. Its register `s_j` is the one it changes. Gains:

    Gamma_W = max_r sum_{sites j} |rho^(j)_{r,s_j}|
    M_W     = largest l1 mass of a stored row or pre-ADD product, over all prefixes
    Sigma_W = largest, over all cuts c and registers x, of sum_{sites j<=c} |segment coefficient of site j in x at c|

**Child contract `C(eps,B)`.** For every input in format with `||x|| <= B`, the child returns `y` in format with `||y - T x|| <= eps`. No linearity is assumed. Inputs need not be reachable or lie on any coarser grid.

## 2. Statements

**Lemma 1 (RDiv) [P].**
- (a) `RDiv` is total: it has no check and no reject.
- (b) `|RDiv_{a/b}(m) - a*m/b| <= 1/2`, and ties go up. So it is the host rule `Q_F(q x)` with upward ties of #6900 and #6891. It is not odd: `RDiv(-m) != -RDiv(m)` at a tie.
- (c) If `b` divides `a*m`, it is the exact quotient.
- (d) Write `b = 2^x * o`, `o` odd. Then `RDiv` is: a least-significant-first pass for `n = a*m + floor(b/2)`; if `o > 1`, one most-significant-first two's-complement long division by `o`, remainder in `[0,o)`, starting at `o-1` for a negative value and `0` otherwise; then `x` low bits dropped. If `o = 1` it is one least-significant-first pass with a carry, and needs no second pass. This holds also for non-constant `b = 2^k`, with the offset placed by a work-tape copy.
- (e) It uses no random bits.
- (f) Its complex residual on one fibre has norm at most `eta_X` for that fibre size.

**Theorem A (one word) [P].** Suppose every frame is unitary on every `R`-fibre and every ADD has a common chart. Run the word on any input, with any realized site residuals `n_j` (a child's residual against the exact operator applied to its actual input, or a division's rounding residual). Then for every public row `r`,

    ||yhat_r - T_r x|| <= sum_{sites j} |rho^(j)_{r,s_j}| * ||n_j|| <= Gamma_W * max_j ||n_j||.

Also, at every cut and register `c`, the stored field satisfies `||z_c|| <= M_W * max_k||x_k|| + Sigma_W * max_j||n_j||`.

**Theorem B (defect tree) [P].** Let a computation be a finite tree whose nodes carry a gain `Gamma_v >= 1` and a mass bound `M_v >= 1` with these two properties. The node's output defect is at most `Gamma_v * max(child defects, eta)`. Every stored field is at most `M_v * B + Sigma_v * E` on input norm `B`. Put `E = eta * max_path prod Gamma_v` and suppose `E * max_v Sigma_v <= 1 <= B_root`. Then, with no circularity:
- every child input has norm at most `B_root * prod_{path}(M_v+1)`;
- the root defect is at most `E`.

**Theorem C (recursion) [P, given S1 to S5].** Under the structure statements below, let `t = K_star * ell`, `ell = floor(log_N D)`, `N = 2^H`, and

    X(D) = 2*log2(D+3) + ell * K_star * (log2 G + 1),   G = the per-context gain of section 5,
    L(D) = 1 + ell * K_star * (log2 (M_ctx+1) + 1).

Replace every division by `RDiv`. Then the root output has `||out - T x||_R <= 2^(X(D) + (D-1)/2 - F)`, and no component exceeds `2^(h + (D+1)/2 + L(D))`.

**Corollary (the #6901 budget) [P, given S1 to S5 and the constants of section 5].** If `c * K_star < 2^H` with `c = 1100`, then for all `D >= 1` and `p, h >= 0`:

    F = p + D + g,  J = h + D + 2,  W = F + J + 1 = p + h + 2D + 3 + g,  temporaries W + 18,

with `g = 0` for `D >= 19` and `g = 5` below, suffices: execution never overflows, never rejects, and every output coefficient has complex modulus error at most `2^(-p-1)`.

**Proposition (relation to the exact theorem) [P].** If children are exact, the word carries the odd root scale with a valid certificate, and the grid is fine enough, every `n_j = 0` by Lemma 1(c). Theorem A then reads as equality. So one circuit serves both modes only with the root-scale step added and that finer grid. Without them the rounded circuit is a different execution and no longer detects a truncated child.

Structure statements, all **[Q]**, none re-derived here:
- **S1.** A path has at most `K_star = v*m*(H+1)^2` unfinished raw contexts per ordinary node and at most `ell` unfinished ordinary nodes (#6901 eq (4a), and its lines 191-193). Those contexts sit in at most `m*(H+1)^2` flow classes, each with at most `v` contexts.
- **S2.** A path has at most `m*(H+1)` nonbase compiler frames per ordinary node (#6901 lines 176-178). A frame is a complement followed by a flow on the same array (FINITE-PRECOMPILATION sec 4), so it has 2 sequential jobs.
- **S3.** A product runs each paid position of U as a complete run of V on the owners (p7-TENSOR sec 1). After the product, each role of rank `K < L = b^v` receives a completion on `L-K` disjoint axes (sec 2). Then every paid rank `R > J = c^v`, and every completion likewise, is replaced by consecutive jobs on disjoint axes of ranks `J,...,J,r`, kept inside the original whole-job normalizers (sec 3). Route adapters are monomial maps with unit quadratic phases and role permutations (FINITE-PRECOMPILATION sec 1 item 3), so they are exact on the grid and norm-preserving. Normalizers are a separate binding (FINITE sec 7; #6901 line 62, "monomial/positive-job"): see the weaker reading in section 9.
- **S3a.** Below the compiler's base range a rank `e` uses the ordinary sequential program, `P_e = e` (FINITE sec 4). It has no raw context (#6901 line 151), but it is `e` sequential leaves.
- **S4.** Every operator composes to a Gaussian-dyadic Clifford on the same root factor, per external row, with origins moving only among complete fibres (#6901 sec 4, eq (5)).
- **S5.** An ordinary node `e = N f + r` is a rank-`N` program at column `f` plus `r < N` direct stages. The root wrapper adds at most `D+3` sequential kernels, pieces and normalization steps, all of gain at most 1 (#6901 lines 330-378). The `q` kernels run first and their selected bits are disjoint from all later ones (`05-layers.tex` lines 620-627). The base is at most `f` direct C stages. CLEAR and INIT give exact zero, the inherited premise.

## 3. Proofs

**Lemma 1.** Write `a m = b Q + rho'` with `0 <= rho' < b`. Then `floor((a m + floor(b/2))/b) = Q + [rho' + floor(b/2) >= b]`. For odd `b` this rounds up exactly when `rho' > b/2`, and no tie exists. For even `b` it rounds up exactly when `rho' >= b/2`. That gives (b) and (c). For (d), multiplication by a constant plus a constant is a carry automaton. Nested floors give `floor(n/b) = floor(floor(n/o)/2^x)`, long division by `o` needs only the remainder as state, and a two's-complement prefix of all ones is the value `-1`, whose floor quotient is `-1` with remainder `o-1`. For (f), each component errs by at most `u/2`, so a complex coordinate errs by at most `u/sqrt2`, and a fibre has `2^X` coordinates: `2^(X/2) * u/sqrt2 = eta_X`. (e) is plain. An exhaustive small-width run of the automaton agrees (section 8).

**Theorem A.** Let `A_j` be the exact linear map of event `j` on the whole register state, and let `z_j` be the actual state. By definition of the residual,

    z_j = A_j z_(j-1) + n_j,     so     z_M = A_M...A_1 z_0 + sum_j A_M...A_(j+1) n_j.     (1)

This is an identity about realized values. It holds for nonlinear children and rounders, because each residual is measured on the actual input of its site. No two rounded trajectories are compared, so no Lipschitz claim is used. This is the recurrence of #6891 PROOF sec 3.

By the common-frame identity of `03-motifs.tex` (lines 168-177), the suffix `A_M...A_(j+1)` started from an arbitrary state in the charts at cut `j` equals `D_out * S_suffix * D_cut^-1`, where `S_suffix` is the scalar suffix and acts pointwise. Its `(r,s)` block is therefore

    rho^(j)_{r,s} * D_final(r) * D_{v_j(s)}^-1.

Both frames are unitary on root fibres (S4), and the operator preserves the fibre decomposition. So the operator norm of that block in the fibre norm is exactly `|rho^(j)_{r,s}|`. Rounding residuals live in stored coordinates, and the transport is a unitary between stored coordinates, so no other basis enters. Taking norms in (1), with `n_j` supported on `s_j`, gives the first display. The same identity between two cuts, with the scalar segment in place of the suffix, gives the stored bound. INIT and CLEAR write exact zero, so a residual dies there, and that matches the zero column. COPY keeps the target's column, so an inherited residual in the target is not erased. Here that column is zero only because the INIT before it wrote exact zero.

The theorem needs the `R`-fibre: a `D`-fibre spans several role fields after the split `u = bg + w`, and the register-wise suffix does not apply to it.

**Theorem B.** Induct along execution order, not along the tree. Suppose every child called so far met its contract. Then every stored field so far obeys the mass bound with defect term at most `Sigma_v * E <= 1 <= B`, so it is at most `(M_v+1) B`. The next child's input is therefore admitted at `(M_v+1) B`, and its contract can be used. The defect bound follows by bottom-up induction: `eps_v <= Gamma_v max(eps_c, eta)`, and a leaf has `eps = eta`, since a rounding site is `eta` by Lemma 1(f). This is the admission argument of #6891 eq (5).

**Theorem C.** Exact debt resets at a completed job. Defects do not. So sequential multiplicity must be counted as gain, separately from nesting. Assign nodes along a path as follows.
1. *Raw context.* One raw unit is a caller node over a word node. By Theorem A applied to each, with the `J` sites of the caller fed by the word, its gain is at most `g_J * Gamma_W + g_S + g_I` (section 5).
2. *Flow class.* A `v`-fold product has `v` contexts, and by S3 its paid position is the run of the next factor, so gains multiply factor by factor. A path through the class also passes one split paid position, at most `R/J + 1` consecutive disjoint-axis jobs, each followed by a unitary suffix. The completion runs after the entire product, at most `L/J + 1` pieces with gain 1 each. So the class gain is at most `(g_ctx)^v (R/J+1) + (L/J+1)`. The split charge belongs to the class, not the context. Stored fields inside a split are unitary images plus accumulated defect, so `M` does not grow, and `Sigma` of this node is at most `R/J + 1` plus the context value.
3. *Compiler frame.* An array receives a complement job, then a source slot. By S3 the adapters contribute no residual. The suffix after each is a unitary job on that array, so `eps_frame <= eps_complement + eps_flow`, gain 2, `M+1 = 2`.
4. *Class unit.* A unit's paid round is the matching target output of the child class, or a completed exit batch. In both cases the contract applies to the field's actual value. Disjoint simultaneous copies add nothing, since the norm is a supremum over fields, and replication factors do not enter. A correlated owned center is one field with an actual value, and the contract covers it.
5. *Small-rank base.* By S3a, gain `e` and `Sigma <= e`, one per ordinary node on a path. With `e < m` this is `log2 m` bits. If the base range reached any rank below `N` it would be at most `H` bits, and the count below still holds.
6. *Ordinary node.* The remainder is at most `r < N` sequential sites of gain 1, so `H` bits, and `Sigma <= N`.
7. *Wrapper.* First the `q` preprocessed kernels, in `||.||_D` with unit `eta_D`: each is unitary on `D`-fibres, on the unsplit field. Then convert once by `||.||_R <= ||.||_D`. The order matters and is the safe direction, because the kernels come first (S5). All later pieces use Theorem A and B in `||.||_R`, with `eta_R <= eta_D`. Normalization shifts and phases contract. Padded rows end within `E` of zero and are then deleted, and nothing reads them after that. So the `F`, `J` and `E` budgets hold with `d = D`.

By S1, S2 and items 2, 5, 6, the bits on one path per ordinary node are at most

    K_star * log2 g_ctx + (K_star/v) * log2((R/J+1)(L/J+2)) + m(H+1) + H + log2 m.

Define `log2 G` as `log2 g_ctx + log2((R/J+1)(L/J+2))/v`. The last three terms are at most `K_star`. This gives `K_star (log2 G + 1)` per node. The base contributes at most `log2 D` and the wrapper at most `log2(D+3)`, which gives `X(D)`. Mass is the same count with `M_v`: frames, base, split and remainder nodes have `M+1 = 2`, one bit each, and the total is inside `L(D)`. Apply Theorem B. The hypothesis `E * Sigma <= 1` is checked in the corollary.

**Corollary.** Take `log2 G <= 129`, `log2(M_ctx+1) <= 151` and `log2 max_v Sigma_v <= H` (section 5).

*Case `ell >= 1`, so `D >= N`.* Since `k <= 2^(k-1) <= N^(k-1)`, `ell <= D/N` (#6901 lines 302-304). With `c = 1100`:
- `ell * K_star * 130 <= 130 D/1100 < D/8`, so `X(D) + H <= (D-1)/2`, since `2 log2(D+3) + H` is negligible at `D >= N = 2^H`. This gives `E <= 2^(-p-1-H)`, so `E * Sigma <= 1`.
- `ell * K_star * 152 + 1 <= 152 D/1100 + 1 <= floor(D/2)`, so `h + (D+1)/2 + L(D) < h + D + 2 = J`.

*Case `ell = 0`.* There are no contexts, no splits and no ordinary node above the base. `X(D) = 2 log2(D+3)`, and `X(D) <= (D-1)/2 + g` with the stated `g`: the largest deficit is 4.17 bits at `D = 3`, and `g = 0` works from `D = 19` on. The stored field is at most `B + (D+3) E <= 2B`, because `(D+3)/2 <= 2^((D+1)/2) <= B_root`.

In both cases `E <= 2^((D-1)/2 + X(D) - p - D - g) <= 2^(-p-1)`. Coordinate modulus is at most fibre norm, so the error bound holds as a complex modulus, not only per component.

*Temporaries.* `|a| <= 40,864 < 2^16` on the word and at most 256 in the caller, with a carry and a sign. The offset `floor(b/2)` is at most 20,480 for `b <= 40,960`, which is below `2^(W+15)`, since `W >= 5`. So `W+18` suffices. The wrapper's normalization shift and the outer shrink of section 6 have non-constant `b = 2^k`, and they are bit drops with a carry and need no multiplier width. ∎

## 4. Why the fibre norm, not coordinate sup norms [P]

The selected review (`pr6030-audit/PROOF-REVIEW.md:151-161`) uses sup-norm majorants. A rank-`r` Gaussian has row-norm bound at most `2^(rf)`, and every prefix, suffix and subinterval is controlled. The envelope is `2^(10^9 + 240152 f)`. That is a valid finite-precision proof, and it carries over with the alphabet line changed. But it charges paid rank mass `f` times: `240152 f` is about `1656 d` at `d = 145 f`. It cannot fit `F = p + d`.

In the fibre norm, frames have norm exactly 1, so `f` leaves the gain entirely. The only `d` term is the one conversion from a component to a fibre, `eta`, paid once at the site. That is what lets the budget survive. Only the triangle inequality and unitarity are used: no independence or correlation assumption, and residuals may be adversarial.

Clause map to that review text:

| review line | here |
|---|---|
| dyadic coefficients and SCALE units | alphabet `A = Z[1/2,1/3,1/5]`, `\|q\|+1 < 2^16` kept |
| elementary majorants at least one | suffix coefficients from the word; sup majorants remain a valid weaker fallback |
| monomial routes norm one | unchanged |
| rank-`r` Gaussian row norm | replaced by fibre norm 1 |
| COPY propagates residual as ADD | unchanged, in Theorem A |
| INIT/CLEAR inherited premise | unchanged |
| summing defect propagation | Theorem A, with `Gamma_W` from the word |

## 5. Constants on the actual word [P]

Word: 67,079 events. Computed from the word and caller as data. Floats for all rows, with the worst row of each word rechecked in exact fractions. `Gamma_W` was recomputed by a second reader's own loop and a third run's own backward pass: `2^22.685`, worst row 1436 in all three.

| quantity | word (#6932) | earlier stage word | dyadic parent |
|---|---|---|---|
| MOVE sites | 6,335 | 6,355 | 6,374 |
| non-integer sites | 22,730 | 22,723 | 19,007 |
| of which odd | 3,001 | 2,941 | 0 |
| `log2 Gamma_M` (MOVE sites) | 18.665 | 18.659 | 20.146 |
| `log2 Gamma_R` (rounding sites) | 22.678 | 22.705 | 22.498 |
| `log2 Gamma_odd` (odd sites only) | 16.785 | 16.721 | none |
| `log2 Gamma_W` (all sites) | **22.685** | 22.711 | 22.756 |
| `log2` root-sum-square, MOVE sites | 13.670 | 13.665 | 15.242 |
| `log2` root-sum-square, rounding sites | 20.612 | 20.613 | 18.415 |
| `log2` largest suffix row mass | 21.709 | 21.709 | 20.296 |

Row 1436 is a helper. Mains reach only `2^12.95`, so `g_J Gamma_W` overstates the mains by about 10 bits. That is not an error, and it is not used.

Other word constants: `log2 Sigma_W = 34.16`. `log2` of stored prefix mass is 29.172. Including pre-ADD products, `log2 M_W = 29.67` (**[Q]** package: 37.48 minus `log2 225 = 7.81`).

The clause does not worsen this: the word's all-site gain is below the dyadic parent's. The odd sites alone are 1.7% of the worst gain, about 0.02 bits.

Caller. No-cancellation majorants, rigorous by submultiplicativity with operator norm 1 for each `LAMBDA`, `IDLE_ONE`, `QUERY` phase and `D`, and real numbers likely well below these [judgement]. Only logarithms enter. Caller helpers are not among the 6 roles in `g_J`. They do not mix with mains, so their defect is at most `18 Gamma_W eps`, far below `G eps`.

| quantity | log2 |
|---|---|
| prefix mass, including the SWAP transient | 120.341 |
| `g_J`, gain at the 18 contacts | 101.927 |
| `g_S`, rounding at non-integer caller scalars | 110.908 |
| `g_I`, `LAMBDA`, idle and query sites | 109.934 |
| `Sigma_C` | 116.337 |

Per class and per context. `J = c^v = 11^1920`, `L = b^v = 12^1920`, `R <= 153^1920` (majorant by the carrier).

| quantity | bits |
|---|---|
| `log2 g_ctx = log2(g_J Gamma_W + g_S + g_I)` | at most 124.62 per context |
| split `log2(R/J + 1)` | at most 7,293 per class |
| completion `log2(L/J + 2)` | at most 242 per class |
| per class, `v = 1920` | at most 246,805 |
| per context equivalent | 128.55, so **`log2 G <= 129`** |
| `(log2 G + 1)/c` at `c = 1100` | 0.1182, below 1/8, so **`c = 1100` stands** |
| `log2 (M_C+1)(M_W+1)` | at most 151; unchanged, since jobs inside a split are unitary |

`Sigma` by node type:

| node | `log2 Sigma` |
|---|---|
| word, caller | 34.16, 116.34 |
| split class | about 7,300 |
| small-rank sequential base | at most 13,935 |
| ordinary node remainder, `r < N` | at most `H` |

So `log2 max_v Sigma_v <= H`. All are harmless at `D >= N`, the only place they occur.

Against the exact mode, the rounded mode drops the root scale `S^K`, its root conversion, the `7.8 t` width, and the dependence on a dyadic endpoint.

## 6. The outer layer in rounded mode [P]

Theorem C gives `y` with `|y - Hz| <= E <= 2^(-p-1)` per coordinate. That breaks the outer Proposition as written (`05-layers.tex` from line 827; disk line 875 onward). Counterexample shape: `Hz = (a-t, b-t)` in the disk, `(a,b)` on the `p`-grid just outside, positive residual above `t`. `Q_p` then returns `(a,b)`, outside the disk, and the error `< sqrt2 2^-p` also fails. The recursive child has no disk contract, so only this outer call is affected (`05-layers.tex` lines 488-494, 690-692, 909-910).

**Proposition R.** Under the hypotheses of that Proposition, including its bands, with `p >= 3` and `F = p + D + g` as in the corollary, let `y` be the rounded layer output on the `F`-grid and return

    y' = y - RDiv_{2^p}(y),     then     Q_p(y').

Then every returned coefficient lies in the complex unit disk, and

    || Q_p(y') - H z ||_inf < 3 * 2^-p.

The time bound `O(V d^{lambda'})` and the widths are unchanged: one extra `O(V)` scan and no format change.

*Proof.* Every row of `H` has absolute row sum one, so `|Hz| <= 1` and `|y| <= 1 + 2^(-p-1)`. By Lemma 1(f), `y' = (1 - 2^-p) y + e` with `|e| <= u/sqrt2`. So

    |y'| <= (1 - 2^-p)(1 + 2^(-p-1)) + u/sqrt2 = 1 - 2^(-p-1) - 2^(-2p-1) + u/sqrt2 < 1,

since `u/sqrt2 < 2^(-p-1)` for `D + g >= 1`. `Q_p` truncates toward zero, so it does not increase modulus, and the disk holds exactly. For the error, in moduli,

    |Q_p(y') - y'| < sqrt2 * 2^-p
    |y' - y|       <= 2^-p (1 + 2^(-p-1)) + u/sqrt2
    |y - Hz|       <= 2^(-p-1)

and the sum is `2^-p (sqrt2 + 3/2 + 2^(-p-1) + 2^(-D-g)/sqrt2)`. The constant is 2.9142 in the limit, at most 2.988 at `p = 3`, `D + g = 6`, the worst allowed case, and above 3 at `p = 2`. The `p`-band is `p` large, so `p >= 3` costs nothing. ∎

**Lemma (`06-transforms.tex` line 222).** Error `sqrt2 l 2^-p` becomes **`3 l 2^-p`**. The disk output, the cost (eq `synthetic-transform-cost`) and the layout are unchanged.

*Proof text (lines 405-420).* The identity `J_E Q_p = Q_p J_E` still holds, but "truncating once after the exact contraction round" no longer does, and `RDiv` is not odd, so `J_E` does not commute through `y'` at ties. Use instead the per-round recursion. A round maps `z_i` to `J_E Q_p(y'(z_i))`, and the exact round is a contraction, so `err_(i+1) <= err_i + 3 * 2^-p`. Prefix-slot rounds (lines 356-371) are direct, stay exact before `Q_p`, and add less than `sqrt2 2^-p`, so they are inside the same recursion. The opposite direction has the same form.

**Convolution (`06-transforms.tex` lines 636-715).** With `delta = 3 l 2^-p` and `eta = sqrt2 2^-p` unchanged (the ring product is direct), the bound `sqrt2 M(3l+1) 2^-p` becomes **`M(9l + sqrt2) 2^-p`**. The proof is otherwise word for word: `2 delta + eta`, then `3 delta + eta`, then the factor `M`. The disk clause reads eq `synthetic-convolution-error`, so it adapts by itself.

**Later margins: read, and no change to `p` [P on `08-assembly.tex`].** The layer Proposition is cited only in sections 05, 06, 08. The Lemma and the convolution are cited only in 06 and 08. Section 08 line 564 reads: `sqrt2 l 2^-p < L 2^-p`, `L = log2 T`, for all sufficiently large `n`. Every later figure uses only the right side:

| figure (08-assembly) | depends on |
|---|---|
| transform errors and product truncation below `3L + 2` | `< L` per transform |
| `E_ring = M(3L+2) < 5TL` | above |
| `\|\|h'\|\| < .701`, `6TL`, `8TL` | above |
| `E_s = 9 * 2^gamma * TL`, `.51`, `.501` | above |
| cutoff `b >= 2^24` with all of these below `10^-3` | above |

The replacement is `3 l 2^-p < L 2^-p`. Here `r = 2^ceil(L/d)` and `l = log2 r` (lines 71-72), so `L > d(l-1)`. For `d >= 6`, `l >= 3` this gives `3l <= d(l-1) < L`, and the bands make `d`, `l` tend to infinity (lines 83-91). So the same "sufficiently large `n`" covers it, and **`E_ring` and every later constant stand unchanged.** No extra bit of `p` is spent. Had the constants been carried through instead, the cost would be about 1.09 bits, so the point is minor either way. `kappa` reads none of it.

**Lines to reword** (they say "exact"; none changes a bound beyond those above): `05-layers.tex` 42, 176-178, 492, 513, 627 ("padded zero row is again zero" becomes "within `E`, then deleted"), 690, 809, 909, 982; the Proposition's statement "returns `Q_p(Hz)`"; `06-transforms.tex` 222, 405-420, 639, 686, 715; `08-assembly.tex` 7-8, 11-12, 564.

**In exact mode nothing here changes.** With the root scale and exact children, #6932's outer Proposition holds as written.

## 7. The new clause and its cost

**Replaces item 4 of #6932 sec 1, and the execution sentence of its sec 2.**

> **Clause R (rounded scalars).** A native word may use ADD and COPY coefficients `q = a/b` in `A = Z[1/2,1/3,1/5]` with `|q| + 1 < 2^16`, and SCALE by units of `A`, with frames as before. Conditions (i) and (ii) of the odd clause and the declared `S` are not required. Its exact endpoint remains required over `Q`, with every public output row in `Z[1/2]`. Execution: `t += q s` writes `t + RDiv_{a/b}(s)`, and `t *= q` writes `RDiv_{a/b}(t)`, on the stored numerators, by Lemma 1(d), with no check and no reject state. A C pair is rounded on its complete numerators. Integer `q` is exact. Children meet the contract `C(eps,B)`. Output is the word's exact action within the defect of Theorem C, not equal to it. The outer layer returns `Q_p(y - RDiv_{2^p}(y))`. The clause covers complex native words only. A BIT ring has no rounding.

`division_pass.py` and #6932's item 4 are least-significant-first with a check, so they are a different operation. `02-streams.tex` lines 198-208 license power-of-two division and charge reversals as linear passes. They do not name fixed odd division, so the clause must: one most-significant-first finite-state pass, charged linear [P as an automaton, Lemma 1(d)]. #6068 does not bind it: it concerns stochastic unbiased rounding, and this is deterministic.

**Scans per call on the word.**

| site | count | passes |
|---|---|---|
| dyadic non-integer | 19,729 | 1 least-significant-first, with the offset carried in it |
| odd denominator | 3,001 | 1 least-significant-first, 1 reversal, 1 most-significant-first, 1 reversal, about 4 against about 3 in #6932 |

All 22,730 sites round if the grid is shared. An earlier sketch said "each of 3,001 divisions becomes one more rounding site", which undercounts: rounding sites are 22.68 bits of gain against 16.79 for the odd ones.

**Raw, recounted on the word.** Baseline reproduces #6932's figures exactly. The charge unit for the new passes is a model, `4(bits+1)` per scan after #6932's formula [judgement]. Old caller first, then with the #6912 block rewrite (`-159,498,240` in every reading).

| charge | upper | second LAMBDA count | margin there | with #6912 | margin |
|---|---|---|---|---|---|
| baseline, #6932 as shipped | 985,187,200 | 997,747,200 | +2,252,800 | 838,248,960 | +161.8M |
| offset at each rounding site | 988,702,024 | 1,001,262,024 | **-1,262,024** | 841,763,784 | +158.2M |
| and MSB scan at odd sites | 989,552,416 | 1,002,112,416 | **-2,112,416** | 842,614,176 | +157.4M |
| and MSB scan at every site | 995,789,344 | 1,008,349,344 | **-8,349,344** | 848,851,104 | +151.1M |
| worst: and 2 scans at odd sites | 996,639,736 | 1,009,199,736 | **-9,199,736** | 849,701,496 | +150.3M |

So:
- "The raw count's bit-length term should cover it" holds for the upper reading and fails for the conservative recharge on the old caller, even for the offset alone.
- Dropping the root scale does not rescue it. The 997,747,200 line carries no per-call scale, so there is nothing to free. The 2,089,440 belongs only to the every-call scale line.
- With #6912's rewrite the margin is at least 150M in every reading tried. **Rounded mode should be declared on the rewritten caller.**

**Owed, not done:** a charge model taken from text rather than assumed, including where reversals land; a tape-level recount of the most-significant-first pass; reruns for any later word. T, P, S and `kappa` are untouched.

## 8. Measurement [P for the bound, S for the model]

One root fibre, 512 coordinates, `d = 9`, generic commuting unitary frames `WH diag WH / 512`, exact integers, no checks. MOVE is the frame numerator rounded, then a child that truncates `g` low bits. Every non-integer site is `RDiv`. Exact reference: the endpoint action on the same input.

**No measurement exceeded its bound.** 15 natural runs on the #6932 word (21,765 row samples) and 14 on the dyadic word (20,174): 0 rows above either bound, with `g` in {0, 20, 44, 70}, `F` in {16, 24, 40, 80}, floor and toward-zero children, all input kinds.

| check, #6932 word | prediction | measured |
|---|---|---|
| `S = 225`, `g = 0`, grid input | error exactly 0 (the Proposition) | exactly 0 on all 1,451 rows |
| `S = 1`, `g = 0`, grid input | at most `2^26.7`; model `2^20.8` | `2^23.95`: bound holds, model 3 bits low |
| fibre-norm gain at `g = 20, 44, 70` | at most `2^23.66` | `2^18.2`, slack 5.5 bits |
| coordinate-max gain, same inputs | not bounded by this theorem directly | `2^15.0` |
| worst err over row bound, `g = 0` | at most 1 | 0.601 |
| worst err over row bound, `g >= 20` | at most 1 | 0.983 (floor child), 0.89 (toward zero) |

**Correction of the earlier section on this.** "Measured `2^14.65` against bound `2^23.66`, slack 9 bits" compared a coordinate maximum with a fibre-norm bound. On those same inputs (`F = 60, g = 44`) the fibre-norm gain is `2^18.18` and the coordinate gain `2^14.98`. The honest slack on the worst row is 5.5 bits, and on some rows a natural truncating child comes within 2% of the row bound.

**The bound is attained.** An adversarial child inside the contract, adding every MOVE residual in phase at a target row, reaches err over bound 0.99989 (row 1436), 0.9999955 (row 517), never above 1. Dyadic word: 0.9999976, 0.9999960.

**Controls, all fail as they must.** Planted MOVE bias at 2x contract: ratio 2.000. Planted rounding bias: 7.96 at amplitude 4, 2.00 at amplitude 1. Unaligned +1 bias: 2.25. Constant `2^5` replaced by `2^4`: 1.9996. Rounding constant `2^4` halved: natural `g = 0` runs fail at 1.20. Theorem A with realized residuals held in every control, as an identity-level bound should. A non-unitary frame and a dropped ADD, also planned as controls, are not reported.

**Nesting.** MOVE slots executed by full rounded runs of the same word, to depth 3 (15 nested calls): top error 0.594 of the composed bound at `g = 0`, 0.885 at `g = 20`, 0 violations. With a +1 rounding bias: 2.243, 68 rows over.

**Rejection.** The truncating child's rejection at event 26,563 in #6932's run is cured by Lemma 1(a): no run rejected anywhere. That event is not special.

**Model [judgement].** Median err over root-sum-square: 1.09 at `g = 0`, 0.91 at `g >= 20`, maximum 4.0.

**Not run:** the caller, so the per-context `2^124.62` is untested; true Clifford gates of `physical.py`; width 2. Nested inner runs are single-input and one row only. The measured level-to-level ratio of about 130 understates a generic gain for that reason.

## 9. Recheck of K_star, caller mass and #6901's hypotheses [P, Q]

**An error in the earlier derivation.** It used `v = 2223`, `m = 153^2223` and `H > 17,784`. `2223` is the *logarithm* power (`LP`). The chronological power is `power = 1920` (`check.py:473`). For #6030 the two values coincide at 1024 (`PROOF-REVIEW.md:113,126`), which is how the confusion arises. #6901's `v` is the chronological power: "cutoff `16^v`, productive floor `17^v`, ambient `145^v`" (PROOF lines 19-20). The check is `step*hi_ > 8*power` (`check.py:497`), that is, `H > 15,360`.

| | earlier | corrected |
|---|---|---|
| `v` | 2223 | **1920** |
| `m` | `153^2223` (16,133 bits) | **`153^1920`** (13,934.2 bits) |
| `H` check | `> 17,784` | **`> 15,360`** |
| actual `H` | not used | **`1,338,590,000,000,000,000`** (`step = 10^13`, `j = 133,859`; minimal, `j-1` fails) |
| `K_star` bits | about 16,173 at `H = 17,784` | **14,065.5** at the written `H`; 13,973 at `H = 15,361` |
| margin | about 1,600 bits | **about `1.34 * 10^18` bits at the written `H`**; 1,377 bits for `1100*K_star` at the smallest `H` the check admits |
| caller mass | "`M <= 2^4000`", no derivation | **`M_C <= 2^120.35`** (majorant, computed) |

Using carrier 153 over the true `maxT` only enlarges `K_star`, and `s > n/m` survives a larger `m`. The margin absorbs any per-node polynomial miss in `H`, `m`, `v`.

**The width line in #6932 sec 4 needs its constants replaced.** `82 t < d` used the #6030 caller mass 10 as a placeholder. On this word, per context: height at most `15 + 157 = 172` bits (157 is a path-maximum majorant over all caller prefixes, not an actual height), magnitude at most `37.48 + 120.35 = 157.83` bits. So **`344 t < d`** is the sufficient form for the exact mode. It follows from `345 * K_star < 2^H`, as in #6901 lines 299-304.

**Hypotheses of #6901 against the per-port root:**

| hypothesis | verdict |
|---|---|
| `r_max < k_min`, `k_min >= 2`: `11^1920 < 12^1920` after the pass | holds; `check.py:478` tail ratios |
| `m` = max productive rank: carrier 153 = `max(maxT, ambient)` | holds; `check.py:481` |
| sources `s > n/m`; `e/n <= (r_max/m)(r_max/k_min)^G <= rho` | holds; general, `r_max <= m-1` |
| at most `v` contexts per class; one raw unit | holds; A and B are one joint stream with 18 joint contacts, so one raw caller |
| `153 < 2^8`, `H > 8v` | holds |
| complete swaps, not interrupted | holds on reading: SWAP is atomic in the caller and the transient is in the majorant |
| owned center as a paid field | holds; FINITE-PRECOMPILATION sec 6 covers it |
| **Literal constants** `1/16`, 8500, `4t`, `14t`, `W+6`, numerators at most 16 | **fail, and are replaced.** Denominator `2^15 * 225`, word mass `2^29.67`, `\|a\|` up to 40,864. Declared by #6932; the replacements are computed here |
| **Integral local endpoint and integral controller prefixes** (#6900 secs 2 and "endpoint-composition"; used by #6901's relative-prefix input) | **fails literally.** The hosted endpoint has `beta = 1/2`, `1+t = 1/2`, and caller scalars include `1/128`. Debt does not reset at a contact, only at the caller's end. Harmless: it is the 157 above, and the same triangle-inequality argument (#6901 lines 226-230) carries it |
| Credited native equalities at every `f` with spectators; full occurrence maps (#6878) | **Not shown, not failed.** 3,230 chart maps, 7,488 contacts and 18 injective field maps at one column. A faithful width-2 run of the recipes passes on 3,438 maps (1,731,297 executions, phase `i^(pf)`), sampled at high rank; an analog of #6878's full ambient maps is missing |

So no hypothesis of `(4a)` fails. Two literal inputs fail with computed replacements. Item 1 of #6901's nonprecision interfaces remains unshown on this word.

## 10. Proved, computed, assumed

- **Proved [P]:** Lemma 1; Theorems A and B; Theorem C and the corollary given S1 to S5 and section 5; Proposition R and its downstream constants.
- **Computed [P]:** section 5, the bit counts of section 9, the raw table. Float gains over all rows, with exact recheck of the worst row by word. Exhaustive `RDiv` automaton, 285,870 cases.
- **Quoted, not re-derived [Q]:** S1 to S5. Frames unitary on fibres: read from the gate alphabet (`physical.py` lines 32-42 raises on any gate but P, X, D, phase, C, and each is unitary), then tensor power at width `f`. The 1,095 frames were not re-verified one by one.
- **Argued, weaker [judgement]:** adapters and normalizers are monomial. If a normalizer contains C stages with direct rounding, add `log2 D` bits per context. The inequality still holds: `K_star (log2 D)^2 / H <= D/8` for all `D >= N`, because it holds at `D = N` and the left side grows more slowly. Lowering of free adapters (`lower_child`) was not checked. The use of a product's factor gains is a reading of p7-TENSOR, with one second reader.
- **Not shown:** a real recursive run of word plus caller; tape cost of the most-significant-first pass as a recount; the actual `P_r`; physical CLEAR. No new `kappa`. No claim that maintainers would accept this.

## 11. What the theorem does not give [P/S]

- **Not equality.** Downstream statements that use exactness now read "within `E`". This includes "the quantizer at any cut is the identity" (#6900 item 4).
- **Detection is lost.** A checked word notices a truncated child, and this one does not.
- **Complex side only.**
- **Word-specific.** Section 5's constants are #6932's word. A later word needs its own `Gamma_W`, `M_W`, `Sigma_W` and raw line. The margin makes the theorem's conclusion likely to survive. A word with a larger `S`, such as `S = 1125`, loses nothing here, since no `S` is used.

---

## Sources and changes (not for a package)

**the numerical run:** Results of the numerical run are folded in at sections 5, 7, 8. It says "theorem survives" and names the two corrections used above.

**Source reads.** `pkg-lift` at origin/main 7c49fe32c, read with `git show`, checkout unchanged: `upstream/build/sections/{02-streams,05-layers,06-transforms,08-assembly}.tex`, `research/higher-moment-strictification/vendor/{FINITE-PRECOMPILATION,p7-TENSOR}.md`; branch `fork/research/p104-odd-scalar-native` for `check.py`, `native.py`. ` earlier reading/src/p6901.md`, `p6932.md`, `6932_README.md`.

**Scripts.** `const.py` (`const.out`) here: every constant in sections 5, 6, 9 that is new. ` numerical run/rawrecount.py`, run read-only by me on ` same table as its RESULT, baseline matches. Earlier: ` earlier reading/{gains,caller_gains,caller2,rdiv}.py`.

**Changes against ` earlier reading/ROUNDED.md`.**

| # | change | source |
|---|---|---|
| 1 | Paid-job splitting charged per class, 7,293 + 242 bits; `log2 G <= 129`; `c = 1100` stands | READ change 1; rechecked on p7-TENSOR sec 3 |
| 2 | Small-rank base charged, 13,934 bits per node | READ change 2; FINITE sec 4 |
| 3 | `D`-fibre and `R`-fibre norms, order stated | READ change 3; #6901 lines 330-348 |
| 4 | Outer Proposition repaired; Lemma `3l`, convolution `M(9l + sqrt2)` | READ change 4; recomputed |
| 5 | Clause R and recount | READ change 5 |
| 6 | `b = 2^k` shift, offset bound | READ minor |
| 7 | "One circuit" qualified | READ minor |
| 8 | **New here.** READ's `Sigma` about `2^7300` is the split-class value only. The largest are the small-rank base (`2^13,935`) and the ordinary remainder (`2^H`). Still harmless | this note, sec 3 and 5 |
| 9 | **New here.** READ expected about 1.1 more bits of `p`. Reading 08-assembly: none needed, `3l < L` absorbs it at line 564 | this note, sec 6 |
| 10 | **New here.** Proposition R's constant holds for all `D >= 1` with the stated `g`, not only `D >= 19` | `const.py` |
| 11 | **Reversed.** An earlier reading said removing the root scale frees 2,089,440, so raw "should fit". On the recharge line it frees nothing. It fails by 1.26M to 9.20M on the old caller, and fits with #6912's rewrite | this note sec 7; the numerical run |
| 12 | Slack 9 bits corrected to 5.5; model 3 bits low | the numerical run |
| 13 | S3 split into S3, S3a; the factor 2 per context removed, since the completion is now charged explicitly | READ change 1 |
