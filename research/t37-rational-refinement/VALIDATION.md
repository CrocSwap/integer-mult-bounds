# Executed validation and reproduction boundary

Base: 8bddbee377e2f3ce1f1247196c4b290d55767d20; OS seed 24.

`python3 -I -B research/t37-rational-refinement/verify.py` passes. It checks
the closed inventory and bytes of all 876 source files; the three supplier
engines used from that closure match the original assembly's engine digests.
It reproduces the original full assembly exactly, then the finer full
assembly with kappa 0.001661960547713947858091. All 47 strict constraints
pass, with positive absorption gap approximately 4.90827e-25. Both native
moment-engine tables, the conservative moment table, both seven-step
bootstrap chains and every invoice input digest are unchanged.

The exact adaptations are recorded in CERTIFICATE.json. ASSEMBLY.json is
the complete fresh refined output. Temporary replay logs and all raw inputs
can be retained with --output. The source archive's obsolete absolute pivot
path is relocated to the identical hash-pinned recipe, without changing its
contents. The objective-grid changes are the only mathematical source edits.

Seven controls reject next fine grid, old next coarse grid, zero eta, zero
beta, old 512-bit complex charge, old 1024-bit row extra and under-reporting
the charged primitive count by one. The assembler retains the 1024-bit
complex/512-bit bit charges and the full row, physical, tape and precision
guards before evaluating the moments and outer bound.

`python3 -I -B research/t37-rational-refinement/test_package.py` passes from
a minimal 32 MB source closure with spaces in its path and no Git/network
dependency. Eight package controls reject false or missing bound/control
receipts, changed outer source, missing source inventory, a false absorption
gap, overwritten output and an optimized-Python assertion bypass.

The source-bound selected-record checker and git diff whitespace checks
pass. The live selected record was refreshed before submission and still
has 0.001661960547713947. Full open PR metadata and targeted all-state
searches show no matching T37 finer-grid contribution; larger pending
different-word proposals are distinguished in README.md.

Native geometry, ownership, emission and cold ancestry evidence are retained
from the frozen maintainer-reviewed construction. They are not freshly
rebuilt here. This package freshly recomputes complete pricing, moments,
bootstrap, finite invoices and outer assembly from those immutable inputs.
It does not claim remote CI, a complete Lean multiplication proof or an
unconditional theorem; all inherited all-size/physical/precision/tape and
analytic hypotheses remain as recorded in the source review.
