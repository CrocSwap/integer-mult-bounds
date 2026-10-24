# Scoped Lean verification of the changed-map kappa improvement

TL;DR: this package checks explicit finite and real-analysis statements used by
the conditional **kappa = 0.00302152** construction. The tested moment saving is
0.00302153, leaving room for the claimed smaller value. The actual complete
replay status, source/output hashes, logs and theorem axiom reports belong to
`LEAN-VERIFICATION.json`; source files alone do not establish a successful run.

Prepared for **Cao Yifan**, with substantial OpenAI Codex assistance.
Apache-2.0; predecessor attribution remains in the native and whole-result
packages. The selected upstream frontier is unchanged.

The focused submission retains the positive construction and its verification
dependencies. Earlier negative controller/projector searches and the separate
736-unit scalar optimization are not stacked into this bound; historical
research notes can refer to exploratory artifacts outside this focused subset.

## What Lean checks

| Modules | Exact scope |
| --- | --- |
| `NativeCore`, `NativeRaw`, finite shards, `NativeData`, both orientations, `Native` | All 4,429 binary bases; 72 maps' two-sided inverses on all 512 vectors; 2,863 paid inclusion classes; 180 signed warp classes; all 408 helper frame interfaces; both 21,449-event frame/contact transcripts; paid census 3,298 and scalar tariffs 158120 / 158168 |
| `AnalyticGain` | Exact old-minus-new moment identity, local gain `12 g(t)` and global gain `216 g(t)`, strictly positive for every `0<t<1` |
| `NumericalMoments` | Actual `Real.rpow` contraction and both charged tail inequalities at tested saving `.00302153`, using proved log/exp remainder bounds |
| `CompilerCapacity` | Real-power compiler capacity and initial-range inequalities for the explicit retained parameters |
| `ArithmeticCertificate` | The 54 strict and 4 functional source-formula outer predicates, their recorded rational values, explicit finite integer compiler inequalities and budget comparisons |
| `KappaWarpVerification` | The package's combined scoped statements; inspect its propositions for the precise conjunction |

For `t=1-.00302153`, the numerical module proves, for the complete literal T/P
profiles:

```text
P(t) < (1 - 1/1000000000) T(t)
P(t+1/5) < (97/100) 20^(1/5) T(t)
10928 * 21 < (97/100) 20^.00302153 T(t).
```

These are inequalities about real powers, rather than assumptions that Python
enclosures are sound. Python chooses finite rational witnesses; Lean checks
their use of mathlib's log and exponential remainder theorems. See
`ANALYTIC-SCOPE.md`, `CAPACITY-SCOPE.md`, and `Native-note.md` for details.

The native model checks frames, contacts and invoices. It does not give
amplitude semantics, Clifford absolute phases, monomial/Fourier lowering, or
the 632-column free noncommutative endpoint identity. Those remain separate
exact Python certificates. JSON/hash-to-Lean transcription is an explicit
external boundary checked by regeneration; Lean does not parse the JSON or
prove SHA256 correctness.
Marker and adapter metadata are inert and unchecked in the finite projection.
The two orientations use their actual terminal scratch frame labels, 0 and
281, and check equality of all 632 persistent terminal frame labels. The
scratch field's zero amplitude belongs to the separate symbolic admission.

The full multiplication transfer retains the framework's analytic
decomposition, all-size native lift, autonomous-helper semantics, matching,
movement/fixed-tape, precision, stock, prime-avoidance and exact-recovery
contracts. No unconditional multiplication theorem or practical speedup is
claimed. The enormous algorithm-defined finite compiler template is not
materialized.

## Pinned setup

Use **Lean 4.21.0**, release commit `6741444a63ee`, and mathlib commit
`308445d7985027f538e281e18df29ca16ede2ba3`. `lean-toolchain`, `lakefile.toml`
and `lake-manifest.json` record these pins and transitive dependencies.
Install Lean through the normal Lean/elan toolchain installation for your
platform; the ignored local `.toolchain/` directory is not distributed.

From this package directory, with `elan`/`lake` on PATH:

```sh
elan toolchain install leanprover/lean4:v4.21.0
lake update
lake exe cache get Mathlib.Analysis.SpecialFunctions.Pow.Deriv Mathlib.Analysis.Calculus.Deriv.MeanValue Mathlib.Data.Complex.ExponentialBounds Mathlib.Tactic.NormNum Mathlib.Tactic.Linarith Mathlib.Tactic.Ring Mathlib.Tactic.Positivity
```

The cache command fetches the listed modules and their dependencies. It avoids
building all of mathlib locally. The verifier checks actual dependency Git
revisions and rejects tracked source modifications. Cached mathlib object files
and the installed Lean release are part of the ordinary trusted toolchain.

Use the repository's global Python 3.14 and existing executable-package
dependencies. No virtual environment or discovery solver is required. In the
commands below, replace `python3.14` with your global Python 3.14 launcher on
platforms that use a different command name. There are no required personal
workspace paths.

## Fresh replay

First replay the separately scoped native/phase and complete arithmetic package
from the repository root:

```sh
python3.14 -B research/kappa-interface-round2-20261022/verify_result.py
```

Then, from this Lean package:

```sh
python3.14 -B generate_arithmetic.py
python3.14 -B verify_lean.py
```

The first command refreshes the transcription receipt after the executable
replay updates its input hashes. The second checks regeneration and compiles
the resulting proofs.

The default is a fresh sequential compile. It follows local import dependencies:
native core/raw tables, finite shards, data, forward/backward words, native
summary, the four math modules, and the root aggregator. It uses a 65,536 KiB
Lean worker stack and a 30-minute timeout per module. Native checking is the
largest part; allow several minutes to tens of minutes depending on hardware
and cache state. Setup downloads have a separate cost. Actual per-module
timings appear in the receipt.

For every module the verifier records the source SHA256, exact command,
exit code, complete log hash, compiled `.olean` hash, local dependency output
hashes, and every emitted `#print axioms` result. It permits only `propext`,
`Classical.choice`, and `Quot.sound` (or an empty dependency list). It also
rejects source uses of `sorry`, `admit`, custom axioms, `native_decide`, and
explicit kernel/compiler trust bypasses. Ordinary finite `decide` proofs are
checked by Lean's kernel.

Before compilation it authenticates the frozen native payload and inherited
source pins, checks receipt links, and reruns all three generators into an
isolated temporary directory. Every generated Lean/JSON byte must agree with
the submitted source. It never regenerates over the submitted files. The
tested and claimed savings must equal their exact admitted rationals. The
complete target/paid profiles are freshly assembled from the actual local
native invoice and retained controller, then compared with both JSON and every
literal coefficient in `NumericalMoments.lean`, with no extra terms allowed.
The payload's canonical decompressed SHA256 is
`4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc`.
The final receipt also binds the final native/arithmetic input JSON and all
generator source hashes.

Generated proof sources are committed. `.olean` files, `.lake/`, downloaded
toolchains and cache data are local build outputs. Replays write module logs
and `LEAN-VERIFICATION.json` alongside the sources. A failed run records a
failure status; it cannot leave a new successful combined receipt.

`FOCUSED-INVENTORY.json` hashes the submitted positive package, including its
proof sources and logs, excluding the inventory itself and build outputs.
Before regenerating receipts, check it with `python3.14 -B publication_inventory.py`.
After an intentional fresh replay, `--write` records the new receipt bytes.

## Explicit reuse and partial work

To avoid repeating a completed native run, genuine source/output/log-bound
module receipts can be reused explicitly:

```sh
python3.14 -B verify_lean.py --reuse-evidence NATIVE-LEAN-VERIFICATION.json --reuse-evidence MATH-LEAN-VERIFICATION.json
```

Only validated rows are reused; missing modules are compiled. The verifier
rechecks the exact source, `.olean`, log, Lean/mathlib pins, expected axiom
reports, regenerated data and imported-module evidence. Reuse is a local
receipt/integrity check, not an independent attestation of a past execution.
The default command remains a fresh replay. `--reuse-only` refuses to compile
missing modules.

`python3.14 -B verify_lean_controls.py` reruns twelve corruption controls for
receipt hashes, axiom reports, compiler bypasses, parameters and profile binding.
It checks the wrapper's rejection paths without recompiling the native proofs.

For a dependency-closed partial run, use `--only MODULE ...`, optionally with
explicit reusable evidence. Its receipt is labelled `PASS_PARTIAL_LEAN_REPLAY`,
which cannot establish the full package result. `--check-inputs` only checks
authentication, source screening, pinned setup and generator equality; its
`PASS_INPUT_BINDINGS_ONLY` message proves no Lean theorem.

Do not run artifact-regenerating suites against the same checkout concurrently.
The verifier compiles sequentially and compares the input/source snapshots
again before issuing a successful full receipt. After a fresh Python replay
changes timing-linked JSON hashes, regenerate the arithmetic transcription
receipt, confirm its Lean source is unchanged, and rerun the Lean wrapper so
the combined record binds the final inputs.

## Open next questions

- Formalize exact Clifford amplitude/absolute-phase semantics for the concrete
  used warp and paid classes. The existing phase recipes are finite first
  inputs, but general semantic soundness lemmas are still needed.
- Formalize the autonomous 632-column free-word endpoint identity, then connect
  the finite model to the inherited all-size compiler transfer. Neither step is
  implied by a passing frame/invoice certificate.
- Review the conditional framework and this changed-map construction
  independently. Scoped Lean checks do not replace review of the unformalized
  hypotheses or promote the selected upstream result.
