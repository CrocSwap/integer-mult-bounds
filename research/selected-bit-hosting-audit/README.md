# Selected PR589 bit hosting: exact pending-projector audit

**Finite geometric audit and scoped counterexample; no new kappa.** All
126,432 helper occurrences of the selected PR589 nine-stage R439 bit supplier
have disjoint physical pending supports, including 14,208 physical families
that host helpers from more than one idle child. The complete paid histogram
is independently recounted and agrees with the selected supplier receipt.

An equal-rank coordinate substitution preserves the slot counts, within-child
disjointness and borrowing windows, but changes the exact bit address operator.
It is a counterexample to a deliberately weakened, count/window-only
geometric implication, **not an input accepted by the production pipeline**.
The source-bound level-to-axis interpretation supplies the missing constraint.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.

## Reproduce

From the repository root, Python 3.12 and its standard library suffice:

```sh
python3 -I -B research/selected-bit-hosting-audit/verify.py
python3 -I -B research/selected-bit-hosting-audit/test_verify.py
python3 scripts/research_package.py --package research/selected-bit-hosting-audit --check-only
python3 scripts/research_package.py --package research/selected-bit-hosting-audit
```

The first command checks [RESULT.json](RESULT.json) without rewriting it and
prints `PASS_SELECTED_BIT_HOSTING_AUDIT: 126432 helper occurrences; 111 port
projectors; 12 controls rejected`. The second runs six tests, including an
independent dense rational-matrix comparison. Both also work with `-O`.
To review intentional receipt changes, `verify.py --write NEW_PATH` writes
only a previously nonexistent file. No optimization, native build or download
is required.

## Exact object and source boundary

Base: `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`. At this base the selected
complex source is PR1094 `0fc329d0bec93ca7cd288eaea1295172e8789810`; its assembly
explicitly retains bit PR589 `a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`, merged
as `b3eb785ac5b4b1ca2beea0f80db078a505626a90`. The assembly's exact bit-receipt
blob and selected manifest hashes bind the tuned word, frozen selection and
receipt consumed here. Full pins are in [SOURCES.json](SOURCES.json).

The finite domain is 111 live ports, 439 full-width-eight helper residuals per
call, nine stages, four pairs, 32 replicas and 64 ambient axes. No pending PR
is a code dependency. The scoped task card and next questions are also in
[TASK.json](TASK.json).

| Recount | Result |
| --- | ---: |
| Controller events / idle children | 29 / 10, including one zero-rank child |
| Independently reconstructed slots per replica | 3,951 |
| Physical calls / helper occurrences | 288 / 126,432 |
| Physical families containing hosted helpers | 28,128 |
| Families hosting helpers from multiple idle children | 14,208 |
| Maximum helpers of one call sharing a physical family | 5 |
| Helper occurrences containing the entire local q-perp block | 21,312 |
| Live-port rational projectors / local frame dimensions | 111 / 636 |
| Recounted rank mass / deficit | 1,808,352 / 10,272 |

The nonzero idle remainders are `{2:13920, 4:14208, 6:14208, 7:21312,
42:288}`. There are also 7,104 zero-rank remainders, all from the terminal
zero-rank child. Adding local transitions and nine rank-seven COPY charges
per call gives the complete histogram
`{1:381024, 2:400416, 3:22752, 4:26880, 5:29376, 6:17376, 7:26784, 42:288}`.
Reflection preserves each transition rank and COPY gap, so forward and
reflected calls have the same rank histogram. This recount does not replay
their scalar semantics or recertify the moment endpoint.

## Pending-projector argument

For any live root vector q, q^T q = 4. On the eight local coordinates put
`P_q = q q^T / 4` and `K_q = I_8 - P_q`. Direct rational multiplication checks
`K_q^2 = K_q`, `K_q q = 0` and `tr(K_q) = 7` at all 111 ports. Define exterior
seven-dimensional blocks `E_j`, for `j=1,...,8`. In a chart with q/2 first,
q-perp next, and the exterior coordinates last, the source level spaces are

- `L_-1 = span(q)`;
- `L_a = Q^8 + E_1 + ... + E_a`, for `0 <= a <= 8` (orthogonal direct sums).

An idle advance `a -> b` therefore has projector `P(L_b)-P(L_a)`. Its chart
axes are `[1, 8+7b)` when `a=-1`, and `[8+7a, 8+7b)` otherwise. Endpoints are
half-open. Replaying the source recipe's pair levels produces this table:

| Child | Pair | Levels | Pending axes | Eligible local stages |
| ---: | ---: | --- | --- | --- |
| 0 | 1 | -1 to 1 | [1,15) | 0,1 |
| 1 | 1 | 1 to 2 | [15,22) | 2 |
| 2 | 2 | -1 to 3 | [1,29) | 0,1,2,3 |
| 3 | 2 | 3 to 4 | [29,36) | 4 |
| 4 | 3 | -1 to 5 | [1,43) | 0,1,2,3,4,5 |
| 5 | 3 | 5 to 6 | [43,50) | 6 |
| 6 | 0 | 2 to 8 | [22,64) | 3,4,5,6,7,8 |
| 7 | 1 | 4 to 8 | [36,64) | 5,6,7,8 |
| 8 | 2 | 6 to 8 | [50,64) | 7,8 |
| 9 | 3 | 8 to 8 | empty | none |

For each physical family, distinct rows of this table have disjoint supports.
Inside each row, the frozen slots partition a subset of its ordered axes;
the remainder is the exact complement. This proves orthogonality of every
pair of hosted supports and of each support with its remaining child factor.

**No orthonormal completion has to be chosen for these slots.** Every selected
slot contains either all seven q-perp axes or none of them; the same is true
of every child and remainder. Thus its actual projector is either `K_q` plus
an exterior coordinate projector, or just an exterior coordinate projector.
Changing the orthonormal basis of q-perp cannot change any of these projectors.
This observation is specific to this width-eight frozen selection; arbitrary
mixed-width slots can split q-perp and need additional basis data.

For a projector P the inherited exact bit address operator is

```
D(P) = [ I-P   P  ]
       [  P   I-P ].
```

If P and Q are orthogonal projectors, block multiplication gives
`D(P)D(Q) = D(P+Q)`. Induction proves that each child's hosted factors and
its remainder equal its original operator on **arbitrary head and tail
vectors**, not just sampled inputs. For commuting coordinate projectors
with overlap the formula is instead `D(P)D(Q) = D(P+Q-2PQ)`: repeated axes
cancel. The separate dense rational tests cover all two-coordinate support
pairs and show that noncommuting projectors cannot use the coordinate-set
argument. These tests accompany, rather than replace, the algebra above.

## Counterexample and production protection

On pair 1, child 0 contains exterior axis 8, while child 7 contains axis 36.
Conjugate **only child 7's realization**, including all its hosted slices and
remainder, by the ambient permutation exchanging axes 8 and 36. Its rank
stays 28; every slot width, relative offset, source stage, helper identity,
within-child disjointness and remainder rank stays unchanged. Its support
now overlaps child 0 at axis 8 and omits axis 36.

The products of this family's idle factors before and after the substitution
differ on exactly these two exterior axes. Applied to `(head=e_8, tail=0)`,
the original product gives `(0,e_8)` and the modified product gives `(e_8,0)`.
This is an exact address-operator witness, independent of the port q. It is
not a replay of the whole interleaved supplier on that particular input;
local calls and bridges also occur between idle deadlines. At an individual
deadline the modified child operator already differs from the source operator.

The production `audit_hosted_k.py` compares the schedule with the source
parent and validates relative slots under each child; `global_k.py` and
the geometry contract assign the actual pending subspaces from those levels.
Neither accepts an arbitrary alternate chart field of the kind introduced
in this adversarial fixture. `adapt9p.py` changes the live-port and COPY-rank
accounting, and PR545's adapter substitutes the live labels; it does not
grant arbitrary pending axes. These pinned constraints protect the selected
construction. The counterexample explains why a replacement geometric
compiler must preserve this binding, even if its rank and timing receipts
are unchanged.

## Independence, controls and limits

The audit independently implements backwards window scanning, direct
intervening-touch checks, finite allocation, ambient masks, all-replica
family checks and exact frame-rank/profile recounting. It compares allocation
and windows against the source's `expand` and `windows` functions. Only these
named pure functions, the source `recipe`, and the literal idle-table
construction are extracted with Python AST; entire producer modules, solvers
and original acceptance checkers are never imported. The source recipe and
geometric level convention are declared inputs, not independent discoveries.

Twelve semantic controls reject equal-rank overlapping and wrong-disjoint
charts, duplicate axes, missing/duplicate helpers, distinct-helper overlap,
illegal stages, negative offsets, wrong width, out-of-replica copy indices,
an intervening bridge with stale windows, and a nonempty zero-rank child.
Six additional tests cover the positive receipt, independent dense matrix
composition, the noncommuting boundary, a split-q-perp rejection, changed
source bytes and a changed committed receipt. Checks remain active under `-O`.

This is a finite geometric certificate with a written projector argument.
It does not prove the inherited complete-call correlated-helper realization,
injective cover-class compilation, local scalar correctness/H1-H5, all-size
compiler, native lowered program, precision/tape, analytic transfer, or the
full multiplication theorem. No complete cold replay, Lean proof, new moment
endpoint, supplier adoption or selected-frontier change is claimed.

Nearby work is retained: [PR1228](https://github.com/CrocSwap/integer-mult-bounds/pull/1228)
and [PR1231](https://github.com/CrocSwap/integer-mult-bounds/pull/1231) derive two
pending ranges for one historical PR442 R747 invocation; this audit covers the
current PR589 R439 allocation and every idle child. [PR1209](https://github.com/CrocSwap/integer-mult-bounds/pull/1209)
and Josie Elliston's retained T16 owner audit treat the complex supplier.
[PR878](https://github.com/CrocSwap/integer-mult-bounds/pull/878) formalizes bit
B boundaries, not this global geometric census. No priority is claimed for
projector algebra, strict borrowing windows or the historical range formulas.
Sagar Thakrar's [PR589 width-packing audit](../bit589-width-packing/README.md)
already recounts the slot capacities and remainders and proves a restricted
width-eight packing optimum. Those counts are consistency checks here; the
added evidence is the current all-child projector census and the exact
rank/window-preserving geometric counterexample.

## Open next questions

1. Can the all-call pending-projector statement be connected to a typed
   physical realization of the actual PR589 emitted word? This would reduce
   the remaining gap between finite placement and complete-call hosting.
   Start by exporting these source-bound slot masks into the PR540/PR1231
   multi-host contract with the R439 word. The missing current-word extraction
   and correlated-helper realization remain blockers; historical Lean data
   cannot simply be renamed.
2. Which mixed-width selected or proposed bit allocations split q-perp?
   The completion-free argument would then require explicit local projectors.
   First run the `mask & 255 in {0,254}` gate on one pinned candidate's slices;
   if it fails, obtain the actual source orthonormal complement before testing
   orthogonality. No such mixed-width source is admitted or excluded here.

## Credit

DreamingOfClouds / eumemic supplied PR589/555/545/543 and the punctured word,
interleaved interface, parameter adapters and retained replica chain. Zhihao
Chen supplied the PR386 bit geometry; DaysSky supplied PR442 idle-axis
hosting; chafreaky and the earlier bank/replica contributors supplied its
retained extensions. Their source notices and disclosed AI assistance remain
intact. The PR1228/1231 auditors and Josie Elliston's independent complex
owner audit provide nearby precedents. Rohan Arun's PR1094 supplies selected
context; it is unchanged. New material is Apache-2.0. This is AI-assisted
research and local checking, not independent human peer review.
