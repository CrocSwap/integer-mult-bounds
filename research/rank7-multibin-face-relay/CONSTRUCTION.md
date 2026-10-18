# One four-bin relay reaches k939

The exact T37 owner allocation below realizes `k=939` in the PR2979 saturated
face family, starting from PR3010's attained `k=940` fill. Two same-width
exchanges expose a legal inverse face swap on two bins that did not form a
legal direct pair in the starting fill. All capacity-48 bins remain unchanged.
The complete paid child profile and its cost for every rank tariff are
unchanged. This is a finite allocation construction, with no new kappa claim.

The reproducible standard-library implementation is `constructor.py`.
`candidate/JOURNAL.json` records both the six distinct endpoint owner changes
and a three-stage sequence with eight assignment transfers. These are changes
to the allocation, not eight extra runtime arithmetic instructions.

## Frozen premises and predecessor credit

The native words, actual ordered provider registry, source chronology and face
patterns are Marius-Paul Dumitrean's PR2979, pinned at
`be191346391661f4d35fc0d1508d0a6029572576`. The starting fill is PR3010 at
`87ca15cf005ab232ca0104ec5137014ac754f487`, which supplies the exact frozen,
disjoint, direct-pair bound and attained `k=940` witness. PR2987 at
`02c3047a1e78e6e35e7573c12434ba26f6f9bd96` supplied the necessary bound
`k>=473`; that bound is inherited, not proved again here. The refreshed
experiment base is `d8e0f83f00191df62174b641e9fff055c357f641`.
`SOURCES.json` binds every included source and start file by SHA-256 and exact
source commit. Source notices and credits are retained.

The chronological owner/flow lineage includes Yiyang Lu / PR2857, Mason Hale /
PR2917, Dugongue and Tekalign; Dumitrean's PR2856 is a prior concrete multi-bin
vacancy-relay example. The present four-bin witness and deterministic replay
were prepared with substantial OpenAI GPT-6.1 Sol assistance. Historical source
results retain their original native, restoration and execution premises.

There are 333 calls at T37, with 408 actual ordered helper widths per call.
The source provider registry, rather than a historical width multiset in the
vendor plan, binds each helper index. Both actual providers have inventory
`{4:26,5:2,6:16,7:52,8:99,9:213}`. Every actual `(time,helper)` identity is
retained. The chronological order, provider dispatch and all source capacities
are fixed. Each owner/child has 112 ports. A physical family is
`(owner, PLAN.pairs[child], PLAN.sides[child], port)`.

A role assigned to a pending bin must satisfy its strict source window
`L<t<=U`, avoid the call's active data family and use its physical family at
most once in that call. Integral masks must be disjoint and form a compact
prefix. Event replay reconstructs the windows from the frozen template and
order; distinct bins are not presumed to be distinct physical families.

## Literal local construction

Write a bin as `(owner,child,port)` and list an occupant as `width@time`.
The four source bins, all from the attained `k=940` fill, are:

| Name | Bin | Capacity | Window | Initial occupants |
| --- | --- | ---: | --- | --- |
| C | `(23,16,0)` | 16 | `(265,306]` | `8@268, 8@269` |
| D | `(17,14,0)` | 32 | `(158,281]` | `7@224, 7@227, 9@259, 9@265` |
| R7 | `(16,17,111)` | 16 | `(221,276]` | `9@260, 7@271` |
| R9 | `(21,15,111)` | 32 | `(190,298]` | `4@253, 9@266, 9@272, 9@288` |

C and D are not a legal direct inverse pair in this starting fill: no D
width-7 role lies in C's window, and neither D width-9 role does. In
particular, `t=265` is the excluded lower endpoint, so it cannot be used in C.

First exchange the two actual width-7 roles `(224,337)` in D and `(271,342)`
in R7. Time 224 is in R7's `(221,276]` window and time 271 is in D's
`(158,281]` window. D's times become `227,259,265,271`, all distinct; R7's
become `224,260`, also distinct. Both patterns and all residual ranks stay fixed.

Next exchange the actual width-9 roles `(259,166)` in D and `(266,64)` in
R9. Both receiving windows admit the incoming role. D's times become
`227,265,266,271`; R9's become `253,259,272,288`. They remain distinct, and
again the patterns and residual ranks stay fixed.

Now perform one inverse face swap. Move C's actual width-8 roles `(268,399)`
and `(269,87)` into D. Move the actual width-7 role `(271,342)` and width-9
role `(266,64)` now in D into C. All incoming times satisfy the strict
receiving windows. The final occupied masks, after ordering by `(time,helper)`
within each affected bin, are:

| Bin | Actual role `(time,helper)` | Width | Mask |
| --- | --- | ---: | --- |
| C | `(266,64)` | 9 | `[0,9)` |
| C | `(271,342)` | 7 | `[9,16)` |
| D | `(227,336)` | 7 | `[0,7)` |
| D | `(265,51)` | 9 | `[7,16)` |
| D | `(268,399)` | 8 | `[16,24)` |
| D | `(269,87)` | 8 | `[24,32)` |
| R7 | `(224,337)` | 7 | `[0,7)` |
| R7 | `(260,141)` | 9 | `[7,16)` |
| R9 | `(253,53)` | 4 | `[0,4)` |
| R9 | `(259,166)` | 9 | `[4,13)` |
| R9 | `(272,168)` | 9 | `[13,22)` |
| R9 | `(288,57)` | 9 | `[22,31)` |

Thus the only pattern changes are

```text
[8,8]@16 + [7,7,9,9]@32 -> [7,9]@16 + [7,8,8,9]@32.
```

R7 retains `[7,9]@16`; R9 retains `[4,9,9,9]@32` and residual 1. C, D and
R7 are saturated before and after. All masks in unaffected bins are unchanged.
The four affected families have different owners. Potential interference with
another child of the same family is checked against the complete fill; source
pending windows for one physical family are disjoint, so merely changing the
child number never licenses a same-call collision.

The final four changing multiplicities are:

| Capacity | Pattern | Count |
| --- | --- | ---: |
| 16 | `[8,8]` | 1,262 |
| 16 | `[7,9]` | 15,314 |
| 32 | `[7,8,8,9]` | 124 |
| 32 | `[7,7,9,9]` | 939 |

Every other multiplicity remains fixed. This passes below PR3010's `k=940`
minimum for its frozen, disjoint, direct-pair model by changing actual roles
through retained-pattern relay bins. It does not contradict that model's exact
matching/cover certificate and does not claim a bound for general allocations.

## Complete paid cost

The source local per-call profile remains
`{1:2445,2:706,3:232,4:108,5:18,8:8}`. The unchanged residual histogram is
`{1:8655,3:2478,5:864,48:14095}`. With all 333 local calls, the complete paid
T37 profile is therefore

```text
{1:822840,2:235098,3:79734,4:35964,5:6858,8:2664,48:14095}.
```

For every inherited rank tariff `H`, the full charged child cost is exactly

```text
822840 H(1) + 235098 H(2) + 79734 H(3) + 35964 H(4)
+ 6858 H(5) + 2664 H(8) + 14095 H(48).
```

The delta against the starting `k=940` allocation is zero for every `H`.
There is no strict recursive moment improvement asserted. The complete rank
mass is 2,408,256. The inherited conditional stock expression remains
`896*37 + 408 helpers + 8 centres + 91 private buffers + 2 guards = 33661`.
It is not a new physical-storage or execution proof. Nothing is removed from
helper restoration, fixed native children, source access or the private buffers.

The standard two-copy source embedding is
`(stage,replica,time)->(stage,replica+37*b,2*time+b)`, `b in {0,1}`.
It has T74, 271,728 roles, doubled paid profile and conditional stock
`896*74+408+8+91+2=66813`. T74 literal verification must check this embedding
against the frozen full source order and dispatch; it is not inferred solely
from doubling an aggregate histogram.

## Reproduction and proof level

Replay into the default `candidate/` directory, which must not already exist:

```text
python3 -B research/rank7-multibin-face-relay/constructor.py
```

Use `--out /absolute/fresh/directory` to reproduce without overwriting the
retained candidate. The constructor authenticates the pinned bytes, preserves
the exact source helpers, checks full geometry at the start and after each of
the three stages, reconstructs the full face mix and complete profile, and
emits deterministic standard-library JSON/gzip files. The search is not needed
for reproduction and has no optional solver dependency. One bounded Python
vacancy-path attempt found this witness at its first tested C/D choice; no
optimization beyond `k=939` was attempted.

The sequential journal's `stages` array has three records. Each contains
`transfers`, with actual role identity, width and complete before/after rows,
and `repacked_stationary`, with every offset-only change for that stage.
Applying both lists simultaneously reconstructs each full intermediate fill:
its face parameters are respectively `940,940,939`. The top-level `moves` are
the six distinct endpoint owner changes, while top-level
`repacked_stationary` lists endpoint offset-only changes. `bin_states` records
the complete four-bin endpoints and source windows. This distinguishes eight
staged assignment transfers from six distinct helpers whose final owners change.

This is a finite exact construction and an explicit local mathematical proof.
Full literal verification is separate from the generator's checks. There is
no formal-kernel proof and no new native-arithmetic, arbitrary dirty-input,
restoration, phase/frame, precision, backing-storage, source-bound norm or
all-size multiplication theorem here. Those remain inherited source premises.
The previously supplied `940<=k<=1063` constructions together with this one
supply `939<=k<=1063` in this fixed finite family; the interval
`473<=k<=938` remains unresolved by this result.
