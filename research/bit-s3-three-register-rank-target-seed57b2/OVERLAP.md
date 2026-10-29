# Overlap intake

## Discovery pass

- The assigned offline command was run:
  `python3 scripts/find_overlap.py --task bit-new-register-model --offline --cache /home/cinna/int-bounds-pass/20261018-luna-xhigh/overlap.json --limit 8`.
- It reported `POSSIBLE_OVERLAP_NOT_A_NOVELTY_CERTIFICATE`, 140 broad matches,
  586 cached open PRs and 2,536 cached Discussions, with an explicit warning
  that both remote snapshots were offline. The most relevant leads were
  Discussion [#2012](https://github.com/CrocSwap/integer-mult-bounds/discussions/2012)
  and [#1999](https://github.com/CrocSwap/integer-mult-bounds/discussions/1999).
- Live Discussion #2012 says its exact result is minimum eight for the six
  targets with two `z=sts` entries and one `c=st` or `ts` entry. That is not
  `diag([s],[t],[st])`. Its latest comment remained dated 2026-10-14.
  Discussion #1999 / PR #2010 uses `SL_2(F3)`, not `S3`.
- The two-register `S3` all-pairs census is in PR #1870 and
  `research/bit-s3-two-target-census-seed36501`; it does not include three
  registers.

## Final live delta check

Checked 2026-10-19 02:24 UTC. `git fetch origin main` returned
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, the frozen task base. No changes
were present in the current-priority, procedure, family-status or task
catalogue guidance.

The live open-PR API was fully paginated again: 586 records. A title/body scan
for the named endpoint, `F2[S3]` three-register models, and mixed three-role
`S3` targets found no open PR matching this exact target. The latest live
comments were refreshed in handoff thread #1166 (684 comments) and mechanism
proposals #1167 (152 comments); no comment stated this endpoint. The latest
bit-mechanism handoff in #1166 concerns the Q8 mixed-negative lower bound,
which uses a different group and target. Start-here #1163 was read again;
claims are advisory and overlap must be checked at submission.

No claim or PR was posted because this donor session explicitly prohibits
external messages and publication. GitHub's board is a changing research
surface; this check supports a scoped local result, not a novelty certificate.
