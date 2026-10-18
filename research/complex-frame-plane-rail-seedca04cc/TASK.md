# Cycle 15 task card: two-coordinate frame rail

- Seed: `ca04ccbf3c8c214a13d9c2452e780d32` (OS-random selector seed)
- Track: `complex-mechanisms`
- Catalogue task: `complex-rank-shape-decoder`
- Priority revision: 3
- Catalogue SHA-256: `6686ad58f1fbdbc87134a78901b60fd53a20d3984355e91defbbebc9e9fa8075`
- Base commit: `0b1cccf86e2f5132ed286a26ef0a681a495740ea`
- Selected-record SHA-256: `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`

## Question and changed hypothesis

In the selected PR1094 native local word, can one canonical two-coordinate plane
`span(e_i,e_j)` be introduced at a helper-to-helper addition and propagated by
inclusion-minimal common-frame closure through later additions, keeping every
scalar gate, start frame, exact A/B target-level and centre-frame boundary,
required target endpoint, and dirty-helper endpoint fixed? Does any such
schedule move enough paid rank mass into larger children to raise the exact
fixed-template packing ceiling by at least 5%?

The change is a global temporal frame schedule for one shared plane. It is not
an added scalar operation or a new endpoint/helper inventory. Every induced
frame climb is charged at its exact rank; candidates changing the exact A/B
boundary, target endpoint, or helper endpoint are rejected.

## Bounded domain and stopping rule

Search the 36 coordinate two-planes of the pinned nine-dimensional F2 frame
space and every A/B addition in the selected word whose two operands are
helpers. For each (plane, seed gate), propagate the plane forward through the
word by the least frame enlargement that preserves monotonicity. Reject any
schedule that changes one of the exact target-level or centre-frame barriers
at the A/B boundary, or any final target/helper endpoint. Compute the complete
exact rank histogram and fixed-template moment ceiling for every surviving
schedule. Stop after this finite domain is covered; report the best profile and
ceiling, including the exact rejection counts by interface and endpoint.

The optimistic screen is favorable: the baseline selected ceiling is
`0.001690054109089`; moving 10% of local rank mass to rank 9 reaches only
`1.04318x`, so at least about 12% must be redistributed to cross the card's
5% threshold. A single local gate change is not a sufficient experiment.

## Source and overlap

Pinned word: member
`candidate/strict/global/base/providers/gauge44/FULL-WORD.json.gz` of
`research/community-frontier1094-audit/selected-replay.tar.gz` (archive SHA-256
`f1da80610bf33c58527f18ad63b4350d0b864e1d4486141ee17ac9bed4d529d6`, member
SHA-256 `49596aa4ed4fd36cd4582fd0e8ddeb09fd80370a7d8aea1ede52a135b536d289`).
The current selected local profile is `{1:2412, 2:418, 3:432, 4:142, 5:82,
8:8}`. The base word and selected record remain untouched.

Relevant predecessors: selected complex provider PR #1094; exact fixed late
block optimum PR #1429 / package `complex-block-rank-optimum`; frame coalescence
PR #699 and SW4 eight-B-frame package `complex-sw4-frame8`; cross-block fixed
late-interface floor PR #1517. Adjacent open PR #1186 supplies an exact frame
solver and delivery-rewrite search for an older PR #1148 joint-entrance k8 word;
this task instead exhausts forced coordinate-plane closures on the selected
PR1094 word, preserving its exact interfaces. The refreshed overlap search at
2026-10-14 16:29:05 UTC covered all 438 open PRs and 619 discussions. Its five
text matches were this run's two claim comments, one plane-port discussion
thread, and two local background documents; no PR title/body matched the query.
Manual review found open PR #1825 (paired plane-port decoder on selected labels)
and PR #1900 (five plane queries for the P111 bit decoder) change the coverage
contract/decoder, while PR #1186 optimizes frames on an older word. These differ
from this fixed-coverage, fixed-word temporal frame schedule. Nearby active
scopes #18924220 (Cartesian source-destination grid), PR #1909 (tetrad-local
masked decoder), and Discussion #1622 (overcomplete ten-term decoder) also
concern different objects and methods. Discussion claim #18924772 and PRs
#1825/#1900 study two-unpaid-coordinate plane-port decoders; this run keeps
coverage and helper inventory unchanged and varies only internal frame timing.

Expected artifact: exact candidate enumerator/closure verifier, replay command,
profile/ceiling receipt, endpoint-conflict and no-op controls, predecessor
attribution, and explicit absence of a new-kappa claim unless full integration
is separately established.

Correction: the first posted claim used the older PR699 SW4 word and was
released at Discussion comment #18926956 before packaging. This revised card
uses the exact selected PR1094 source archive and word member above.

Claim expiry: 2026-10-14 17:18:00 UTC.
