# Frozen grouped cyclic inverse validation

Both complete replays passed on macOS arm64 / Python 3.11.15 and Linux
aarch64 / Python 3.14.8, with isolation, optimization and bytecode disabled.
The full mathematical receipts are byte-identical to each other and to
`../grouped-dirty-cyclic/EXPECTED.json`.

Frozen source manifest SHA256:
`424e13945d3e69e62d9aa736a5ef52b5e14bdadeceb5b475a9e25d0e30f9e2b5`.
Complete mathematical receipt SHA256:
`89f5f8ed967c3c748a7be30bc82dc910c9fb233ff329f57bcea055834bdf6c63`.

The per-platform `*-MATH.json.gz` files retain the complete receipts.
Compare their decompressed bytes; compressed containers are not mathematical
identities. `*-PACKAGE.json`, `*-PLATFORM.json` and `*.log.txt` retain the
package controls, environment and complete terminal logs. `VALIDATION.json`
records the cross-platform comparison and evidence hashes.

Each platform passed 11 package rejection controls and a complete replay
from a read-only relocated copy in a path containing spaces. Linux additionally
ran the supplied source package read-only, outside a repository checkout,
under a durable supervisor that recorded exit status zero.

The replay covers 160 real, 40 weighted complex, 120 mixed-root and 48
original-kernel cases, 2,313 exact budget rows, three all-size polynomial
identities, 16 additional mathematical rejection controls and 36 independent
fraction-free solver comparisons. All ten pinned kernel fixtures through
radix 16 meet their original 128-bit target. Source and dirty connector
restoration and inverse-word cancellation are exact, including arbitrary
odd lowest working bits. The written all-length proof is separate from
these finite computational checks.

All 14 consumed source files match their pinned Git objects, as recorded in
`SOURCE-GIT-CHECK.json`. Selected-record consistency and staged whitespace
checks passed. Only the new research packages and scoped workflow are added.
The complete repository suite and hosted CI were not run by these
prepublication records; the workflow runs full Python 3.11/3.14 replays.

Two prepublication issues are recorded in `PREPUBLICATION-CORRECTIONS.json`:
the strict inventory rejected macOS archive sidecars before mathematics ran;
then Linux exposed inherited read-only permissions in disposable mutation
fixtures. Repacking removed sidecars, and the test harness now makes only
those disposable fixtures writable. Mathematical source and expected results
did not change. Both complete platform runs were repeated on the final
manifest above, including all package controls.

Related PR805 uses determinant-balanced in-place leaves for real coefficients
bounded by 1/2 and leaves exact coefficient growth outside its bounded-width
contract. This package instead uses higher-order additive groups with complex
unit phases and bounded coefficient preparation. Its code is not imported;
no savings from the two constructions are combined.

No new kappa, bit-reversible arithmetic compiler, common-label/Clifford
realization, physical tape schedule or full multiplication theorem is claimed.
