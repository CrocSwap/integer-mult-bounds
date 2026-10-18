# Validation and handoff

Environment: Linux x86_64, CPython 3.12.14, standard library only.
Author-run evidence with substantial OpenAI Codex assistance; not independent
human review or formal verification. Checks were completed on 2026-10-15 UTC.

## Executed

The recommended reproduction command is:

```sh
python3 -I -B scripts/research_package.py --package research/compact-repair-partition-audit-seed66
```

**PASS.** It validates package metadata and source provenance, then executes
the normal verifier and six optimized test groups. The observed output was:

```text
PASS_COMPACT_REPAIR_PARTITION_AUDIT addresses=2396160 orbit_length=512 physical_records=4096 no_new_kappa
Ran 6 tests in 55.806s
OK
PASS_REGISTERED_RESEARCH_PACKAGE research/compact-repair-partition-audit-seed66 outcome=completed
```

The six groups cover:

1. A reversed repair shift is rejected by the actual pinned inverse-source map.
2. Two Boolean payloads give the explicit cross-cell information obstruction.
3. Canonical JSON comparison distinguishes a Boolean from the integer one.
4. An altered executable source is rejected before its injected code can run.
5. A false Git blob is rejected even with unchanged source bytes.
6. A clean, unrelated, Git-free export passes under `-I -O -B`, changes no
   files, rejects an altered cycle receipt, and refuses to overwrite it.

Normal and optimized acceptance therefore agree. The corrupted executions
fail as intended; they are successful rejection controls, not failures of
the unmodified package. The original stream fixtures reject independent
half-range repair and admit the residue-cell alternative. Tariff fixtures
exhibit overcharging/undercharging risks from fragmentation and repeated
bad-record visits, without confusing those failures with a source bug.

Additional completed checks: Python syntax for all five Python files;
metadata/source-pin validation alone; exact comparison of all five retained
files to their fetched source Git objects; and whitespace/diff review.
The original task-card baseline returned
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`; that orientation command is not a
mathematical acceptance test.

## Pins and overlap

Analysis started at main `bd1b3bc7174cddbfa4e30ac073dc134f48aa6e77`.
Before publication, main advanced to
`7cfd2fd64bff65b0f01771fede3d11b37c06c68e`; this branch was rebased there.
AGENTS.md, autoresearch.md, CONTRIBUTING.md, priority revision 5, the selected
record, family/bottleneck guidance and replay runner were unchanged. The
updated review ledger was inspected. Historical analysis/source pins remain
explicit; no upstream file is changed by this contribution.

PR2250 and PR2476 heads were refreshed and remained exactly
`d404b48a1e7b147556b309497d55089c837dddb2` and
`32e88ddfd111b93fbcfb306514397cf406e4d5d4`.
Public open-PR queries for repair/partition and repair/orbit and PR2476's
visible conversation were refreshed. No competing partition-repair claim
was visible. The broader local overlap search and Discussions 1163, 1166,
1167, 2209 and 2253 were consulted during selection. Coverage is bounded:
there was no complete remote pagination or search of every unpublished diff.

Older PR1108 already supplies the raw saturation law/order, and PR763 uses
invariant source/back-field fibres. These are explicitly credited. The new
question concerns the actual repair's target-cell boundaries and aggregate
tariff, not priority for that earlier algebra. The attempted scoped claim
on PR2476 received a GitHub integration 403. No upstream comment was posted
or retried; CLAIM.json is the local coordination record.

## Not executed or established

No repository-wide suite, selected supplier cold replay, complete PR2250
catalogue replay, Lean build, hosted CI, full GL/orthogonal-cover execution,
or physical partition-dispatch benchmark was run. No new primitive cost,
supplier admission, unconditional multiplication theorem or κ follows.

The proof covers all finite partitions in its stated no-communication
contract and the specified two-slot earlier-source family. Full records,
correct global keys and a uniform per-cell tariff remain assumptions for
the cost corollary. Cell access, metadata, gathering, merging, parking and
any cross-cell routing still need implementation and pricing.
