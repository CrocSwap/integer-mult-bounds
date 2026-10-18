# Validation record

Validated on macOS with CPython **3.12.14**, standard library only, on
2026-10-13. Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
The local runtime was
`/Users/evaayala/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3`.
The reproduction commands below use `python3` with Python 3.10 or later.

## Completed checks

```sh
python3 -I -B research/gaussian-nonlinear-copy-floor/verify.py --output /path/to/NEW.json
python3 -I -B research/gaussian-nonlinear-copy-floor/test_package.py
make selected-record-check
```

- Complete primary replay passed with the marker in
  [evidence/full-replay.txt](evidence/full-replay.txt). The newly written
  receipt was byte-identical to CERTIFICATE.json. It covers all **2,579,856
  unordered nonempty flat pairs**, all **640 maximum cliques**, and all
  **60 port-incidence counts**. The unchanged PR738 calculation and its six
  rejection controls are retained; this is not a new independent geometry proof.
- The separately written nonlinear checker passes **49,152 receiver decodes**
  on all **4,096 input tuples**, **4,096 mixed-derivative checks**, and
  **2,621,440 conditional projection assignments** over **559,104 outside
  assignment classes**. Omitted inversion fails on 4,096 receiver cases;
  dropped bits fail on 12,288 / 12,288 / 8,192 receiver cases. Width underpricing
  and illegal side information are explicit correct-code boundary examples.
- All **three focused package tests** passed in 0.468 seconds; output is in
  [evidence/package-tests.txt](evidence/package-tests.txt). They cover zero,
  uniform and concentrated demands on all five maximal-clique sizes; invalid
  demands; five changed receipt fields; source tampering and omission; selected
  source tampering; isolated relocated source checks; deliberate optimized-mode
  rejection; and preservation of an existing output file.
- A minimal copy containing only this package and the nine pinned base inputs
  passed the **complete** isolated replay from an unrelated working directory
  outside the checkout. Its fresh receipt was byte-identical; see
  [evidence/relocated-replay.txt](evidence/relocated-replay.txt). This goes beyond
  the source-only relocation check in the focused tests.
- `make selected-record-check` passed. The selected conditional kappa remains
  `1661634653669567/1000000000000000000`.
- A separate AI worker reviewed the written proof, accounting scope, controls
  and code, and individually checked nonorthogonality and inclusion-maximality
  of all **8,704 maximal cliques**. No actionable issue remained; the bounded
  record and reviewed code hashes are in [evidence/review.json](evidence/review.json).
  This is not independent human peer review.

## Interpretation and limits

The all-width injection argument is in PROOF.md. Truth tables establish the
stated finite controls, not arbitrary-width correctness by enumeration.
The driver deliberately rejects optimized Python (`-O`) because its retained
geometry uses assertions. No successful optimized replay is claimed.

Only this new research package is submitted. No generator, existing certificate,
selected construction or upstream/ file changes. Full `make verify`, selected
supplier cold replay, hosted CI and proof-assistant verification were not run or
claimed for this isolated note. The physical per-bit pricing and inherited stage
accounting remain explicit premises; the full multiplication theorem and the
nonlinear decoder optimum remain unresolved.
