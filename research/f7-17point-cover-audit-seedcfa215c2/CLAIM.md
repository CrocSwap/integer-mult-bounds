# Task card — KB3c (pair-collision object change): audit PR 2542's "no 17-point set covers F2^7"

Task ID / proposed scope key: kappa-blocker KB3c (assigned explicit open request,
discussion 1166); drawn card `supplier-boundary-audit` (scope key
`dcdb0fa8e49b08a958d0`, chooser seed `cfa215c2c38597502362f49fd5b40ff0`); scope
**changed** to the set-level claim audit below.

Base commit; exact predecessor and dependency heads:
`0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (canonical main, priority revision 4).
Predecessors: [PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542)
by Aaron Wang (head `3b6011d2400f50ab0ad9e105c7c55a18f3cef4cf`, package
`research/universal-f7-singleton-seedb859517b`), engine vendored byte-exact;
[PR 2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634) by Aaron Wang
(head `e2f30d93efbef5658334072aa855aa95e795e394`, package
`research/universal-f7-singleton-l20-seed06704c39`);
[PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) by Nicholas
Stone (NicholasStone) completing the simple-20-cycle census to 15/15 shards.
Model source: [PR 943](https://github.com/CrocSwap/integer-mult-bounds/pull/943)
by Ross Richardson (`research/universal-connector-boundary`); pinned record
[PR 1185](https://github.com/CrocSwap/integer-mult-bounds/pull/1185) by Doug
Colkitt (Mister-Meeseeks) (`research/universal-connector-six-source`).

Concrete object and question:
PR 2542's README asserts **"No 17-point set covers `F2^7`"** (section "Why length
18 collapses", item 3), but its own `lemma_a_table` / `lemma_a_by_multiset`
contradiction is computed only for the split rows `(9,8)`, `(8,9)` (and `(8,8)`);
its CERTIFICATE records `size17_splits = {"9_8": false, "8_9": false}` only.
Counting-feasible 17-point parity splits `(s,t) = (|E|,|O|), s+t = 17` are exactly
`(9,8), (8,9), (10,7), (7,10), (11,6), (6,11)`. Question: **does any 17-point
set `S` with `S+S = F2^7` exist at all** — i.e. is PR 2542's literal claim true,
or does a 17-point covering set exist (falsifying instance)? Equivalently, extend
the pair-representation identity to the surviving rows `(10,7)/(7,10)/(11,6)/(6,11)`
and decide their realizability exactly.

Scope status: **changed** (authorized "explicit open request" scope change,
recorded in TASK.json with this reason). The assignment drew the card; the draw
(supplier-boundary-audit / uniform-transfer-audit / selected-stock-envelope) is
saturated/off-track. The assignment's options (a)/(b)/(c) were checked against the
live board: (a) the L=20 simple-cycle shards are **completed** by [PR
2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) (6,305,209,079
nodes / 597,148,314 simple 20-cycles / 0 universal, 15/15 shards); (b) the
repeated-state L=20 **word** census (splits (10,9),(10,8),(9,9),(10,7)) is
**actively claimed** by Nicholas Stone (NicholasStone, Kimi agent), discussion
1166 comment 18954844 (2026-10-15 17:46 UTC, expires 21:30 UTC); (c) the
existence of an L=20 universal word is that claim's own question. Pair-collision
rule: changed objects on the match. The changed object is the **set-level**
question the assignment itself names as the recorded remainder ("PR 2542's 'no
17-point set covers F2^7' overreaches its own lemma table") — a claim audit
matching the drawn adversarial-audit track, decided without enumerating words.

Existing restriction being changed (or exact claim being audited):
Audited claim: "No 17-point set covers F2^7"
([PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542), README,
section "Why length 18 collapses", item 3). Scope boundary: set-level covers only
(`S subset F2^7`, `|S| = 17`, `S+S = F2^7`); no word enumeration (Nicholas
Stone's claimed object), no kappa/supplier/selected-frontier change.

Method; explicit parameter ranges/candidate alphabet:
1. Reproduce PR 2542/2634 recorded numbers first (n=5 L=10 words=945 max=31;
   n=6 L=12 words=10395 max=49; n=6 L=14 words=945945 max=59; L18
   nodes=15775992 cycles=312064 universal_words=0; L20 campaign 120/126/128).
2. Extend the pair-representation identity to rows (10,7),(7,10),(11,6),(6,11):
   closed-form `lemma_a_table` rows plus the sharper collision-multiplicity
   identity (cross-sum collisions: `sum_o C(r_o,2) = 2 sum_x A_x B_x`, odd excess
   `sum_o (r_o - 1) = st - 64`, profiles partitioning the excess), machine-checked
   against `lemma_a_by_multiset`-style enumeration.
3. Smallest falsifying instance first: search for one 17-point covering set
   (set-ILS at k=17, then exact structured search of the extremal Sidon/Sidon
   profile (10,7) with 0 in A WLOG; A subset of E = F2^6 image, B subset of the
   odd coset, exact pair-sum support constraints). Sharded/resumable with exact
   counts if the tree exceeds the budget.

Nearest overlapping PRs and why this adds something:
[PR 2542](https://github.com/CrocSwap/integer-mult-bounds/pull/2542) proves the
L=18 exclusion using only the (9,8)/(8,9) rows; this audits its generalized
headline and fills the missing rows. [PR
2634](https://github.com/CrocSwap/integer-mult-bounds/pull/2634) records the
open remainder and the cover/walk dichotomy (open question 2: "Is r((C2)^7) =
20?"); this decides the k=17 level exactly where its identity leaves it open.
[PR 2691](https://github.com/CrocSwap/integer-mult-bounds/pull/2691) and
Nicholas Stone's active claim enumerate words at L=20; a set-level exclusion of
the (10,7) row prunes their smallest split (handoff), and their object is
explicitly not taken.

Optimistic full cost budget; required observable improvement:
Finite combinatorial object; no supplier moment to price. Required observable:
the complete six-row 17-point split table with machine-checked identity rows and
either (i) an explicit 17-point covering set or (ii) exact exclusions of the
searched profile classes with exact counts.

Success evidence; falsification test; time/compute cap:
Success = exact rows + witness-or-exclusion evidence, reproduced by a second
independent implementation. Falsification of "no 17-point cover" = one explicit
S with S+S = F2^7 (replayable in microseconds). Cap: one session, ~150 minutes,
with the final quarter reserved for verification, package, gate and handoff;
shard checkpoints if the exact search runs long.

Predecessor authors; intended artifact and reproduction command:
Predecessor authors: Aaron Wang (PR 2542, PR 2634), Nicholas Stone (PR 2691),
Ross Richardson (PR 943), Doug Colkitt (PR 1185). Intended artifact: this
package (`research/f7-17point-cover-audit-seedcfa215c2/`) plus one focused PR.
Reproduction: `python3 -I -B research/f7-17point-cover-audit-seedcfa215c2/verify.py`
(plus `independent.py`, `test_engine.py`, and the sharded search entry point).
