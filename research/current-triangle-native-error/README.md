# Complete triangle error operator in native charts

This scoped proof accounts for all three scalar rounding sites and all
three native MOVE error sites in the current PR #7669 triangle. It
compares the actual output charts, including the different old/new x
frames. It does not assume that chart transport commutes with rounding.

If E is the square root of the sum of all six squared local residual
norms, the new block's output error is at most `C_new E`, where
`5.435547392075 < C_new < 5.435547392076`. The constant is sharp for
arbitrary residual vectors with this joint budget. Sharpness for a
particular floor quantizer or actual caller is not asserted. The proof
also gives the old four-port constant and the complete ten-port
old/new difference. No new kappa is claimed.

Read [PROOF.md](PROOF.md) for the quantified interface, exact propagation
matrices, rational eigenvalue certificates and tensor/spectator lift.
[RESULT.json](RESULT.json) gives every source clock, matrix, norm interval,
512-column frame check, full-field residual check and fault control.
[error_operator.py](error_operator.py) derives the formal residual matrix.
[verify.py](verify.py) checks it with the retained direct Gaussian frames.

## Source and distinct scope

The exact candidate in
[PR #7669](https://github.com/CrocSwap/integer-mult-bounds/pull/7669) is
`ee251f6005d2a92b887c5b804bd7aac05989d278b2c9ccb3c3091b50d533b08d`.
Its source files are pinned at `95d476623f1468822057554475dc8badb19bfa44`.
The source's later documentation head leaves the words and local tapes
unchanged. The copied verifier from
[PR #7671](https://github.com/CrocSwap/integer-mult-bounds/pull/7671),
head `f34696319eb19d05d1b09f7372c3146be3ea1635`, supplies complete source
reconstruction and local window binding. Its common-coordinate scalar
law is not used as a transport-aware error bound.

This takes that proof's explicit native-transport question. The source
contributor is studying actual rounding and reachability. This result
has a separate scope: it takes local residual allowances as inputs and
proves their propagation. It supplies no native allowance, reachable
grid, signed range, physical runtime or free correction. Those unknown
costs and premises cannot be set to zero. All five selected assumptions
and the selected frontier remain unchanged.

The exact input and copy pins are in [SOURCES.json](SOURCES.json) and
[VENDORED.json](VENDORED.json). The copied source directory is a partial
dependency snapshot, not the source's full replay package.

## Reproduce

Use Python 3.12 and the standard library, from the repository root:

```sh
python3.12 -B scripts/research_package.py --package research/current-triangle-native-error
```

Normal and optimized commands must print `PASS_CURRENT_TRIANGLE_NATIVE_ERROR`,
followed by the registered package pass. The bounded checks cover all
1536 forward/adjoint columns of the three one-column frames, all ten
local residual ports on full 512-component fields, exact spectral
certificates and four semantic faults. The whole native word, sixteen-call
caller, price CLI and complete multiplier are not replayed.

## Open next questions

Supply native error allowances and reachable scalar grids at the six
literal sites. Then use the proved operator to combine those allowances
with earlier and later caller errors. The first step is the source's
transport-aware quantizer and reachability analysis; this package does
not reserve or duplicate that work. A complete physical tariff and signed
range argument are still required before this local bound can enter a
multiplication theorem.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
SYLforge supplied the candidate, exact edit and prior rational identity.
Ali Romman supplied the pinned source reconstruction and scalar audit.
CubeJerry supplied the retained direct Gaussian frame checker, prepared
with Codex assistance. Its notices and the copied source provenance
preserve the earlier native, caller, compiler and helper contributors.
New work is Apache-2.0. All retained source bytes are unchanged.
