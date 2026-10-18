# Local sprint claim

Contributor: William Lawyer, with substantial OpenAI Codex assistance.
Start: 2026-10-13 07:54:33 UTC. Expected finish: by 09:54:33 UTC.
Track: structural decoder research. Assignment seed: **40**, one operating-system
draw using Python `secrets.randbelow(100)`.
Base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.

Three narrow candidates were considered:

1. Test a mixed partial-hyperplane rectangle decoder on the Gaussian E8 unit.
   PR767 leaves partial supports open, but a positive supplier would require
   a new complete cost and realization argument.
2. Test PR770's explicit hyperplane-pair dual on **all** nonorthogonal cliques,
   including non-maximal cliques. Its inspected proof expressly excludes them.
3. Extend the Gaussian scalar floor to fixed-support nonlinear messages.
   PR785 supplies this mechanism on Hurwitz geometry; that transfer offers
   less separation from existing work than the all-clique certificate gap.

Selected candidate: **2**. Seed 40 selects the second candidate by `seed % 3`;
its useful diversification is the previously excluded certificate domain.
Object: the 60 Gaussian E8 lines and PR770's 900 ordered orthogonal-normal
hyperplane pairs. Hypothesis: each nonempty nonorthogonal clique Q meets both
hyperplanes in at least `45 |Q|` ordered pairs. Test by complete integer
clique enumeration, with a separately constructed geometry and traversal.
Deliverable: a solver-free exact dual certificate closing this method's gap,
or an explicit failed-dual witness; no new kappa claim.

The live inventory retrieved at 07:58:21 UTC contains 654 open PRs through
#857 and no open issues or pinned coordination issue. Scope overlaps were
checked in PR738, PR767, PR770, PR785, PR798 and PR801; their exact inspected
heads will be retained with the result. The ledger marks PR620 partially
reviewed; pending PR claims are not accepted supplier results.
No external reservation issue is opened. This local claim is the reservation.

Research will stop by 09:24:33 UTC, leaving the final 30 minutes for verification
and handoff. One evidence-driven pivot is allowed if the proposed dual fails.

## Result update

Result posted at 2026-10-13 08:41:32 UTC:
[PR868: Gaussian E8 all-clique certificate ceiling is 40](https://github.com/CrocSwap/integer-mult-bounds/pull/868).
Research note / scoped negative result, **no new kappa**. The first result
commit is `7cdd3ac12254290c55bac602d5e293dea4d981ae`.

The original 900-pair extension fails concretely on singleton `{0}`:
42 hits rather than 45. One evidence-driven pivot retains the 180 ordered
orthogonal-normal hyperplane pairs with six-line intersection. Each has
Gaussian pairing charge two. Every nonempty clique has at least nine hits
per vertex, bounding every nonnegative weighted-clique certificate by 40.
This closes PR770's expressly excluded non-maximal-clique domain; the
predecessor's feasible value 40 and scalar decoder interval [40,60] are
unchanged. A cost-40 decoder and a stronger multiplication bound are not
constructed.

Domain and stopping rule: every nonempty clique in the fixed 60-line Gaussian
E8 nonorthogonality graph, extending until no vertex can be added; no sample
or size cutoff. Completed coverage: **2,068,372 cliques**, sizes 1–12, with
all counts and minima in `CERTIFICATE.json`. Seed 40 selected the task; the
coverage itself is deterministic and exhaustive. The increasing-order
traversal and an independent Gaussian-coordinate, Bron–Kerbosch/submask
implementation agree on the complete domain digest
`e07f4d5b163728561aa881fd76ba32092d93a2914c2718019964f8dd013e8efd`.

The code and mathematical inputs pass ordinary replays and an isolated,
optimized cold export from staged Git blobs. All 10 package tests pass,
including source/certificate corruption controls and exhaustive small-graph
checks. `VALIDATION.md` records the measured checks and exclusions. A separate
scoped AI worker reviewed the proof; no independent human review is claimed.

The refreshed overlap inventory at 08:33 UTC contains 661 open PRs through
#866, no coordination issue, no duplicate of this scope, and unchanged heads
for all eight inspected source PRs. Exact pins and predecessor credits are
retained. No external claim requires an update; this is the single local
claim result update. Research stopped after the complete certificate and
independent replay, within the 120-minute budget, leaving ample verification
and handoff time. Only the new package changes; no selected frontier or
`upstream/` files are edited.
