# Three-stage cover reproduction

The extension inherits PR #115 at
`cf60442983c153a3a0f5272ea4713f99eba13c86` and gives the conditional saving
`3146011/10000000000 = 3.146011e-4`.

From the repository root, using Python 3.11+ and a C++17 compiler:

```sh
make three-stage-cover-verify
```

CI runs this target in its own `three-stage-cover` matrix group. Its
incremental scope is:

- Rebuild the new pinned PR #117 local DAG, compatible matching, full backward
  subspace intersections, actual scalar word and partial source gauges.
  Independently check scalar supports, signed coefficients, divisor 21,
  carrier containment, center closure, untouched source roles, actual frame
  transitions and reverse target chains. Intermediate frames can be
  degenerate; their validity follows from the new general Clifford proof.
- Reconstruct the unchanged PR #97 local physical ranks from its pinned
  paths, then compose the new three-stage bit inventory. The unchanged
  upstream complete-basis and rational-frame suites are inherited checks.
- Certify the bit moment with the full rare-class local-ring fallback,
  stopped ordinary saving, complex moment, full finite group order and
  router charge, exact semantic guard, row reserve, 47 strict inequalities
  and seven assembly margins.

For the moments and arithmetic alone:

```sh
make three-stage-cover-certificate
```

The group is specified by a written construction; verification does not
materialize its vertices. The complex group size and finite routing allowance
remain in the certificate. The bit group depends on atom width; its uniform
batching, weighted children and internally borrowed rows are proved in
`notes/three-stage-cover-bit.tex` and `notes/three-stage-cover-rows.tex`.
Finite arithmetic does not by itself verify those all-size interfaces.

To retain regenerated local files outside the repository:

```sh
python3 scripts/three_stage_cover_producer.py --work-dir /tmp/three-stage-cover-work --output /tmp/three-stage-cover-verification.json
```

The [main proof](../notes/three-stage-cover-note.tex) includes
[general Clifford frames](../notes/general-clifford-frames.tex), exact data
chronology and phases, complete dirty cleanup, weighted factorization,
fallback, row restoration and final composition. Sources are included
without a PDF. `SOURCES.json`, `NOTICE` and `references/three-stage-cover/`
retain the adopted author's source pins and original legal notices.

The previous submitted production code and certificates remain unchanged.
Unselected round7/round8 research and large generated graphs are excluded.
Only the new selected local construction and changed cover/assembly are
verified this round.

## Shared source digests

Changes to `Makefile`, `README.md` and `NOTICE` also affect the inherited
joint-dual source manifest. After reviewing their final content, explicitly
run `scripts/experiments/pin_joint_dual_sources.py`, regenerate the joint
arithmetic certificate, and update its validation receipt's certificate
digest. The unchanged mathematical fields and prior replay payload must
match the preceding submission. A full producer replay is required when
those producer or verifier inputs change; the full command is
`make verify-joint`.

The final reproducibility check runs against staged artifacts and requires
`git diff --exit-code` to remain clean. CI verifies committed hashes and
does not silently refresh source pins.
