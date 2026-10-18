# The chronological width-7 cut on the fixed packing face

This checks the allocation mechanism in Marius-Paul Dumitrean's PR [2979](https://github.com/CrocSwap/integer-mult-bounds/pull/2979), frozen at
`be191346391661f4d35fc0d1508d0a6029572576`. The integer mix, chronology and literal
fill are predecessor artifacts, not new constructions here. The new result is
an independent derivation of the cut, its exact consequence for the one-parameter
face, and a check of the literal two-copy realization. It does not claim a new
exponent saving.

The precise conclusion is that **every feasible member of the stated face family
must have `k >= 473`**. Member `k=472` fails the cut by one role. Member `k=473`
passes this necessary cut; no realization of that member is provided. The source
literal realization is member `k=1063`.

## Premises and source chronology

The fixed domain has 37 replicas, nine calls per replica, 408 ordered helpers per
call, and 112 indivisible ports per `(owner replica, child)` bin. Both declared
provider inventories are
`{4:26, 5:2, 6:16, 7:52, 8:99, 9:213}`. The ordered width of each actual helper is
read through the literal provider dispatch; equal inventory counts do not replace
that binding. Derivation of those widths from native entering and exiting frames
is an inherited premise.

Use zero-based time `t` in the literal `PLAN.order`, denoted `O37`, and let
`tau_s(r)` be the position of `(stage s, replica r)` in that order. Each replica's
stage order is increasing. The checker does not reconstruct the order from an
assumed priority: in this source, sorting by `(4*s+r,s,r)` first disagrees at time
14, where that priority puts `(2,0)` and the literal source puts `(0,9)`.

The source recipe identifies the pair touched by each local call. Scan the
`TEMPLATE.execution_schedule` in its written order. A local event updates that
pair's most recent source stage; a bridge updates both its source and destination
pairs. An idle-cover event ends the pending window at its current stage and starts
it strictly after the pair's most recent source event, or at initial time `-1`.
Only children retained in `TEMPLATE.idle_children` are owner bins. Bank and padding
children mentioned by other idle-cover events are excluded. This gives the
following stage endpoints without running the predecessor owner engine:

| Children | Capacity | Legal call times for owner `r` |
|---|---:|---|
| 0, 2 | 16 | `-1 < t <= tau_1(r)` |
| 1, 3 | 8 | `tau_1(r) < t <= tau_2(r)` |
| 4, 6 | 32 | `-1 < t <= tau_3(r)` |
| 5, 7 | 8 | `tau_3(r) < t <= tau_4(r)` |
| 8, 10 | 48 | `-1 < t <= tau_5(r)` |
| 9, 11 | 8 | `tau_5(r) < t <= tau_6(r)` |
| 12, 13 | 48 | `tau_2(r) < t <= tau_8(r)` |
| 14, 15 | 32 | `tau_4(r) < t <= tau_8(r)` |
| 16, 17 | 16 | `tau_6(r) < t <= tau_8(r)` |

All 666 instantiated windows agree exactly with `PLAN.windows`, including every
integer time in each window. Lower endpoints are excluded and upper endpoints
are included. Physical family identity remains
`(owner replica, PLAN.pairs[child], PLAN.sides[child], port)`; changing child IDs
does not necessarily change the physical family.

## The interval cut

For an inclusive interval `I=[a,b]`, a window `(L,U]` meets `I` exactly when
`U >= a` and `L < b`. The pattern restriction used here is that **at most one
width-7 role occupies any capacity-16 bin over that bin's entire pending window**.
This holds for every member of the fixed face below. It is not a general
capacity bound: a different pattern `[7,7]@16` could hold two such roles and lies
outside this argument's domain.

There are `52 |I|` width-7 roles requested in `I`. Every one assigned to capacity
16 needs a different bin whose window meets `I`. Therefore, if `B16(I)` counts
those bins and `R` counts all width-7 slots outside capacity 16 globally,

```text
R >= number of width-7 roles in I outside capacity 16
  >= 52 |I| - B16(I).
```

For `I=[45,332]`, there are 288 calls. For children 0 and 2, the eligible replicas
are exactly `14..36`, giving 23 owner windows for each child; in particular
`tau_1(13)=44` excludes replica 13. For children 16 and 17, all 37 owner windows
meet `I`. Consequently,

```text
B16(I) = 112 (23 + 23 + 37 + 37) = 13,440,
demand = 52 * 288 = 14,976,
R >= 14,976 - 13,440 = 1,536.
```

The checker also exhausts all `333*334/2 = 55,611` nonempty contiguous call
intervals, using these exact source windows. The maximum of
`52 |I| - B16(I)` is 1,536, attained uniquely by `[45,332]`. Thus the bound above is
the strongest global-reserve bound obtained from a single contiguous interval
with this counting rule. This is neither a check of all subsets of calls nor a
sufficient Hall criterion for the full scheduling problem. The count also
relaxes active-family and coordinate restrictions; those cannot invalidate this
necessary lower bound.

## The exact one-parameter family

Undo the source's 1,063 swaps to define member `k=0`. The four changing pattern
counts at member `k` are:

| Capacity | Pattern | Multiplicity |
|---:|---|---:|
| 16 | `[8,8]` | `323+k` |
| 16 | `[7,9]` | `16253-k` |
| 32 | `[7,8,8,9]` | `1063-k` |
| 32 | `[7,7,9,9]` | `k` |

All other pattern counts are exactly the source `T37-FACE-MIX.json` counts. The
covered domain is every integer `0 <= k <= 1063`. All multiplicities remain
nonnegative. Each step implements the source's swap

```text
[7,8,8,9]@32 + [7,9]@16 -> [8,8]@16 + [7,7,9,9]@32.
```

The capacity-16 patterns have at most one width-7 slot, and no unchanged pattern
contains a width-7 slot. Hence the exact total outside capacity 16 is

```text
R(k) = (1063-k) + 2k = 1063+k.
```

The interval cut implies `1063+k >= 1536`, equivalently `k >= 473`. The initial
global-reserve deficit is exactly 473 roles. At `k=472`, the global reserve is
1,535, which is one short. At `k=473`, the global reserve is 1,536. Nothing in
this calculation ensures that all those slots can serve the interval, that the
other widths can be assigned, or that family and mask constraints can be met.

Every changed bin is full both before and after a swap. Thus each step preserves
the counts of each width, each capacity, every idle rank, and the inherited native
calls, bridges, centres and cleanup interface. Its complete paid-profile change
is zero, conditional on that unchanged interface. This is a possible allocation
repair, not a scalar-operation saving promoted to a recursive improvement.

## The literal T74 witness

The literal `ORDER` is exactly the interleaving

```text
O74[2t+b] = (s, r+37b), where O37[t]=(s,r) and b in {0,1}.
```

The provider IDs also project identically in the two copies. For any same-copy
source endpoint with `L >= 0`, its image is `2L+b`; the initial endpoint remains
`-1`. The equivalence
`L < t <= U` iff `2L+b < 2t+b <= 2U+b`, with the initial case checked separately,
proves that the embedding preserves each copy's legal source times.

The checker visits all 271,728 literal rows, checking complete `(call,helper)`
coverage, source windows, at most one helper per physical family per call,
capacity bounds, disjoint integral coordinate masks, and compact pending prefixes.
All owners are in the requesting call's copy. Projecting `time -> time//2` and
`owner -> owner mod 37` gives two identical sets of 135,864 literal rows. The
actual bin patterns equal twice the source `k=1063` mix, including empty bins.

Each copy has 17,316 width-7 roles, with 2,126 outside capacity 16. Within the cut,
12,853 use capacity 16 and 2,123 use other capacities. These are checks of the
existing final witness; they do not construct `k=473`.

From the literal idle ranks and the **declared** provider-local paid profiles,
the checker independently sums the complete source child profile

```text
T74: {1:1645680, 2:470196, 3:159468, 4:71928,
      5:13716, 8:5328, 48:28190}.
```

Equivalently, its conditional charged child cost is
`1645680 H_1 + 470196 H_2 + 159468 H_3 + 71928 H_4 + 13716 H_5 + 5328 H_8 + 28190 H_48`,
for the inherited recursive tariff `H`. Source native arithmetic, arbitrary dirty
input restoration, the derivation of paid local profiles, physical stock, source
access, precision, and outer transfer remain predecessor obligations rather than
newly admitted consequences of this finite check.

## Reproduction and proof level

```sh
python3 research/rank7-chronological-face/independent_hall.py
python3 -O research/rank7-chronological-face/independent_hall.py
```

The importable interface is `verify_hall(package_root=None)`, returning a
JSON-serializable receipt. It uses only the Python standard library and does not
execute or import any predecessor producer, searcher or owner engine. It verifies
the hashes of its eight frozen JSON inputs against `SOURCES.json` and rechecks
them at exit. All checks raise explicit exceptions, so `python3 -O` retains them.
Six controls reject a real width-7 role at its excluded lower endpoint, an
expanded source window, a duplicated same-call physical family, a missing width-7
role, a demand undercount by one, and a changed two-copy interleaving.

The counting inequality and implication `k>=473` are written mathematical proofs
for the stated fixed model. The source extraction, complete interval maximum and
literal geometry are finite exhaustive computations over the pinned artifacts.
There is no formal-kernel proof, no all-parameter allocation theorem, and no claim
that the new boundary member is schedulable.

## Attribution

The source package credits Marius-Paul Dumitrean for its new words and allocation
(with substantial AI assistance from Anthropic Claude), Mason Hale/PR2917 for the
T74 chronology, Jeremy Kothe/PR2833 for the source materializer and inherited
supplier, Yiyang Lu/PR2857 for chronological flow and realization, Dugongue for
the owner-engine lineage, Tekalign for the earlier independent owner checker,
and themilkman216 for the cap-integrality observation. The face swap and source
cut are retained from PR2979; their origin is not reassigned by this independent
check. See the frozen `sources/CREDITS.md` and `sources/NOTICE` for the complete
predecessor credits and license notice. This independent proof and checker were
prepared with GPT-6.1 Sol assistance.
