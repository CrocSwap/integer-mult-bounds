# Finite reachable alphabets at the FinTM2 boundary

The external proof linked in PR2411 uses Mathlib's FinTM2. Its type requires
a finite **input** alphabet, finite control and finite labels; other declared
stack alphabets may be infinite. This package supplies a source-bound
all-prefix finite-symbol lemma and a fixed primitive-action bound that
justify that part of the machine interpretation. It identifies no defect
in PR2411 and changes no multiplication saving.

For one fixed machine, collect all input symbols and every value of every
push callback on every control state. This is one finite alphabet for every
input and every execution prefix. The maximum statement depth over all
labels bounds the primitive actions per macro step. Both statements are
kernel checked on isolated definitions extracted from the exact pinned
Mathlib semantics. Arbitrary dependent symbol types are permitted.

[PROOF.md](PROOF.md) gives the hypotheses, source-to-model correspondence,
finite-table interpretation and the boundary between kernel proof and the
written multitape argument. This is not a full Mathlib import, a physical
tape compiler, or an independent rebuild of the external multiplier.

## Reproduce

The standard-library Python 3.12 hook is explicitly **non-kernel**:

```sh
python3.12 scripts/research_package.py --package research/fintm2-reachable-alphabet
```

The separate kernel workflow needs the official Lean 4.34.1 compiler,
commit `5045d0056413266e57c625dcd7c365b10e377c52`, without Mathlib installation:

```sh
python3.12 -I -O -B research/fintm2-reachable-alphabet/verify.py --kernel --lean /path/to/lean
```

It compiles both modules in fresh temporary storage and requires all four
named transitive axiom reports. No prebuilt package oleans are reused.
[KERNEL.json](KERNEL.json) binds the proof bytes and accepted reports.
The local compiler archive was checked against its official SHA256.
A separate AI reviewer inspected the source/model boundary and independently
repeated the dedicated kernel command successfully. A Git-free relocated
replay and four actual source/semantic/proof/receipt corruptions also passed.
Use writable TEMP/TMP if required by the execution sandbox.

The independent Python model checks 1,533 complete input/control cases,
24,582 macro prefixes, 116,778 primitive actions, six semantic rejecting
controls, and seven reporting rejections. These checks support the boundary
and do not replace the kernel inductions. `RESULT.json` is deterministic.

## Limits

The isolated theorem and source-extraction check have distinct trust roles.
The actual Mathlib-name instantiation, finite-table machine conversion and
constant-overhead multitape interpretation are written arguments. No full
external theorem build, hosted CI, runtime benchmark, independent human
review or new formalized multiplier claim is made. Input encodings and
analytic exponent calculations of PR2411 are unchanged.

## Open next questions

Import the pinned Mathlib modules and elaborate the same invariants directly
for Turing.FinTM2, deriving the complete lists from its Fintype fields and
binding initList. This would remove the source-extraction correspondence
from the remaining review boundary. First port the unchanged induction
through exact definitions; a full compatible Mathlib build is required.

Then formalize the finite-table relabeling into a finite-alphabet multitape
machine with a step-count simulation. The fixed-depth lemma is one input,
not that simulator itself; the existing single-tape shuttle implementation
does not provide the required constant overhead.

## Credit

Dan Brown and Kenny Daniel authored the MIT-licensed external theorem linked
by PR2411. Mathlib's authors retain the Apache-2.0 source notices. New
source and proof are Apache-2.0, prepared by ywz65 with substantial OpenAI
Codex assistance in investigation, implementation, proof and checking.
