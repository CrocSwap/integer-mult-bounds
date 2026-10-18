# Mixed residual ranks close one P112 beta shape

For any two P112 six-dimensional label spaces, suppose some direction reaches
residual binary rank four after at most twelve line deletions. Then all directions
reaching rank six after separately chosen twelve-line deletions span at most
three dimensions. This finite bound is sharp for the separate-set contract.

Under the pinned TWOSIDE piece and quotient hypotheses, this excludes beta
`(b,t)=(5,4)` shape `3,4^2,6^6`. The observation is to retain the weight-four
nonbasis piece as a rank-four anchor; a generic separate-twelve-deletion
extension is false.

The submission refresh found concurrent [PR3164](https://github.com/CrocSwap/integer-mult-bounds/pull/3164),
head `857384079ab640a949fb7618b7909664d3e737e5`, which reports a different
root-simplex proof excluding both shapes left by PR3162. This package therefore
corroborates one of those exclusions, not a still-open residue. Its distinct
result is the sharp mixed-rank theorem for arbitrary flat pairs and separate
cuts, without a nine-piece or root-simplex hypothesis. PR3164's proof was read,
not cold-replayed in this session.

This is author-checked finite evidence, not independent human or proof-kernel
review. It does not prove the full C5 conjecture, `C(P112)>=64`, a new decoder,
a supplier admission or a new kappa. The selected frontier is unchanged.

## Evidence

[PROOF.md](PROOF.md) states the theorem, the all-direction coverage argument,
the exact oracles and the quotient-basis application. [RESULT.json](RESULT.json)
records all 159 first-flat orbit rows covering 123,511,995 representative pairs.
Every one of 987 anchor answers and all 832 positive pairs also receive Python
checks, including complete direction inventories and rational ranks. Native
oracles pass 109,239 comparisons against exhaustive retained-subset optima.

The cutoff grows from seventy to seventy-two, but an explicitly checked gap in
the complete E7/D7 support histogram leaves the same 248 directions. The scan
retains the predecessor's signed-Gram symmetry checks. Root-only coverage would
not justify the rank-six theorem.

Two exact negative controls delimit the result. PR3162's unanchored twelve-line
fixture has rank five. [CONTROL14.json](CONTROL14.json) gives a rank-five anchor
and five independent rank-six directions with separate fourteen-line cuts.
Neither fixture refutes a common-set or actual-piece conjecture.

## Reproduce

From the repository root, with Python 3.12+ and a C++17 compiler:

```sh
python3.12 -B scripts/research_package.py --package research/p112-mixed-rank-anchor --check-only
python3.12 -B scripts/research_package.py --package research/p112-mixed-rank-anchor
```

The replay and fourteen behavioral test groups take about thirty seconds on the
author's machine. Exact environment and additional checks are in
[CHECKS.json](CHECKS.json). No third-party Python dependencies, Lean or Docker
are needed. A direct replay can retain diagnostics externally:

```sh
python3.12 -B research/p112-mixed-rank-anchor/verify.py --work /YOUR/NEW/EXTERNAL/DIRECTORY
```

Without `--work`, scratch is temporary and removed on exit. Set `TMPDIR` to a
session-owned external directory if required by your workspace policy. A direct
Git-free export needs this package and the two `VERIFY.json` input paths.

[SOURCES.json](SOURCES.json) pins main, the original card and both live inputs.
Its `retained_files` inventory authenticates the vendored PR3162 files by SHA256
and records their exact source commit, path and Git blob. Replay does not require
a pending PR's Git history. Origin-byte equality was separately checked before
publication; reviewers can fetch PR3162 and compare those recorded blobs. No
predecessor file is edited. All new files are confined to this package.

## Open next questions

- Can the 832 positive pairs be classified geometrically, replacing part of the
  finite census? Start with the sharp span-three fixture and the source-bound
  signed-Gram group. No such classification is supplied.

The previous remaining `2,5^3,6^5` shape is now reported excluded by concurrent
PR3164. Do not assign another search for it on the basis of PR3162's historical
residue. `CONTROL14.json` still usefully rejects a different attempted relaxation;
it does not contradict PR3164 or any common-set theorem.

[Task and overlap record](TASK.json). The canonical investigation is
[Discussion3156](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156),
particularly [PR3162's handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-18998421).

## Credit

Nick Petalas. Apache-2.0. The reduction, TWOSIDE hypotheses and original finite
programs are DreamingOfClouds's PR3154, exact head
`708f0ad8928c383de8294aea3c126e9461d2066d`, with the retained E8/decoder lineage.
This successor builds on Nick Petalas's PR3161 and PR3162, the latter at
`ebd7fd275288e4a9f658e77fa77a0119a8322e74`. PR3163 is a distinct rank-seven
common-deletion calibration slice, not this mixed-rank exclusion. The flat/orbit
enumerator, dual rank-six oracle and geometry are copied unchanged from PR3162;
the anchor oracle, mixed-rank scan, independent checks and new application are
added here. See `vendor/PREDECESSOR-NOTICE.md` and `vendor/LICENSE`.

Development and internal checking used substantial automated assistance.
