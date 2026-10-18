# Bounded PR review batches

Use a frozen inventory of **40 PRs per batch** when the queue is large, with
completed compatible subsets normally published in checkpoints of roughly 10.
An authorized historical reconciliation may freeze 100 PRs, using shared-content
indexes and separate per-PR dispositions. That is a reconciliation inventory,
not 100 full replays or permission to close unmatched work. Compare against the
PR's recorded base and cross-check GitHub's complete changed-file count; comparing
only against today's main can omit files incorporated after submission.
Smaller 12–24 PR inventories remain appropriate for dependency-heavy work.
Batch size is a work inventory, not a promise that every PR will pass review
or be merged. Research
notes, negative results, independent checks, Lean work and verification tooling
are first-class contributions alongside new exponent claims.

## Freeze scope before expensive work

Record a timestamped live snapshot, exact PR heads, contributors, complete
changed-file inventories and dependency relationships. Keep author-closed
predecessors as explicit dependencies when their work is used; preserve their
credit without reopening them. New arrivals and changed heads go to a later
batch unless a concrete correctness dependency requires a documented scope
change. A title, green CI, or imported subdirectory is not a completed review.

Use four queues: construction/frontier, verification/Lean/tooling, scoped
research/negative results, and completed-review closure. Work on one related
family at a time, with dependency-ready checks batched together. Avoid repeatedly
mixing unrelated large cold replays into a single review.

## Share expensive work, retain individual decisions

A shared replay may support several PRs only when its source/input hashes,
required stages, artifacts, interface and claim scope match. Run candidate-specific
checks and mutation controls separately. Replaying the newest composition does
not automatically verify every predecessor's theorem or search claim.

For each PR, record:

1. Exact reviewed head and coverage of every changed file.
2. Accepted claim, inherited assumptions, and what is excluded or unverified.
3. Source, execution and adversarial evidence; explicit reasons for dependency reuse.
4. Integration location, adaptations and individual attribution.
5. Final disposition and GitHub state at publication.

Apply the existing review ledger's completion gates. A batch plan is a triage
record and must not silently mark its entries reviewed or incorporated.

## Publish in checkpoints

Land completed, compatible subsets together. One difficult or failing PR should
not hold the entire batch open indefinitely: record the exact unresolved
obligation and carry it forward. A scoped negative result can be accepted; an
unreproduced claim stays open. Never bulk-close PRs by number, shared topic or
presence of some imported files.

Before publishing, recheck PR heads, validate source and evidence files against
the Git index (including ignored log files), run affected integration checks,
and preserve the prior selected-result checkpoint if the frontier changes.
After publishing, verify remote main and actual PR resolutions. Keep Linux CI
status distinct from local execution. Do not erase historical partial-review
records when a later batch finishes them.

## Cadence

Maintain a small active review set within the frozen inventory. Start with
receipt/checker correctness, then expensive replay scheduling, then construction
claims and their independent audits. Track completed reviews, integrations,
closures and carry-forwards separately. This improves throughput without
confusing a larger nominated batch with a larger verified result.
