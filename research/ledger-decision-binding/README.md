# Bind review-ledger state to the recorded family decision

Research consolidation and tooling correction; **no new κ claim**.
Contributor: roife, with substantial OpenAI Codex assistance, including a
separate agent's read-only review and regression-test work. Apache-2.0.

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Assignment seed: **99**, drawn with Python `secrets.randbelow(100)` using OS
randomness. Seed modulo five selects the fifth recorded family, K492, for the
concrete mutation experiment. This is a bounded metadata audit, not a search
for a stronger construction.

## Finding and resolution

At this base, `scripts/verify_pr_reconciliation.py` accepted a PR626 ledger row
whose `reviewed_head` and `current_head` were both replaced with forty zeroes.
It compared the two ledger fields to each other, while separately comparing
the authoritative decision's reviewed head to its receipt. The missing
comparison was between the ledger row and that decision.

Four other independent changes also passed the complete baseline checker:
marking the row `superseded`, substituting an unrelated integration location,
removing its closure record, and changing its GitHub state from `MERGED` to
`OPEN`. The last is an inconsistency with the frozen decision, not a claim
about live GitHub state. See [RESULT.json](RESULT.json) for exact inputs,
source hashes and both checker outcomes.

The fix checks the following review-state fields projected by
`reconcile_pr_queue.py` against their final authoritative family decision: number, reviewed/current heads,
disposition, GitHub state, integration location, remaining question and closure,
plus completion flags and evidence when supplied by that family. A missing
field is distinct from an explicitly recorded null closure; JSON booleans
remain distinct from integers even inside completion records. The check applies
to all five recorded family rounds (89 records at this base).

This adds a consistency condition to the existing source-hash, receipt,
changed-file, execution and incorporation checks. It does not replace any of
them. Partial reviews may still have incomplete execution and different
reviewed/current heads when those are the recorded values. The earlier
family533 records need not acquire completion fields they never had.

All 89 committed family projections already match their decisions. **No
corruption of the committed ledger or mathematical certificate was found.**
The accepted conditional result at the base remains
`51110230636731/31250000000000000 = 0.001635527380375392`, from PR626 with PR543.
The selected certificate, construction packages and `upstream/` are unchanged.

## Reproduce

From a clone retaining the exact base commit, run:

```sh
python3 -B research/ledger-decision-binding/reproduce.py
```

Only Python's standard library and Git are needed. The script reads the
baseline checker from the pinned commit and checks its SHA-256 before executing
it. It requires the original ledger bytes. Each case substitutes just one
in-memory ledger read; every other read still reaches the checkout. Accepted
baseline runs complete all existing checks; the fixed checker rejects altered
rows early. The script never writes a ledger or contacts GitHub. Expect both checkers to accept the unchanged ledger, the baseline to
accept all five mutations, and the fixed checker to reject all five with a
field-specific error. Its final line is:

```text
PASS: unchanged ledger accepted; all five previously accepted provenance mutations rejected
```

Add `--output /path/to/result.json` to save a fresh report. Further focused
checks are:

```sh
python3 -B -m unittest discover -s tests -p test_pr_reconciliation.py -v
python3 -B scripts/verify_pr_reconciliation.py
```

Expect 14 passing tests and a final `PASS immutable snapshot plus explicit
family rounds: 528 PRs, attributed heads, evidence pins and unresolved questions`.
The tests also reject removed fields and preserve legacy/partial-review
semantics. This is finite metadata validation, not a formal proof of the full
multiplication theorem. All inherited mathematical assumptions remain.

## Selection, overlap and attribution

Three candidate tasks were considered: selected dependency-head consistency,
later-family ledger consistency, and a historical exceptional-root negative
result. All 20 explicit selected dependency heads initially agreed with the
ledger; the exceptional-root topic overlapped open PR630. The ledger failure
mode was chosen. No pinned coordination issue existed when queried; the
scope was claimed locally before the experiment. All 491 open PR titles and
bodies were queried and screened for overlap, including searches for both
reconciliation script names and `pr-ledger`; none targeted this check. A later
refresh covered 497 open PRs through #677. PR675 audits the same selected
construction's mathematical owner boundaries, whereas this contribution binds
review-ledger metadata; neither depends on the other. The stopping rule was
to test the five listed mutations against PR626, repair their common missing
binding, and verify the full existing family projection without expanding
into construction or theorem review.

This builds on Douglas R. Colkitt's reconciliation, family review and evidence
infrastructure, including commit `5c5567d` and its predecessors. PR626's owner
allocation is Chafik Boukhalfa's work on Jeremy Kothe's PR622/623 construction;
eumemic supplied PR543. Their original sources, notices, review limitations
and cumulative attribution remain intact. The independent agent corroborated
four equivalent full-checker mutations on PR622 using the same failure
mechanism; that corroboration is not a separate mathematical audit.
