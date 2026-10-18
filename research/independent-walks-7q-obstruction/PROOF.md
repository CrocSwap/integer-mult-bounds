# Partitioned independent walks cannot undercut tariff 436 at Q=7

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898). It answers
the **partitioned independent-walks** open question left after same-walk
multi-connector / priced-shadow work on the #2715 lineage: can two restored
walks with **distinct slot lists**, independent dirt, and dual even-parity
readout undercut the six-query endpoint tariff `436` at total `Q = 7`?

No new kappa is claimed. Leave-alone packages through #2715 are not edited.
Pending same-walk `multi-connector-7q` and `dirty-parity-8q` packages are not
edited or competed with on their fixtures.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n` is an open slot list
`(s_0,…,s_{n-1})` with `s_0 = 0` whose closed completion `(s_0,…,s_{n-1},0)`
has only nonzero edges. Length-1 lists are illegal: the closed return is the
zero edge `(0,0)`.

A **partitioned independent dual** of total query count `Q = 7` is a pair of
valid restored walks of lengths `(n_0,n_1)` with `n_0 + n_1 = 7` and
`n_0,n_1 ≥ 2`. Up to swap the only cases are `(2,5)` and `(3,4)`. Each walk
carries its own dirt coefficient. For mask `m` the dual even-parity cost is

```text
min_a (e0[a] + e1[a ⊕ m]),
```

where `e_i` is the even-subset table of walk `i` (with `e_i[0] = 0`).

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

## Length-1 exclusion

A length-1 list `(0,)` closes to `(0,0)`. That edge has XOR `0`, so it is not a
restored walk. Consequently `(1,6)` and `(6,1)` are not legal partitions of a
`Q = 7` dual schedule.

## Fixture A: partition `(2,5)`

Short walk `(0,σ)` has even table `e0[0]=0`, `e0[σ]=2`. Long walk
`(0,b_1,b_2,b_3,b_4)` with distinct nonzero labels. Dual cost collapses to

```text
R = Σ_{m=1}^{31} min( e1[m],  2 + e1[m ⊕ σ] ).
```

**Lemma (cover ⇒ outside coset).** Covering requires the long span `V` to have
rank `4` and `σ ∉ V`. Then masks in `V` pay `e1`, and masks in the complementary
coset pay `2 + e1(· ⊕ σ)`, so

```text
R = 2 · Σ_{v ∈ V \ {0}} e1[v] + 32.
```

**Lemma (F₂⁴ even-sum).** Any four linearly independent nonzero labels are a
basis of a 4-dimensional subspace. With a free `0`-slot, even-subset cost of a
vector equals the least even integer `≥` its Hamming weight in that basis.
Summing over the `15` nonzero vectors of `F₂⁴` yields exactly `40`. Hence every
covering `(2,5)` schedule has

```text
R = 2·40 + 32 = 112.
```

**Census.** Distinct-label pairs: `31 · C(31,4) = 975415` candidates; covering
count `416640`; attainable `R = {112}` only; structural identity holds on every
covering pair.

Champion: `((0,1), (0,2,4,8,16))` with path `X = 6`, tariff `502`.
(The `X = 0` figure `490` is only the abstract lower bound from `R = 112`;
a length-5 closed walk lies in a bipartite hypercube, so odd closed single-bit
tours are impossible and attainable path `X` is strictly positive.)

## Fixture B: partition `(3,4)`

**Census.** Distinct-label pairs: `C(31,2)·C(31,3) = 2090175` candidates;
covering count `833280`; attainable `R = {112}` only (machine-checked dual
`min_a` on every covering pair — not a copy of a constant).

Champion: `((0,1,2), (0,4,8,16))` with path `X = 6`, tariff `502`.

## Tariff consequence

Every covering partitioned dual at `Q = 7` has exact `R = 112`. Even at
`X = 0`,

```text
38·7 + 2·112 + 2·0 = 490 > 436.
```

Positive path-`X` only increases the bill. Partitioned independent walks
therefore cannot undercut the six-query endpoint under the PR1898 abstract
tariff. By comparison, a single same-walk even-subset schedule can reach
`R = 82` ([#2686](https://github.com/CrocSwap/integer-mult-bounds/pull/2686));
splitting the query budget across two independent dirt ports forces a much
worse readout invoice.

## Scope limits

- Fixes the **partitioned** independent-walk interface at total `Q = 7` with
  distinct nonzero labels within each walk. Transfer-coupled schedules
  (shared prefix, priced transfer, divergent suffixes) are outside; same-walk
  multi-connector / priced shadow remains the pending `multi-connector-7q`
  package.
- Shared non-path XOR schedules remain deferred (soft-overlap with #2643).
- Host screens are deferred.
- Leave-alone through #2715 (including #2593, #2643, #2677, #2686, #2687, #2715)
  is not edited.
- No new kappa, physical supplier, or multiplication theorem.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q=6`, endpoint tariff 436 | — |
| #2643 | `X≥6` at single-walk `Q=7` | — |
| #2686 | Even-subset `R≥82` on one walk | — |
| #2715 | All-subset collapses under dirty-parity; OQs | — |
| Pending mc7q | Same-walk dual / dirty shadow stay at `R≥82` | — |
| **This** | — | **Partitioned dual walks at `Q=7` have exact `R=112`; tariff floor `490>436`** |
