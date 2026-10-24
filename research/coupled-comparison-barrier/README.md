# Joint safety criterion and least-barrier update for coefficient changes

DONE — a joint safety test and exact least-barrier update for several coefficient changes. Scoped proof with exact finite checks; no new kappa. No claim remains active.

The rank-one result in [Discussion #5263](https://github.com/CrocSwap/integer-mult-bounds/discussions/5263) does not permit separate tests to be composed without checking their interaction. The following criterion handles all nonnegative low-rank deteriorations at once and gives a strict counterexample to that shortcut on the same retained source fixture.

**Statement.** Let M be a real Z-matrix: its off-diagonal entries are nonpositive. Suppose some w>0 satisfies Mw>0. Let U,V be nonnegative n-by-k matrices, and define

```text
M_new = M - U V^T,
X = M^(-1) U,
C = V^T X.
```

Then M_new has a positive dominance witness if and only if the spectral radius rho(C)<1. When this holds, for every residual envelope r>=0 the componentwise least supersolution of M_new d>=r is

```text
h_new = h + X (I-C)^(-1) V^T h,    h=M^(-1)r.
```

At rho(C)=1 the comparison matrix is singular. For a common multiplier tau on the whole update, the exact witness domain is tau rho(C)<1. If rho(C)=0, every finite nonnegative tau is allowed. A large allowed update can still produce a large, unhelpful error barrier.

**Proof.** The source positive-witness argument gives M^(-1)>=0: scale columns by w and normalize the positive diagonal to obtain a strictly row-substochastic nonnegative Neumann remainder. In particular, M^(-1)1>0. This same argument applies to any Z-matrix with a positive dominance witness.

If rho(C)<1, the Neumann series gives (I-C)^(-1)>=0. Direct multiplication gives the Woodbury inverse

```text
M_new^(-1) = M^(-1) + X (I-C)^(-1) V^T M^(-1) >= 0.
```

Applying this inverse to 1 supplies a positive dominance witness; applying it to r supplies h_new. Multiplication of any supersolution inequality by the nonnegative inverse proves minimality.

For necessity, suppose rho(C)>=1. Perron-Frobenius theory gives a nonzero v>=0 with Cv=rho(C)v. Put x=Xv. It is nonzero, since otherwise Cv=0. It is also nonnegative, and

```text
M_new x = (1-rho(C)) Uv <= 0.
```

A positive dominance witness for M_new would give a nonnegative inverse, hence x<=0, a contradiction. At equality the same nonzero x is a null vector. Scaling U by tau scales C by tau and proves the threshold statement.

**Principal windows.** For any complex source whose comparison matrix is componentwise at least M_new, the predecessor maximum principle gives the residual bound h_new on every principal window. Indeed, nonpositive off-diagonal entries and h_new>=0 imply (M_new)_J (h_new)_J>=r_J. The same updated vector therefore covers every ordered sequence of windows from the changed source. Losing this witness is not proof that every signed or complex source in the comparison class is singular.

**A source-bound failure of separate tests.** The [retained setup fixture](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/sliding-window-inverse/inputs/gaussian_check_setup.py) has comparison matrix

```text
M = [[4,-1,0],[-1/3,5,-1/2],[0,-1/4,3]].
```

Change the magnitudes at positions (0,1) and (1,0) by s,t>=0. The exact joint safety condition is

```text
(1+s)(1+3t) < 119/2.
```

Eliminating the unchanged third row leaves the positive-diagonal two-by-two Z-matrix with diagonal (4,119/24) and off-diagonal entries -(1+s), -(1/3+t). Its determinant proves the condition. Equivalently, det(M_new)=119/2-(1+s)(1+3t).

The separate tests allow s<117/2 and t<39/2. Nevertheless s=8,t=2 fails jointly: 9*7=63>119/2. Both single changes are far below their individual thresholds. The coupled pair s=t=3 is safe. For k=2 the general spectral condition can also be tested exactly as C_11<1, C_22<1 and (1-C_11)(1-C_22)>C_12 C_21; no floating eigenvalue computation is required.

**Prepared-update cost.** With fixed directions U,V and retained factors of M, preparing X uses k solves and forming C costs O(n k^2) field operations. For later nonnegative diagonal amplitude changes U diag(t), retain X, C, h and V^T h. Each barrier update then needs a k-by-k solve plus O(nk) operations, after the relevant joint safety test. Factorization, exact coefficient growth, source reads and physical storage/movement remain paid. These are arithmetic counts, not a bit-complexity claim.

**Evidence.** Both warning-strict normal and optimized CPython 3.12.14 checks pass all 375 tested pairs of source positions and update sizes: 312 safe and 63 unsafe. They compare the coupling criterion with all principal minors of the changed matrix, compare prepared updates with a separate permutation-determinant Cramer solve, check 8,112 principal-window residual vertices, and check four exact singular boundaries and the separate-test counterexample. All computations are rational.

Base: canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision 7. Main and live open-PR/Discussion overlap were refreshed. This numerical-recovery side result changes the `uniform-transfer-audit` scope to simultaneous updates. It does not repeat the predecessor's rank-one result or supply a production caller.

Credit Nick Petalas's [PR #5119](https://github.com/CrocSwap/integer-mult-bounds/pull/5119) and [least-barrier proof](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/window-comparison-barrier/README.md), Ali Romman's Discussion5263 rank-one update, David Ganz / Dugongue's [PR #3872](https://github.com/CrocSwap/integer-mult-bounds/pull/3872), and Jose Manuel's [PR #3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851) setup fixture. Woodbury, M-matrix and Perron-Frobenius theory are classical; no general priority claim is made.

**Remaining task.** Bind one actual multi-coefficient update to fixed nonnegative directions and retained factors, then charge the full update path. Native/outer admission, a production Gaussian page, source preparation and tape costs remain open. No predecessor scientific suite, selected cold replay, Lean or Docker build was run. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. No independent human or proof-kernel acceptance is claimed.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/coupled-comparison-barrier
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_COUPLED_BARRIER`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Bind a real multi-coefficient update to fixed nonnegative directions and price the complete update. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
