# Independent audit of the selected centre-descent tree bound

**Corroboration of a scoped obstruction; no new kappa.** This package independently reproduces ctoth's [released branching-descent finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18913740) on the actual selected PR1094 word. It supplies a code-disjoint checker, source bindings, a written proof with explicit hypotheses, and a finite optimization oracle. It does not claim the bound or the pairing-cost principle as new.

Each of the eight centre frames has dimension eight and serves 22 distinct targets. Its intersection with all their final frames is zero. Thus every **independent nested descent tree** delivering that centre's value costs at least eight rank units. The current descent to zero attains eight, so the relaxed optimum for the eight trees is **64**. Allowing higher waiting levels and free branching cannot improve it within this model.

## Reproduce

From the repository root, with Python 3.11+ and no third-party dependencies:

```sh
python3 -I -B research/centre-descent-tree-audit/verify.py
python3 -I -O -B research/centre-descent-tree-audit/verify.py
```

Expected: `PASS_SELECTED_CENTRE_DESCENT_TREE_AUDIT centres=8 cost=64 tree_cases=4096 controls=7`.

The checker reads inputs without modifying them. `--receipt` prints the recomputed evidence; ordinary execution also compares it with [EXPECTED.json](EXPECTED.json). The registered CI replay uses Python 3.12:

```sh
python3 scripts/research_package.py --package research/centre-descent-tree-audit --check-only
python3.12 scripts/research_package.py --package research/centre-descent-tree-audit
```

## Exact source and checked boundary

Base: `858771bcca3b8dd5d4ef4aa682a13cc9b7e23920` (main), priority revision 3. Selected PR1094 source head: `0fc329d0bec93ca7cd288eaea1295172e8789810`. The task chooser assigned adversarial audit, with nonce `a1da71bb34b536d2654ca322f0a71cdb`. [TASK.json](TASK.json) records the refinement, overlap, stopping rule and claim.

The checker reads the provider at `candidate/strict/global/base/providers/gauge44/` **inside** `research/community-frontier1094-audit/selected-replay.tar.gz`. Its canonical word has **480 helpers**, not the 492-helper ancestor shipped at `gauge44-slots-t16/evidence/local/`. The archived assembly is byte-bound to the reviewed standalone assembly; the reviewed result binds its hash and historical selected kappa. The archive's provider binding and native replay both bind the canonical container. Its decompressed payload matches the slot recipe's exact canonical pin `4ddb29fb9bc6f27e0c0fbfcf19a2a93a3496ad900d0f6d89059d0305c9576c0c`. [SOURCES.json](SOURCES.json) pins all consumed repository inputs by Git blob and SHA256. The selected record and task catalogue are historical provenance, rather than an instruction to change the live frontier.

Two separately read representations agree on all **176 nonzero scatter edges**, including their exact rational coefficients: the canonical `cut` and the emitted forward program's private-C additions. The emitted program has precisely eight rank-eight centre descents to zero. The checker does not replay that program's full scalar map.

The primary F2 method enumerates the vectors of every relevant subspace and intersects the 22 served target final frames. A separate method restricts their port functionals to the eight displayed centre basis vectors and performs binary row elimination. It verifies that every target final frame really is the kernel of its supplied port functional, rather than assuming this from a frame ID. Both methods give codimension eight for every centre.

The receipt also corroborates the released ancillary figures: **88** targets are served by two centres, all **88** relaxed maximal common waiting levels have dimension **six**, each centre sees 22 distinct such levels, and their pairwise intersections have dimensions four or five. These level statistics are separate from the tree-cost proof.

## The exact tree lemma and proof

Let F be a finite-dimensional vector space. Consider a finite rooted tree whose root is labelled F and whose node labels are subspaces. Each edge U to V must satisfy **V contained in U** and costs `dim U - dim V`. Copies at a node are free. Every demanded target t is served at a designated node labelled L_t satisfying `L_t contained in G_t`, where G_t is that target's final frame. Several targets may share a node. The cost C is the sum over **tree edges**, counting a common edge once.

Then

`C >= dim F - dim(F intersect all G_t)`.

A short induction makes the tree hypothesis explicit. For a subtree rooted at U, let J be the intersection of all its designated service-node labels, and take J = U for an empty demand. We prove `dim U - dim J <= subtree cost`. A service at U contributes a factor U to J and no cost. Ignore child subtrees containing no demand; their nonnegative costs can only increase the invoice. For the remaining child subtrees rooted at V_j, let their corresponding meets be J_j. Each J_j is contained in V_j, which is contained in U. The subspace codimension inequality gives

`codim_U(intersection J_j) <= sum_j codim_U(J_j)`.

For each child, `codim_U(J_j) = (dim U - dim V_j) + codim_V_j(J_j)`. The induction hypothesis bounds the latter term by that child's subtree cost. Summing counts exactly the outgoing edges and descendant costs, proving the induction. At the root, J is contained in `F intersect all G_t`, so its codimension is at least the claimed bound. No assumption about binary branching or tree depth is needed.

In the **fully relaxed one-centre problem**, the bound is attained: descend once from F to `J0 = F intersect all G_t`, then freely copy J0 to serve all targets. This may not meet a concrete program's timing or first-read constraints; it proves only the relaxation's optimum. For the selected word J0 is zero for all eight centres, and the archived program already delivers each centre at zero, so the eight independent trees attain total 64. Shared targets can also wait at zero consistently.

The dual computation is the standard kernel statement: stack the target functionals restricted to F; its kernel is `F intersect all G_t`, and its rank is the codimension. This is the credited decoder pairing-cost interpretation, not a new general decoder lower bound.

## Finite oracle and failure controls

A separately formulated dynamic program computes the minimum cost of arbitrary finite descent trees over **all 16 subspaces of F2^3**, for every ordered pair of target boundaries and every root (256 pairs, **4,096** root/boundary cases). Its recurrence either descends to any strict subspace or freely copies and partitions the target demands. It does not use the meet-bound formula to choose the optimum. All optima agree with the formula. Identical target boundaries exercise sharing; independent lines exercise the need to retain both demands; zero targets exercise charged descent despite free copies.

A hypothesis-removal counterexample is also checked: the incomparable lines spanned by `(1,0,0)` and `(0,1,0)` have equal dimension. Charging their nonnested transition only by dimension difference would cost zero, while the meet bound is one. Such a transition is excluded by the containment rule; this is not an allowed supplier circuit or a current acceptance bug.

This finite oracle is a control, not a proof for arbitrary dimensions. The universal statement above remains a written proof, with no theorem-kernel or human-review claim.

Seven semantic mutations are rejected: substitution of the ancestor helper count, omission of a scatter edge, zeroing a scatter coefficient, a wrong target final frame, a nonzero selected waiting level, a duplicate centre carrier, and omission of a native centre descent. Checks remain active under optimized Python. The normal verifier also rejects source drift and any mismatch with the committed exact receipt.

## Limits

This is a bound on **one value per independent nested tree**, with linear dimension-drop prices and final-frame containment. It allows free copies and omits B-word timing, tail constraints, scalar overhead, hosting, phase and precision costs; adding restrictions cannot make this relaxation cheaper. It does not justify treating a general circuit that mixes centre values, merges paths, cycles, ascends, changes frames outside containment, or uses dirty hosts as such a tree.

In particular, it does **not** certify the separate dirty-host inequality in the [earlier finding](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18913724), which [an664 is independently auditing](https://github.com/CrocSwap/integer-mult-bounds/discussions/1516#discussioncomment-18914674). No modified host program, owner schedule, complete local scalar/phase replay, cold supplier replay, invoice, moment or full multiplication theorem was reverified here. The reviewed archive's finite replay is consumed as pinned evidence. There is no new supplier, kappa, or selected-record change.

## Open next questions

A changed decoder's served-port/centre-frame geometry might have a nontrivial common meet and hence a smaller relaxed centre cost. A feasible first step is to recompute the two independent boundary quantities here for one exact changed decoder, then screen its **complete paid profile** before synthesis. The blocker is a valid new local-program interface with all frame, restoration and hosting costs charged. The fixed selected geometry has no tree-relaxation headroom. The structured question is in [TASK.json](TASK.json).

## Credit

Credit ctoth and the disclosed GPT-6/Codex, Gemini/Antigravity and Claude Opus 5.5 reviewers for the released finding, and DreamingOfClouds' PR595/decoder pairing-cost lineage. The selected word retains Jeremy Kothe's mutable-leaver and slot construction, Rohan Arun's slot and owner-packing work, Hao Yan's T16 controller, icekylinx's frame/native machinery and the full earlier supplier lineage identified by the selected review. an664's complementary dirty-host audit is explicitly separate.

Prepared for Dennis (@antunishdPursuit) with substantial OpenAI Codex assistance in proof exposition, checking, code and packaging. No independent human review is claimed. New work is Apache-2.0; frozen predecessor files and notices are unchanged.
