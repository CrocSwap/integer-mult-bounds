# Multi-connector / priced-shadow readout cannot undercut tariff 436 at Q=7

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 1 of
[#2715](https://github.com/CrocSwap/integer-mult-bounds/pull/2715)
(`research/cheaper-readout-7q-obstruction`): whether a **multi-connector** readout
alphabet (two live connectors, or a priced shadow snapshot) can reach `R ≤ 78`
at `Q = 7` with `X = 6` after a complete dirty bill.

No new kappa is claimed. Leave-alone packages through #2715 are not edited.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. Connector prefixes of a restored length-7 walk are slots
`(s_0,…,s_6)` with `s_0 = 0`. The even-subset score

```text
R_even = Σ_{m=1}^{31} min{|T| : T ⊂ {0,…,6}, |T| even, ⊕_{i∈T} s_i = m}
```

satisfies `R_even ≥ 82` on every covering Q=7 walk
([#2686](https://github.com/CrocSwap/integer-mult-bounds/pull/2686)), so at
`X = 6` the abstract tariff `(b,a,x)=(38,2,2)` is at least `442 > 436`.

## Fixture A: priced shadow snapshot with inherited dirt

At one index `k`, pay a full-row copy producing a second live connector holding
value `σ = s_k` and **the same dirt coefficient** as the primary (inherited
dirt). Readouts may use primary slots and/or one shadow read. Legal dirty
cancellation requires even total live-read parity across primary and shadow.

**Lemma (sym-diff collapse).** Every legal dirty-shadow schedule has the same
cost as an even-subset schedule: an odd primary set `S` plus one shadow read
realizing `XOR(S) ⊕ σ` is equivalent, via `S Δ {k}`, to an even primary set of
cost `|S| ± 1` realizing the same mask. Even primary schedules are already
even-subset. Hence for every covering slot list and every `k`,

```text
R_dirty-shadow(k) = R_even.
```

**Census.** On all `583296` covering distinct-6 sets, the min-over-`k` dirty
shadow total matches even-subset exactly (spectrum `{82,88}`). One-repeat basis
layer: `R = 96` only (`1680` walks).

## Fixture B: two independently dirty connectors, same walk

Admit a second connector with independent dirt on the same slot list. Each port
needs even live-read parity separately. Cost for mask `m` is

```text
min_a (e[a] + e[a ⊕ m]),
```

where `e` is the even-subset per-mask table (with `e[0] = 0`).

**Lemma (triangle).** Concatenating two even realizing sets (or taking their
symmetric difference on one connector) yields `e[m] ≤ e[a] + e[a ⊕ m]`. The
bound is achieved at `a = m`. Therefore the dual-independent total equals
`R_even` on every covering list: **no improvement**.

**Census (machine-checked).** On all `583296` covering distinct-6 sets,
`dual_independent_from_even` computes `Σ_m min_a (e[a]+e[a⊕m])` directly
(not by copying `Σ e[m]`), the triangle inequality is verified on each even
table, and both match even-subset (spectrum `{82,88}`;
`matches_even_on_covering = triangle_holds_on_covering = 583296`).

## Counterfactual: dirt-free shadow

If the snapshot were somehow dirt-free while retaining `σ`, primary would still
need even parity while shadow reads would be free of dirt. Then

```text
R_clean = min( e[m],  1 + e[m ⊕ σ],  1_{m=σ} ).
```

**Census.** Min-over-`k` totals attain `{71, 80}` (histogram `97216 / 486080`).
The champion `(0,1,2,6,12,24,16)` reaches `R_clean = 71` at `k=1`, hypothetical
tariff `38·7 + 2·71 + 2·6 = 420 < 436`.

This counterfactual is **illegal** under the PR1898 arbitrary-dirt contract: a
copy of a dirty connector inherits dirt, and there is no dirt-only register with
which to scrub the shadow while keeping `σ`. Finite check: shadow-only readout
of mask `σ` has odd inherited-dirt parity on that output.

## Tariff consequence

After a complete dirty bill, every legal multi-connector / priced-shadow
schedule on covering Q=7 walks still has `R ≥ 82`. At the
[#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643) XOR floor
`X = 6`, tariff `≥ 442 > 436`. Charging the snapshot copy `C` only increases
the bill. The free clean-shadow undercut is not realizable.

## Scope limits

- Fixes one dual-connector interface (correlated dirty shadow; independent dual
  same-walk) and the illegal clean-shadow counterfactual. Other multi-row
  alphabets with new query schedules or transfers are outside.
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Host screens are deferred.
- Leave-alone through #2715 (including #2593, #2643, #2677, #2686, #2687) is
  not edited.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436 | — |
| #2643 | `X≥6` at `Q=7` | — |
| #2686 | Even-subset `R≥82` | — |
| #2715 | All-subset collapses under dirty-parity repair; OQ1 asks multi-connector | — |
| **This** | — | **Legal dirty shadow / dual same-walk stay at R≥82; clean shadow would hit 71 but fails dirty bill** |
