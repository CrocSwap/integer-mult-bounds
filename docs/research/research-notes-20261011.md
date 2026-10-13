# Research and verification integration, 2026-10-11

A subsequent [frontier integration](community-pr531-review.md) adds the research
packages and proofs from #531, #523 and #493, with fresh finite dependency
replays and a new selected conditional witness. The batch below remains the
historical research-only integration.

**No change to the selected κ.** Research notes, negative results, experiment
records and verification improvements are integrated on their own merits.
The [selected conditional construction](community-pr279-review.md) remains
κ=0.000723571590007464. Inclusion of a research package is not adoption of a
larger numerical claim in its historical records.

The [queue snapshot](pr-queue-20261011.json) contains 457 open PRs, including
77 drafts. Many older contributions remain open despite prior cherry-picked
integration or review. This batch does not claim to review the entire queue.

## Newly reviewed research packages

| PR | Contributor | Included contribution | Review scope |
|---|---|---|---|
| [#468](https://github.com/CrocSwap/integer-mult-bounds/pull/468) | Ali Romman | [Nine-call lower bound](../../research/bit-three-register-lower-bound/README.md) for the specified three-register abelian bit model | Read the symbolic reductions and exact-search implementation; replay both complete engines and controls. This is a scoped computer-assisted result, not Lean verification or a barrier for other register models. |
| [#524](https://github.com/CrocSwap/integer-mult-bounds/pull/524) | Chafik Boukhalfa | [Carry-graded box convolution](../../research/graded-box-convolution/README.md) | Reviewed the mixed-radix carry identity, signed packing and coefficient bounds; independently reran the submitted finite package. This removes a representation overhead in the stated experiment, not the remaining all-size/tape costs. |
| [#477](https://github.com/CrocSwap/integer-mult-bounds/pull/477) | Rohan Arun | [Attributed experiment archive](../../research/experiment-log/README.md) | Checked the complete file manifest, all 100 original idea IDs, 300 initial trial IDs and local links. Historical searches and mathematical claims were **not** independently rerun. Later additions exceed the original campaign counts. |

Exact source heads and execution receipts are in
[the integration record](research-notes-20261011.json). Original commits,
attribution and AI-assistance disclosures are retained. The archive's
classification of timeouts, execution failures and bounded unsuccessful
searches must not be promoted to mathematical impossibility claims.

## Previously reviewed batch now integrated

These seven contributions were prepared on `review/community-round9-ready`
but had not reached main. The [original review ledger](../../research/community-round9-audit/INDEX.md)
records their pinned heads and evidence. The integration retains its two
maintainer clarifications concerning regenerated artifacts and benchmark units.
This pass also corrects a sign typo in #222’s inverse-Gram explanatory text;
the implementation already uses the correct plus sign.

| PR | Contributor | Contribution |
|---|---|---|
| [#239](https://github.com/CrocSwap/integer-mult-bounds/pull/239) | Richard Hoekstra | Exact dual-Gram acceleration for large-frame nondegeneracy tests, with comparison tests. |
| [#222](https://github.com/CrocSwap/integer-mult-bounds/pull/222) | Romain Hédouin | Faster historical bit-word generator; fresh output compared with main's pinned PR181 archive and its independent checker. |
| [#218](https://github.com/CrocSwap/integer-mult-bounds/pull/218) | Joel Pulikkan / GamingPuzzled | Parallel exact frame-pair checks with a serial fallback. |
| [#190](https://github.com/CrocSwap/integer-mult-bounds/pull/190) | Romain Hédouin | Removes unrelated Makefile/README/NOTICE pins from the historical joint-dual calculation; mathematical source obligations stay pinned. |
| [#220](https://github.com/CrocSwap/integer-mult-bounds/pull/220) | Maxime Fleury | Gzip-container reproducibility audit, heuristic scanner and scoped contribution guidance. |
| [#231](https://github.com/CrocSwap/integer-mult-bounds/pull/231) | Joel Pulikkan / GamingPuzzled | Lucas-parity obstruction for the specified star/overlap decoder family, with finite controls. |
| [#209](https://github.com/CrocSwap/integer-mult-bounds/pull/209) | Jacob Sussman | Parallel Fourier-side Lean development reference and attribution. This entry is not a newly rebuilt formalization. |

The source pins for these seven still matched the open PR heads at the queue
snapshot. Their changes were incorporated by cherry-pick, and the seven PRs
were closed after publication and a fresh head check. That closure records
integration, not rejection. #468, #477 and #524 are marked merged by GitHub.

## Verification and remaining queue

Fresh checks cover the modified rational-frame routines, the complete affected
joint-dual suite, the full recycled-bit frame check and its tests, historical
bit-word regeneration, the decoder-parity cases, both newly replayed research
packages, archive integrity, and the selected-result record. Detailed results
and limits are recorded beside the commands in the integration JSON.
The gzip scanner is a heuristic smoke check, not certification of every
regenerated artifact. No new Linux execution or complete Lean build is claimed.

The current-status and contribution-review landing pages now point to the
actual selected gen4 record; their older entries remain historical.

The newer construction queue remains separate. In particular, the inspected
head of [#531](https://github.com/CrocSwap/integer-mult-bounds/pull/531)
claims conditional κ=0.001517760977820331, with a 504-helper complex supplier,
the #523 controller and the #493 bit supplier. Its source, normalized wrapper,
mutable-basis realization, physical allocation and inherited interfaces need
review before selection. This batch does not certify that claim or substitute
a bit-only primitive rate for the multiplication exponent. The broader
obstruction packages #288 and #446 also remain pending their own scoped review.

Maintainer review and integration: Douglas Colkitt with OpenAI Codex assistance.
