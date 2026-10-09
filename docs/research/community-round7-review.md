# Community integration: recycled bit registers and verification

Douglas Colkitt, with OpenAI Codex assistance, 2026-10-09. This is a
conditional maintainer audit, not independent human peer review or a formal
proof of integer multiplication. Main publication and PR closures are left
for the morning. The integration branch is `integration/overnight-20261009`,
based on main `d1d6c070f5a8c684727ee7ec35d930f9ebfa9758`.

## Selected composition

The candidate is **κ = 472154791/1000000000000 = 0.000472154791**,
about 2.44% above the preceding `0.0004609169`. It composes:

| PR | Author | Pinned head | Contribution |
|---|---|---|---|
| #147 | William Porter / hpst3r | `29383a28d96b9880edbe59ed930f1da1dd6fdfa6` | 1,549 terminal accumulators eliminated |
| #150 | DaysSky | `40d4038760ebb6d6d3d702ce88fa3645de29f0c1` | Delayed reads and 3,338 physical register handoffs |
| #146 | Thomas Marchand / Th0rgal | `70355a3192028852598e96624ae29b389e664451` | 187 additional selected gauges |
| #151 | SovereignSteak | `5a46ac37ae2e2f8f75637cb2cf6b9d0b36afc436` | Parallel identical gauge/recycling composition; atom 473/10^6 |
| #148 | Rohan Gupta / gupt1156 | `975c3cf5d4ee0c90d5a76500d431bfc59102bb72` | Atom exponent reduced to 1/2000 |

The #147/#150/#151 histories are retained as merge ancestors. #146/#148 are
selectively composed, with source heads, original selection bytes and credit
in the [source manifest](../../research/recycled-bit-integration/SOURCE.json).
Their old root documents and mutually incompatible selected certificates are
not wholesale merged. Draft status is retained; no PR is closed by this review.

James Chang's #124 compensated birth-read identity and SovereignSteak's #122
terminal elimination are explicit dependencies. All #144, #130, #128, #117,
#97, Swapnil Jain and earlier framework credits remain applicable. The
[notice](../../research/recycled-bit-integration/NOTICE) distinguishes direct
contributions, inherited mechanisms and integration work.

The initially checked composition used atom 1/2000 and gave
0.000472143085. #151 arrived during the review, independently supplying the
same finite row and physical plan plus the tighter atom choice. Its complete
scalar and exact arithmetic checks pass; the existing full rational-frame
check applies to the identical word. Both parallel gauge contributions are
credited. The original 106-PR snapshot remains immutable; #151 is separately
recorded as the sole late addition to this review batch.

## Mathematical review

A terminal accumulator is eligible only if it is never read as an auxiliary
control and has one final target. Its initial-dirt subtraction and final
read cancel, so each actual forward update can go straight to its target.
The new target frame chain still has to be nested; scalar cancellation alone
does not authorize moving the operation to another frame.

A dead physical register can become a later virtual recipient only after
its last use and before the recipient's untouched-value read. That read must
observe the donor's actual final value, not its original dirt. The negative
response cancels the subsequent response to that same value even when it is
correlated with sources and other scratch. Every physical source/workspace
update must be inverted in actual reverse chronology. Keeping the old inverse
order fails a concrete corruption control. Restoring two virtual values is
not required: the single surviving physical input must be restored exactly.

The #146 subset is a superset of the original selected gauges. After deleting
the eliminated slots and recipient entrance gauges, the composed timetable
is solved again. The regenerated word retains exactly #150's 4,878 new
frame-pair obligations. Every scalar gate uses one common frame; the actual
new rational inclusions and nondegeneracy are checked from reconstructed
integer bases. Inherited transitions are ordered subsequences of certified
chains, and the full check also verifies every distinct inherited inclusion.

The full scalar word is evaluated on independent formal variables for all
27,521 data, target and physical scratch inputs, over both F2 and Z. The
finite certificate includes all local chains, copied centers, exterior gauge
children, data finishes, rare-class fallback and both supplier moments. The
rank mass is 1,896,925 in dimension 69; W is 27,521 and deficit is 2,024.
The largest child is 60. The old dimension-69 row reserve remains conservative.
The complex supplier, full router and semantic precision guard are unchanged.

The #148 atom setting and #151’s tighter 473/10^6 setting pass both strict subordinate-adapter inequalities on
the composed profile. All 47 final inequalities and seven margins must pass
with the full effective bit saving. Adjacent-grid exclusion is specific to
this profile and parameter choice. In particular #146's min-cut optimality
is not claimed for the changed schedule or for the true transcendental
objective rather than its finite rational upper-bound weights.

## Verification improvements

**#101, Andrew Barnes / Bortlesboat**, reviewed at
`76f55061bb50d8244c985807909a5f44254bd906`, binds every literal scatter
incidence to the paid output multiset, checks index domains and rejects
optimized Python. The cancelling-scatter counterexample is rfu08's #64
contribution. The exact reviewed change and its history are integrated;
provenance conflicts are resolved against the current README and Makefile.
All 16 focused tests pass locally. Historical numerical witnesses are unchanged.

**#64, rfu08**, at unchanged head
`2d970ab3ca0271cfb2b609dc9aae1b7073b7774d`, contributes independently scoped
finite audits and formal interfaces. Its literal Lean profiles are historical
PR64/68/73 instances, not the new selected construction. The package contains
298 audited declarations in 27 unique modules, including concrete stack and
counter primitives, floor-child recurrence and conditional state-cost proofs.
The complete scheduler, routing and analytic multiplier instantiation remains
unfinished. The full source-bound package is integrated with offline checks,
pinned-source finite replay and kernel-audit CI targets. Fresh offline checks
pass; final Linux and kernel validation is recorded separately.

## Queue review and next mechanisms

The [queue map](../../research/overnight-pr-review-20261009/QUEUE.md) gives
106 pinned dispositions and author-mentioned dependencies. Every row is
triaged; this is not a claim to have fully proved all 106 submissions.
Older headlines are not merged over the current result, and lower numerical
claims are not treated as invalid or undeserving of credit.

The unchanged #83 fixed-profile recursion barrier remains scoped to its
64 complete profiles. #90's documentation intent is reflected in the current
selected-result/review/reproduction links. #122/#124 mechanisms have concrete
descendants in this integration. Other promising transfers include #143's
per-target read deadlines and joint frame/gauge optimization, and #125/#133/
#145 frame shrinking and handoff-boundary adjustment. Their different local
words and cover geometries require new paid ledgers before claiming a gain.

There is also a concrete dependency problem to preserve in the queue:
#145's current README retracts its paired lockstep number following
[Swapnil Jain's #132 counterexample report](https://github.com/CrocSwap/integer-mult-bounds/pull/132#issuecomment-6073516734).
#135 relies on that live-core lockstep schedule and already lists its missing
physical execution proof. Its headline is not eligible for integration without
repair. Orthogonal address directions do not make a shared physical stream
independent storage for concurrent live cores. The selected construction uses
sequential completed cores. This review inspected the report and retraction;
it did not independently run the commenter's small counterexample.

## Reproduction and evidence

Run `make recycled-bit-full-verify` for the new complete finite check and
`make verify-tests` for the corruption controls. The original #147 and #150
checkers remain executable. `make machine-transfer-check` and
`make formal-machine-transfer-verify` have their own explicitly limited scope.
The [validation receipt](community-round7-validation.json) records local
results and final Linux status separately. The committed CI configuration
alone is not evidence of a successful run. No change to main is authorized
by this report alone.
