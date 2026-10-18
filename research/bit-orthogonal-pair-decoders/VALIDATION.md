# Validation receipt

Base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`. Only
`research/bit-orthogonal-pair-decoders/` is added. The selected PR942 certificate,
all predecessor inputs and `upstream/` are unchanged.

Local environment: Windows, CPython 3.12.14 and 3.13.15. No packages were
installed. The mathematical checks use only the Python standard library.

Completed on 2026-10-13:

```sh
python3 -I -B research/bit-orthogonal-pair-decoders/test_package.py
python3 -I -S -B research/bit-orthogonal-pair-decoders/verify.py
python3 -I -S -O -B research/bit-orthogonal-pair-decoders/independent_check.py
python3 -I -B scripts/verify_selected_result.py
```

- The package tests exercise both implementations, deterministic receipt
  regeneration, swapped-partner rejection in both implementations and broken
  source-pin rejection.
- The primary rejects `-O` before invoking the pinned engines, whose own
  mathematical rejection checks use assertions. The independent implementation
  has no such dependency and passes under `-O`.
- The primary checks 39 obligations, including all 10,404 live decoder entries
  of the P102 witness and all 26 members of the puncture chain. It also checks
  six mathematical negative controls.
- A separate scope control changes the fixed reader basis on P111, obtains
  two cost-6 terms, and checks the complete identity and costs 68/67 on
  P111/P110. It prevents the one-root dual count from being mistaken for a
  universal restriction on that puncture. This control was added after an
  independent AI review identified the original prose overstatement.
- The independent checker uses lattice-membership enumeration, a different
  simple system and full-block Bareiss integer ranks. It imports neither the
  primary checker nor predecessor geometry code. It does not independently
  recompute the pricing engines or prove the written theorem.
- `RESULTS.json` regenerates byte-for-byte. Source SHA-256 checks cover seven
  executable/data inputs; six historical context inputs also match the Git
  blobs at the exact base. The recorded PR717 port-price note was retrieved at
  its pinned head and its Git blob and SHA-256 match `SOURCES.json`.
- The repository's selected-record check passes, including its source inventory
  and proof-supplement hashes.
- Receipt generation explicitly uses LF newlines, including on Windows, so a
  Git checkout does not change its byte representation. A broken executable
  source pin stops pricing before the engine import or moment calculation.
- A minimal export from the staged Git index, containing this package and its
  pinned inputs, passes all eight package tests on CPython 3.13.15 outside the
  checkout. This tests the bytes reviewers receive, not just working-copy
  newline representations. Staged whitespace checks also pass.

The full repository `make verify`, cold selected-supplier replay, native
multi-stage admission, physical emission, full changed-supplier invoices,
Lean multiplication verification and hosted CI were not run. No existing
supplier or generator changed, so those results are not needed to interpret
this scoped research package and are not claimed here.

The universal puncture quantifier rests on the written argument and its
explicit root-subspace coverage premise, not on enumerating all subsets of
120 lines. No exhaustive census of nine-pair systems is claimed.
