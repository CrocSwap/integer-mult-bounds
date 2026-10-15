# Independent reconstruction of the eight K492 emitter controls

This package reconstructs and executes **all eight `emit.*` source-site controls**
listed in [`PROOF-NOTE-R.md`](../complex-k492-owner-repair/PROOF-NOTE-R.md), on the
retained #626 fixture selected at the historical source baseline. The fresh
unmodified emitter reproduces the retained `HOSTED.json` exactly. Five source reversions fail at their intended
emitter statements, two produce artifacts that the independent checker rejects,
and the cosmetic label reversion passes with only its label and directly derived
template digest changed. Eighteen additional semantic corruptions are rejected
after refreshing output hashes; two positive controls pass.

The scientific source baseline is `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Publication preparation uses integration base
`ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`; all 24 pinned inputs are identical at
both commits. #626 is a historical checkpoint, not the current selected frontier.
Existing construction code, input data and selected records are unchanged.
This is a finite verification contribution with no new multiplication bound.

## Exact obligation and boundaries

The provider count is `R=492`; the fixed parent's count is `R0=504`. The checked
contract connects those distinct quantities to the serialized emitter output:

1. The two native provider words have 224 data columns and 492 helper columns.
   Each residual width is the exact binary rank of the terminal frame minus the
   entrance rank. Both frames are independent, and the entrance is contained in
   the terminal span.
2. The literal allocation has one role for every element of
   `{0,…,8} × {0,…,7} × {0,…,491}`. Each invocation owns 716 distinct live
   families, with its first 224 data owners preserved.
3. Each helper's family, width, offset, residual coordinates and spectator
   coordinates match the independently reconstructed source allocation and
   frames. Sorted occupied intervals partition each consumed idle prefix.
4. Physical storage and its disjoint namespace use the provider count:
   `7168+8+492+2=7670`. The parent remains at 11,704 live and 12,218 physical
   rows, with stock gap `8+504+2=514`.
5. The output preserves the pinned parent's unchanged fields, expands its event
   blocks in the selected complete-call order, binds every provider artifact and
   source file, and contains the exact remaining idle suffixes and paid profile.

`independent.py` imports **only Python's standard library**, not the primary
emitter, audit, invoice, assembly, witness or generated-identity modules. Binary
Gaussian elimination and sorted interval endpoints supply independent checks of
the rank and partition statements. Exact orthogonality uses integer bit parity.
The primary emitter still runs as the implementation under test, in a separate
process; its only local import is the pinned `witness.py` loader.

This contract checks unchanged controller expansion and allocation structure.
It **does not re-prove** source owner-window feasibility, bridge timing, local
scalar identities, Clifford phases, normalization wrappers, or the validity of
the retained source native receipts. Those are inherited inputs. Informational
prose such as the version, loop-order description, helper-route description,
provider-dispatch description and receipt scope is not treated as executable
proof data. The code checks the underlying structures stated above.

The unavailable original `Stack492/revert_controls.py`, `REVERT-492.json`,
`REVERT-504.json` and `GlobalR/run504b` fixture are not claimed to be recovered.
This is a new reconstruction on the retained selected R492 fixture. It does not
execute the other 24 source rows, the R504 suite, invoice/assembly inequalities,
or a full cold provider rebuild. All-size compilation, mutable-basis realization,
whole-call hosting, precision/tape/exact recovery and analytic transfer remain
outside this finite check. No optimality, practical speedup or full theorem proof
follows from these results.

## Reproduce

From the pinned repository root, with Python 3.10 or later and no third-party
packages:

```sh
python3 -B research/k492-emitter-independent-controls/run.py --out /tmp/k492-emitter-review
```

The output directory must not already exist. Expected final line:

```text
PASS_COMPLETE_EIGHT_EMITTER_SITE_SLICE
```

The command checks all 24 input pins before copying the fixture into the output
directory. It runs nine local emitter processes: the baseline and eight exact
single-site reversions. A reversion anchor must occur exactly once. Expected
primary failures must have the specified exception class **and terminal emitter
source line**; missing files or unrelated assertions do not count as rejections.
No network, solver, paid API or external executable is needed beyond Python.

`INPUT-PINS.json` records immutable raw hashes and decompressed payload hashes.
Each run writes Python/platform/zlib details, checker and harness hashes, actual
commands, exit statuses, stdout/stderr digests, exact source patches, baseline
artifacts, semantic mutation recipes, and machine-readable results. Seconds and
absolute command paths are execution metadata; exact mathematical equality uses
the full decompressed JSON or explicitly identified semantic fields. Regenerated
gzip container hashes are not cross-environment acceptance criteria.

## Fixture provenance

The selected emitter and witness loader come from
[`complex-k492-owner-repair/code`](../complex-k492-owner-repair/code). `SPEC.json`
and `OWNERS.json.gz` are that package's unchanged selected data. The rebound plan,
two seven-artifact provider sets, parent canonical word and data-phase file come
from the retained [`community-k492-audit/pr626/replay/mixed-global`](../community-k492-audit/pr626/replay/mixed-global).

That retained directory omits its large parent global-template container. The
identical payload is present at
[`structural-gain/frontier-composition/global-replay/base/split-centres/GLOBAL-TEMPLATE.json.gz`](../structural-gain/frontier-composition/global-replay/base/split-centres/GLOBAL-TEMPLATE.json.gz).
Its decompressed SHA-256 is
`7db047a427a7979d69e163c78a1e32bd445628fb86723e131a3138361355a9c3`, exactly the
`parent_template_sha256` in the selected retained `HOSTED.json`. This is an
identified retained payload, not a synthetic parent. The raw container is also
pinned. The baseline then reproduces the **entire** retained `HOSTED.json`.

## Exact results

| Quantity | Independently reconstructed value |
|---|---:|
| Provider helper count / fixed parent helper count | 492 / 504 |
| Provider helper frame pairs checked | 984 |
| Call/helper roles | 35,424 |
| Owners per invocation | 716 |
| Live / physical rows | 7,168 / 7,670 |
| Parent live / physical rows | 11,704 / 12,218 |
| Entering helper roles | 16,368 |
| Cross-replica helper roles | 28,404 |
| Idle remainder children | 2,339 |
| Actual 73-column charts | 7,672 |
| Binary Gram-matrix entries checked | 596,848 |
| Rank mass / deficit | 520,704 / 2,560 |

The exact private intervals are centres `[7168,7176)`, helper tableau
`[7176,7668)`, and coefficients `[7668,7670)`.

The paid profile is
`{1:181659, 2:30016, 3:31104, 4:11520, 5:5040, 6:576, 8:576, 37:1, 48:2215}`.
It is recounted from literal local-program events and the reconstructed idle
suffixes, rather than accepted from a printed total. Native width histograms are
`ck={4:30,5:48,7:68,8:92,9:254}` and
`jp8={4:30,5:48,7:36,8:112,9:266}`.

The fresh template's canonical JSON SHA-256 is
`22b41c45fdac1dcc7495311fe701f4697219654843558785ed72fae91df531b0`.

| Source control | Observed outcome |
|---|---|
| `emit.R_from_providers` | `IndexError`, emitter line 42: a 504-helper range indexes the 492-helper word |
| `emit.roles_72R` | `AssertionError`, line 48: 35,424 roles do not equal 36,288 |
| `emit.widths_range` | `IndexError`, line 42: stale width range indexes past the word |
| `emit.all_helpers_owned` | `AssertionError`, line 77: helper domain 0–491 differs from 0–503 |
| `emit.physical` | Emitter succeeds; independent `emit.physical` rejects 7,682 instead of 7,670 |
| `emit.reserved_tableau` | Emitter succeeds; independent `emit.reserved_tableau` rejects endpoint 7,680 instead of 7,668 |
| `emit.parent_R0` | `AssertionError`, line 93: parent gap 514 differs from `8+492+2=502` |
| `emit.version_label` | Accepted; only `GLOBAL-TEMPLATE.version` and `HOSTED.template_sha256` differ |

The proof note's general sentence saying R0 controls should pass is imprecise
for `emit.parent_R0`: that particular mutation replaces the required R0 with R.
Its table and evidence correctly expect rejection, which this run reproduces.
The separate `assemble.parent_banks` identity control is outside this slice.

The eighteen semantic mutations cover wrong physical/tableau sizes, truncated
helper domain, family aliasing, a private family used as a live owner, false
provider R or widths, wrong residual width or spectator, omitted role or idle
remainder, changed source-event order, provider artifact link corruption, changed
retained recipe/call window, erased async parent schedule, an empty input-binding
inventory, and a false input digest. Each template-changing control recomputes
the template digest and summary digest before checking. Summary-only binding
controls retain the correct template digest and refresh the summary digest.
Source inputs remain fixed and pinned. Rejection obligations are recorded, so a
digest mismatch or unrelated exception cannot substitute for the intended check.

The positive controls accept a cosmetic label change and actual gzip
recompression with a different timestamp/compression level. The source label
reversion is additionally compared after normalizing **only two exact fields**;
there is no blanket removal of hash or metadata fields.

## Evidence and independent review

[`evidence/RESULT.json`](evidence/RESULT.json) is the machine-readable outcome.
[`evidence/BASELINE.json`](evidence/BASELINE.json),
[`evidence/SOURCE-REVERTS.json`](evidence/SOURCE-REVERTS.json), and
[`evidence/SEMANTIC-CONTROLS.json`](evidence/SEMANTIC-CONTROLS.json) contain the
exact counts, eight source receipts, and twenty semantic/positive control
recipes. Each source case retains its command, stdout/stderr and exact patch;
successful emitters retain their generated artifacts. Input fixtures and copied
source files can be regenerated from the pinned source inventory. The separate
review and fresh rerun are recorded in [`REVIEW.md`](REVIEW.md).
Publication path normalization and the additional validation run are documented
in [`PUBLICATION.md`](PUBLICATION.md).

## Prior work and attribution

This adds the eight non-assembly emitter sites excluded by
[#766](https://github.com/CrocSwap/integer-mult-bounds/pull/766). It does not repeat
that PR's all-fourteen assembly-site suite.
[#724](https://github.com/CrocSwap/integer-mult-bounds/pull/724) already supplies
related invoice/assembly R/R0 accounting evidence and identifies the parent-R0
conceptual distinction; the contribution here is execution of the actual emitter
sites with an independent output oracle.
[#675](https://github.com/CrocSwap/integer-mult-bounds/pull/675) concerns source
controller windows and bridge timing, which remain inherited here. The overlap
review originally screened 623 unique open PRs in 624 raw inventory rows; that
historical snapshot is retained in `OVERLAP.md`.
[#780](https://github.com/CrocSwap/integer-mult-bounds/pull/780) independently checks
the same checkpoint's owner footprints with sorted interval endpoints, and
[#727](https://github.com/CrocSwap/integer-mult-bounds/pull/727) optimizes the related
occupancy check with bitmasks. The interval technique is not claimed as new here;
the contribution is the complete eight-emitter source-control reconstruction and
its separately expressed output contract. Overlap screening is a scoped snapshot,
not a guarantee against concurrent or unpublished work.
[#819](https://github.com/CrocSwap/integer-mult-bounds/pull/819) supplies related
gzip-portable native-owner binding; gzip-insensitive comparison is likewise not
claimed as a new technique. The publication refresh screened 767 open and 383
closed PR titles/bodies and is recorded alongside the original overlap audit.
The source heads and precise overlap boundaries are in [`OVERLAP.md`](OVERLAP.md).

K492 suppliers and the R generalization retain Jeremy Kothe / `jeremykothe2` and
the GlobalR, AtomReviewer, AtomScout, Stack492, Port480 and ColdBeyond credits.
The selected owner allocation retains Chafik Boukhalfa / `chafreaky`'s #626 credit,
the #623 dispatch/seed-map credit, GamingPuzzled's owner-headroom lead, and all
DreamingOfClouds / earlier-source attributions in the original
[`NOTICE.md`](../complex-k492-owner-repair/NOTICE.md). No source notice is replaced.

The independent reconstruction and adversarial-hash methodology was informed by
the pinned [Krenn independent verifier](https://github.com/brianross93/Krenn/blob/ab446724a61a293a3268c63b9e9e721c6a360561/experiments/krenn_quantum_graph/independent_verifier.py)
and [ThetaTwist exact derivation](https://github.com/brianross93/thetatwist/blob/b4ec6c13088b89961834cc675b44b81372199b02/PROOF.md).
No theorem or result from those unrelated systems is imported into this check.

Prepared for Brian Ross with substantial OpenAI Codex / GPT-6 Astra assistance,
including a separate Astra code review and rerun. This is AI-assisted independent
implementation evidence, not a claim of human peer review. New files use the
repository's Apache-2.0 license.
