# Local verification receipt

2026-10-13, macOS arm64. No hosted-CI success or independent human mathematical
review is asserted.

- CPython **3.12.13**, full registered replay:
  `python3.12 scripts/research_package.py --package research/sparse-redundant-decoder`.
  PASS, six test groups, 14.334 seconds locally. This includes both complete
  mathematical engines, exact receipt regeneration, overwrite refusal,
  corrupted active minimum rejected by both, incomplete/missing receipts,
  changed-source rejection and optimized read-only file relocation.
- CPython **3.14.7**, optimized six-group package replay: PASS (17.501 seconds).
  After adding PR845 provenance, both full direct engines were repeated under
  `-I -O -B`: PASS; the final source checks and mathematical receipt agree.
- The primary engine checks 32,385 planes, 765 single functions, five sharp
  witnesses and twelve additional exact integer-shift examples: 213,248
  identity entries in total. The second checker separately verifies all finite
  lemmas and all 62,720 sharp-witness entries. Each is finite evidence for the
  universal written proof, not a finite sample promoted to a theorem.
- Six semantic controls reject missing compensation, wrong ninth normal,
  missing affine pairing constant, unpunctured geometry, omitted compatibility
  constraints and incomplete plane coverage. All-active versus eight-active
  sharp witnesses prevent conflating those two bounds.
- `python3 -m unittest discover -s tests -p 'test_research*.py'`: 20 tests,
  one pre-existing skip, PASS.
- `python3 -m unittest discover -s tests -p 'test_selected_result*.py'`: five
  tests, PASS. `python3 scripts/verify_selected_result.py`: PASS selected
  record, exact kappa, original inventory and proof supplement.
- Registered metadata/source pins and staged whitespace: PASS.
- Full overlap refresh: 809 open PRs, 62 discussion/comment/reply records,
  327 local notes, complete remote pagination and no warnings. It identified
  incorporated PR845, and the final claims explicitly credit its existing64
  floor. The selected source files and upstream main remained at the exact
  recorded base when refreshed.

Not run: `make frontier1094-verify`, unrelated historical supplier suites,
native/controller admission, Lean, and a full replay of PR845's broader
all-real-normal theorem. This new package derives its fixed-frame result
separately and leaves the selected construction and all existing files intact.
