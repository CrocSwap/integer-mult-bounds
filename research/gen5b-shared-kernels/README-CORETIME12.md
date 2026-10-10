> Historical final12-only checkpoint. For the combined 70/72 construction and
> the current 16-file acquisition manifest, use [README.md](README.md).

# A 12-helper co-retiming proposal on pinned PR #299

This is a standalone changed-stage verifier and conditional research proposal.
It adds no changes from PR #299 to `main`, and does not depend on PR #294.
PR #299 is an unmerged dependency, not an already available `main` package.

The proposal introduces 12 early helper restorations while undoing six old
restorations, with coordinated root and partner deliveries. Its measured local
paid histogram delta is `{1: +18, 2: -12}` and its residual-family delta is
`{2: +12, 3: -18, 4: +6}`. Under the retained PR #299 admission and all-size
interfaces, the resulting exact arithmetic gives:

- Bit coarse saving: `750469712644613 / 10^18`
- Conditional kappa: `749906929903449 / 10^18 = 0.000749906929903449`
- PR #299 comparison: `0.000749899215319498`
- Literal stock: `1,229,735`, down by 15
- Unreplicated paid calls: `482,665`; rank mass: `2,455,070`; deficit: `4,400`

The gain is `7714583951 / 10^18`, about 0.001029% of PR #299's kappa.
All identified changed-stage obligations pass the checks in this packet,
conditional on the retained source/compiler interfaces. This is not an
unconditional multiplication bound or a full replay of the inherited finite
admission. The earlier optimistic 32-helper price omitted
partner-carrier work and is superseded; it is not a result of this package.

## Dependency and data acquisition

The final12 component uses eleven inputs pinned to PR #299 head
`5f6bd3fbc0e6796dd31263cef1f06dc968186f64`, under
`research/five-stage-gen5b-kernels-restorations-sinks`.
[Immutable source package](https://github.com/CrocSwap/integer-mult-bounds/tree/5f6bd3fbc0e6796dd31263cef1f06dc968186f64/research/five-stage-gen5b-kernels-restorations-sinks).

`inputs.json` records each exact byte count, SHA-256 and Git blob SHA-1. Large
word, frame and selection files are deliberately not duplicated here. The
loader rejects missing, altered or unpinned data before parsing it.

From this directory, use Python 3.11 or newer, without optimization (`-O`):

```sh
python3 -B fetch_inputs.py --destination /tmp/coretime12-inputs
export CORETIME_SOURCE_DIR=/tmp/coretime12-inputs
python3 -B -m unittest discover -s . -p 'test_*.py' -v
python3 -B run_coretime12.py --check
```

The fetcher retrieves only the immutable public files listed in `inputs.json`
from GitHub and verifies their bytes. It never runs a downloaded producer,
installs a dependency or imports upstream Python. It needs network access only
for missing data. An existing directory is verified rather than overwritten.

In this combined package, `verify_all()` additionally requires the five pinned
PR300 files. The current `inputs.json` and main [README.md](README.md) acquisition
step cover all sixteen files. A PR299 package directory alone, or a normal main
checkout, is therefore insufficient. The source root can be anywhere; all
checks work independently of the current working directory.

To regenerate the compact receipts, explicit bank-address table and full chart
factor programs elsewhere:

```sh
python3 -B run_coretime12.py --output-dir /tmp/coretime12-results --check
```

Add `--write-streams` to save both complete scalar suffixes as compressed JSON.
The generated streams, full bank-address table and full matrix/factor listings
are not committed; their deterministic reproducer and digest receipts are.

## Verification coverage

- Exact local integer-map and source-span checks select 12 compatible helpers
  from the independently reproduced candidate census.
- The complete 55,985-addition changed suffix preserves all 18,954 independent
  entry columns forward and backward over F2 and over the integers. Sources,
  targets and dirty entries are arbitrary, rather than initialized to zero.
- Exact nonnegative coefficient majorant operators also agree in both
  directions. A separate 172,944-swap commutation certificate proves signed
  equivalence and a conservative factor-two scalar-norm bound.
- All 60 affected chronological frame paths are checked over the rationals,
  including 212 containments and the 12 inherited post-descent partner setups.
- All 18 changed endpoint charts are constructed and exactly factored. They
  use at most 142 factors, within the retained 576-chart/815-normalizer bounds.
- Explicit role-to-bank assignment covers all 15,427 helpers and 925,620
  role/replica occurrences per stage, with five disjoint stage namespaces.
  A full-width bank packing witness, exact moments, all 47 outer inequalities,
  and rejection of both adjacent coarse and kappa grid points are recomputed.
- The changed displayed finite bill is `90386288803484701`, below `2^80`;
  the conservative payload bound has 103 bits, below the retained `2^104` cap.
- Mutation controls reject missing restoration, missing partner promotion,
  missing bank capacity, incompatible frames, invalid arithmetic inputs and
  altered source data.

See [PROOF-CORETIME12.md](PROOF-CORETIME12.md) for the surgery and accounting argument,
`certificates/coretime12/` for exact reproducible receipts, and [NOTICE.md](NOTICE.md)
for contributor attribution and AI-assistance disclosure.

## What remains conditional

The pinned unchanged prefix and its original admission are inherited. The
unchanged finite compiler, weighted compilation, routing, prime, setup and
all-size interfaces are not rerun here. The displayed finite-bill check does
not assign a value to the source theorem's unknown full constant `C_full`.
Its positive bridge inputs remain conditional on the retained finite bridge.
The bit payload contract remains F2; the stronger integer suffix identity does
not assert that the whole parity-filtered supplier is an integer decoder.

Neither repository-wide `make verify` nor the inherited full admission suites
were run: only newly authored verifier programs execute. Passing these checks
does not establish a full machine-checked multiplication theorem. No production
guard, selected main certificate or inherited manuscript patch is modified.
