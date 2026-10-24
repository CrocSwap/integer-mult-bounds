# Exact small-component frame optimum at one fixed price

Prepared by Chris R / Clear1nsight with substantial OpenAI Codex assistance.

At **C=15108879/5000000000 = .0030217758**, exact min-sum elimination on #4994's **18 small components/68 contacts**, with the **1,271-variable component held at source**, has exactly the source paid histogram in both orientations: `{1:2201,2:412,3:510,4:127,5:40,8:8}`. This proves zero saving in this restricted product at this C. Four chosen contact labels change under the tie rule; the source is a minimizer, with no uniqueness claim.

The separate integer-cut extension stops at cut 3: cuts 1/2 equal source (3298/4395), while cut 3 is **5075 versus source 5080**. Its feasible histogram `{1:2223,2:421,3:490,4:132,5:40,8:8}` differs by `22H1+9H2−20H3+5H4` and costs **+0.077586985710037469603912620755..756** at the fixed power price. Thus the proposed all-concave extension fails. **Cuts 4..8 were not run.** This is neither a global/all-price optimum nor a new physical schedule, caller or κ result. The zero-saving ceiling concerns only the native recursive rank moment at this single C and fixed restricted graph/domain. Equal profiles may have different finite routing, storage or precision costs. Other exponents, the larger component, changed ownership/interfaces and compiler routes are outside the claim; no complete-cost or physical optimality follows.

[Independent review](evidence/REVIEW.md) explains the mathematical certificate: complete actual subspace domains, every original mapped multiedge and fixed-neighbor unary, finite infeasibility penalty 5328, exact min-sum recurrence/traceback and all 29,790 reconstructed containments. The independent checker does not import the author solver, factor builder, domain generator or price comparator. It checks 8,760 bucket alternatives across the four objectives/two orientations, all 119 strict fixed-price comparisons using a separately pinned rational interval library, and factor-deletion, nonoptimal-argmin and histogram corruption controls. It reuses the authenticated source constructor/frame-DAG; it does not independently replay native phase semantics.

## Reproduce

Python3.12+, standard library only. From any directory (replace the path):

```sh
python3 -I -W error -B research/small-coupled-frame-optimum/verify.py
python3 -I -O -W error -B research/small-coupled-frame-optimum/verify.py
```

Each command authenticates the full retained independent packet, runs its unchanged checker, then reruns the unchanged author fixed-price and cut drivers with explicit `--source-root` and private output paths. Semantic comparisons remove only elapsed-time fields and summary receipt hashes that bind those times; underlying receipt data are compared completely. Default commands write only private temporary files, print compact summaries, require no Git/network, and never regenerate frozen results. Expected runtime is under 30 seconds per mode on this workstation. The author driver stops at k=3. Its loop and provisional all-eight status string remain visible unchanged in the archive; the stop receipt and wrapper enforce the actual completed scope.

Registered checks:

```sh
python3 -B scripts/research_package.py --package research/small-coupled-frame-optimum --check-only
python3 -B scripts/research_package.py --package research/small-coupled-frame-optimum
python3 -B scripts/check_research_commit.py --package research/small-coupled-frame-optimum --check-source-history
```

## Provenance and portability

Base `f259dabc7d70e0db8d6d36bfda888f008bbfecc1`. Source #4994 `ef2810fe43829960789f783e44ee6484d0368f09`, retaining #4971 `0130b196145a43a7d305de41f49e56e8e8556378`. Independent interval source: `20bb93cd990d2ff683e4d0fc56b87a42cd5d3296:research/higher-moment-strictification/verify.py`.

The whole 57-file independent input manifest plus its own FILES.json is retained byte-for-byte in `evidence/`, including all frozen author code/results, corrections, timing receipts, source proposal, graph snapshot and original license/NOTICE. [BRIEF.md](BRIEF.md) preserves the author stopping decision, including its historical local-publication status. [ORIGINS.json](ORIGINS.json) maps the original Git requests to their exact retained bytes. SOURCES uses original upstream provenance rows plus same-path live-input pins at a retained ancestor. Both upstream heads are canonical ancestors; publication preflight checks history separately from byte integrity. The archive preserves source line endings and the native verifier's original extra blank EOF; the path-specific whitespace attribute records that exception. No AST/scientific expression rewrite or loader adaptation is needed: the existing author `--source-root` interface is used. Export byte integrity is not authenticated provenance or mathematical acceptance.

[CONTROL-CLARIFICATION.md](evidence/frozen/CONTROL-CLARIFICATION.md) preserves the original author control limits. The independent controls are stronger and separately described in the review. No historical full suites, native phase/emitter campaign, selected cold replay, large-component enumeration, Pareto search or objectives 4..8 are part of this package.

## Task, overlap and credit

The claimed `complex-rank-shape-decoder` card is explicitly **changed** to a supporting exact restricted optimum/independent verification. [TASK.json](TASK.json) retains the original card. Claim/review publication coordination: [#4994 comment](https://github.com/CrocSwap/integer-mult-bounds/pull/4994#issuecomment-6358831540).

1337isnot1337 supplies [#4994](https://github.com/CrocSwap/integer-mult-bounds/pull/4994)'s interval/realization model; Dugongue supplies [#4971](https://github.com/CrocSwap/integer-mult-bounds/pull/4971)'s frame-carrying swaps; Cao Yifan and native/controller/compiler predecessors supply the retained word. Astra supplies the authenticated source-specific proposal and its fit to Rina Dechter's published min-sum bucket-elimination theorem (1999), cited in the unchanged [PROPOSAL.md](evidence/source/PROPOSAL.md). The new contribution is the bounded exact implementation, certificates, independent reconstruction and portable verification. All source credit and Apache-2.0 notices are retained.

[#5016](https://github.com/CrocSwap/integer-mult-bounds/pull/5016) is neighboring numerical full-domain MILP evidence, with different coverage from this exact restricted certificate. krzysztofwojt's [#5024](https://github.com/CrocSwap/integer-mult-bounds/pull/5024), head `390d7255f0e128be54e007962d7febb47697a7c5`, proves an all-price global optimum for any number of **intact source zero-edge regions** under its fixed maps/boundaries. Our per-contact small-component domain permits splitting source regions and fixes the big component. These are different restrictions; no dominance claim is made.

## Open next questions

A changed physical word or interface needs a source-bound complete favorable invoice before expansion. The 1,271-variable component, broader schedules and physical caller remain open; this package supplies no reason to enumerate them. See the smallest bounded follow-up in TASK.json. No new κ or selected-frontier change is claimed.
