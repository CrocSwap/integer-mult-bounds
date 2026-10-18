# Validation and handoff

Environment: Linux x86_64 / WSL2, CPython **3.12.3**.
The assignment seed is **38**. The exact contribution base is
`ba82555c64e1879e4b7decce28186f208fcb8262`.
The work window started at 18:38 UTC on 2026-10-13 and ends at 19:28 UTC.
Implementation and source correction completed before 19:09 UTC.
The remaining work is verification, source/overlap inspection and handoff.

## Completed result

The actual PR1042 R480 seven-slot scalar programs save **408 real-component
primitives per orientation** under the retained sign compiler and PR696 lowering.
Forward: **149002 -> 148594**. Backward: **149018 -> 148610**.
The paid recursive profile remains unchanged. No new kappa is claimed.

The two implementations reproduce the complete receipt and primitive hashes.
All **4,332 scalar runs** receive a fresh arbitrary-input boundary check.
Both scalar projections cover **713 input columns**, including all nine dirty
private registers. Per-register run magnitudes and denominator depths agree.
The whole scalar projection has unchanged maxima of 131088 / 1154896 and
denominator depths of 4 / 17. These are not full physical precision measurements.

## Executed checks

```sh
python3 -I -B research/selected-k8-sign-seed38/check.py
python3 -I -O -B research/selected-k8-sign-seed38/test_package.py
make selected-record-check
python3 -B -m unittest discover -s tests -p 'test_selected*.py'
git diff --cached --check
```

The complete command prints:

```text
PASS_SELECTED_K8_SIGN_PACKAGE runs=2166+2166 columns=713 saved=408/408 controls=120 no_new_kappa
```

The package tests include optimized minimal offline relocation, 10,000 integer
arithmetic steps compared against `Fraction`, and source/receipt corruptions.
The source identity checks reject both the archived cold ancestor and the
pre-slot R480 word. Canonical word identity accepts equivalent JSON/gzip data.
The published input archive itself remains an immutable byte-pinned source.
The relocated complete command runs without Git metadata or external packages.
The selected-record check and **25 selected-record regressions** pass at the base.

The original full repository suite, supplier cold replay, native Clifford/frame
execution, global hosting/invoice/assembly, hosted CI and Lean were not run.
The package changes none of their inputs or generators.
The retained native receipt describes the original source. It is not a fresh replay.

## Source correction

The first screen used `gauge44-slots-t16/evidence/local/` and measured 652/652.
Those files describe a retained R492 ancestor. That screen is not the contribution.
No commit or PR published its mislabeled receipt.

The final overlap inspection found **woklerx's PR1132**, head
`36a82dd551cd18b8b32c2013ba928f59ad52678c`.
Its provenance reconciliation identified the wrong-input trap.
The actual reproduction script confirmed that PR1042 uses `slots/local/`
from `research/community-frontier1042-audit/selected-replay.tar.gz`.
The archive receipt binds those programs to the selected assembly.
The contribution retains the original scope and replaces its input and receipt.
It does not combine the ancestor and selected-word counts.

The input archive SHA256 is
`22c3f4dce4b897a1d423d1388801933e288b6a6b1906cb15e1b16a5eb68db754`.
The selected word's canonical content SHA256 is
`c2b294300760e1fd6eeab8c22c4d13e4633dca40e52cac8da0d68163a76e3ca8`.
[SOURCE-PINS.json](SOURCE-PINS.json) records four repository inputs, five named
archive members, and the immutable selected context.

## Upstream and overlap refresh

The full-queue refresh inspected **756 open PRs through #1141**.
No pinned coordination issue existed, so the claim remains local.
Relevant concurrent work includes PR1115's U8 shear rewrites, PR1118's historical
CK coefficient synthesis, PR1126's leaver-core optimum, PR1138's relabeling atlas
and PR1140's factory-register bound. These use distinct objects or objectives.
No pending code or saving is composed with this contribution.

Upstream advanced to `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, selecting PR1094.
All **four corrected repository inputs** match their pins in that fetched tree.
This package remains pinned to PR1042, the reviewed selection at its exact base.
It does not claim transport to a later selected word.
Ross Richardson's PR919 supplies the method and retained compiler.
Sagar Thakrar's PR696 supplies the comparison lowering.
The README preserves the construction lineage and concurrent provenance credit.

The immediate pre-submit refresh reached **PR1152** and found no pinned issue.
PR1143 (`fee8dc25e104b2c45ddba1ded4dca846794ba32f`) excludes a distinct
commuting-ADD class on the same frozen word. This result changes primitive signs.
PR1142 (`0c2873e6ac844b369a5962f06ef0a74ac86cf4a4`) audits the full capsule.
This package authenticates only its consumed members and claims no capsule-wide audit.
The four package tests and whitespace check pass after the source correction.

New material is Apache-2.0. @Scratch-net contributes with substantial OpenAI
Codex assistance in research, implementation, proof, verification and writing.
The separate implementations are AI-assisted, not independent human peer review.

## Final handoff

Submitted as [PR1153](https://github.com/CrocSwap/integer-mult-bounds/pull/1153).
Exact implementation commit: `643cf099f16b055731e393fea9582b45eff51035`.
The handoff commit updates only this document and the local claim.
Executable code, source pins and the exact receipt remain unchanged.
No PR was merged or closed, and the selected frontier remains untouched.
