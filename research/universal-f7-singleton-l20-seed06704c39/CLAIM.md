# Task card — kappa-blocker KB3b (local card, written before computation)

Task ID / proposed scope key: drawn card `p104-side-correction` (track
`complex-mechanisms`, chooser OS seed `06704c399acc3c61ee5b20d9cc253f9b`,
catalogue scope key `72dfbf0708467ad34793`); **scope changed** to the assigned
kappa-blocker KB3b, the explicit open request continuing the sharp singleton
`f(7)` question (refined object: the `L = 20` / `L = 22` singleton universal
path at seven sources).

Base commit; exact predecessor and dependency heads:
- base main `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (priority revision 4)
- predecessor https://github.com/CrocSwap/integer-mult-bounds/pull/2542 head
  `3b6011d2400f50ab0ad9e105c7c55a18f3cef4cf`, branch
  `research/agent-58-f7-singleton-b859517b`, package
  `research/universal-f7-singleton-seedb859517b` (KB3: `f(7) >= 20`)
- pinned record `research/universal-connector-six-source` (PR 1185 lineage) and
  the PR943 model `research/universal-connector-boundary`, both at base

Concrete object and question: in the PR943 prefix-walk model, restored source
words over seven singleton labels; `D(w) = {q_s xor q_t} = F2^7` universal, `f(n)`
the minimum length. Pinned `f(5) = 12`, `f(6) = 16`; after PR 2542 the gap is
`20 <= f(7) <= 24` (Gray bound `2^ceil(n/2) + 2^floor(n/2) = 24`). Question:
does a universal seven-source singleton word of length 20 or 22 exist (a
Gray-beating construction), or can length 20 be excluded (Gray's 24 sharp)?

Scope status: **changed**; reason: authorized "explicit open request" scope
change recorded in `TASK.json`. The drawn complex-mechanisms cards
(`p104-side-correction`, `complex-rank-shape-decoder`,
`complex-new-helper-inventory`) were not taken; the orchestrator assigned KB3b
from discussion 1166 as the explicit open request (the recorded open boundary
"neither 20 nor 22 is excluded, and 24 is attained" of
`research/universal-connector-six-source/README.md`, continued by PR 2542's open
question 1). Taking this request instead of the drawn card is the recorded
scope change.

Existing restriction being changed (or exact claim being audited): the recorded
gap `20 <= f(7) <= 24` in the singleton alphabet only.

**Assignment premise correction (exact obstruction recorded early).** The
assignment's option (a) "exclude length 19" is dead on arrival in this model:
PR943's restoration facts force every label count even and `>= 2`, so every
restored word has even length (a closed hypercube walk; the cube is bipartite).
No length-19 word exists to census. The census "one step up" from length 18 is
therefore **length 20**, and (a) is executed as an L = 20 exclusion.

Method; explicit parameter ranges/candidate alphabet: singleton alphabet
`{0..6}` only. (1) Reproduce PR 2542 and the pinned six-source numbers
byte-exactly (EXPECTED.json: n=5 L=10 words=945 max=31; n=6 L=12 words=10395
max=49; n=6 L=14 words=945945 max=59; counting bounds 10/14/18; Gray 12/16/24;
PR 2542 census nodes=15,775,992 simple 18-cycles=312,064 universal=0). (2) Split
identity rows (`lemma_a_table`) for the L = 20 splits `(|E|,|O|)` in
{(10,10),(10,9),(9,10),(10,8),(8,10),(9,9)} and the L = 22 splits, with the
per-split collision budgets derived from the rows. (3) Construction route:
stochastic/exhaustive search of covering sets `P` (`|P| <= 20`, then `<= 22`)
with `P + P = F2^7`, checked for closed-walk realizability (Hamiltonian cycle
via subset DP/DFS); direct word-level search on length-20/22 restored words as
a second engine. (4) Exclusion route: extend the restricted-growth cycle census
to L = 20 with PR 2542's proved-necessary prunes (multiplicity room,
self-avoidance where the identity forces `|P| = L`, collision budget), sharded
by depth-3 prefix into resumable checkpoints.

Nearest overlapping PRs and why this adds something: PR 2542 is the direct
predecessor (L = 18 excluded; its engine is vendored byte-exact with hash pin
and credit). Distinct concurrent scopes: DUO pair-source alphabet
(https://github.com/CrocSwap/integer-mult-bounds/pull/2396,
https://github.com/CrocSwap/integer-mult-bounds/pull/2128,
https://github.com/CrocSwap/integer-mult-bounds/pull/2156), sparse
weight-1/2/3-mask family (https://github.com/CrocSwap/integer-mult-bounds/pull/2229,
https://github.com/CrocSwap/integer-mult-bounds/pull/2236,
https://github.com/CrocSwap/integer-mult-bounds/pull/2397), four-root paired-call
(https://github.com/CrocSwap/integer-mult-bounds/pull/2282). None touches the
singleton `f(7)` word-length question; this package adds the next length step.

Optimistic full cost budget; required observable improvement: no kappa, supplier
or frontier change; the observable is the recorded `f(7)` gap itself (either
`f(7) >= 22`, or `f(7) <= 22` with a checked word).

Success evidence; falsification test; time/compute cap: exact coverage
verification of any found word (`word_is_universal`, dual-predicate
independent replay) plus byte-exact reproductions before any new number; for an
exclusion, complete per-split enumeration with leaf counts agreeing across
shards. Priced budget about 120 minutes; one bounded pivot maximum (first
construction search, pivot to the L = 20 census, or vice versa); early kill
with the exact obstruction (split rows, node counts, which splits completed)
recorded.

Predecessor authors; intended artifact and reproduction command: PR943 model by
Ross Richardson (`research/universal-connector-boundary`); pinned record by
Douglas Colkitt (`research/universal-connector-six-source`, PR 1185); PR 2542
engine by Aaron Wang with help from opencode
(`research/universal-f7-singleton-seedb859517b`). Intended artifact: this
package on branch `research/agent-61-f7-singleton-06704c39`; reproduction:

```sh
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/verify.py
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/independent.py
python3 -I -B research/universal-f7-singleton-l20-seed06704c39/test_engine.py
```

Pair-collision check (before computation, 2026-10-15 14:07-14:15 UTC):
`agent_tools.py disc-comments` (with nested replies) over discussions 1317 and
1166 since 2026-10-14, plus `scripts/find_overlap.py --refresh` on the object's
proper names ("universal source path", "singleton alphabet", "seven-source",
"Gray bound", "f(7)", "restricted-growth"). No fresh CLAIM on the singleton
`f(7)` object; the only related activity is my direct predecessor's KB3
claim (discussion 1166 comment 18947532) and its FINDING/DONE at 14:02 UTC
(comment 18950671, PR 2542), both released. This card is its continuation.
