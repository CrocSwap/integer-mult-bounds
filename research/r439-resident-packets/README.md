# R439 packets resident across a window

Two borrowed dirty banks can stay assigned to logical packets between events
of the exact PR2448/PR2481 R439 window. With whole-window restoration in place
of per-event restoration, the complete bill becomes **1084 routes, 1084 packet
exchanges and 3565 P-record XOR passes**, down from PR2481's1232/1232/4009.
No event is reordered and all borrowed dirt restores at exit.

The source-bound schedule has542residence intervals. This is the exact minimum
number of loads only in the fixed two-bank, common-frame, fixed-order model
defined in [PROOF.md](PROOF.md). It does not include every reversible adapter.
In particular PR2519 uses one bank,1232routes,626exchanges and2191XOR passes
with per-event restoration. This package claims neither dominance nor additive
savings over that different schedule.

The reduced complete GL2(Z/9) fixture checks431811formal independent input
records, all431568family outputs including422577unowned records, resident
values and parked dirt at all313event boundaries, and both directions.
Seven semantic faults must reject. A separately implemented request scheduler
agrees with the exact DP; both agree with a recurrence allowing prefetch and
early eviction on all1554request words of length1through4 over three families.

```sh
python3.12 scripts/research_package.py --package research/r439-resident-packets
python3.12 -I -O -B research/r439-resident-packets/verify.py
```

Use a writable TEMP/TMP on restricted Windows hosts. Reproduction checks the
committed receipt; it does not overwrite it. Source inputs have SHA256 and Git
blob pins. A fresh empty bytecode namespace covers retained Python loaders.
This is replay hygiene and not a sandbox for hostile code.

The payload contract assumes reversible route children preserve every parked
original and inactive bank and restore their own workspace and heads. It also
requires caller permission to leave originals exchanged until the window end.
Outer fresh payload/CLEAR/disposal counts are zero; borrowed capacity, headers,
control, private route scratch and physical scans remain charged obligations.
This is not a uniform GL64 compiler, full supplier, new kappa or full theorem.
The selected frontier and frozen source packages are unchanged.

Credit ywz65's PR2481 for the dirty exchange protocol and finite endpoint
harness, Ross Richardson's PR2448/2407/2437 for the retained window/routing
implementation, Jose Manuel's PR2195 and the retained supplier/exporter lineage.
PR2481 is pinned atd3ec95362a071e2726c5ff4ce587de80c7d4f984;
PR2448 at76311b90337a04dd811877d101c86ff8ecd65904. The standard caching/exchange
ideas are not claimed as new. This contribution supplies their changed
ownership contract, exact source-bound optimum and fully counted realization.
Prepared for ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
No human or formal-kernel review or hosted CI pass is claimed.

## Open next questions

Can the actual caller grant residence across this window without accessing
parked originals? Check every caller access against the saved residence trace;
a complete hosting proof is still absent. Which of this schedule and PR2519 is
cheaper under a real route backend? Price both invoices with identical route,
scan, header, control and scratch tariffs; call counts alone do not decide it.

Canonical [claim](https://github.com/CrocSwap/integer-mult-bounds/pull/2481#issuecomment-6193562425).
TASK.json records base, selection, scope pivot and incomplete live-overlap coverage.
