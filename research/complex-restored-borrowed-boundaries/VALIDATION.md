# Validation and handoff

Executed 2026-10-13 UTC on macOS arm64, CPython **3.14.6** and **3.9.6**,
Apple clang **17.0.0** (`clang-1700.6.4.2`), C++17. Research and refreshed
submission base: `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`.

## Completed checks

- Optimized primary replay and ordinary primary replay pass. The optimized
  replay completes in 9.60 seconds locally (one observation, not a benchmark
  improvement claim). A second generated receipt is byte-identical to
  EXPECTED.json; no compressed artifacts are generated.
- Every canonical state and minimum distance matches the separate C++ search:
  3,938 + 69,672 + 2,299,917 = **2,373,527 states**. The six-register
  translated radius-four intersection is empty.
- Eleven test groups pass on both Python versions. Each includes a complete
  offline relocated replay, under isolated optimized Python, with no changed
  source or package bytes. A changed six-register lower-bound receipt is rejected
  after a full replay. Source corruption is rejected for each of seven inputs.
- Dense independent matrix oracles reproduce the GL3 radius-three, GL4
  radius-two and GL6 radius-two balls. All 151^2 GL3 radius-two products check
  the meeting equation. Tests cover missing negations, shortened BFS depth,
  false distances, inverse generators, dyadic quotient maps, invalid F2 halving,
  false exact conclusions from modular equality, and donor-coordinate bit width.
- Exact Fraction witnesses and their literal inverses pass on every input
  column. All **37 primitive omissions** fail. Disposable workspace words
  preserve data while destroying the donor column: the restored-donor check
  rejects exactly the missing obligation. Read-only specialization examples
  compare every retained prefix, with a control against silently dropping
  arbitrary dirty source terms.
- The write-count fixtures check all donor counts 0..19 against the proved
  bound. This finite arithmetic is an illustration, not the proof of the
  universal lemma. The length-nine/two-donor control records the excluded
  scope explicitly.
- The C++ six-register enumeration also passes UndefinedBehaviorSanitizer
  (`-fsanitize=undefined -fno-sanitize-recover=all`) and produces exactly the
  same 2,299,917-state byte stream as Python. No 64-bit truncation is used for
  the 72-bit working matrices.
- Fresh source census matches all **168** PR969 boundary records, all event
  intervals, frames, swap positions, mappings and cycles in four orientations.
  Four omitted swap gates, wrong signs and inserted frame/event barriers fail
  recognition controls.
- All seven replay and four context SHA256/Git-blob pins match their exact base
  objects. The adapted PR1145 originals match its pinned commit. Live GitHub
  confirms the PR969 and PR1145 heads recorded in SOURCES.json.
- `python3 -B scripts/verify_selected_result.py` passes, and all five
  `test_selected_result.py` tests pass. The selected record remains unchanged.
- Final scoped diff, Markdown links and `git diff --check` pass. Only this
  package and its focused workflow are submitted; upstream/ is unchanged.

## Coverage limits and next review

The principal review obligation is the short-word reduction in PROOF.md:
rank preservation excludes destructive gates; a restored written donor costs
at least two writes; read-only donors can be specialized away for a lower
bound. Its finite consequence is fully enumerated, not extrapolated from a
sample. This is computer-assisted evidence, not a Lean formalization.

Nine versus ten operations for the disjoint permutation remains unresolved.
Clean/disposable helpers, changed input promises, joint optimization across
surrounding events and joint real/imaginary circuits are excluded. No complete
supplier/native/phase/physical, precision/tape, hosting, all-size or outer
analytic verification was run; no new kappa or complete row saving is claimed.
No repository-wide `make verify` or selected cold replay was needed for this
isolated historical scalar boundary result.

Overlap refreshed through PR1213 and the current discussion board (including
1210's masked-root-star claim). Those objects are distinct. The nearest work is
PR1145's no-donor result, PR1095's monomial-prefix/disposable-workspace bound,
and PR969's actual swap construction. Full attribution is in NOTICE.md.

The added focused workflow is configured for Linux Python 3.11 and 3.14.
Hosted CI is separate and was not claimed passed at submission. Upstream has
neither a `codex` nor `codex-automation` label, so neither label is invented.
