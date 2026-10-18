# Audit of the centre block triangle screen at `|B| = 13`

**Exact counterexample to one lower-bound step. This does not settle the labelled block problem and gives no new `κ` bound.**

The still-open [PR #3147](https://github.com/CrocSwap/integer-mult-bounds/pull/3147), at head `5cbc48b18cb05327a8dacab3f626412d3bc5e924` when inspected, asks whether its two-stage block obstruction extends past `|B| = 12`. Its verifier's `check_c4_free_degree_feasibility` uses the expression

```text
C(m,3) - U (m - 2) + W_min
```

as a lower bound for the number of triangles in the distance-2 graph `G2(B)`. Here `U` is the number of nonedges of `G2(B)` and `W_min` is the minimum possible number of wedges in a graph on `m` vertices with `U` edges, computed from the balanced degree sequence. After subtracting the incidence claws, the code treats the result as a lower bound on six-cycles.

This package supplies an exact `m = 13` incidence graph for which that proxy is `52`, while `G2(B)` has only `39` triangles. The missing term is the number of triangles in the complement graph. The example does **not** obey the predecessor's braid-cycle capacity, so it is not a counterexample to the final block-floor conclusion. It shows that this degree-only rejection cannot be extended to `m = 13` using the proxy as a lower bound.

## Construction and exact counts

Let `B = D = Z/13`. Join `D_j` to `B_j`, `B_(j+1)`, and `B_(j+3)`, with indices modulo 13.

- Every vertex on each side has degree 3.
- The six nonzero differences between the offsets `{0,1,3}` are `±1`, `±2`, and `±3` modulo 13, all distinct. Therefore any pair of `B` vertices has at most one common `D` neighbor. The incidence graph has no 4-cycles.
- `G2(B)`, joining pairs of `B` vertices with a common `D` neighbor, is the 6-regular circulant with offsets `±1, ±2, ±3`. It has 39 edges and 39 triangles.
- Each of the 13 `D` neighborhoods contributes one distinct incidence-claw triangle. The remaining 26 triangles in `G2(B)` each use three distinct `D` vertices and correspond one-to-one with six-cycles of the incidence graph.
- The complement `H = overline(G2(B))` is 6-regular, has 39 edges, 195 wedges, and 13 triangles.

For any simple graph `G` on `m` vertices, with complement `H`, `U = |E(H)|`, `W(H) = sum_v C(deg_H(v),2)`, and `t(H)` triangles in `H`, inclusion-exclusion gives the exact identity

```text
t(G) = C(m,3) - U (m - 2) + W(H) - t(H).
```

Each missing edge of `G` lies in `m-2` triples; pairs of missing edges with a shared endpoint are restored by `W(H)`, then triples whose three pairs are all missing must be subtracted by `t(H)`. In this construction:

```text
t(G2) = C(13,3) - 39*11 + 195 - 13 = 39.
```

The audited proxy uses `W_min = 195` (which is attained here because the complement is 6-regular) but omits `t(H)`, producing

```text
proxy triangles       = 286 - 39*11 + 195 = 52
proxy six-cycle value = 52 - 13 incidence claws = 39
actual six-cycles     = 39 - 13 incidence claws = 26.
```

Thus `52` is not a lower bound on `t(G2)` under the stated C4-free incidence assumptions, and `39` is not a lower bound on the six-cycle count for this class.

## What this does and does not establish

The construction is **not** a feasible braid-labelled incidence graph. Under the predecessor's degree-3 rule of at most one six-cycle per degree-3 vertex, 13 vertices on either side allow at most `floor(13/3) = 4` six-cycles, while this example has 26. It does not refute the conclusion that no braid-capacity-feasible graph exists at `m = 13`; it shows only that this proxy cannot prove that conclusion.

The repository's exact 50-edge braid graph and 896 dependent-triple census are not used to assign labels to this construction. The `m = 13` labelled CSP therefore remains open. This audit also does not by itself disprove the reported `7 <= |B| <= 12` result; those cases need a parameter-specific validation of the same triangle inequality or another valid argument.

No supplier, recursive-cost, hosting, precision, or selected-result calculation is changed. The selected record remains the repository's validated `κ = 0.001672660197076918`; this package proves no new bound on it.

## Reproduction

Python 3.12 standard library only:

```sh
python3.12 -B research/centre-braid-triangle-audit/verify.py
python3.12 scripts/research_package.py --package research/centre-braid-triangle-audit --check-only
python3.12 scripts/research_package.py --package research/centre-braid-triangle-audit
```

The first command constructs the graph from the modular incidence rule and checks all degree, C4, edge, triangle, claw, six-cycle, wedge, and complement-triangle counts by exact enumeration. The verifier uses no floating-point arithmetic or external packages.

## Open next questions

Can a valid degree-profile bound that includes complement triangles, or an exact labelled search using the actual braid edges and dependent triples, settle `m = 13`? The first step is to replace the omitted-complement-triangle expression with a proved bound, then compare its six-cycle lower bound with the per-vertex braid capacities. If that relaxation is inconclusive, the remaining task is an exact labelled incidence search. No result here decides that search.

## Credit

The audited formulation and `m = 13` question are from `dcharb78`'s open PR #3147. This package adds the explicit cyclic incidence example, the exact complement-triangle identity, and a small independent verifier. Prepared by OpenAI Codex with AI assistance; no independent human or formal-kernel review is claimed. Apache-2.0.
