# Capacity-tagged realization of the sharp T=29 profile

All statements concern the fixed U8 whole-helper family of PR795/PR890/PR942
and the arithmetic relaxation of PR992. Nothing here concerns chronology,
owner geometry, the physical schedule, the controller invoice or kappa.

## Setting

Per replica there are 672 bins of capacity 8 and 448 bins of each capacity
16, 32 and 48, and nine calls supply 720, 288, 486, 1098 and 1944 whole helpers
of widths 4, 5, 7, 8 and 9. At `T=29` the quotas are

```
capacity:  8      16     32     48
bins:      19488  12992  12992  12992      (58464 bins)
width:     4      5      7      8      9
helpers:   20880  8352   14094  31842  56376
```

Total capacity is `1403136`, total helper width is `986058`, so the residual
mass is `417078 = 14382*29`. PR992's sharp profile is

```
n = {0:49770, 1:4, 2:1, 48:8689},
```

which has 58464 bins and mass `4 + 2 + 48*8689 = 417078`.

A *legal pattern* is a capacity tag together with a multiset of whole helper
widths of total width at most that capacity; its remainder is the unused
capacity. There are 1163 legal patterns. With the inherited prices
`(-1,-20,-8,-2,4)` for widths `(4,5,7,8,9)` and bonuses `(2,4,8,-13)` for
capacities `(8,16,32,48)`, `u(r)` is the largest bonus plus helper price among
legal patterns of remainder `r`; in particular `u(0)=0`, `u(1)=19`, `u(2)=13`
and `u(48)=-13`.

**Question (hypothesis q_b6cf2a2ce15a43ed:e10).** Do nonnegative integer
counts of legal patterns exist whose capacity tags meet the four quotas, whose
widths meet the five demands, and whose remainders give exactly `n`,
including all 49770 rank-zero bins?

## Lemma 1 (zero slack forces tight bins)

For any realization, the sum of all bin prices is fixed by the inventory:

```
sum_c quota_c * bonus_c + sum_w demand_w * price_w = 29*(896 - 4788) = -112868.
```

Each bin of remainder `r` has price at most `u(r)`, so the sum is at most
`sum_r n_r u(r) = 4*19 + 13 - 13*8689 = -112868`. Equality of the two sums
forces every bin to attain `u(r)`. The checker verifies both totals.

## Lemma 2 (forced structure)

Enumerating the tight patterns of the four remainder classes present in `n`:

- rank 48: only the empty capacity-48 bin;
- rank 1: only `32:{9,9,9,4}`;
- rank 2: only `32:{9,9,8,4}` and `32:{9,9,4,4,4}`;
- rank 0: `8:{8}`, `8:{4,4}`; `16:{8,8}`, `16:{8,4,4}`, `16:{4,4,4,4}`,
  `16:{9,7}`; `32:{8,8,8,8}`, `32:{8,8,8,4,4}`, `32:{8,8,4,4,4,4}`,
  `32:{8,4,4,4,4,4,4}`, `32:{4^8}`, `32:{9,8,8,7}`, `32:{9,8,7,4,4}`,
  `32:{9,7,4,4,4,4}`, `32:{9,9,7,7}`, `32:{9,9,9,5}`; `48:{9,9,9,9,8,4}`,
  `48:{9,9,9,9,4,4,4}`.

Consequences, each checked by the program:

1. The only tight pattern containing a width-five helper is `32:{9,9,9,5}`, so
   every realization has exactly 8352 such bins.
2. The 12992 capacity-48 bins split into 8689 empty bins and 4303 full bins,
   and each full tight capacity-48 pattern holds four nines: 17212 nines.
3. With the 25056 nines of item 1 and the 14 nines of the rank-1 and rank-2
   bins, exactly `56376 - 17212 - 25056 - 14 = 14094` nines remain, which
   equals the width-seven demand. Every remaining tight rank-zero pattern
   pairs each nine with exactly one seven, so the width-nine demand is implied
   by the width-seven demand.
4. Sevens live in `16:{9,7}` (one each) or in capacity-32 tight patterns (at
   most two each). After items 1 and the rank-1/rank-2 bins, 4635 capacity-32
   bins remain, so at least `14094 - 2*4635 = 4824` and at most 12992
   capacity-16 bins are `16:{9,7}` in every realization. This is a necessary
   range only; nothing is claimed about which of its values are attained.

## Proposition (a compact witness exists)

The following ten pattern counts realize `n` exactly:

```
 8:{8}            11202      32:{9,9,9,5}       8352
 8:{4,4}           8286      32:{9,9,9,4}          4   (rank 1)
16:{9,7}          12992      32:{9,9,8,4}          1   (rank 2)
                             32:{9,9,7,7}        551
                             32:{8,8,8,8}       4084
48:{}              8689      48:{9,9,9,9,8,4}   4303
```

Quotas: `11202+8286 = 19488`; `12992`; `8352+4+1+551+4084 = 12992`;
`8689+4303 = 12992`. Demands: fours `2*8286 + 4 + 1 + 4303 = 20880`; fives
`8352`; sevens `12992 + 2*551 = 14094`; eights `11202 + 1 + 4*4084 + 4303 =
31842`; nines `12992 + 3*8352 + 12 + 2 + 2*551 + 4*4303 = 56376`. Remainders:
`8689` of rank 48, `4` of rank 1, `1` of rank 2 and `58464 - 8694 = 49770` of
rank 0. Every pattern is tight, so the total price is `-112868`.

The witness is reconstructed in closed form by `verify.py` from three explicit
choices (all capacity-16 bins are `16:{9,7}`, the free capacity-32 bins are
`32:{8,8,8,8}`, the full capacity-48 bins are `48:{9,9,9,9,8,4}`); the
remaining counts are then forced by the quotas and demands.

## Second realization (nonuniqueness)

The reviewer's blind hand construction (REVIEW.md) is a second realization,
transcribed into `verify.py` as data and checked by the same exact census:

```
 8:{8}            11203      32:{9,9,9,5}       8352
 8:{4,4}           8285      32:{9,9,9,4}          4   (rank 1)
16:{9,7}           4824      32:{9,9,4,4,4}        1   (rank 2)
16:{8,8}           8168      32:{9,9,7,7}       4635
48:{}              8689      48:{9,9,9,9,8,4}   4303
```

It differs from the witness above in eight pattern counts, including the
rank-2 pattern. Two distinct checked realizations establish that the
realization is not unique; nothing is claimed about any other count vector.

## Conclusion and limits

PR992's sharp aggregate profile passes the capacity-tagged whole-helper
pattern constraint that its relaxation omits: there is no obstruction at this
level, and the realization is not unique, as the two checked realizations
show. Lemma 2, item 4, is a necessary range only. The result does not
construct owner windows, charts or a controller for `T=29`, does not bound any
supplier outside the fixed U8 family, and changes no kappa.
