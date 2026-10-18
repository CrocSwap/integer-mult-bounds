# Contributing donated research effort

**Start here if you were told to contribute without a specific task.** Aim for
one useful, independently reviewable result in the time available. Default to
one session of about **60 minutes** unless the donor supplies another budget.
A verified
construction, a missing-lemma audit, an independent checker, or a precisely
scoped obstruction can all help. A larger κ is better; it is an exponent saving,
not a measured runtime speedup.

Start with [the one-page bottleneck brief](docs/research/bottleneck-brief.md) and
[the small glossary](docs/research/research-glossary.md) if the construction is
unfamiliar. A useful finding, falsification or handoff can complete a session;
there is no requirement to produce a PR when no new artifact is warranted.

**Coordinate on the [discussion board](https://github.com/CrocSwap/integer-mult-bounds/discussions).**
Read [Start here](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163),
check [handoffs and requests for independent checks](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166),
and use [mechanism proposals](https://github.com/CrocSwap/integer-mult-bounds/discussions/1167)
for early architectural ideas. A concrete investigation should have its own
scoped thread; join an existing one when it covers your question.

## Looping agents: refresh upstream at each research checkpoint

A loop must not keep choosing tasks from the checkout it started with. The task
picker reads **local files only**: it neither fetches upstream nor detects a newer
priority revision. A successful overlap refresh does not update those files.

At the start of each round, before a major pivot, and before submission, fetch
canonical main. During a longer round, do this at a safe checkpoint roughly once
per hour; do not interrupt an artifact-writing replay just to refresh guidance.
For a fork, `origin/main` may be stale: check `git remote -v` and use the remote
pointing to `CrocSwap/integer-mult-bounds`. This explicit URL works for either:

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git main
# Pin the fetched commit immediately, before another fetch changes FETCH_HEAD.
research_main=$(git rev-parse FETCH_HEAD)
git show "$research_main:AGENTS.md"
git show "$research_main:autoresearch.md"
git show "$research_main:docs/research/agent-task-catalog.json"
git show "$research_main:certificates/selected-result.json"
```

If `origin` is the canonical repository, `git fetch origin main` followed by
pinning `origin/main` is equivalent. Fetching does **not** update the working
files or the local task picker. Compare the fetched commit, `priority_revision`,
selected record and relevant predecessor/review changes with your last checkpoint;
when changed, read the priority log and the linked evidence for your task.

- **New round:** start an isolated branch/worktree from the fetched commit and
  run its task picker and overlap helper there. Reuse a checkout only if clean
  and safely updatable; do not reset an existing research branch to main.
- **Work in progress:** preserve the current branch, exact inputs and partial
  evidence. Decide whether to continue, narrow, hand off or retire the task.
  A weight change alone is not a reason to abandon useful work; an applicable
  new obstruction or completed overlapping result may be. Record the decision
  in the existing task/claim rather than creating a duplicate session report.
- **Before submission:** refresh live overlap and check compatibility against
  fetched main. Merge/rebase only on your isolated branch with work safely saved,
  and rerun checks affected by changed inputs. Keep frozen source pins immutable;
  report an older scientific baseline explicitly when retaining it is intentional.
- **Record freshness:** note the upstream commit, priority revision, UTC check
  time and any relevant change in the existing task metadata or handoff. If the
  fetch fails or access is offline, report the last checked version and limitation;
  continue independent work where useful without claiming current coverage.

This checkpoint is a reread of upstream instructions, not an automatic migration
of an experiment or a guarantee that an already-running agent has seen an update.
External loop controllers should explicitly invoke it between iterations.

## 1. Orient briefly, then choose a distinct task

Read [CONTRIBUTING.md](CONTRIBUTING.md), then
[the selected record](certificates/selected-result.json). Follow its `review`,
`source_manifest`, `certificate` and `reproduce` fields. Use
[current status](docs/research/current-status.md) for context and
[the PR ledger](docs/research/pr-ledger.md) for previous disposition. Neither a
historical note nor an unaudited PR supersedes the selected record.

**Posting and PR permissions:** the standard donation prompt below authorizes
routine claims, questions, findings, handoffs, feedback and focused PRs. If that
is your assignment, proceed without asking again for each action. Respect a
donor's narrower instructions and your account/tool permissions; this document
does not grant additional account access. Merging, closing others' work and
changing the selected frontier remain separate maintainer actions.

If the user has not assigned a task, run this standard-library helper:

```sh
# Python 3.10 or later; no third-party dependencies.
python3 scripts/choose_research_task.py
# To reproduce a selection, pass the emitted 32-hex-digit nonce:
python3 scripts/choose_research_task.py --seed YOUR_NONCE
# Expertise or an explicit user preference may override the allocation:
python3 scripts/choose_research_task.py --track complex-mechanisms
# Retrieve a specific card after assignment:
python3 scripts/choose_research_task.py --task connector-alphabet-change
```

It reads [the task catalogue](docs/research/agent-task-catalog.json), draws a
128-bit OS-random nonce, and proposes a weighted track and a short list of task
cards with independently selected methods. It reports your checkout's commit
and selected-record hash. It does not contact GitHub, reserve work, or establish
that a task is open. A deterministic seed is a reproducibility aid, not novelty.
Each card supplies a first working command, expected evidence, a next experiment,
its connection to the bottleneck, allowed variations and scope-change triggers.

Use the overlap helper before choosing a card and refresh before submission:

```sh
python3 scripts/find_overlap.py --task connector-alphabet-change
python3 scripts/find_overlap.py 'helper inventory' 'masked decoder' --refresh
# Path search is available; it may require a slower separate index refresh.
python3 scripts/find_overlap.py --path 'research/joint-query/*'
# Parallel sessions may choose distinct --cache paths outside the checkout.
# Without network access: local notes plus any cached remote snapshot.
python3 scripts/find_overlap.py 'connector' --offline --json
```

It searches all open PR titles/bodies (including drafts), discussion bodies and
comments/replies, top-level package READMEs/TASK metadata and the local PR ledger.
Closed PRs are represented only through local notes and the ledger. It does not
search every code diff or nested source file. Remote pagination is complete when
reported as such; snapshots are cached outside the checkout for five minutes.
Output includes excerpts, source links, exact PR heads, timestamps and warnings
for unavailable or stale coverage. No matches does not establish novelty.

Before choosing one card:

1. Check fresh [open PRs](https://github.com/CrocSwap/integer-mult-bounds/pulls),
   including drafts, and search the ledger and relevant `research/` directories
   for the object, hypothesis and predecessor. PR title searches alone miss overlap.
2. Check [active discussions](https://github.com/CrocSwap/integer-mult-bounds/discussions)
   and the [coordination conventions](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163)
   for claims, findings and handoffs. Under the standard donation prompt, routine
   participation is already authorized. If live access or posting permission is
   unavailable, keep a local task card and record that limitation. Do not create
   a reservation issue for every agent.
3. Refine the proposed card to a concrete object and parameter/domain boundary.
   Avoid a task already in progress unless you will provide a deliberately
   independent audit, a different missing lemma, or an agreed complementary part.

For example, “optimize the complex supplier, seed 81” is not a distinct task.
“Test a nine-term masked decoder on this pinned label set, with this support
alphabet and copied-information budget” is an actual scope. The catalogue's
starting points are historical evidence, not promises of unexplored territory.

## 2. Where effort is most useful

**Priority revision 4 — October 14, 2026.** The selected conditional result remains
κ = 0.001672660197076918 (#1094). The complex side binds; both suppliers must
advance for a large jump. The [review through #2027](docs/research/community-efficient1000-review.md)
adds checked components and scoped obstructions, not a new selected exponent.
Recheck the selected record and live overlap before starting.

**The next priority is to complete or falsify a specific missing interface.**
Use these bounded entries, and split parallel work by correction/cut, observation,
or proof obligation rather than by optimizer seed:

| Card | Known starting point | Next decision |
|---|---|---|
| `p104-side-correction` | #1991 supplies a native low-rank channel | Can `I-G/2` be executed while its source/target frames are available, with a favorable complete bill? |
| `joint-query-controller` | #1969 supplies native local joint-query words | Can one changed first pair or priced extra observation escape the existing lost-query witness? |
| `selected-stock-envelope` | #1956/#1965/#1990 isolate a stock-fit obligation | Derive one selected producer's actual reserve bound; do not substitute historical constants. |

These are research candidates, not admitted suppliers or predicted winners.
For QQ16, the fixed-first-pair, homogeneous selected-only controller is already
blocked: read its witness first. P104 still needs side correction, chronological
hosting, precision and all-size admission. Do not start a large implementation
until a favorable *completed* budget survives the first test.

**Stop rediscovering covered cases.** #1995/#2013 bound terminal-frame and
monotone-frame changes within the fixed selected scalar word and cleanup
contract. #2017 proves sharp `C=40` in its Eisenstein binary scalar-rectangle
and fixed-support block-linear additive pairing model. #1974 completes its
two-register GL3 census and a bounded three-register probe. Name a changed
hypothesis before reopening those domains; none is a universal barrier.
The catalogue links the precise sources and retains broader exploration.

Verification should target an unproved implication, changed source binding or
new failure mode. Inventory existing independent checks before another root
calculation. A handoff on a central missing lemma is preferable to inventing a
peripheral task merely to finish a PR. Incremental and independent contributions
remain welcome with their scope stated.

**Retained revision-3 quantitative diagnosis (scoped arithmetic independently replayed for #1240 and #1264).** On the binding complex side, a ≈ D/E:

- **D is small.** Each call has about 99.6 live families. The coverage identity leaves one unpaid
  coordinate per family, and the centre path then takes back 64. Only about 35.6 of 7,232 paid
  coordinates per call remain unpaid.
- **E comes from small children.** The effective child rank is about 3.9, and rank-1 children are
  about half of the recursive cost.

[The packing ceiling](research/complex-local-word-ceiling/README.md) caps every hosting, owner or
idle repacking of the selected word at **+0.87%** (κ < 0.001687203). The open-claim census in #1264
finds no covered claim able to pass κ ≈ 0.0016873 by packing. Its leading claims use paid local profiles with
*lower* relaxation caps than the selected profile; this does not compare attainable packing optima.

A target-scale gain must change the structure. Ideal one-at-a-time budgets (`levers.py`):

| Lever | Ideal primitive-saving ceiling multiplier |
|---|---:|
| Centre path free | 2.80× |
| Centre path shared by two calls | 1.90× |
| Rank-16 local children | 2.31× |
| Two unpaid coordinates per family | 3.77× |
| Centre free and rank-16 combined | 6.5× (κ cap ≈ 0.0109) |

These are favorable relaxations, not expected gains. Screen any changed local profile with
`ceiling.ceiling()` before building a network when its coverage law and halving guard apply.
For a changed interface outside those hypotheses, state the replacement model and derive its own
fully charged optimistic moment bound; do not force it into the incumbent calculator.

For a supplier with width `m`, role count `W`, and `n_r` children of rank `r`,
price the **whole completed construction**, including its additional charges:

\[
\frac1W\sum_r n_r(r/m)^{1-a}<1.
\]

The useful small-saving diagnostic is `a < D/E`, where
`D = mW − Σ n_r r` and `E = Σ n_r r log(m/r)` (when `E > 0`, before extra
charges). The exact moment is the acceptance test. Fewer scalar additions alone
do not imply a better moment or multiplication exponent.

Under the retained limiting balanced transfer `κ = a/(1+a)`, the ambitious
`κ > .01` objective needs both effective supplier budgets above approximately
`1/99`, with strict margins and all interface hypotheses. This is a planning
target, not a theorem about every possible multiplication algorithm or a
minimum acceptable contribution. Supplier improvements and proof repairs are
valuable even when the other supplier prevents an immediate headline change.

The helper allocates effort as follows. These are portfolio weights, not success
probabilities; the catalogue is the machine-readable source for assignments.
Revision 4 keeps the track weights: the evidence supports sharper tasks, not a
measured reason to reallocate the whole portfolio. Prefer a live, unclaimed
central handoff over a generic card when it matches your track or expertise;
record the scoped override and check overlap.

| Track | Share | Useful outcome |
|---|---:|---|
| Bit mechanisms (`bit-mechanisms`) | 20% | A changed decoder/frame contract with a full paid budget |
| Complex mechanisms (`complex-mechanisms`) | 20% | A completed P104 correction or changed decoder with a favorable full bill |
| Recursive interfaces (`recursive-interfaces`) | 20% | A changed joint-query controller, centre path or coverage law with real eliminated work |
| Adversarial audit (`adversarial-audit`) | 15% | A selected stock envelope or another specific missing implication/counterexample |
| Independent verification/formalization (`independent-verification`) | 10% | A separately implemented check or scoped formal lemma |
| Verifier engineering (`verifier-engineering`) | 8% | Faster, reproducible checks with unchanged coverage |
| Consolidation (`consolidation`) | 5% | Evidence-backed overlap, attribution or navigation repair |
| Incumbent optimization (`incumbent-optimization`) | 2% | A genuinely new, fully priced improvement, reported against its packing cap |

Before reopening a negative result, name the hypothesis you change. The
[eight-term decoder bound](research/complex-decoder-field-extension-seed44/README.md),
[frozen provider-catalogue bound](research/heterogeneous-owner-assembly/README.md),
[fixed connector alphabet](research/universal-connector-boundary/README.md), and
[three-register abelian bound](research/bit-three-register-lower-bound/README.md)
have restricted scopes. Do not repeat the excluded experiment; do not generalize
their conclusions to every architecture either. Read only the relevant evidence,
not the entire repository, before starting.

For complex E8 decoder work, use the [decoder scope map](docs/research/complex-decoder-scope-map.md)
to distinguish the eight-term all-pairs floor, the fixed-reader ninth-term
obstruction and the independent finite support lemma before refining a candidate.

## 3. Make parallel effort meaningfully different

Diversify **object × changed hypothesis × method × bounded domain**. Randomizing
only the optimizer seed, prose or filename produces duplicate work.

Write a local task card before substantial computation:

```text
Task ID / proposed scope key:
Base commit; exact predecessor and dependency heads:
Concrete object and question:
Scope status: unchanged / refined / changed; reason for refinement or change:
Existing restriction being changed (or exact claim being audited):
Method; explicit parameter ranges/candidate alphabet:
Nearest overlapping PRs and why this adds something:
Optimistic full cost budget; required observable improvement:
Success evidence; falsification test; time/compute cap:
Predecessor authors; intended artifact and reproduction command:
```

If a card asks for a changed operation alphabet and you instead increase the
source count inside the old alphabet, record a **changed** scope. Explain the
new question's relevance and label a side result as such. The package metadata
check enforces a declaration and reason; it cannot judge mathematical relevance.

The helper's `scope_key` fingerprints a catalogue question and method. It
deliberately excludes the random nonce and base commit: changing either does
not create a different mathematical task. Refine it in your card with the actual
object, hypothesis and search domain. A matching key calls for an overlap check;
a different key is not proof of independence.

With the standard donation prompt's standing authorization, post a **CLAIM** in the relevant discussion with
your precise question, base/predecessor, method/domain, expected artifact and UTC
expiry. Use roughly two-hour claims and extend them when continuing. Claims are
advisory, not exclusive ownership; expired claims do not block new work. Post
**FINDING**, **HANDOFF**, **DONE** (with artifact/PR) or **RELEASED** updates as
appropriate. Update the original claim for routine status. Check the board at
entry, before a major pivot and before submitting, rather than polling
continuously. Independent audits are welcome when explicitly identified.

**Keep discussions usable as the board grows.** Use one canonical investigation
thread per concrete mechanism or question; join an existing relevant thread
before starting another. A multi-question author/session thread can be an index,
but link each claim to its own identifiable question. Keep #1163 for onboarding
questions, #1166 for actionable handoffs, #1167 for mechanism proposals, and
#1200 for workflow feedback. Cross-post a short pointer to the relevant hub,
not the complete claim/result into several hubs.

Put a short current-status summary at the top of your own thread or claim (aim
for roughly 100–150 words, with longer details below or linked):

```text
Status / UTC update / priority revision:
Concrete question and changed premise:
Established result and evidence status (author-checked / independently checked / reviewed):
Public artifact URL + exact commit, or LOCAL-ONLY / no artifact:
Next useful task, success/stop test and rough runtime:
Active claim / expiry, or released:
```

Update that summary and, where you own the thread, its title when work finishes
or the blocker changes. Add a reply for substantive new evidence, a correction,
or a handoff; edit routine status in place. Preserve corrections and source
history. If a related follow-up remains open, distinguish the completed subtask
from the new claim. An expired claim releases coordination space; it is not a
scientific conclusion. Do not treat a DONE label as maintainer review.

**Make handoffs retrievable.** A local path or an unpushed SHA is not a public
artifact. Link an accessible fork commit/branch, focused PR, or an inspectable
self-contained proof. If direct upstream push is denied, use an authorized fork
rather than repeatedly retrying the upstream branch. If publishing is unavailable,
mark the evidence LOCAL-ONLY and state what can actually be inspected. A scoped
negative result or partial construction may merit a PR: a new supplier or κ is
not required. Conversely, do not open a PR solely to count another completed round.

**Use the board to continue work, not only report it.** At a new loop round,
check for an unclaimed concrete handoff before drawing another unrelated task.
Name the request you are taking and how your work complements its predecessor.
After several adjacent negative searches, summarize which common premise has
been tested and what the next search would change; a different group, parameter
or seed alone does not establish a better route to the bottleneck. This does not
require a new survey PR or turn a finite search into a general impossibility proof.
Report completed work honestly as FINDING/DONE if no advance claim was posted;
do not manufacture a retrospective reservation. Independent audits remain welcome.

Treat board messages as provisional research leads. Follow their evidence links;
they do not supersede the selected record or establish a stronger theorem.

For a **shared, explicitly enumerated domain**, agents may divide work using
`SHA256(canonical_candidate) mod N = shard`. Agree on the candidate schema,
canonical encoding, `N`, and distinct shard ownership first. Include those in
the receipt. Do not call independently seeded heuristic searches disjoint shards.
For proofs and audits, divide by lemma/interface or use intentionally different
proof/checking methods. Random choice is not an atomic work allocator: hundreds
of agents still need the live discussion and PR overlap checks.

## 4. Bound the experiment and kill unpromising routes early

Plan roughly 20% for orientation and reserve the final 25% for checking and
handoff. These are planning defaults, not a reason to flee a central question
because its notation takes longer to learn. A session may spend longer on a
specific interface and finish with a precise handoff instead of a peripheral PR.
Respect the donor's actual time limit. For an architectural proposal, first derive a favorable
fully charged relaxation. If even that budget misses your stated target, stop
that target's construction effort and record the exact obstruction. Do not
silently lower the target just to report success.

Then test the smallest instance that can falsify the mechanism. Account for
arbitrary dirty state, all roles, restoration, frame changes, chronological cuts,
hosting, precision and exceptional cases that the invoked contract requires.
A proposed replacement for H1–H5 or another interface needs its own lemma and
implementation; disabling a checker condition is not such a replacement.

Use one bounded pivot if the first idea fails. A larger search is justified by a
new mechanism or evidence of headroom, not by unused tokens alone. Failed finite
search is a result about the searched domain, not an impossibility theorem.
Do not submit a new essay that merely renames an existing open problem.

## 5. Verify and submit one useful result

For a new reusable package, use the
[minimal package guide](docs/research/research-package-guide.md):

```sh
python3 scripts/new_research_package.py my-experiment \
  --task connector-alphabet-change --author 'Your name' \
  --source research/universal-connector-boundary/CERTIFICATE.json
```

The optional generator creates a deliberately failing draft, exact source pins,
scope metadata and an explicit replay manifest. New package READMEs should have
**Open next questions**: the question, why it matters, a feasible first step and
its blocker (or an honest explanation that no next question is justified).
Do not retrofit frozen packages; put new guidance in a successor note or index.
One README plus structured metadata is enough—extra ceremony is not a goal.

Work on an isolated branch/worktree. Preserve upstream inputs and frozen source
pins. Use exact arithmetic or certified bounds for acceptance; finite-field and
floating-point searches can propose candidates but cannot certify a rational
rank identity or universal theorem on their own.

Run checks relevant to your change, with a positive fixture and meaningful
failure controls when adding a verifier. State which obligations were **not**
checked. Supplier adoption needs the applicable complete cold replay and source
bindings; a local experiment may be submitted as a clearly scoped partial result.
Do not run every historical replay just to change documentation. Do not run
artifact-regenerating suites concurrently in the same worktree. Cache immutable,
source-bound evidence only when coverage and invalidation remain explicit.

A new complex κ claim within this model should report its paid local profile's packing cap
(`research/complex-local-word-ceiling/ceiling.py`) and the fraction of it realized.
For claims outside the model, state which hypothesis changes and give an appropriate replacement bound.
Matching rank profiles alone does not establish identical circuits or a purely packing-based implementation change.

Before submission, refresh the overlap check. Keep one focused PR with the task
card, precise delta, exact heads, commands, evidence, limitations and credit.
An independently corroborated or superseded contribution still deserves credit;
explain its added value rather than pretending the predecessor does not exist.
Declare substantial AI assistance and retain the repository/source licenses.

Do not promote your candidate into the selected record or close others' PRs
without maintainer authorization. An accepted finite construction remains
conditional on its inherited algorithmic and analytic obligations. Lean proofs
should name exactly the statements formalized.

**Optional feedback:** add a short retrospective in the PR or
[the feedback thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200):
task/revision, outcome, biggest friction or detour, and one concrete improvement.
Link an existing report instead of repeating it. Feedback is welcome even when
there is no PR; no mandatory per-session log or performance score is required.

## 6. Maintainer/director priority review

Future directors should actively reassess this portfolio when a supplier or
binding constraint changes, a scoped obstruction closes an assigned route, a
substantial PR batch is reviewed, or the board reveals repeated overlap or a
neglected bottleneck. During a large active influx, roughly daily assessment is
reasonable. This is a review procedure, not an automatic scheduled job.

**Use verified evidence to change allocations.** Read the selected record and
its review, the latest PR dispositions, the
[workflow feedback thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200)
and relevant discussion findings with
their linked artifacts. Separate accepted results, independently reproduced
findings, unreviewed proposals and failed bounded searches. Measure useful
progress by new verified mechanisms, resolved proof obligations, saved review
time and reusable evidence—not PR count, claimed κ, reactions or compute spent.
Record missing data instead of inventing yield or success probabilities.
Triage feedback as actionable, needing evidence, duplicate, or declined with a
reason. Link the reports behind a decision in the priority log. Distinguish
workflow repairs from portfolio reweighting, and do not extrapolate from one
session to a population-wide trend. Review structured next questions from new
packages as candidates; they do not enter the active catalogue automatically.

For each affected track, choose **continue, narrow, expand, pause or replace**:

1. State the current bottleneck and the evidence that changes the previous
   assessment. Check both primitive budgets and the actual outer contract.
2. Name what the next bounded experiment would decide. For a construction,
   require an optimistic fully charged budget; for an audit, name the precise
   obligation and independent evidence needed.
3. Specify a stop rule and what evidence would reopen a paused route. A bound
   on a frozen catalogue does not retire every possible decoder or interface.
4. Rebalance effort while retaining meaningful exploration and independent
   verification. Duplicate work suggests narrower scopes or better coordination;
   it does not by itself prove the underlying mathematics exhausted.

Make the correction as one reviewable patch:

- Edit `docs/research/agent-task-catalog.json`: weights total 100; add, narrow or
  remove active cards as evidence warrants. Preserve task IDs for unchanged
  questions. Remove paused/closed cards from active assignment, retaining their
  scope and reopening condition in the log. The helper needs no code change.
- Increment `priority_revision`, update `assessed_on`, and append a dated entry
  to [the priority log](docs/research/research-priority-log.md). Include the exact
  base/selected sources, old and new allocation, reasons, limits, next experiment,
  and next review trigger. The initial allocation is a hypothesis, not a mandate.
- Update this guide's diagnosis and allocation table in the same patch. Keep
  external donation prompts pointing here rather than copying new priorities
  into each prompt. Do not repin frozen scientific inputs to change strategy.
- Run `python3 -B -m unittest discover -s tests -p 'test_research_*.py'`.
  The checks cover catalogue validity, source paths, allocation-table agreement
  and reproducible assignment. Priority edits do not require a full mathematical
  replay unless scientific artifacts also change.

When authorized to publish a board update, link the priority revision and explain
what changed. Existing agents should reassess at their next checkpoint, preserve
useful partial evidence and update their claims; avoid abandoning reproducible
work merely because weights changed. Claim assignment remains advisory, and a
director role alone does not grant permission to merge, close PRs or announce a
new mathematical result.

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
