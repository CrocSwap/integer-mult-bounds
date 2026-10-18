# Shared-dirt partitioned duals undercut independent floors but not tariff 436 at Q=8

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It names one freestanding `#840`-style priced
readout alphabet at eight queries beyond same-walk / dirty-shadow / partitioned
dual / one-repeat / two-repeat: the **shared-dirt** (single coefficient / joint
even live-read parity) dual on distinct partitioned restored walks. It answers
preferred next18 and open questions 1–2 of pending
`cursor/independent-walks-tworepeat-8q-60b9`.

No new kappa is claimed. Leave-alone packages through #2858 / #2851 are not
edited. Pending onerepeat / tworepeat tips are not edited or competed.

## Soft-overlap vs deferred shared-XOR

Deferred soft-overlap notes (e.g. #2851 / #2840) reserve **shared non-path XOR
schedules** (X-side) against [#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643).
This package couples only the **R-side dirt coefficient**: both walks share one
dirt register so live-read parity is joint. Path-`X` on each restored walk and
all non-path XOR schedules remain the independent / unpaid-as-before baseline.
The shared-XOR soft-overlap is therefore **not opened**.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n≥2` is an open slot list starting at
`0` whose closed completion has only nonzero edges.

A **shared-dirt partitioned dual** of total query count `Q = 8` is a pair of
valid restored walks of lengths `(n_0,n_1)` with `n_0+n_1=8` and `n_0,n_1≥2`,
distinct nonzero labels within each walk, and **one shared dirt coefficient**.
Legal dirty cancellation requires even **total** live-read parity across both
walks. With even/odd subset tables `(e_i,o_i)` on walk `i`, the dual cost is

```text
R = Σ_{m=1}^{31} min(
      min_α (e0[α] + e1[α ⊕ m]),
      min_α (o0[α] + o1[α ⊕ m])
    ).
```

Independent dirt ([#2851](https://github.com/CrocSwap/integer-mult-bounds/pull/2851))
admits only the even+even branch, so shared-dirt `R` is always ≤ independent `R`
whenever both cover.

Up to swap the only partitions are `(2,6)`, `(3,5)`, and `(4,4)`. Length-1
components are not restored. The abstract complete-call tariff at
`(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

## Fixture A: partition `(2,6)`

Short walk `(0,σ)` has `e[0]=0`, `e[σ]=2`, `o[0]=1`, `o[σ]=1`. Shared cost
collapses to

```text
R = Σ_m min( e1[m],  2 + e1[m ⊕ σ],  1 + o1[m],  1 + o1[m ⊕ σ] ).
```

**Census.** Distinct-label pairs: covering count `3916416` (same as independent
covering); attainable `R ∈ {82,88,96}` with histogram
`583296 / 2916480 / 416640`. Minimum `R = 82`.

Champion `((0,16),(0,1,2,4,8,15))` has shared `R = 82` and independent `R = 92`.
Path `X = 16`, tariff `500`. The `X = 0` figure `468` is the abstract lower
bound from `R = 82`.

## Fixture B: partition `(3,5)`

**Census.** Covering count `10416000`; attainable `R ∈ {82,88,96}` with
histogram `1458240 / 7291200 / 1666560`. Minimum `R = 82`.

Champion `((0,1,2),(0,4,8,15,16))` has shared `R = 82`.

## Fixture C: partition `(4,4)`

**Lemma (swap symmetry).** `dual_shared(e0,o0,e1,o1) = dual_shared(e1,o1,e0,o0)`
by reindexing `α ↦ α ⊕ m` on each mask. Ordered census uses the upper triangle
and doubles off-diagonal contributions.

**Census.** Covering count `14165760`; attainable `R ∈ {82,88,96}` with
histogram `1944320 / 9721600 / 2499840`. Minimum `R = 82`.

Champion `((0,1,2,4),(0,8,15,16))` has shared `R = 82`.

## Tariff consequence

Every covering shared-dirt partitioned dual at `Q = 8` has `R ≥ 82`, attained
on all three shapes. Even at `X = 0`,

```text
38·8 + 2·82 + 2·0 = 468 > 436.
```

Positive path-`X` only increases the bill. Shared dirt **undercuts** the
independent-dirt floors (`92` / `98` / `100` on `(2,6)` / `(3,5)` / `(4,4)`) but
still cannot undercut the six-query endpoint under the PR1898 abstract tariff.
By comparison, same-walk even-subset reaches `R ≥ 74` (tariff floor `452` at
`X = 0`); shared-dirt on partitioned walks lands strictly between same-walk and
independent dual.

| Alphabet | Covering min R | Tariff floor (X=0) | Undercuts 436? |
|---|---:|---:|---|
| Same-walk even-subset (#2677) | ≥74 | ≥452 | no |
| Dirty-shadow (#2840) | ≥74 | ≥452 | no |
| Distinct partitioned (#2851) | 92 | 488 | no |
| One-repeat partitioned (pending) | 112 | 528 | no |
| Two-repeat partitioned (pending) | — (covering 0) | — | no |
| **Shared-dirt partitioned (this)** | **82** | **468** | **no** |

## Scope limits

- Fixes the **shared-dirt** partitioned dual interface at total `Q = 8` with
  distinct nonzero labels within each walk. Same-walk, dirty-shadow, distinct
  partitioned, one-repeat, and two-repeat leave-alones / pending tips are
  outside and not edited.
- Transfer-coupled dual/shapes and host screens remain deferred soft-overlaps
  and are not opened.
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643); this
  package does not share X.
- No new kappa and no multiplication theorem are claimed.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436, `(b,a,x)=(38,2,2)` | — |
| #2851 | Partitioned independent dual at `Q=8` has `R≥92` | — |
| pending tworepeat | Two-repeat covering 0; OQ1–OQ2 | — |
| **This** | — | **Shared-dirt dual at `Q=8` has `R≥82` (all shapes); tariff floor `468>436`; beats independent floors; soft-overlap-safe vs shared-XOR** |
