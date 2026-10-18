# One-repeat transfer-coupled (5,1,1) cannot improve on R=84

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 1 of [#2836](https://github.com/CrocSwap/integer-mult-bounds/pull/2836):
after a transfer-coupled dual of shape `(5,1,1)` whose six nonzero schedule
labels contain **exactly one repeated** nonzero value, can dual even-parity
readout improve on the distinct-label floor `R=84`, or undercut tariff `436`?

No new kappa is claimed. Leave-alone packages through #2836 are not edited.

## Setup

Retain the transfer-coupled `(5,1,1)` contract of #2836 / #2817: shared prefix of
length 5 starting at `0`, divergent nonempty suffixes of length 1, transfer
`C≥1`, independent dirt on the two walks, dual even-parity

\[
R=\sum_{m=1}^{31}\min_a\bigl(e_0[a]+e_1[a\oplus m]\bigr).
\]

Canonical prefixes sort the nonzero multiset (matching the distinct-label census
representatives). Divergent suffixes are unordered with `sa<sb`.

A schedule is **one-repeat** when the multiset of its six nonzero slots has
exactly five distinct values (one label of multiplicity two). The two disjoint
cases are:

1. **Prefix-internal double.** Prefix nonzero multiset `{d,d,o₁,o₂}`; suffixes
   fresh and divergent.
2. **Suffix–prefix collision.** Prefix four distinct nonzero labels; exactly one
   suffix equals a prefix label; the other suffix is fresh.

(Identical suffixes `sa=sb` are excluded by divergence. Two distinct colliding
suffixes would create two repeated labels.)

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is
`38·Q + 2·R + 2·X + C`.

## Census

Exact `min_a` dual (C helper, pure-Python cross-check):

| Layer | Covering | Min R | Histogram |
|---|---:|---:|---|
| Prefix-internal double | 2499840 | **98** | `{98: 2499840}` |
| Suffix–prefix collision | 1666560 | **96** | `{96: 1666560}` |
| Combined | 4166400 | **96** | — |

Every covering schedule in each layer attains a single R value. Combined minimum
is `R=96 > 84`.

Pinned champions recompute under both the C dual and an independent pure-Python
dual:

- Prefix-dup: `prefix=(0,1,1,2,7)`, `suf={8,16}`, `R=98`.
- Suffix-hit: `prefix=(0,1,2,4,9)`, `suf={1,16}`, `R=96`.

## Tariff consequence

At the combined minimum `R=96`, even the most favorable path bill `X=0` with
`C=1` gives

\[
38\cdot 7 + 2\cdot 96 + 2\cdot 0 + 1 = 459 > 436.
\]

Positive path-`X` only increases the invoice. One-repeat layers therefore cannot
undercut the six-query endpoint, and they strictly worsen the distinct-label
floor answered by #2836 / #2817.

## Machine checks

`verify.py` recomputes both layer censuses, champion duals, and the tariff floor.
`independent.py` recomputes both censuses on a private dual path and rechecks
champions in pure Python. Package tests cover corruption, source-pin drift,
duplicate JSON keys, and `-O`/`need()` smoke.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
