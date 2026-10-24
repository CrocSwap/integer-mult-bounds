# Global intact-region optimum after carried-frame swaps

**Scoped negative result; no new κ.** On both PR4997 contact graphs, the source
paid profile is globally optimal for every `0<t<1`, allowing **any number** of
intact free regions to change chart together. This closes its larger simultaneous
region question under the same fixed-boundary assumptions; it does not extend
the one/two-region census by one more move size.

The full minimum paid histogram is
`{1:2201, 2:412, 3:510, 4:127, 5:40, 8:8}`.
The original assignment attains it. No uniqueness claim is made.

## Scope and evidence

The [proof](PROOF.md) fixes the scalar word, literal signed native maps, owners,
start/final charts, owned-center interfaces and source zero-edge regions.
Within this model, every binary subspace is allowed, with each strand charged
by its nonnegative dimension difference. Additional physical constraints can
only restrict this favorable model. A region split, changed boundary, scalar
rewrite, frame descent or changed native map is outside the theorem.

Exact necessary subspace propagation reduces the 768 free regions to **565
forced charts and 203 binary choices** in each orientation. Complete interaction
components have at most 33 variables; deterministic elimination has separators
of at most three. Every comparison is certified for the whole exponent interval
by majorization or one of five written inequalities. Two inequalities are new;
the other three retain PR4997's credit. No floating calculation is used for
acceptance, and an unknown comparison fails closed.

[RESULT.json](RESULT.json) records the full counts and input hashes.
[WITNESSES.json.gz](WITNESSES.json.gz) contains every propagated bound,
elimination state and an attaining assignment. The source has 29,966 strand
edges forward and 29,974 backward; the eight extra backward edges have zero
rank. Every edge is owned once, and all eight rank-eight center queries are
added to the global strand minimum.

The retained source replay checks all 632 normalized input rows, including
identity restoration of rows 224 through 631 (408 arbitrary helper rows).
The new [independent oracle](oracle_checks.py) exhausts 655 assignments across
seven small graphs, using explicit-set subspaces and a different exact
rank-two objective. It includes a four-variable coupled graph, nonidentity
maps and parallel edges. Source-image, nonbinary-interval, omitted-edge,
rank-mass, reversed-cost and malformed-map controls reject. The package is
author/agent checked; no independent human or formal proof-kernel review is
claimed.

Canonical coordination: [Discussion #5006](https://github.com/CrocSwap/integer-mult-bounds/discussions/5006).
[TASK.json](TASK.json) records the refined card, value/overlap check and limits;
[SOURCES.json](SOURCES.json) pins canonical main
`f259dabc7d70e0db8d6d36bfda888f008bbfecc1` and every consumed dependency.
PR4994 supplies separate per-contact bounds; it does not optimize the coupled
assignment. PR4993's continuing variable-boundary/split-region search is
broader and is not excluded here. The #4953/#4999 mod-I³ line is unrelated.

The later [PR5016](https://github.com/CrocSwap/integer-mult-bounds/pull/5016),
head `be656882128732110c00d08ceff265e71bece0f9`, reports a numerical HiGHS
optimum over 4,684 marginal subspaces at one child-price point. It explicitly
leaves an exact global certificate open. Its full-contact domain permits more
than intact-region changes; this package supplies an exact all-exponent theorem
only for the narrower intact-region domain, not an exact certificate for PR5016.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/global-intact-region-optimum --check-only
python3.12 scripts/research_package.py --package research/global-intact-region-optimum
python3.12 -I -W error -B research/global-intact-region-optimum/verify.py
python3.12 -I -O -W error -B research/global-intact-region-optimum/verify.py
```

The registered hook runs both normal and optimized modes with 120-second
limits per command; allow one minute for the pair on a typical laptop.
Success is `PASS_GLOBAL_INTACT_REGION_OPTIMUM no_new_kappa`.
Direct replay requires only the declared source files and this package, with
their relative paths preserved. Git and network access are unnecessary.
`--write` regenerates this package's receipt and compressed witnesses only.
Verification compares the canonical decompressed witness payload. All new
scientific Python modules are compiled from source bytes to avoid stale pyc.

## Open next questions

Can a source-compatible split of an intact zero-edge region, or a changed
boundary, lower the **complete** moment? That changes a hypothesis of the
proved optimum. Coordinate with PR4993 before taking one literal change;
first price every new edge, owned-center operation and helper restoration.
Absolute phases, arbitrary-input correctness and complete physical/controller
costs must accompany a proposed gain. A larger search over unchanged intact
regions is no longer a useful next step.

Fresh physical phase lowering, finite-precision/tape pricing, native all-column
admission and full controller/compiler/BIT/outer replays remain outside scope.
The selected exponent stays `60403/20000000 = 0.00302015`.

## Credit

Prepared by Krzysztof Wójt with substantial OpenAI Codex assistance. A separate
Luna supporting agent inventoried handoffs/overlap and source dependencies and
wrote the small-graph oracle; the primary agent reviewed it and owns integration.

Credit Cinna Davis / 1337isnot1337 for PR4997's graph, two-region theorem and
three power inequalities; Dugongue for PR4971's carried-frame swaps and the
native source; Cao Yifan / intqwq, zxv, Jacob Alan Sussman, James Reed / jwr404,
Rohan Arun, Ali Romman, DaysSky, Nick Petalas, Ryanson Jonathan and the retained
native/controller/compiler lineage. All original attribution and the full
[source NOTICE](../swap-contact-fusion-gate/inputs/NOTICE) and
[LICENSE](../swap-contact-fusion-gate/inputs/LICENSE) are unchanged, declared
inputs and retained in source exports. New work is Apache-2.0.
