# Dirty-parity collapse extends to eight queries

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 2 of
[#2715](https://github.com/CrocSwap/integer-mult-bounds/pull/2715)
(`research/cheaper-readout-7q-obstruction`): whether the same dirty-parity
collapse applies at eight queries for all-subset versus even-subset floors.

No new kappa is claimed. Leave-alone packages through #2715 are not edited.
Pending `multi-connector-7q` dual-census repair, deferred shared-XOR soft-overlap
with #2643, and host screens are not opened.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. Connector prefixes of a restored length-8 walk are slots
`(s_0,…,s_7)` with `s_0 = 0`. The **even-subset** score is

```text
R_even = Σ_{m=1}^{31} min{|T| : T ⊂ {0,…,7}, |T| even, ⊕_{i∈T} s_i = m}.
```

[#2677](https://github.com/CrocSwap/integer-mult-bounds/pull/2677) / the path-lowered
789q invoice records that on distinct-slot covers the minimum is `R_even = 74`
(witness `(0,1,2,3,4,8,16,29)`), so even at `X = 0` the abstract tariff
`(b,a,x)=(38,2,2)` is at least `452 > 436`.

## Candidate cheaper alphabet: all-subset / odd-cardinality

Allow every nonempty realizing subset (odd cardinalities included):

```text
R_all = Σ_{m=1}^{31} min{|T| : T ⊂ {0,…,7}, |T|≥1, ⊕_{i∈T} s_i = m}.
```

**Census (distinct nonzero 7-sets).** Covering sets: `2430400`. Attainable
totals `R_all ∈ {61, 64, 68}` with histogram `416640 / 1180480 / 833280`.
Minimum `61`.

**One-duplicate layer.** Length-8 multisets with exactly seven distinct labels
including `0`: covering count `4083072`, attainable `R_all ∈ {66, 72}`
(minimum `66`).

The distinct-7 champion `(0,1,2,3,4,8,16,29)` attains `R_all = 61`. The
hypothetical tariff `38·8 + 2·61 + 2·0 = 426` is **strictly below** the
six-query endpoint `436` even with free XOR budget.

## Dirty-connector obstruction

Each live readout `R_m` on connector `z` adds one copy of `A_m · z_dirt` to
output `y_m`. For arbitrary connector dirt to cancel on every output, the number
of live `R_m` events for each mask `m` must be even. Therefore every
odd-cardinality realizing set is **illegal** in the PR1898 dirty-restoration
contract unless repaired.

Finite check: a minimum all-subset schedule on the champion leaves a nonempty
set of masks with odd live-connector parity (13 odd min-masks).

## Priced repair: zero-slot parity completion

Every restored walk here has a 0-valued slot (the start). For an odd realizing
set `S`:

- if `S` already contains a 0-valued index, drop one such index (`|S|-1`, same XOR);
- otherwise adjoin one 0-valued slot readout (`|S|+1`, same XOR).

Both moves restore even live-connector parity without changing the pure mask.
Define `R_repair` as the minimum cost over even sets and such repaired odd sets.

**Lemma.** On any slot list containing a 0-valued index, `R_repair = R_even`.
Every repaired odd set is an even set with the same XOR, and every even set is
already admitted.

**Census.** On all `2430400` covering distinct-7 sets, `R_repair` matches
`R_even` exactly (spectrum `{74,80,84}`; `repair_equals_even_count = 2430400`).
On the one-duplicate layer, `R_repair ∈ {82,88}` with minimum `82`.

## Tariff consequence

After dirty-parity repair, every covering distinct-7 Q=8 schedule still has
`R ≥ 74`, matching the #2677 even-subset distinct-slot floor. Even at `X = 0`,
tariff `≥ 452 > 436`. One-duplicate covers repair to `R ≥ 82` (tariff `≥ 468`).
The free all-subset undercut (`426 < 436`) is not realizable under the PR1898
dirty-connector contract; the minimal priced repair returns to the even-subset
floor.

## Scope limits

- This prices the natural odd-cardinality alphabet (all-subset) plus zero-slot
  parity repair at `Q = 8`. Multi-connector alphabets (including independent
  walks), dirty-shadow fixtures, output-mixing readouts, and host screens are
  outside; the pending `multi-connector-7q` dual-census repair is not edited.
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Leave-alone through #2715 (including #2593, #2643, #2677, #2686, #2687, #2715)
  is respected.
- Exact XOR floors at `Q = 8` and non-distinct multi-repeat layers beyond one
  duplicate are not claimed.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436 | — |
| #2643 | `X≥6` at `Q=7` | — |
| #2677 / 789q | Path-lowered invoices; distinct-slot `R≥74` at `Q=8` | — |
| #2686 | Even-subset `R≥82` at `Q=7` | — |
| #2715 | All-subset→repair collapse at `Q=7` (OQ2: does it extend to Q=8?) | — |
| **This** | — | **All-subset would hit R=61/tariff 426 at Q=8, but dirty-parity repair collapses to R≥74/tariff 452** |
