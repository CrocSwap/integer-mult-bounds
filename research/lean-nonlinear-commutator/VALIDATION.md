# Executed validation

Checked on Linux x86-64, 2026-10-13, with Python 3.14.4 and 3.12.3 and the
official Lean 4.21.0 Release compiler, commit `6741444a63ee`. Only core and
bundled Std are required. The toolchain archive SHA256 is recorded in
`SOURCES.json`; no compiler or library binary is redistributed.

## Formal proof and source traces

The following passes from the repository root:

```sh
python3 -B -I research/lean-nonlinear-commutator/verify.py --lean /path/to/lean-4.21.0/bin/lean
```

The verifier compiles both the generic proof and the generated trace statements
from source in a fresh temporary directory. It uses one Lean worker, a 64 MiB
thread stack, warnings as errors, recursion bound 100,000, heartbeat bound
4,000,000, and a 300-second timeout per invocation. The larger explicit stack
is needed for the expanded 83-factor equality; the ordinary default stack
overflowed in the initial attempt. The complete planned domain passes with
the explicit settings.

All 12 generic statement probes use only `propext` and/or `Quot.sound`.
All **34 literal source-trace equalities have no axiom dependencies**. No
placeholder, custom assumption, or native evaluation oracle is admitted.
The `IsAdditive` premise and completed-leaf interface remain explicit model
hypotheses, as detailed in `MODEL.md`.

| Completed check | Coverage |
|---|---:|
| Actual source traces, both signs, n=1..64 and n=83 | 130 |
| Instructions in those traces | 206,830 |
| Kernel-checked literal traces, both signs, n=1..16 and n=83 | 34 |
| Mutable source execution cases | 1,170 |
| Source leaf calls including whole-word inverse checks | 3,722,940 |
| All ordered binary trees through seven leaves | 197 |
| Additional functional/word/delta execution cases on those trees | 2,364 |
| Compiler rejection controls | 6 |
| Disallowed-axiom audit controls | 3 |
| Source alias/depth admission controls | 4 |

The source cases cover widths 1,2,3; the complete tree census covers widths
2,3. Both use the fixed floor, bounded-square, and integer-shear families.
Nonzero signed dirt and initial targets are deterministic. The finite domain
is not an adaptive search, and no finite replay is extrapolated into the
universal theorem.

The generated `TraceCases.lean` SHA256 is
`35d6a7bed4b0b0350e539c71a5f58a5a9f54ad4abc02bd436c7c0985b34455bc`.
Use `--emit-cases /new/TraceCases.lean` to export it. The generic proof's
SHA256 is `c08de49fe02781d69eddc7bb9b4f3c8d311cc1bbe21e6ccb1db86eeafb97dceb`.

## Reproducibility and failure checks

The complete ordinary isolated Python 3.14.4 replay matches `EXPECTED.json`.
A standalone copy outside Git, in a path containing spaces, passes under
isolated **optimized** Python 3.12.3. Every copied package file and directory
is read-only during that run, and all bytes remain unchanged afterward. It
took about 41 seconds on this host, including all controls; no performance
improvement is claimed.

An early portability check found that `ast.dump` serializes empty fields
differently between these Python versions. The final receipt instead binds
the exact extracted `compose` source segment, SHA256
`7b9651bbed8bc2faa0cbdbfa896d75175564b01bca612dc8971c51e8ca9a5361`.
The entire immutable source is separately pinned by SHA256 and Git blob.
All proof-relevant receipt fields compare by canonical JSON, without elapsed
times, host paths, or interpreter debug serialization.

Additional package checks reject a changed pinned `dirty.py`, a missing
`dirty.py`, and a receipt replacing the first integer factor count `1` with
JSON `true`. The last case tests strict receipt comparison despite Python's
ordinary `1 == True`. Existing receipt and generated-case output destinations
are rejected before work, preserving their original contents. These controls
also run with Python optimization enabled.

The compiler controls independently alter scratch restoration, a final target
sign, the target-independent leaf contract, ideal factor order, whole-word
reversal, and a source-derived literal sign. Each produces a Lean error.
Audit inputs containing `sorryAx`, `Lean.ofReduceBool`, or a custom assumption
are rejected. Source admission rejects source/target aliasing, each ancestor
alias as scratch, and insufficient depth before invoking a leaf.

## Repository and publication scope

`make selected-record-check` passes with the selected exact
κ=`1661634653669567/10^18`. Package whitespace and scope checks pass. No selected
artifact, producer, or `upstream/` source changes. Full regenerating suites,
cold supplier reconstruction, and hosted CI success are outside the local
validation claim.

The final full queue refresh covered **686 open PRs through #894**. Main
remained `f567884aeb8851b6e794af1184119a3bfbe1e631`, and consumed PR628/663
heads were unchanged. New PR889 batches distinct output shears with a common
factor and has a different interface; PR893 audits historical Lean source
and recorded evidence. Neither supplies this binary-tree semantics proof.
There is no pinned coordination issue; the local claim records the result
and final PR link.

The all-size typed semantics and the bounded Python/address connection are
distinct evidence. Numerical leaf correctness, all-size address-compiler
correctness, Python semantics, external-data nonaliasing, physical execution,
and the full multiplication reduction remain as stated in `MODEL.md`.
