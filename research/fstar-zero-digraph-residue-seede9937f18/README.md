# fstar-zero-digraph-residue-seede9937f18

**Residue-class attack on open problem F-star: the non-3-dichromatic zero digraphs (no kappa, no frontier change).** This package takes residue class (ii) of the exact residue that [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717) named after proving Lemmas SF, MP, RK and AN: "zero digraphs that are not 3-dichromatic (Lemma MP then gives only `sum_i MAS(Z[C_i])`)", left untouched by [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) (which closed class (i)). It does three things: (1) exact zero-digraph machinery (MAS over all subsets, the exact Lemma MP value over all pivot maps, dichromatic numbers with and without the pivot constraint sets `D(t)`); (2) calibration on DreamingOfClouds' stored fixtures `tied_min` (12 lines) and `cex_min_1` (19 lines), reproducing every recorded anchor and then computing the dichromatic structure of both zero digraphs (the open question 2 of PR 2717); (3) a smallest-first adversarial search for the first instance where the matched-pivot value falls below `floor(2v/3)`, with exact `cert` where exhaustive a-enumeration terminates and the proven chain cost as the falsifier criterion. **F-star itself is not proved and not refuted here.** Every claim is labelled PROVEN, CHECKED or DEMOTED.

## The object

A `T = 3` exact decoder on `v` lines is `M = sum_{j=1..3} p_j q_j^T` over the rationals with `M_tt != 0` on every line. Row support `pi(t) = {j : p_j(t) != 0}`, column support `sigma(t) = {j : q_j(t) != 0}`, `D(t) = pi(t) intersect sigma(t)` (nonempty). An *L8 labelling* is F2 vectors `a(t)` supported in `pi(t)`, `b(t)` supported in `sigma(t)`, with `K_ts = a(t) . b(s) mod 2`; `cert(M)` is the largest `|S|` admitting an order with `K_tt = 1` on `S` and `K_ts = 0` at every incidence `M_ts = 0` with `t` before `s` (`t, s` in `S`). The proven chain `cost >= sum_j r_j >= cert(M)` is from `research/root-unit-decoder-lemmas` (merged). **F-star** is `cert(M) >= floor(2v/3)` for every exact 3-total rational decoder.

Write `Z = {(t,s) : t != s, M_ts = 0}` for the **zero digraph**. For a pivot map `c : [v] -> D(t)` (a unit mask `e_i` with `i` in `D(t)`), let `C_i = c^{-1}(i)`; **Lemma MP** (PR 2717) gives `cert(M) >= sum_i MAS(Z[C_i])`, where `MAS` is the maximum size of an induced acyclic subset. Call `max_c sum_i MAS(Z[C_i])` the **matched-pivot value**. `Z` is *3-dichromatic* when `[v]` partitions into three acyclic classes; it is *3-dichromatic under `D`* when the classes can additionally be chosen with each line's colour inside its `D(t)` (equivalently: some pivot map has all three classes acyclic, i.e. the matched-pivot value equals `v`).

**The residue attacked here (class (ii)).** PR 2717 demoted exactly: "zero digraphs that are not 3-dichromatic (Lemma MP then gives only `sum_i MAS(Z[C_i])`)", and asked (open question 2) whether a rank-3 zero digraph can be non-3-dichromatic at all. PR 2747 left class (ii) untouched and asked (open question 1) whether `max_c sum_i MAS(Z[C_i]) >= floor(2v/3)` always holds; if it does, Lemma MP proves F-star outright. This package computes both questions exactly where exact computation reaches.

## Calibration - CHECKED (all recorded anchors reproduce)

Machine results (`verify.py`, stdlib, deterministic; certificate digest `86f48c1bacdbe4a9`):

| anchor | recorded by | recorded value | this package |
|---|---|---|---|
| `tied_min` one-copy L8 | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds (CP-SAT, CHECKED (recorded)) | 11 | 11 (hill-climb re-found, witness replayed) |
| `cex_min_1` one-copy L8 | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds (CP-SAT, CHECKED (recorded)) | 18 | 18 (stored witness replayed) |
| chain engine on `cex_min_1` stored pairing | [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) by DreamingOfClouds | 22 (`10+6+6`) | 22 (admissibility re-checked) |
| Lemma MP on `tied_min` | [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) by Aaron Wang (navinor) | 9 (4096 pivot maps) | 9 (4096 pivot maps, exhaustive) |
| Lemma MP on `cex_min_1` | [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747) by Aaron Wang (navinor) | 16 (6144 pivot maps) | 16 (6144 pivot maps, exhaustive) |

## New: the dichromatic structure of the canonical fixtures - CHECKED

| instance | v | `floor(2v/3)` | `chi(Z)` unconstrained | `MAS(Z)` | largest mutual-zero clique | MP (exhaustive) | `v - MP` | 3-dichromatic under `D` |
|---|---:|---:|---|---:|---:|---:|---:|---|
| `tied_min` | 12 | 8 | 3 exactly (subset DP, exhaustive) | 4 | 3 | 9 | 3 | no |
| `cex_min_1` | 19 | 12 | 3 exactly (colouring found; mutual-zero triangle forces 3) | 10 | 3 | 16 | 3 | no |

Consequences, each CHECKED:

1. **Both canonical fixtures have dichromatic number exactly 3 without the pivot constraints.** The obstruction that keeps `cert < v` on `cex_min_1` (18 of 19) is therefore *not* the dichromatic number of the digraph; it lives in the pivot constraint sets `D(t)` together with the labelling structure. PR 2717's open question 2 ("can `Z` itself be non-3-dichromatic") is not realized by either fixture; both fixtures are, however, non-3-dichromatic *under `D`* (the operative sense of class (ii) for Lemma MP).
2. The largest mutual-zero clique is 3 on both fixtures: the Lemma RK (a) bound (no mutual-zero `K_4`) is attained, so clique bounds alone cannot force a dichromatic number above 3 on these instances.
3. The matched-pivot value loses exactly `v - MP = 3` lines on each fixture (`9 < 12`, `16 < 19`), and both values remain at or above both threshold forms (`floor` and `ceil` of `2v/3`): 9 vs 8 and 16 vs 12/13. F-star holds on both canonical class-(ii) instances by the structural certificate alone.

## New: smallest-first falsifier search in the class-(ii) domain - CHECKED (scoped negative)

Smallest falsifying instance first: `v` ascending from 3, four generator families per `v` (entries in `{-1,0,1}` and `{-2..2}`), all designed to populate the residue: `random`/`random2` (unstructured boxes), `sparse` (1-2 nonzero coordinates per `p(t)`, `q(t)`, dense zero digraphs), `forced` (support masks chosen first so at least half the lines have `|D(t)| = 1`, heavily constrained pivot maps), `mutual` (rejection sampling for many mutual-zero pairs). 286 instances, `v = 3..12`, deterministic seeds per instance in `CERTIFICATE.json`.

| quantity | value |
|---|---|
| falsifiers (explicit admissible `B` with chain cost below `floor(2v/3)`, or exact `cert` below threshold) | **0** |
| instances with matched-pivot value below `floor(2v/3)` | **0** |
| minimum matched-pivot ratio `MP / v` | 2/3 (attained at `v = 3`, seed 4611, `MP = 2 = floor(2v/3)`) |
| minimum engine-witness ratio | 0.909 (10 at `v = 11`; every witness above threshold) |
| instances non-3-dichromatic under `D` (`MP < v`) | 8 (listed below) |
| instances with `chi(Z) >= 4` unconstrained | 0 found (286/286 backtracking decisions found a 3-colouring; 0 undecided) |

The complete class-(ii) population found (every one has `chi(Z) <= 3` unconstrained and `cert = v` exactly by exhaustive a-enumeration):

| v | seed | family | MP | `floor(2v/3)` | exact `cert` | arcs in `Z` | mutual-zero pairs |
|---:|---:|---|---:|---:|---:|---:|---:|
| 3 | 4611 | random | 2 | 2 | 3 | 4 | 1 |
| 4 | 4641 | random | 3 | 2 | 4 | 4 | 1 |
| 4 | 4932 | random | 3 | 2 | 4 | 3 | 1 |
| 6 | 6788 | random2 | 5 | 4 | 6 | 5 | 1 |
| 8 | 8848 | sparse | 7 | 5 | 8 | 22 | 5 |
| 9 | 9654 | sparse | 8 | 6 | 9 | 25 | 5 |
| 10 | 10932 | random | 9 | 6 | 10 | 26 | 3 |
| 10 | 10654 | sparse | 9 | 6 | 10 | 33 | 7 |

**Exact obstruction record (early kill).** The matched-pivot value never fell below `floor(2v/3)` anywhere in the domain; its deficit `v - MP` never exceeded 3 (and equals 3 only on the fixtures), while F-star would need the deficit to exceed `ceil(v/3)` (4 at `v = 12`, 7 at `v = 19`) for the MP route alone to fail. The first instance where the matched-pivot value touches the floor exactly (`v = 3`, seed 4611) still has `cert = 3 = v` by exact enumeration. On all eight class-(ii) instances the general labellings reach `cert = v` while matched pivots do not: the label patterns beyond matched pivots (the same effect PR 2747 documented on `tied_min`, where MP gives 9 but `cert = 11`) carry the certificate there.

## What is proved, what is witnessed, what is demoted

- **PROVEN:** nothing new. This package proves no new lemma; Lemma MP (PR 2717) and the chain `cost >= sum_j r_j >= cert(M)` (merged `research/root-unit-decoder-lemmas`) are cited, not restated.
- **CHECKED (machine, `verify.py`, stdlib, deterministic, ~57 s):** controls (brute-force-over-all-labellings agreement 3/3 at `v = 3`, diagonal decoder `cert = 3`, corrupted-witness rejection 2/2, subset-DP MAS hand values 3/3, dichromatic hand values 4/4, `MP = 3` on the diagonal decoder); the calibration table above (every recorded anchor reproduced); the dichromatic structure of both fixtures (exact `chi`, `MAS`, mutual-zero clique, exhaustive MP); and the 286-instance search with exact MP values, replayed witnesses, exact `cert` where a-enumeration terminates and bounded admissible-`B` chain scans.
- **DEMOTED / OPEN:** F-star for general rational decoders is neither proved nor refuted. The matched-pivot floor `max_c sum_i MAS(Z[C_i]) >= floor(2v/3)` is witnessed on 288 instances (2 fixtures + 286 searched), not proved. No "exactly when" or necessity claim is made for any hypothesis. Whether some rank-3 zero digraph has `chi(Z) >= 4` unconstrained remains open (none found here; the backtracking decision is exact when it terminates and 0 runs were undecided in this domain, but the search is bounded in `v`). The chain costs are bounded-search upper bounds on the minimum, not exact minima. The recorded fixture limits 11/18 rest on PR 2111's recorded CP-SAT optimality, not re-verified here. Residue classes (i) and (iii) are not re-attacked. One control's expected value was initially written wrong (the dichromatic number of a directed 3-cycle is 2, not 1; the subset DP returned the correct 2) and corrected in the control after the first run; the correction is recorded here rather than hidden.

## Open next questions

1. **The class-(ii) floor beyond `v = 12`.** Does `max_c sum_i MAS(Z[C_i]) >= floor(2v/3)` hold at `v = 13..20` under forced `|D(t)| = 1` pivot sets with dense mutual-zero structure? Why it matters: Lemma MP would then prove F-star outright. First step: extend the `forced` and `mutual` generators to `v = 20` and compute exact MP where the pivot-map product allows. Blocker: nothing structural; needs a dedicated enumeration session.
2. **Can `chi(Z) >= 4` happen at rank 3?** Realize a triangle-free high-chromatic graph (e.g. Mycielski-type) as a mutual-zero pattern of a `p(t) . q(s)` perpendicularity digraph over the small integers. Why it matters: it separates the digraph obstruction from the labelling obstruction. Blocker: exact chi above `v = 13` is currently budget-limited.
3. **The label patterns behind `cert = v`.** On all eight class-(ii) instances general labellings beat matched pivots to `v`; classifying those labels (as PR 2747 asked for the fixtures) would name the labelling family a class-(ii) proof actually needs. Blocker: none; analysis of stored witnesses.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -B research/fstar-zero-digraph-residue-seede9937f18/verify.py
python3 scripts/research_package.py --package research/fstar-zero-digraph-residue-seede9937f18 --check-only
python3.12 scripts/research_package.py --package research/fstar-zero-digraph-residue-seede9937f18
```

Expected markers: `PASS_FZD_CONTROLS`, `PASS_FZD_FIXTURES`, `PASS_FZD_SEARCH`, `PASS_FSTAR_ZERO_DIGRAPHS`, and `CERTIFICATE.json` with digest `86f48c1bacdbe4a9` (full digest printed by the run; ~57 s on the authoring host). The registered CPython 3.12 replay prints `PASS_REGISTERED_RESEARCH_PACKAGE research/fstar-zero-digraph-residue-seede9937f18 outcome=completed`. `make` is not installed on the authoring host; the commands above are the underlying ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings and the proven chain `cost >= sum_j r_j >= cert(M)` are from the merged package `research/root-unit-decoder-lemmas` ([PR 1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) by DreamingOfClouds, with Claude Opus 5.5 (Anthropic) via Claude Code assistance). The rank-3 configuration model, the named instances `tied_min` and `cex_min_1`, their recorded one-copy certificate limits (11 and 18, CP-SAT, CHECKED (recorded)), the stored cost-22 pairing `data/cex_min_1.B22.json` and the structural lemmas L5/SCC are DreamingOfClouds' work in [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) and [PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162); `data/tied_min.json` and `data/cex_min_1.json` are byte-identical copies of their data files (sha256 `670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` and `86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`). The residue statement, Lemmas SF/MP/RK/AN and the exact-completion engine design this package's engine adapts are Aaron Wang's work in [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717); Lemma MX and the class-(i) closure are Aaron Wang's [PR 2747](https://github.com/CrocSwap/integer-mult-bounds/pull/2747); the falsifier-census frontier (196 instances) is Aaron Wang's [PR 2335](https://github.com/CrocSwap/integer-mult-bounds/pull/2335); the exact cost 12 of `tied_min` is Aaron Wang's [PR 2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379); the exact cost 21 of `cex_min_1` is Nick Petalas' [PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206). The stored 18-witness `data/cex_min_1.witness.json` is from PR 2717's package. This package does not claim their results; the new content is the exact zero-digraph machinery (subset-DP MAS, exact matched-pivot values, dichromatic decisions), the dichromatic structure of both fixtures' zero digraphs, and the class-(ii) smallest-first search with its exact obstruction record.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance; no independent human review claimed). New work in this package is Apache-2.0.
