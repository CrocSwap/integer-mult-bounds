# Independent JP8 scalar restoration check

The selected #626 JP8 scalar programs have the expected endpoint maps on all
716 persistent registers and eight arbitrary incoming private-centre registers.
A new exact reverse-mode checker verifies every output coordinate in both
orientations, using only Python's standard library. It imports no constructor,
production auditor, or finite-field helper.

There is a concrete coverage difference. Removing backward event **13113**, the
initial `C0` clear, preserves every ordinary input column and leaves all private
outputs zero. It nevertheless sends an incoming `C0=1` to **107 nonzero persistent
outputs**, including `L0=-1` and `L224=-1`. The certificate records the entire
rank-one defect. The original program passes the stronger check.

Status: **independent finite verification**, with no new kappa claim. At the exact
base `66849e1475c930fd7732b1a0067ffee7e1e95f60`, the selected conditional witness is
`51110230636731/31250000000000000 = 0.001635527380375392`, #626 with #543.

## Reproduce

From the repository root, with Python 3.11 or later:

```sh
python3 -I -B research/jp8-adjoint-restoration/verify.py
```

Expected final line:

```text
PASS_JP8_ADJOINT_RESTORATION outputs=724x2 inputs=724 controls=6 kappa=unchanged
```

`--report` prints the recomputed certificate after comparing every field with
[EXPECTED.json](EXPECTED.json). The command is offline, writes no outputs, and
works with `-O`. It takes about four seconds on the recorded macOS environment.
[VALIDATION.json](VALIDATION.json) records the measured checks, not a benchmark
claim or a Linux CI result.

[SOURCES.json](SOURCES.json) pins the selected record, its source inventory, the
actual #626 SPEC, and the predecessor checker and emitter. The verifier follows
the selected record to its inventory, checks that inventory's SPEC hash, and
checks the SPEC's whole-artifact and per-orientation program hashes. The two
gzip inputs use decompressed payload hashes, so changing gzip timestamps or
compression streams does not change mathematical equality. No receipt's PASS
field is taken as evidence for the new endpoint calculation.

## Statement and method

Write the persistent input as `x,y,h`, with 112 sources, 112 targets, and 492
helpers. Write the eight private-centre inputs as `c`. The scalar projections
of the literal emitted programs satisfy

```text
forward:  (x, y, h, c) -> (x,   y+x, h, 0)
backward: (x, y, h, c) -> (x-y, y,   h, 0).
```

Every coordinate is arbitrary. In particular, all 492 helper values are
restored and all outputs are independent of incoming `c`.

For a scalar operation matrix `A` and an output functional `w`, substituting
the operation into the functional gives `A^T w`. If the forward program is
`A_m ... A_1`, processing operations in reverse order computes
`A_1^T ... A_m^T w`. Starting with every output basis functional therefore
computes every row of the complete program matrix. Clear and copy are handled
by substitution; they are not assumed invertible.

| Literal operation | Pullback of the functional coefficients |
|---|---|
| `target += q * source` | `w[source] += q * w[target]` |
| `target *= q` | `w[target] *= q` |
| `target = source` | Transfer `w[target]` to `w[source]`, then remove `w[target]` |
| `target = 0` | Remove `w[target]` |

The parser rejects same-register add/copy operations, unknown scalar operations,
invalid register indices, zero denominators, and primitives outside the pinned
dyadic contract. Exact `Fraction` arithmetic prevents rounding or tolerance
acceptance. Both orientations have 22,693 scalar operations. The checker proves
1,448 output-functional equalities, each on 724 possible input coordinates.
The resulting matrices each have 828 nonzero entries.

The implementation differs from the predecessor `hpe_emit_local.check_local`
and `hpe_audit_local.local`: those propagate all live input rows forward through
the stream. This checker propagates one output functional at a time backward.
It also includes incoming `C` coordinates, whereas the predecessor scalar
endpoint routines initialize only `L` coordinates. A small fixed algebra check
covers all four operation types. Each reported omission witness is separately
executed as a scalar basis-vector input in forward time, for both the intact
and damaged streams.

## Exact negative controls

All event indices below are zero-based indices in the pinned emitted event
arrays, including nonscalar events. Delete exactly the named event and set only
the indicated input coordinate to one.

| Omission | Direction / event | Input | Observed output | Required value |
|---|---|---|---|---:|
| First compensation addition | forward / 169 | `L224` | `L113 = -1` | 0 |
| First early cleanup addition | forward / 17243 | `L0` | `L448 = 1` | 0 |
| First full cleanup addition | forward / 18676 | `L8` | `L489 = -1/4` | 0 |
| First centre copy | forward / 13114 | `L0` | `L112 = 3/4` | 1 |
| Final `C0` clear | forward / 13144 | `L0` | `C0 = 1` | 0 |
| Initial `C0` clear | backward / 13113 | `C0` | `L0 = -1` | 0 |

For the last control, the checker does more than find one witness. It recomputes
all 724 output rows and verifies the exact formula

```text
damaged_program - intact_program = d * e_C0^T,
```

where `d` is the complete 107-entry vector in
`EXPECTED.json:dirty_centre_gap.nonzero_output_coefficients`. All entries outside
those persistent output rows are zero. This certifies that the damaged and
intact programs agree on **all 716 ordinary input columns**, not merely on one
test input. They also both clear their private outputs. An endpoint test with
private inputs fixed to zero cannot detect this omission. A separately executed
call to the pinned predecessor's `local()` routine confirms acceptance of that
restricted endpoint test; see the validation record.

This does not show that full production admission accepts the damaged artifact.
Its source hashes and event-order checks are separate obligations. Nor does it
show a violated predecessor promise about dirty private inputs. The new result
states the stronger scalar property and makes the distinction reproducible.

To reproduce the predecessor comparison from the repository root, run this
separate command **without `-O`**, so the predecessor's assertions remain active:

```sh
python3 -B - <<'PY'
import copy
import hashlib
import json
import sys
from pathlib import Path

if sys.flags.optimize:
    raise RuntimeError('Predecessor assertions must be enabled')
source = Path('research/complex-k492-owner-repair/code/hpe_audit_local.py')
provider = Path('research/community-k492-audit/pr626/replay/mixed-global/base/providers/jp8')
pins = json.loads(Path('research/jp8-adjoint-restoration/SOURCES.json').read_text())
if hashlib.sha256(source.read_bytes()).hexdigest() != pins['files_sha256'][str(source)]:
    raise RuntimeError('Changed predecessor source')
sys.argv = [str(source), str(provider)]
namespace = {'__name__': 'predecessor_comparison'}
# This unique boundary excludes the reporting and output-writing driver.
prefix, _ = source.read_text().split('profiles={};checks={}')
exec(compile(prefix, str(source), 'exec'), namespace)
events = copy.deepcopy(namespace['ir']['local_programs']['backward'])
if events[13113] != ['scalar', ['clear', ['C', 0]], 0]:
    raise RuntimeError('Changed event position')
del events[13113]
_, result = namespace['local'](events, True)
print(result['all_exact_columns'], result['private_work_erased'])
PY
```

Expected: `716 True`. This calls only the historical local routine on an
in-memory mutation, not its full admission driver. It writes no source files
or receipts. The primary verifier above independently establishes the whole
restricted-map equality without executing the predecessor.

## Scope, provenance, and limits

This is a complete exact check of the two fixed finite scalar projections. It
is not a sampled search, a formal proof-assistant development, or a proof of the
full integer multiplication theorem. No construction search was run. Seed 79
selects JP8 from the two selected suppliers; it does not determine randomized
test inputs. Coverage ends after all output rows, six specified omissions, and
the complete one-clear defect are checked.

Frame changes, centre transport, and ordinary/residual adapters are recognized
metadata events and are excluded from the scalar map. Their geometric and
operator semantics are inherited. The check does not rerun wrapper amplitudes,
all-size compilation, common-label or mutable-basis realization, whole-call
hosting, coefficient-work implementation, prefix bounds, costs, moments,
precision/tape/recovery, analytic transfer, or outer assembly. Arbitrary scalar
centre inputs do not by themselves prove a dirty physical centre interface.
The selected frontier and all existing files remain unchanged.

Credit belongs to Jeremy Kothe's #622/#623 K-triangle and supplier work,
Chafik Boukhalfa's #626 selected allocation/package, DreamingOfClouds' independent
scalar auditor and cold-helper work, icekylinx's emitter/compiler lineage,
Dugongue's scalar ancestry, eumemic's #543 bit supplier, Rohan Arun's recurrence
work, and the predecessors retained in their notices. The selected construction
and review are linked by
[the selected record](../../certificates/selected-result.json) and
[the maintainer review](../../docs/research/community-k492-review.md).

The overlap review considered #646/#683/#687 on K-triangle schedules,
#702/#712 on wrapper amplitudes, #692 on weighted-stride duality, and #675 on
owner timing versus scalar bridges. A refreshed 553-PR queue through #734 also
included #722's JP8 coefficient-work sharing, #729's frame-lifetime audit, and
#734's bounded signed-Horner lowering. **Concurrent #734 already includes
arbitrary private inputs in its forward primitive replay.** This package adds
a reverse-mode implementation for the original selected scalar stream and the
complete rank-one clear-omission defect. It makes no priority claim for private
input coverage. These results are compatible; no pending patch is imported or
used as a dependency. The immediate pre-submission refresh through #743 found
no later submission on this same endpoint/omission obligation. The local
[sprint claim](CLAIM.md) records the seed, alternatives, timing, and absence of a
pinned coordination issue.

Prepared for **Sagar Thakrar (@thakrarsagar)** with substantial OpenAI Codex
assistance in research, implementation, exact checks, review, and writing. A
separate Codex worker checked the mathematics and concrete counterexamples;
this is not independent human peer review. New code and prose are under the
repository's Apache-2.0 license. No predecessor license or attribution is
replaced.
