# Selected PR1094: no improving single whole-helper relocation

On the selected PR1094 owner map, **no single whole-helper relocation between
existing owner bins can strictly reduce the idle moment**, for any real
`0 < a < 1`, with call times, helper widths and actual source-event windows fixed.
Source and destination slices may compact to preserve their occupied prefixes.

This is a complete finite census of one move class, with a short exact comparison
proof. It is not a global packing optimum, a new supplier, or a new kappa. It
does not exclude neutral paths, swaps, multi-role repacking, different call
orders, changed local words, helper splitting or idle-axis transfers.

## Result and evidence

The input is main `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, with PR1094's
selected owner map at audited head
`0fc329d0bec93ca7cd288eaea1295172e8789810`. The exact inputs and originating
catalogue/selected-record provenance are in [SOURCES.json](SOURCES.json).
[TASK.json](TASK.json) records the refined `selected-packing` card, chooser nonce,
method, bounded domain, nearest overlap and structured next questions. The
[coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1332)
records this scope.

[The reproducible certificate](CERTIFICATE.json) contains the baseline owner
recount, all 20 rank classes, every possible improving pair with its event
positions/window endpoints, the positive fixture and eleven inherited owner
mutation controls.

| Capacity-feasible distinct-bin role/destination pairs | Count |
| --- | ---: |
| Strictly lower idle moment for every `0<a<1` | 19 |
| Identical idle moment for every `0<a<1` | 32,872 |
| Strictly higher idle moment for every `0<a<1` | 336,423,971 |
| Total | 336,456,862 |
| Legal strictly improving pairs | **0** |

These are capacity counts before chronology and family restrictions; this
package does not enumerate every *legal* neutral or worsening move. The full
logical role/bin Cartesian domain has `69,120 * (32,256 - 1) = 2,229,465,600`
pairs. The capacity filter and rank-class sums account for every one that fits.
Bins with zero remainder are included in the domain, but cannot receive a
positive-width helper.

The 32,256 bins have remainders
`{0:24730, 1:2276, 3:377, 7:7, 48:4866}`. Only three roles supply the 19
capacity gains:

| Role `(stage, replica, helper)` | Remainder change | Destinations | Why excluded |
| --- | --- | ---: | --- |
| `(1,15,226)`, width 7 | `1+7 -> 8+0` | 7 | Call event 181 is after six windows `(-1,13)` and before one window `(255,430)` |
| `(5,7,69)`, width 4 | `7+7 -> 11+3` | 6 | Call event 376 is after all six windows `(-1,13)` |
| `(8,4,115)`, width 4 | `7+7 -> 11+3` | 6 | Call event 390 is after all six windows `(-1,13)` |

The destinations in `(-1,13)` are `(owner=1, child=0, port=0..5)`; the other
is `(owner=13, child=15, port=14)`. All 19 fail the strict chronological window
already. The obstruction therefore holds even if the active-pair and per-call
family-uniqueness restrictions are relaxed. The verifier retains those checks
for its positive fixture.

## Exact comparison and completeness

Let a source bin have free rank `x`, a destination have free rank `y`, and the
moving helper have width `w>0`, with `y>=w`. A relocation changes the free-rank
pair from `(x,y)` to `(x+w,y-w)`, preserving its sum. With `p=1-a` in `(0,1)`,
its moment contribution, apart from a fixed positive normalization, is
`x^p+y^p`. Rank zero contributes zero, even when its child is omitted.

For fixed sum `S`, `t^p+(S-t)^p` is symmetric and strictly decreasing as the
larger argument increases above `S/2`, by strict concavity. Continuity handles
zero arguments. Consequently the new minus old moment has sign:

- negative iff `x+w>y`;
- zero iff `x+w=y` (the two remainders exchange);
- positive iff `x+w<y`.

If `x>=y`, the new maximum `x+w` is strictly larger. If `x<y`, compare `x+w`
with `y`: above gives a larger maximum; equality exchanges the entries; below
makes both new entries smaller than the old maximum. This proves the three
cases for **every** real `0<a<1`, without floating-point comparisons, numerical
root ordering or sampled exponents.

Group source roles by `(x,w)` and destination bins by `y`. For each `y>=w`,
the number of distinct-bin pairs is
`source_roles * (destination_bins - [x=y])`, because every source role has
exactly one own bin in the matching destination class. Every role belongs to
one source class, and every bin to one destination class. This counts the
entire capacity-feasible domain without enumerating hundreds of millions of
nonimproving pairs. Only negative-sign classes need individual legality checks;
all 19 are materialized and rejected by their actual event windows.

The source-event geometry/windows, helper widths and original map are checked
with Josie Elliston's pinned [PR1091 owner audit](../t16-owner-audit-seed67/verify.py),
including its eleven mutation controls. This package reuses that geometry and
baseline checker; it does **not** claim a separately implemented geometry audit.
Its new enumeration and comparison proof are separately testable. Input bytes
are hashed before decoding or executing the pinned audit. Registered replay
also checks their historical Git provenance.

## Positive fixture, controls and replay

A negative result needs a checker that can find a gain. In memory, the positive
fixture legally moves role `(0,0,0)` (width nine) from `(14,4,14)` to the empty
rank-48 bin `(0,8,0)`. This worsens `0+48` to `9+39`. The new census detects its
legal, strictly improving inverse `39+9 -> 48+0`, plus other gains. The retained
owner checker accepts both altered maps, with the idle histogram independently
recounted; the inverse restores every bin remainder. These maps are controls,
not admitted physical constructions or modifications of the frozen input.

The six test groups cover 1,768 integer radical-product comparisons at `a=1/2`,
a direct enumeration of every pair in a small multi-role fixture, strict window
endpoints, active pairs, family collisions and release of the moving role's own
family. They also reject omitted candidate evidence, false window bounds,
changed moment signs and a suppressed positive inverse. Actual subprocess
controls reject corrupted owner bytes and a missing certificate entry, run in
a minimal offline tree with read-only files and a spaced path under `-I -O -B`,
and preserve an existing output when regeneration is requested at that path.

Python 3.12+ and the standard library suffice. From the repository root:

```sh
python3 -I -O -B research/frontier1094-single-relocation/verify.py
python3 -I -O -B research/frontier1094-single-relocation/test_verify.py
python3.12 -B scripts/research_package.py --package research/frontier1094-single-relocation
```

Expected primary status:

```text
PASS_PR1094_SINGLE_RELOCATION_OBSTRUCTION capacity_pairs=336456862 possible_gains=19 legal_gains=0 positive_inverse=PASS no_new_kappa
```

To regenerate to a **new** output path:

```sh
python3 -I -O -B research/frontier1094-single-relocation/verify.py --write /tmp/single-relocation.json
```

Default verification regenerates the entire certificate in memory and compares
every byte with `CERTIFICATE.json`; it does not modify repository artifacts.

Executed locally on 2026-10-13 with CPython 3.12.14 and 3.14.7 on macOS 26.3.1
arm64: registered 3.12 replay, normal and optimized direct replay, all six test
groups, metadata/source provenance and `make selected-record-check` pass. The
20 research-workflow tests pass with one existing skip. The portable certificate
SHA256 is `66a4abb2f9e01fac2654b44a5f2b3fec2242bda0508083ac78bebd83ecef004a`.

## Scope, pricing and overlap

The local paid profile, 144 complete calls, bit supplier and inherited fixed
extra charges are held fixed. Thus the comparison concerns the two changed idle
terms of the complex recursive moment. The selected binding check gives
complex saving about `0.0016754627`, bit saving about `0.0017334270`, and selected
conditional kappa `0.001672660197076918`; these values are orientation from the
selected record, not newly certified supplier endpoints here. The absence of
a legal lower idle bill precludes an improvement via this move class under that
unchanged contract. Runtime, precision or controller-cost changes are outside
this comparison.

The selected replay `make frontier1094-verify`, native local-word rebuild,
serialized controller, invoice, chart reconstruction, exact endpoint/outer
repricing and hosted CI were **not run** for this census. All-size/compiler,
common-label/mutable-source realization, whole-call hosting, precision/tape,
analytic-transfer and bit H1–H5 obligations remain inherited. This is not a
formal verification of the full multiplication theorem.

[PR1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240), pinned at
`1e136b8c4a552050820334ad113628775182f08c`, supplies a broader fractional rank-51
packing ceiling. [PR1254](https://github.com/CrocSwap/integer-mult-bounds/pull/1254),
at `95743c1c5ddc4c78670e1ecfe94374d54e69ee46`, compares twelve frozen profiles.
[PR1276](https://github.com/CrocSwap/integer-mult-bounds/pull/1276), at
`588425ebfc307dea3a94db9ba4bd4a3c74141b55`, repartitions unhosted rank-48 axes.
Their broader bounds, profile comparisons and changed-axis moves differ from
this exact role/window census. Newer packing proposals can be stronger; this
package certifies only the specified selected-map neighborhood.

## Open next questions

1. Can one **legal neutral relocation followed by a strict relocation** escape
   this fixed point? Filter the 32,872 capacity-neutral pairs by windows/family
   uniqueness, then enumerate newly available gains using only the two changed
   bins. Neutral movement can move a rank-seven remainder to a different event
   window. No two-step exhaustion or controller admission is established here.
2. Which multi-role or schedule changes attain the selected word's remaining
   packing headroom? Compare exact changed-role/window patterns in accepted
   PR1094 and pending proposals while retaining full admission. This census
   excludes neither those constructions nor improvements on different maps.

The relevance, first experiment and blockers are structured in [TASK.json](TASK.json).

## Credit and disclosure

Rohan Arun supplies PR1094's rare-pattern owner exchanges, on Jeremy Kothe's
PR1087 and preceding owner-packing work. Josie Elliston supplies PR1091's
source-event geometry, whole-helper owner recount and eleven failure controls
(head `b4c13a228acb80f74c682b7097f0ce9bbf51bc4e`). Douglas Colkitt's maintainer
composition applies that audit to PR1094. Hao Yan / FanPUYen's controller,
PR1018/987's seven-slot word, the PR1005 and retained supplier/bit ancestry remain
credited in the selected review and predecessor notices. Their files are
referenced unchanged rather than copied or repinned.

Prepared for @Arham-Tahir64 with substantial OpenAI Codex assistance in
selection, proof, implementation, verification and documentation. No independent
human review is claimed. New material is Apache-2.0; retained notices and
source-specific licenses continue to apply.
