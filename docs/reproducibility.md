# Reproducing the result

The primary artifacts are the [compact-control note](../artifacts/compact-control-note.pdf),
[combined patch](../patches/compact-control-34.patch), and
[exact layer certificate](../certificates/compact-control-layer.json).
They are conditional on the retained algorithmic interfaces and written
extensions identified in the [review guide](research/compact-control-review.md).

## Requirements

The verification path needs Python 3.11 or newer, Git, and Make, with no
third-party Python packages. Run commands from the repository root. All input
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
git apply --directory=build/review patches/compact-control-34.patch
```

Read `build/review/build/main.tex` and its included sections. The other patches
are alternatives based on the same original manuscript, not successive commits.

## Build the note

With Tectonic installed:

```sh
make compact-note
```

The result is `artifacts/compact-control-note.pdf`. Build the earlier
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

Build the latest note with `make compact-note`. The earlier notes and
patches remain available as independent witnesses.


## Ternary five-subset witness beyond 2^-28

Run `make verify` with Python 3.11+, Make, Git and a C++17 compiler (`c++`).
The new scripts use the Python standard library only. Full exact producer
checking requires roughly 1.2 GB memory and under 30 MB temporary storage.
`python3 scripts/prime_field_network.py --quick` checks only the final rational
witness and is not a replacement for the full circuit checks.

`make prime-field-note` builds `artifacts/prime-field28-note.pdf` with pdfLaTeX.
For the full manuscript, copy `upstream/build` to a disposable directory and
apply `patches/prime-field28.patch` with `git apply --directory=<copy>`; or
write the output of `scripts/make_prime_field_patch.py`'s `patched_files()`
over that copy. Compile `main.tex` with pdfLaTeX, run BibTeX, then run pdfLaTeX
twice. Keep the pinned upstream files unchanged. Each repository patch is an
independent alternative, not a patch stack.
