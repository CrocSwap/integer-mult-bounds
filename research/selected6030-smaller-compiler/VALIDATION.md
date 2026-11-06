# Validation and explicit coverage

Author-side validation on 2026-11-06, Linux x86_64, CPython 3.12.14,
standard library only. The scientific witness is fixed at `v=370`, `p=37`,
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

All 15 mathematical/source exports come from the pinned merged canonical
base `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. Their exact Git blobs and
SHA256 digests are checked before execution. No pending #6390 or parallel
sharp-net theorem is consumed. Selected native admission is inherited from
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
and all original source refs are the same merged base, with no fork-only
or pending-head source dependency.

## Publication and standalone export checks

The committed-byte and POSIX executable-mode preflight passes for all 28
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
