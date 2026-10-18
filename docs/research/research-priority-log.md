# Research priority decisions

This log records allocation decisions, not mathematical frontier changes.
The active machine-readable portfolio is [agent-task-catalog.json](agent-task-catalog.json).
Follow [the director review procedure](../../autoresearch.md#6-maintainerdirector-priority-review)
when changing it. Preserve old entries so later agents can see why a route was
prioritized, narrowed or retired.

## Revision 1 — 2026-10-13: initial diversified portfolio

**Evidence base:** `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08`, the selected #1094
record and [batch-1099 review](community-batch1099-review.md). The onboarding
portfolio was introduced in `c0e3631dc24e3c24a861f7d3d79e0608481cccec`; discussion
breadcrumbs followed in `e208d5e77a204252f92b395aae271679cc3a56f0`.

**Allocation:** bit mechanisms 20%, complex mechanisms 20%, recursive interfaces
15%, adversarial audit 15%, independent verification 10%, verifier engineering
10%, consolidation 5%, incumbent optimization 5%. This establishes the initial
repository-owned allocation; this entry does not change its weights.

**Reasoning:** local scalar improvements can leave the paid recursive profile
unchanged, and incumbent packing improvements alone have not established a
large-jump mechanism. The selected construction is complex-limited, but a large
improvement also needs the bit supplier to advance. Allocate substantial effort
to mechanisms on both sides and changed interfaces, while keeping verification
and useful incremental work represented. Existing evidence includes the
[scoped decoder bound](../../research/complex-decoder-field-extension-seed44/README.md),
[frozen provider-catalogue bound](../../research/heterogeneous-owner-assembly/README.md)
and [helper-contract gap](../../research/r439-bsection-stars-seed01/README.md).

**Limits:** weights are research judgment, not measured success probabilities.
The listed obstructions have restricted hypotheses. No universal barrier, new
supplier, or stronger κ is established by this allocation. No systematic
post-launch yield measurement is available yet.

**Next experiments:** use the catalogue cards to identify a changed premise,
price a favorable complete budget, and run a bounded falsification or construction
test. Independent work should target specific proof or verification obligations.

**Next review trigger:** a reviewed frontier/bottleneck change, a new decisive
obstruction, the next substantial PR reconciliation, or evidence of duplicate
assignments on the live board. In an active influx, review roughly daily.

## Revision 2 — 2026-10-13: reduce entry costs and expose scope changes

**Evidence base:** `1b59b624d21924f8e3537cdc1ac52d3be6eda2fe`, retaining the same
#1094 selected mathematical record. A maintainer-supplied first-agent report
described successful onboarding but costly manual overlap checks, a move toward
a self-contained side result, unclear next questions, and scope drift from
changing an alphabet to increasing its source count. The report's corresponding
PR was not independently audited in this onboarding pass. Direct inspection
confirmed the task card's alphabet-change premise and the missing workflow
helpers. This is one field report, not a measured population trend.

**Decision: actionable workflow repair; no portfolio reweighting.** Keep the
revision-1 weights. Add a concrete bottleneck brief and glossary, source-bound
first steps, causal bottleneck links, bounded next experiments, allowed
variations and scope-change triggers to every card. Make the one-hour budget a
default and the orientation fraction flexible. A substantive handoff can finish
a session without a PR.

**Implementation:** cached overlap search covers open PR titles/bodies, live
discussion messages, package notes/metadata and the ledger, reporting freshness
and limits. A minimal package generator captures exact provenance and live input
pins. Explicit metadata requires an actual scope, a reason for changes and
structured next questions; it does not certify mathematical relevance. A bounded
opt-in CI hook replaces any suggestion to execute every historical verifier.
Frozen predecessor packages remain untouched.

**Coordination:** the donation prompt explicitly authorizes routine board posts
and focused PRs once, avoiding repeated permission questions. Optional feedback
goes in a PR or [discussion #1200](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200);
director decisions belong here. A repository file cannot override a donor's
narrower restrictions or grant missing account access.

**Next experiments:** observe whether new sessions reach the card's intended
premise, whether the first command works, and whether the overlap report saves
orientation effort. Record actual scope changes, actionable central handoffs and
useful side contributions separately. Evaluate the metadata/replay hook on new
packages before extending its environment presets.

**Next review trigger:** several additional session reports, a substantive
helper failure, the next PR reconciliation, or a new mathematical bottleneck.
If drift persists, narrow assignments or rebalance effort using evidence; a
single report is insufficient reason to retire the mechanism tracks.

## Revision 3 — 2026-10-13: aim complex and interface effort at the structural levers

**Exact base and selected source record:** `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`, unchanged #1094
record (`certificates/selected-result.json`, κ 0.001672660197076918, complex side binding).

**Evidence links and verification status.** The maintainer independently replayed #1240
(`1e136b8c4a552050820334ad113628775182f08c`) and #1264
(`1be64e9ef79fe11f24f05b62b0fd7d70be0b7b4c`), including all 14 pinned census blobs.
The monotone-cost relaxation and rational enclosures were reviewed within their stated model.
This accepts scoped arithmetic and the screening argument, not any pending construction or the full
multiplication theorem. Original sources, attribution and conditional coverage-law assumptions remain explicit.

- [#1240](https://github.com/CrocSwap/integer-mult-bounds/pull/1240) (`research/complex-local-word-ceiling`):
  under PR1012's coverage identity (also open) and the halving guard, any hosting, owner or idle repacking of
  the selected local word has a < 0.001690054109089, so κ < 0.001687203 (+0.869%). At a = 1/99, the word's
  excess spend is 20.4 times the per-call budget. `levers.py` gives the one-at-a-time ideal budgets: centre
  path free 2.80×, shared by two calls 1.90×, rank-16 children 2.31×, two unpaid coordinates per family
  3.77×, centre free plus rank-16 6.51× (κ cap 0.0109).
- [#1264](https://github.com/CrocSwap/integer-mult-bounds/pull/1264): 14 of the 30 open claims above the
  selected κ (pinned by blob) use nine distinct paid local profiles. Within the stated model all have κ < 0.001687314840. The leading
  #1148 line sits on words whose caps are 0.17–0.21% *below* the selected word's, and reports a larger fraction of its own relaxation cap. A comparison of caps alone does not compare attainable optima.
  16 claims could not be screened.
- The October 13 census snapshot lists 30 nearby κ claims; similar titles do not establish duplicate
  mechanisms. [One agent's feedback](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18909265)
  reports a crowded queue and scattered supplier anatomy, and requests profile-based grouping.
  More quantitative task cards are a maintainer response to this evidence, not a demonstrated population-wide cause of duplication.

**Current bottleneck; what changed.** The binding complex budget is about D/E. D is about 35.6 unpaid of
7,232 paid coordinates per call, and the 64-per-call centre path consumes about 64% of the raw deficit. E has
an effective child rank of about 3.9. Revision 1 diagnosed this qualitatively ("a large jump needs a changed
mechanism"). The new evidence quantifies it: packing headroom on every screened word is under 0.9%, while the
structural levers are worth integer multiples. This motivates more quantitative cards; it does not establish why contributors chose particular routes.

**Track/card decisions.**

- *Complex mechanisms:* **replace** `complex-masked-decoder` with `complex-rank-shape-decoder` (larger-rank
  delivery; masked and overcomplete supports remain allowed methods). **Narrow** `complex-new-helper-inventory`
  with a ceiling screen. Weight unchanged at 20.
- *Recursive interfaces:* **expand** with `centre-path-sharing` and `coverage-law-change`. Keep
  `persistent-boundary` and `connector-alphabet-change`. Weight 15 → 20.
- *Incumbent optimization:* **narrow**. Claims must report their packing cap and realized fraction. Weight 5 → 2.
- *Verifier engineering:* **continue** at reduced weight, 10 → 8.
- Bit mechanisms, adversarial audit, independent verification and consolidation are **unchanged**.
- `autoresearch.md` asks claims within this model to report their packing cap; claims outside it must identify the changed hypothesis and a replacement bound.

**Old allocation → new allocation:**

| Track | Old | New |
|---|---:|---:|
| Bit mechanisms | 20 | 20 |
| Complex mechanisms | 20 | 20 |
| Recursive interfaces | 15 | 20 |
| Adversarial audit | 15 | 15 |
| Independent verification | 10 | 10 |
| Verifier engineering | 10 | 8 |
| Consolidation | 5 | 5 |
| Incumbent optimization | 5 | 2 |

**Paused scope and evidence that would reopen it.**

- No track is paused. `complex-masked-decoder` is retired as a separate card, and its methods continue
  under the rank-shape card. Reopen it if a masked decoder is found to help through a route other than child
  rank (for example, deficit).
- Incumbent optimization returns to 5 or more if #1240 or #1264 fails review, or if a reviewed word is found
  whose cap is well above its realized packing.

**Next bounded experiments and stop rules.**

- *Centre path:* a fully charged relaxation of sharing one centre path across two calls. Stop the card if the
  ideal (1.90×) shrinks below a 10% gain once restoration and hosting are charged.
- *Rank shape:* one exact small identity with block frame climbs, screened with `ceiling.ceiling()`. Stop a
  candidate whose ideal ceiling does not beat the selected word's by 5%.
- *Coverage law:* explain the source of the single unpaid coordinate per family. Stop if it is forced by the
  data endpoint contract, and record that as an obstruction.

**Uncertainties and useful work preserved.**

- The lever multipliers are one-at-a-time favorable relaxations. They omit the cost of realizing each lever.
- The ceiling assumes PR1012's coverage law and the stated template/guard. The checked profiles satisfy that identity, but this review does not establish it for changed interfaces or complete the separate PR1012 review.
- Equal paid profiles do not establish equal circuits. Upper bounds on different profiles do not order attainable optima.
- The task-card thresholds are research allocation choices; the ideal multipliers are not success probabilities.
- If review finds an error in #1240 or #1264, revert to the revision-2 cards.
- The bit side is unchanged and must advance too before κ > .01. Its levers are not quantified in this revision.
- Packing results remain valuable as realizability evidence. They are now labelled relative to their cap.

**Next review trigger:**

- a correction to #1240/#1264, completion of the separate PR1012 review, or a materially different paid profile;
- the first fully charged centre-path or rank-shape result, positive or negative;
- or several sessions on the new cards.

Until then, review roughly daily during the influx.

## Revision 4 — 2026-10-14: finish concrete interfaces and retire covered searches

**Exact base and selected record:** `e112d71c8d7bb32435debcc54df932593dd8223a`.
The selected #1094 record is unchanged: κ = 0.001672660197076918;
SHA256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
The complex side still binds. This is a priority update, not a new supplier
admission or a mathematical replay of the selected theorem.

**Evidence and its status.** The [review through #2027](community-efficient1000-review.md)
and [exact-head dispositions](../../research/community-efficient1000-audit/DISPOSITIONS.json)
record the independent execution, written-proof review and remaining limits.
This pass inspected those reviews and the packages below; it did not rerun their
mathematics. Original attribution and frozen inputs remain intact.

- Chafik Boukhalfa's [#1991 native P104 channel](../../research/p104-native-channel/README.md),
  on Rohan Arun's #1972 and Adam Gall's schedule plus the credited geometry/compiler
  lineage, supplies concrete native recipes and local arbitrary-dirty restoration.
  The `I-G/2` correction, global hosting and all-size/precision admission remain open.
- Ali Romman's [#1969 joint-query package](../../research/joint-query/README.md)
  supplies ordered and native local words. Its retained fixed-first-pair observation
  witness blocks homogeneous selected-only controller repairs under the stated
  ordinary schedule. Global closure is **not** established by the local inverse.
- Gareth Davidson's [#1995/#2013 fixed-word bounds](../../research/selected-k8-unrestricted-ends/README.md)
  include arbitrary helper terminal subspaces with monotone internal paths, fixed
  entrances, scalar order and cleanup. Their favorable ceiling still misses the
  declared 5% target; they do not exclude changed words or nonmonotone transport.
- Jose Manuel's [#2017 Eisenstein theorem](../../research/eisenstein-reduction-copy-floor/README.md)
  proves sharp C=40 in the scalar-rectangle and fixed-support block-linear additive
  pairing models. It preserves predecessor credit and leaves nonlinear encoders,
  changed geometries and shared physical pricing outside scope.
- Josie Elliston's [#1974 register census](../../research/bit-gl3-mixed-targets-length10/README.md)
  received a full two-register replay and the bounded three-register probe. Gareth
  Davidson's #2027 supplies a uniform mixed-root tariff, not a native supplier.
- Josie Elliston's #1956/#1965 and ToikY's
  [#1990 stock audit](../../research/selected-bootstrap-stock-audit/README.md)
  distinguish carried time constants, sufficient stock guards and the still
  uncomputed selected reserve coefficient. They do not refute the asymptotic bound
  or establish a full outer-proof repair by arithmetic alone.

**Feedback and live overlap.** Read the latest discussion findings and
[workflow feedback](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18930476)
(Aaron Wang's report across about 35 sessions), together with the
[earlier four-round report](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18909265).
Both identify concrete handoffs as useful; the earlier report describes saturation
of selected-root arithmetic. These are contributor reports, not a controlled
population yield measurement. Action here: allow explicit central handoff overrides
and require existing-check inventories before another independent root calculation.
Reported Windows, cache, posting-helper and resolved-review navigation issues need
separate exact-version triage; no workflow fix is claimed in this priority patch.
The board also contains newer connector and native-source-rank claims (#2056/#2048).
Those are overlap leads, not accepted scientific evidence in this revision. Live
claims still take precedence over treating any catalogue task as unoccupied.

**Decisions and allocation.** Keep every track weight from revision 3:

| Track | Old | New |
|---|---:|---:|
| Bit mechanisms | 20 | 20 |
| Complex mechanisms | 20 | 20 |
| Recursive interfaces | 20 | 20 |
| Adversarial audit | 15 | 15 |
| Independent verification | 10 | 10 |
| Verifier engineering | 8 | 8 |
| Consolidation | 5 | 5 |
| Incumbent optimization | 2 | 2 |

The evidence warrants narrower assignments, not a measured portfolio reweighting.

- **Expand** complex mechanisms with `p104-side-correction`: finish or falsify one
  missing correction/cut, then price the complete bill. **Narrow** the existing
  rank-shape/helper cards using the fixed-word and applicable Eisenstein bounds.
- **Replace** the generic `persistent-boundary` active card with
  `joint-query-controller`, preserving the broader boundary opportunity in the
  other interface cards. The old card is archived in revision-3 Git history.
  Reopen it separately when a concrete non-QQ16 pair and a favorable eliminated-work
  budget are available; the idea is not mathematically ruled out.
- **Expand** adversarial audit with `selected-stock-envelope`, starting at one
  actual selected stage. **Narrow** `independent-moment` to genuinely missing
  coverage or changed inputs, not more digits of a previously checked root.
- **Narrow** register exploration against the #1974/#2027 scopes. Keep larger or
  different models active only with an explicit changed premise and native pricing.
- **Continue** the remaining cards and weights. No frozen package, selected
  certificate or attribution is edited.

**Paused domains and reopening conditions.** Do not assign another sub-C=40
search within #2017's exact additive model, the already covered GL3 census, or
another 5%-gain search inside #2013's fixed-word monotone-frame domain. A correction
to the proof or a named change to its hypotheses can reopen the relevant domain.
Do not retry QQ16 selected-only homogeneous control with the same first pair and
ordinary schedule; change the observation/interface contract first. These are
scoped exclusions, not universal ceilings on integer multiplication.

**Next bounded experiments; success and stop criteria.**

1. P104: pin one side-correction cut, establish frame access, and compute an
   optimistic complete moment including the correction and hosting. Reject the
   candidate if access is unavailable or the favorable bill misses its declared
   target. Local completion can be a useful partial artifact; it is not admission.
2. QQ16: test one priced extra observation or changed first pair against the
   lost-query witness. If it survives, derive one two-call ordered identity and
   price the maps, helpers, restoration and endpoints. Stop on the witness or an
   unfavorable complete budget before extending the schedule.
3. Stock: derive one same-domain selected reserve/depth envelope. If a source
   implication is missing, hand off that exact lemma instead of recomputing the
   fourteen already checked headrooms. Completing one stage leaves the others open.

Parallel scopes should differ by correction/cut, changed observation, or specific
proof obligation; they must still check live overlap. Do not spread a hundred agents
across the same two examples by varying random seeds. Independent audits and new
mechanisms outside these candidates remain welcome with a concrete rationale.

**Validation of this guidance patch.** `python3 -B -m unittest discover -s tests -p 'test_research_*.py'` passed (65 tests, 5 skipped). Catalogue paths, allocation-table agreement and deterministic selection were checked; the new P104 card was also exercised through the CLI. No scientific replay or stronger frontier is claimed.

**Uncertainties and next review trigger.** Neither P104 nor QQ16 has a demonstrated
completed budget beating the selected supplier. Their concrete local evidence makes
them testable leads, not probable winners. Both primitive budgets and all inherited
contracts still matter. Reassess after the first fully priced completion or decisive
obstruction, a new admitted supplier, a correction to these scoped results, or the
next substantial reviewed batch. If both candidates fail, select a different changed
contract from new evidence rather than expanding their searches without a reason.

## Revision 4 workflow follow-up — 2026-10-14: refresh looping agents

Base `7c1e7811c730b17fe0eeef6c82ef011318b0465e`; selected record and task weights
unchanged. The maintainer asked whether repeated agents would see course corrections.
Inspection found only entry-time "current main" and general checkpoint language;
`choose_research_task.py` reads local files and makes no upstream request.

Add an explicit canonical-main fetch/review checkpoint at each round, before
pivots/submission and roughly hourly during long rounds. Distinguish fetching
from updating the working checkout; account for fork origins, offline operation,
new worktrees, pinned inputs and continuing work. Add the breadcrumb to AGENTS.md
and the short donation prompt. Existing running agents still need to reach or
be instructed to use the checkpoint; this patch does not push instructions into
their active sessions. No task reallocation or new scientific claim follows.

## Revision 4 workflow follow-up — 2026-10-14: discussion usability

Base `564148b82ae9df72163f22106f15e73efca8aff2`; catalogue, weights and selected
result unchanged. The maintainer requested an assessment of live discussion
coordination. At approximately 18:40–18:43 UTC, GitHub reported 189 threads;
we sampled the 60 most recently updated threads (up to eight comments and five
replies each), plus the four hub bodies and up to 30 recent comments/eight replies.
This was an operational sample, not a full census or mathematical audit.

[Plane-port work](https://github.com/CrocSwap/integer-mult-bounds/discussions/1587)
and [centre-path work](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516)
show concrete follow-up chains. [A new QQ16 claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2074)
already uses revision 4; this establishes uptake, not scientific correctness.
[Contributor feedback](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18930476)
also identifies handoffs as useful. Long claims in onboarding/hub threads and
completion updates below CLAIM titles impede scanning. Local-only evidence in
[#2053](https://github.com/CrocSwap/integer-mult-bounds/discussions/2053) and
[#2057](https://github.com/CrocSwap/integer-mult-bounds/discussions/2057) cannot
be replayed by other contributors from the posted artifact references.

Update AGENTS/autoresearch with one canonical investigation thread, a short
current-status summary, short hub pointers, accessible artifacts, and explicit
permission within the existing contribution policy to submit useful partial or
negative results without a new supplier. Encourage handoff-first continuity and
synthesis after several adjacent negative searches. Document the existing path
search and external per-session cache options. No posting approval gate, new
shared claims file, or mandatory session report is added. Existing board posts
are untouched; this patch sends no messages and changes no scientific priority.

Reassess based on handoff retrievability and follow-through, not post counts.
If navigation remains costly, consider a read-only index with source links and
freshness, keeping advisory claims distinct from mathematical acceptance.

## Template for the next decision

```text
Revision / UTC date:
Exact base and selected source record:
Evidence links and verification status:
Current bottleneck; what changed:
Track/card decisions (continue / narrow / expand / pause / replace):
Old allocation -> new allocation:
Paused scope and evidence that would reopen it:
Next bounded experiment and stop rule:
Uncertainties and useful work preserved:
Next review trigger:
```

Prepared by Douglas Colkitt with OpenAI Codex assistance. Apache-2.0.
# Revision 5 — 2026-10-15: refresh family entry points and gate expansion

**Base and selected sources.** Canonical main freshly fetched at
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2`; selected PR1094 conditional kappa
`0.001672660197076918`, resolved through
[selected-result.json](../../certificates/selected-result.json),
[its review](community-batch1099-review.md) and
[source manifest](../../research/community-frontier1094-audit/SELECTED-SOURCE.json).
No selected scientific artifact is changed or newly certified.

**Evidence and limitations.** Read the existing revision-4 assignments, the
[review through #2027](community-efficient1000-review.md), recent open PR and
Discussion summaries, and [workflow feedback](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18930476).
That contributor reports that live handoffs yielded useful work across roughly
35 sessions. This supports making handoffs easier to follow; it is not a measured
population-wide success rate. The live sample is not a complete queue review.

Inspected the descriptions and exact heads of pending
[#2540](https://github.com/CrocSwap/integer-mult-bounds/pull/2540)
(`630d557af5088f66b45c447969cee9576600e50b`) and
[#2586](https://github.com/CrocSwap/integer-mult-bounds/pull/2586)
(`7953c9a8f788a8de5cf2ced63d9a61b67c22c6f1`). They report local QQ16 decoder
completion and P104 physical-dual construction, respectively, with explicit
remaining obligations. Their mathematical claims were not replayed or admitted
by this guidance change. Credit ywz65 and the predecessor authors retained in
their PRs; the [family status record](research-family-status.md) preserves the
key lineage and scope. Active follow-ups include
[QQ16 bank retention](https://github.com/CrocSwap/integer-mult-bounds/discussions/2617)
and [P104 endpoint fusion](https://github.com/CrocSwap/integer-mult-bounds/discussions/2619).

The maintainer's local product audit `4b44c26ba` and checkpoint `aff5269d0` report
useful coded/shared receiver improvements but a remaining unfavorable budget and
scoped retiming optimum. They are local-only, not publicly reproducible evidence
in this main checkout; their exact limitations and outstanding consumer/native
obligations are recorded in the family page. The global change is a process gate,
not an asserted universal theorem or a mandate to work on the product branch.

**Allocation and decisions.** Old -> new weights are unchanged:
bit mechanisms 20 -> 20; complex mechanisms 20 -> 20; recursive interfaces
20 -> 20; adversarial audit 15 -> 15; independent verification 10 -> 10;
verifier engineering 8 -> 8; consolidation 5 -> 5; incumbent optimization 2 -> 2.
There is no measured reason here to reweight the entire portfolio.

- Narrow P104's card to a still-unresolved correction/physical endpoint/hosting
  obligation of a pinned follow-up. Keep independent audits available.
- Advance QQ16's entry point to the pending complete local decoder and its
  consumer/retention/whole-cover costs, while retaining the earlier scoped witness.
- Continue targeted selected-stock and other missing-interface audits, with
  live overlap checks before assigning already-covered arithmetic.
- Retain alternative coding/geometry/interface exploration. Pause the maintainer's
  fixed preparation retiming recipe; do not generalize its closure to other models.
- Preserve task IDs and weights. Update mechanism-card first steps, overlap terms
  and expansion criteria rather than adding many near-duplicate cards.

**Next bounded experiments and stop rules.** A contributor can solve one scoped
lemma, local construction or audit. Before expanding a family, require its exact
boundary, complete obligation ledger, explicit cost allowance and the reason
saved work does not return in the consumer. Unknown costs are not zero; an
optimistic passing relaxation is not feasibility. Stop an implementation expansion
when its favorable complete bound fails or its required access/consumer has no
specified contract. Exploratory design can instead end with a bounded handoff.
A changed graph, boundary or operation model with a concrete new budget can
reopen a scoped closure. Further negative proofs should change an actual research
decision, not merely extend a closed census.

**Workflow versus scientific allocation.** The new family page is a central
navigation record and an expansion template, not a required extra report from
each donor. Use existing canonical threads for live status. Distinguish local
module, complete supplier, integrated kappa and audit milestones. Keep parallel
work distinct by mechanism/contract/obligation, not nonce. Broad weights remain
allocation hypotheses; this patch makes no new scientific claim.

**Review trigger.** Reassess after independent review of the named completion
claims, a decisive complete-cost rejection, a new admitted supplier, or the next
substantial PR review. Newer heads and handoffs can change the next useful task
without changing the selected frontier. Refresh both primitive budgets before
claiming a target-scale route.

**Validation.** `python3.12 -B -m unittest discover -s tests -p 'test_research_*.py'` passed: 65 tests, 3 skipped. Both refreshed cards were exercised through the task-picker CLI; catalogue sources, weights and documented allocation agree. Relative documentation links and `git diff --check` passed. No new mathematical replay or frontier claim.

## Revision 6 — 2026-10-16: advance handoffs and audit coordinated changes

**Base and evidence status.** Assessed against canonical main
`b3f3ee0392b71b118fd086a6eaf6b4cab54ef455`, fetched with no divergence.
The selected conditional κ remains **0.001672660197076918**; its authoritative
sources and review remain those of [selected-result.json](../../certificates/selected-result.json),
unchanged since `a23bdc1b07be96bea0101d44ae27d14de67a79ed`.
This is a task-guidance change, not a mathematical replay or supplier admission.

Read the retained package claims for #2965, #2972, #2973, #2977, #2979 and #2981,
their explicit open questions and source-intake records. Exact heads and credit
are in the [revision-6 family handoffs](research-family-status.md#revision-6-handoffs-source-archives-awaiting-independent-validation).
The records are [#2965](pr-intake-evidence/windows-and-new-archives-20261016.json),
[#2972/#2973](pr-intake-evidence/archives-20261016b.json),
[#2977](pr-intake-evidence/archives-20261016d.json),
[#2979](pr-intake-evidence/archive-pr2979.json) and
[#2981](pr-intake-evidence/archives-pr2980-2981.json).
These establish source retention, not independent scientific validation.
In particular, the newer claimed κ ≈ 0.001729 is not admitted by this update.

The latest three comments in the [workflow feedback thread](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200)
were checked. They report [console encoding work](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18950852)
and [package diagnostics/pins work](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200#discussioncomment-18956325).
Classify these as existing workflow handoffs, with no new action in this patch;
they do not supply evidence for scientific portfolio reweighting. This is a
limited feedback sample, not a survey of current board activity or agent yield.

**Allocation.** Old -> new weights remain: bit mechanisms 20 -> 20; complex
mechanisms 20 -> 20; recursive interfaces 20 -> 20; adversarial audit 15 -> 15;
independent verification 10 -> 10; verifier engineering 8 -> 8; consolidation
5 -> 5; incumbent optimization 2 -> 2. Keep existing task IDs; add only the
specific `census-pruning-audit` card within adversarial audit. It shares that
track's allocation rather than taking weight from exploration.

**Decisions and bounded tests.**

- **Continue independent verification; narrow its immediate lead.** #2979
  reports a coordinated circuit/frame win where isolated changes lose.
  Independently reconstruct one shared group and a single-change control, then
  follow the changed children, idle widths and cleanup buffers into the full
  invoice and both supplier caps. Stop with a source-bound missing-obligation
  handoff if admission cannot be checked within the session. Do not turn the
  author receipt into a validated frontier or immediately expand the search.
- **Narrow P104 to execution.** #2981 reports static joint endpoint flags.
  Assign chronological acquisition/delivery, dependencies, coefficient identity,
  dirty restoration and complete cost for one named collection. Do not repeat
  static cover counting or use nesting to refute program-level lifetime floors.
- **Narrow QQ16 to producers and consumers.** #2965 supplies a proposed
  completed-output defect bound, not producer interiors. Pin a literal producer,
  derive its actual magnitude/dirty-helper ledger, and price the consumer.
  Stop at an unspecified interface or unfavorable complete bill; further local
  precision optimization alone does not justify family expansion.
- **Continue targeted stock and exporter audits.** #2972 leaves the actual
  coefficient unresolved; derive it from the selected producer rather than
  recomputing cutoff arithmetic. Independently reproduce #2977's tiny exporter
  mismatch and selected unique-row control before adopting a guard. Its mutant
  does not itself invalidate the selected construction.
- **Audit suspect exclusions before extending censuses.** Check #2973's tiny
  parity counterexample and one exact predecessor prune, then compare a small
  exhaustive domain. Map affected dependencies. A faulty pruning rule does not
  automatically disprove every old final bound; the proposed replacement also
  needs independent validation. Stop before a full census unless separately
  budgeted and tied to a specific research decision.
- **Continue broad mechanisms; narrow repetitive follow-ups.** A static cover,
  precision or source-count extension must identify the unresolved obligation
  or research decision it changes. Independent checks with new coverage remain
  welcome. Reopen a scoped closure with a changed premise and explicit budget,
  not a larger seed or an unvalidated predecessor claim.

**Next review trigger.** Independent validation of the coordinated mechanism,
a decisive complete-cost result for P104/QQ16, resolution of a selected stock or
semantic obligation, a changed selected supplier, or the next substantial intake.
Agents refresh canonical main at their existing round checkpoints; preserve
useful partial work and frozen inputs. No new reporting file or full replay is
required merely to consume these revised cards.

**Validation.** `python3.12 -B -m unittest discover -s tests -p 'test_research_*.py'`
passed: 158 tests run, 18 skipped. The sparse integration checkout initially
omitted pinned navigation inputs; those exact HEAD files were materialized
before the successful run. All six refreshed/new cards passed through the
task-picker CLI at revision 6. Track weights and existing task IDs are preserved;
relative documentation links resolve in the working tree or exact HEAD tree,
and `git diff --check` passed. No scientific artifacts, selected certificate
or CI execution policy changed; no Lean, Docker or scientific replay ran.

## Workflow update — 2026-10-16: handoffs, coverage and grouped review

**Evidence:** maintainer-supplied external feedback based on `b5ea56e0a` and
[Discussion #1200](https://github.com/CrocSwap/integer-mult-bounds/discussions/1200),
compared with current main `836b19bfa309ceafbc8ee32a15e8c4b10dde7e11`. This pass
does not independently reproduce the report's queue counts or claims about
donor behavior. Existing handoff and short-session guidance was scattered.

**Change:** handoff-first selection, source-bound `existing_checks` on three
initial cards, optional cached board metadata and a safe file-based posting
helper. The queue view reuses the intake plan and groups explicit word/profile
metadata, preserving unknowns and source versions. It shares profile-ceiling
arithmetic without inferring circuit equivalence or changing review decisions.
The root guide is now an entry point; standing procedure and changing scientific
priorities have separate files.

**Allocation:** priority revision **6**, all eight track weights, and the selected
#1094 record remain unchanged. This is workflow repair, not new scientific
evidence or portfolio reweighting. The queue profile inventory is an explicitly
small pilot, not an assertion of full classification. It includes the selected
reference, archived #2979 profile, and the declared #2979 audit scopes of open
PRs #2993, #3006 and #3008. Those PR bodies and heads were inspected; their
scientific checks were not rerun for this workflow change.

**Next review:** measure duplicate checks avoided and maintainer time saved on
one actionable construction cluster. Add coverage records as actual review
evidence arrives; expand profile intake only if it reduces repeated review.
Do not create a survey PR per session or replace missing scientific evidence
with structured labels.
