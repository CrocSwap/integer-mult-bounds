# Local validation

Executed on October 12, 2026 (PDT; October 13 UTC), on macOS 27.0.1 arm64,
CPython **3.14.5**. Exact base:
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.

The following passed on the final executable implementation:

```sh
python3 -I -B research/complex-compensation-basis/verify.py
python3 -I -B -O research/complex-compensation-basis/verify.py
python3 -I -B research/complex-compensation-basis/test_verify.py
python3 -I -B research/complex-compensation-basis/search.py
make selected-record-check
```

The two strict verifier modes reproduce every EXPECTED.json field. Both run
all 716 input columns of original and candidate scalar programs in forward
and inverse-transpose orientations. The new boundary also receives a separate
Fraction replay. The unmodified native emitter and independent local auditor
accept the changed canonical word, with all **25 native controls** rejected.
All **10 new controls** and **six focused tests** pass. The 124,320-choice
bounded search reproduces RECIPE.json and all per-pair prices exactly.

Additional package checks passed in a minimal copied checkout containing only
this directory and the eleven files named in SOURCES.json:

- A relocated checkout whose path contains spaces, with isolated optimized
  Python, reproduces the complete certificate (about 5 seconds locally).
- Both gzip inputs recompressed at level 1 with a different timestamp are
  accepted. Mathematical equality uses their entire decompressed payload.
- Appending a single whitespace byte to the decompressed canonical word is
  rejected at `source pin`, before native execution.
- Adding a newline to the pinned native emitter is rejected at `source pin`.
- A recipe claiming one extra saved primitive is rejected by the independently
  recomputed fully paid pair price.
- A certificate claiming one extra saved primitive is rejected at
  `certificate mismatch` after fresh recomputation.
- With `PYTHONOPTIMIZE=2` in the environment and the parent running under `-O`,
  native subprocesses still execute under `-I` with assertions enabled and
  reject all 25 controls.
- All six focused tests pass in the minimal checkout under `-I -O` too.

The timings are reproduction observations, not a before/after performance
benchmark or runtime-speedup claim. All test-generated native files were
confined to temporary directories. No tracked source artifact was regenerated.
Staged whitespace and local documentation-link checks pass. The final diff
is confined to `research/complex-compensation-basis/`.

The source operator, recipe and certificate are pinned independently of Git's
current branch name, so a clean checkout can replay without remote access.
The frozen source payloads match the selected #626 SPEC. The source code has
no third-party Python dependency. A second Python version was not available
on PATH and is not claimed tested.

No full `make verify`, selected cold construction rebuild, fresh global
hosting/invoice/outer admission, remote Linux CI or Lean run was performed.
Those are not consequences of this isolated local construction. The source
supplier and selected result were not changed. No independent human review
or delegated-agent review is claimed.
