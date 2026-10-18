# Helper470 retirement: timing and the exact fixed-slot optimum

**Research note and conditional cost certificate. No new bit endpoint, kappa,
or supplier admission.** In the declared slot model, PR1256's helper470
retirement is best used at stages **2, 4 and 6**, with the original word at the
other six stages. Requiring retirement in all nine stages increases the bill.

Ross Richardson's [PR1256](https://github.com/CrocSwap/integer-mult-bounds/pull/1256)
provides the finite local circuit and a favorable two-slot relaxation but leaves
its timing open. This package adds the exact timing support, explicit slot
placements, a joint-placement optimum in a bounded class, and the complete
conditional profile. Its local circuit replay corroborates PR1256; the local
patch is not new work here.

Base: `410026dc5513b87db92ae98571d1d5984c69a983`. The selected record resolves to
PR1094, kappa `836330098538459/500000000000000000`, with PR589 on PR555 as the bit
supplier and the complex side binding. We followed its actual
`research/community-frontier1094-audit/ASSEMBLY.json`, source manifest and
`docs/research/community-batch1099-review.md`. The selected cold command is
`make frontier1094-verify`; it was not run for this standalone research note.

## Declared class and result

Keep the selected nine-stage recipe, 32 replicas, 439 helpers per call, and all
other helpers' exact placements. For helper470 in each stage, choose:

1. Keep the original word and its width-eight residual, when retirement is optional.
2. Use PR1256's word and shrink the existing allocation to its first seven cells.
3. Use PR1256's word and move the entire width-seven residual into a contiguous
   interval that was idle in the **original** allocation and is legal for that stage.

Different converted helpers may share an originally empty rank-42 child, with
disjoint cells. New holes freed by another conversion are **not** destinations.
No other helper moves, new banks, recipe changes, copied totals or new operations
are allowed. Replicas use the same placement; independent replica choices cannot
improve on the same per-replica minimum. This is a finite rank-and-window model,
conditional on admitting the changed local endpoint and mixed stage dispatch.

The source recipe has ten idle children, one of rank zero. The exact nonzero
window support is:

| Child index | Pair | Capacity | Permitted stages |
|---:|---:|---:|---|
| 0 | 1 | 14 | 0, 1 |
| 1 | 1 | 7 | 2 |
| 2 | 2 | 28 | 0, 1, 2, 3 |
| 3 | 2 | 7 | 4 |
| 4 | 3 | 42 | 0, 1, 2, 3, 4, 5 |
| 5 | 3 | 7 | 6 |
| 6 | 0 | 42 | 3, 4, 5, 6, 7, 8 |
| 7 | 1 | 28 | 5, 6, 7, 8 |
| 8 | 2 | 14 | 7, 8 |

Capacity is not free space. Originally idle space that can hold seven cells
exists only in the 222 copies of each rank-seven child and nine completely
empty copies of child 6. Stages 0 and 1 cannot relocate in this class. The full
single-relocation census has **2,610** positions: 666 in rank-seven children and
1,944 in rank-42 children, counting all contiguous starting offsets.

The selected placement is `[child, family-copy, offset, width, stage, helper-index]`:

```text
[1, 14, 0, 7, 2, 248]
[3, 14, 0, 7, 4, 248]
[5, 14, 0, 7, 6, 248]
```

Helper index 248 is local register 470. OS seed 14 selected the third of three
candidate tasks and copy 14 among the 222 tied host copies. The result covers
the entire declared class, not just that seed's placements. All 126,432 helper
occurrences are assigned family indices and checked for local slot collisions,
widths, completeness and untouched windows. These checks do **not** bind the
physical pending projectors across children of a family.

## Complete cost and the joint-placement argument

Replaying the credited patch on all 661 dirty scalar columns in both directions
gives `0 -> 1 -> 2 -> 7` for helper470, instead of `0 -> 1 -> 8`.
The other 660 frame paths and all nine COPY/ERASE pairs are unchanged. Per
converted call, ADDs change 24,305 to 24,307, MOVEs 2,911 to 2,912, and the local
paid histogram changes by `e1 + e5 - e7`. Here `er` denotes one rank-r child.
The three selected stages therefore add 192 scalar ADDs and 96 MOVEs across
32 replicas; this is not a scalar-operation saving.

Let `g(r) = r (64/r)^a`, `g(0)=0`, at the pinned
`a = 1733427039589844234749/10^24`. Returning all eight cells to the old host
with remainder r and consuming seven from a distinct idle remainder q gives

```text
Delta H = e1 + e5 - e7 + e(r+8) - er + e(q-7) - eq.
```

Zero-rank children are omitted. In-place shrinkage instead returns one cell:
`Delta H = e1 + e5 - e7 + e(r+1) - er`.

The old helper470 remainders, by stage, are `4,4,2,2,2,2,4,2,6`. Every in-place
change is a strict loss. Rank-seven relocation is a strict gain where legal.
To handle joint packing correctly, enumerate every nonempty subset of the six
stages that can use child 6: **63 subsets**, each priced with the single joint
remainder `42 - 7 |S|`. Every such group costs strictly more than its best
fallback, both with optional and mandatory retirement. Its child-count surcharge
is no smaller. Every multi-child placement partitions into these groups, so no
combination of the nine empty rank-42 children can improve the fallback.
The distinct rank-seven children can attain their fallbacks simultaneously.

A separate state enumerator checks the conclusion without that reduction. It
enumerates **2,550 distinct complete profiles** with optional retirement and
**211** with mandatory retirement, including all feasible rank-42 bin loads.
Every profile other than the declared minimizer has a strictly larger full bill.
Tied choices of family copy/offset can have the same profile; no unique physical
allocation is claimed.

The selective profile change across 32 replicas is

```text
+96 e1 -64 e2 -32 e4 +96 e5 -192 e7 +64 e10 +32 e12.
```

The complete inherited bill is
`sum(Hr*g(r))/(64*28416) + 32*64*sum(Hr)*64^a/(10^16*28416)`.
All unchanged allowances and the bad-residue surcharge are retained.

| Deployment | Paid children | Rank mass | Full bill minus baseline |
|---|---:|---:|---:|
| Original PR589 | 904,896 | 1,808,352 | 0 |
| Retire only stages 2,4,6 | 904,896 | 1,808,352 | approximately -3.0483817628e-7 |
| Best compulsory retirement in all nine stages | 905,088 | 1,808,352 | approximately +3.0325008908e-7 |

The certificate contains exact outward rational intervals and all complete
profiles. Decimal figures are display values, not decisions. The primary check
uses a 64-term positive atanh logarithm with a geometric tail and a 24-term
exponential with a geometric tail, followed by outward dyadic rounding.
The independent check uses the retained Mercator engine for all profile
comparisons and both retained moment engines for the three complete bills.
This certifies a cost ordering at one exponent, not a new endpoint or a general
root-ordering theorem.

## Reproduce and evidence limits

From the repository root, Python 3.12, standard library only, no network:

```sh
python3.12 scripts/research_package.py --package research/bit-helper470-window-placement-seed14
```

Expected markers: `PASS_HELPER470_WINDOW_PLACEMENT`,
`PASS_INDEPENDENT_HELPER470_PLACEMENT`, seven tests `OK`, and
`PASS_REGISTERED_RESEARCH_PACKAGE ... outcome=completed`.
The direct scripts also work under `-I -O -B`.

The primary replay reconstructs the receipt and rejects twelve controls,
including each omitted retirement gate, stale cleanup, a stage outside its
window, incorrect widths/extents, duplicate/missing helpers and omitted idle
charges. Tests also cover intervening bridge touches, joint remainder pricing,
a fully filled rank-42 child, partial overlap, source corruption and a forged
owner witness rejected by both implementations under Python optimization.
`--emit NEW_PATH` regenerates a receipt without overwriting existing files.

**Unresolved:** H4 replacement and reverse physical routing; a stage-indexed
emitter for mixing the original and retired words; actual mixed-width pending
projectors and complete-call correlated-helper realization; the new renamed
native/hosted stream and its precision/tape invoice; and the all-size/compiler
and analytic obligations. The existing emitter keys local programs by forward
or reverse orientation, so the proposed stage-selective dispatch is not an
already implemented supplier. The baseline orientation is unchanged, but the
new wrapper must be built and admitted. We do not infer physical admission from
the scalar replay or owner counts, and did not run native, hosted, selected cold
replay, or Lean checks. No new kappa or practical speedup is claimed.

## Open next questions

1. Can stages 2,4,6 realize these exact rank-seven placements with a valid H4
   replacement? Start with stage 2, child 1, copy 14 and bind the retiring
   hyperplane to the host's actual pending projector. Then build the mixed
   stage emitter. The endpoint and correlated-helper contracts are blockers;
   timing and cardinality alone do not settle them.
2. Can relocation into holes freed by other conversions improve this result?
   Start with the two stage-0/1 old slots in child 2 and permit explicitly paid
   coordinated relocation. That changes the declared destination class; it is
   not covered by this optimum. Establish a favorable complete invoice before
   investing in physical construction.

## Credit, overlap and provenance

- Ross Richardson, PR1256: the unchanged-prefix local retirement circuit and
  two-slot cost formula. Exact head `d6d5a994fcdcd8d04ec439ff988daa8f37b17ece`.
- Cinna Davis, PR1401: the same-slot cost obstruction; Sricharan Vagvala,
  PR1302: finite native replay and full-frame closure. Their findings are
  retained, not refuted by this conditional selective placement.
- Ali Romman, PR1043/1128: earlier source-boundary deletion with a hosted invoice
  and the restoration boundary analysis. PR1043 reports a complete hosted
  invoice; that package was not rerun here, and its savings are not combined.
- DreamingOfClouds, PR589 and the PR510/463 template lineage; eumemic, PR555 and
  punctured adapters; DaysSky, PR442 hosting; chafreaky and Zhihao Chen, retained
  audits; Sagar Thakrar, PR1023 width-packing analysis and incentive.
- PR1307 (@commdata2338): the distinction between slot/window counts and physical
  pending-projector bindings. Its mixed-width limitation is explicitly retained.
- Concurrent discussion1427 changes the stage recipe while keeping width-eight
  helpers. This package freezes that recipe and studies one width-seven endpoint.

The complete initial overlap scan covered 820 open PRs and 154 discussion
records, including comments, with no pagination warning. No pinned coordination
issue existed; [CLAIM.json](CLAIM.json) records the local claim and three
candidates as requested. [TASK.json](TASK.json) records the deliberate change
from the already covered H2/K card to the H4/hosting question. See
[SOURCES.json](SOURCES.json) for base, live source Git/SHA256 pins and exact
predecessor heads. No frozen package, `upstream/`, or selected record changes.

Prepared by **Hanson Sun (@bbMisk)** with substantial **OpenAI Codex assistance**
in investigation, implementation, verification and writing. The separate
implementation is an algorithmic cross-check, not independent human review.
New work is Apache-2.0; predecessor attribution and licenses are retained.
