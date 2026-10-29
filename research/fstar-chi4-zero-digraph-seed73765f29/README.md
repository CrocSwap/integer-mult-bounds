# fstar-chi4-zero-digraph-seed73765f29

**The chi(Z) >= 4 case of F-star residue (ii): structural lemmas, anchor
calibration, and a smallest-first search with exact obstructions (no kappa, no
frontier change).** This package takes the question
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) left as
its open question 2 (and [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717)
as its open question 2): **can an exact 3-total rational decoder's zero digraph
have dichromatic number `chi(Z) >= 4` at all?** It (1) proves structural lemmas
constraining any such instance (PROVEN below), including an explicit rank-3
decoder with `chi(U(Z)) = 4` but `chi(Z) = 2` that separates the
underlying-graph question from the dichromatic one; (2) reproduces every
recorded anchor of PRs 2717/2747/2774/2869 in a fresh engine before trusting
anything new (CHECKED); (3) runs a bounded, smallest-first search for the
smallest `chi(Z) >= 4` instance across four generator families and a sequential
linear construction of the smallest triangle-free 4-chromatic target, recording
the exact obstruction per route (CHECKED, scoped negative); and (4) settles
every instance examined through the D(t)-pivot, anchor and certificate
machinery. **F-star itself is not proved and not refuted here.** Every claim is
labelled PROVEN, CHECKED or DEMOTED.

## The object

A `T = 3` exact decoder on `v` lines is `M = sum_{j=1..3} p_j q_j^T` over the
rationals with `M_tt != 0` on every line. Row support `pi(t) = {j : p_j(t) !=
0}`, column support `sigma(t) = {j : q_j(t) != 0}`, `D(t) = pi(t) intersect
sigma(t)` (nonempty). The **zero digraph** is `Z = {(t,s) : t != s, M_ts = 0}`;
`U(Z)` is its underlying undirected graph (`{t,s}` adjacent iff at least one
direction is an arc) and `G_0` the **mutual-zero graph** (`{t,s}` adjacent iff
both directions are zeros). `chi(Z)` is the dichromatic number: the least number
of classes partitioning the lines so that each class induces an acyclic
subdigraph. The proven chain `cost >= sum_j r_j >= cert(M)` and the definition
of `cert(M)` (L8 labellings) are from the merged
`research/root-unit-decoder-lemmas` ([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590)
by DreamingOfClouds, with Claude Opus 5.5 (Anthropic) via Claude Code
assistance). **F-star** is `cert(M) >= floor(2v/3)` for every exact 3-total
rational decoder.

Two colouring notions must be kept apart, per the maintainer review of
PR 2717/2774 (`docs/research/community-efficient1700-review.md`, retained
counterexample `research/community-efficient1700-audit/checks/check-2717-pivot-counterexample.json`):
`chi(Z) <= 3` is a property of the digraph alone, while *3-dichromatic under
`D(t)`* asks for a partition whose classes come from a pivot map `c(t)` in
`D(t)` (equivalently: matched-pivot value `max_c sum_i MAS(Z[C_i]) = v`, Lemma
MP of PR 2717). Ordinary 3-dichromaticity and nonempty `D(t)` do **not** imply
a `D(t)`-compatible partition; this package reports the two quantities
separately everywhere.

After [PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869)
(Aaron Wang) the residue of F-star is (i') cancellation lines
`{t : v_2(M_tt) > gamma}` plus (ii) zero digraphs; PR 2774 settled (ii) on the
fixtures (both `chi(Z) = 3` exactly, yet non-3-dichromatic under `D(t)`: the
obstruction there is the pivot constraints, not the digraph coloring) and left
the `chi(Z) >= 4` case open. That case is what this package attacks.

## Recorded anchors reproduced first - CHECKED

Fresh engine (`verify.py`, stdlib, deterministic, about 12 s), calibrated
against every recorded anchor before any new computation:

| anchor | recorded by | recorded value | this package |
|---|---|---|---|
| `tied_min` one-copy L8 | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds (CP-SAT, CHECKED (recorded)) | 11 of 12 | 11 (engine witness, independently replayed) |
| `cex_min_1` one-copy L8 | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds | 18 of 19 | 18 (stored witness replayed) |
| chain engine on `cex_min_1` stored pairing | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds | 22 (`10+6+6`) | 22 (admissibility re-checked) |
| Lemma MP on `tied_min` | [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) by Aaron Wang (navinor) | 9 (4096 pivot maps) | 9 (4096 maps, exhaustive) |
| Lemma MP on `cex_min_1` | [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) by Aaron Wang | 16 (6144 pivot maps) | 16 (6144 maps, exhaustive) |
| `chi(Z)` of both fixtures | [PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) by Aaron Wang | 3 exactly (unconstrained) | 3 exactly (`tied_min` by subset DP; `cex_min_1` 3-dichromatic with a mutual-zero triangle forcing 3) |
| `MAS(Z)`, mutual clique | [PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774) by Aaron Wang | 4 / 10 and 3 / 3 | 4 / 10 and 3 / 3 |
| anchor reach `S_gamma` | [PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869) by Aaron Wang | 0 of 12 and 8 of 19 (= `anchor_good`) | 0 of 12 and 8 of 19 |

## PROVEN: what any chi(Z) >= 4 instance must look like

Lemma RK (PR 2717, cited not restated): `G_0` has no `K_4`; `Z` contains no
transitive 4-tournament; every zero pair landing in a block has
`|pi(t) intersect sigma(s)| >= 2`.

> **Lemma C1 (reduction to the underlying graph).** If `chi(Z) >= 4` then
> `chi(U(Z)) >= 4`.

*Proof.* A proper colouring of `U(Z)` makes every class arc-free, hence
acyclic. So `chi(Z) <= chi(U(Z))`. QED

> **Lemma C2 (small v).** `chi(Z) <= 3` for every rank-3 zero digraph with
> `v <= 4`; any `chi(Z) >= 4` instance has `v >= 5`.

*Proof.* `v <= 3` is trivial (all-singletons). For `v = 4`, if `chi(Z) >= 4`
then every partition into 3 classes fails; partitions of type (2,1,1) exist for
every choice of pair, and a 2-vertex class contains a directed cycle iff it is
a digon. So every pair would be a digon and `G_0 = K_4`, contradicting Lemma
RK (a). QED

> **Lemma C3 (neighbourhood spans).** For every line `t`, the vectors
> `{p(s) : s in N_{G_0}(t)}` span at most 2 dimensions, and so do
> `{q(s) : s in N_{G_0}(t)}`.

*Proof.* Mutual zero gives `p(s) . q(t) = 0` for all `s` in the neighbourhood,
and `q(t) != 0`; dually `q(s) . p(t) = 0`. QED

> **Lemma C5 (two-plane classification of G_0 neighbourhoods).** For every
> line `t` with `N = N_{G_0}(t)`: if `p(t)` is not parallel to `q(t)` then
> `G_0[N]` is empty; if `p(t)` is parallel to `q(t)` then `G_0[N]` is a
> disjoint union of cliques of size at most 3 and complete bipartite graphs. In
> particular `G_0[N]` contains no odd cycle of length >= 5.

*Proof.* All `p(s)`, `s in N`, lie in the plane `q(t)^perp`; all `q(s)` in
`p(t)^perp`. In the non-parallel case choose coordinates `q(t) = e_1`,
`p(t) = e_2`: then `p(s) = (0, y_s, z_s)`, `q(s) = (x_s, 0, w_s)`, so
`p(s) . q(r) = z_s w_r`; a mutual edge needs `z_s w_r = z_r w_s = 0`, while the
diagonal `M_ss = z_s w_s != 0` forces all `z_s, w_s` nonzero - no mutual edges.
In the parallel case both factors lie in one plane, say `R^2` with rotation
`R90`. Mutual edge `{s,r}` iff `q(r)` is parallel to `R90 p(s)` and `q(s)` is
parallel to `R90 p(r)`; writing `x_s = direction(p(s))`, `y_s =
direction(R90^{-1} q(s))` this reads `y_r = x_s and y_s = x_r`, i.e. vertices
are grouped by their ordered pair `(x, y)` and edges run only between groups
`(a, b)` and `(b, a)` (complete bipartite), or inside a group with `a = b`
(clique; size <= 3 by Lemma RK (a)). QED

> **Lemma C4 (no odd wheels).** `G_0` contains no `W_{2k+1}` (an odd cycle with
> a vertex adjacent to all of it) as a subgraph; in particular no vertex is
> adjacent in `G_0` to every vertex of a 5-cycle.

*Proof.* The cycle vertices would all lie in `N(t)`, and Lemma C5 excludes odd
cycles of length >= 5 inside `G_0[N(t)]`. QED

> **Lemma C6 (basis-pivot families are tripartite).** If there is a basis
> `e_1, e_2, e_3` and a map `f : [v] -> {1,2,3}` with every `q(t)` parallel to
> `e_{f(t)}`, then `chi(Z) <= 3` (colour by `f`).

*Proof.* Within one class `f = a`, an arc `t -> s` needs `M_ts = 0`, i.e.
`p(t)[a] = 0` (up to the nonzero scalar of `q(s)`), but the diagonal `M_tt != 0`
gives `p(t)[a] != 0`. So no arc lies inside a class. QED

None of C1-C6 proves `chi(Z) <= 3` in general; together they constrain any
future `chi(Z) >= 4` instance to `v >= 5`, `chi(U) >= 4` (by C1), with all
digon structure odd-wheel-free and planar-classified per neighbourhood, and
outside every basis-pivot family.

## The separation example: chi(U) = 4 while chi(Z) = 2 - CHECKED (hand example)

Six lines with `p = [(1,1,0), (0,1,1), (1,0,1), (1,1,0), (1,1,1), (0,0,1)]`,
`q = [(1,0,0), (0,1,0), (1,0,0), (0,1,0), (0,0,1), (1,0,-1)]` (control 8 of
`verify.py`, all entries hand-checkable). The underlying graph `U(Z)` is the
5-wheel `W_5` (10 edges), so `chi(U(Z)) = 4`; yet `Z` has dichromatic number
exactly 2 (the digon `{2,5}` forces 2; the classes `{0,2,3}` and `{1,4,5}` are
acyclic), the matched-pivot value is `6 = v` and exact `cert(M) = 6 = v`. So a
4-chromatic underlying graph does **not** force `chi(Z) >= 4`: the dichromatic
question is about cycle-forcing orientations, and this instance is a member of
the basis-pivot family of Lemma C6.

## Search for the smallest chi(Z) >= 4 instance - CHECKED (scoped negative)

Smallest falsifying instance first (`v` ascending), exact `chi` by subset DP,
one bounded pivot maximum per route, early kill with the exact obstruction
recorded. Declared domains and outcomes:

| route | domain / budget | outcome | exact obstruction record |
|---|---|---|---|
| random symmetric / asymmetric boxes | `v = 3..11`, entries `{-2..2}`, seeded | 0 instances with `chi(Z) >= 4`; max `chi(Z) = 3` (C5-seeded) | n/a (no candidate) |
| mutual-dense rejection sampling | `v = 3..11`, >= `v` digons required | same | n/a |
| C5-perpendicularity-seeded extension | `v = 3..11` | `chi(Z) = 3` reachable (the hand C5 control), never 4 | n/a |
| sequential linear construction of the Grötzsch graph as `G_0` (registered) | 3 trials x 60000 nodes | no solution; deepest placements 6, 8, 6 of 11 vertices | node cap hit after backtracking; per-vertex linear nullspaces collapse to rank 3 or sample exhaustion at the deepest cut |
| sequential construction (dev-run, `evidence/SEARCH-LOG.md`) | 12 trials x 200000 nodes | no solution; deepest <= 8 of 11 | same failure mode |
| annealing CSP on the Grötzsch incidence system (dev-run) | 25 restarts x 4000 steps | stalls at 12 constraint violations | no zero-violation configuration found |
| hill-climbs on exact `chi(Z)` (dev-run) | `v = 6..12`, symmetric and asymmetric | max `chi(Z) = 3` from structured seeds, 2 from random starts | n/a (no candidate above 3) |

The Grötzsch graph (11 vertices, triangle-free, 4-chromatic) is the smallest
triangle-free 4-chromatic graph and the smallest 4-chromatic target not already
excluded by Lemma C4 (odd wheels) or Lemma RK (a) (`K_4`). The sequential
constructor places vertices in degree order and solves the mutual-incidence
constraints `p_i . q_j = 0` exactly as linear nullspaces; its failure is
recorded as a budgeted obstruction, **not** an unrealizability proof.

Predecessor search context (recorded, cited): PR 2774's 286-instance census
(`v = 3..12`, four families) found `chi(Z) >= 4` on 0 instances (286/286
decided 3-dichromatic); this package does not repeat that census.

## Settlement of every instance examined - CHECKED

| instance | v | `floor(2v/3)` | `chi(Z)` | `chi(U)` | `chi(G_0)` | MP | anchor reach | cert | F-star |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| `tied_min` | 12 | 8 | 3 | 3 | 3 | 9 | 0 of 12 | witness 11 (recorded max 11) | holds |
| `cex_min_1` | 19 | 12 | 3 (<= 3 decided, mutual triangle) | <= 3 | 3 | 16 | 8 of 19 | witness 18 (recorded max 18) | holds |
| separation example | 6 | 4 | 2 | 4 | 2 | 6 | 6 of 6 | exact 6 | holds |
| 22 searched instances | 3..11 | - | <= 3 (max 3) | <= 3 | <= 3 | = `v` on all 22 | - | >= `v` via Lemma MP | holds |

The fixtures remain non-3-dichromatic **under `D(t)`** (`MP < v`) even though
`chi(Z) = 3`, and both carry certificates above threshold through general
labellings beyond matched pivots (11 > 9, 18 > 16) - exactly the PR 2774/2747
picture. Note also that the anchor reach is a valuation quantity (Lemma SG, PR
2869) and is independent of `chi(Z)`: no dichromatic fact alone can falsify
F-star, which is a statement about `cert(M)`.

## The verdict on the chi(Z) >= 4 case

**Not realized in any declared domain; not proved vacuous.** CHECKED evidence:
the smallest-first search across four generator families, the sequential
construction of the smallest 4-chromatic mutual-zero target, and the recorded
predecessor census produce zero `chi(Z) >= 4` instances; the maximum attainable
in every route is 3 (attained). PROVEN constraints: any instance must have
`v >= 5`, `chi(U) >= 4`, odd-wheel-free and planar-classified digon
neighbourhoods (C4/C5), and lie outside every basis-pivot family (C6). The
separation example shows the `U`-level can reach 4-chromaticity at rank 3 while
`chi(Z) = 2`, so the obstruction, if it exists, is genuinely about cyclic arc
structure and not about the underlying graph. On every instance examined, F-star
holds (`cert = v` via matched pivots on the searched ones; 11/8 and 18/12 on the
fixtures), so the residue (ii) obstruction remains what PR 2774 recorded on the
fixtures: the pivot constraints `D(t)` and the labelling structure, not the
digraph coloring. The `chi(Z) >= 4` branch of the residue is therefore
**reducible to a concrete construction question** (realize a 4-chromatic cyclic
zero digraph at rank 3, or prove `chi(Z) <= 3` from C1-C6 plus the rank
constraints), with no F-star falsifier in sight.

## What is proved, what is witnessed, what is demoted

- **PROVEN:** Lemma C1, C2, C3, C4, C5, C6 above, each with its exact
  hypothesis and written proof; and the separation example's `chi(U) = 4` /
  `chi(Z) = 2` / `cert = 6` values (hand-checkable entries, machine-checked).
- **CHECKED (machine, `verify.py`, stdlib, deterministic, certificate digest
  `032e7239429ba1f8`, about 12 s):** controls 8/8 (brute-force-over-all-labellings
  agreement 3/3 at `v = 3`, diagonal decoder `cert = 3`/`MP = 3`/`chi = 3`,
  corrupted-witness rejection 2/2, dichromatic hand values 4/4, the hand C5
  perpendicularity instance `chi(Z) = 3`, the efficient1700 retained rank-2
  pivot counterexample reproduced exactly (ordinary `chi = 2 <= 3`, MP `1 < 2 =
  v`), the `M = 2 I_3` anchor control, and the separation example); the
  calibration table above (every recorded anchor reproduced); and the
  smallest-first search with exact `chi`, exact MP values, replayed witnesses
  and the sequential Grötzsch obstruction record.
- **DEMOTED / OPEN:** `chi(Z) <= 3` for all rank-3 zero digraphs is **not**
  proved; the search is bounded in `v` (<= 11 for exact `chi`, 12 in dev-run
  hill-climbs) and in construction budgets (60000-200000 nodes), and a failed
  construction is not an unrealizability proof. F-star for general rational
  decoders is neither proved nor refuted. No "exactly when" or necessity claim
  is made for any lemma hypothesis. The matched-pivot floor is witnessed on the
  searched instances and both fixtures, not proved. Chain costs and engine
  witnesses are bounded-search quantities; the recorded fixture limits 11/18
  rest on PR 2111's recorded CP-SAT optimality, not re-verified here.

## Open next questions

1. **Is `chi(Z) <= 3` forced at rank 3?** Either realize the smallest 4-chromatic
   cyclic zero digraph (v >= 5, outside basis-pivot families; e.g. an exhaustive
   pattern search at v = 5..6 with exact rank-3 realization tests), or prove
   `chi(Z) <= 3` from the C1-C6 constraints plus Lemma RK. Why it matters: it
   either deletes the digraph-coloring half of residue (ii) or names the exact
   obstruction a class-(ii) proof must overcome. Blocker: no structural
   contradiction found and no fixture found in the bounded search.
2. **Would `chi(Z) >= 4` even falsify F-star?** On any future fixture compute
   anchor reach, matched-pivot value and exact cert (the `settle()` machinery of
   `verify.py` reports exactly these). The separation example and both fixtures
   indicate certificates survive coloring obstructions. Blocker: no `chi(Z) >= 4`
   fixture is known.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -B research/fstar-chi4-zero-digraph-seed73765f29/verify.py
python3 scripts/research_package.py --package research/fstar-chi4-zero-digraph-seed73765f29 --check-only
python3.12 scripts/research_package.py --package research/fstar-chi4-zero-digraph-seed73765f29
```

Expected markers: `PASS_FC4_CONTROLS`, `PASS_FC4_CALIBRATION`, `PASS_FC4_SEARCH`,
`PASS_FSTAR_CHI4_ZERO_DIGRAPHS`, and `CERTIFICATE.json` with digest
`032e7239429ba1f8` (about 12 s on the authoring host). `make` is not installed
on the authoring host; the commands above are the underlying ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain
`cost >= sum_j r_j >= cert(M)` are from the merged
`research/root-unit-decoder-lemmas`
([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by
DreamingOfClouds, with Claude Opus 5.5 (Anthropic) via Claude Code assistance).
The rank-3 configuration model, the named instances `tied_min` and `cex_min_1`,
their recorded one-copy certificate limits (11 and 18, CP-SAT, CHECKED
(recorded)), the stored cost-22 pairing `data/cex_min_1.B22.json` and the
structural lemmas L5/SCC are DreamingOfClouds' work in
[PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) and
[PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162);
`data/tied_min.json`, `data/cex_min_1.json`, `data/cex_min_1.B22.json` and
`data/cex_min_1.witness.json` are byte-identical copies of their data files
(sha256 `670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93`,
`86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`,
`15f5039069a175831f92c4ffe023a23a6f6e6bd6665f0ca2c2734bbe672b51ef`,
`153f4d2e8dc262f547a91f2daff9724cab88beb4d45c399497efc68a8ed2c933`). The
residue statement, Lemmas SF/MP/RK/AN and the exact-completion engine design
this package adapts are Aaron Wang's work in
[PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717); Lemma MX
and the class-(i) closure are Aaron Wang's
[PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747); the
fixture dichromatic structure, the zero-digraph machinery and the chi(Z) >= 4
question are Aaron Wang's
[PR 2774](https://github.com/CrocSwap/integer-mult-bounds/pull/2774); Lemmas
SC/SG, the class-(iii) collapse and the residue rename are Aaron Wang's
[PR 2869](https://github.com/CrocSwap/integer-mult-bounds/pull/2869); the
falsifier census frontier (196 instances) is Aaron Wang's
[PR 2335](https://github.com/CrocSwap/integer-mult-bounds/pull/2335); the
exact cost 12 of `tied_min` is Aaron Wang's
[PR 2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379); the exact
cost 21 of `cex_min_1` is Nick Petalas'
[PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206). The
maintainer review and its retained rank-2 pivot counterexample are the
community audit in `research/community-efficient1700-audit`. This package does
not claim their results; the new content is the PROVEN structural lemmas
C1-C6 with proofs, the chi(U) = 4 / chi(Z) = 2 separation example, the fresh
engine reproducing every anchor, and the bounded chi(Z) >= 4 search with its
per-route obstruction records.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance;
no independent human review claimed). New work in this package is Apache-2.0.
