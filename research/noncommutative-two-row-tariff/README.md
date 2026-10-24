# Exact two-row dirty-fanout tariffs over finite noncommutative rings

DONE — the exact two-row dirty-fanout price over every finite associative ring. Scoped all-positive-price theorem with an unrestricted finite shortest-word check; no new kappa. No claim remains active.

This extends lee-phys's finite-commutative five-term formula in [PR #5139](https://github.com/CrocSwap/integer-mult-bounds/pull/5139) to noncommutative finite rings. The functional form of the predecessor formula is retained and credited. The changed condition is principality of the **left** demand ideal, with ordered noncommutative construction coefficients.

**Contract.** Let R be a finite associative ring with 1!=0. Two independent dirty rows a_0,a_1 and a disjoint preserved source p lie in R^w, w>=1. Require A_i=a_i+lambda_i p for all inputs. Use only

```text
P_i(beta):  A_i <- A_i + beta p,       cost mu_i>0,
E_i(alpha): A_i <- A_i + alpha A_(1-i), cost c_i>0.
```

Coefficients multiply on the left. Prices are stationary, complete and independent of coefficients. Words are finite and input-independent, all dirt returns, and no extra rows, free basis changes, clearing or observers are allowed. Every required inverse is paid separately.

For L=R lambda_0+R lambda_1, define

```text
D   = [lambda_0!=0] mu_0 + [lambda_1!=0] mu_1,
T_i = 2 mu_i + 2 c_j, where j=1-i.

If L is not principal, S_i=infinity.
Otherwise, for nonzero total demand:
S_i = mu_i                         if lambda_j=0,
      mu_i+2 c_j                   if lambda_j!=0 and lambda_j in R lambda_i,
      mu_i+2 c_j+2 c_i             otherwise.
```

At zero total demand OPT=0. At every other demand, over all permitted interleavings and repeated source insertions,

```text
OPT = min(D,T_0,T_1,S_0,S_1).
```

**Lower bound.** A row cannot have exactly one nonzero incoming row addition in a word that restores all original dirt. Before that unique addition, its dirt row is still its original basis row. The other current dirt row belongs to an invertible two-row basis. A nonzero coefficient times that other row cannot vanish: multiplying by the corresponding inverse-basis column recovers the coefficient. After the addition no later incoming gate can undo the change. Source insertions do not alter dirt. Thus each used incoming direction occurs at least twice. This argument works over noncommutative rings and zero divisors.

If both rows receive source insertions, their source cost alone is at least D. If only row i receives source insertions and it receives at least two, then either lambda_j!=0 and at least two incoming additions to j are required, giving T_i, or lambda_j=0 and direct insertion at the only demanded row already costs no more.

If there is exactly one insertion at i, the left-ideal invariant from [Discussion #5300](https://github.com/CrocSwap/integer-mult-bounds/discussions/5300) forces L to be principal. A nonzero demand at j requires at least two incoming additions to j. If row i receives no incoming addition, its final demand is the inserted beta=lambda_i and every contribution to row j is a left multiple of beta. Consequently lambda_j not in R lambda_i forces at least two incoming additions to i as well. These alternatives give exactly S_i as a lower bound. Together they cover every word.

**Attainment.** D is direct insertion at every demanded row. T_i is the restoring echo

```text
E_j(-lambda_j), P_i(1), E_j(lambda_j), P_i(lambda_i-1).
```

Zero calls may be deleted. If lambda_j=0, S_i is direct insertion. If lambda_j=r lambda_i, use E_j(-r), P_i(lambda_i), E_j(r).

In the remaining principal case, finite-ring shortening gives a,beta,r with

```text
beta=lambda_i-a lambda_j,
lambda_j=r beta,
lambda_i=(1+a r) beta.
```

The five-gate word E_i(-a), E_j(-r), P_i(beta), E_j(r), E_i(a) restores both dirt rows and has the required source column. It costs S_i. The product order a r is retained. Discussion5300 supplies the finite-module proof of shortening through the semisimple quotient and nilpotent radical; it does not divide by a nonunit or form a quotient by a one-sided annihilator. This completes the upper bound and the theorem.

**Noncommutative discriminator.** In UT2(F2), take (lambda_0,lambda_1)=(E_11,E_12), with one-based matrix indices. The left ideal is nonprincipal, although E_11 R is the generated right ideal. At prices (mu_0,mu_1,c_0,c_1)=(100,1000,1,1), the exact optimum is 202. An incorrectly admitted one-insertion term would underprice it. This is a real noncommutative instance, not a relabelled commutative ring.

**Independent finite evidence.** A Dijkstra search uses the full two-by-three original-dirt/source coefficient matrix as its state. It admits every nonzero coefficient in all four gate types, arbitrary order, and arbitrary repetition; it does not assume the displayed word forms or use the formula as a cutoff. Across five positive-price contexts over UT2(F2), it settles 46,604 states, discovers 99,577 states, and finds all 64 demand endpoints in every context. All 320 exact minima equal the formula. The normal and optimized warning-strict CPython 3.12.14 runs agree. These finite price contexts corroborate the proof; they are not an exhaustive enumeration of real price vectors.

Base: canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision 7. Fresh main and current Discussion/PR overlap were checked. This is a declared noncommutative two-row tariff question under the changed connector-interface scope. The prior general-row source-count result and full-matrix-ring feasibility result are inputs, not repeated contributions. Infinite-ring and arbitrary-many-row total-price formulas remain outside this statement.

Credit lee-phys's [pinned finite-commutative formula](https://github.com/CrocSwap/integer-mult-bounds/blob/ff3cc58e370d0f678e529246f8c73e8094e18fcf/research/finite-commutative-fanout/README.md), Krzysztof Wojt's [PR #5045](https://github.com/CrocSwap/integer-mult-bounds/pull/5045) for the source-count and return classification, Nick Petalas's [PR #4916](https://github.com/CrocSwap/integer-mult-bounds/pull/4916) for the noncommutative dirty-row contract, and Ross Richardson's [PR #3121](https://github.com/CrocSwap/integer-mult-bounds/pull/3121) for the dirty-cut lineage. Ali Romman's [PR #5310](https://github.com/CrocSwap/integer-mult-bounds/pull/5310) and [pinned finite-module proof](https://github.com/aliromman/integer-mult-bounds/blob/77fef394048539d269a45433f30a064d34af96a9/research/finite-ring-source-insertions/README.md) supply the finite left-module shortening extension, first recorded in Discussion5300. This proof dependency is fixed at 77fef394048539d269a45433f30a064d34af96a9; no executable is imported. Classical stable-range and module theory retain their credit.

**Remaining work.** A physical caller must supply complete coefficient-independent prices before this abstract optimum can be used. Source access, native frames, exact arithmetic, precision, movement and head return are not free. A useful next task is to price one triangular-ring realization of the displayed demand; no new multiplier or supplier is supplied. No predecessor scientific replay, selected cold replay, native replay, Lean or Docker build was run. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. No independent human or proof-kernel acceptance is claimed.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/noncommutative-two-row-tariff
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_NONCOMMUTATIVE_TWO_ROW_TARIFF`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Price one triangular-ring realization under a complete physical cost model. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
