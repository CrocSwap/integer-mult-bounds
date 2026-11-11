# Chronological batch divisibility in the direct mixed compiler

**Result:** the fixed chronological flow in [PR #4436](https://github.com/CrocSwap/integer-mult-bounds/pull/4436)
admits a smaller, explicitly computable productive width. For prescribed smaller
supplier widths, the formula below gives the **least common replication factor
under the stated batching policy**. A histogram-only relaxation can fail: an
actual rank-12 toy flow accepts multiplier 175 in aggregate but needs 700 at
one parent-round cut.

At raw p7 rank 1,000, the new productive width has **2,524 bits**, versus
**17,504 bits** for #4436's nested construction. The old width is an integer
multiple of the new one; the reduction factor has 14,981 bits. The normalized
rank-one leaf cost is exactly unchanged at every checked rank. This is a
conditional batching lemma and finite accounting result, **with no new kappa**.
It does not establish a smaller asymptotic width order or a practical algorithm.

## 1. Source and the missing question

The audited source is zxv's #4436 at
`56003680aee2871773de408e5f01cc5dd46b144c`, sections 2–3 and open question 3.
It realizes Sussman's integer lockstep construction with overlapping ranks,
pays unmatched exits, and chooses `a_n = B_(n-1)`, `B_n = a_n S_n` so every
smaller width divides the replication factor. Its original LCM freedom is
explicit predecessor work. The addition here is the exact batch-by-batch
gcd/LCM criterion, its chronological counterexample and a source-bound finite
construction using it recursively.

All target ranks are at least 2; `m` is their maximum; every paid rank is
positive and below `m`. Keep the source's default height
`G = floor(log_(k_min)(floor(n/m)))`, complete source census, native word and
parent-round order. Only the replication factor changes. The input profile
is the frozen p7 native invoice, not a new audit of its physical correctness.
`VENDOR.json` binds four exact source files by URL, commit, Git blob and SHA256.
They are retained locally for Git-free replay; no unmerged Git object or
network is needed by the scientific verifier.

The all-column, arbitrary-input, spectator, whole-job adapter, routing and
owned-state contracts of the source remain hypotheses. Equal ranks alone
do not implement a physical adapter. Native work and physical routing remain
paid under those contracts.

## 2. Batching policy and least replication factor

Let `S_s` be the source-job count at rank `s`, and `S = sum_s S_s` the total
source count at ambient rank `n`. The prescribed completed program of each
smaller rank `e` has productive width `B_e > 0`. Put `B_0 = 1` and give a
zero-rank complement zero cost.

The allowed batching policy is:

1. Before the flow, group **all source complements** by rank `n-s`. These
   act on distinct original arrays before any enters the chronological flow.
   Each group has `a S_s` arrays after common replication by `a`.
2. At **one parent-round cut in one path class**, group equal-rank unmatched
   exits across that class's units. Complete every group before returning
   from that cut. A cut with `q` exits of rank `e` has `a q` arrays.
   Separate paths or paid positions are separate cuts, even when their
   ranks and multipliers agree.
3. Match and resume native calls exactly as in #4436. Replicated copies of
   a given class run in lockstep. No unfinished job is pooled with a later
   cut; no extra productive input is credited.

Record batches `(e,q)`: complements have `(n-s,S_s)` and exits have their
**per-cut** counts. For this finite list define

```text
a_n = lcm over batches (e,q) of B_e / gcd(B_e,q),
B_n = S * a_n.
```

**Lemma.** These widths are valid under the inherited source contracts, and
`a_n` is the least positive replication factor for this policy and the
prescribed smaller widths.

**Proof.** A whole rank-`e` supplier invocation handles `B_e` arrays.
Partitioning `a q` arrays into whole invocations is possible exactly when
`B_e | a q`. With `g = gcd(B_e,q)`, coprimality of `B_e/g` and `q/g`
makes this equivalent to `(B_e/g) | a`. All conditions hold exactly when
their LCM divides `a`, proving necessity, sufficiency and minimality.
Every recursive rank is below `n`: the source proves `0 < s <= n` and
`0 < e < n`. Strong induction therefore supplies every invoked program.
Complements run first; every exit finishes before its parent resumes.
The same disjoint inputs, owners, adapters and completed endpoints as
the source give a full rank-`n` transform on `a_n S` productive arrays.
No fractional invocation is used. QED.

Minimality is **local to this policy and the chosen smaller library**.
It does not optimize earlier libraries jointly, permit fractional suppliers,
vary replication independently between classes, or optimize every schedule
and physical implementation. New widths need not be nested or monotone.

## 3. Counting the chronological cuts

`batches.py` is a new multiplicative-polynomial implementation. Let `F_h(c)`
count ordered target words of length `h` with product `c`, with `W_k`
distinguishable copies of target rank `k`. Then

```text
F_0(1) = 1,
F_h(c) = sum_k W_k F_(h-1)(c/k),
```

where noninteger quotients contribute zero. This equals the sum of the
source's multinomial counts over exponent vectors with the same product.
Product collisions are summed. Only products at most `floor(n/m)` need
storage, since all target factors are at least 2.

At depth `d` and path multiplier `rho`, a present parent supplies
`F_(G-d)(c)` units when `m rho c <= n`. At a rank-`r` paid position the
child demands the subset of Pascal terms with `m rho r c/k <= n`. For
a present parent, demand is at most supply. A positive difference is the
per-cut batch at rank `rho r c`; an absent parent is supplied by new sources.
At depth `G`, each present class contains one unit, so each paid position
has a **single** exit before replication.

Equal-`rho` paths may be compressed for counting. The stored `copies` field
counts occurrences, including repeated paid positions. It multiplies the
total exit and cost census but **never the per-cut batch size** in the LCM.
The checker independently enumerates literal ordered target words and paid
positions in 101 fixtures, comparing complete source/exit counts and the
multiset of cuts. Target ranks 2, 4 and 8 exercise product collisions.

## 4. Cost preservation and inherited width bound

Write `P_e` for the complete rank-one leaf count of a width-`B_e` supplier.
Complement groups contribute `sum_s (a S_s/B_(n-s)) P_(n-s)` leaves;
exit groups contribute `sum_cuts (a q/B_e) P_e`, with all occurrences
retained. Dividing by `B_n = a S` gives the predecessor's exact recurrence:

```text
L(n) = [sum_s S_s L(n-s) + sum_e E_e L(e)] / S.
```

The factor `a` cancels. With the same base `B_e=1, P_e=e` for `e<m`,
induction proves identical normalized leaf costs at every rank. Batching
therefore supplies no new exponent saving.

For the all-rank width comparison, suppose `B'_e | B_e` at every smaller
rank, where unprimed widths are the old nested construction. Each modulus
`B'_e/gcd(B'_e,q)` divides `B_e`, which divides `B_(n-1)` by old nesting.
Their LCM `a'_n` divides `B_(n-1)`. Multiplying by the same `S` gives
`B'_n | B_n`. Equal bases complete the induction. The new construction
inherits `exp(O(N log N))`; finite reductions do not prove a better order.

## 5. Counterexample to pooling across cuts

Use the source equality fixture `targets = {2:4, 3:1}`,
`paid = {1:6, 2:2}` at `n=12`. The new recursive widths through rank 11 are

```text
e:    0  1  2  3  4   5    6    7    8    9   10    11
B_e:  1  1  1  5  5  25  140  140  700  625  875  4375
```

Sources are `{6:60, 8:64, 9:6, 12:28}`; aggregate exits are
`{1:216, 2:216, 4:72, 8:8}`. Clearing complements and aggregate exits gives
multiplier **175** and every aggregate division is integral. But eight
separate rank-8 leaf cuts each contain one job: depth 2, path multiplier 4,
final paid rank 2. Each needs `700 | a`. At `a=175`, the individual batch
has only 175 arrays; the parent cannot complete it with the prescribed
width-700 supplier while waiting for other cuts. The least valid multiplier
is **700**, giving `B_12=110600`.

This refutes this specific pooled divisibility relaxation. The original
#4436 nested construction is valid and is not alleged to contain this bug.
A different schedule or smaller-rank library needs its own argument.

## 6. Exact finite evidence

| Fixed flow | Final rank | Nested width bits | New width bits | Ranks with strict reduction |
| --- | ---: | ---: | ---: | ---: |
| `{2:1,5:1} <- {1:2,4:1}` | 100 | 433 | 42 | 95 of 96 |
| `{2:4,3:1} <- {1:6,2:2}` | 100 | 1,002 | 88 | 97 of 98 |
| Raw p7 | 1,000 | 17,504 | 2,524 | 879 of 880 |

The p7 reduction factor lies in `[2^14980,2^14981)`. These are bit lengths
of enormous integer widths, not physical runtime measurements. `RESULT.json`
records unsigned-big-endian integer hashes, all-rank witness hashes and the
full small counterexample. Standard-library checks cover:

- all nine frozen #4436 source/exit/column/matching receipts;
- 101 independent literal cut fixtures and 2,304 brute-force multiplier cases;
- 1,074 nonbase compiled ranks with **49,474** batch constraints;
- integral batches, divisibility into old width, and unchanged normalized
  leaf costs at every rank, also against a separate rational recurrence;
- frozen nested width and leaf-count hashes for both toys and raw p7;
- twelve rejection controls: pooling across cuts, merging repeated paths
  and paid positions, reducing replication, deleting premature exits and
  malformed rank/count contracts.

No predecessor evaluator is imported or executed. `vendor/flow.py` is a
source reference only. Frozen receipt matches authenticate the comparison;
they do not independently validate the native supplier.

## 7. Reproduction, coordination and limitations

Python 3.12, no dependencies, from the repository root:

```sh
python -B scripts/research_package.py --package research/chronological-batch-width --check-only
python -B scripts/research_package.py --package research/chronological-batch-width
python -B scripts/check_research_commit.py --package research/chronological-batch-width --check-source-history
```

A Git-free copy of this package can run `python -I -O -B verify.py`.
`--write` regenerates the receipt for authoring; default replay compares
the fresh result with the committed receipt. Explicit exceptions keep all
checks active in optimized Python.

Local validation used CPython 3.12.0 on Windows. The metadata/pin check,
registered ordinary and optimized replays, and a fresh Git-free isolated
optimized replay passed. In that separate copy, altered source bytes and
an altered receipt both rejected. Two code mutations also rejected: pooling
repeated chronological calls into one batch, and omitting their repeated
leaf cost. These checks are author-side evidence, not independent review.

Base: canonical main `2a13eb1827784206202db90e5dc8327cf8a250db`, priority
revision 7. The `independent-moment` card is explicitly changed to
chronological batching and width, following #4436's open question 3.
[Discussion #4503](https://github.com/CrocSwap/integer-mult-bounds/discussions/4503)
is canonical. Initial overlap covered all 5,731 tracked local note paths,
354 open PRs, 3,379 Discussion records and 3,787 closed PRs, with complete
reported pagination at 02:29–02:31 UTC on October 22. This is bounded text
coverage, not exhaustive diff review or a novelty certificate.

Submission refresh: canonical main was unchanged. The final snapshot covered
355 open PRs, 3,381 Discussion records and 3,787 closed PRs at 02:39–02:41
UTC, with complete reported pagination and all tracked local notes searched.

#4456 recounts the flow; #4476 checks its original nested widths and routing.
This adds the least per-cut multiplier and smaller actual width witnesses.
#4467's default-height analysis and #4483's changed-height convergence
theorem are separate. No claim is made that the old exponent question
remains generally open after #4483, whose compiler is not audited here.

The historical baseline orientation command stopped on the sparse-omitted
`research/kappa-rebuild/CLAIM.json`; it is not claimed as passing. No selected
cold replay, native/physical admission, formal-kernel proof, independent
human review or new kappa is claimed. The selected frontier is unchanged.

## Open next questions

1. **Can the width sequence be bounded more sharply in all ranks?** This
   decides whether the finite improvement changes growth order. Start with
   prime valuations of `B_e/gcd(B_e,q)` on actual chronological cuts. A
   uniform valuation argument and global optimization over earlier libraries
   remain unresolved.
2. **Does the policy reduce widths for #4483's changed-height flow?** Its
   smaller ambient-rank result motivates this application. First pin its
   cut inventories and verify rank descent and batching boundaries. Only
   #4436's default flow is instantiated here; numerical transfer is unproved.

## Credit

Jacob Alan Sussman supplied the multinomial integer compiler and original
unseparated question. zxv supplied #4436's chronological overlapping flow,
nested width theorem and source export, building on #4359's native bridge.
Cinna Davis / 1337isnot1337 supplied #4416's p7 construction; native lineage
remains credited in the frozen receipt and predecessor note. Ryanson
Jonathan / pinterbanget supplied #4456's independent flow check and #4476's
width/routing evidence. Those results are not new here.

Prepared for **Mihir Srivastava / mihir-s-05 with substantial OpenAI Codex
assistance** in derivation, implementation, verification and writing.
No subagents. New material is Apache-2.0; retained sources keep their notices.
