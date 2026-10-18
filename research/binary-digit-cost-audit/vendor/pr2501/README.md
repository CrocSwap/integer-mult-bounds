# Complete selected BIT residual traces

We connect the full good and fallback adapter words to binary coefficient
evaluation, serialized leaf children and one shared stream trace. PR2449
implemented the first-column head callback. Here we retain later-pivot
chronology, fallback permutation snapshots, physical orientation and the
complete adapter/child/inverse sequence.

The trace carries coefficient references, not values captured from one high
header. Each stream pass prepares its coefficient from the current raw prefix.
The packet interpreter visits all prefixes for each primitive and enters each
child once for the whole packet. Leaf children execute atom swaps, ADDs and
signs; they use no weighted-swap oracle.

[PROOF.md](PROOF.md) gives the normal-form refinement, child/source contract,
binary cardinality invariants and local `C_q V(n+w)` bill under the retained
root coupling. We require every child width to be below 64. Larger recursive
children, the selected directory producer and the full family/owner/global
caller remain open. We retain the selected frontier and claim no new exponent.

## Evidence

We check the actual selected COPY510 and nonidentity owner MOVE sources on
640 address columns across four complete operator cases. These include a
two-column fallback with 32,891 child invocations, a later-pivot example over
`Z/25`, and nonconstant generated ancestor weights. We compare with the direct
raw-projector operator, independently of the normalizer tables and trace.

We also execute these complete Boolean streams with binary counters and
fixed-radix digit passes:

- Good and fallback four-atom residuals, each with 26,244 payload bits and
  arbitrary outer/within-block spectators.
- A six-atom embedding with 2,916 bits, checking the unused middle.
- All 81 high lifts over one fixed GL2 low class, with 531,441 payload bits,
  2,430 fresh coefficient preparations and one child entry/return.
- A two-header fallback packet, checking that its child count stays shared
  across the headers. This sampled packet is not a complete fallback high cube.

For those streams we check the source coordinate of each output bit, preserve
input/directory contents and audit erased scratch. Separate checks compare
eleven actual serialized child evaluations with the local formulas, retain
parent records through sibling calls, and obtain head coefficients `[0,6,3]`
from three high lifts of the same selected low class.

Adversarial controls distinguish intermediate from terminal permutations,
logical from redirected physical shear operands, required orientation
reversals and the leaf inverse. They reject source/rank/branch, child and
cardinality-layout faults. Binary cardinality checks include a 522-bit input.
The checker blocks runtime word inspection and scans the runtime modules for
numerical decoding/oracle calls, with explicit exceptions for fixed compilation
and finite flags.

The selected tests cover complete address operators. The complete Boolean
packet tests use the two-dimensional model. We have not enumerated the
selected GL64 Boolean payload or performed a new Lean build or independent
human review. These are different scopes.

## Reproduction

Use Python 3.12 and the standard library from the repository root:

```sh
python3.12 scripts/research_package.py --package research/selected-complete-residual --check-only
python3.12 scripts/research_package.py --package research/selected-complete-residual
```

The manifest registers the source suite, the complete high-packet replay and
the adversarial suite under optimized Python. Their timeouts are 500, 600 and 100
seconds. The optimized command covers the controls, not a second complete
packet run. We developed the package with CPython 3.12.13 on macOS arm64.

`RESULT.json` retains compact receipts and SHA256 values of the canonical full
results. Inspect a complete result with:

```sh
python3.12 -I -B research/selected-complete-residual/verify.py --suite source --emit
python3.12 -I -B research/selected-complete-residual/verify.py --suite packet --emit
python3.12 -I -O -B research/selected-complete-residual/verify.py --suite controls --emit
```

## Review map

| Files | Interface |
| --- | --- |
| `forms.py`, `plan.py`, `numeric.py` | Chronological tables, fixed-low itinerary and binary coefficients |
| `trace.py`, `children.py` | Shared symbolic trace and actual serialized child programs |
| `cardinality.py`, `bitstream.py` | Binary layout sizes, digit swaps and signs |
| `stream_runner.py`, `packet.py` | Complete fibres and one trace across the high packet |
| `checks.py`, `check_packet.py`, `control_checks.py` | Independent endpoints, bit origins and semantic controls |

We pin main inputs and the necessary PR2449 dependency files in
[SOURCES.json](SOURCES.json). [NOTICE.md](NOTICE.md) retains predecessor and
concurrent credit, including the separate PR2473 local-invoice audit and
PR2475 whole-call staging result.

## Open next questions

1. Can the caller replace the below-64 child guard with a complete recursive
   selected invocation? Start by generating the fresh raw directory for one
   larger child and returning through this same shared packet boundary. The
   fresh-row producer, recursive workspace and complete caller still block it.
2. Can the owner schedule consume this residual interface together with
   whole-call staging? Start with one selected COPY/ERASE interval and its
   exact physical field map. Conditional staging does not by itself implement
   the selected global call or its numerical admission.
3. Can a formal compiler certify the word, cardinality and shared-trace
   refinements? Start with the binary primitive and child-frame invariants.
   We currently have written proofs and executable checks.

[TASK.json](TASK.json) records structured first steps and blockers.
Jose Manuel (`jmbarrancoml`) prepared this work with substantial OpenAI Codex
assistance. We coordinated in
[Discussion2319](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18947427).
