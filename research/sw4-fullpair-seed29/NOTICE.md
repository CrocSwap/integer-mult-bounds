# Notice and attribution

Apache-2.0, same as the repository.

- The P6k4 word bytes (`inputs/P6K4-WORD.json.gz`) are the pinned selected-source
  input (`SW4-RECIPE-P6k4.json` `input_sha256 =
  0390ec65dc4d47df1887aabdc2ec5b6ddea3cfc8e65582873fdfeba81d100073`).
  The bytes were cross-checked against the independent vendoring in open
  PR #775; the sha pin binds them to the selected construction chain
  regardless of that PR's status.
- Construction lineage: BRoute's read-set exchange (search notes and recipe),
  Jeremy Kothe's PR #699, ColdWitness's drivers, and the upstream supplier
  authors cited in `research/complex-sw4-frame8/PROVENANCE.md` and
  `research/gauge44-frames-x/`. The pair rule, insertion rule, and
  frame-floor policy follow the credited SW4 construction; the floating-cost
  exponent is credited to PR #775 / the PR #699 complex endpoint.
- PR #775 (at1as, coupled partial read exchanges) is a concurrent contribution
  this work depends on for scope delimitation only: its README explicitly
  excludes all-full combinations, which is the class decided here. Its
  evaluator source was used after the fact as a cross-check harness and is
  not imported or vendored.
- Concurrent PR #874 (seed-61 audit of ideal-gain additivity at the X4 stage)
  is corroborating context: it distinguishes exact profile additivity from
  strictly convex ideal gains. This note's proxy-cost comparisons assume no
  linear ideal-gain arithmetic.
- Prepared with help from opencode. No independent human review is claimed.
