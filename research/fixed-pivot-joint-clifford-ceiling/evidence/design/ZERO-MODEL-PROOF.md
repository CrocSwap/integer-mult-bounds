# The retained zero-chart binary family has exactly the source invoice

The model with one retained zero-polynomial chart choice at each of 43 groups cannot save any cost. Every one of its `2^43` simultaneous assignments has exactly the original paid profile and the original helper profile. This conclusion uses the source incidence structure and 43 retained witness identities; it does not enumerate the assignments or invoke a solver.

The source is Cinna Davis's PR5124 at `0335701859182b7bdf31706b0d969c72f5de41c7`. `RESULT.json` records 43 unchanged-polynomial moves in its complete contracted census and retains only the first witness `(499, 7)`. Its separate `DISCOVERY.json` records all 43 distinct groups/axes in the first round of the contracted plateau run. The floating energies in that discovery file are not used as certificates. Each of those 43 specified witnesses was rebound to its exact baseline and changed nine-dimensional Lagrangian chart, and its four incident paid ranks were recomputed exactly. No new Pauli axis, neighboring chart or assignment was generated.

`ZERO-MODEL-INVENTORY.json` records the 43 retained pairs and all 172 incident rows. `ZERO-MODEL-WITNESS-BINDING.json`, SHA256 `af46672c959594e0583fe634bf2a851ecd6667c46c588383481de43d7591fce7`, records their actual chart bases and rank transitions. Every listed single-move paid-rank polynomial is identically zero. All 43 groups are distinct. Their 172 incident rows are all paid identity transitions, and no row has two selected endpoints. Thus the selected groups form an independent set in the complete signed-incidence graph. There is no selected self-loop, selected helper endpoint, selected warp endpoint, or selected-selected parallel row.

Let `Z` be these 43 groups. For `g in Z`, let `L_g(0)` be its original chart and `L_g(1)` its listed retained alternative. Write `delta_g(r)` for the change in the count of paid rank-`r` calls caused by changing only `g`. The exact retained-witness check gives `delta_g(r) = 0` for every `g` and rank `r`. For any binary assignment `x in {0,1}^Z`, every paid incidence has at most one endpoint in `Z`. Its rank change therefore depends on at most one bit. Consequently, for every rank `r`,

`P_x(r) - P_0(r) = sum_(g in Z) x_g delta_g(r) = 0`.

All helper incidences and the eight paid rank-eight centres stay unchanged. Hence `P_x = P_0` and `T_x = T_0` as multisets, before any moment is evaluated. In particular `E_x(C) = 0` for every real `C` for which the rank moments are defined. The result is stronger than a nonnegative numerical test on `[0,.005]`.

The binary energy has no interaction terms. Every aggregate four-state cross-difference is identically zero, so the KZ regularity test is vacuous and a min-cut implementation cannot produce a saving. Repackaging the unchanged invoice, walking this binary plateau, or enumerating all `2^43` assignments is unnecessary.

The completeness statement for the 43-move *source census* retains the authenticated published census premise: this note exactly rechecks the 43 explicit stored witnesses and observes that their count equals the source's recorded total. It does not repeat the 817,600-neighbor census. The all-assignment invoice identity itself requires only the 43 rebound witnesses and the empty induced incidence graph.

## Concrete extension requiring a separate contract gate

A different model must move at least one group outside `Z`, change a retained chart choice, or change the source word. The existing incidence inventory identifies a concrete three-group candidate shape: unfrozen bridge group 172 joins zero groups 499 and 572 by incidence IDs 1193 and 1411. Their retained zero axes are 7 and 25. The complete three-group incident union has 14 paid identity rows, including two separate parallel incidences `(119,172)` that must both remain charged. Frozen groups 526 and 592 remain fixed.

For one future specified chart `B` at group 172, define `E_172(B)` as its complete single-move excess, and `R_499(B)`, `R_572(B)` as the signed four-state cross-differences on the two shared edges. Because the two leaves have no edge between them, the exact model is

`E(x_172, x_499, x_572) = x_172 E_172(B) + x_172 x_499 R_499(B) + x_172 x_572 R_572(B)`.

For that fixed `B`, the best leaf choice is determined by `E_172(B) + min(0,R_499(B)) + min(0,R_572(B))`. This can in principle differ from the already tested two-site energy; two favorable interactions could combine. It is not a prediction of a gain. The existing 3,066-candidate receipt supplies `E_172(B)` and `R_499(B)` for the 1,022 previously declared bridge charts, but supplies no `R_572(B)` table. The added term is an unresolved source obligation, not an omitted free adjustment. A fresh gate would need the exact additional tables, helper and boundary checks, explicit domain, interval signs and independent review before any extension runs.

No three-group table, extended candidate census, optimizer, solver, emitter or compiler was executed. The present recommendation is to stop the 43-zero-chart binary model and preserve the bridge model only as a distinct, untested handoff subject to root review.

## Provenance and credit

The captured discovery source is `zero-model-inputs/DISCOVERY.json`, SHA256 `a611408b9d76622acf50d02d8c37a24bec9f5ec2b3f53c46351f8d565ece4b2d`, from [the exact PR5124 source](https://github.com/CrocSwap/integer-mult-bounds/blob/0335701859182b7bdf31706b0d969c72f5de41c7/research/independent-clifford-expansion/DISCOVERY.json). The contracted graph SHA256 remains `f5db08a5814b14b11b93b79207afb1a8d5ec2c5803c1cf6bbc3333cccf0a94af`. Credit Cinna Davis for the complete single-move census, retained witness walk, alphabet and geometry, and the native-word and Clifford predecessors already listed in `CONTRACT.md`. The incidence-factorization proof and bounded joint follow-up were developed with OpenAI Codex assistance.
