# Partitioned independent walks cannot undercut tariff 436 at Q=8

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It is a freestanding `#840`-style priced alphabet at
eight queries: two restored walks with **distinct slot lists**, independent
dirt, and dual even-parity readout. It answers open question 2 of
[#2840](https://github.com/CrocSwap/integer-mult-bounds/pull/2840) (and the
matching handoff on pending transfer-coupled-onerepeat): whether any other
priced readout alphabet undercuts the six-query endpoint tariff `436` at `Q=8`
after a complete dirty bill.

No new kappa is claimed. Leave-alone packages through #2840 are not edited.
Pending `cursor/transfer-coupled-onerepeat-7q-60b9` is not edited or competed.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n` is an open slot list
`(s_0,…,s_{n-1})` with `s_0 = 0` whose closed completion `(s_0,…,s_{n-1},0)`
has only nonzero edges. Length-1 lists are illegal: the closed return is the
zero edge `(0,0)`.

A **partitioned independent dual** of total query count `Q = 8` is a pair of
valid restored walks of lengths `(n_0,n_1)` with `n_0 + n_1 = 8` and
`n_0,n_1 ≥ 2`. Up to swap the only cases are `(2,6)`, `(3,5)`, and `(4,4)`.
Each walk carries its own dirt coefficient. For mask `m` the dual even-parity
cost is

```text
min_a (e0[a] + e1[a ⊕ m]),
```

where `e_i` is the even-subset table of walk `i` (with `e_i[0] = 0`).

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

## Length-1 exclusion

A length-1 list `(0,)` closes to `(0,0)`. That edge has XOR `0`, so it is not a
restored walk. Consequently `(1,7)` and `(7,1)` are not legal partitions of a
`Q = 8` dual schedule.

## Fixture A: partition `(2,6)`

Short walk `(0,σ)` has even table `e0[0]=0`, `e0[σ]=2`. Long walk
`(0,b_1,…,b_5)` with distinct nonzero labels. Dual cost collapses to

```text
R = Σ_{m=1}^{31} min( e1[m],  2 + e1[m ⊕ σ] ).
```

**Lemma (rank-4 outside identity).** When the long span `V` has rank `4` and
`σ ∉ V`, masks in `V` pay `e1` and masks in the complementary coset pay
`2 + e1(· ⊕ σ)`, so

```text
R = 2 · Σ_{v ∈ V \ {0}} e1[v] + 32.
```

On the champion `((0,16),(0,1,2,4,8,15))` one has `Σ e1 = 30`, hence
`R = 2·30 + 32 = 92`. The identity is machine-checked on that witness.

**Census.** Distinct-label pairs: `31 · C(31,5) = 5267241` candidates; covering
count `3916416`; attainable `R ∈ {92,96,104}` with histogram
`1416576 / 1249920 / 1249920`. Minimum `R = 92`.

Champion path `X = 16`, tariff `520`. The `X = 0` figure `488` is only the
abstract lower bound from `R = 92`.

## Fixture B: partition `(3,5)`

**Census.** Distinct-label pairs: `C(31,2)·C(31,4) = 14631225` candidates;
covering count `10416000`; attainable `R ∈ {98,104}` with histogram
`3124800 / 7291200`. Minimum `R = 98` (machine-checked dual `min_a` on every
covering pair).

Champion: `((0,1,2), (0,4,8,13,16))` with path `X = 12`, tariff `520`.

## Fixture C: partition `(4,4)`

**Census.** Ordered distinct-label pairs: `C(31,3)² = 20205025` candidates;
covering count `14165760`; attainable `R ∈ {100,104,112}` with histogram
`3610880 / 9999360 / 555520`. Minimum `R = 100`.

Champion: `((0,1,2,4), (0,7,8,16))` with path `X = 16`, tariff `536`.

## Tariff consequence

Every covering partitioned dual at `Q = 8` has `R ≥ 92`, attained only on
`(2,6)`. Even at `X = 0`,

```text
38·8 + 2·92 + 2·0 = 488 > 436.
```

Positive path-`X` only increases the bill. Partitioned independent walks at
eight queries therefore cannot undercut the six-query endpoint under the PR1898
abstract tariff. By comparison, a single same-walk even-subset schedule can
reach `R = 74` ([#2677](https://github.com/CrocSwap/integer-mult-bounds/pull/2677)
/ dirty-shadow collapse [#2840](https://github.com/CrocSwap/integer-mult-bounds/pull/2840));
splitting the query budget across two independent dirt ports forces a worse
readout invoice (`R ≥ 92`).

## Scope limits

- Fixes the **partitioned** independent-walk interface at total `Q = 8` with
  distinct nonzero labels within each walk. Transfer-coupled schedules,
  transfer-coupled onerepeat, dirty-shadow, and same-walk multi-connector
  leave-alones are outside and not edited.
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Host screens are deferred.
- Soft-overlap transfer-coupled-dual/shapes vs #2817/#2836 is not opened.
- Leave-alone through #2840 (including #2836, #2817, #2779, #2764, #2761,
  #2715, #2687, #2686, #2677, #2643, #2593, #2487) is not edited.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436, `(b,a,x)=(38,2,2)` | — |
| #2677 | Distinct-slot `R≥74` at single-walk `Q=8` | — |
| #2779 | Partitioned dual walks at `Q=7` have exact `R=112` | — |
| #2840 | Dirty-shadow at `Q=8` matches even-subset; OQ2 | — |
| **This** | — | **Partitioned dual walks at `Q=8` have `R≥92` (min on `(2,6)`); tariff floor `488>436`** |
