# Sprint claim: parity edge compatibility

- Track: structural decoder research; OS assignment seed **46**.
- Exact base: `8bddbee377e2f3ce1f1247196c4b290d55767d20`.
- Started: 2026-10-13 16:09 UTC; expected finish: 16:49 UTC.
- Verification and handoff reserved: 16:39–16:49 UTC.
- Scope: the fixed historical `ParitySide(10)` DAG, all internal edges whose
  endpoints each admit a source/target-incident-safe frame at their minimum
  separating dimension. Exhaust all endpoint frame choices and check nesting
  and internal-edge residual legality. Record explicit incompatible edges if
  found. This is a finite geometry question, not a proposed new supplier.
- Method: exact binary vector spaces, exhaustive radical-partner cosets,
  direct residual checks and independently checked obstruction witnesses.
- Deliverable: a reproducible census, exact certificate, proof of the finite
  enumeration domain, source pins and meaningful negative controls.

## Candidate choice and overlap

Three narrow candidates were considered: (1) compatible minimum frames across
internal DAG edges; (2) incident-safe larger-frame repairs at radical-one nodes;
(3) prescribed three-target deletion thresholds. Candidate 2 is covered by
PR #993; candidate 3 is covered by #966 and independently checked by #971.
Candidate 1 directly tests a remaining stage-interface obligation.

The `h=10` member is the first dimension beyond the documented `h=8` failure
and connects to the complete #972/#993 local censuses. The novelty is the
edge constraint. Seed 46 also selects zero-based entry 46 of the 80-edge
follow-up for a separate explicit repair inspection: edge `1238 -> 1246`,
with frames `span(64,9,5)` and `span(930,64,18,8,4,1)`. The seed does not
restrict exhaustive coverage or turn a repeated local census into novelty.

No open sprint coordination issue was found. Immediate pre-claim PR refresh
at 16:15 UTC found #972 at `f39f92a085fc95fe4245b06d4a695739d79763bc`,
#993 at `76b71ff5bea1088fb5019dea25fe89698287e673`, and #920 at
`913817423bbfaf241dec1d6b9edb1c7ded349508`. All three concern pointwise
or source/target incident geometry; #972/#993 explicitly leave simultaneous
nested frames unresolved. The review ledger and historical parity failure
were read before selection. This is a local claim; no reservation issue
was opened.

## Acceptance and boundaries

Every reported edge count must come from the fixed DAG and an exhaustive
endpoint domain. A rejection at minimum dimensions must not be described as
an obstruction at every dimension. Already impossible individual nodes are
excluded from the edge question and counted separately. The result must have
one offline command and corruption controls that remain effective under `-O`.
No selected certificate, production supplier, `upstream/`, or unrelated file
will change. No complete multiplication theorem or improved kappa is claimed.

## Evidence-driven extension at 16:21 UTC

The full minimum-dimension census found 200 failed edges, including 80 whose
target has a completable radical-one source span. The extension quotients for
both endpoints of these 80 edges have dimension at most three. Exhausting
all dimensions is therefore a small, closed follow-up rather than a broad
search: it separates 30 absolute pair obstructions from 50 edges repaired
with one extra endpoint dimension. The all-dimension claim is confined to
these 80 explicitly selected edges. The original 120 nondegenerate-span
failures are retained as historical corroboration, not claimed as new.

Contributor: thakrarsagar; substantial OpenAI Codex assistance in research,
implementation, checking and writing.

## Completed handoff

Submitted [PR #1014](https://github.com/CrocSwap/integer-mult-bounds/pull/1014)
on 2026-10-13 at 16:37 UTC. The exact result is 200 failed minimum-frame
edges, including 80 completed-radical targets. Exhausting every dimension
for those 80 proves 30 absolute endpoint-pair obstructions and supplies
50 exact one-dimension local repairs. Ten built-in checks, four corruption
trials, four historical tests and selected-record consistency pass. Final
verification and packaging began at 16:31 UTC; the contribution finished
ahead of the 40-minute bound. No new kappa or complete supplier is claimed.
