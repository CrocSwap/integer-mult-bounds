# Two-repeat partitioned walks cannot cover at Q=8

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It names one freestanding `#840`-style priced
readout alphabet at eight queries beyond same-walk / dirty-shadow / partitioned
dual / one-repeat: the **two-repeat** (excess-2) companion of partitioned
independent duals. It answers preferred next17 and open questions 1–2 of pending
`cursor/independent-walks-onerepeat-35-44-60b9`.

No new kappa is claimed. Leave-alone packages through #2851 are not edited.
Pending onerepeat tips are not edited or competed.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n≥2` is an open slot list starting at
`0` whose closed completion has only nonzero edges.

The **excess** of a walk is `Σ (count(ℓ)−1)` over nonzero labels. One-repeat
has excess `1`. **Two-repeat** means excess exactly `2`.

A **two-repeat partitioned dual** of total query count `Q = 8` is a pair of
valid restored walks of lengths `(n_0,n_1)` with `n_0+n_1=8` and `n_0,n_1≥2`,
where at least one side is two-repeat, with independent dirt and dual
even-parity cost

```text
R = Σ_{m=1}^{31} min_α ( e0[α] + e1[α ⊕ m] ).
```

Up to swap the only partitions are `(2,6)`, `(3,5)`, and `(4,4)`.

The abstract complete-call tariff at `(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

## Fixture A: partition `(2,6)`

Short walk `(0,σ)`. Long walk of length 6 with excess 2 on five nonzero slots
forces exactly three distinct nonzero labels. Restoring shapes:

| Shape | Count |
|---|---:|
| `{d:2,e:2,o}` | **13485** |
| `{d:3,o₁,o₂}` | **13485** |
| Total valid | **26970** |

**Lemma (span ≤ 8).** Three labels span a subspace of rank ≤ 3, hence size ≤ 8.

**Lemma (coset union ≤ 16).** Pairing with short `(0,σ)` reaches at most
`span ∪ (span ⊕ σ)`, size ≤ 16 < 32. Dual covering is therefore impossible.

**Census.** Exact covering count **0** (machine-checked on all `26970·31`
pairs).

## Fixture B: partition `(3,5)`

Short walk: distinct-label length-3 (`C(31,2)=465` even tables). Long walk:
excess 2 on four nonzero slots.

| Shape | Restores? | Count |
|---|---|---:|
| `{d:2,e:2}` | yes | **465** |
| `{d:3,o}` | no | 0 |
| `{d:4}` | no | 0 |

**Lemma (sumset ≤ 16).** Long `{d,e}` has span size ≤ 4; short length-3 has
span size ≤ 4; the XOR sumset has size ≤ 16 < 32. Dual covering is impossible.

**Census.** Exact covering count **0** on all `465·465` pairs.

## Fixture C: partition `(4,4)`

Two-repeat on length-4 means shape `{d:3}` (three identical nonzero labels).
Any ordering has an adjacent zero-XOR edge on the closed walk.

**Census.** Valid two-repeat length-4 walks: **0**. Covering count **0**.

## Tariff consequence

No covering two-repeat partitioned dual exists at `Q=8`. There is therefore no
dirt-legal `R` and no complete-call tariff in this alphabet that can undercut
the six-query endpoint `436`. By comparison:

| Alphabet | Covering min R | Tariff floor (X=0) | Undercuts 436? |
|---|---:|---:|---|
| Distinct partitioned (`#2851`) | 92 | 488 | no |
| One-repeat partitioned (pending) | 112 | 528 | no |
| **Two-repeat partitioned (this)** | **— (covering 0)** | **—** | **no** |

## Scope limits

- Fixes the **two-repeat** (excess-2) partitioned independent-walk interface at
  total `Q=8`. Same-walk, dirty-shadow, distinct partitioned, and one-repeat
  leave-alones / pending tips are outside and not edited.
- Transfer-coupled dual/shapes, shared-XOR, and host screens remain deferred
  soft-overlaps and are not opened.
- No new kappa and no multiplication theorem are claimed.
