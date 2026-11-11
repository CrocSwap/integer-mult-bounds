# Validation and evidence boundary

Executed on Linux x86_64, CPython 3.12.14, standard library only,
2026-11-10. Scientific base:
`e54523517d0f03e58352e647c403a5af3e525a57`.

## Registered checks

From repository root:

```sh
python3 -B scripts/research_package.py --package research/stratified-owned-reserves --check-only
python3 -B scripts/research_package.py --package research/stratified-owned-reserves
```

The metadata and eleven live byte/Git-blob pins passed. The full registered
replay passed both ordinary and optimized exact checks and the separate
subprocess boundary suite. The deterministic mathematical receipt digest
in both modes was
`8127af69796828d95423a5ecdbc1e282a06b9e82784e30122d02e89d5606ac17`.
The final marker was
`PASS_REGISTERED_RESEARCH_PACKAGE research/stratified-owned-reserves outcome=partial`.

The exact finite counts are in RESULT.json:

* 512 finite stage graphs, 12,384 independently enumerated paths, plus 351
  bounded source-refined six-stage paths and a separate three-tape weighting.
* A 31-node complete sibling history with restored origins and separately
  retained maxima; controls show why entry backing, external factors and
  coordinatewise historical maxima cannot be omitted.
* 60,600 smaller-width stock checks, 1,188 envelope monotonicity checks and
  the exact symbolic N=2/rho=1/250 discontinuity with depths 2904 and 2903.
* 118 complete Cartesian reservation coordinates, with inverse maps,
  stage-local changes/restoration and one-time row padding.

The independent bounded path checker does not use Bellman updates to expand
routes. The written induction proves arbitrary finite histories. Small graph
and stock checks are corroboration rather than a universal proof by search.
The q=3 unit-coefficient and GL2 examples are algebraic controls only.

## Rejection and isolation

`test_boundaries.py` creates a disposable mirror containing the package and
exactly its eleven declared source inputs. It executes successful normal
and optimized Git-free replays, then independently corrupts three real
inputs and requires the appropriate failing subprocess result:

1. The receipt schema integer `1` is changed to Boolean `true`; Python's
   untyped equality would identify them, but complete typed canonical JSON
   equality rejects, also with `-O`.
2. A source byte suffix is appended; its SHA256 gate rejects.
3. A radix embedding factor four is replaced by one; the source-refined
   graph certificate comparison rejects with `-O`.

The original bytes are restored between controls and a final good replay
passes. The package's normal verification is read-only. It compiles its own
model directly from source bytes rather than loading an existing bytecode
cache; the generic registered runner also supplies its isolated cache.

## Unrun and unresolved

No full selected supplier replay, emitted numerical dispatcher, huge final
compiler instance, hosted CI, Lean/kernel proof or independent human review
was executed or claimed. The exact .0034 base space contract, actual local
coefficients, width maxima, source root generation, common format and stock
fit remain premises as stated in PROOF.md. No physical tape tariff, complete
running-time improvement or changed κ is inferred from these checks.

## Separate review

The analytic research worker independently reviewed the proof and selected
source boundaries, then implemented a descending-path/geometric-tail checker
without the author's bounded-depth enumeration. Its portable review, exact
receipt and code are included in independent-review. The receipt binds
PROOF.md and stack_model.py by SHA256, eleven live scientific source inputs,
1,068 coordinate certificates, 4,920 descending paths and four controls.
Normal and optimized replays pass. Historical catalogue/selected provenance
remains bound by the generic metadata validator, rather than requiring those
working files never to change after this frozen scientific base.

The author checkpoint efb348fbb7cd39b5c8e9b41043774e7f468502bb passed the
committed-byte/mode preflight for all 24 then-existing package/live-input
files. The integrated review receives fresh registered and committed-byte
checks before publication; remote publication is a separate coordinator gate.
