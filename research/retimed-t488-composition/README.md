# Retimed suppliers composed with the T488 allocation

**Work in progress: full conditional admission is running. No improved endpoint is claimed until its final source-bound release passes.**

This package composes the two commuting release retimings from [PR3642](https://github.com/CrocSwap/integer-mult-bounds/pull/3642) with the literal T488 three-chronology allocation from [PR3633](https://github.com/CrocSwap/integer-mult-bounds/pull/3633). It closes the predicted packing gap by binding the actual retimed words to all 1,791,936 helper roles, then replaying native, controller, physical-cost, precision and modern outer gates. Neither predecessor improvement is credited as newly discovered here.

The candidate root lies in `(0.001730418899766071163804, 0.001730418899766071163805)`. Its candidate released value is the lower endpoint minus `10^-46 + 10^-70`. The difference from the exact PR3642 modern endpoint would be `0.000000024507952107748684`. Arithmetic alone does not admit that bound.

The complete proposed paid histogram is `{1:10817496, 2:3179808, 3:1024434, 4:447984, 5:94794, 8:35136, 48:186782}`. It covers 4,392 calls, 437,248 live families and 437,757 physical families, including 91 private zero buffers. The original T488 allocation and physical helper identities are retained; every changed native word and the complete new bill are checked separately.

## Reproduction and validation scope

The bounded verifier freshly reconstructs and audits the literal allocation, replays the local operator identity and controls, and checks the root and modern outer arithmetic independently. It is distinct from the full scientific admission described in [full-replay/README.md](full-replay/README.md). The combined bounded replay passed all four components in about 33 seconds; see [PUBLIC-VALIDATION.json](PUBLIC-VALIDATION.json). This is local validation, not hosted CI.

From the repository root with Python 3.12 and NumPy 2.5.4 installed:

```sh
python3.12 -B scripts/research_package.py --package research/retimed-t488-composition --check-only
python3.12 -B scripts/research_package.py --package research/retimed-t488-composition
```

Set `TMPDIR` to a mounted writable research output location before running; generated files remain outside the package. Source reconstruction and full replay require the exact pinned canonical source closure; they do not fetch mutable branch names.

The primary scientific run freshly replayed both changed native providers before its current full admission. Unchanged ancestor native/parent evidence is explicitly authenticated reuse. A packaged all-in-one wrapper is a separate delivery artifact and is not described as end-to-end tested unless actually executed.

[PROOF.md](PROOF.md) explains the composition and costs. [CREDITS.md](CREDITS.md) retains source attribution. Component manifests bind exact bytes, Git blob identities and originating heads. Decompressed semantics, rather than gzip container identity, are used when comparing regenerated compressed artifacts.

## Conditional scope

All inherited all-size dispatch/compiler and recursive rounding premises remain. So do common-label and mutable-source realization, whole-call hosting, SCALAR/COPY/CLEAR and zero-allocation contracts, uniform coefficient/stock bounds, bootstrap, precision, tape/recovery, and analytic/BIT H1-H5 assumptions. Finite symbolic and integer checks establish their stated instances and implications, not those general premises. No unconditional multiplication theorem, formal-kernel verification, independent human peer review or selected-frontier update is claimed.

## Open next questions

Further work should change the supplier, geometry or recursive interface, with a complete paid bill; repeated repacking under fixed widths is ceiling-limited. A separate valuable direction is a general proof of an inherited all-size obligation. Structured questions, first steps and blockers are in [TASK.json](TASK.json).
