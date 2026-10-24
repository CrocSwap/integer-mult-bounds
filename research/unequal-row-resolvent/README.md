# Exact inverse envelope for unequal row contraction budgets

DONE — exact inverse envelope with unequal row gaps. This is a scoped written theorem with exact finite checks. No kappa or selected-frontier change is claimed. No claim remains active.

The common-row-budget result in [PR #5255](https://github.com/CrocSwap/integer-mult-bounds/pull/5255) has the following strict extension. It retains each row's own budget instead of replacing every budget by the largest one. The [predecessor proof](https://github.com/aliromman/integer-mult-bounds/blob/d63d8848442acc0bdc7b62578e12726c530af3fa/research/sharp-banded-resolvent/README.md) is a source reference, not a runtime dependency.

**Statement.** Let G be any finite directed support graph, with every diagonal entry allowed. Assign a real number 0<r_i<1 to row i. Admit all complex matrices E with that support and sum_k |E_ik|<=r_i. For each root j define w_jj=1, and for i!=j let w_ij be the maximum of the products of r_v over vertices of a simple directed path from i to j, excluding j. Set w_ij=0 when no path exists. Then

```text
max_E ||(I-E)^(-1)||_1 = max_j [ sum_i w_ij / (1-r_j) ].
```

A nonnegative real matrix attains the maximum. For uniform r_i=rho, the path weight is rho raised to directed distance, so this recovers the predecessor's formula. This is a new nonuniform-row contract, not a new claim about its uniform special case.

**Proof.** Fix j and set h_i=w_ij/(1-r_j). Every nonempty path has weight below one, so h_i<h_j whenever i!=j and h_i>0. For i!=j, the optimal-path equation is h_i=r_i max_(i->k) h_k. A path that revisits a vertex can be shortened with a strict increase in weight; hence simple paths suffice. At j the allowed loop gives h_j=1+r_j h_j, and h_j is the largest h entry.

Put B=|E| entrywise. The row constraints and these equations give (I-B)h>=e_j. Since ||B||_infinity<1, the inverse (I-B)^(-1) is entrywise nonnegative. Thus (I-B)^(-1)e_j<=h. The Neumann series also gives |(I-E)^(-1)|<=(I-B)^(-1). This proves the entry and column upper bounds.

To attain the bound, put r_j in the root diagonal. At each other reachable i, choose a successor k with h_i=r_i h_k and put r_i in E_ik. Set all other entries to zero. Each chosen edge strictly increases h, so these choices have no directed cycle and must reach j. The root column of (I-E)^(-1) is exactly h. Choose a root with the largest sum. This proves attainment and the norm formula.

**Useful finite distinction.** On the three-vertex path with both edge directions and loops, row budgets (1/2,3/4,1/4) give the exact maximum 7. Replacing them all by 3/4 gives 10. The improved value is the exact optimum over the stated support/budget class, not just a better sufficient estimate. The root-1 attaining matrix has entries E_01=1/2, E_11=3/4, E_21=1/4 and all other entries zero.

**Evidence.** CPython 3.12.14, standard library, warning-strict normal and optimized execution both pass: 5,259 attaining graph/budget/root cases, 282 signed diffuse matrices, the 7-versus-10 fixture, and seven controls. The checker enumerates every directed off-diagonal support through three vertices and all row-budget assignments from {1/4,2/3,3/4}. It computes the actual inverse by rational elimination, independently of the path recursion. The proof is dimension-uniform; finite checks alone are not its proof.

Base: canonical main ff3cc58e370d0f678e529246f8c73e8094e18fcf, priority revision 7. This is a conditioning side result under `uniform-transfer-audit`. Live open-PR/Discussion searches and the pinned precision-note search found no matching unequal-row optimum; arbitrary historical diffs and unpublished work are outside coverage. The variable-gap band-solver precision question is distinct from this finite graph optimum.

**Limits and next question.** The theorem does not prove the Gaussian caller's row budgets, exclude concentration, lower physical tape costs, or admit a supplier. A useful next task is to extract heterogeneous rational row bounds from one actual rounded coefficient matrix and compute its maximum-product paths. That concrete source binding and its preparation cost are still missing. No predecessor scientific replay, selected cold replay, Lean, Docker, or native/outer run was performed.

Credit Ali Romman's PR5255 for the uniform support optimum, Cinna Davis's [PR #4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) for the conditioning context, and James Reed's [PR #4282](https://github.com/CrocSwap/integer-mult-bounds/pull/4282) for periodic sections. Neumann-series, maximum-principle, and optimal-path methods are classical. Prepared by Ali Romman with substantial OpenAI Codex assistance; Apache-2.0. No general literature-priority or independent human/proof-kernel acceptance is claimed.

## Reproduce

```sh
python3 -B scripts/research_package.py --package research/unequal-row-resolvent
```

Use Python 3.12 with the standard library. The normal and optimized commands must print `PASS_UNEQUAL_ROW_ENVELOPE`. The launcher must print `PASS_REGISTERED_RESEARCH_PACKAGE`. The checker has no external runtime inputs.

## Open next questions

Extract unequal rational row budgets from one emitted coefficient matrix and charge their preparation. The source binding and physical cost model are not supplied by this package. See `TASK.json` for the structured scope.
