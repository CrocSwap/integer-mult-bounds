# Publication check

The explicit assignment was to repair PR1048's pricing and independently check
its post-first-move coverage. The user subsequently authorized publication.
The research scope remains the frozen at-most-two-transport domain in PROOF.md;
this is an audit and scoped negative result, not a new construction.

Submission base: `bce54fb3f895cbe5cd4c0eb477c3afeed100190f` (current main fetched
2026-10-13). The original local commits `ce0b65fd` and `fb8a792a` remain preserved
on their separate branches. Their scientific files were applied unchanged to
the submission base; publication edits add this record, the PR933 distinction
and concrete next questions. The selected construction is unchanged.

## Validation on the submission base

CPython 3.13.2, macOS, standard library only. All 36 mandatory input byte pins
pass. The 24 retained PR1048/PR1182 files are additions absent from main; the
12 already-upstream inputs are byte-identical to the research base. All four
research engine/driver hashes in REVIEW.md remain unchanged.

```sh
python3 -I -O -B research/pr1048-complete-feasibility/independent_pairs.py --full --time-budget 1200 --output /tmp/pr1048-publication-independent-pairs.json
python3 -I -B scripts/verify_selected_result.py
```

The fresh independent run completed in 119.384 seconds. Its complete status,
59,998 pairs, all aggregate counts, all 93 delta records and rational intervals,
endpoint signs, driver hashes, and synthetic control equal the saved complete
receipt. Transcript:
`b39d6d23210ab7eee24c04e165b078e39ea00053e4be4b523f7c793e24b79679`.
Fresh receipt SHA256:
`664dee24036846d2729bd8bc1f0c14e05bd57ac73240e21285f763b15a63743f`.
The selected-record/source-inventory/proof-supplement guard passes.

The guard rejects optimized Python, so it was run with assertions enabled.
An initial inventory check detected only two generated tune/wlib `.pyc` files,
with zero missing or changed source files; those generated files were removed
before the successful check. Existing untracked duplicate-name files are not
part of the contribution. The full selected cold replay, native admission,
repository-wide historical suites and hosted CI were not run.

## Overlap and attribution

- PR1048 remains open at `07730cd8302c378607259a9ad0efb73e0b57a2f2`.
- PR1182 remains open at `0213b8911bfeefd5c81ddf320bac6a0fb7e86215`; its certified
  bracket repair is reused unchanged with attribution, not re-proposed as ours.
- Ian Libânio's PR933 at `b9348c6907516e55dc07e135ad4d7a480d4f9840` already reports
  broader relocation/all-frame results, with a 2,000-pair independent sample.
  Its README was read at blob `a1af337e68859ed520a1d72e539339a076fc09a2`.
  This corrects the earlier overlap record's omission. Its larger domain was
  not replayed or certified here. We claim neither first priority for the
  negative result nor equivalence with its domains or quotients.
- PR1368 at `6ae784908c57f3aa5a2165d382b21a40accdf7a6` gives a lower-frame
  obstruction for eight separate phase-B blocks. PR1310 at
  `b9ca10f02fca37c8214d880c244ac14ead6bae7a` concerns complex k8 gauges, and PR1371
  at `d47c4c300a53bb206becd13db89cea8c287c929b` concerns a PR589 projector identity.
  None was imported or is claimed to be superseded.

Live PR searches included `1048`, `reframing`, and `two-move`, and latest-created
metadata through PR1379. The start-here and handoff discussions 1163/1166 were
read; literal 1048/1182/reframing matches were absent in the fetched handoff
page. This is bounded overlap evidence, not an exhaustive novelty audit.

The useful addition is the certified signed reference-root comparison,
explicit complete pair-projection argument, and full separate replay of the
declared narrower domain. Existing maintainer counterexamples and the PR1182
bracket repair are reproduced and credited. Source licenses, supplier credit,
Brian Ross's Krenn/ThetaTwist methodological attribution and substantial AI
assistance disclosure are retained. No code from PR933 was copied.
