# Selected K492 helper-count audit

**Research audit / independent finite recount; no new kappa.** All 14
`assemble.*` substitutions in the selected construction's
[PROOF-NOTE-R](../complex-k492-owner-repair/PROOF-NOTE-R.md) now have a portable,
source-pinned replay. Thirteen stale-count/index substitutions fail at their
specified assertion. The equivalent `9*504` parent-bank substitution reproduces
the entire selected assembly receipt. No defect is found in these current
assembly checks.

The [maintainer review](../../docs/research/community-k492-review.md) explicitly
excluded the original author's unavailable 32-site scratch reversion suite.
This package supplies new coverage for its **14 assembly-side sites only**,
using the selected #626 fixture. It does not claim to recover that script,
reproduce the other 18 sites, or repeat its R=504 compatibility fixture.

## Reproduce

From any directory, with Python 3.11 or later and only its standard library:

```sh
python3 -I -B research/k492-helper-accounting-audit/verify.py
```

Use an absolute script path when outside the repository. Expected output:

```text
PASS_SCOPED_K492_HELPER_ACCOUNTING_AUDIT documented_sites=14 rejected=13 equivalent=1 additional_source_controls=2 audit_controls=8
```

The command checks all immutable source pins, independently recounts the finite
inputs, executes the full unchanged assembly and all source controls, and
compares the deterministic result to [EXPECTED.json](EXPECTED.json).
`--output /tmp/k492-audit.json` writes a fresh receipt instead of comparing it.
No repository artifacts are regenerated. Optimized Python (`-O`) is explicitly
rejected before replay because the imported production code requires assertions.

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Selected #626 source: `660de893d27bb7abd1d5b01b1640207528a5c851`.
The unchanged selected saving is
`51110230636731/31250000000000000 = 0.001635527380375392`.
[SOURCE.json](SOURCE.json) pins every consumed repository input and executable
dependency, with the selected dependency heads. [CLAIM.json](CLAIM.json) records
OS-random assignment seed **73**, three candidate tasks and the local claim;
no pinned or other sprint coordination issue was available.

## What the recount establishes

The two counts have different meanings: R=492 is the helper count of an executed
provider, whereas R0=504 belongs to the retained parent geometry. Both CK and
JP8 have `2*112+492 = 716` native columns. Independent binary elimination checks
that the stored frames are bases; their ranks give every helper's start and end
dimensions. For each provider the conservation identity is

    sum(helper widths) = 9R - sum(start ranks) - sum(9 - end ranks).

The exact totals are:

| Provider | Helpers | Entrance rank | Terminal codimension | Width sum | Local adapters |
|---|---:|---:|---:|---:|---:|
| CK | 492 | 424 | 146 | 3858 | 426400 |
| JP8 | 492 | 380 | 146 | 3902 | 437040 |

Every literal `(stage, replica, helper)` role occurs exactly once, and its width
matches the native word: `9*8*492 = 35,424` roles. This is a count/width check;
it is not another owner-window or physical-chart proof. The helper map is a
bijection after the twelve removed parent registers are excluded. Translating
the old helper indices `(270,282,294,306)` through the **absolute-register** map
gives `(264,276,288,300)`, all width eight. The old indices have widths
`(7,8,9,7)` in CK and `(8,9,9,8)` in JP8, so retaining them is not equivalent.

The recount reads all four native `LOCAL-PROGRAMS` orientations. For a scalar
addition with reduced coefficient `n/2^e`, the retained implementation clears
coefficient work, performs `bit_length(|n|)-1` doublings and `popcount(|n|)`
additions, halves e times, accumulates with sign and clears the work. Its cost
per real component is therefore

    bit_length(|n|) + popcount(|n|) + e + 2.

The new implementation uses this closed formula rather than executing the
production Horner accumulator. It also counts scales, copies, clears, recursive
children and both wrapper endpoints. The complex charge is twice the real
charge. This verifies a count for the **retained implementation**, not minimal
scalar cost, an l1 prefix bound, or scalar endpoint correctness.

The selected physical stock is `7168+492+8+2 = 7670`. The parent remains
`7168+9*504 = 11704` live rows and `11704+504+8+2 = 12218` physical rows.
The resulting finite parent-envelope price is `1833791190783112`, and its
rebased value is `1833791190482956`. The inherited parent idle count of 16,128
is consumed from the pinned owner receipt; this audit does **not** reconstruct
the omitted parent `GLOBAL-TEMPLATE` or establish that idle count independently.

Writing `C = 64*74^3 = 25934336`, two illustrative exact deltas are:

* Using R0 instead of R for two-way helper routing adds
  `8*C*2*72*(504-492) = 358516260864`.
* Using R instead of R0 for the nine parent banks omits
  `8*C*9*(504-492) = 22407266304`.

The first is an **overcharge**, rejected because it disagrees with the fixed
receipt. Its rejection does not show that a larger conservative allowance is
mathematically invalid. The second undercounts the retained parent envelope.
Neither experiment changes the selected construction or proves a new bound.

## Source controls and their limits

Each mutation replaces one unique executable substring in memory, leaving the
fixture unchanged. A rejection counts only if it is an `AssertionError` at the
specific expected line in that mutated source. Imports, malformed fixtures,
unrelated assertions and unexpected acceptance fail the audit. The 14 control
names must equal the 14 `assemble.*` rows parsed from the pinned proof note.

The baseline and every accepted control run the complete production assembly:
provider admission, finite guards, both rational moment engines, conservative
and native endpoints, outer inequalities and the assembly's own endpoint/grid
controls. Their **entire returned JSON objects** must equal the selected
`ASSEMBLY.json`, allowing only JSON's conversion of integer object keys to
strings. No production assertion is removed or replaced with a stub.

Two extra source controls reject `9*R` for the parent-bank charge and accept
the equivalent `R=504-12`. Eight harness/recount controls cover a stale native
helper count, dependent frame basis, missing/duplicated roles, wrong widths,
source corruption and absent/ambiguous mutation anchors. Two exact toy prices
also check the signed multibit Horner formula and its extra-halving charge.

This is a bounded audit, not a search: all fourteen specified sites, the two
selected providers and both orientations are covered, then execution stops.
Seed 73 selected candidate index `73 % 3 = 1`; it is not a claim of independence
by itself. Finite replay is not a formal proof of the multiplication theorem.
The archived local algebra/frame/phase/restoration receipts remain inherited;
the suppliers are not cold-rebuilt. Uniform compilation, common-label and
mutable-basis realization, pooled hosting, normalized residuals, precision,
tape and analytic transfer remain conditional. This addition does not require
or claim a repository-wide `make verify` or `make frontier626-verify` rerun.

## Validation record

Local verification on 2026-10-13, macOS / CPython 3.11.5:

* The reproduction command above matches the committed deterministic receipt.
* The existing, unchanged `code/assembly_controls.py` passes all **114**
  admission rejection controls on these selected owner/invoice inputs and the
  pinned `vendor/multicold` dependency.
* `make selected-record-check` passes.
* A minimal export containing only this package and its 23 pinned input files
  passes when invoked by absolute path from `/tmp` with isolated imports.
* Corrupted expected-receipt and source-file exports fail as intended; the
  source corruption is rejected before execution. A `-O` export invocation
  fails explicitly. `git diff --check` passes.

These are local results. No remote CI result or cold supplier reconstruction
is claimed. The exported-input and corruption tests use temporary directories;
no frozen source or selected certificate is edited.

## Concurrent work and credit

During the final overlap check, Sagar Thakrar / @thakrarsagar's
[PR #724](https://github.com/CrocSwap/integer-mult-bounds/pull/724), pinned at
`624ccfe44b1c5816f0279481d91cca6a5a2290ab`, had already supplied an independent
R/R0 invoice audit and resolved the proof note's introductory pass/fail
contradiction. Its route and parent-bank deltas agree with this recount.
Those conclusions are corroboration, not a priority claim.

The distinct coverage here is the **complete 14-row assembly reversion table**,
including provider-column, width, local-adapter and mapped-index assertions
outside #724's accounting slice; execution of the **whole assembly** on the
baseline and equivalent controls; and fresh closed-form operation counts from
the four local programs rather than using their invoice totals as inputs.
No #724 implementation is imported. #675's owner timing/bridge audit, #706's
independent moment bounds and #729's helper-frame lifetime audit concern other
obligations and are not dependencies of this result.

Jeremy Kothe / jeremykothe2 and the credited GlobalR/AtomReviewer and other
Claude research agents supplied #622's K-triangle construction, R generalization
and original reported scratch controls; Jeremy also supplied #623's dispatch.
Chafik Boukhalfa / chafreaky supplied #626's owner repair and portable checks.
Douglas Colkitt supplied the maintainer review and archived replay evidence.
DreamingOfClouds' cold-helper construction, Rohan Arun's #559 recurrence
correction, eumemic's #543 bit supplier, icekylinx and the full retained
compiler/accounting lineage retain credit. Their notices remain unchanged.

Prepared by **Gabriel Roa / @gaboroa14**, with substantial **OpenAI Codex**
assistance in selection, design, implementation, analysis, verification and
writing. No independent human peer review or proof-assistant certification is
claimed. New files are Apache-2.0, under the repository license.
