# Maintainer queue intake: review changes, not the backlog

This is the default for authorized PR maintenance, including after compaction or
handoff. It takes precedence over historical batch recipes and generated generic
priority lists. It changes scheduling, not the standard of scientific evidence.
The review ledger remains authoritative for acceptance and attribution;
[pr-intake-state.json](pr-intake-state.json) is only a persistent scheduling cache.

## Start here every session

```sh
python3 scripts/pr_intake.py plan --refresh --output /tmp/pr-intake-plan.json
```

This fetches canonical main, reads open PR metadata once, compares exact heads and
watched source/dependency identities, and selects at most 100 actionable entries.
It never reads full PR bodies, executes contribution code, merges, closes, posts,
or changes the cache. Use the canonical integration checkout; preserve unrelated
user work. `--live-json` supports offline diagnostics but is explicitly not fresh
GitHub evidence. Recheck the live head before publication or closure.

Before reviewing a PR that modifies existing files, run
`python3 -B scripts/check_pinned_edits.py --base main --head <PR head>`. It lists
every file whose old bytes another file pins by SHA-256 and exits 1 when a frozen
`research/` or `upstream/` file is changed in place while still pinned. It is a
static byte check of one diff: it executes no contribution code and replays nothing.

If the fresh plan has zero actionable entries, stop routine intake and report
the remaining revision/deferred counts. Do not fill an empty batch with dormant
reviews or poll indefinitely unless the user explicitly requested monitoring.

Read the summary and **selected** entries first, not the entire ledger. Within
the selected chunk, handle ready integrations together, group shared dependencies,
and review each changed mechanism once. New/changed heads receive priority over
unfinished older review; pending review stays visible until explicitly resolved
or deferred. A changed head invalidates reuse, but does not require rerunning
unchanged scientific inputs whose exact coverage remains valid.

## What wakes an old entry

- A different PR head.
- A changed or removed watched main file/directory or review evidence blob,
  including executable-bit and regular-file/symlink changes with identical bytes.
- A watched PR head change or its departure from the open queue (not proof it merged).
- A scheduling policy-version change.
- `--wake PR_NUMBER` after new relevant external evidence or explicit direction.

The planner does not read Discussion/comment bodies. A revision supplied only in
comments must be explicitly woken. Watch actual scientific dependencies as well as
shared production paths when they can resolve a hold. The whole main commit,
queue length, passage of time, unrelated CI activity and compaction are **not**
reasons to repeat a review. Increment `POLICY_VERSION` only when existing cached
scheduling decisions genuinely require reconsideration.

New records retain both object IDs (`watch_paths`) and Git modes (`watch_modes`).
For older records, the planner recovers missing file modes from their recorded
`baseline` in memory, grouping only the required paths into one read per baseline.
It does not rewrite the cache or wake entries just because the record format is
older. Closed/draft PRs, pending reviews, and entries already woken by another
known change or `--wake` need no historical mode lookup. Otherwise, if required
history is unavailable, planning reports an error instead of preserving an
unchanged hold or ready-to-integrate decision;
make that recorded history available or review the dependency and refresh its
record with `record`.
If the baseline is available but its file object differs from the cached object
(or is absent), the planner reactivates only that entry with an explicit
baseline-mismatch reason. It cannot safely recover the reviewed file's mode from
that baseline, and leaves the persistent record for the reviewer to refresh.

## Persist each changed decision once

Use `record` after reviewing the exact head; it checks the live head by default:

```sh
python3 scripts/pr_intake.py record --number 123 --head FULL_REVIEWED_SHA \
  --status waiting_revision --reason 'Concrete failure and required repair' \
  --evidence docs/research/EXISTING-REVIEW.json \
  --watch-path scripts/RELEVANT_SOURCE.py --watch-pr 122
```

Use real existing evidence and paths at the selected base; omit irrelevant watch
arguments. Commit the updated cache with the actual review/integration evidence.
Do not repeatedly record unchanged entries. `record` does not update the ledger,
authorize a merge, or certify tests. Status meanings:

| Status | Next action |
| --- | --- |
| `ready_to_integrate` | Finish explicit acceptance gates, source retention, attribution and publication. |
| `pending_review` | Unfinished substantive work; remains actionable. |
| `waiting_revision` | Concrete correctness/integrity or migration repair needed; dormant until woken. |
| `deferred_replay` | Explicitly scheduled separately or resource-stopped execution; dormant, obligations remain open. |

A generic “not yet reviewed” is not a revision request. Do not mark pending work
as blocked merely to shrink the queue. Leaving the open queue does not certify
incorporation; reconcile actual GitHub state and retained sources separately.

## Time and inference budget

- Reconcile the **whole queue cheaply**, then work in chunks of **up to 100 actual
  decisions**. Never pad a chunk by rereading dormant PRs.
- Carry forward unchanged review evidence by reference. Record only new decisions
  and receipts. Do not create another 100-entry audit directory, copy old source
  packets, or rewrite old reports for an unchanged batch.
- Bulk archive eligible isolated research after source/integrity intake, preserving
  authors and explicit unverified scientific obligations. Shared tooling and known
  correctness failures cannot enter through the archive lane.
  For each newly added or changed top-level `research/*/VERIFY.json`, check
  that every declared input is an exact repository-relative Git path at the
  reviewed source head. Even a standalone receipt using this filename enters
  the shared planner. An invalid path can break unrelated PR planning (#5555);
  syntax and historical source-pin checks alone do not catch it. This is a
  metadata check, not permission to launch every registered scientific replay.
- Group related construction chains; review the strongest relevant descendant and
  each unique delta, retaining predecessor credit. This is not automatic approval
  or closure of ancestors.
- Before publishing a merge with contribution heads as parents, compare their
  ancestry against all other open PR heads. GitHub can mark an ancestor PR merged
  even when its files are not installed in the default tree. Resolve and record
  each such predecessor explicitly, including whether a checked successor
  supersedes a held version; do not silently close an unrelated or unresolved hold.
- Run relevant checks once per changed source/dependency/environment obligation.
  Reuse exact-source receipts with explicit coverage; keep expensive frontier
  verification separate from archive intake.
- No automatic Lean, Docker, all-history suites, or parallel heavy jobs. Current
  local replay limits remain serial, sampled 1 GiB descendant memory, and explicit
  timeouts. A resource stop stays deferred until the execution plan changes.
- Historical blanket sweeps are manual-only (five workflows changed on 2026-10-16).
  They share `research-archive-replay` concurrency and one matrix leg at a time.
  Dispatch one workflow deliberately: GitHub keeps one running and one pending,
  and a newer pending run can replace the older one. This is not a FIFO queue.
  Automatic affected-package CI remains enabled; a shared runner change may still
  select all packages and requires a separately budgeted replay decision.
- For hosted CI, record run ID and source SHA. Poll that same run; a transient
  observation failure is not permission to restart it. Do useful independent work
  while it runs. Scope workflow triggers to avoid unrelated automatic workloads.
- Summaries report **new integrations, new holds, pending actionable work and
  separately deferred replays**. Reconciled entry count is not completed reviews.

## Handoff and completion

Keep the current scheduling cache, exact-head ledger and a short checkpoint with
any live run IDs, integration branches and next commands. A new session should
resume that checkpoint, not reconstruct all earlier batches. The initial durable
checkpoint is [pr-intake-checkpoint.json](pr-intake-checkpoint.json).

“All caught up” requires a fresh queue read, all actionable work resolved and
all remaining revision/deferred obligations accurately reported. It does not mean
all PRs have been scientifically verified. If the user's goal requires outstanding
replays, keep that goal incomplete until they are actually resolved.

Test scheduling changes with `python3 -B tests/test_pr_intake.py`; this is a cheap
metadata test and intentionally launches no contribution workloads.

## View construction clusters without rereviewing the queue

Use the plan already fetched for this session. The grouping tool makes no
network requests, runs no contribution code, and changes no intake decisions:

```sh
python3 scripts/pr_queue_groups.py --plan /tmp/pr-intake-plan.json --output /tmp/pr-groups.json
# Narrow a pilot, or reuse the existing body-search cache for author metadata.
python3 scripts/pr_queue_groups.py --plan /tmp/pr-intake-plan.json --number 2993 \
  --overlap-cache /tmp/overlap.json --output /tmp/pr-groups.json
```

The output preserves intake lanes, exact heads, review evidence, dependencies
and declared remaining obligations. `construction_groups` use an exact declared
word SHA-256 **and** the full cost model. Related audits can instead declare a
`construction_ref` with the source PR `number` and exact `head`; these groups are
explicitly labelled source-reference groups, not byte-verified word equivalence.
When neither identity exists, entries stay separate. `profile_role` distinguishes
a candidate's own profile from an audited construction reference: an audit PR
must not be presented as a new κ claim.
`profile_clusters` share calculations across equal profiles, but never certify
circuit equivalence. Do not merge/close a PR just because its histogram or
ceiling matches another. Different profiles/coverage laws cannot reuse the same
ceiling without a new calculation.

The default [profile inventory](construction-profiles.json) is a small seed,
**not a full queue census**. Metadata applies only to its exact PR head;
changed heads, missing profiles and conflicting declarations remain unclassified.
The selected profile is a pinned reference, not a claim about every successor.
A triage contributor can extract one actionable cluster into this inventory or
attach its data to the existing review. Avoid a new survey PR per session.
Maintainer review remains separate from donor metadata extraction.

A PR author may include this optional fenced JSON in the PR body, which the
existing overlap cache can supply to the grouping tool:

```json
{
  "schema": "integer-mult-construction/v1",
  "word_sha256": null,
  "dependencies": [2942, 2957],
  "remaining_obligations": ["Independent circuit/frame admission review"],
  "profile": {
    "model": "one-unpaid-coordinate-halving-v1",
    "m": 73,
    "families": 896,
    "stages": 9,
    "centre": 64,
    "idle_rank_cap": 51,
    "local_profile_per_call": {"1": 2445, "2": 706, "3": 232, "4": 108, "5": 18, "8": 8}
  }
}
```

`word_sha256` must identify the complete canonical word relevant to the claim,
including frame/schedule data; provide its artifact and hashing convention in
the prose. Leave it null if that identity is unavailable. A generator filename,
PR title, or profile hash is not a word hash. Author declarations remain
unreviewed even if the ceiling arithmetic succeeds. The body cache binds the
metadata to the observed PR head, not to a verified scientific artifact.

The queue tool calls the retained, trusted
[ceiling implementation](../../research/complex-local-word-ceiling/ceiling.py)
once per distinct supplied profile, at most 20 by default (`--max-profiles`,
maximum 100). It implements only the stated one-unpaid-coordinate coverage,
halving guard, and outer transfer. Out-of-model inputs, numerical bracket
failures and missing data remain explicit; they do not reject a new mechanism.
Pricing is bounded to widths 2–128 and finite rational metadata. Larger models
need a separately scoped calculation. A ceiling is an optimistic upper bound,
not an attainable packing or an admitted κ.

Each local count uses at most 60 characters, with a decimal exponent between
-60 and 60 when scientific notation is used. The exponent is checked before
expanding the rational. Its reduced numerator and denominator must each have
magnitude at most `10^60`, and its value must lie between 0 and `10^9`.
Ordinary integer, fraction, decimal and bounded scientific spellings remain
supported. An over-budget profile is reported as `unknown_or_outside_model`;
other profiles in the same queue remain eligible for calculation.
