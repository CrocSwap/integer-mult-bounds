# Validation record

The checks ran on 2026-10-13 with CPython 3.14.7 on macOS 26.6.1 arm64.
They used the standard library and one CPU thread.

```sh
python3 -I -B research/k8-frame-antichain/verify.py
python3 -I -O -B research/k8-frame-antichain/verify.py
python3 -I -O -B research/k8-frame-antichain/independent.py
```

All commands passed. The primary checker also passed from an unrelated
directory after the package was copied to a path with spaces. Its normal
and optimized results matched the same certificate.

The primary checker rejects five mathematical controls at their specified
conditions: a repeated demand frame, a comparable frame pair, a changed
demand coefficient, a substituted target label that permits a whole
block, and an omitted low cleanup tail. The last control includes all
arbitrary input columns and fails at exact helper restoration.

Two separate package controls ran against a temporary copy of the
actual command. Removing one certificate value witness failed with
`certificate differs from replay`. Changing one scalar coefficient in
the compressed word failed with
`input pin mismatch: SEVEN-SLOT-WORD.json.gz`. The input and certificate
were restored after each case. No source pin was weakened for a control.

The independent checker imports no primary-checker code. It uses 112
separate scalar column replays to check the 192 value witnesses. It
checks the antichain with explicit sets of binary points. It checks all
112 split ranks with integer determinants, rather than Gaussian
elimination. It also checks every cap witness and the four-cap escape.
Both implementations were prepared with AI assistance. This is not a
claim of external human peer review.

The sharp upper witness is executed by the primary checker: all 728
ADDs in all 14 packet programs, the 112-source partition, the 24-register
allocation in each program, monotone common frames, clean support
containment, and all 192 required values. The upper bound is not inferred
from a field that merely reports a helper count.

The input word's separate native rebuild is recorded in
`BASELINE-REPLAY.md` and `BASELINE-REPLAY.json`. No new full supplier
invoice or kappa was tested. The root coordinator owns the repository
baseline suite and any full cold replay. This package changes neither
the selected result nor `upstream/`. Hosted CI and a formal proof
assistant were not run.
