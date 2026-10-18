# Admit PR883's explicit X4 primitive lowering

Finite compiler refinement and complete accounting; no new kappa.

Philipp's PR883 gives four-primitive implementations of the selected X4 word's
56 zero-frame precondition pairs. This package emits those literal instructions
inside a complete primitive program, preserves every physical frame, phase,
center and wrapper event, and binds the refinement to a complete selected replay.
An independent two-row matrix check validates every emitted pair. Complete
737-column scalar replay checks the emitted streams and all private clearing.

The original macro ledger remains the logical proof interface. Its native
frame, phase, wrapper and whole-owner admission is valid because every changed
pair has the identical endpoint at frame zero, uses only the same two targets,
and introduces no recursive child or scratch register. All logical macros and
compiler adapter reserves remain charged. The new concrete implementation is
explicitly distinguished from the original macro ledger; see PROOF.md.

The complete 72-call invoice saves **56,448 real-component primitives** and
**36,288 coefficient-work operations**. The latter uses the predecessor's
per-component accounting convention, not an additional saving to add to the
primitive bill. Physical stock remains 7682; the conservative prefix remains
257 of 512 bits. All finite guards and the unchanged exact assembly pass at
`1661634653669567/1000000000000000000`. No runtime measurement is claimed.

## Reproduce

Python 3.11+, standard library only for the lowering/admission package. A full
bit reconstruction additionally needs the predecessor's C++17/Boost toolchain.
Supply a complete selected PR799 replay and its actual PR741 ancestry directory:

```sh
python -I -B research/x4-primitive-admission/admit.py \
  --replay /completed/frontier799/replay --ancestor /completed/frontier741 \
  --out /fresh/external/refined-admission
python -I -B research/x4-primitive-admission/test_controls.py \
  /fresh/external/refined-admission
```

If using the original public PR799 worker rather than PR865's guarded runner,
pass its work directory directly. The unchanged vendored PR865 coverage gate
checks all required ancestry stages/artifacts and selected-stage logs/results
before the mathematical binder. An existing or in-repository output is refused.
Native admission intentionally rejects disabled assertions.

`lowering/PRIMITIVE-PROGRAMS.json.gz` is the emitted concrete implementation;
`LOWERING.json` retains its exact endpoint, prefix, paid-profile and source
bindings. `invoice/` holds the complete recomputation. `candidate-package/`
contains a separate copied assembly context and generated refinement contract.
`ASSEMBLY.json` and `RESULT.json` are published only after assembly succeeds.
Original source packages, selected records and defaults are never edited.

Six emitted-prefix corruptions per orientation, immutable source drift and three
assembly controls must fail. The retained PR883 controls also reject all 672
pair deletion/sign mutants. The original source package's independent pair
proof and seven source/interface controls were freshly reproduced separately.

## Credit and scope

PR883 at `b31a870a3842b37f6ab97767c506ce91783632a2` is by Philipp (@mightyOil).
Its exact original package is retained in `vendor/pr883`; no priority for the
factorization, gatewise comparison or optimality proof is claimed. PR865 supplies
the required-evidence gate, crediting Lucas (@ljste)'s PR838 and concurrent PR847.
Selected native/phase/controller/invoice/assembly sources retain Jeremy Kothe,
Chafik Boukhalfa, icekylinx, DreamingOfClouds, Rohan Arun, eumemic and predecessor
attribution. SOURCES.json pins the consumed sources and contexts.

Overlap refresh through PR902 found ToikY's concurrent PR901, which changes
the following arbitrary-helper compensation and preserves this precondition.
Its candidate is not consumed; no combined saving or integration priority is
claimed. Main remains at the pinned f567884a context.

Prepared for **nightangelflowerwin-ops** with substantial **OpenAI Codex
assistance** in integration, verification, mathematics and writing, Apache-2.0.
No independent human review, new exponent, measured speedup or full multiplication
theorem is claimed. All-size compilation, physical realization/hosting,
precision/tape and analytic transfer remain inherited assumptions.
