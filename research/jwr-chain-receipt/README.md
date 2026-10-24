# jwr404 halo-absorption chain: disposition receipt

**Task:** overlap-receipt. **Base:** canonical main `f626db5c`. **No new κ. No closures recommended.**

This receipt covers 13 open PRs by jwr404 that extend the Gaussian halo-tensor chain after the merged #4506 (`research/gaussian-tensor-nine-faces`).

## Disposition

| PR | Package | Answers open question of | Status at base |
|----|---------|--------------------------|----------------|
| #4508 | gaussian-tensor-nine-axis | #4506 (merged) | open, not retained |
| #4509 | gaussian-tensor-nine-bridge | #4508 | open, not retained |
| #4511 | gaussian-axis-inheritance | #4509 | open, not retained |
| #4512 | gaussian-second-row | #4511 | open, not retained |
| #4515 | gaussian-operator-lift | #4512 | open, not retained |
| #4520 | gaussian-restricted-gate | (root; cites #4515, #4517) | open, not retained |
| #4523 | gaussian-global-tail | (root; cites #4520) | open, not retained |
| #4524 | gaussian-unequal-gate | (root) | open, not retained |
| #4526 | gaussian-heavy-slice | #4524 | open, not retained |
| #4527 | gaussian-slice-ten-gate | #4526 | open, not retained |
| #4528 | gaussian-slice-ten-copies | #4527 | open, not retained |
| #4530 | gaussian-slice-nine-gate | #4528 | open, not retained |
| #4531 | gaussian-slice-nine-copies | #4530 | open, not retained |

- **Retention.** No package from the set is present at its merge base or on main `f626db5c`. Each PR is a single-package addition of 5 files. Exact heads, merge bases and per-file blobs are in `RECEIPT.json`.
- **Factor-9 versus factor-10.** #4530 and #4531 restate #4527 and #4528 with the factor-9 gate instead of factor 10. The factor-10 statements stay valid but are coarser, so a maintainer taking the slice results needs only the factor-9 pair, plus the factor-10 pair for attribution.
- **Outside the author's set.** #4517 (pinterbanget, open) answers #4515's open question; #4520 cites it.

## Verify

```text
python3 -B research/jwr-chain-receipt/verify.py
```

The verifier checks recorded facts only: SHA well-formedness, single-package additions, no retention at base, answer edges pointing backwards, and the factor-9/10 pairing. It does not test the working tree, so it still replays after any of these PRs merges. To compare heads, fetch `pull/<n>/head`.

## Limitations

- This records structure and provenance. It does not replay or review the mathematics of any PR.
- PR heads may move after recording; compare against `RECEIPT.json`.

## Open next questions

- An independent mathematical replay of the factor-9 slice pair #4530/#4531, which carries the chain's final absorption statements. First step: run each PR's registered verifier at its recorded head.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance. Credit for all listed results: jwr404.
