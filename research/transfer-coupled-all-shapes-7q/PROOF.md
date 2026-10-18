# Transfer-coupled duals cannot undercut tariff 436 at Q=7

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
open question 1 of [#2779](https://github.com/CrocSwap/integer-mult-bounds/pull/2779)
and the remaining-shapes follow-up left by the maximal-share `(5,1,1)` package:
after a **transfer-coupled** dual (shared prefix, priced transfer `C≥1`,
divergent suffixes) and a complete dirty bill at total `Q=7`, can any unordered
shape `(p,a,b)` undercut the six-query endpoint tariff `436`?

No new kappa is claimed. Leave-alone packages through #2779 and the pending
`(5,1,1)`-only transfer-coupled package are not edited.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **transfer-coupled dual** of shape `(p,a,b)` with
`p+a+b=7` and `p,a,b≥1` consists of:

- a shared prefix of `p` slots starting at `0` (queries charged once);
- two nonempty divergent suffixes of lengths `a` and `b` with labels disjoint
  from the prefix and from each other;
- a transfer surcharge `C≥1` (fork cost);
- two restored walks `W0 = prefix∥suf_a` and `W1 = prefix∥suf_b` carrying
  **independent** dirt;
- dual even-parity readout
  `R = Σ_{m=1}^{31} min_a (e0[a] + e1[a⊕m])`.

Fair shared-prefix XOR billing charges prefix-internal edges once and both
fork/suffix/return branches fully. Path costs are always even:
`X = 2·Σ(wt(δ)-1)`.

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is
`38·Q + 2·R + 2·X + C`.

## Census

Up to swapping suffixes (`a≤b`) there are nine shapes. Distinct-label covering
duals were enumerated with an exact `min_a` dual (C helper, pure-Python
cross-check):

| Shape | Covering | Min R |
|---|---:|---:|
| `(1,1,5)` | 3499776 | 92 |
| `(1,2,4)` | 8749440 | 98 |
| `(1,3,3)` | 5832960 | 100 |
| `(2,1,4)` | 17498880 | 90 |
| `(2,2,3)` | 34997760 | 94 |
| `(3,1,3)` | 34997760 | 88 |
| `(3,2,2)` | 26248320 | 90 |
| `(4,1,2)` | 34997760 | **86** |
| `(5,1,1)` | 8749440 | **84** |

Global minimum is `R=84` at `(5,1,1)` only. Every other shape has `R≥86`.

## X=0 lemma on the critical shape

On `(5,1,1)`, `X=0` forces every fair-path edge to have Hamming weight 1.
Returns to `0` then force suffix labels in `{1,2,4,8,16}`. Enumerating all
distinct weight-1 prefix paths of length 4 from `0` (300 paths) and all
admissible suffix pairs yields **zero** covering duals. Since fair `X` is
always even, every covering `(5,1,1)` schedule has `X≥2`.

## Tariff consequence

- Critical shape: `38·7 + 2·84 + 2·2 + 1 = 439 > 436`.
- All other shapes: `R≥86` already gives `38·7 + 2·86 + 2·0 + 1 = 439 > 436`
  at `X=0`.

Hypothetical `R=84,X=0,C=1` would tariff `435<436`, but that schedule class is
empty. Positive path-`X` only increases the bill. Transfer-coupled duals
therefore cannot undercut the six-query endpoint under the PR1898 abstract
tariff after a complete dirty bill.

By comparison, partitioned independent walks (#2779) sit at `R=112`, and
same-walk even-subset (#2686) at `R=82` with a single dirt port (no transfer).

## Machine checks

`verify.py` recomputes the critical `(5,1,1)` and second `(4,1,2)` censuses,
the X=0 Gray lemma, champions of every shape, and the tariff floor.
`independent.py` recomputes all companion-shape censuses with a separate dual
path and rechecks the critical champion in pure Python. Package tests cover
corruption, source-pin drift, duplicate JSON keys, and `-O`/`need()` smoke.

Prepared by Wentao Li with substantial AI assistance. Apache-2.0.
