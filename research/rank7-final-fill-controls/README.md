# V45 final-word controls fail the complete packing budget

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or formal-kernel review is claimed.

Every control that restores at least one of PR2979's four V45 endpoints from
rank seven to rank eight fails its claimed complex saving, even after allowing
arbitrary fractional repacking in the fixed capacity model. The control retaining
only helper249 at rank seven has complete moment **at least 1.000005090277**.
The fully coordinated final word passes at the same saving.

This is a finite independent invoice audit and a scoped obstruction. It does
not report a defect in the shipped joint construction, a new supplier, or a
new kappa. The selected frontier is unchanged.

## Exact object and difference from earlier checks

The source is [PR2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979),
head `be191346391661f4d35fc0d1508d0a6029572576`. The base is
`463113d675af7410ac91d53a4fed51ec6494eb9a`, priority revision 6.
All twelve live inputs in [SOURCES.json](SOURCES.json) match both the base
checkout and the original PR head. No predecessor Python code is executed,
imported or copied. Coordination is in [discussion #2612](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612).

The four original helper names are `249,251,265,267`; their compact allocation
indices, derived from the actual removed-role lists, are `25,27,41,43`.
Each has zero entrance and the common final seven-dimensional space
`[256,128,64,35,16,11,5]`. Its own parent endpoint has dimension eight and
contains that space.

A control replaces any subset of these four terminal entries with their parent
rank-eight entries. **All final scalar gates, partner frames, later extraction
and rewrite stages, other endpoints, dispatch and private names stay fixed.**
Both providers independently pass the resulting monotone frame recount. Each
widened endpoint adds exactly one rank-one terminal child per invocation and
one unit of helper residual width. The fixed T74 dispatch has 666 invocations.

These are controls of the **final word**, not reconstructions of the original
stage-one experiment. [PR2993](https://github.com/CrocSwap/integer-mult-bounds/pull/2993)
and the [V45 profile audit](../rank7-v45-profile-audit/README.md) already check
that original group's local profile and losing singleton guide price.
[PR3014](https://github.com/CrocSwap/integer-mult-bounds/pull/3014) proves a complete
cost increase when lowering V45 on the older PR2942 assignment. This package
answers its changed-final-fill question: it checks the actual final assignment,
then bounds all repackings of these explicitly different controls.
[PR2987](https://github.com/CrocSwap/integer-mult-bounds/pull/2987)'s chronological
packing audit and later allocation refinements retain their separate scope.
The earlier [single-lowering](../rank7-v45-single-lowering/README.md) and
[shipped-invoice](../rank7-v45-shipped-invoice/README.md) checks by jwr establish
the recorded guide margins and endpoint/buffer inventory. They do not check
these counterfactual final allocations or the complete packing lower bound.

## Complete recursive invoice and literal capacity witnesses

The checker reads all 271,728 placements and all 149,184 bins. It reconstructs
source availability intervals from the source event schedule, checks each
replica's stage order, unique roles, distinct physical families within a call,
nonoverlapping coordinate masks and compact prefixes. Empty bins are charged.
The two independently recounted local profiles are

```text
{1:2445, 2:706, 3:232, 4:108, 5:18, 8:8}.
```

The actual dispatch is 250 base and 416 extra calls. The independently rebuilt
idle profile and complete profile are

```text
idle     {1:17310, 3:4956, 5:1728, 48:28190}
complete {1:1645680, 2:470196, 3:159468, 4:71928,
          5:13716, 8:5328, 48:28190}.
```

The complete rank mass is 4,816,512. The per-call local rank mass minus helper
width mass is 1,856; widening an endpoint increases both by one. Consequently,
a legal control allocation must replace its idle invoice as well. Retaining
the final idle profile while adding the control's terminal children violates
the complete rank-mass identity.

Every one of the 2,664 V45 occurrences lies in a bin with zero idle remainder.
Grant free compaction inside each bin and even arbitrary rearrangement of its
disjoint axes. Restoring any endpoint to rank eight still exceeds capacity.

| Widened endpoints | Overfull bins | Excess width | Whole-occurrence width that must leave those bins |
|---|---:|---:|---:|
| 249 only | 646 | 666 | at least 5,110 |
| 251 only | 650 | 666 | at least 5,142 |
| 265 only | 650 | 666 | at least 5,142 |
| 267 only | 650 | 666 | at least 5,142 |
| 251,265,267 (only 249 remains lowered) | 1,938 | 1,998 | at least 15,354 |
| all four | 2,578 | 2,664 | at least 20,428 |

For example, bin `(owner=2, child=0, port=99)` has capacity 16. It contains
helper index 27 at time 0 with width 7 and helper index 177 at time 4 with width 9.
Widening original helper251 makes the required width 17. The result contains
an explicit witness and a digest of every witness for each of the sixteen
subsets; `--witnesses` can emit them all.

For any capacity-preserving reassignment, each overfull source bin must lose
at least one of its original whole helper occurrences. In these actual bins
the excess is at most two and every occupant is wider than the excess, so the
minimum total width deleted from a bin is its shortest new occupant width.
Summing those minima gives the last column. The bound is sharp in the
relaxation that permits deletion into a free sink. It does not construct a
legal relocation, price movement, or allow required occurrences to disappear.

## Why no repacking rescues the controls at the source saving

Use the exact claimed complex saving

```text
a = 1729033982646513517717 / 1000000000000000000000000.
```

Write `t_r = r^(1-a)`, with `t_0=0`. There are, per replica, 672 bins of capacity 8
and 448 each of capacities 16, 32 and 48. The local word has nine invocations per
replica and width inventory `{4:26,5:2,6:16,7:52,8:99,9:213}` per invocation.
Its complete normalized moment is the per-replica tariff sum divided by
`896*t_73`.

For a capacity-c bin containing n_w helpers of width w, the idle tariff is
`t_(c-sum(w*n_w))`. Define helper potentials

```text
p9 = (t3 - t48)/5       p8 = (3*p9 - t5)/4
p7 = 2*p8 - p9          p6 = 3*p8 - 2*p9
p5 = -t5               p4 = t1 + 4*p8 - 3*p9
```

and bin potentials

```text
alpha8 = -p8, alpha16 = -2*p8, alpha32 = -4*p8, alpha48 = t48.
```

These solve the ten equalities of the retained fractional basis. The checker
independently enumerates **all 2,551 patterns** over widths 4 through 9 in the
four capacities and verifies

```text
alpha_c + sum(n_w*p_w) <= t_(c-sum(w*n_w)).
```

Twelve patterns are symbolically tight. Every other inequality has a strictly
positive rational lower bound. Summing these inequalities proves a lower bound
for the entire idle bill, including fractional mixtures and allocations that
ignore chronology. Adding every local child gives a lower bound for the
complete recursive invoice, not only its idle component.
Explicitly, for bin counts `B_c`, width inventory `I_w` per call and local
profile `L_r` per call, the lower bill per replica is

```text
sum_c B_c*alpha_c + 9*sum_w I_w*p_w + 9*sum_r L_r*t_r.
```

The checker derives `B_c` from all source bins and independently binds the
source fractional basis to these bin counts and to `9*I_w`.

Widening one endpoint changes that bound per invocation by

```text
t1 + p8 - p7 = (20*t1 + t3 + 5*t5 - t48)/20.
```

This direction is strictly positive for every `a>0`: the positive ranks 1, 3, 5
have total rank mass 48, and each has `r^(-a) > 48^(-a)`. The dual feasibility
and the following numerical separations are certified at the stated source
saving; no claim of dual optimality over every saving is needed.

| Widened endpoint count | Certified lower bound on complete moment, rounded downward |
|---:|---:|
| 1 | 1.000001693386 |
| 2 | 1.000003391832 |
| 3 | 1.000005090277 |
| 4 | 1.000006788723 |

The baseline fractional bound has headroom at this saving, and the **actual**
complete baseline profile independently satisfies the strict moment inequality.
Thus rejecting the controls is not caused by testing above the joint word's
own accepted numeric endpoint. No numerical root search or additional endpoint
digits are supplied.

`dual.py` uses integer arithmetic only. Successive floor/ceiling integer square
roots enclose `r^(1/2^j)` on a 256-bit grid. The first 128 binary exponent bits
of a give a lower exponent; one last root bounds the omitted tail. Outward
rounded products enclose `r^a`, and division gives bounds on `r^(1-a)`.
Rational linear combinations then enclose every dual slack and moment margin.
All full rational bounds are retained in [RESULT.json](RESULT.json).

## Physical ledger and remaining obligations

The nominal stock arithmetic is preserved exactly:

```text
66,304 live families + 408 helper names + 8 centres
+ 91 private buffers + 2 coefficient families = 66,813.
```

The checker binds the 91 private names to the actual cleanup operand inventory
and preserves all 5,207 cleanup operations per provider. This is namespace and
invoice accounting; private zero-return and physical reuse are separate
obligations. No scalar, wrapper, movement, prefix or precision charge is
removed. Unpriced costs are not assumed to vanish: the packing relaxation
rejects the controls already, before additional physical implementation costs.

The scientific scope stops at the fixed whole-helper capacity model. Changed
words, partner frames, helper splitting/coding, capacity pools, consumer
contracts or local rank profiles are outside it. Native phases and full warp
semantics, dirty-input operator identities, complete ownership/backing and
movement, physical scalar implementations, prefix/precision/tape, outer release
and all-size/compiler implications are not checked. Both supplier caps and the
selected exponent remain unmodified; no new bit-side cap or outer transfer is
asserted. Failure of the complex budget is sufficient for this control test.

## Reproduce

Python 3.12, standard library only, no network or solver:

```sh
python3 -B scripts/research_package.py --package research/rank7-final-fill-controls
```

The verifier prints

```text
PASS_RANK7_FINAL_FILL_CONTROLS cases=16 rejected_controls=15 roles=271728 bins=149184 packing_patterns=2551
```

The registered hook also runs thirteen behavioral groups. They include an
explicit-point-set frame oracle, algebraic square/cube bounds for the interval
engine, a separate pattern enumerator, all-subset axis-spill counts, exhaustive
small deletion subsets, and semantic rejection of missing/duplicate roles,
family conflicts, unavailable windows, overlapping/noncompact slices, omitted
source bins, missing private names, unpaid children, an infeasible dual and an
omitted pattern. An optimized Git-free export passes, and a changed source
byte is rejected before decoding. Checks use exceptions and survive `-O`.

`verify.py --emit` prints the deterministic result. `verify.py --witnesses
WITNESSES.json` exclusively creates the optional full witness file. Default
verification does not write repository artifacts. The full result requires
about five seconds locally; behavioral controls take about twelve seconds.

## Open next questions

The two questions in [TASK.json](TASK.json) distinguish original stage-one
attribution from supplier admission. A matched complete comparison of the
original parent/joint/single words needs separately legal allocations and all
charges; these final-word controls do not supply it. A physical admission audit
should join the exact final fill to the native/private evidence and choose one
remaining consumer cost. Another lowering or packing search is not started.

## Predecessor credit

Marius-Paul Dumitrean (mdumitrean) supplied PR2979's construction,
PR2942 parent words, final allocation and fractional basis. Nick Petalas supplied
PR2993's independent frame audit and PR3014's old-assignment obstruction and
handoff. Ross Richardson supplied PR2987's independent chronological packing
analysis. Jeremy Kothe supplied the frame/cleanup conventions and rewrite
lineage; Mason Hale supplied PR2917's T74 call order and dispatch and, with
Jeremy Diviney, the paired-extraction chain.
Credit the retained V45 price/inventory checks by jwr (James Reed; PR3112 and
PR3119) and Gonzalo Mier's V45 profile audit (PR3079) as complementary evidence.
Retain Yiyang Lu's allocation lineage, Tekalign's source-window/owner conventions,
Dugongue's packing and owner-engine lineage (PR2863, PR2839), icekylinx, Sagar
Thakrar, themilkman216 and the geometry/native/owner contributors credited by
the immutable source package. The earlier native endpoint audits, Nick Petalas's
PR3006 and PR3008 and ToikY's PR3038, are credited as complementary evidence,
not imported implementations or newly checked here.
