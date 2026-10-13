# Independent verification of the PR623 owner repair

Conditional kappa **0.001635527380375392**, exactly
`51110230636731/31250000000000000`. The gain over credited PR623 is
`36715454937/1000000000000000000`. The 64 JP8 / 8 CK dispatch and all
R492 supplier words are unchanged.

The literal idle profile changes from
`{1:122,2:1,3:1,12:1,21:1,48:2215}` to `{1:123,37:1,48:2215}`.
The paid profile is
`{1:181659,2:30016,3:31104,4:11520,5:5040,6:576,8:576,37:1,48:2215}`,
with rank mass520704 and35,424 complete helper roles.

| Fresh platform | Stages | Receipt artifacts | Replay seconds |
| --- | ---: | ---: | ---: |
| macOS arm64, Python3.14.8 |64|51|285.905080334|
| Linux aarch64, Python3.14 |64|51|338.861518659|

Both final portable-package replays rebuilt the baseline and native
suppliers. No baseline or local receipt was reused. These are execution
times, not controlled performance benchmarks. All receipt artifact hashes,
all128 raw stage-log hashes, package/source pins and exact endpoints were
checked independently by collect_verify.py under `-I -O`.

The supplemental checker reconstructs each actual helper width and both
native program orientations, verifies literal physical families, call
chronology, owner windows, disjoint compact footprints and rank mass,
then checks the moment using a separate exact rational log/exp engine.
Its output is byte-identical across platforms. The declarations checker
reconstructs the complete SPEC from WITNESS and EXPECTED. Two positive
controls and eight malformed-input rejections pass with assertions
disabled; see SUPPLEMENT-CONTROLS.json and audit_supplements.py.

## Provenance and limits

SOURCE-REVIEW.json records exact source pins and the six changed files
in the selected candidate: MANIFEST plus five data files. All verifier,
constructor, recipe, controller, invoice and assembly code is byte-identical
to PR623 and PR622. Packaging adds bundled sources, documentation and the
separate checks; name/source-directory declarations are updated consistently.

selected-continuation/ retains search/admission provenance, including
explicit baseline/native reuse in that earlier53-stage branch replay.
Its receipt is contextual evidence; macos/ and linux/ carry the final
fresh replay's complete receipt artifacts and raw stage logs.

The selected search used coordinated literal repairs, a bounded
LP-neighborhood MIP, then fixed-pattern flow repair with cross-time Hall
cuts. Two initial stronger aggregate nominations failed literal expansion.
Only the repaired literal map and unchanged strict admission establish
the result. Floating solver objectives/statuses do not certify a bound or
an optimum. Historical data/cand.json and data/search/ in the main package
remain credited PR623 provenance, not this continuation's search outputs.

No global or fixed-dispatch packing optimality, new supplier construction,
priority, unconditional multiplication theorem, complete Lean proof or
practical speedup is claimed. The inherited compiler, common-label,
mutable-source, whole-call hosting, precision/tape/exact recovery,
analytic-transfer and bit H1-H5 assumptions remain.

Credits: jeremykothe2 and Claude Opus for PR623/PR622; GamingPuzzled for
PR620's owner-map lead; DreamingOfClouds and the earlier supplier authors
listed in the preserved NOTICE.md. This continuation, packaging and
independent checks were prepared by OpenAI Codex for chafreaky.

## Replay

From the repository root:

```sh
bash research/complex-k492-owner-repair/verify.sh /tmp/k492-replay
python3 -I -O -B research/complex-k492-owner-repair-validation/audit_supplements.py --work /tmp/k492-replay
```

The new workflow runs the same full wrapper on Python3.11 and3.14.
Platform environment/process metadata and the Linux terminal record are
retained beside each replay. SHA256SUMS.json covers every validation file
except itself; the separate core MANIFEST covers every core/vendor file
except its own top-level manifest.
