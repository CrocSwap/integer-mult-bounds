# Dirty-shadow sym-diff collapse extends to eight queries

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 2 of
[#2761](https://github.com/CrocSwap/integer-mult-bounds/pull/2761)
(`research/multi-connector-7q-obstruction`) and the matching handoff in
[#2764](https://github.com/CrocSwap/integer-mult-bounds/pull/2764): whether the
**dirty-shadow sym-diff collapse** that forced priced shadow snapshots back to
even-subset cost at `Q=7` extends verbatim to eight queries.

No new kappa is claimed. Leave-alone packages through #2817 are not edited.
In particular, `research/transfer-coupled-7q-obstruction/` is not touched.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. Connector prefixes of a restored length-8 walk are slots
`(s_0,…,s_7)` with `s_0 = 0`. The even-subset score

```text
R_even = Σ_{m=1}^{31} min{|T| : T ⊂ {0,…,7}, |T| even, ⊕_{i∈T} s_i = m}
```

satisfies `R_even ≥ 74` on every covering distinct-7 list
([#2677](https://github.com/CrocSwap/integer-mult-bounds/pull/2677)), so at
`X = 0` the abstract tariff `(b,a,x)=(38,2,2)` is at least `452 > 436`.

## Fixture: priced shadow snapshot with inherited dirt

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

The identity is machine-checked on the champion for all eight snapshot indices
(`128` odd primary subsets each) and enforced on the census by requiring
`dirty_r == even_r` for every covering list and every `k`.

**Census.** On all `2430400` covering distinct-7 sets, the min-over-`k` dirty
shadow total matches even-subset exactly (spectrum `{74,80,84}`). On all
`4083072` covering one-duplicate length-8 multisets, dirty-shadow likewise
matches even-subset (spectrum `{82,88}`).

## Counterfactual: dirt-free shadow

If the snapshot were somehow dirt-free while retaining `σ`, primary would still
need even parity while shadow reads would be free of dirt. Then

```text
R_clean = min( e[m],  1 + e[m ⊕ σ],  1_{m=σ} ).
```

**Census.** Min-over-`k` totals attain `{67, 70, 76}` on distinct-7 (histogram
`416640 / 1180480 / 833280`) and `{71, 80}` on one-dup. The champion
`(0,1,2,3,4,8,16,29)` reaches `R_clean = 67` at `k=2`, hypothetical tariff
`38·8 + 2·67 + 2·0 = 438 > 436`.

Unlike the Q=7 companion (#2761), where a free clean shadow would undercut
(`420 < 436`), at Q=8 the illegal clean-shadow floor still fails to undercut
the six-query endpoint at `X=0`. The counterfactual remains **illegal** under
the PR1898 arbitrary-dirt contract: a copy of a dirty connector inherits dirt.
Finite check: shadow-only readout of mask `σ` has odd inherited-dirt parity.

## Tariff consequence

After a complete dirty bill, every legal dirty-shadow schedule on covering Q=8
walks still has `R ≥ 74`. At `X = 0`, tariff `≥ 452 > 436`. Charging the
snapshot copy `C` only increases the bill. Even the free clean-shadow floor
stays at `438 > 436`.

## Scope limits

- Fixes the priced dirty-shadow snapshot at Q=8 and the illegal clean-shadow
  counterfactual. Dual-independent same-walk and transfer-coupled shapes are
  outside (open #2817 leave-alone for `(5,1,1)`).
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Host screens are deferred.
- Leave-alone through #2817 (including #2764, #2761, #2779, #2715, #2687,
  #2686, #2677, #2643, #2593, #2487) is not edited.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436 | — |
| #2677 | Distinct-slot even-subset `R≥74` at Q=8 | — |
| #2761 | Dirty-shadow collapse at Q=7; OQ2 asks Q=8 | — |
| #2764 | Dirty-parity collapse at Q=8; OQ2 asks dirty-shadow | — |
| **This** | — | **Dirty-shadow collapse at Q=8: legal R≥74 (tariff 452); clean counterfactual R=67 (tariff 438) still fails undercut** |
