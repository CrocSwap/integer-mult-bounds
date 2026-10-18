# Finite multitape controller and proof toolkit

A self-contained Mathlib-based Lean contribution for actual fixed finite
multitape executions, exact costs, dirty parking, compiler simulation and
canonical binary output. This extends the preceding generic toolkit in PR1641.
All imports are bundled modules, Mathlib or Lean; no personal Lean library is
needed. The selected supplier profiles and kappa are unchanged.

`Absolute.ParkingController.boundary_machine_correct` constructs one fixed
five-tape, four-symbol, 90-state controller. For EVERY active bit list x, inactive
bit list y, absolute parking head h and arbitrary ancestor cell function, it
pushes y, moves x, executes a real bit-flip child, moves the result back, pops y,
and genuinely halts in exactly **6|x|+5|y|+18** physical transitions. The complete
inactive stream, parking tape and all heads return literally; IO/temp return to
marked-empty. Empty and unequal-length streams are included. It starts with the
explicit marked-stream convention (separator at −1); MarkerLifecycle separately
proves real charged marker installation/removal in two steps per operation.

`ParkingController.wrapper_correct` lets contributors substitute any ACTUAL
verified child execution, including a length-changing one. Input x, output z,
parked y and child time t give exact cost **2|x|+2|z|+5|y|+16+t**. Its premises
include the full physical child entry/return bank and true halt; arithmetic or
recursive correctness is not assumed inside the closed bit-flip theorem.

ParkFootprints proves every actual push/pop prefix stays at or above the
appropriate parking/stream marker and preserves the entire old ancestor prefix.
Completed routines have actual finite FootprintedRuns with the same exact cost.
MarkedStreamFootprints supplies analogous real-copy/flip bounds and idle-tape
facts. Arbitrary dirty ancestors do not add runtime.

`OutputNormalization.compiled_fixedWidth` is an actual two-stack finite TM2
program compiled to real multitape transitions. From the actual MSB-first list
`(fixedBits w n).reverse`, with n<2^w, it empties the source and emits canonical
`Nat.bits` before any existing output suffix in at most **10(w+1)** physical
transitions. The source takes exactly w+1 macrosteps, including EOF. Pure binary
lemmas are extracted from our Problem1.8 proof and independently checked using
only Mathlib. Upstream already has normalization; this supplies lightweight
interoperability with this toolkit, not new normalization mathematics. An
origin-anchored upstream buffer adapter or LSB-to-MSB reversal is additional work.

The retained `VerifiedPipeline.compile_completed_frame` turns actual halted
fixed heterogeneous TM2 executions into absolute-coordinate multitape runs with
charged bounded overhead and same-cost finite-frame replay. API.md maps the
compiler, frame, locality, trace, scheduler and asymptotic interfaces.

## Verification

Lean 4.34.1 and Mathlib d13f23b723b8a846827a245b89c10fc7d3f11612 are pinned in
lean/lean-toolchain and lean/lake-manifest.json. With that separately installed
environment, run from this package:

```sh
python3 -I -B verify.py
python3 -I -B replay.py --out /tmp/fresh-toolkit-check --cache-project /path/to/pinned/cache --lean /path/to/lean
```

The first command verifies immutable source hashes, finite controls and report
rejection controls; it does not run Lean. The second rebuilds EVERY module into
a new external directory and audits ALL declarations by their defining module,
including private/global/generated helpers. Only propext, Classical.choice and
Quot.sound are allowed. Real Lean fixtures test private/global coverage and
reject unused private axioms, public axioms and unproved private theorems. It
also checks exact declaration inventory against expected/AXIOMS.json. The cache
supplies only pinned Mathlib dependency libraries; no existing toolkit artifact
is imported by the fresh build. Outputs must stay outside the package.

VALIDATION.json binds the final proof/auditor sources and independent audit.
MANIFEST.json hashes every shipped source and document; an external upload
receipt separately binds that complete manifest. Finite simulations support
interface review; universal proof evidence is the Lean kernel/axiom audit.
Hosted CI and independent human review are not claimed. ci/formal.yml is an
optional dedicated workflow recipe; generic VERIFY.json runs only Python checks.

## Open next questions

1. Connect an arithmetic child using its actual physical Runs/Halts contract.
2. Implement and charge the upstream origin-anchored buffer-to-stack adapter.
3. Assemble on-tape recursive control, physical row routing and the recurrence.

The supplied theorems are sufficient and universal at their stated interfaces;
the package does not assert the complete fast multiplication theorem.
See PROOF.md, API.md, FRONTIER.md and NOTICE.md for scope and attribution.
