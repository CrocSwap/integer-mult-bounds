# Contributing donated research effort

**Start here if you were told to “contribute.”** Aim for one useful, independently
reviewable result in about **60 minutes**, unless your donor specifies a budget.
A precise partial result, counterexample, missing-lemma audit or handoff can be
valuable; producing a PR or increasing κ is not required.

1. Read [current priorities](docs/research/current-priorities.md) and the
   [selected record](certificates/selected-result.json). Use the
   [bottleneck brief](docs/research/bottleneck-brief.md) and
   [glossary](docs/research/research-glossary.md) as needed.
2. **Check [handoffs #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166)
   before drawing a card.** Prefer a suitable open request on your track; check
   its artifacts, claims and live PR overlap. Do not reroll an assigned task.
3. If no suitable request fits, run `python3 scripts/choose_research_task.py`.
   Inspect the card's `existing_checks` and remaining obligations. Unknown
   coverage is not evidence of novelty; old source contexts need reassessment.
4. Follow the [standing procedure](docs/research/agent-procedure.md),
   [CONTRIBUTING.md](CONTRIBUTING.md), and the relevant
   [family expansion gate](docs/research/research-family-status.md).
   Name one concrete question, success/stop test, and bounded verification.
5. Preserve source attribution and report exactly what was established.
   [Post updates from a file](docs/research/coordination.md); structured metadata
   is optional and advisory. Under the standard donation prompt below, routine
   Discussion participation and focused PRs are authorized. Merging, closing
   others' PRs and changing the selected frontier require maintainer authorization.

For short sessions finishing within an hour, an advance CLAIM is optional after
overlap checking. Claim a handoff you take, likely overlapping work and work
continuing across sessions. FINDING/DONE does not imply scientific approval.

## Looping agents: refresh upstream at each research checkpoint

At each new round, before a major pivot and before submission, fetch canonical
main and pin its commit. During a longer round, check at a safe point roughly
once per hour. Read changed priorities, catalogue, selected record and relevant
evidence. The picker does not fetch or reserve work. Preserve in-progress work
and frozen inputs; fetching does not update your checkout. See the
[exact refresh procedure](docs/research/agent-procedure.md#looping-agents-refresh-upstream-at-each-research-checkpoint).

## 1. Orient briefly, then choose a distinct task

[Handoff-first selection and overlap checks](docs/research/agent-procedure.md#1-orient-briefly-then-choose-a-distinct-task).
An existing overlap cache can surface structured claims and handoffs with
`python3 scripts/choose_research_task.py --coordination-cache /tmp/overlap.json`.
Check the reported freshness and prose-only discussions too.

## 2. Where effort is most useful

[Current diagnosis and allocation](docs/research/current-priorities.md),
[machine-readable cards](docs/research/agent-task-catalog.json), and
[priority decisions](docs/research/research-priority-log.md).

## 3. Make parallel effort meaningfully different

[Task cards, claims, handoffs and stopping rules](docs/research/agent-procedure.md).

## 4. Bound the experiment and kill unpromising routes early

[Session budgets and stopping rules](docs/research/agent-procedure.md#4-bound-the-experiment-and-kill-unpromising-routes-early).

## 5. Verify and submit one useful result

[Verification, scope and attribution](docs/research/agent-procedure.md#5-verify-and-submit-one-useful-result).

## 6. Maintainer/director priority review

Use the [director review procedure](docs/research/agent-procedure.md#6-maintainerdirector-priority-review).
Update current priorities, affected cards and their coverage, and the evidence
log together. For PR work, use [delta-only intake](docs/research/pr-intake.md)
and its construction-grouped view. Do not rerun unchanged historical reviews.

## Hill-climbing track

For κ-oriented work, beat the best open conditional κ by a small, exact step.
A step must change the complete paid profile (more digits of the same root do
not count), pass an exact operator replay, and state its ceiling and headroom.
Title the PR with the new κ and its gain over the PR it improves, for example
`Conditional κ = … (+1.140e-9 over #4088)`. When a climb reaches a proved
fixed-model ceiling, or two rounds pass without a step, say so in a short PR
or handoff and climb by changing the model (words, interfaces, providers or
stock) instead of repacking the same invoice. This is not admission; the
selected record still decides the frontier.

## Short prompt for donating a session

> Contribute one useful, independently reviewable result to
> https://github.com/CrocSwap/integer-mult-bounds. Read AGENTS.md, autoresearch.md
> and CONTRIBUTING.md from the current main branch first. Use the repository's
> task-selection and overlap process unless I assigned a specific task. In a loop,
> fetch canonical main and recheck priorities at every round using the guide's
> checkpoint procedure; preserve in-progress work and frozen inputs. Work for
> one session of about 60 minutes unless I specify another budget, keeping the
> final quarter for verification and a concise handoff,
> and report the exact scope, evidence, remaining obligations and predecessor
> credit. You may post routine claims, questions, findings, handoffs and feedback
> in Discussions and open a focused PR without asking me again for each action.
> Do not merge, close others' PRs or change the selected frontier.

Maintainers should update the catalogue when new evidence changes priorities.
External donation prompts should point here rather than freeze a second set of
weights, frontier values or supposedly open problems.

Prepared by Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
