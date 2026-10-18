# Atlas applications: T372 concentration, mixed-fibre bounds and exact recovery

This package turns selected results from the four-volume pure mathematics atlas (PR #2849) into a checked multiplication allocation, source-bound magnitude bounds, concrete dirty-state reader adapters, and two exact erasure-recovery tools.

The T372 construction supports the conditional target

**κ = 0.001718659357407250209979 − 10⁻⁴⁶ − 10⁻⁷⁰.**

It improves the full pinned PR #2848 headline by exactly 21227558005129/25000000000000000000000, approximately 8.4910232020516 × 10⁻¹⁰. The newer PR #2853 claims approximately 0.0017193776586975866590 using different native words, so this checked allocation is not the current numerical frontier. The package does not present its smaller number as superior. The final refresh and bounded composition check are recorded separately.

## Concrete results

- **Feasible rank concentration:** three literal role transfers in 372 interleaved replicas, with 1,365,984 helper roles and 3,348 calls checked. The complete normalized paid cost is smaller than PR #2848 for every rank exponent 0 < p < 1. The numerical saving is a consequence of that full profile, not an unpriced local saving.
- **Magnitude control:** the actual eight-stream controller has a uniform boundary norm majorant of 10. Under the checked mixed cover/fibre and complete-endpoint hypotheses, the actual magnitude envelope is 121 bits, or 179 bits retaining the inherited local reserve. A 256-bit magnitude payload is sufficient for that premise. The admitted main candidate retains 2048 bits; denominator, arithmetic-depth, C₀, mass and outer precision checks are separate.
- **Dirty-state reader:** an exact in-place rank 2 involution implements the desired reader permutation on the actual PR #2833 providers, using 234 dyadic scalar operations and no scratch. It is nonunitary and is not inserted into the multiplication circuit.
- **Measurement recovery:** a missing maximal commuting Pauli class is reconstructed exactly. A six-qubit fixture gives 65 mutually unbiased measurement bases, 4,095 nonidentity observables and 4,160 rank-one projector recipes.
- **Pilot recovery:** for every prime p, an exact orthogonal p × (p − 1) matrix of pth-root phases is completed while every received integer phase code is preserved. The tool handles gauges, row/column permutations and signed exponent representatives.

The positive sufficient statements and all proof arguments are in `CONSTRUCTION.md`, `APPLICATION-MAP.md` and the application folders. Standard mathematical ingredients are credited as standard; the finite constructions, source bindings and implementations are the deliverable. No measured hardware, noisy-channel or runtime improvement is asserted.

## Independent offline replay

Python 3.10 or newer with its standard library suffices for the owner, exact rational moment, reader, Pauli and pilot checks. Keep assertions enabled. From this package directory, choose a fresh work directory outside the package:

```text
python -B tools/verify_package.py --work ../atlas-offline-run
```

This authenticates the complete file inventory and every SHA-256, runs the separately implemented source-event and rational moment auditors, checks the actual native reader words, verifies the Pauli fixture with a checker that imports no recovery code, and reruns all 41 pilot erasures plus 13 rejection controls. Generated pilot work is copied outside the immutable package. It then checks that the package has not changed. `--hash-only` performs authentication without replay.

`tools/audit_owners.py` is a credited generalization of PR #2848's independently implemented source-event checker. `tools/audit_moment.py` is a separate integer/Fraction implementation using 128-term logarithm and degree 24 exponential enclosures with explicit positive tail bounds and outward dyadic rounding. Separate implementations are not independent human peer review.

## Complete native and outer replay

The exact PR #2833 source is external to avoid uploading 541 repeated predecessor files. Either export the pinned Git commit using `vendor/pr2848/materialize_source.py`, or fetch the authenticated raw files into a fresh external directory with Node:

```text
node --use-system-ca tools/fetch_source.cjs ../atlas-source
```

The fetch verifies the exact manifest hash and all 541 entries at head `e9307b48d7d1b690939935ecef0f8e524e6d92f4`. It uses ordinary certificate verification. A failed partial download is preserved; choose a new directory for another attempt.

Use Python 3.13 with NumPy, SciPy, SymPy and mpmath installed in the replay environment. The fresh run recorded NumPy 2.5.4, SciPy 1.18.1, SymPy 1.14.0 and mpmath 1.4.1; gmpy2 and psutil were absent. These are the actual versions, not a claim that the predecessor's requirements file was installed exactly. No dependency constraint or source guard was weakened.

On Windows, create an isolated replay interpreter first:

```text
python -B tools/make_lf_runtime.py --out ../atlas-runtime
../atlas-runtime/Scripts/python.exe -B reproduce.py --source ../atlas-source --work ../atlas-full-run --jobs 3
```

The helper uses installed dependency locations read-only and makes `Path.write_text` default to LF inside that isolated interpreter, preserving explicit newline choices. This prevents inherited generated-byte hashes from changing under Windows newline translation. It changes no global configuration, validator predicate or immutable source. On a POSIX system with LF output defaults, run `python -B reproduce.py` with the same arguments directly. A short absolute work path is recommended on Windows.

The default replay runs four fresh native chains, the retained parent and complete owner/hosting/geometry/BIT/precision/outer/release admission. Explicit `--prepared-native` reuse is authenticated and labelled; it is not presented as fresh generation. `--dry-run` prints the authenticated command plan only. The published comparison driver differs from PR #2848's source only by adding the exact pinned PR #2848 comparison record.

## Scope and provenance

The multiplication headline is conditional on the retained all-size compiler, source-access, hosting, precision/tape, recovery, ordinary recursion, BIT and analytic-transfer obligations. A successful finite release checks their stated finite suppliers and arithmetic; it does not replace those hypotheses with a new unconditional asymptotic theorem. This deliverable is informal mathematics plus exact computational certificates. No new Lean theorem, kernel check or transitive-axiom audit is claimed.

`vendor/pr2848/` contains byte-preserved predecessor source and its original claims. Those original T248 claims are references; the current claim is this package's root `CLAIM.json`. Licenses and notices are retained. See `CREDITS.md` for the full relevant PR lineage, explicit PR #2805 reader overlap and the bounded neighborhood-search scope. The canonical Lean tree and authoritative DAG remain unchanged.
