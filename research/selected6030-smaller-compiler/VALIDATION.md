# Validation and explicit coverage

Author-side validation on 2026-11-06, Linux x86_64, CPython 3.12.14,
standard library only. The primary scientific witness is fixed at `v=370`, `p=37`,
`h=5550`, `H=1449000000000`; no source native word or selected record is edited.

## Executed

```
python3 -I -B research/selected6030-smaller-compiler/verify.py
python3 -I -O -B research/selected6030-smaller-compiler/verify.py
python3 -I -B research/selected6030-smaller-compiler/independent_oracle.py
python3 -I -O -B research/selected6030-smaller-compiler/independent_oracle.py
python3 -B scripts/research_package.py --package research/selected6030-smaller-compiler --check-only
python3 -B scripts/research_package.py --package research/selected6030-smaller-compiler
```

The metadata/source-pin check and both registered modes pass. Each scientific
run compares the same entire deterministic RESULT.json, ending with
`PASS_SELECTED6030_SMALLER_COMPILER`; each takes about one second locally.
Frozen source functions are compiled directly with `optimize=0`; local checks
use explicit exceptions and remain active under interpreter `-O`.

The source-event invoice and the original assembly/path-length recount agree
with every selected paid and target bin. All complete net taxes, full paid
log-law excess, base range, 38 polynomial coefficient comparisons, final
integer rank, nine outer rows, 54 strict checks, four functional checks and
ordinary BIT/stock gates pass. The original selected coarse moment and final
integer threshold are reproduced as positive controls.

Controls reject the stated product 369, degree 36, loss of concentration,
sublinear tail, missing paid call, omitted whole idle, changed source bytes,
free completion and the preceding height grid. A dropped original-paid tail
produces a deliberately demonstrated false positive. The formal signed toy
inventory checks the exact net-gap identity before numerical moments.

A separate author-side AI worker read the proof, code and pinned source
contracts and reran `python3 -I -W error -B verify.py`. It found no substantive
blocker in the full-versus-net completion budget, capped-reference moment
normalization, strictified count bounds or fresh-constant prescription.
This is not independent human or proof-kernel review.

The lead separately implemented `independent_oracle.py`, without source compiler
imports. In both normal and optimized registered runs it reconstructs all 38
log-moment bounds using 371 exact binomial probabilities, then independently
reconstructs all 38 numerator and 38 denominator coefficients using iid moment
convolution and Newton forward differences. Its five 100-digit Decimal checks
corroborate the separate rigorous interval proof. The exact grid comparisons
and reduction factor also agree. `REVIEW.json` records the exact hashes of the
proof, primary verifier, witness, receipt and separate oracle.

## Source and overlap coverage

All 15 primary mathematical/source exports come from the pinned merged canonical
base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Their exact Git blobs and
SHA256 digests are checked before execution. No pending #6390 or parallel
sharp-net theorem is consumed by the primary certificate. Selected native admission is inherited from
the authenticated selected record/receipt/review.

Focused public PR searches covered `"6030" "compiler"`,
`"6030" "net-tax"`, `"6030" "concentrated"`,
`"6030" "smaller" "rank"`, `"selected" "net-tax"`, and
`"1449000000000"`, with bounded title/body result sets. The exact-height query
returned no result. The lead's current handoff/overlap check and direct reads
of #4433, #4480, #5787, #6109 and #6390 supplied the relevant predecessors.
This is not an exhaustive search of arbitrary diffs or unpublished work.

## Not executed or established

No complete selected cold replay is claimed. The lead's source-orientation
baseline could not complete in the sparse checkout because the historical
`certificates/checkpoints/frontier4359.json` dependency was absent; it was
not reported as PASS and the 1,405-file selected closure was not hydrated.
The local native operator, all-column ownership/phase proof, rounded
multiplier, numerical complete uniform-word constants and full physical
threshold are inherited or unmaterialized. No native suite, Lean, Docker,
physical tape execution, hosted CI, human acceptance or proof-kernel proof
ran for this application.

The checkout is shallow. The optional full-history source-ancestry preflight
cannot establish full history here; exact source bytes and self-contained
replay are separate checks. Every mathematical input is inside the package,
and all primary source refs are the same merged base, with no fork-only
or pending-head source dependency in that primary result.

## Publication and standalone export checks

The initial publication committed-byte and POSIX executable-mode preflight passed for all 28
package files. The official export and declared-input coverage check pass;
the archive contains those 28 files plus its generated integrity manifest.

```
python3 -B scripts/check_research_commit.py --package research/selected6030-smaller-compiler --check-modes
python3 -B scripts/export_research_package.py export --package research/selected6030-smaller-compiler --output /tmp/selected6030-compiler.tar.gz
python3 -B scripts/export_research_package.py check /tmp/selected6030-compiler.tar.gz --check-inputs
```

The archive was extracted outside the repository with file modes 0444 and
directory modes 0555. Using the absolute CPython executable, empty PATH,
`-I -W error -B`, and then `-I -O -W error -B`, both the primary verifier and
independent oracle passed. The primary runs took 0.640 and 0.892 seconds;
the independent runs took 1.478 and 1.647 seconds. Every one of the 29
exported file hashes and modes stayed unchanged. No Git executable was
available through PATH; neither verifier uses the network. Hosted CI remains
separate and was not observed by this worker.

## Optional joint example validation

The optional joint example adds the explicitly pinned pending sharp-net proof
at fork head `a0ef8b7ae2592202247b15da453ce42598863a26`. Its frozen bytes and
source metadata are separate from the unchanged primary source inventory.
The primary proof, verifier, witness and receipt retain their original hashes.
Direct scientific runs passed in normal and optimized isolated modes:

```sh
python3 -I -B research/selected6030-smaller-compiler/joint_verify.py
python3 -I -O -B research/selected6030-smaller-compiler/joint_verify.py
python3 -I -B research/selected6030-smaller-compiler/joint_independent_oracle.py
python3 -I -O -B research/selected6030-smaller-compiler/joint_independent_oracle.py
```

Each joint verification first reproduces the complete original primary receipt,
then authenticates the pending proof, checks turning signs and stationary-root
brackets, recomputes the complete gap and full paid-log mass, checks every
coefficient of both tuples, and checks ordinary bases, final integer grids and
all unchanged outer predicates. Both compare the same JOINT-RESULT.json.
Controls reject v=365 and p=35 in the stated certificates and detect the false
positive from dropping the original tail. The new raw-instance recurrence is
independently iterated. The separate oracle reconstructs all 38+37 moments and
numerator/denominator coefficients by binomial mixtures and Newton differences,
without importing the scientific compiler. Full native, physical, precision
and global-optimality limitations remain unchanged.

A second separate author-side agent supplied an independent Fraction-series
interval oracle for the new coefficient, with explicit log/exp tails and four
negative controls. Its only publication edits add attribution and remove the
receipt write. Normal and optimized stdout agree exactly. `joint_oracles.py`
runs it and the independent binomial/Newton oracle in each mode, keeping the
registration within the repository's eight-command limit. JOINT-REVIEW.json
binds both separate AI reviews and all optional scientific artifacts by hash.
These reviews do not constitute independent human or formal acceptance.

For the optional addition, committed-byte and executable-mode checks passed
for all 38 package files at `e1fc47ef819661210aa5cd0050332e7034d1bf4c`.
The official exporter and declared-input check passed. That archive was
extracted outside the repository with files 0444 and directories 0555.
All four registered scientific entry points passed both normal and optimized
isolated modes with warnings as errors and an empty PATH. The 39 exported
file hashes and modes, including the generated integrity manifest, remained
unchanged. This final documentation-only record changes no scientific artifact
or registered command. Hosted CI was not observed.
