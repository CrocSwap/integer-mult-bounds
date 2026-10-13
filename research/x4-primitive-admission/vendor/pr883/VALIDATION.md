# Validation — 2026-10-13

Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`. macOS arm64.

## Completed contribution checks

- `python3 -B -I -O research/x4-precondition-seed22/check.py`:
  **PASS**, CPython 3.14.7. Both exact certificates match; 737 columns in each
  orientation, 672 instruction mutants, exhaustive pair search, seven tests.
- A minimal copy containing only this package and the five pinned source files
  was placed under a directory containing spaces. The same `check.py`, invoked
  by absolute script resolution with `/usr/bin/python3 -B -I`, **PASS**, CPython
  3.9.6. No installed third-party libraries were used.
- A separately delegated AI review confirmed the algebra and invoices,
  ran all seven tests from `/private/tmp` with `-B -I -O`, and independently
  regenerated `INDEPENDENT.json` with exact structural equality. No blocking
  finding remained. This is not independent human review.
- Cross-certificate comparison: all 56 ordered register pairs agree between
  the two implementations; per-macro minima `[2,3,1]` and 737-column inventory
  agree with the integration receipt.
- `make selected-record-check`: **PASS**, existing selected
  `1661634653669567/1000000000000000000` unchanged.
- `git diff --cached --check`: **PASS**. Only this new research directory is
  staged. No `upstream/`, production code, source archive, selected certificate
  or predecessor notice changes.

## General repository suite — incomplete, not a pass

One `make verify` ran on a fresh `git archive` export of the exact base, to keep
unrelated generated files out of this contribution. It ran from 09:25:28 to
09:36:21 UTC (10 minutes 53 seconds), then was deliberately interrupted to
keep the bounded sprint focused on verification and handoff.

The six earlier groups completed: `verify-community`, `verify-producers`,
`verify-partial-gauge`, `verify-three-stage-cover`, `verify-paired-cube`, and
`verify-recycled-bit`. The selected-record check also passed at the start of
`verify-entrance-banks`. Interruption occurred while that target ran
`research/coordinated-frames-and-entrance-banks/verify.py`; it is **not** a
mathematical failure or a completed check. Exit status was 130.

The captured log SHA-256 is
`ef90b5bf2cd4b02e6758f169e112e73f1eda33908ca5547a91a4b18f4ae75062`.
No complete repository-suite, selected cold-replay, full physical precision,
global admission, hosted CI or Lean pass is claimed. The new package has no
third-party dependency and its own checks all completed.

## Final overlap screen

At 09:32 UTC, main was still the exact base. The initial full snapshot covered
669 open PRs through #876; the latest 100 were refreshed through #880.
Pinned coordination issues remained empty. New #877–#880 do not concern
the selected X4 two-register precondition factors. Exact nearby source heads
and distinctions are in `SOURCES.json` and `README.md`.
