# Transfer-coupled (5,1,1) duals cannot undercut tariff 436 at Q=7

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
the **transfer-coupled** open question left by partitioned independent walks:
can a shared prefix, priced transfer `C≥1`, and divergent suffixes undercut the
six-query endpoint tariff `436` at total `Q = 7` after a complete dirty bill?

The claim is restricted to shape `(p,a,b) = (5,1,1)` (maximal sharing / longest
walks). No new kappa is claimed. Leave-alone packages through #2764 / #2761 are
not edited. Pending independent-walks / dirty-parity / multi-connector fixtures
are not competed with on their own claims.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **transfer-coupled schedule** of shape `(p,a,b)` with
`p+a+b = 7` consists of:

1. a shared restored **prefix** of length `p` starting at `0`;
2. a priced **transfer** of cost `C ≥ 1` forking the connector state;
3. two divergent **suffixes** of lengths `a` and `b`.

The two walks are `prefix∥suffix_a` and `prefix∥suffix_b`. Shared prefix queries
are counted once, so the query bill is `Q = p+a+b`. Each walk carries independent
dirt, so dual even-parity readout costs

```text
R = Σ_{m=1}^{31} min_a (e0[a] + e1[a ⊕ m]).
```

**Fair shared-prefix XOR billing** charges prefix edges once, adds the transfer
`C`, then charges each tip chain `(prefix_end → tip → 0)` separately. The
abstract complete-call tariff at `(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X` with
`C` folded into the fair-`X` bill.

## Why `(5,1,1)`

Up to swap, shapes with `p≥1` and `a,b≥1` are the fifteen triples listed in the
independent-walks OQ. Shape `(5,1,1)` maximises the shared prefix and produces
two length-6 walks at `Q=7` — the most threatening dual-row configuration after
partitioned walks collapsed at `R=112`. Spot samples of `(4,1,2)`, `(3,2,2)` and
`(3,1,3)` observe covering minima `R≥86`; already `R+X≥86>85` forbids undercutting
`436` at `Q=7`, but those shapes are not fully censused here.

## Undercut threshold

At `Q=7`,

```text
38·7 + 2(R+X) < 436  ⟺  R+X < 85.
```

Any covering schedule with `R≥86` is therefore blocked even at `X=0`. The only
remaining threat is `R≤84` with very small fair `X`.

## Census of distinct-label `(5,1,1)`

Prefix nonzero labels form a 4-set `P ⊂ {1,…,31}`; tips `a≠b` lie outside `P`.
Even-subset tables depend only on the slot **set**, so the dual `R` census is
over unordered tip pairs. Covering count:

```text
covering = 8 749 440,
attainable R = {84, 88, 90},
histogram: 84 ↦ 1 458 240,  88 ↦ 2 083 200,  90 ↦ 5 208 000.
```

In particular **min `R = 84`**. (Machine-checked dual `min_a`, not a copied
constant; independent checker reproduces the same histogram.)

## Fair-`X` floor on the `R=84` layer

For each `R=84` system, the fair-`X` cost decomposes by path end-point:

```text
X = min_pend ( path_0→P→pend + C + edge(pend,a) + edge(pend,b)
               + edge(a,0) + edge(b,0) ),
```

with `C=1`. Enumerating all `1 458 240` systems yields

```text
min fair X |_{R=84} = 9,
```

attained at prefix `(0,1,3,6,12)` with tips `(8,16)` (and the tip swap). No
`R=84` schedule has fair `X≤8`. Consequently every covering `(5,1,1)` bill
satisfies `R+X ≥ 84+9 = 93 > 85`.

## Tariff consequence

```text
38·7 + 2·84 + 2·9 = 452 > 436.
```

Positive deviations of `R` or `X` only increase the bill. Transfer-coupled
`(5,1,1)` duals therefore cannot undercut the six-query endpoint under the
PR1898 abstract tariff after charging walks, transfer, and dirt.

`C=0` is rejected by the priced-transfer interface (`need(C≥1)`).

## Scope limits

- Fixes transfer-coupled shape `(5,1,1)` with distinct nonzero labels.
  Other `(p,a,b)` triples are out of full census (spot samples only).
- Same-walk multi-connector / priced shadow remain #2761; dirty-parity at
  `Q=8` remains #2764; partitioned independent walks remain their own package.
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Host screens are deferred.
- Leave-alone through #2764 / #2761 (including #2593, #2643, #2677, #2686,
  #2687, #2715, #2761, #2764) is not edited.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436 | — |
| #2643 | `X≥6` at single-walk `Q=7` | — |
| #2686 | Even-subset `R≥82` on one walk | — |
| #2715 | All-subset collapses under dirty-parity | — |
| #2761 | Same-walk dual / dirty shadow stay at `R≥82` | — |
| Independent-walks | Partitioned duals have exact `R=112` | transfer-coupled OQ |
| **This** | — | **`(5,1,1)` transfer-coupled duals have min `R=84`, min fair `X=9` at that layer; tariff floor `452>436`** |
