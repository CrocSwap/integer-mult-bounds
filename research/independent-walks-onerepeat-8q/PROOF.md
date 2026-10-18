# One-repeat partitioned (2,6) cannot improve on R=92 at Q=8

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It is a freestanding `#840`-style priced alphabet at
eight queries: the **one-repeat** companion of the partitioned independent dual
on shape `(2,6)`. It answers open question 1 of pending
`cursor/independent-walks-8q-60b9`: whether allowing one repeated nonzero label
in the length-6 walk improves on distinct-label `R=92`.

No new kappa is claimed. Leave-alone packages through #2846 are not edited.
Pending independent-walks-8q is not edited or competed.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n≥2` is an open slot list starting at
`0` whose closed completion has only nonzero edges.

A **one-repeat (2,6) dual** is a pair

- short walk `(0,σ)` with `σ∈{1,…,31}`,
- long walk `(0,ℓ_1,…,ℓ_5)` whose five nonzero slots contain **exactly one**
  repeated nonzero label (multiset shape `{d:2,o₁,o₂,o₃}`),

with independent dirt and dual even-parity cost

```text
R = Σ_{m=1}^{31} min( e_long[m],  2 + e_long[m ⊕ σ] ).
```

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

## Length-1 exclusion

A length-1 list `(0,)` closes to `(0,0)`. That edge has XOR `0`, so it is not a
restored walk. The short component of `(2,6)` therefore cannot itself host a
one-repeat layer.

## Structural identity

**Lemma (Σe = 40 on rank-4 one-repeat longs).** Every valid restored length-6
walk whose nonzero multiset has shape `{d:2,o₁,o₂,o₃}` and whose four distinct
nonzero labels span a rank-4 subspace has

```text
Σ_{v ∈ V \ {0}} e_long[v] = 40,
```

where `V` is the long span. Machine-checked on all `3749760` such walks.

**Lemma (rank-4 outside).** When the long span has rank `4` and `σ ∉ V`,

```text
R = 2 · Σ_{v ∈ V \ {0}} e_long[v] + 32 = 2·40 + 32 = 112.
```

**Lemma (inside span never covers).** If `σ ∈ V`, the dual cost returns `None`
on every one-repeat rank-4 long (machine-checked: zero inside-span covers).

**Lemma (rank-3 never covers).** If the four distinct nonzero labels have rank
`<4`, no `σ` yields a covering dual. Admitted in `model.py` /
`independent.py` census: every valid rank`<4` long is dual-scanned for all
`σ`, with `valid_rank_lt4_walks=781200` and `covering_rank_lt4=0`.

## Census

Valid one-repeat length-6 walks: `4530960`, of which rank-4: `3749760`.
Outside-span short labels per rank-4 long: `31 − 15 = 16`. Covering pairs:

```text
3749760 · 16 = 59996160.
```

Attainable spectrum: `{112}` with histogram `{112: 59996160}`. Minimum `R=112`.

Champion path `((0,16),(0,4,1,8,2,1))` has path `X=8`, tariff `544`. The
`X=0` figure `528` is only the abstract lower bound from `R=112`.

## Tariff consequence

Every covering one-repeat `(2,6)` dual has `R=112`. Even at `X=0`,

```text
38·8 + 2·112 + 2·0 = 528 > 436.
```

Positive path-`X` only increases the bill. Distinct-label `(2,6)` floor `R=92`
(pending iw8q) is strictly better than one-repeat `R=112`, so one-repeat does
not reopen an undercut of the six-query endpoint under the PR1898 abstract
tariff.

## Scope

This is a priced-alphabet obstruction, not a multiplication theorem and not a
new kappa. Leave-alone packages through #2846 and pending
`cursor/independent-walks-8q-60b9@379aaf8f` are not edited. Deferred
soft-overlaps (transfer-coupled-dual/shapes; shared-xor; host screens) are not
opened.

Prepared by Wentao Li with substantial AI assistance.
