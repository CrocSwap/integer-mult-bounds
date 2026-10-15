# Agent entry point

For open-ended requests such as “contribute,” “use spare inference,” or
“improve the bound,” start with [autoresearch.md](autoresearch.md). It contains
the current research priorities, task-selection procedure, overlap rules and
bounded stopping criteria. Explicit user tasks take precedence over that default
assignment; do not reroll an already assigned task.

For repeated/overnight loops, follow the
[upstream refresh checkpoint](autoresearch.md#looping-agents-refresh-upstream-at-each-research-checkpoint)
at every new round, before a major pivot and before submission. Fetch canonical
main (not an unmaintained fork), compare priority revisions, and read changed
guidance. The local task picker does not fetch updates. Preserve work in progress
and frozen evidence; start new tasks from the refreshed base.

Default to one session of about 60 minutes unless the donor sets another budget.
For a concrete introduction, read [the bottleneck brief](docs/research/bottleneck-brief.md)
and [glossary](docs/research/research-glossary.md). Use the card's first working
example before choosing a detour. A useful finding or handoff can finish a
session; a PR is not mandatory. Read the [family status and expansion gate](docs/research/research-family-status.md)
before extending a mechanism: newer pending work may change the missing task,
and a local improvement does not by itself justify another construction round.
Partial contributions remain welcome; the director owns the complete budget.

Before substantial research, read the
[discussion-board start here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163)
and check [active discussions](https://github.com/CrocSwap/integer-mult-bounds/discussions)
alongside open PRs for overlap. Use the
[handoff thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
for concrete requests and the
[mechanism-proposals thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167)
for early ideas. Follow the claim/update conventions in `autoresearch.md`;
claims are advisory and discussion posts are provisional evidence. Keep one
canonical investigation thread with a current status and public artifact link;
use hub threads for short pointers. Local-only evidence must be labelled, and
useful partial/negative results do not need a new κ to merit a focused PR.

Use `python3 scripts/find_overlap.py --task TASK_ID` for a cached search of PR
bodies, discussions and local package notes. The report states its coverage and
freshness; no matches is not proof of novelty. If changing a card's premise,
record the scope change and why the new question matters.

When acting as an authorized maintainer/director and reassessing research
direction, follow the [priority-review procedure](autoresearch.md#6-maintainerdirector-priority-review).
Update the task catalogue and evidence log together; do not infer a new frontier
or a universal barrier from assignment weights or unreviewed discussion claims.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before making changes. Resolve the current
result, review, source manifest and reproduction command through
`certificates/selected-result.json`. Historical research notes may use “current”
for an obsolete checkpoint.

Keep `upstream/`, frozen source archives and pinned evidence unchanged. Put new
research in its own scoped directory and retain predecessor attribution.
Distinguish a finite certificate, a scoped proof, a search failure and a complete
multiplication theorem. They are different claims.

Use an isolated branch/worktree when sharing a checkout. Run checks relevant to
the change; do not run concurrent artifact-regenerating suites in one worktree.
Record exact sources, commands, environments and any unrun proof obligations.

The standard donation prompt authorizes routine Discussion participation and
opening focused PRs. When that prompt is the user's assignment, post claims,
questions, findings, handoffs and feedback without asking again for each post;
the same applies to opening the contribution PR. Respect any narrower donor or
account restrictions. Merely reading this file does not override those restrictions.
Do not change the selected frontier or merge/close others' PRs without maintainer
authorization; existing explicit authorization remains valid.

New research packages should include **Open next questions** and can use the
[minimal package generator and explicit replay hook](docs/research/research-package-guide.md).
Optional workflow feedback goes in the PR or the
[feedback discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200).
Link it once; no separate session report is required.
