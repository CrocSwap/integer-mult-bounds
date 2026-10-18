# Cycle 3 claim

Claimed 2026-10-13 at 16:48 UTC. Assignment seed 7 was drawn once with
`secrets.randbelow(100)`, using OS randomness. Track: bit supplier.
Base: `2921874911956718fcaaaf9396fe8267b3cfa9f0`, clean fetched main.
Branch: `research/cycle03-seed07-helper-quartets`.
Finish by 17:23:24 UTC; reserve 17:13:24 onward for verification and handoff.

Hypothesis: a general GL(4,2) basis on the union of two disjoint helper pairs
can reduce the complete ADD count of the precision-admitted PR941 R439
candidate while retaining its 104-bit local and 192-bit nine-stage caps.
Freeze the PR915 target basis and every operation outside D. No new kappa,
selected-supplier adoption, global regeneration or changes to upstream/.

Method and stopping rule: choose exactly 64 distinct pair-of-pair indices
by sorting SHA256 of `7:i:j` over all 19,701 unordered pairs of the 199
PR941 pairs. Enumerate all 20,160 GL(4,2) matrices by breadth-first search
using lexicographically ordered XOR generators, retaining one shortest
word per matrix. Price all 1,290,240 combinations with preparation and
literal reverse cleanup included. For each quartet reconstruct its cheapest
representative, breaking ties by matrix tuple, and check the complete word's
positive precision bounds. Pick one admitted improvement by complete ADDs,
then F, B and quartet indices. No adaptive restarts or combination of winners.
If none passes, report the finite failed search, not a general impossibility.

Optimistic complete price before implementation:
`6220 + 612 + 2*(197 + length(H)) + weight(E*K*H_inverse)`.
The 6,220 outside-D ADDs, 306 target preparations and 306 restorations,
197 untouched helper pairs, complete injection and both quartet passes
are all charged. Paid recursive ranks, helpers, copies and frame paths stay
fixed; a smaller local word alone does not establish a better supplier bound.

Three candidates considered: this four-helper fusion; a simultaneous
helper-and-target basis change; further phase-A retiming. Choose the first
because its exact finite class and complete price fit this cycle. The second
would change two interacting contracts; the third overlaps existing prefix
and moment work.

Coordination checked immediately before claiming: no pinned sprint and only
open issues #913 and #650, neither coordination. No reservation issue opened.
Live PR metadata checked through #1021; all-state searches for GL(4,2),
four-helper, quartet and helper inspected. PR941 disjoint matching, PR965
pair-plus-singleton GL(3,2), PR967 three-helper stars and PR978 historical
R420 sharing are predecessors or adjacent scopes. PR1015 is phase B and
PR1016 is a fixed-frame moment obstruction. This search is a four-helper
fusion around the frozen PR941 matching, with all other pairs retained.

Deliverable: exact witness and bounded-search census with source pins,
independent finite replay, negative controls, cost and scope proof; one PR
only if useful evidence and relevant checks pass, otherwise a clean local
patch and handoff. Sagar Thakrar / @thakrarsagar, with substantial OpenAI
Codex assistance. Apache-2.0; predecessor attribution retained.

## Completed result

Submitted 2026-10-13 at 17:10:45 UTC:
https://github.com/CrocSwap/integer-mult-bounds/pull/1045
Implementation head: `51871a0aa67132565acba1de38bb97db14a187fb`.
This completion note is the one result update to the local claim.

All 64 quartets and all 1,290,240 basis prices completed. The chosen quartet
`[269,88,288,153]` uses three preparations in place of two, saves five
injection ADDs and costs two additional preparation/restoration ADDs.
Complete cost: 11,949 to 11,946; this is the exact minimum in the declared
64-quartet class. The independently replayed all-disjoint-pair floor is
11,948. Sixty-two quartets give no improvement and one other saves one ADD.
Every cheapest representative passes the two inherited precision caps.
F becomes 70,355; B remains 10,548,832. No new kappa or best-circuit claim.

Verification includes independent group/domain/distance and full-price
censuses; the 96,141-edge pair-bound dual; 661 input columns in both D
directions; 11 local and four external adverse cases plus a charged neutral
case; unchanged owning checks; native 5/9/11-stage replay on both words and
96 rejected bridge controls; 43 source pins; 25 selected-record and nine
finite-bit-contract tests. The native receipt records 186 dependency hashes.
Verification and handoff occupied the final part of the cycle, beginning
before 17:00 UTC, ahead of the reserved 17:13:24 start.

Metadata and claims were refreshed through #1043 immediately before
submission. PR1040 changes the target basis after PR967, whereas this
construction freezes E and changes four PR941 helpers; it is credited.
PR1023 is a hosting-width result, PR1027 is an R480 six-wire circuit and
PR1043 changes source access and helper stock. No same-object claim was
found. Refreshed main is still the recorded base; all 43 source blobs and
the selected kappa are unchanged. No pinned sprint exists. The repository
has neither a codex nor a codex-automation label available.

PR1045 is open and attached to the originating chat. GitHub CI was queued
at the 17:11 UTC submission check; success is not asserted. Whole-hosted
adoption, the complete supplier invoice, outer assembly and inherited
uniform/realization/tape/analytic assumptions remain. No full repository
suite, selected supplier cold replay, Linux run or formal proof was done.
