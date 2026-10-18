# Executed validation

Executed on 2026-10-13 with Windows / CPython 3.14 at base
`2921874911956718fcaaaf9396fe8267b3cfa9f0`.

| Command from repository root | Result |
| --- | --- |
| `python research/complex-decoder-field-extension-seed44/verify.py --write` | PASS; initial exact certificate recording |
| `python -I -O -B research/complex-decoder-field-extension-seed44/verify.py` | PASS; complete certificate comparison under isolated optimized execution |
| `python -B scripts/verify_selected_result.py` | PASS unchanged selected record, exact kappa and source/proof inventory |
| `make verify` | Unavailable: Windows reports that `make` is not recognized |
| `git diff --cached --check` | PASS for the twelve new package files |

The new verifier builds its root ordering independently, checks all
14,400 label-pairing entries, implements exact Gaussian rational inversion
and clears denominators to verify ordinary-transpose decoder identities
using integers. The three examples each check every pair among all 120
root lines, then compute support costs for 25 puncture sizes. All 25
phase-scaled attaining costs are independently checked. Their matrices
come from two fixed families, with full root-pair identities rechecked
at p=0,8,16,24. No floating point arithmetic is used.

Seven negative controls expose unrestricted complex cross-term
nonparallelism, support-preserving real projection as a false duality
argument, replacing transpose by conjugate transpose, giving the
genuinely nonreal witness a seven-dimensional root-zero flat, a corrupted
dual coefficient, a missing source pin and a corrupted source digest.
The isotropic and phase examples are actual counterexamples to those
specified shortcuts, not failures of PR968's explicitly real theorem.

The inherited replay invokes PR968 sections A/B/C and its E attaining
chain after finding the first exact frame pair. It does **not** replay
the full 1,260-frame census, its favorable-budget pricing or its complete
original package. The imported assertions run in a separate `-I -B`
process without optimization, even under an optimized parent verifier.
The source inventory is required exactly, so omitting a pin cannot
disable a dependency check.

The arbitrary-complex quantifier is justified by PROOF.md, not by the
finite Gaussian-rational examples. The real E8 hyperplane-flat
classification F6 and the inherited real geometric lemmas remain
explicit premises. Root coordination reviewed the complex duality and
counting bridge with no substantive blocker; this is not a claim of
independent human or proof-assistant review.

No supplier is changed or priced. Native compilation, complete repository
suite, hosted CI, physical asymmetric centres, changed recursive profiles,
outer assembly and all-size multiplication verification are not claimed.
Only the new package is added; selected and predecessor files are unchanged.

Coordination replay note: a receipt comparison failed during precommit
finalization. The failing intermediate receipt was not preserved, so its
exact cause cannot be reconstructed. After commit 78b5e793, both worker and
coordinator reproduced the saved certificate under isolated optimized
execution; a recursive comparison found no differing fields. The inherited
log contains fixed facts only, with no timings. No certificate was
regenerated in response to that transient failure.
