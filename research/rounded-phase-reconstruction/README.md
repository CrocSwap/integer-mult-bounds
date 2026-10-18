# Independent formal audit of rounded-phase reconstruction

PR1141's rounded three-shear phase stream can reconstruct its two-register
state exactly. This package supplies an independent Lean proof of that existing
claim for arbitrary integer-grid states and every walk length, with explicit
source binding and failure controls. It does not introduce a phase construction
or repeat its analytic error argument.

The result is in [PROOF.md](PROOF.md) and [Reconstruction.lean](Reconstruction.lean).
The seven exported roots prove both rotation inverses, both nonlinear state
inverses, both all-length reconstructions and deterministic readout preservation.
The inverse must restore the ratio before rebuilding its chart and must reuse
the same rounded product with opposite addition. Half-up rounding is not odd.

## Source and credit

The unchanged source is Ali Romman's [PR1141](https://github.com/CrocSwap/integer-mult-bounds/pull/1141),
commit `1627bf208f80e490522343590dd52f38b329e238` in
`aliromman/integer-mult-bounds`, directory `research/dirty-stride-fast-phases`.
Its exact reconstruction argument and algorithm are predecessor work.
[VENDOR.json](VENDOR.json) authenticates all 25 retained files by Git blob and
SHA-256 before any source module is imported; original notices and the nested
PR1038/PR985/PR479 lineage are retained. Vendoring supports a Git-free exact
replay, not a new attribution claim.

Substantial OpenAI Codex assistance was used for proof, code, tests and writing.
Independent agent review is evidence of a separate replay, not maintainer or
human acceptance.

## Reproduction and recorded evidence

Standard-library Python 3.12, from the repository root:

```sh
python -I -B research/rounded-phase-reconstruction/verify.py
python -I -O -B research/rounded-phase-reconstruction/verify.py
python -I -O -B research/rounded-phase-reconstruction/integrity.py
python scripts/research_package.py --package research/rounded-phase-reconstruction
```

The Python replay checks [RESULT.json](RESULT.json): 12,556 rotation fixtures,
496 source/lattice chart comparisons, 5,000 arbitrary dirty nonlinear state
fixtures, 48 forward/reverse/repeated-readout traces totaling 4,056 steps, four
actual prepared phase-pass roundtrips, and six semantic failure controls.
Each rotation and nonlinear fixture checks both directions. Primitive tests
include `b=0,1`; the actual `Phase.prepare` tests respect its `b>=2` domain.
Manually constructed arbitrary states test the exact arithmetic, not the
predecessor's analytic seed-admission contract.

Fresh formal verification is a separate command, using the official Windows
Lean 4.34.1 build with commit
`5045d0056413266e57c625dcd7c365b10e377c52`:

```sh
python -I -O -B research/rounded-phase-reconstruction/kernel.py --lean /path/to/lean.exe
```

It compiles from a fresh temporary directory and compares [KERNEL.json](KERNEL.json):
seven roots with only `propext`, four false-proposition rejections, and an axiom
guard control. The pinned receipt is platform-specific. Python's registered
replay checks its structure and proof hash but **does not run Lean**. A different
toolchain needs a separate reviewed receipt, not an assertion that this run
occurred. Both receipt-writing options refuse existing destinations; ordinary
commands do not rewrite evidence. A writable TEMP/TMP may be needed on Windows.

## Milestone, costs and consumer boundary

This is a **local formal audit module**. It strengthens one named restoration
claim in PR1141. The all-size algebra is proved; source interpretation is
reviewed and finitely tested. The Python implementation is not compiled into
Lean semantics by a verified translator. No analytic approximation or error,
register-width, bit-time, physical scratch, tape restoration or full supplier
claim is proved here. Those obligations remain with the predecessor and any
downstream consumer. No cost is silently set to zero because it is unmodeled.

The guidance-revision-5 family decision is **narrow and stop** at this audit.
Further mechanism work needs a named consumer and a plan for the remaining
precision, physical realization and total-resource obligations. The selected
frontier and frozen predecessor evidence are unchanged.

## Open next questions

* Can the exact source interpreter be connected to the Lean definitions by a
  verified translation or an explicit small-step refinement? This would remove
  the reviewed/finite boundary. Start with `rotate` and then `State.step`;
  Python rationals, control guards and metering semantics are blockers.
* Can the predecessor's analytic phase-error recurrence be formalized on the
  same exact grid model? It would connect reconstruction with useful precision.
  Start from its stated one-step error lemma; real analysis, seed preparation
  and all caller-domain hypotheses remain obligations.

The assignment, overlap limits and refresh checkpoint are recorded in
[TASK.json](TASK.json). A cache search without matches is not proof of novelty.
