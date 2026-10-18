# R480 nonforest panel: 4,858 Horner primitives beyond our forest baseline

**Finite scalar construction; no new κ.** The new compensation network saves
**4,858 Horner primitives beyond our reimplementation of PR1080's signed
bi-forest method** on this input: 18,934 → 14,076, or 25.7% of that panel
(2.44% of the original complete word's scalar primitive count). The forest
comparator is our code, not PR1080's published implementation. Replacing only the panel in the complete
pipeline saves **5,180 copy/unit primitives**, a different tariff from Horner.

The cleanup remains an application of PR1119's two-sided method. Running its
**unmodified published synthesis routines** on this input, at dimension 704,
seed 30 and seventeen sequential trials, gives a best cleanup cost of 36,482
Horner / 24,944 copy/unit primitives. The package cleanup costs 33,368 /
22,448: **3,114 / 2,496 fewer**, respectively. These compare bounded outputs,
not method optima or a new factorization algorithm.

The matched comparison counts all scalar events in the complete local word
under the credited PR696 tariff. Recursive child work and physical Clifford/phase
costs are excluded from this table:

| Compensation panel / cleanup | Forward | Inverse transpose |
|---|---:|---:|
| Our PR1080 forest / published PR1119 routine | 67,874 | 67,890 |
| Nonforest / same published routine | 62,694 | 62,710 |
| Our PR1080 forest / package cleanup | 65,378 | 65,394 |
| Nonforest / same package cleanup | **60,198** | **60,214** |

The surrounding event stream is identical. Scalar helper preparation,
coefficient work and restoration are fully charged. The panel alone saves
5,180 on either cleanup (7.9% of the scalar primitive count against the
identical package-cleanup pipeline). The two selected outputs together
save 7,676 (11.3%) against the bounded published-routine/forest pipeline.
The larger PR1979 comparison is historical context below, not a measure of
the new method's isolated contribution.

| Exact local quantity, original Horner tariff | Ungauged source | Combined application |
|---|---:|---:|
| Compensation scalar macros | 7,208 | **1,819** |
| Compensation real primitives | 80,400 | **14,076** |
| Restoration scalar macros | 6,680 | **3,786** |
| Restoration real primitives | 70,996 | **33,368** |
| Whole-word scalar macros, either orientation | 19,693 | **11,410** |
| Whole-word forward real primitives | 198,766 | **94,814** |
| Whole-word inverse-transpose real primitives | 198,814 | **94,862** |

Against this historical, unoptimized source, the combined application saves
103,952 real primitives per orientation (**52.3%**) and **42.1%** of scalar
macros. Most compensation savings are inherited method application:
80,400 → 18,934 accounts for 61,466 of the 66,324 saved primitives.
All target/helper preparation, coefficient work and restoration are charged.
These counts do not measure integer multiplication speed. The 3,494 paid
recursive children retain the profile
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`; its recurrence moment and selected
κ `836330098538459/500000000000000000` remain unchanged.

## Construction and why it helps

Write the original compensation as `y ← y + C h`, where C is the selected
112-by-240 rational matrix on its active eligible helpers. Let P and H be
invertible dyadic changes of basis on targets and helpers. Execute

```text
y ← P y
h ← H h
y ← y + (P C H^-1) h
h ← H^-1 h
y ← P^-1 y
```

The final state is exactly `(y + C h, h)` for arbitrary incoming targets and
helpers. This equation holds over Q and C. Inverse transpose is a group
homomorphism, so the backward implementation swaps/negates additions and
reciprocates scales **in the same chronological order**. Both complete native
orientations are checked.

[RECIPE.json](RECIPE.json) fixes all **481** basis operations: 148 on targets
and 333 on helpers, including 60 power-of-two scales. The middle contains
857 nonzero additions. The literal replacement, including the reverse inverse
restoration, is [COMPENSATION.json](COMPENSATION.json).

The changed alphabet permits repeated parents and donors, chronological
dependencies, dyadic shears and rescaling. Fifty-two helper children have
multiple distinct parents, with up to six; this is outside a single-parent
signed forest. The complete network combines several coefficient patterns,
turning many quarter coefficients into unit coefficients or zeros.

As a same-input comparator, **our own reimplementation** of PR1080's alternating
signed bi-forest method produces an 18,934-real-primitive compensation panel.
This runs our `discover.py`, not PR1080's published code. Its literal
[FOREST-RECIPE.json](FOREST-RECIPE.json) is checked on arbitrary dirty columns
and fully repriced. The new 14,076 panel saves **4,858 more**, or **25.7%** of
that panel cost. The comparator is a reproduced coordinate fixed point on this
source, not an optimum over all forests, arithmetic circuits or pending work.
Historical published U8/CK counts concern different pinned words and are not
added to these savings.

Applying the inherited cleanup method saves another 37,628 primitives against
the original full-frame restoration. Its exact 704-column
operator has only 3,340 off-diagonal entries, although the original synthesis
uses 6,680 macros. [CLEANUP-RECIPE.json](CLEANUP-RECIPE.json) records 514
dyadic-unit pivots on FULL-ended non-target registers. For its two-sided
factorization `L M R = S`, where S is a scaled permutation, execute
`R^-1`, S, then `L^-1`. Right inverses retain their nomination order; left
inverses reverse it. Three unit additions realize each signed interchange,
and the final diagonal absorbs its sign. [CLEANUP.json](CLEANUP.json) gives
all 3,786 literal gates. The standard-library constructor reconstructs and
checks the original rational operator on every column; it trusts no search
status or floating-point identity.

[METHOD-BASELINES.json](METHOD-BASELINES.json) retains the exact seventeen
published-routine trial receipts and the winning trial 6 (swap penalty 6,
scale penalty 1). [PR1119-CLEANUP.json](PR1119-CLEANUP.json) and
[FOREST-COMPENSATION.json](FOREST-COMPENSATION.json) supply the literal matched
baselines. `reproduce_baseline.py --upstream .` re-runs the source-pinned
`apply_word_to_cols` and `solve_lpr_smart_scale` functions unchanged; only their
supported `dim` argument changes to 704. Its new-input minimum-Horner selection
is explicit, not the original U8 choice of trial 16. The full legacy verifier
is not run because its main routine is bound to the older 728-register U8
word and its historical archive. The generated R480 operator and every full
matched pipeline are separately checked here. Original notices, including
the predecessor's Gemini assistance disclosure, are retained in
[PR1119-NOTICE.md](comparators/PR1119-NOTICE.md).

This replaces the complete restoration operator rather than a repeated-operand
corridor. It therefore changes the hypothesis of the scoped read-barrier result
in [PR1165](https://github.com/CrocSwap/integer-mult-bounds/pull/1165), which
does not exclude refactorization. The fixed scalar-word and cleanup hypotheses
of [PR1995](https://github.com/CrocSwap/integer-mult-bounds/pull/1995) and
[PR2013](https://github.com/CrocSwap/integer-mult-bounds/pull/2013) are also changed;
this does not improve their paid-profile or packing-ceiling budgets.
Two-sided cleanup synthesis is inherited from
[PR1119](https://github.com/CrocSwap/integer-mult-bounds/pull/1119) on the
historical U8 word. The new artifact is the combined compensation/restoration
circuit on this exact selected R480 source. Its two disjoint replacement
intervals are composed in the same full replay, so the savings are not inferred
by adding unrelated receipts.

The compensation network executes at frame zero before entry adapters. The
240 affected helpers have zero entrance and FULL exit and are restored before
the original word continues. Restoration executes at FULL after exit adapters,
before the original post wrappers, touching only the same FULL-ended non-target
registers. The circuit uses the existing 480 public helpers,
eight private centres and one coefficient work stream. Native frame changes,
centre paths, wrappers, helper inventory and all non-scalar events agree exactly
with the selected source.

For a reduced nonzero addition coefficient `q=n/2^d`, the unchanged cleared-work
binary-Horner charge is

```text
2 [3 + bit_length(|n|)-1 + popcount(|n|) + d].
```

Each factor two counts real and imaginary components. Doubling/halving scales
cost two real primitives each. Both basis boundaries are charged. The local
bound **reimplements** the pinned `invoice_allcold.py` formula, rather than
calling that file, including the compiler reserve `64*(73+1)^3` and all
scalar-macro adapter charges. The allowance falls from 10,038,040,553,630 to
6,601,014,768,270 (34.2400%). This is macro-driven: omitting the real-primitive
term gives the same percentage to that precision. It is **non-binding**:
gauge44 is the only provider (144 calls), already below its `< 2^48` check;
the provider choice, paid profile and κ do not change. A global hosted invoice
has not been regenerated.

## Reproduce

Python 3.10+ and its standard library suffice for verification:

```sh
python3 -I -O -B research/complex-compensation-network/verify.py
python3 -I -O -B research/complex-compensation-network/independent_check.py
python3 -I -O -B research/complex-compensation-network/test_package.py
```

The first command checks [CERTIFICATE.json](CERTIFICATE.json), emits the new
full native word in a temporary directory, runs the unmodified hash-pinned
emitter and frame/wrapper auditor, and compares native emission with a separately
spliced complete event stream. `--out NEW_DIRECTORY` retains those artifacts;
existing directories are refused. `--upstream .` additionally binds the exports
and native sources to the pinned live upstream checkout. Normal replays never
rewrite a committed result; `--record NEW_FILE` creates a fresh development receipt.

The separate integer-dyadic checker imports no primary or native implementation.
It executes every literal coefficient-work clear, source addition, double, halve,
target accumulation, copy and centre operation in the original and replacement
programs, both ways and with two lowerings, the three matched panel/cleanup
pipelines, plus the published gauge word under copy/unit: **22 programs on
all 713 logical/private input columns**.
All 480 public helpers restore and all nine private inputs erase. The positive
prefix bounds decrease from **52 / 68 bits** to **41 / 54 bits** forward/backward,
within the inherited 192-bit allowance. Maximum reduced denominator powers fall
from **4 / 17** to **3 / 2**; in the backward program the maximum denominator is
4 instead of 131,072.
[INDEPENDENT.json](INDEPENDENT.json) retains the independently derived receipts.

Twenty-three boundary/recipe controls, 25 native frame/wrapper controls and three
private-work controls pass. Package tests check optimized standalone relocation
without Git metadata and eighteen actual corrupted files, requiring their named
guards. The claimed-price and helper-inventory controls test those fields;
a separate nonzero-entry-frame fixture exercises helper eligibility. A determinant-two
fixture checks signed permutation and both sides of the restoration factorization.
New checks remain active
under `-O`; assertion-based native subprocesses run with optimization disabled.
The integer checker uses the same phase/interval splicing conventions as the
primary checker and does not implement frame or adapter semantics. Frame/wrapper
legality rests on the unchanged upstream native auditor. These are separate
arithmetic implementations by the same assisted author, not independent human
review or proof-assistant formalization.

The optional discovery command uses the existing **NumPy 2.5.1** installation:

```sh
python3 -B research/complex-compensation-network/discover.py --seconds 120
```

It reproduces the exact recipe from the original matrix, with deterministic
integer ties. It starts from alternating signed forests, allows unrestricted
single dyadic shears/scales, then searches one/two-donor moves with beam 16.
The recipe was reproduced in approximately 20 seconds locally. Search caps and
local minima are not optimality certificates. NumPy is not a verification or
registered replay dependency. [TASK.json](TASK.json) records the search domain,
scope change and attempted structural routes.

The cleanup nomination uses a bounded 96-candidate weighted pivot search;
its exact recipe reproduced in approximately 45 seconds:

```sh
python3 -B research/complex-compensation-network/discover_cleanup.py --seconds 120
```

For a practical scalar comparison, [INDEPENDENT.json](INDEPENDENT.json) also
executes Sagar Thakrar's existing
[PR696 copy/unit lowering](https://github.com/CrocSwap/integer-mult-bounds/pull/696).
It overwrites coefficient work with a source copy and specializes unit additions,
paying a final clear in both cases. With the same stronger lowering on both
words, the historical ungauged source falls **149,002 → 60,198** forward and
**149,018 → 60,214** backward (59.6%). That source is superseded by merged
gauge constructions; it is not the strongest published comparator.

Merged same-word gauge work includes
[PR1161](https://github.com/CrocSwap/integer-mult-bounds/pull/1161),
[PR1214](https://github.com/CrocSwap/integer-mult-bounds/pull/1214),
[PR1259](https://github.com/CrocSwap/integer-mult-bounds/pull/1259),
[PR1263](https://github.com/CrocSwap/integer-mult-bounds/pull/1263) and
[PR1353](https://github.com/CrocSwap/integer-mult-bounds/pull/1353).
PR1263 reaches 136,002 / 136,018; PR1353 reaches 135,912 / 135,928.
The stronger merged [PR1979](https://github.com/CrocSwap/integer-mult-bounds/pull/1979)
composes nineteen PR1369 temporal gauges on PR1263's static background:

| Complete word, same PR696 tariff | Forward | Inverse transpose |
|---|---:|---:|
| Published PR1979 gauge word | 134,070 | 134,086 |
| This combined application | 60,198 | 60,214 |
| Difference | **73,872 (55.10%)** | **73,872 (55.09%)** |

[COMPARISON-SOURCES.json](COMPARISON-SOURCES.json) pins PR1979's unchanged
menu, static gauges, expected transition receipt and original credit notice.
`comparison.py` reconstructs its complete stream from our exact original word,
checks every published transition and invoice, and matches the frozen literal
stream. The separate arithmetic checker verifies its endpoint, helper return,
private erasure, paid profile and positive-prefix bound on every input column.
PR1979 is the strongest merged same-word gauge comparator found in the recorded
search; no general optimum is claimed. Both methods rewrite helper coefficients,
so their savings **are not added**; no composition was attempted. The copy/unit
lowering itself is inherited, not a replacement native emitter or a new method.

An optional matched benchmark executes the complete scalar projection on
1,024-bit integer payloads with exact halving guards and arbitrary dirty inputs:

```sh
python3 -I -B research/complex-compensation-network/benchmark.py --out NEW_TIMING.json
```

The CPython interpreter results in [BENCHMARKS.json](BENCHMARKS.json) use eleven
alternating-order rounds and five repetitions, checking the endpoint on every
run. The runtime ratios are about **2.3×** under Horner and **2.6–2.7×** under
copy/unit, compared with the ungauged source. Dispatch and guard-call overhead
dominate; halving has an extra guard call, so op mix affects the ratio.
This is an interpreter workload comparison, not evidence of faster arithmetic
or multiplication. It times one real component and excludes frame operators,
recursive children and compiler work. No PR1979 timing comparison was run.
The circuit counts and certificate do not depend on timing.

In a pinned upstream checkout, the registered package metadata/replay commands are:

```sh
python3 scripts/research_package.py --package research/complex-compensation-network --check-only
python3.12 scripts/research_package.py --package research/complex-compensation-network
```

All four registered Python 3.12.11 commands and the metadata/source-pin check
passed locally on macOS arm64. Hosted CI has not run.

## Maintainer timing provenance and independent replay

The maintainer replayed all four declared verification commands, including
complete native emission/frame checks, the 22 integer-dyadic programs,
relocation/corruption controls and all seventeen published-routine trials.
All declared upstream inputs match their pinned Git blobs and current main.
This validates the scoped finite construction, not a new supplier or κ.

The original `BENCHMARKS.json` is preserved verbatim. Its recorded benchmark
source hash (`32dad02a…`) does **not** match the submitted `benchmark.py`
(`a46bd2cd…`), and the exact older script was not located in the published
PR history. Its timing provenance is therefore not authenticated against the
submitted script. The maintainer did not rewrite that historical source hash.

[MAINTAINER-BENCHMARK.json](MAINTAINER-BENCHMARK.json) records a fresh run of
that exact submitted script with the same 1,024-bit workload, eleven alternating
rounds and five repetitions. Every endpoint was checked on every run. Median
ratios were 2.36–2.39 under Horner and 2.68–2.69 under copy/unit lowering.
These are environment-specific scalar interpreter measurements; they exclude
recursive children, frame operators, compiler work and integer multiplication.
Optional search-nomination timings and optimality were not independently checked.

Maintainer review and provenance clarification: Douglas Colkitt with OpenAI
Codex assistance. Original construction and predecessor credit remain above
and below; this is not an independent human or proof-assistant review.

## Sources, novelty and limits

The base is main **`0b1cccf86e2f5132ed286a26ef0a681a495740ea`**. The exact selected
replay archive and exported provider `candidate/strict/global/base/providers/gauge44/`
are hash-bound in [SOURCES.json](SOURCES.json) and [REFERENCE-PINS.json](REFERENCE-PINS.json).
Selected word payload: `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`.
The saved inputs and native sources under `reference/` permit standalone replay.

The new result is this complete combined R480 network, source-specific search
and paid whole-word improvement. Basis conjugation and two-sided cleanup
factorization are inherited. This work does not
correct another submission or claim invention of restored bases, dyadic shears
or MST methods. It changes the single-parent restriction of the forest starting
class and checks the resulting actual complex circuit. No unrelated provider's
counts are used as the baseline.

The final refresh searched titles and bodies of all 1,996 PRs returned across
open, closed and merged states, alongside 909 freshly fetched Discussion records
and 1,538 local records. The helper reports complete pagination and no warnings;
keyword searches do not cover every code diff or establish exhaustive novelty.
[TASK.json](TASK.json) records the coverage and source heads.
The newer [PR2132](https://github.com/CrocSwap/integer-mult-bounds/pull/2132)
commuting-reorder/free-frame class explicitly excludes coefficient-rescaling
and compensation changes; it does not cover this changed scalar synthesis.
Main was refreshed to `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`, with priority
revision 4; its selected record still matched the scientific base. This continues the
existing construction rather than selecting another research card.
PR1119's
historical cleanup method and PR1165's current corridor barrier are credited
and distinguished above. No matching combined R480 circuit was found; these
searches do not establish exhaustive novelty. Other local sessions studied
rank-six frame climbs, five-call routing and dirty-root connectors, distinct
from this scope.

The original helper-inventory card seeks an improved recursive budget. This is
an explicitly **changed-scope partial result**: an exact, materially cheaper
native complex scalar circuit with an unchanged paid profile. Full physical
Clifford/phase compilation, typed supplier integration, global owner/hosting
invoice, outer assembly, repository-wide cold replay, hosted CI and the inherited
all-size/precision/tape assumptions have not been newly discharged.
`SCALAR-FRAME-AUDIT.json` would need regenerating for adoption. The phase recipes
cover children and endpoint adapters, so this scalar replacement does not change
them.

## Open next questions

1. Can one learned helper shear remain across entry and save paid recursive
   work? First choose a specific shear from the recipe, conjugate its affected
   raw gates, extract every common frame and screen the whole paid profile.
   It matters because the current saving is scalar-only. The blocker is legal
   frame chronology and a fully charged new supplier contract.
2. Can a joint chronological synthesis reduce more scalar work than these two
   boundary replacements? First combine one restored helper block with its next
   same-frame factory gates and verify every intervening read and wrapper.
   It could remove repeated preparation; the blocker is the distinct native
   frame paths and paying the complete return, precision and compiler reserve.

3. Can admissible gauges reduce this rewritten word further? The submitted
   circuit replaces the gauged comparator; it does not compose the old gauge
   schedules with the new network. First derive new event-index schedules and
   conjugate every affected basis/cleanup gate, charging all scale transitions.
   Legal live frames, complete restoration and the 192-bit prefix allowance
   must survive; reusing the old schedules does not establish composition.

## Credit and license

Restored target/helper bases credit **Sricharan Vagvala** ([PR749](https://github.com/CrocSwap/integer-mult-bounds/pull/749)),
**David Awad** ([PR807](https://github.com/CrocSwap/integer-mult-bounds/pull/807)),
**Ross Richardson** ([PR917](https://github.com/CrocSwap/integer-mult-bounds/pull/917),
[PR932](https://github.com/CrocSwap/integer-mult-bounds/pull/932)), and their predecessors.
The alternating arbitrary-depth bi-forest starting method credits **Stephan
Arrington** ([PR1080](https://github.com/CrocSwap/integer-mult-bounds/pull/1080)).
His historical two-sided cleanup method is
[PR1119](https://github.com/CrocSwap/integer-mult-bounds/pull/1119).
Copy/unit lowering credits **Sagar Thakrar**
([PR696](https://github.com/CrocSwap/integer-mult-bounds/pull/696)).
Same-word gauges credit **woklerx** (PR1161), **Hanson Sun / bbMisk** (PR1214),
**Sagar Thakrar** (PR1259), **Philipp / mightyOil** (PR1263), and **Cinna Davis /
1337isnot1337** (PR1353, PR1369 and PR1388). The nineteen-menu composition
credits **George Lydakis / lydakis** (PR1979), with its retained
[original notice](comparators/pr1979/NOTICE.md).
Related dyadic forest bounds and jointly restored two-target shears credit
**woklerx** ([PR961](https://github.com/CrocSwap/integer-mult-bounds/pull/961),
[PR1011](https://github.com/CrocSwap/integer-mult-bounds/pull/1011)); the historical
helper-butterfly extension is [PR1116](https://github.com/CrocSwap/integer-mult-bounds/pull/1116).
Those bounds and recipes are not audited or corrected here.

The selected R480 data retain **Rohan Arun / PR1094**, **Jeremy Kothe / PR1087**,
Douglas Colkitt's frontier selection, icekylinx's compiler/emitter/Horner lineage,
DreamingOfClouds' native frame/wrapper replay, and all E8/k8/T16 predecessors.
Native source headers remain verbatim; the retained
[upstream notice](reference/UPSTREAM-NOTICE.md) preserves their notices.

Substantial **OpenAI Codex assistance** was used in research, synthesis,
implementation, both checking methods and writing.
Donor-supplied read-only review feedback informed these revisions; its reviewer/model
provenance is not confirmed. No subagents or independent human review is claimed.
New material is Apache-2.0 under
[LICENSE](LICENSE).
