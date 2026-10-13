# Validation record

Environment: Windows 11, CPython 3.12.14 (`C:\Users\warha\.local\bin\python3.12.exe`),
standard library only. Base commit `f567884aeb8851b6e794af1184119a3bfbe1e631`
(origin/main), branch `research/agent-06-complex-seed20`. No package was
installed; no repository outside this one was cloned.

## Commands run

1. `python3 -B research/complex-sw4-frame8/construction/sw4/build_sw4.py
   research/complex-insert-slides-seed20/inputs/PROMOTED-P6K4-WORD.json.gz
   <tmp>/sw4-control research/complex-insert-slides-seed20/inputs/SW4-RECIPE-P6k4.json`
   — the pinned recipe on the vendored input: PASS, output content sha256
   `d232183f233899961bf55cac67a18545ed33548d9a7ca7078990d1a83d557c59`
   equals the recipe's `output_sha256`, all four inherited controls
   (C0/N1/N2/N3) hold, pinned profile `{1:2548, 2:342, 3:438, 4:186, 5:56, 8:8}`,
   W = 3778. This is the positive control for the vendored input word and the
   vendored recipe copy.

2. `python3 -B research/complex-insert-slides-seed20/verify.py` — the package
   verification (behavior tests + complete census re-enumeration + controls +
   pin comparison). Final line:

   ```
   PASS_INSERT_SLIDES_SEED20 singles=56 pairs=1372 swaps=4 legal=1060 improving=0 best_root=0.001663428754540
   ```

3. `python3 -B research/complex-insert-slides-seed20/test_search.py` —
   six behavior/failure tests, all pass (also run inside verify.py).

## Checks not run (out of scope for this standalone research note)

- `make verify` and `make frontier799-verify` (the repository-wide suites and
  the selected construction's cold replay): no generator, certificate,
  selected-record or supplier file is touched by this change.
- Linux CI, any Lean build, and the PR589 bit-circuit replay.
- Remote GitHub Actions of this PR.

The independent check of the pricing functional is internal to this package
(float root + exact-engine bracketing + the frame8 calibration against the
selected record's endpoint); a second independent implementation of the
census itself was not built.

## Determinism

The enumeration is deterministic and complete (no random choices, no
optimizer, no network). Sprint assignment seed 20 (OS draw) selected the
track only. `EXPECTED.json` pins the census counts, both roots, the
exact-engine cross-check strings and the canonical rows digest
(`sha256` of the sorted-JSON rows), so any semantic change to the census
fails verification.
