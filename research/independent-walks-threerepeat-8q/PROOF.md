# Three-repeat partitioned walks cannot cover at Q=8

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It names one freestanding `#840`-style priced
readout alphabet at eight queries beyond same-walk / dirty-shadow / partitioned
dual / one-repeat / two-repeat / shared-dirt: the **three-repeat** (excess-3)
companion of partitioned independent duals. It answers preferred next19 and
open question 1 of pending `cursor/shared-dirt-walks-8q-60b9@fc3a2cb3`.

No new kappa is claimed. Leave-alone packages through #2861 / #2860 / #2858 /
#2851 are not edited. Pending shared-dirt tip is not edited or competed.
Soft-overlap with shared-dirt is avoided: this package stays on the
independent-dirt excess axis and does not couple the dirt coefficient.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n≥2` is an open slot list starting at
`0` whose closed completion has only nonzero edges.

The **excess** of a walk is `Σ (count(ℓ)−1)` over nonzero labels. One-repeat
has excess `1`. Two-repeat has excess `2`. **Three-repeat** means excess
exactly `3`.

A **three-repeat partitioned dual** of total query count `Q = 8` is a pair of
valid restored walks of lengths `(n_0,n_1)` with `n_0+n_1=8` and `n_0,n_1≥2`,
where at least one side is three-repeat, with independent dirt and dual
even-parity cost

```text
R = Σ_{m=1}^{31} min_α ( e0[α] + e1[α ⊕ m] ).
```

Up to swap the only partitions are `(2,6)`, `(3,5)`, and `(4,4)`.

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

## Fixture A: partition `(2,6)`

Short walk `(0,σ)`. Long walk of length 6 with excess 3 on five nonzero slots
forces exactly two distinct nonzero labels. Restoring shapes:

| Shape | Restores? | Count |
|---|---|---:|
| `{d:3,e:2}` | yes | **930** |
| `{d:4,o}` | no | 0 |
| Total valid | — | **930** |

**Lemma (span ≤ 4).** Two labels span a subspace of rank ≤ 2, hence size ≤ 4.

**Lemma (coset union ≤ 8).** Pairing with short `(0,σ)` reaches at most
`span ∪ (span ⊕ σ)`, size ≤ 8 < 32. Dual covering is therefore impossible.

**Census.** Exact covering count **0** (machine-checked on all `930·31`
pairs). Shape `{4,1}` is exhaustively checked never to restore.

## Fixture B: partition `(3,5)`

Short walk: distinct-label length-3 (`C(31,2)=465` even tables). Long walk:
excess 3 on four nonzero slots forces shape `{d:4}`.

Any ordering of `(0,d,d,d,d)` has an adjacent zero-XOR edge on the closed walk.

**Census.** Valid three-repeat length-5 walks: **0**. Covering count **0**.

## Fixture C: partition `(4,4)`

Three nonzero slots admit at most excess `2` (shape `{d:3}`). Excess `3` is
impossible on length-4.

**Census.** Valid three-repeat length-4 walks: **0**. Covering count **0**.

## Tariff consequence

No covering three-repeat partitioned dual exists at `Q=8`. There is therefore
no dirt-legal `R` and no complete-call tariff in this alphabet that can undercut
the six-query endpoint `436`. By comparison:

| Alphabet | Covering min R | Tariff floor (X=0) | Undercuts 436? |
|---|---:|---:|---|
| Distinct partitioned (`#2851`) | 92 | 488 | no |
| One-repeat partitioned (pending) | 112 | 528 | no |
| Two-repeat partitioned (pending) | — (covering 0) | — | no |
| Shared-dirt partitioned (pending) | 82 | 468 | no |
| **Three-repeat partitioned (this)** | **— (covering 0)** | **—** | **no** |

## Scope limits

- Fixes the **three-repeat** (excess-3) partitioned independent-walk interface at
  total `Q=8`. Same-walk, dirty-shadow, distinct partitioned, one-repeat,
  two-repeat, and shared-dirt leave-alones / pending tips are outside and not
  edited.
- Soft-overlap with pending shared-dirt is avoided: this package does not couple
  dirt coefficients (R-side shared-dirt) and stays on the independent excess
  axis.
- Transfer-coupled dual/shapes, shared-XOR, and host screens remain deferred
  soft-overlaps and are not opened.
- No new kappa and no multiplication theorem are claimed.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436, `(b,a,x)=(38,2,2)` | — |
| #2851 | Partitioned independent dual at `Q=8` has `R≥92` | — |
| pending onerepeat / tworepeat | Excess-1 / excess-2 companions | — |
| pending shared-dirt | Shared-dirt `R≥82`; OQ1 asks for fifth alphabet | — |
| **This** | — | **Three-repeat dual at `Q=8` has covering 0 on all shapes; cannot undercut 436; answers next19 / shared-dirt OQ1 without competing with shared-dirt** |
