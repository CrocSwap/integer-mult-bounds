# Finite native Lean certificate

`NativeCore.lean` defines a finite certificate checker using Lean `Std` only.
`native_generate.py` authenticates canonical payload SHA256
`4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc`,
the frozen source pins, and the original inherited frame prefix, then transcribes
the actual emitted words and constructive witnesses to `NativeData.lean`,
`NativeRaw.lean`, the `NativeFrames0..3.lean` and `NativeOperators0..3.lean`
proof shards, `NativeForward.lean`, and `NativeBackward.lean`. `Native.lean` states the combined
finite results and prints their axiom dependencies.
The backward segment proofs are additionally split across
`NativeBackwardProofs0..3.lean`.

All finite proofs use ordinary `by decide`, checked by Lean's kernel.
There is no `native_decide`, `sorry`, `admit`, or custom axiom. The coefficient
domain for a frame of dimension d is all 2^d binary masks, with d at most9;
its natural-number XOR encoding is evaluated exactly.

The certificate covers:

- All4429 declared binary bases are independent: their only zero linear
  combination among all binary coefficient masks is the zero mask.
- All72 bound binary G maps have explicit two-sided inverses on all512 vectors;
  exactly34 differ from the inherited G bindings.
- All2863 distinct paid classes have explicit generator coordinates witnessing
  strict nested frame inclusion and the declared positive dimension increment.
  This includes all128 newly occurring paid classes.
- All180 signed warp/frame classes have explicit generator coordinates proving
  transport inclusion in both directions, with equal dimensions. This covers
  every actual occurrence's operator and input/output frame binding.
- Both full21449-event native words are partitioned into168 consecutive segments
  each. Every segment checks every scalar's actual source and destination frame,
  every paid and warp transition, the current frame state, dyadic/unit conditions,
  and the retained scalar tariff. Consecutive segment states agree, and their
  first/last states are the actual emitted initial/final frame arrays.
  The632 persistent final frames agree between orientations. The owned scratch
  C₀ ends cleared with frame tag0 forward and281 backward; the certificate uses
  those actual distinct scratch tags and proves equality of the persistent
  prefixes. Its symbolic zero-value semantics remain in the Python checks.
  The terminal owned scratch frame is tagged0 forward and281 backward;
  their632 persistent terminal frame labels agree. The scratch field's zero
  amplitude is part of the separate symbolic admission, outside this model.
- Both complete paid invoices are
  `2201 H1 + 412 H2 + 506 H3 + 135 H4 + 36 H5 + 8 H8`, totaling3298 calls.
  Exact real scalar allowances are158120 forward and158168 backward.
- All408 helper input/output frame interfaces are matched to actual endpoints,
  checked for strict inclusion, and yield28 H4 +7 H7 +47 H8 +326 H9.

The Lean statement has a precise boundary. Lean does not parse the JSON or prove
SHA256 correctness: the small Python generator and its input authentication are
the transcription boundary connecting the embedded data to the frozen artifact.
Marker and adapter metadata are inert in this numeric projection and are not
validated by the finite checker. Their physical and symbolic roles remain in
the separate native Python admission.
Lean does not prove the Clifford absolute phases, lowering to monomial/Fourier
recipes, or the632-column free-noncommutative symbolic endpoint identity.
Phase and adapter markers are inert frame annotations in this checker, following
the inherited literal frame model; their physical semantics remain outside it.
Those obligations retain the existing independent exact Python validation in
`research/warp-interface-20261022/verify_candidate.py`. This finite certificate
and the separate analytic Lean gain theorem do not formalize the complete
integer-multiplication theorem or discharge its inherited analytic, uniform
compiler, stock, precision, prime, tape, and recovery assumptions.

Lean elaboration status and the final replay command are recorded by the parent
package's verification receipt and `NATIVE-LEAN-VERIFICATION.json`. Runs use
Lean's `-s 65536` option (64MiB thread stacks); source catalogues are split into
small declarations and independent proof shards. The original monolithic build
hit Lean's stack limit during expression equality; this was a build-structure
limit, and no passing result is claimed from that attempt.
Generated Lean files must be regenerated with
the global Python3.14 executable after any change to the transcription script.

## Open next questions

The next formalization step is an exact finite Clifford representation and its
absolute-phase semantics; the current180 warp and128 new paid phase recipes are
concrete first inputs. A separate symbolic sparse-dyadic free-word evaluator
could then formalize the632-column endpoint identity. Both require general
semantic soundness lemmas and remain outside this finite frame certificate.
