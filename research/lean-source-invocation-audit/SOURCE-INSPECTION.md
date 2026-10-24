# Source invocation inspection

The exact source is PR442 at `4e16d001d505d4f21dd2bcfc44591f9be4c279bd`,
retaining PR434's R747 bit word. Full hashes, owner rows, frame data, and
scope notes are in `invocation-source.json`. The inputs come from the fresh
local PR442 replay recorded in the preceding package's
[repository checks](../lean-whole-residual-hosting/repository-checks.json).
Its source-window [receipt](../lean-whole-residual-hosting/source-check-result.json)
records the same hosted-template JSON hash as `invocation-source.json`.

## Actual word and selected call

Use **stage 2, replica 0, pair 0, forward**. It has 987 live registers:
120 sources, 120 targets, and 747 dirty helpers. Register 987 is a private,
initially-zero temporary used in nine COPY/ERASE episodes.

The literal forward word has 19,002 events: 4,291 MOVEs, 14,693 ADDs,
nine COPYs, and nine ERASEs. Compact forward JSON SHA256 is
`4ed9ed1f7756ea6ff2c299b61ed1dc3fe0fa5bbbb91b5170133596b452c8085e`;
the original six-int records SHA256 is
`99cb283793818ad03f8f16f95a8eb23d0b18769d0657d58043fb7a427471c35d`.
No event is omitted from the Lean data projection; MOVEs remain normalized
scalar no-ops, with their physical meaning a separate obligation.

| Helper | Register | Start/end frames | Hosted owner | Parent owner |
| --- | ---: | --- | --- | --- |
| 0 | 240 | 0 / 1 | `[507,["hosted",2,16,8]]` | `[9142,["bank",56,8]]` |
| 1 | 241 | 0 / 1 | `[508,["hosted",2,0,8]]` | `[9143,["bank",56,8]]` |
| 2 | 242 | 0 / 1 | `[508,["hosted",2,8,8]]` | `[9144,["bank",56,8]]` |
| 3 | 243 | 0 / 1 | `[508,["hosted",2,16,8]]` | `[9145,["bank",56,8]]` |

Frame 0 is the empty basis, dimension zero. Frame 1 has basis `2 I_8`,
dimension eight. Both selected helpers 0 and 3 therefore have declared
rank-eight residuals. Family 507 is pair 2/side 0/port 27; family 508 is
pair 2/side 0/port 28. The parent call names neither family. The hosted call
has 747 hosted helper owners on 317 different families.

## What the independent checker establishes

`research/lean-source-invocation-audit/check_source.py` reconstructs the
literal forward events from the binary records, compares both templates,
checks the exact selected owners and empty/full frames, and binds every
generated Lean event in all 96 chunks to the original word.

Its independent Python interpreter replays all 987 input basis columns.
Every source/helper row is restored; target row `i` is
`e_i XOR e_(i-120)` for `120 <= i < 240`; the temporary returns to zero.
It checks current frames, equal-frame ADDs, immutable open centers,
clean COPY inputs, matching ERASE centers/frames/values, and final frames.
The private temporary is not included among arbitrary dirty inputs.

This all-column replay is Python evidence, not a Lean physical semantics
theorem. The separate generated Lean proof checks its stated zero and
helper-3 input trajectories. No particular small address field is assumed
admitted. Source-checker controls reject omission of helper 3's actual final
cleanup (event 18730), omission of the first actual COPY, and alteration of
the first literal Lean ADD.

## Precise single-host scope failure

The current `PhysicalContract` requires original `e.base` and relocated
`e.hosted` to have the **same map on retained `R`**. Only the distinguished
host stream may differ. Take that host to be family 507 and retain family
508 in `R`.

Under the source's written geometry endpoint semantics, the parent call
fixes family 508, whereas the hosted complete sweep applies its factors on
`[0,24)`. A payload reading the first half of coordinate 16, at an address
whose two halves there differ, distinguishes those outputs. The factors on
`[0,16)` do not affect this witness. At one fixed cover invocation, helper
3 supplies the corresponding difference at `(508,d sigma_3^-1)`.

Thus the wholesale parent-to-hosted call cannot instantiate that single-host
contract while retaining family 508. This diagnoses our interface's scope;
it is not a counterexample to whole-residual hosting. A multi-host contract,
or an explicit sequence of one-helper relocations holding every other
placement fixed, is needed for the full layout change. Dropping family 508
from `R` would leave that data family's endpoint uncertified.

The source emits owner selectors and a written isometry recipe, not
numerical helper `sigma` matrices. Exact physical MOVE lowering, owner-chart
injectivity, and transport of the residual to the selected mask are still
separate obligations. The failure inference above is conditional on those
written geometry endpoints; the normalized instruction certificate does
not silently discharge them.
