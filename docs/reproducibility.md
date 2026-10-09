# Reproducing the result

For the three-stage cover extension, run `make three-stage-cover-verify`.
The [incremental guide](three-stage-cover.md) covers the new PR #117 local
word, cover moments and exact assembly.

For the partial-gauge extension, run `make partial-gauge-verify`. Its
[incremental guide](partial-gauge.md) separates the pinned PR #97 bit input,
new complex producer and exact assembly.

For the new stopped product-ring extension, run `make stopped-product-verify`.
Its [incremental reproduction guide](stopped-product.md) covers the h24
rational-center producer, new moments, stopping parameters and assembly.
The community checkpoint and historical targets below retain their own scope.

The selected release is documented in the [joint-frame community review](research/community-round2-review.md)
and [current status](research/current-status.md), with the
[selected parameter certificate](../research/matrix-exponent-synthesis/candidate/arithmetic.json).
The bound is conditional on the retained original #109 framework. Earlier notes,
patches, and the [preserved research](research/preserved-research.md) are historical
reproduction targets. Run `make verify-research` to regenerate its certificates;
the expanded tests also run in `make verify-tests`.

## Requirements

The verification path needs Python 3.11 or newer, Git, Make, and a C++17 compiler supporting
unsigned 128-bit integers and OpenMP (GCC, or Clang with libomp), with no
third-party Python packages. The enlarged-frame profiler additionally needs Boost
multiprecision headers (`libboost-dev` on Ubuntu); the ordinary joint-frame
witness does not use Boost. Run commands from the repository root. All input
source files are bundled, so verification runs without network access.

The local preparation checks used Python 3.14.6 and Tectonic 0.16.9. The supplied
GitHub workflow targets Python 3.11, 3.13, and 3.14 on Ubuntu 24.04; a workflow
configuration is not a claim that those hosted runs have already passed.

## Arithmetic, identities, and patches

```sh
make verify
```

This command performs these steps:

1. `scripts/certify.py` checks the pinned source hashes and parameter inequalities,
   then writes `certificates/parameters.json`.
2. `scripts/search_network.py` encloses logarithms with exact rational arithmetic,
   checks finite candidates and the infinite tail, and writes
   `certificates/network-search.json`.
3. `scripts/make_patch.py` regenerates seven parameter-only patches against the
   unchanged upstream files.
   `scripts/nonadjacent.py` and `scripts/make_nonadjacent_patch.py` additionally
   generate the follow-up routing certificate and three scheduling patches.
   `scripts/tune_routing.py` generates the tuned 2^-76 certificate and combined patch.
   `scripts/reuse_network.py` and `scripts/make_reuse_patch.py` generate the
   stage-sharing 2^-75 certificate and standalone combined patch.
   `scripts/incidence_network.py` and `scripts/make_incidence_patch.py` generate
   the incidence-circuit 2^-67 certificate and standalone combined patch, including
   exhaustive verification of the underlying ordered-pair rectangle partition.
   `scripts/dag_network.py` and `scripts/make_dag_patch.py` generate the
   shared-computation 2^-63 certificate and standalone combined patch. They
   check the exact symbolic linear map and both support-frame directions of
   the reversible circuit compiled by `scripts/exclusion_circuit.py`.
   `scripts/shared_point_network.py` and `scripts/make_shared_point_patch.py`
   generate the cross-group sharing certificate and independent patch for
   kappa=13*2^-66. They check exact supports and both frame directions in the
   global graph compiled by `scripts/shared_point_circuit.py`.
   `scripts/paired_network.py` and `scripts/make_paired_patch.py` generate the
   h=50 paired-network certificate and independent patch for kappa=2^-59. They
   also check the stopped guard constants and revised Gaussian inequalities;
   these proof models are selected explicitly in the parameter checker.
   `scripts/prepare_layers.py` records generalized guard and unequal-exponent
   recurrence estimates, the independent complex-family search, and clearly
   marked hypothetical sparse-primitive targets in `layer-preparation.json`.
   This preparation pass does not change the published 2^-59 witness.
   `scripts/audit_sparse_fusion.py` records finite phase identities, a bounded
   central-frame screen, and the cost targets for future sparse primitives.
   Its output is a research audit, not a stronger multiplication certificate.
   `scripts/audit_fused_block.py` checks a complete parity-butterfly sandwich
   and records the cut-rank obstruction for coordinate-child/pointwise-only
   recursion. Its exact identity does not supply a faster multiplication bound.
   `scripts/audit_short_guards.py` records logarithmic working guards and a
   reduction to a still-unproved fast gathering routine. Exact address tests
   check the reduction's maps, not a new tape-time or multiplication bound.
   `scripts/audit_gather_schedules.py` checks a reversible merge tree, scoped
   interval-schedule obstructions, and optimistic round-reuse accounting.
   It does not rule out coded gatherers or certify a new multiplication bound.
   `scripts/audit_coded_carries.py` checks an exact but linear carry code and
   small controls for a scoped flat affine-circuit obstruction. The bounded
   attempt supplies no sublinear recurrence or new kappa.
   `scripts/audit_cancellation.py` checks the first cancellation circuit's
   scalar map and dirty-scratch restoration, then records nonorthogonal-path
   bounds rejecting two topologies under the retained data-stage frames.
   `scripts/audit_joint_frames.py` reproduces a complete small bit invocation's
   edge ranks and checks rational controls for the fixed-boundary local
   optimality proof. It does not certify a stronger multiplication bound.
   `scripts/audit_compact_controls.py` checks the compact dirty-control address
   maps, inverses and exceptional repair. `scripts/compact_control_layer.py`
   records the new conditional `83/10^12 > 2^-34` witness, with reservations,
   the revised recurrence, independently sized complex motif, generalized
   guards and all assembly margins. Its general tape claims depend on the
   written [compact-control proof](../notes/compact-control-note.tex).
   `scripts/make_compact_control_patch.py` generates the independent combined
   patch, including the changed global exceptional-stream accounting.
   `scripts/complex_compression.py` records the follow-up weighted complex
   circuit, binary phase-frame audit and conditional `2^-31` witness.
   `scripts/make_complex_compression_patch.py` integrates that interface and
   all downstream constants into an independent complete upstream patch.
   The earlier compact-control certificate and source patch remain unchanged;
   see the [construction and integration boundary](research/complex-compression.md).
   `scripts/research_networks.py` and `scripts/search_network_variants.py`
   record scoped family bounds and clearly marked exploratory scores.
4. The standard-library unittest suite checks certificate boundaries, selected
   finite identities, network counts, patch dependencies, and search bounds.
5. Git checks that each alternative patch applies to the pinned source.

The generators overwrite their output certificates and patches. To confirm
that the checked-in outputs reproduce exactly, run on a clean checkout:

```sh
git diff --exit-code -- certificates patches
```

The compact-control note builds with `make compact-note`. Its statement remains
conditional on the identified upstream interfaces and supplied written
extensions. See the
[current research status](research/current-status.md) before treating older
research pages or preparation certificates as current conclusions.

The theorem certificates and all-h bound comparisons use `fractions.Fraction`;
no floating-point result controls their acceptance. The separate exploratory
higher-subset screen uses floating point to select candidates, then encloses
their scores exactly; it certifies neither a new construction nor optimality.
Sampled finite identity tests use fixed random seeds.
Passing these checks does not prove the full multiplication-machine theorem.

## Apply one patch for review

The following creates a fresh local review directory and refuses to reuse an
existing one. It leaves the bundled source untouched:

```sh
mkdir -p build
mkdir build/review
cp -R upstream/build build/review/build
git apply --directory=build/review patches/ternary-30.patch
```

Read `build/review/build/main.tex` and its included sections. The other patches
are alternatives based on the same original manuscript, not successive commits.

## Build the note

With Tectonic installed:

```sh
make ternary-note
```

The result is `artifacts/ternary-note.pdf`. Build the preceding
compact-control note with `make compact-note`. Build the earlier
parameter-only note with `make note`, producing `artifacts/parameter-note.pdf`.
Build the separate routing audit
with `make audit-note`, producing `artifacts/nonadjacent-axis-note.pdf`.
Build the tuning note with `make tuned-note`, producing
`artifacts/routing-tuned-note.pdf`. Build the preserved stage-sharing note with
`make reuse-note`, producing `artifacts/stage-reuse-note.pdf`.
Build the rectangle-circuit note with `make incidence-note`, producing
`artifacts/incidence-note.pdf`.
Build the shared-computation note with `make dag-note`, producing
`artifacts/dag-note.pdf`.
Build the cross-group and paired notes with `make shared-point-note` and
`make paired-note`, producing `artifacts/shared-point-note.pdf` and
`artifacts/paired-note.pdf`, respectively.
Build the local complex-network follow-up with `make complex-note`, producing
`artifacts/complex-compression-note.pdf`.
The first run may download fonts
and TeX packages; the numerical verification does not use them. PDF builds may
differ in metadata or typesetting across TeX environments. The exact-byte
reproducibility check covers JSON certificates and patches, not the PDF.

Full patched-manuscript previews were also compiled during preparation. With
Tectonic, the original pdfTeX-only metadata commands `pdfinfoomitdate`,
`pdftrailerid`, and `pdfsuppressptexinfo` must be commented out in a disposable
copy. Those preview-only edits are not included in the mathematical patches.

## Source provenance

The pinned upstream revision is
`adc7f1241b42e322a6451854ab7e4b4c146bf78a`.
[The manifest](../upstream/manifest.json) records each source URL and SHA-256
hash. `make fetch` downloads that exact revision and refuses to overwrite
changed source files. Fetching is optional and requires network access.

## Automation

[The verification workflow](../.github/workflows/verify.yml) runs `make verify`
and rejects changes to regenerated certificates or patches. It uses immutable
commit pins for the official [checkout](https://github.com/actions/checkout)
and [setup-python](https://github.com/actions/setup-python) actions, with
read-only repository permissions. The PDF is supplied for readers and can be
rebuilt locally using the command above.

Build the latest note with `make ternary-note`. The earlier notes and
patches remain available as independent witnesses.

## Ternary construction

The full `audit_ternary_side.py` constructs about 21 million addition nodes
and uses multiple gigabytes of memory. It verifies exact support keys,
pruning and role counts, and independently expands complete h=8,9 controls.
`make_ternary_patch.py` checks the certificate's source hashes before generating
the independent patch. Its twelve focused tests are in `test_prime_core.py`,
`test_ternary_side.py`, and `test_ternary_patch.py`. The source-hash manifest
includes the standalone exact Kronecker-product helper used by the compiler.

No exploratory overnight search is required by this release. All prior
certificates, patches and bundled upstream files are preserved unchanged.

## Imported candidate reproduction (pending maintainer review)

The following contributor instructions are retained from PR #39 at
`70ae24129649f6d6d4ec6360962a80c3c42a38f1`; their past validation statements
describe contributor runs, not this integration run. See
[the integration ledger](research/community-integration.md) for maintainer results.

# Reproducing the current result

Run from the repository root with Python 3.11+, a C++17 compiler supporting
unsigned 128-bit integers (GCC or Clang), Git, and Make. No third-party
Python package or network access is required.

```sh
make copied-centers-verify
```

The incremental target:

- Matches the unchanged positive-label bit producers at h25 and h23 to
  the previously verified partial-swap certificate.
- Recomputes all 47 rational corner pivots and verifies all 315 symbolic
  zero-minor partitions using 630 exact integer-rank calculations.
- Regenerates the new h28, d19 mixed-center complex producer, checking its
  scalar supports, center coefficients, binary frames, matching and histogram.
- Applies the copied-center histogram replacement, reconstructs both complete
  child lists and checks both strict moments, the semantic precision guard,
  product row stock, seven margins and 47 strict assembly constraints.

The copied-center scheduling and simultaneous rational-basis arguments are
written proofs. The finite checks establish their selected arithmetic inputs.
Unchanged historical producers and suites are skipped. Intermediate graphs
and compiled tools are temporary; `--work-dir PATH` retains them if needed:

```sh
python3 scripts/copied_centers_producer.py --work-dir /tmp/copied-centers-producers
```

For arithmetic alone, use `make copied-centers-certificate`. `make verify`
also runs inherited checks, including the previous structured-bulk target.

## Proof and dependencies

The proof is supplied as [LaTeX source](../notes/copied-centers-note.tex).
No PDF is generated for this submission. The selected
[two-stage and corner sources](../references/copied-centers/README.md) and
[semantic/analytic sources](../references/semantic-bulk/README.md) retain
original licenses, notices and hash manifests.

[SOURCES.json](../SOURCES.json) pins the archive, parent and contribution
sources. Raw graphs, alternatives, terminal-eligibility experiments and
recursive copies of predecessor archives remain outside the submission.
The [historical manuscript patch](../PATCHING.md) retains the #10 result.
