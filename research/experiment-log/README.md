# Research experiment log

A shared record of what was tried, what happened, and when a retry is justified. This initial import covers the original100-idea campaign, three recent100-trial R715 batches, 14 additional scoped search records and 16 execution-failure attempt groups (31 retained artifacts, including propagated wrapper errors). It does not claim every historical command was recoverable. [Counts](COUNTS.json) distinguish ideas, trials, artifacts and attempts.

| Category | Contents |
|---|---|
| [Original100 ideas](campaign-100/README.md) | Eight topic files; successes, scoped failures, partial work and40 proposals with no execution evidence |
| [From-scratch kernel trials](kernel-search/from-scratch-100.md) | All100 trials, no improvement over the fixed baseline; exact input witnesses retained |
| [Retain-and-repair trials](kernel-search/retain-and-repair-100.md) | All100 trials, including losers and improved candidates; parameters and limits retained |
| [Factored-kernel trials](kernel-search/factored-warm-100.md) | All 100 additional trials, no gain, with raw ledger and search script |
| [Other negative searches](negative-searches/results.json) | Retiming, target mixing, donor/entrance search, stage counts, solver timeouts and rejected interface |
| [Execution failures](execution-failures/index.json) | Separate files for storage, compiler, dependency, path, serialization, metadata and assertion failures |
| [Completed verification](verification/README.md) | Reusable full/component receipts with explicit scope |

## Before repeating an experiment

Read the matching category and exact source record. Compare the source word/hash, baseline, assumptions, objective, seed range, parameter choices and verifier scope. Reuse a completed matching run when possible. Record the concrete changed assumption, input, search neighborhood or repaired environment that justifies a retry. A time limit is not infeasibility; a losing finite search is not a global impossibility; an environment error is not a mathematical rejection.

For future entries use [ENTRY-TEMPLATE.json](ENTRY-TEMPLATE.json). Keep raw failures and correction records; add a superseding entry instead of overwriting history. Store one file per coherent experiment or batch within its topic, with stable IDs and evidence paths/hashes. Keep successful and failed runs together so the baseline is reproducible. Contributors should summarize what went wrong and what future agents should check first.

## Evidence and limits

The original100-item archive is pinned to PR368 commit `fa8ab946df57ebadae1a470b637c2a590a0a5317`. Recent PR473 evidence is pinned to `31e557d09c0d55959c91fd27d903bed46fe2d607`. Local import sources and SHA256 hashes are in [PROVENANCE.json](PROVENANCE.json). Paths inside historical raw records identify their original workspace; category links are the public navigation. Archived [discovery scripts](discovery-scripts/README.md) preserve the search recipe but require their original dependencies. This publication reorganizes evidence; it does not rerun or independently validate every historical claim.

Attribution: original campaign authors and all credited upstream contributors retain authorship; source reports and notices remain linked in the campaign archive. Index and recent R715 search/verification work by Rohan Arun with OpenAI Codex assistance. Conditional supplier/compiler and analytic assumptions remain unchanged.

Latest followup: [warm kernel, target-factor composition and new recorded failures](followups/warm-kernel-and-target-factors.md).

Additional completed search: [100 factored-kernel trials, no gain](kernel-search/factored-warm-100.md).

New replication screen: [ten counts with all results and assignments](negative-searches/factored-replica-screens.md); the best aggregate has now passed initial physical checks, while stronger-complex composition and full verification remain pending. See [latest terminal outcomes](verification/latest-terminal-outcomes.json).

Latest recorded failure: [complex-template hash mismatch](execution-failures/complex-template-hash.md). Latest successes and unresolved checks are indexed in [verification](verification/README.md). Initial counts above are the import baseline; later outcomes are retained in followup and verification files.

Post-factor followup: [retiming through five-operation groups, new extreme frames and delivery reordering](negative-searches/factored-retiming/README.md), all with no gain and an initial reporting failure retained.

Completed hosting followup: [exact rational scaling to84 replicas](negative-searches/rational-hosting/README.md); fresh full Python3.14 and completed-provider-reuse Python3.11 receipts are now in [verification](verification/README.md). The initial zero-rank reporting failure is retained.

New structural search: [nested donor entrances](negative-searches/nested-donors/README.md), four fixed-incumbent attempts and20 fully priced local candidates, no gain; exact words, witnesses, results and initial constructor failure retained.

Circuit simplification: [40 redundant additions removed and native checks passed](negative-searches/commuting-cancellations/README.md), unchanged paid profile and two subsequent retiming screens with no gain.

Hierarchy search: [all 424 alternatives and the baseline](negative-searches/hierarchy-rewrites/README.md), including 423 alternatives without helper-stock reduction, one unverified R714 nomination, every compiled word, and the failed strict baseline comparison with its separate diagnosis.

Changed-stock followup: [R714 exact local replay and40 kernel trials](negative-searches/r714-kernels/README.md), including the infeasible no-kernel baseline and both no-gain batches. [Replica28 initial manifest failures](execution-failures/response-replica28-manifest/README.md) preserve both Python-version attempts and the root-only inventory correction.

New composition screen: [PR485 selection plus target factors, response packets and nested promotions](negative-searches/pr485-composition/README.md): five variants, two distinct words, both below the submitted bound.

Kernel basis followup: [eight no-gain donor-expression runs, four basis-exchange runs and the cancellation-first hypothesis](kernel-search/nested-basis-exchanges/README.md). All endpoints, seeds, histories, exact prices and losing alternatives are retained. The successful rank139 candidate is published separately in PR473.

Further search: [80000 exchanges with temporary entrance demotion](kernel-search/nested-basis-demotions/README.md) found no global gain despite a better local proxy; exact prices, histories and a floating packing-marginal diagnostic are preserved.

Complex-side frontier followups: [PR496 packing, entrance, basis and retiming screens](negative-searches/complex496-followups/README.md), all without an admitted improvement; initial execution failures and an explicitly unreviewed fallback-count arithmetic proposal retained.

Coordinated complex gauges: [476 trials, 22 profile classes, all-hosted and bank-permitting prices](negative-searches/complex496-coordinated-gauges/README.md), with no admitted gain.

Retimed-frontier followup: [PR501 directed closures, 400 neutral moves, and six stage-count models](negative-searches/complex501-followups/README.md), all with no improvement in their tested neighborhoods.

Stage-dependent composition: [retimed gauge/kernel trade searches, every homogeneous loser, and the mixed-word nomination](negative-searches/complex501-gauge-trades/README.md). The new computed candidate is in draft PR473 pending physical admission.

- [Asynchronous scheduling followups](negative-searches/async505-schedules/README.md):10,224 fixed-map rejections, two no-gain allocation models,48 new orders, original execution/matching failures and repaired explicit owner construction.

- [Exact asynchronous inventory limit](negative-searches/async505-inventory-wall/README.md):133 timing screens,146-profile exact dual certificate in two arithmetic engines, and new kernel/entrance screens.

- [Partial-own asynchronous composition](negative-searches/partial-own-async/README.md):new-factory allocation, completed finite composition, and a separately unverified coordinated-gauge followup.

Exact frame-only optimality (Rohan Guliani): [the selected #626 jp8/ck words are LP/CP-SAT optimal over all frame assignments of their gate sequences](../frame-lift-search/README.md); 11 sampled commuting-reorder restarts, re-solved exactly, gave no gain.
