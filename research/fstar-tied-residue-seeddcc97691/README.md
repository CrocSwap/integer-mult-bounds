# fstar-tied-residue-seeddcc97691

**Residue-class attack on open problem F-star: the tied-minimum / isotropic lines (no kappa, no frontier change).** This package takes residue class (i) of the exact residue that [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717) named after proving Lemmas SF, MP, RK and AN: the lines the mod-2 anchor cannot anchor (the tied-minimum / isotropic lines of `research/root-unit-decoder-lemmas` section 7). It adds one proved lemma with exact hypotheses (Lemma MX, a mixed anchor–repair–pivot certificate in two order forms, strictly subsuming Lemma AN and Lemma MP as sufficient conditions), an exact per-line classification of the residue on DreamingOfClouds' stored fixtures `tied_min` (12 lines) and `cex_min_1` (19 lines), an exact obstruction record for the mixed route on `cex_min_1`, and a smallest-first bounded falsifier search in the tied domain (40 instances, `v = 3..12`). **F-star itself is not proved here.** Every claim is labelled PROVEN, CHECKED or DEMOTED.

## The object

A `T = 3` exact decoder on `v` lines is `M = sum_{j=1..3} p_j q_j^T` over the rationals with `M_tt != 0` on every line. Row support `pi(t) = {j : p_j(t) != 0}`, column support `sigma(t) = {j : q_j(t) != 0}`, `D(t) = pi(t) intersect sigma(t)` (nonempty). An *L8 labelling* is F2 vectors `a(t)` supported in `pi(t)`, `b(t)` supported in `sigma(t)`, with `K_ts = a(t) . b(s) mod 2`; `cert(M)` is the largest `|S|` admitting an order with `K_tt = 1` on `S` and `K_ts = 0` at every incidence `M_ts = 0` with `t` before `s` (`t, s` in `S`). The proven chain `cost >= sum_j r_j >= cert(M)` is from `research/root-unit-decoder-lemmas` (merged). **F-star** is `cert(M) >= floor(2v/3)` for every exact 3-total rational decoder; the source states the stronger ceiling form `cert(M) >= ceil(2v/3)` (which is what closes the last `T = 3` windows at `v` not divisible by 3); this package works with the floor form of [PR 2335](https://github.com/CrocSwap/integer-mult-bounds/pull/2335) / [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717), and reports both where they differ.

**The residue attacked here (class (i)).** In a 2-integral normalization with mod-2 anchor labels `a0(t) = p(t) mod 2`, `b0(t) = q(t) mod 2` one has `K0_ts = M_ts mod 2`, so the anchor kills every incidence; `K0_tt = M_tt mod 2` is 1 exactly on the lines with `M_tt` odd. The source's obstruction: what resists are the isotropic lines whose minimal 2-adic valuations among the products `p_k(t) q_k(t)` tie (two tied minima, the reduction cancels), where no one-sided repair exists. PR 2717's Lemma AN handles only the count of odd diagonals, not the tied lines' repair or ordering. This package tests exactly that: can the anchorable lines and the tied lines always be kept together at `>= floor(2v/3)` by one mixed labelling with one order?

## Per-line residue classification — CHECKED

For each line `t` (relative to the stored primitive 2-integral normalization):

- `anchor_good`: `K0_tt = 1` (`M_tt` odd);
- `repairable_1s`: `K0_tt = 0`, but some `a*` inside `pi(t)` gives `a* . b0(t) = 1` and `a* . b0(s) = 0` at every incidence `M_ts = 0` (a full one-sided repair with `b` fixed at `b0`, which is then orderable for free);
- `tied_isotropic`: neither — the stated residue.

On both fixtures the residue is total: `tied_min` has 0 `anchor_good`, 0 `repairable_1s`, 12 `tied_isotropic` (every line has even diagonal and no one-sided repair), and `cex_min_1` has 8 `anchor_good`, 0 `repairable_1s`, 11 `tied_isotropic`. The mod-2 anchor is therefore vacuous on `tied_min` (0 of 12) and four lines short of `floor(2v/3) = 12` on `cex_min_1` (8 of 19).

## Lemma MX (mixed anchor–repair–pivot certificate) — PROVEN

> **Lemma MX.** Let `M = sum_j p_j q_j^T` be a `T = 3` decoder with a 2-integral factorization and anchor labels `a0, b0`. Partition the lines into `A`, `U`, `T` (remaining lines are not kept). Every `t` in `A` satisfies `K0_tt = 1`. Every `t` in `U` carries a chosen `a*(t)` inside `pi(t)` with `a* . b0(t) = 1`, `b(t) = b0(t)`. Every `t` in `T` carries the matched pivot `a(t) = b(t) = e_{c(t)}` with `c(t)` a unit mask inside `D(t)`; write `C_i = {t in T : c(t) = e_i}`. Let `Z` be the zero digraph. Then `cert(M) >= |A| + |U| + sum_{i=1..3} MAS(Z[C_i])` under either of the two exact hypothesis sets:
>
> **(A-first)** (i) each `t` in `U` has `a*(t) . b0(s) = 0` for every `s` in `A` union `U` with `M_ts = 0` and no pivot bit `c(s)` set in `a*(t)` for any `s` in `T` with `M_ts = 0`; (ii) no pivot bit `c(s)` is set in `a0(t)` for any `t` in `A`, `s` in `T` with `M_ts = 0`.
>
> **(T-first)** (i') each `t` in `U` has `a*(t) . b0(s) = 0` for every `s` in `A` union `U` with `M_ts = 0`; (ii') no pivot bit `c(t)` is set in `b0(s)` for any `t` in `T`, `s` in `A` union `U` with `M_ts = 0`.

*Proof.* The labelling is a valid L8 labelling: supports hold by construction, and `K_tt = 1` on `A` by `K0_tt = 1`, on `U` by `a* . b0(t) = 1`, on `T` by the matched pivot. Consider the conflict digraph `D_K = {(x,y) : M_xy = 0, K_xy = 1}`. Anchor-to-anchor pairs `A x (A union U)` carry `K = M mod 2 = 0` at incidences, so those conflicts vanish always; conflicts `U x (A union U)` vanish by (i)/(i'); conflicts from `A` to `T` vanish by (ii) in the A-first form, conflicts from `T` to `A` union `U` vanish by (ii') in the T-first form. Keep `S = A union U union (union_i S_i)` with `S_i` a maximum acyclic induced subset of `Z[C_i]` (size `MAS(Z[C_i])`), and order `A union U` first (any order) then each `S_i` with every internal conflict pointing backward (sink-first topological order); in the T-first form the two blocks exchange. Every conflict between kept pairs then points backward, so no before-pair carries `K = 1`, and `|S| = |A| + |U| + sum_i MAS(Z[C_i])`. `QED`

Special cases: `U = T` empty is Lemma AN's count `#{t : M_tt odd}`; `A = U` empty is [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717)'s Lemma MP matched-pivot certificate. Lemma MX is therefore at least as strong as both as a sufficient condition. The computation below also evaluates the two forms and the class variants exhaustively where possible, and every accepted value carries a labelling/order witness replayed by an independent checker.

## Fixtures: Lemma MP closes the canonical tied instances — CHECKED

Machine results (`verify.py`, exhaustive over **all** pivot maps `c : [v] -> D(t)` as unit masks: 4096 maps on `tied_min`, 6144 on `cex_min_1`):

| instance | v | `floor(2v/3)` | `ceil(2v/3)` | AN (mod-2 anchor) | MP (exhaustive) | MX (max over forms) | engine witness | PR 2111 recorded |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `tied_min` | 12 | 8 | 8 | 0 | 9 | 9 | 11 (re-found) | 11 (CHECKED, recorded) |
| `cex_min_1` | 19 | 12 | 13 | 8 | 16 | 16 | 18 (stored witness replayed) | 18 (CHECKED, recorded) |

So **F-star holds on both canonical tied-minimum instances by a structural certificate**: the matched-pivot construction alone (no anchor, no search) reaches 9 and 16, at or above both the floor and the ceiling threshold, even though the mod-2 anchor is vacuous on `tied_min` and short on `cex_min_1`. The engine witnesses reproduce [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111)'s recorded one-copy L8 maxima 11 and 18 (the recorded values are DreamingOfClouds' CP-SAT results, not re-verified here; the certificate sides are re-found/replayed). Every MX/MP value carries a replayed witness.

## The mixed route's exact obstruction on `cex_min_1` — CHECKED

Mixing the 8 anchor lines of `cex_min_1` into the pivot construction fails **completely**: for every one of the 6144 pivot maps, the A-first hypothesis (ii) fails (`A->T conflict`, 6144/6144) and the T-first hypothesis (ii') fails (`T->AU conflict`, 6144/6144). The winning MX value 16 is therefore the pure matched-pivot (all-`T`) construction; no anchor/pivot mixture adds anything on this instance in either block order. This is the exact obstruction to extending AN/MP by naive mixing on the canonical hard instance: the anchor labels `a0` and `b0` of the 8 anchorable lines always carry pivot bits at incidences into (and from) the tied block.

## Tied-domain falsifier search, smallest first — CHECKED (scoped negative)

Two generators aimed at the residue: `tied_isotropic` (every line constructed with exactly two tied minimal valuations at level 0 and even diagonal — the anchor isotropic on every line) and `mixed` (half the lines with a unique minimal valuation and odd diagonal, half tied). `v` ascending from 3, two instances per family and `v`; 40 instances total.

| `v` range | instances | exact `cert` (exhaustive `a`-enumeration) | witnesses | falsifiers | `cert` |
|---|---:|---|---|---:|---|
| 3–6 | 16 | 16 decided | — | 0 | `= v` on all |
| 7–12 | 24 | budget-limited | 24 full-size (`= v`) | 0 | `= v` on all |

A witness of size `v` pins `cert(M) = v` exactly (it is the maximum), so `cert = v` holds on all 40 instances; 16 of them are additionally decided by exhaustive `a`-enumeration. Every instance is at or above `floor(2v/3)`; minimum witness ratio 1.0. The falsifier criterion (an explicit admissible pairing `B` with `sum_j rank_F2 B[R_j,A_j] < floor(2v/3)`, which by the proven chain would refute F-star) was tested by an exhaustive `B`-scan when the admissible-pair count is at most 12 and a deterministic local search otherwise: no `B` below threshold was found on any instance (bounded search, not an exhaustive non-falsification proof). Lemma MP reaches `v` on all 40 instances; Lemma MX never falls below MP and is never strictly above it on this domain (`mx_strictly_above_mp = 0`), with the winning variant/mode recorded per instance.

## What is proved, what is witnessed, what is demoted

- **PROVEN:** Lemma MX, both order forms, with the exact hypotheses above (written proof). Together with [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717)'s proven chain and the source package's proven consequence (F-star closes every open `T = 3` window), each closed instance closes its windows.
- **CHECKED (machine, `verify.py`, stdlib, deterministic):** controls (brute-force-over-all-labellings agreement 3/3 at `v = 3`, diagonal decoder `cert = 3`, corrupted-witness rejection 2/2, the MX all-anchor special case reproducing AN's count, an MP control with replayed witness); the per-line residue classification of both fixtures; the exhaustive MP/MX maxima 9/16 over all 4096/6144 pivot maps with replayed witnesses; the mixed-route obstruction counts 6144/6144 in both order forms; engine witnesses 11 and 18 on the fixtures (matching PR 2111's recorded one-copy maxima); the tied-domain search above (`cert = v` on 40/40, zero falsifiers).
- **DEMOTED / OPEN:** F-star for general rational decoders is **not** proved here. Residue class (i) is closed on the two canonical fixtures and the searched tied domain, not for all tied decoders; no necessity or "exactly when" claim is made for any hypothesis (each is sufficient as stated). That matched pivots always reach `floor(2v/3)` is *not* proved — it is witnessed on 42 instances (2 fixtures + 40 searched). Residue class (ii) (zero digraphs that are not 3-dichromatic) and class (iii) (non-dyadic entries) are untouched. The `B`-scan values are bounded-search upper bounds on the minimum chain cost, not exact minima. The recorded fixture certificates 11/18 rest on PR 2111's recorded CP-SAT optimality, not re-verified here. Exact pairing costs known elsewhere (12 on `tied_min`, [PR 2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379) by Aaron Wang; 21 on `cex_min_1`, [PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206) by Nick Petalas) bound `cert` from above via the chain only through `cost >= cert`, and are cited, not recomputed.

## Open next questions

1. **Does the matched-pivot family always reach `floor(2v/3)`?** Concretely: is `max_c sum_i MAS(Z[C_i]) >= floor(2v/3)` for every rank-3 zero digraph with pivot maps into `D(t)`? Why it matters: Lemma MP would then prove F-star outright, and this package witnesses it on all 42 tied-domain instances tested (with `cert = v` on the 40 searched). First step: adversarial construction of decoders minimizing `max_c sum_i MAS(Z[C_i])`, smallest `v` first, using the two-tied-minima generator with dense zero digraphs (rank-3 constraints of Lemma RK apply). Blocker: none structural; needs a dedicated enumeration session.
2. **Insertion-finite MX.** The two block orders fail completely on `cex_min_1`; the general order allows each anchor line to be *inserted* at a valid cut of the pivot order (exact criterion: the anchor line's pivot-block out-neighbours must all precede its in-neighbours in one linear extension). Why it matters: it is the precise remaining power of the mixed route, and its failure would close naive mixing entirely. First step: implement the cut criterion and re-run on `cex_min_1`'s 6144 maps; record how many anchor lines become placeable. Blocker: none; small code.
3. **What labels do the attaining certificates actually use?** The fixture certificates 11 and 18 exceed everything the anchor/pivot families reach (9 and 16). First step: diff the stored/re-found witnesses' labels against all matched pivots and anchor labels, and classify the label patterns (two-bit labels, off-diagonal pairs). Blocker: none; analysis of existing witnesses.

## Reproduce

Python 3.10+, standard library only, from the repository root:

```sh
python3 -B research/fstar-tied-residue-seeddcc97691/verify.py
python3 scripts/research_package.py --package research/fstar-tied-residue-seeddcc97691 --check-only
python3.12 scripts/research_package.py --package research/fstar-tied-residue-seeddcc97691
```

Expected markers: `PASS_FSTARTIED_CONTROLS`, `PASS_FSTARTIED_FIXTURES`, `PASS_FSTARTIED_MX`, `PASS_FSTARTIED_SEARCH`, `PASS_FSTAR_TIED_RESIDUE`, and `CERTIFICATE.json` with digest `439d75261e9a2b9e` (full digest printed by the run; ~306 s on the authoring host). The registered CPython 3.12 replay prints `PASS_REGISTERED_RESEARCH_PACKAGE research/fstar-tied-residue-seeddcc97691 outcome=completed`. `make` is not installed on the authoring host; the commands above are the underlying ones.

## Credit and provenance

F-star, the `cert(M)` definition, L8 labellings, the proven chain `cost >= sum_j r_j >= cert(M)` and the tied-minima obstruction are from the merged package `research/root-unit-decoder-lemmas` (Douglas Colkitt with OpenAI Codex assistance lineage). The rank-3 configuration model, the named instances `tied_min` and `cex_min_1`, their recorded one-copy certificate limits (11 and 18, CP-SAT, CHECKED (recorded)), the stored cost-22 pairing `data/cex_min_1.B22.json` and the structural lemmas L5/SCC are DreamingOfClouds' work in [PR 2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111) and [PR 2162](https://github.com/CrocSwap/integer-mult-bounds/pull/2162); `data/tied_min.json` and `data/cex_min_1.json` are byte-identical copies of their data files (sha256 `670ed90924b601ade22f0d4adaff46d1667e5449326a0f7ba7b88dd8f5906f93` and `86064701dde94b4f35427bc3e19275eaf1e40e9e90d4fea28e7857f3564d4dd7`). The residue statement, Lemmas SF/MP/RK/AN and the exact-completion engine design this package's engine adapts are Aaron Wang's work in [PR 2717](https://github.com/CrocSwap/integer-mult-bounds/pull/2717); the falsifier-census frontier (196 instances) is Aaron Wang's [PR 2335](https://github.com/CrocSwap/integer-mult-bounds/pull/2335); the exact cost 12 of `tied_min` is Aaron Wang's [PR 2379](https://github.com/CrocSwap/integer-mult-bounds/pull/2379); the exact cost 21 of `cex_min_1` is Nick Petalas' [PR 2206](https://github.com/CrocSwap/integer-mult-bounds/pull/2206). The stored 18-witness `data/cex_min_1.witness.json` is from PR 2717's package. This package does not claim their results; the new content is Lemma MX with its proof and both order forms, the exact per-line residue classification, the exhaustive mixed-route obstruction on `cex_min_1`, and the tied-domain search.

Prepared by **Aaron Wang** with help from opencode (substantial AI assistance; no independent human review claimed). New work in this package is Apache-2.0.
