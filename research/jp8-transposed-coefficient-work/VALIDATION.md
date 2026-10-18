# Validation record

Base `c290b7b919790300e14004a75d8d24b55ca3c5b5`; completed 2026-10-13.
Windows Python 3.14.0 and Ubuntu 24.04 / WSL Python 3.12.3 both pass the
literal replay, independent integer replay and five packaging tests.

```sh
python3 -I -B research/jp8-transposed-coefficient-work/verify.py
python3 -I -B research/jp8-transposed-coefficient-work/independent.py
python3 -I -B research/jp8-transposed-coefficient-work/test_package.py
python3 -I -B research/jp8-transposed-coefficient-work/native_replay.py --output NEW_DIRECTORY
```

Completed coverage:

- 1,091 transposed blocks and 6,776 arbitrary local input columns, including
  dirty private work; exact full paired primitive replay on 725 columns in
  each orientation, including all dirty helpers and private inputs.
- Exact counts 224,422 / 224,470; complete positive prefix envelopes identical
  to the pinned 64/101-bit original values; all paid children and non-scalar
  event hashes retained.
- Separate integer-grid matrices and integer/exponent full backward prefix
  recurrence; both original and companion isolated prefixes checked.
- All 377 isolated-prefix growth cases recorded, including worst ratio 40/9;
  explicit four-quarter-source counterexample with original/new prefixes 2/4.
- Ten construction controls and four independent controls reject incorrect
  clearing, signs, order, scaling, endpoints and excessive intermediate growth.
- The unchanged native auditor checks the original macro frame/wrapper
  contract in a fresh scratch directory and rejects its 25 controls.
- Five packaging tests execute with `-O -I -B` from a different working
  directory. A minimal copied tree needs only this package and six pinned
  source files. Equivalent gzip recompression passes without writes; source,
  vendor, companion and receipt mutations are detected. The independent
  checker remains runnable after deliberate corruption of the unused vendor.
- All six runtime input bytes match Git blobs at the base. The vendored
  constructor is byte-identical to the named file in PR811 commit
  `b5c244c916dd0b30957332edad7ae7ae22b0eb9d`.
- Ruff 0.17.0 passes for all new/vendored Python sources. Selected-record
  integrity passes for the current #741 fraction
  `1661202643272239/1000000000000000000`. Staged whitespace and focused diff
  checks pass.

No full repository suite, full selected cold reconstruction, global invoice
or admission regeneration, Lean, or remote CI pass is claimed. The native
check concerns the unchanged original macro word; the new private-work
lowering is verified separately and has not been admitted into production.
The finite cost changes remain historical #626 results, with no claimed
transport into #741 and no new kappa.
