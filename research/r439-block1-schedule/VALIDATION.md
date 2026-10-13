# Executed validation

Date: 2026-10-13. Base:
`f567884aeb8851b6e794af1184119a3bfbe1e631`.
Environment: Debian 13 x86_64, CPython **3.12.14**, GCC **14.2.0**.
All verification was performed by the same OpenAI Codex agent; no separate
human or delegated-agent review is claimed.

## Completed

- `python3 -I -B research/r439-block1-schedule/search.py` reproduces the entire
  candidate and every distance: minima 14 + 16, 2,048 states, 10,240
  state/destination checks, 8,464 feasible edges. This is exhaustive only
  in the two defined fixed-factor scheduling classes.
- `python3 -I -B research/r439-block1-schedule/verify.py` passes with 13 controls.
  The same report also passes under `-O`. The verifier uses F2 donor elimination
  and entrywise integer lifting; the nomination uses packed subset sums.
  Integer matrices, all 1,024 local Boolean inputs, all 661 arbitrary columns,
  E8 geometry, H1-H5 and the decomposed conclusion, actual record semantics,
  frame paths, copied-centre lifecycle, complete costs and prefix bounds pass.
- `python3 -I -B research/r439-block1-schedule/check_package.py` passes from a
  minimal relocated source tree without repository metadata, under `-I -B -O`
  and with spaces in its path. Altered immutable source bytes, missing source
  coverage, wrong physical wire binding, understated minimum and false receipt
  saving are rejected at their expected checks. Existing output is preserved.
- `BOOST_INCLUDE=/tmp/r439-boost/usr/include python3 -I -B
  research/r439-block1-schedule/native.py --write-receipt
  --output /tmp/r439-block1-native-first` completed fresh native checking on
  both words. The retained `NATIVE.json` records legality and all 5/9/11-stage
  fields, except timing and temporary stream path. Both words cover
  **883 / 1,327 / 1,549** formal columns and reject **6 / 18 / 24** omitted
  bridges per stage configuration: **96** bridge controls in total.
- A second native run from a minimal source closure at a path containing spaces,
  invoked outside the original checkout under `-I -B -O`, exactly matched the
  retained receipt. Python and C++ positive prefixes and scalar counts agree.
- `make selected-record-check` passes at the exact base. The selected
  certificate, all pre-existing tracked files and `upstream/` are unchanged.
- The four word/checker/generator files annotated in `SOURCES.json` were
  compared directly to their original PR589 Git objects; all bytes agree.

The native Boost dependency was absent initially. The Debian header package
`libboost1.83-dev_1.83.0-4.2_amd64.deb` was downloaded from
`https://deb.debian.org/debian/pool/main/b/boost1.83/` and extracted into `/tmp`,
without changing system packages. Download SHA256:
`1f11fc6fb2ffe9378a0f0ebc8f2fd9223fb958b4a40bb9381c67a8857d947ca3`.
This is an environment dependency, not a mathematical source certificate.

## Corrections during development

The initial exploratory split guessed 19 + 16 gates. Checking the actual
positive factor maps exposed entries greater than one in that first prefix.
The generator's true upper/lower boundary is 14 + 21; both factor maps are
binary with unit diagonal there. All published nomination and verification
use that fixed boundary. This was corrected before any candidate was accepted;
no failed search or optimum is inferred from the rejected exploratory split.

## Limits

No repository-wide regenerating `make verify`, cold reconstruction of the
supplier, new hosted-parent program/invoice, outer assembly, Lean proof or
remote CI run is claimed. Those constructions and generators were not changed.
The native checkers' signed lift and finite F2 endpoints do not discharge the
inherited signed decoder, all-size, realization, hosting, precision/tape and
analytic obligations. No unrestricted circuit minimum or improved kappa.

Metadata was refreshed through PR874, including concurrent PR873's distinct
frame-508 block. Main was still the exact base. GitHub denied fork creation
with HTTP 403 `Resource not accessible by integration`; the first handoff was
a local commit and patch. The contributor subsequently created the fork, and
the verified branch was pushed successfully. Upstream PR creation through both
the CLI and connected app still returned HTTP 403; no PR or hosted-CI success
is claimed. Publication-time overlap was refreshed through PR876 without a
matching block-1 contribution; main remained the exact base.
