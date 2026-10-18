# Executed validation

All results below were executed locally on 2026-10-14 UTC from base
`410026dc5513b87db92ae98571d1d5984c69a983`. Environment: Linux x86_64,
Python 3.12.14, GCC 14.2.0, C++17 `-O2`, Boost 1.83 headers.
Boost version-header SHA-256:
`a547ee7eddf1b96695027922345b471feba8bcba79a8572399d282247c02e4ab`.

## Completed checks

1. **PASS:** bounded search, exactly 1,000 trajectories, seed 2026101406.
   The node-6 witness has 43 ADDs versus 51. Its complete four-background
   precision bills independently agree with the verifier.
2. **PASS:** normal Python `verify.py --replay-search`, all 8 subsets,
   4,096 Boolean inputs and inverses per replacement, 720 persistent dirty
   columns per subset, every frame path, exact positive bounds, original
   H1–H5 and PR425 predicates, and the unchanged exporter.
3. **PASS:** Python 5/9/11-stage replays for every subset
   (960/1,440/1,680 formal columns respectively), 179 rejection controls.
4. **PASS:** all 8 subsets under the unchanged C++ legality and 5/9/11-stage
   column checkers. All 384 omitted-bridge controls reject. Native receipts
   agree exactly with Python's ADD counts, positive bills and paid histograms.
5. **PASS:** minimal source export, no Git metadata or cached outputs, in a
   path containing spaces; `-I -O -B` complete search and native replay.
   The six package controls reject a changed supplier input, missing source
   pin, illegal recipe frame, incorrect search precision receipt, incorrect
   complete-bill certificate and existing output directory. The existing
   output's marker is preserved.
6. **PASS:** `python3 -B scripts/verify_selected_result.py` and
   `git diff --check`. No selected artifact or upstream input is edited.

The normal development run retained evidence at `/tmp/r480-qnode6-first`.
The native run retained full logs at `/tmp/r480-qnode6-native-fixed`; the clean
export test creates and removes its own temporary directory.
These paths are convenience locations, not reproduction dependencies.
The complete mathematical receipts are committed as `CERTIFICATE.json` and
`NATIVE.json`; the unchanged inputs are bound by `SOURCES.json`.

The full clean-export check used:

```sh
BOOST_INCLUDE=/workspace/.setup/boost/usr/include python3 -I -B research/r480-qnode6-composition/test_package.py --native
```

Expected marker:
`PASS_R480_QNODE6_PACKAGE clean_export=True optimized=True native=True rejection_controls=6`.

During development the native wrapper initially compared the C++ histogram's
ordered list with Python's dictionary. It correctly stopped on that mismatch.
The wrapper now converts the expected dictionary to an ordered list and checks
every entry. All eight unchanged native checkers then passed; no mathematical
admission condition was removed.

## Scope and unrun work

No repository-wide historical suite, selected-frontier cold replay,
hosted-parent invoice, remote CI or Lean theorem build was run. The complete
finite local and 5/9/11-stage checks above do not discharge the inherited
all-size/compiler, mutable-source/common-label, physical hosting, uniform
precision/tape or analytic hypotheses. This historical bit circuit is not
installed as a selected supplier.

Public overlap queries were refreshed after verification, and Git transport
confirmed the exact PR1003/1089 heads remained unchanged. Upstream main
advanced to `e6f9716621f4e01fc190617934cdfaf072bd976f` with two historical-review
commits; **none of the consumed pinned files changed**. The exact research
base remains recorded above. `OVERLAP.json` records the available public
metadata and incomplete-coverage limits. API publication and coordination
posting were not attempted, following the donor's stated restriction.

Prepared for @CubeJerry with substantial OpenAI Codex assistance; Apache-2.0.
