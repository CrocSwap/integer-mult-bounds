# Two simple chronologies cannot attain the coupled-carrier packing cap

**Scoped obstruction, with exact source-bound checks; no new kappa.**
The fixed PR3148/PR3153 inventory cannot attain its packing relaxation in
stage-major or replica-major order, for **any positive number T of replicas**.
At the first cap-integral count, T20, at least **1,857** or **7,500** capacity-eight
bins, respectively, must use a non-tight pattern. This answers a bounded part
of [PR3153's smaller-replica handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/3145#discussioncomment-18996207).
It leaves interleaved T20 orders open.

| T20 order | Required capacity-eight bins | Eligible width-eight roles in their three neighborhoods | Forced non-tight bins |
| --- | ---: | ---: | ---: |
| Stage-major | 13,440 | 11,583 | 1,857 |
| Replica-major | 13,440 | 5,940 | 7,500 |

An exact interval matching attains each displayed role count in a relaxation
that ignores all other helper widths and same-call physical-family conflicts.
The obstruction already holds in that favorable relaxation. No actual packing
or physical program is constructed. As a positive control, all **49,728** such
bins admit a matching for the shipped, interleaved T74 order.

## Source contract and the new implication

Keep the inherited provider inventory per local call
`{4:26, 5:2, 6:18, 7:50, 8:99, 9:213}` and local paid profile
`{1:2433, 2:724, 3:228, 4:102, 5:20, 8:8}` fixed. Both named providers have
these counts. Each replica executes stages 0 through 8 in increasing order.
A bin belongs to a replica, idle child, and one of 112 ports. Its window is
**open at the preceding touch and closed at its final stage**.

A forward interpretation of the frozen template's local calls and bridges
reconstructs all eighteen child types. It agrees with all **666** serialized
windows of the original T37 plan. The six capacity-eight children are:

| Children | Physical families within an owner | Window for owner r |
| --- | --- | --- |
| 1, 3 | 2, 3 | t(r,1) < time <= t(r,2) |
| 5, 7 | 4, 5 | t(r,3) < time <= t(r,4) |
| 9, 11 | 6, 7 | t(r,5) < time <= t(r,6) |

Each row supplies 224 distinct bins per owner. The template's historical T37
replication field is not asserted to construct T20: only its per-replica stage
and pending-window contract is transported to the two explicitly defined orders.

The inherited packing dual has twelve tight patterns among 2,551 legal
patterns. Its **only tight capacity-eight pattern is [8]**. The primary replay
executes PR3153's authenticated exact arithmetic module, checks the entire
primal/dual pattern certificate, and evaluates all six other capacity-eight
patterns. It does not rely on a saved PASS receipt. Each other pattern has
reduced cost strictly greater than **3/250**, uniformly on the inherited
root bracket. Thus any cap-attaining allocation must place one distinct
width-eight role in every capacity-eight bin. This implication, combined with
the source windows, is the obstruction used here.

## Proof

For any set S of capacity-eight bins, let N(S) be the union of their eligible
call times. A call has only 99 width-eight roles. Therefore at most
`99 * |N(S)|` bins of S can receive the tight pattern [8]. At least
`max(0, |S| - 99*|N(S)|)` bins must be non-tight. Ignoring physical-family
conflicts enlarges the feasible set, so it cannot invalidate this lower bound.
This is the necessary matching-count inequality; it assumes neither an
allocation heuristic nor native supplier admission.

**Stage-major.** Execute all T calls of stage 0, then all T of stage 1, and so
on. For either pair of children whose window runs from stage s to stage s+1,
where s is 1, 3, or 5, take all 224T associated bins. Their windows have at most
2T-1 eligible call times: the first call of stage s is excluded, and the last
possible deadline is the last call of stage s+1. Hence each group forces

```
224T - 99(2T-1) = 26T + 99
```

non-tight bins. The three groups are distinct, giving **78T+297** overall.
This lower bound also holds with arbitrary replica permutations within each
complete stage block. For the increasing-replica order replayed here, the
eligible union has exactly 2T-1 calls and a matching fills all those slots.
At T20 the per-group counts are 4,480, 3,861 and 619.

**Replica-major.** Execute all nine stages of one replica before beginning
the next. Each of the three short windows contains only its upper-stage call.
It has 224 demanded bins and 99 eligible roles. The 3T disjoint groups force
**125*3T = 375T** non-tight bins. This is independent of the permutation of
whole replicas. At T20 the per-stage-pair counts are 4,480, 1,980 and 2,500.

A useful necessary condition for any changed interleaving is
`t(r,s+1)-t(r,s) >= 3` for s in {1,3,5}: one owner's 224 required placements
need at least three calls of capacity 99. These individual inequalities are
not sufficient, as the stage-major T20 counterexample shows; subsets of owners
must also satisfy the matching-count inequality.

**Cost consequence.** Write `H_q(b)=q*(73/q)^b`, with H_0=0, and normalize the
complete inherited bill by `73*896*T`. At a fixed b in PR3153's cap bracket,
subtracting the same dual objective from every packing leaves the sum of bin
reduced costs. All are nonnegative; every forced non-tight capacity-eight bin
contributes more than 3/250. For T20 the normalized excess over the packing
relaxation is therefore strictly greater than

```
stage-major:   5571/327040000   (about 0.0000170346135)
replica-major: 9/130816         (about 0.0000687989237)
```

The complete inherited relaxation moment at the left endpoint
`b = 17297774946785970118869 / 10^25` is also enclosed in the replay. Adding
either exact penalty gives a lower bound above one. This rejects those orders
at that endpoint; it neither optimizes their smaller attainable exponent nor
changes the selected result. The claim is conditional on the pinned inventory,
window model, additive bin pricing, and inherited local paid profile.

**Matching evidence.** The new checker uses earliest-deadline matching on
individual unit jobs, aggregating identical intervals for efficiency. Processing
slots in time order and choosing an available job with earliest deadline is
maximum-cardinality: in any maximum matching using a different available job
at that slot, exchange it with the chosen job's later assignment, if present;
its release is already past and its deadline is no earlier. If the chosen job
was unmatched, replace the other job. This preserves cardinality. The tests
compare the implementation with a separate exhaustive subset-matching oracle
on all 5,670 multisets/supply profiles in the stated tiny domain. The T20 Hall
upper bounds and actual matching counts independently certify equality.

## Reproduce and evidence

Python 3.12, standard library only; no solver, native compilation or network:

```sh
python3 -I -B research/coupled-t20-window-audit/verify.py
python3 -I -B research/coupled-t20-window-audit/test_verify.py
python3 -B scripts/research_package.py --package research/coupled-t20-window-audit
```

Expected primary marker:

```text
PASS_COUPLED_T20_WINDOW_AUDIT stage_major_deficit=1857 replica_major_deficit=7500 baseline_T74_deficit=0 cap8_bad_penalty_gt=3/250
```

The primary replay finishes in about one second. `--emit` prints the full
regenerated receipt; the normal command compares every field with
[RESULT.json](RESULT.json). It records exact source intervals, all six short
Hall witnesses, matching hashes, rational reduced-cost bounds and moment
bounds. [SOURCES.json](SOURCES.json) pins six live inputs to the base commit.

Controls cover the exhaustive matching oracle; open/closed window boundaries;
job and call capacities; all serialized source windows; physical-family aliases;
missing ports; duplicate or noncausal calls; changed provider widths and primal
counts; corrupted source bytes; and the complete optimized CLI. The written
closed forms cover all positive T; finite replays at T=1,2,3,20,74 corroborate
them. The published T74 order is a positive control for this necessary matching
relaxation only. Its passing count is not a new full allocation audit.

## Scope and decision

The original `complex-new-helper-inventory` card is **changed** to the explicit
PR3153 follow-up. It fixes the inventory and rejects two chronological realizations;
it does not propose a new helper type. [TASK.json](TASK.json) records the single
draw, scope change, overlap and the bounded stopping decision. Scientific base:
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.

**Decision: stop synthesis for these two chronology families.**

## Open next questions

The useful next
step remains a genuinely interleaved T20 order that passes the necessary matching
conditions, followed by an integral tight-pattern assignment with physical-family
exclusion and all other widths. First enforce the three individual gap constraints
and all interval matching constraints; reject a candidate before a large allocation
solve if any fail. Passing those constraints still leaves the full assignment,
chronology/bridges, compact offsets, native frames, dirty restoration, physical
stock/prefix/outer admission and all-size/analytic obligations open. This package
performs none of that synthesis or supplier admission, and does not prove T740
necessary. A changed inventory or source contract requires a new cost calculation.

The stock identity `896*T+509` would count 18,429 physical families at T20;
it is inherited bookkeeping conditional on a complete construction, not a
physical space bound established by this audit. No new lowering search or
family expansion is justified by the present negative result alone.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
No independent human or proof-assistant review is claimed. Apache-2.0.

Nick Petalas's PR3153 (`c509607d1208396ec0045f0ab79f8392fce40b01`) supplies
the independent cap audit, exact arithmetic reused here, and smaller-replica
handoff. Jeremy Diviney's PR3148 (`f2927a4b8afcf0701a6b945e14f30de1d94f5176`)
supplies the cap-attaining T740 construction. dcharb78's PR3133 supplies the
coupled inventory; Gonzalo Mier's PR3143
(`dcfaf1d1a7cfebaab22b95776a36a543bc684d50`) supplies the comparison.
Nick Petalas's PR3024/3030, Marius-Paul Dumitrean's PR2979, Tekalign's owner
checker, Arham Tahir's PR3136 audit and the retained geometry/native/owner
contributors keep their predecessor credit. Hiroki Kumazaki's old-journal
transport test in Discussion3145 is a different, already completed task.
Original source files and their notices are retained unchanged.
