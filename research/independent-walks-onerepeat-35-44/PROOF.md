# One-repeat (3,5)/(4,4) cannot improve on R=98 / R=100 at Q=8

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It is a freestanding `#840`-style priced alphabet at
eight queries: the **one-repeat** companions of the partitioned independent duals
on shapes `(3,5)` and `(4,4)`. It answers open question 1 of pending
`cursor/independent-walks-onerepeat-8q-60b9`: whether allowing one repeated
nonzero label on those partitions improves on distinct-label `R=98` / `R=100`.

No new kappa is claimed. Leave-alone packages through #2851 are not edited.
Pending independent-walks-onerepeat-8q is not edited or competed.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n≥2` is an open slot list starting at
`0` whose closed completion has only nonzero edges.

A **one-repeat (3,5) dual** is a pair

- short walk `(0,a,b)` with distinct nonzero labels (distinct-label length-3),
- long walk whose four nonzero slots have multiset shape `{d:2,o₁,o₂}`,

with independent dirt and dual even-parity cost

```text
R = Σ_{m=1}^{31} min_α ( e_short[α] + e_long[α ⊕ m] ).
```

A **one-repeat (4,4) dual** is a pair with one side a restored one-repeat
length-4 walk (only form `(0,d,o,d)` restores) and the other a distinct-label
length-4 walk. Both-sides one-repeat is checked separately.

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

## Length-3 exclusion

A length-3 one-repeat candidate is `(0,d,d)`. Closing gives edge `d→d` of XOR
`0`, so it is not a restored walk. The short component of `(3,5)` therefore
cannot itself host a one-repeat layer (machine-checked: `0` valid walks).

## Structural facts (machine-checked)

**Lemma (Σe = 16 on covering one-repeat L5 champions).** Every covering
one-repeat length-5 long in the `(3,5)` census that appears as a first witness
has long span of rank `3` with

```text
Σ_{v ∈ V \ {0}} e_long[v] = 16.
```

**Lemma ((3,5) covering spectrum).** Over all `465` distinct length-3 even
tables and `13485` one-repeat length-5 even tables, every covering dual has
`R=112`. Covering count `2499840`; histogram `{112: 2499840}`.

**Lemma ((4,4) covering spectrum).** Over all `930` one-repeat length-4 even
tables and `4495` distinct length-4 even tables, every covering dual has
`R=112`. Covering count `1666560`; histogram `{112: 1666560}`.

**Lemma (both-sides one-repeat never covers).** The `930×930` both-one-repeat
`(4,4)` census has covering count `0`.

## Census

| Dual schedule | Covering pairs | Exact min R | Beats distinct? |
|---|---:|---:|---|
| Distinct `(3,5)` (iw8q) | 10416000 | 98 | — |
| One-repeat `(3,5)` (this) | **2499840** | **112** | **no** |
| Distinct `(4,4)` (iw8q) | 14165760 | 100 | — |
| One-repeat×distinct `(4,4)` (this) | **1666560** | **112** | **no** |
| One-repeat×one-repeat `(4,4)` | **0** | — | — |

Champions:

- `(3,5)`: `((0,1,2),(0,8,4,16,4))` with path `X=8`, tariff `544`.
- `(4,4)`: `((0,1,2,1),(0,4,8,16))` with path `X=8`, tariff `544`.

The `X=0` figure `528` is only the abstract lower bound from `R=112`.

## Tariff consequence

Every covering one-repeat `(3,5)` or `(4,4)` dual has `R=112`. Even at `X=0`,

```text
38·8 + 2·112 + 2·0 = 528 > 436.
```

Positive path-`X` only increases the bill. Distinct-label floors `R=98` /
`R=100` (pending iw8q / published #2851) are strictly better than one-repeat
`R=112`, so one-repeat does not reopen an undercut of the six-query endpoint
under the PR1898 abstract tariff.

## Scope

This is a priced-alphabet obstruction, not a multiplication theorem and not a
new kappa. Leave-alone packages through #2851 and pending
`cursor/independent-walks-onerepeat-8q-60b9@5ee2550c` are not edited. Deferred
soft-overlaps (transfer-coupled-dual/shapes; shared-xor; host screens) are not
opened.

Prepared by Wentao Li with substantial AI assistance.
