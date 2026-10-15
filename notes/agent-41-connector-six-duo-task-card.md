# Task card: connector-alphabet-change, six-source DUO Pareto (agent-41)

Task ID / proposed scope key: `connector-alphabet-change` (drawn), scope key
`ff4f5113ed2256ab19ed`; chooser OS nonce `f6e1088f04305c75046a5a048c04b89a`;
track `recursive-interfaces`; priority revision 4.

Base commit; exact predecessor and dependency heads: base
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (origin/main at session start).
Predecessors (read-only, in-tree): `research/universal-connector-boundary`
(PR943/PR934, Ross Richardson), `research/duo-toggle-connector` (PR1403
claim lineage, Navinor), `research/universal-connector-six-source`
(PR1185/PR1215). Concurrent external: https://github.com/CrocSwap/integer-mult-bounds/pull/2056
(head `c713ff9e`, pair-source five-source restatement, claimed 17:42Z,
released 18:22Z).

Concrete object and question: in the connector model extended by exactly the
pair-source DUO family (charged weight-2 steps), what is the six-source
universal-path Pareto profile (k calls, W adds)? Any witness with k < 16 and
W <= 16 Pareto-improves singleton f(6) = 16 and drops the all-63-row batch
below 142 root queries.

Scope status: **changed**; reason: the card's own first-counterexample domain
(3/4/5 sources) is saturated by `research/duo-toggle-connector` and the
concurrent PR above; the card's scope-change trigger records "keeping the
alphabet and only increasing the source count" as a changed assignment; the
six-source question is the predecessor's own recorded open question 2. Side
result (labelled): counting closure of that predecessor's open question 3
(three-source calls cannot lower W below 12 at k = 10 on five sources).

Existing restriction being changed (or exact claim being audited): the
singleton-alphabet value f(6) = 16 and the frozen support bound 2(n + rows)
for the all-63-row batch; the changed premise is the added DUO operation
family of `research/duo-toggle-connector`, already defined and charged there.

Method; explicit parameter ranges/candidate alphabet: exact prefix-difference
reduction; seeded hill-climbing over closed walks on F2^6 with weight-1/2
steps, k in {12, 13, 14, 15}, number of DUO calls in {1..6}, total budget
about two minutes (seed 20261014); exact lower bounds and complete all-unit
censuses (945 and 10,395 canonical words) for exclusions; code-disjoint
replay of every certified fact.

Nearest overlapping PRs and why this adds something:
https://github.com/CrocSwap/integer-mult-bounds/pull/2056 (five-source, same
DUO family; different source count and open question);
https://github.com/CrocSwap/integer-mult-bounds/pull/1185 (singleton f(6)=16,
improved here by the DUO witness); `research/duo-toggle-connector` (five
sources; its open questions 2 and 3 are exactly this package's main question
and side result).

Optimistic full cost budget; required observable improvement: batch 140
queries at 142 adds (saving 2o in the predecessor price model); if only
singleton-length words were found, no improvement and the route dies.

Success evidence; falsification test; time/compute cap: explicit witness with
all 64 masks covered (exact replay); falsification by the four mutation
controls and the two complete censuses; compute cap two minutes of search.

Predecessor authors; intended artifact and reproduction command: Ross
Richardson, Douglas Colkitt, Hanson Sun, Navinor, Arham Tahir (comparison).
Artifact: `research/connector-six-source-duo/` with
`python3 -B research/connector-six-source-duo/verify.py` ->
`PASS_CONNECTOR_SIX_DUO witness=(14,16) n5max=31 k12max=49 mutations=4`.
