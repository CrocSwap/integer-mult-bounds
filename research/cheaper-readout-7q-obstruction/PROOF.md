# Odd-cardinality cheaper readout does not undercut tariff 436 after dirty-parity repair

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 1 of
[#2686](https://github.com/CrocSwap/integer-mult-bounds/pull/2686)
(`research/seven-query-r-floor`): whether a readout alphabet strictly cheaper
than even-subset connector-state combinations can reach `R ≤ 78` at `Q = 7`
with `X = 6`.

No new kappa is claimed. Leave-alone packages through #2686 are not edited.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. Connector prefixes of a restored length-7 walk are slots
`(s_0,…,s_6)` with `s_0 = 0`. The **even-subset** score is

```text
R_even = Σ_{m=1}^{31} min{|T| : T ⊂ {0,…,6}, |T| even, ⊕_{i∈T} s_i = m}.
```

[#2686](https://github.com/CrocSwap/integer-mult-bounds/pull/2686) proves
`R_even ≥ 82` on every covering Q=7 walk (sharp), so at `X = 6` the abstract
tariff `(b,a,x)=(38,2,2)` is at least `442 > 436`.

## Candidate cheaper alphabet: all-subset / odd-cardinality

Allow every nonempty realizing subset (odd cardinalities included):

```text
R_all = Σ_{m=1}^{31} min{|T| : T ⊂ {0,…,6}, |T|≥1, ⊕_{i∈T} s_i = m}.
```

**Census (distinct nonzero 6-sets).** Covering sets: `583296`. Attainable
totals `R_all ∈ {66, 72}` with histogram `97216 / 486080`. Minimum `66`.

**One-repeat spanning layer (GL basis).** All `1680` covering one-repeat walks
have `R_all = 80` only.

The credited champion `(0,1,2,6,12,24,16)` attains `R_all = 66` with path-local
`X = 6`. The hypothetical tariff `38·7 + 2·66 + 2·6 = 410` is **strictly below**
the six-query endpoint `436`.

## Dirty-connector obstruction

Each live readout `R_m` on connector `z` adds one copy of `A_m · z_dirt` to
output `y_m`. For arbitrary connector dirt to cancel on every output, the number
of live `R_m` events for each mask `m` must be even. Therefore every
odd-cardinality realizing set is **illegal** in the PR1898 dirty-restoration
contract unless repaired.

Finite check: the minimum all-subset schedules on the champion and on the first
`R_all = 66` witness each leave a nonempty set of masks with odd live-connector
parity.

## Priced repair: zero-slot parity completion

Every Q=7 restored walk has a 0-valued slot (the start). For an odd realizing
set `S`:

- if `S` already contains a 0-valued index, drop one such index (`|S|-1`, same XOR);
- otherwise adjoin one 0-valued slot readout (`|S|+1`, same XOR).

Both moves restore even live-connector parity without changing the pure mask.
Define `R_repair` as the minimum cost over even sets and such repaired odd sets.

**Lemma.** On any slot list containing a 0-valued index, `R_repair = R_even`.
Every repaired odd set is an even set with the same XOR, and every even set is
already admitted.

**Census.** On all `583296` covering distinct-6 sets, `R_repair` matches
`R_even` exactly (spectrum `{82,88}`). On the one-repeat basis layer,
`R_repair = 96` only (`1680` walks), matching the even-subset repeat floor.

## Tariff consequence

After dirty-parity repair, every covering Q=7 schedule still has `R ≥ 82`. At
the [#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643) XOR floor
`X = 6`, tariff `≥ 442 > 436`. The free all-subset undercut is not realizable
under the PR1898 dirty-connector contract; the minimal priced repair returns to
the even-subset floor already proved in #2686.

## Scope limits

- This prices one natural odd-cardinality alphabet (all-subset) plus zero-slot
  parity repair. Multi-connector alphabets, output-mixing readouts, and host
  screens are outside.
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Leave-alone through #2686 (including #2593, #2643, #2677) and pending
  `odd-kernel-query-pair` are not edited.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436 | — |
| #2643 | `X≥6` at `Q=7` | — |
| #2677 / 789q | Path-lowered invoices; distinct-slot `R∈{82,88}` | — |
| #2686 | Even-subset `R≥82` at `Q=7` (OQ1: cheaper alphabets?) | — |
| **This** | — | **All-subset would hit R=66/tariff 410, but dirty-parity repair collapses to R≥82/tariff 442** |
