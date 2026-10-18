# Validation receipt

2026-10-13, macOS arm64, Python 3.14.8. Base and refreshed `origin/main` both
equal `66849e1475c930fd7732b1a0067ffee7e1e95f60`.

- `python3 -I -B research/complex-signed-digit/verify.py`: PASS.
- `python3 -I -O -B research/complex-signed-digit/verify.py`: PASS, including
  all nine controls with assertions disabled.
- `make selected-record-check`: PASS for the selected record, exact kappa,
  original source inventory and proof supplements.
- `git diff --cached --check`: PASS.
- In-memory CLI corruption checks replaced the pinned program bytes and
  reduced the expected forward cost by two. They failed with `source drift`
  and `committed receipt mismatch`, respectively. No source file was changed.

A separately delegated Codex worker independently recounted both orientations
and obtained the same costs and exact prefix fractions. Its review identified
the need to reject temporary writes outside scratch; the checker now enforces
that restriction and tests an endpoint-neutral target excursion. This was
AI-assisted review, with no independent human-review claim.

The final overlap review at 04:48:49 UTC covered 540 open PRs through #721.
No pinned coordination issue existed. Relevant refreshed heads were:

- #696, `5a3f983715027c4fd83f50bc9001d4b18463bed1`: copy and unit lowering,
  unchanged since initial inspection. The present saving isolates numerator
  recoding and does not count its improvement.
- #681, `fdc2e4f3c6825530b02143b30deab5de10209479`: expanded to fourteen raw
  factory windows since initial inspection. Its macro changes remain distinct
  from recoding coefficients of the unchanged selected JP8 word.
- #687, `82bbb9c3ac34540f196410d137ebc59d9c2c43a9`: finite K-triangle
  read-relocation neighborhood, unchanged.
- #717, `07f4671a838088b59c6356ab2b5ffe30038d4b1a`: construction-format
  limits and invoice sensitivity. Its reported search classes do not recode
  the private coefficient stream.

These pending contributions are credited context, not source dependencies.
The metadata refresh found no duplicate signed-digit JP8 contribution.

The post-submission head check found concurrent #722 at
`a0766ab0fab379e1997fadc3ca157578d57986c1`. Its body and file inventory were
inspected. It shares preparation across forward cleanup blocks and keeps
binary Horner; this result preserves each macro boundary, recodes numerators,
and also improves backward. README.md and the PR description credit this
distinct contribution. No additive saving or implementation dependency is
claimed. The source and mathematical checks above are unaffected.

The full regenerating `make verify`, selected cold replay, global hosting and
assembly, Linux CI and Lean were not run. This package adds a local circuit
and an exact finite check; it does not modify the selected construction.
The inherited all-size, physical, precision/tape and analytic obligations
listed in README.md remain unresolved by this work.
