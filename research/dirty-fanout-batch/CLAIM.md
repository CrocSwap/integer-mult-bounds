# Sprint claim: dirty common-factor fanout

- Track: recursive interfaces; OS-random seed **58** (Python secrets.randbelow(100)).
- Exact base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
- Object: simultaneous independent output shears `y_i += A_i B x` with a shared, unchanged input and entirely dirty workspace.
- Method: one batched dirty commutator, exact noncommutative replay, a restricted-query lower bound, and complete weighted recursive cost/storage accounting.
- Seed choices: fanout `2 + 58 % 5 = 5`, common factor length `1 + 58 % 17 = 8`; left lengths 1 through 5.
- Deliverable: scoped interface construction and standalone exact verifier/certificate; no new kappa.
- Finish target: 2026-10-13 08:29 UTC (19:29 Australia/Melbourne). Final 10 minutes reserved for verification and handoff.

Three candidates were considered: cancellation of repeated transparent calls; deferred sibling cleanup; shared common-right-factor output batching. The first overlaps PR840's native dyadic pair; the second overlaps PR822's dirty connector reuse and PR714/788 clean checkpoints. The third changes the multi-output contract and retains conservative private scratch.

At claim time the public issues page listed only #650, with no pinned sprint coordination issue. GitHub API read access returned `Forbidden`; no claim was posted. Public open-PR metadata was checked through #856, plus searches for boundary, echo/checkpoint/batch/prefix, common right factor, fanout and multiple outputs. Relevant context: #628, #663, #673, #689, #714, #730, #788, #822, #840. Existing echo work changes decomposition/scratch for one product output; this work batches distinct outputs sharing B. No claim of general algebraic novelty or first discovery is made.

Selected state read: #799/#589, kappa `1661634653669567/10^18`, its actual X4 proof note and maintainer review. This package does not change that construction.

## Result update

Completed one scoped construction: common-factor multi-output batching with
246 versus 680 complete binary factor-shear calls and four dirty arrays.
The proof, full weighted/storage/routing/precision bill, exact certificate,
independent checks and controls are in [README.md](README.md) and
[VALIDATION.md](VALIDATION.md). There is no new κ or admitted supplier.

The overlap refresh reached #859 and explicitly distinguished #793's scalar
coefficient batching. No coordination issue was found. API access is denied,
so the completed contribution is handed off as one local commit and clean patch;
no external claim or PR was posted. Existing source and the selected frontier
remain unchanged.
