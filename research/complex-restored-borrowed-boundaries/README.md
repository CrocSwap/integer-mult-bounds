# Arbitrarily many restored dirty donors do not cheapen CK/JP8 boundaries

**Scoped negative result; no new kappa.** Borrowing any finite number of fixed,
arbitrarily dirty registers and restoring all of them cannot achieve the
existing disposable-scratch price for a three-cycle or a disjoint 2+3-cycle.
Exact primitive minima are **4**, **6**, and **between 9 and 10** respectively,
compared with the disposable-scratch costs **4**, **5**, **8**.

The new part is a write-count and read-only-specialization lemma reducing *any
number* of restored dirty donors to at most one at the relevant short budgets.
Two independently represented searches then agree on every one of **2,373,527
states**. This changes the register contract explicitly excluded by PR1145;
it does not rerun its moved-coordinates-only experiment. PR1095's
monomial-prefix/disposable-workspace class is different too.

The full [proof](PROOF.md) separates the exact lemma, complete finite quotient
exclusion, rational upper witnesses and the frozen historical application.
The 168 retained PR969 CK/JP8 boundaries require at least 238 instead of 224
primitives per real component if all donors must restore. There is no complete
supplier work-row saving or change to the paid recursive profile.

## Reproduce

Python 3.9+ (standard library) and clang++ or g++ supporting `unsigned __int128`:

```sh
python3 -I -O -B research/complex-restored-borrowed-boundaries/verify.py
python3 -I -O -B research/complex-restored-borrowed-boundaries/test_package.py
```

Expected first command's final line:

```text
PASS_COMPLEX_RESTORED_BORROWING boundaries=168 states=2373527 costs=4,6,>=9 arbitrary_restored_donors no_new_kappa
```

Both commands run offline and leave tracked inputs unchanged. The verifier
compiles its separate C++ enumerator in a temporary directory, compares every
canonical matrix/distance pair, checks all exact witnesses and 37 gate omissions,
replays the full boundary census, and requires the entire EXPECTED receipt.
`--record NEW_PATH` writes a fresh receipt only after all semantic checks and
refuses to overwrite an existing path. Canonical uncompressed JSON is the
receipt equality criterion; no compressed output hash is used as mathematics.
The test command adds dense matrix/product oracles, dirty-donor controls,
source and receipt corruptions, and minimal offline relocation.

Research base **`1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`**; OS seed **33**.
At this base the selected conditional kappa is `0.001672660197076918` (PR1094),
with complex supplier binding and unchanged PR589/555 bit supplier. That record
is context, not the historical supplier being modified. The selected certificate,
review and source manifest were followed; no selected file is changed.

[SOURCES.json](SOURCES.json) binds all seven mandatory replay inputs by SHA256
and Git blob, plus base-context and adapted-source provenance. The actual swap
predecessor is **PR969**, ToikY, head
`d1ee3f46a6167ea54913e070af3161c71a99e1f2`; PR1145's PR971 reference was a
narrative misidentification. The bytes are correctly retained in the swap-run
package. Pending PR1145 head `fd4d5ffc448361297e717aa30eafed578caf8e61` supplies
the adapted finite-search/census implementation, with its scope stated separately.
[NOTICE.md](NOTICE.md) preserves predecessor credit and AI disclosure.

No nine-operation exclusion, unrestricted circuit optimum, surrounding-run
optimization, native/physical/phase replay, new hosting/invoice/precision/tape
admission, all-size compilation or multiplication theorem is claimed. See
[VALIDATION.md](VALIDATION.md) for executed checks and [CLAIM.md](CLAIM.md) for
selection, bounded domain, overlap and handoff.
