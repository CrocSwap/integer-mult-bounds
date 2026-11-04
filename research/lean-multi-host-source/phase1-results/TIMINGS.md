# Phase 1 timings and limits

| Module | 4.33 seconds | 4.21 seconds | Ratio |
|---|---:|---:|---:|
| RowEvaluation | 0.613 | 0.718 | 1.171x |
| LinearReplay | 0.697 | 0.932 | 1.337x |
| TreeReplay | 0.963 | 1.421 | 1.476x |
| MatrixData | 39.090 | 48.802 | 1.248x |
| FramedReplay | 0.595 | 1.155 | 1.941x |
| FrameTraceCore | 0.512 | 1.140 | 2.227x |
| FrameTraceLiterals | 38.761 | 50.313 | 1.298x |
| MatrixCheckpoints | 72.588 | 108.727 | 1.498x |
| FrameTraceCheckpoints | 104.650 | 173.208 | 1.655x |
| PortData | 89.810 | 115.867 | 1.290x |
| PortRowData | 0.462 | 0.895 | 1.937x |
| PortGeometry | 6.584 | 10.366 | 1.574x |

Every listed final module probe passed using `lake build <module>`, the
inherited 8 MiB OS stack and no environment overrides or additional compilation
options. The data-module measurements include their newly split node modules.
The 4.33 baseline used direct Lean; Lake startup contributes to the 4.21 times.
The first three small-module timings were measured in the second checkout; its
local artifacts were then deleted before the final fresh aggregate build.

The two failed ordinary-Lake attempts (unsplit matrix nodes and the original
PortGeometry automation) remain in `module-timings.json`. Failure logs redact
absolute checkout/toolchain paths; each record contains both the original log
hash and the hash of the included redacted log. Earlier raised-stack results are
diagnostics only and are excluded from these successful timings.

The checkpoint ratios predict **50.1–55.4 minutes for FrameData**, compared
with 33.5 minutes on 4.33; weighting by checkpoint runtime gives 53.2 minutes.
This is an estimate, not a FrameData compatibility result. Its current 4,312
definitions and large lookup expressions may also require source partitioning.

Applying the same ratios to the 52-module Task B baseline suggests about
**68–75 minutes of serial compilation**, excluding dependency setup and audit.
The current upstream formal job limit is 45 minutes. A full port must address
this through ordinary source/package structure or an explicitly approved CI
integration decision; this phase does not solve it.

A planning estimate for the remaining port and validation is **one focused
working day (roughly 4–8 hours)** if the remaining issues resemble this probe.
Further data restructuring or repeated failures could make it longer. Stop
limits and the prohibition on theorem-statement changes remain in force.

The required Mathlib dependency build took 522.650 seconds (8m43s), after the
official cache endpoint was denied by the environment proxy. Only the required
dependency closure was built, not all of Mathlib. This setup time is excluded
from the local-module table.

Full Task A / Task B validation, the complete 931-declaration audit, the
deferred differential test and CI integration remain Phase 2 work.
The original review branch and PR #540 have not been changed.
