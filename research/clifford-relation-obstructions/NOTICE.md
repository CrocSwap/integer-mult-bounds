# Attribution and source scope

Prepared by [littleBro](https://github.com/littleBro) with substantial OpenAI
Codex assistance in the research, implementation, proof exposition, packaging
and validation. New contribution under the repository's Apache-2.0 license.
No independent human review or contributor endorsement is represented as
completed.

The open complex m=3, W=3, s=8 register problem and prior exclusions are
credited to eumemic's [PR #288](https://github.com/CrocSwap/integer-mult-bounds/pull/288),
pinned at `475a088b5862f75f0b10596cfd6842d19531a5ec`, and the predecessors it
credits, including Swapnil Jain's closed-ideas list and P1/P2 and the upstream
Clifford-frame framework. This package does not claim to originate that problem
or the general algebraic methods.

The implementation is a focused extraction and adaptation of same-author
local exploratory packages. `ORIGINS.json` records hashes of those source
snapshots and of the earlier proof payload. Those provenance hashes are not
external dependencies or a claim that the snapshots were publicly reviewed.
All code and exact witnesses required here are supplied in this directory.

The source target is CrocSwap/integer-mult-bounds main at
`66849e1475c930fd7732b1a0067ffee7e1e95f60`. Its selected construction was not
changed or replayed as part of this standalone contribution. At that base,
the selected kappa was 0.001635527380375392, conditional as stated in the
selected record and maintainer review.

Overlap review read the earlier open-PR metadata through #661 and refreshed
recent metadata through #666. PR #620 concerns E8/decoder research; #634
concerns coding-gap and minrank questions; #651 concerns fixed K-triangle
delivery; #661 concerns fixed-order R420 frame optimality; #662 accelerates
existing helper checks. None of those descriptions supplies these 33 fixed
register-word certificates. This comparison is not an audit of every PR diff
or a proof of literature novelty. The scoped result remains open to review.
