# Two-receiver shared-packet addendum

This addendum considers the exact normalized Gaussian word of ToikY's
[#8072](https://github.com/CrocSwap/integer-mult-bounds/pull/8072), head
`75f7e1c44f48c43983016bcf8878c4d9e5e87c62`, and builds on the receiver-stock
certificate at [#8074 head `a9e110ae5580f6366a1098987adbe8398a047c7a`](https://github.com/CrocSwap/integer-mult-bounds/commit/a9e110ae5580f6366a1098987adbe8398a047c7a).
The input is the same authenticated `word.json.gz`; no second word or stock
cache is used.

## Contract and stopping condition

For each original move `u: a -> b` appearing with nonzero coefficient in the
original row of a second move `v: b -> d`, remove these two moves. Give the
original sender `a` its entire original stock, even values created later in the
saved word. Allow it to form any rational linear packet `t`. A relay `h` gets
that packet and passes it unchanged to `b` and `d`; if `h` equals an endpoint,
the coincident leg is local and has zero grade. Both receivers may decode
arbitrary rational linear combinations of the packet and their other original
stocks. The rewrite must reconstruct the original scalar `u` at `b` and the
original scalar `v` at `d`, and fixes the other original functions. This model
grants acausal stock availability and no uncharged input-dependent side channel.

Eight incidences have `a=d`: after deleting `v`, the source and second receiver
are the same chart, and their remaining independent stock cannot generate `v`.
For every remaining incidence, enumerate **all 1,103 original charts** as
possible relay. A nonlocal leg must connect properly nested frames; equal-depth
distinct charts are not charged as zero-grade legs. Let `g(x,y)` be the
absolute frame-depth difference. Compare the old integer raw grade
`g(a,b)+g(b,d)` with `g(a,h)+g(h,b)+g(h,d)`. If no legal relay makes the
latter strictly smaller, stop for that incidence; a more general price
analysis is not inferred.

The word has **11,819** such original row incidences. Of the rest, **58** have a
strictly cheaper relay, covering 39 chart triples. The checker proves **47** of
those have no nonzero common packet in `S_a ∩ S_b ∩ S_d`, and that the **11**
remaining cases have only a multiple of `u`, which has zero coordinate on the
removed `v` at its receiver. There is therefore no candidate in this family.
A canonical digest of all 58 incidence, relay and rank records is
`c2969359ad56459f42323c8e6b5945b89a8dc7c53d537ab6c606b04fbe3f123f`.

## The rational rank argument

The existing evaluator authenticates the complete graph and proves that each
original local stock is independent modulo `p=65521`. All word coefficients
have denominators prime to `p`, so each stock also has a rational basis whose
square pivot minor is a `p`-unit. For each source stock `S_a` and receiver stock
`S_d`, form 36 modular annihilators and explicitly check every annihilator
against every stock basis row. Each such modular annihilator lifts to a rational
one with `p`-unit denominator: fix integer lifts of its free coordinates and
solve the pivot equations using the nonsingular stock minor. Its reduction is
the checked modular vector.

Pair these 72 annihilators with each original stock vector at `b`. If the
resulting modular matrix has full row rank, a nonzero rational minor persists,
so no nonzero vector of `S_b` is annihilated by all 72 vectors. In particular,
`S_a ∩ S_b ∩ S_d = {0}` over Q. This gives 47 exclusions. In the other 11 the
modular pairing rank is exactly one less than `dim(S_b)`, so the rational
intersection has dimension at most one. Each `u` is nonzero, belongs to
`S_b`, is defined by a row over `S_a`, and has the following exact rational
representation in the independent stock of chart 127:

```text
91582 = 103243
91560 = -2*104268 - 2*104318
97266 = -103991/2 - 103944/2
89777 = 104126 + 104146 + 104063 + 103952 - 104092/58
96513 = 103514
```

Thus the intersection is exactly `span(u)`. In each of the 11 cases the removed
`v` is absent from the relevant right-hand side. Independence of the chart-127
stock makes the `v` coordinate of every multiple of `u` zero, so that receiver
cannot decode `v` after its arrival is removed. The checker expands these five
identities over all 1,291 rational input coordinates. Its negative control
replaces `-1/58` by `-1/57` and requires rejection.

Each nonnegative pairing dot product is at most
`1291 * 65520^2 = 5,542,095,686,400 < 2^53 < 2^63`. Therefore its binary64
integer accumulation is exact, and the program compares one dot product to a
Python-integer calculation before reducing modulo `p`. Randomness only selects
annihilators: their annihilation equations and nonzero rank minors are checked.
The replay includes a positive toy with a working pair of decoders and a
negative full-rank toy.

## Boundary

This is a finite exclusion in the stated one-packet, original-sender,
two-original-scalar model, not a new rate or a global impossibility theorem.
Other senders or changed sender stocks, unrelated transfer pairs, multiple new
packets, rewritten dependencies, preservation of only downstream combinations,
nonlinear operations, and equal-raw-grade changes with a different nonlinear
price remain open. A positive replacement would still need a real chronology,
full transition identity, paid and productive invoice, ownership and return
checks, independent validation, and κ qualification.
