# Executed validation

Local host: macOS arm64, Apple clang 21.0.0 (C++17), CPython 3.12.13 and
3.14.7. New material only; predecessor and upstream inputs unchanged.

- CPython 3.12.13, assertions disabled: complete native exclusion, exact upper
  word, signed distance-nine positive control, complete dense GL(2,3)/GL(3,3)
  oracle, all input controls and fresh 168-boundary recount passed. Rebuilt
  EXPECTED.json after all checks, including the retained predecessor hashes.
- Five package test groups pass on CPython 3.12.13 in 40.675 seconds, including
  full read-only relocated replay, three source-corruption rejections and a
  receipt corruption rejected after another full native replay.
- CPython 3.14.7 complete optimized replay agrees field for field with the
  committed receipt. Different Python versions do not make the underlying
  native implementations independent; the separate representations do.
- Registered Python 3.12 quick replay and source/metadata pins pass. This quick
  command explicitly omits the native exclusion; it is not the full result.
- Selected-record integrity passes. Five selected-record tests pass. Twenty
  repository research tests pass with one expected skip. Whitespace checks pass.

Both native engines enumerate all 2,299,917 six-register matrices/minimum
radius-four distances; the full 20,699,253-byte canonical streams agree.
Each tests all 151,794,522 middle transitions with zero hits, plus the direct
intersection. The four-register signed-cycle control has 1,000 middle hits
and minimum nine; the direct intersection has zero hits. The target canonical
ball SHA256 is `a943ba6bc12d9da2d57ea31edb27455804adaea1280c1fd226af4c4915f210d0`.
The hash summarizes the full byte comparison and is not a substitute for it.

Source-bound contextual checks: selected base/main
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f` remained current at the final fetch;
PR1216 and PR1145 heads were unchanged. Final overlap snapshot covered 794
open PRs through #1300 and the available Discussion claims; no overlapping
nine-versus-ten result was found. The scoped coordinator written review found
no blocker, but did not independently execute the full exclusion.

No Linux/hosted CI success, selected supplier cold replay, physical compiler,
rounding/precision theorem, Lean result or independent human review is claimed.
The dedicated native workflow is newly supplied; its remote status is separate.
