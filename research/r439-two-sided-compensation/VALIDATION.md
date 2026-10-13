# Validation record

Executed on Linux, 2026-10-13, with CPython 3.14.4 and CPython 3.12.3,
GCC C++ 15.2.0, C++17, and Boost 1.83 headers. Boost was extracted outside
the repository from Ubuntu `libboost1.83-dev_1.83.0-5ubuntu5_amd64.deb`, SHA256
`c17abc5a40a074c3d959655191ebec1561fa25f14f4948f6788be49417d4b234`.

## Completed checks

The ordinary CPython 3.14.4 run of `verify.py` passed against the entire
committed EXPECTED.json receipt. An isolated `-I -O -B` CPython 3.12.3 run
also passed from an unrelated working directory. That second run used only
this package and the 14 source files in SOURCES.json, without Git metadata,
under a path containing spaces. All source files and directories were made
read-only before execution; output went to a separate temporary directory.
The canonical full receipts are identical, SHA256
`5ea81356e925a7326390f17c378bdf3e2f04b58aad0d39a7f1857595a24f3c93`.

Each full verifier run includes:

- Regeneration of all 192,282 pair scores, all tie keys, the guarded disjoint
  greedy pass, the complete recipe and the canonical word payload.
- Independent set-valued census and reconstruction. Literal forward/reverse
  replay checks 4,760,850 positive instructions across all admitted partial
  words; no guard rejection occurs.
- All 48,729 four-term matrix coefficients, including the 7,031 nonzero
  mixed-term entries. The same helper pairs alone would cost 14,156 D ADDs;
  their standalone saving is not added to the parent saving.
- All 661 distinct input columns for original, parent and candidate D words,
  each in both directions. Full owning E8/frame/endpoint checks also pass.
  The original H2 and literal K extraction remain explicitly false for the
  two changed words; every other interface predicate passes.
- Fresh compilation of unchanged C++ legality and 5/9/11-stage checkers.
  All three words pass on 883/1,327/1,549 formal columns. All 144 omitted
  bridges are rejected. Every register's MOVE sequence and all COPY/ERASE
  records agree, retaining rank mass 5,129.
- Nineteen local rejection controls and the paid endpoint-neutral helper
  pair. Native and Python counts and both positive bounds agree.
- Binding the nine-stage prefix expression and bridge exponent to the
  pinned source, reproducing the baseline invoice estimate, and checking
  the strict 192-bit ceiling for all three words.

All eight package tests passed on both interpreters, including the optimized
read-only run. They reject source drift, missing sources, duplicate/nonfinite
JSON, boolean/integer receipt confusion and overwrites; recompressed candidate
payloads compare equal.

`make selected-record-check` passed after moving an exploratory Python bytecode
cache outside the selected package inventory. Its initial failure identified
only that untracked `.pyc` file; there were no missing or changed source files.
The scoped staged whitespace check passed. No source or frontier record was
changed to make either check pass.

## Submission context and limits

The final upstream fetch remained at
`91a2094f2e022930069e8cfdc810a3ea1b81cd09`. The instructions gist remained at
`4180bf0d4045ffdcd12d75bb1fec91c234420162`. A fresh 714-open-PR snapshot through
PR924 retained parent PR915 at `e9daefe320a0043000bd9746664ed02c3287d056` and
predecessor PR733 at `dfe84e09298abc5c5e0074afda59a821e10abfb4`.

No new R439 two-sided D construction appeared in that refresh. PR917 is a
complex CK two-sided construction; PR923 changes the selected R439 phase-B
frame520 block and its cleanup. The latter credits PR904's overlap, but does
not change D. Their savings are not composed here. The frozen 18-PR review
batch on the base is not edited or treated as approval of this contribution.

The executable claim is a finite circuit and explicit prefix bound. Remaining
integration work is acceptance of the semantic D interface, complete changed
hosted emission and audit, updated finite/precision invoices, and outer
assembly. The common-label realization and analytic assumptions remain
inherited. No full `make verify`, selected cold replay, formal multiplication
theorem, new exponent, measured runtime improvement or hosted CI success is
claimed by these local checks.
