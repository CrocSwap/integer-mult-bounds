# Selected X4 target forests: finite circuit construction, no new kappa

A restored signed target forest reduces the selected PR799 X4 compensation
panel from **6,320 to 2,324 additions**, including **106 preparation and 106
restoration gates**. Both complete scalar projections save **47,690 real
primitives** under the unchanged cleared-work binary-Horner lowering.

| Complete scalar projection | Original | Forest | Saving |
|---|---:|---:|---:|
| Forward real primitives | 193,162 | 145,472 | 47,690 |
| Inverse-transpose real primitives | 193,210 | 145,520 | 47,690 |
| Scalar macros, either orientation | 19,197 | 15,201 | 3,996 |

This gives **13,890 additional real primitives saved** compared with ToikY's
PR901 disjoint-pair result on the same selected panel (159,362 / 159,410).
Those predecessor numbers are contextual reported results, not imported
receipts or summed savings. The construction here is repriced from its own
complete emitted words. No pending implementation is imported.

The exact attained floor is **10,883 primitives per real component** for the
compensation panel, versus 34,728 originally. Equivalently the complex-stream
circuit has 10,883 scalar instructions and costs **21,766 real primitives**.
A complete 12,544-edge graph census, independently coded Prim solver and every
cycle inequality prove optimality **only within the specified signed-unit,
single-parent target-forest class with independent Horner lowering**.

The selected conditional kappa remains **0.001661634653669567**. This package
does not change the selected record, any supplier generator or `upstream/`.

## Reproduce

From the repository root with Python 3.9+ (standard library, offline):

```sh
python3 -I -O -B research/complex-x4-target-forest/verify.py
```

Expected final line:

```text
PASS_X4_TARGET_FOREST compensation=6320->2324 saved_real=47690/47690 forest_floor=10883 columns=737 orientations=2 no_new_kappa
```

The command checks immutable source inputs, rebuilds the exact recipe, lowers
and replays baseline and replacement scalar programs, runs adverse controls,
invokes the independent checker and compares every receipt field with
[EXPECTED.json](EXPECTED.json). It writes no files. `--write NEW_PATH` is an
explicit development-only receipt command and refuses existing output paths.

Additional checks:

```sh
python3 -I -O -B research/complex-x4-target-forest/test_package.py
python3 -I -O -B research/complex-x4-target-forest/independent.py
```

The second checker reads its own pinned inputs, implements its own graph and
symbolic operator, constructs coefficient microcircuits, runs Prim and checks
all 12,544 cycle inequalities. It does not import the generator. Both checkers
use exact Fraction arithmetic; algorithmic and implementation independence
is claimed, not an independently developed rational-arithmetic library or
independent human review.

## Construction and coverage

[PROOF.md](PROOF.md) gives the general substitution and cost proof.
[RECIPE.json](RECIPE.json) specifies every signed edge, root and exact weight.
[experiment.py](experiment.py) constructs an explicit candidate event stream
by replacing only the pinned 6,320-operation zero-frame compensation segment.
The recipe contains six rooted trees. Leaves are prepared before parents,
residual rows are injected, then parents are restored before children. Every
source access, coefficient work clear/double/halve/add, basis operation and
restoration is counted. No helper stream, frame adapter, recursive child or
copy is added. All non-scalar events remain byte-for-byte equal as JSON values.
The forward panel preserves helpers; the inverse-transpose panel writes them
as required by its dual map. Complete scalar endpoints restore public helpers
and erase private work in both orientations.

Full literal primitive replay checks **728 logical plus nine arbitrary private
input columns**, including all 504 public helpers, eight private centres and
coefficient work. It checks the required final forward/dual shears, public
helper restoration, and private erasure. The independent compensation check
covers **328 arbitrary target/helper columns**, including all 216 active
helpers; the other logical registers are untouched by the panel. Eight
coefficient microcircuits are separately checked on arbitrary source, target
and private-work values. Two real components follow the same real-coefficient
circuit. These are scalar projections: neither checker executes physical
Clifford/frame/phase events or redoes global hosting.

The five primary operator controls and seven independent controls include
missing preparation/restoration, sign errors and underbilled edges. Nine
package tests additionally reject a valid-but-nonminimal all-root forest,
a cycle, boundary corruption, uncleared private coefficient work or target corruption from an omitted clear, and
source corruption, and test minimal relocation without Git metadata. The
missing-preparation control deliberately **passes a helper-only replay** but
fails arbitrary-target checking; checking only the helpers would miss it.

The deterministic search domain is all 112 root edges and both signs on each
of 6,216 unordered target pairs: **12,544 exact edge prices**. Kruskal ends
after its complete edge census and spanning-tree construction; no time or
probabilistic cutoff is used. Seed **34**, drawn using OS randomness, breaks
ties only. Completed coverage is the full stated graph. The written MST
reduction and checked cycle certificate justify the scoped optimum; no
arbitrary-circuit optimum or impossibility theorem is asserted.

## Precision and remaining obligations

The positive prefix envelope is recomputed on every literal primitive. The
baseline envelopes match the pinned selected replay exactly. Forward remains
`6812058044968180837/256` (55 bits). Backward rises from
`48299247699832632898063/16` (72 bits) to
`219829455967238186882729/16` (74 bits). Both remain below the pinned
**192-bit local allowance**. Exact maximum fractional depths of actual
intermediate rows remain **3 forward / 19 backward**, including private-input
columns. Smaller gate counts do not imply containment of all old prefixes.
These bounds are finite scalar checks, not an all-size rounding/tape proof.

Production integration still needs a typed alternative-compensation admission,
fresh source bindings, owner/hosting/invoice replay and outer assembly. The
paid recursive profiles are unchanged. All inherited all-size/compiler,
common-label/mutable-source, whole-call hosting, precision/tape,
analytic-transfer and bit-supplier hypotheses remain. No new global bound,
practical runtime speedup or full multiplication-theorem proof is claimed.
This does not combine PR883's precondition lowering or PR917's helper changes.

## Provenance and attribution

Exact base: **`91a2094f2e022930069e8cfdc810a3ea1b81cd09`**.
Accepted source: PR799 at `80e6463157cfc80b85af09e7e2f14748fe2dac60`.
[SOURCES.json](SOURCES.json) pins the committed maintainer replay archive,
its consumed decompressed members and the selected X4 canonical/program pins.
No network, generated ancestor cache, or pending source is required. Immutable
input archives are hashed exactly; member equality uses decompressed bytes.

This transports an existing mechanism to the selected X4 circuit and checks
its additional saving and exact family floor. Credit **@dd-hemant PR816** at
`133735a2cc2319c12ba5d786214b2217e083e7da` for the signed rational forest/MST
method on historical CK; **Oscar Fennell PR759** for binary forests and the
superroot reduction; **Sricharan Vagvala PR749** for rational restored pairs;
and **ToikY PR901** at `dbe8dc01f8306bd7dab8d861a953b23e5cda6a70` for selected
X4 disjoint pairs. PR909 at `5896f6fce48ee1d507722cc91eb1dcccc878670d` excludes
nonunit disjoint pairs but explicitly leaves overlapping bases outside scope.
PR917's historical CK two-sided circuit is distinct and its savings are not
assumed additive. Prior closed frame-only or disjoint-pair searches are not
reopened by extra computation; the forest class permits overlapping targets.

Credit **Jeremy Kothe PR799**, **Chafik Boukhalfa PR741**, **icekylinx** and the
retained gauge, compiler, cold-helper, owner, precision and supplier lineage.
The source archive and notices are retained unchanged. See the selected
[maintainer review](../../docs/research/community-frontier799-review.md).

Prepared by **Ross Richardson with substantial OpenAI Codex assistance** in
research, code, exact checking and writing, including separate AI workers for
the Prim/operator checker and mathematical review. New files are Apache-2.0,
as specified in the repository [LICENSE](../../LICENSE). No independent human
review is claimed. [CLAIM.md](CLAIM.md) records assignment and coordination;
[VALIDATION.md](VALIDATION.md) records checks and unrun gates.
