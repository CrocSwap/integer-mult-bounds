# QQ16 third-moment transcript capacity

Thirteen rational query coordinates per regular-cover owner cannot repair
the fixed QQ16 selected-input loss under the retained erased-family
observation contract. The new certificate gives

```text
rank([B0;B1;B2]) >= 280|G|/13,
selected A/T defect >= ceil(176|G|/13),
residual after a width-13 record >= ceil(7|G|/13).
```

Fourteen coordinates are necessary, not proved sufficient or optimal.
These are information dimensions, not paid recursive ranks. The selected
frontier and all frozen packages remain unchanged. No new supplier or κ.

## What changed

Ross Richardson's [PR2104](https://github.com/CrocSwap/integer-mult-bounds/pull/2104)
uses two exact moments to obtain rank at least 144|G|/7.
commdata2338's [PR2153](https://github.com/CrocSwap/integer-mult-bounds/pull/2153)
transfers that bound to the joint A/T defect and excludes records with at
most twelve coordinates per owner.

This package adds the third moment, `tr(T^3)=(109/3)|G|`, for
`T=sum_s B_s*B_s/48`, and an exact cubic spectral certificate. It improves
their defect lower bound by 88|G|/91 and excludes width thirteen.
[PROOF.md](PROOF.md) includes the ordered route and defect arguments.

Two different checks establish the new finite premise. A complete census
of 18,432 ordered route products finds that the stage-1 and stage-2
product sets intersect only at identity. A chart-swap reconstruction
checks the same implication using disjoint external axes and 96 distinct
ordinary frames. Their identity triple coefficient is exactly 6,144.
No predecessor executable is imported.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B scripts/research_package.py --package research/qq16-third-moment-capacity
python3.12 -I -O -B research/qq16-third-moment-capacity/verify.py
python3.12 -I -O -B research/qq16-third-moment-capacity/test_verify.py
```

Expected verifier line:

```text
PASS_QQ16_THIRD_MOMENT_CAPACITY rank>=280|G|/13 defect>=176|G|/13 width>=14 no_new_kappa
```

Normal and optimized registered replay pass on Linux with CPython 3.12.15.
The direct normal/optimized verifier runs also pass under a 512 MiB
address-space cap, with a measured peak child RSS of 114,672 KiB. The Git
provenance launcher ran without that cap because Git maps a larger existing
packfile. All 65 research-workflow tests and selected-record integrity pass.

The read-only verifier checks live source hashes and exact equality with
[RESULT.json](RESULT.json). Three semantic controls reject a changed query
coefficient, collapsed stage routes and a duplicate chart. Seven behavior
and arithmetic tests include source and receipt corruption through the CLI.
Validation stays enabled under `-O`.

Source commits, Git blobs and hashes are in [SOURCES.json](SOURCES.json).
[TASK.json](TASK.json) records the central-handoff override, overlap,
predecessor heads, scope and final freshness check. The generic launcher
also authenticates historical task and selected-record provenance.

## Verification limits

This is author-checked exact finite source evidence plus a written proof.
It has no independent human or formal-kernel review. The retained QQ16
witness supplies the global erased-family trajectory; this package does
not rerun it, the native local words or the full selected cold replay.

Records of width fourteen and fifteen, nonlinear encoders and changed
trajectories remain outside the exclusion. Native access, retention,
cleanup, ownership, tape, recursive precision and supplier adoption remain
open. PR2174's adjacent sixteen-coordinate recovery grants the B1-cut
selected values; it is not a final-only controller or paid-cost invoice.

## Implementation bounds

The verifier has no recursion or dynamic code evaluation. Its route
products have exactly 96² iterations per stage; binary application has
at most 25 iterations. The 48 spectator axes must remain fixed. Packet
input is at most 1 MiB compressed and 16 MiB decompressed, and every
proof-relevant collection comes from fixed, hash-bound source bytes.
Functions stay below 60 physical lines and all semantic guards remain
active under optimization. Each test subprocess has a 30-second timeout.

Power-of-ten rule 3 has a managed-runtime deviation in `verify.py` and
`test_verify.py`: Python allocates parsed objects, integers and census
tuples during checking. The fixed source dimensions, input caps and
18,432-product limit bound this batch workload. Replay under a memory cap
checks the compensating control. A fixed-capacity native implementation
would only be needed if this certificate becomes a larger search tool.
The diagnostics are `-Wall` compilation and normal/optimized tests. No
additional Python static analyzer was run.

## Open next questions

1. Can a higher-moment certificate exclude width fourteen or fifteen?
   The exact stack rank determines the remaining information gap. First
   compute another identity trace with all route products counted, then
   bound the spectral indicator on [0,3]. The cover is too large for naive
   matrix expansion, and additional moments may still not decide the gap.
2. Can a proposed width-fourteen or width-fifteen record recover the
   selected inputs under the complete observation operator? Test its
   kernel against all required selected rows before native costing.
   No such record or final-only controller has been supplied. The
   sixteen-coordinate result in PR2174 is a useful upper description
   under its explicitly granted B1-cut observations.

## Credit

Nick Petalas. New work is Apache-2.0; retained notices are unchanged.
Ali Romman and the PR1969 contributors supplied the conserved maps,
selected sections, route packet and erased witness. Ross Richardson
supplied the two-moment method in PR2104. commdata2338 supplied the joint
A/T capacity argument in PR2153 and the adjacent recovery in PR2174.
Cinna Davis's PR2079/PR2122 and Adam Gall's PR2086/PR2093 supplied the
preceding query and logger investigations. The inherited supplier lineage
includes Rohan Arun, Jeremy Kothe, Hao Yan and Zhihao Chen.
