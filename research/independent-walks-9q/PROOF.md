# Partitioned independent duals at Q=9 cannot undercut tariff 436

This is a scoped obstruction in the five-source common-B mutable-source alphabet
of [PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898) at unit
tariff `(b,a,x)=(38,2,2)`. It names one freestanding `#840`-style priced
readout alphabet: the **Q=9 partitioned independent dual companion** of the
Q=8 distinct partitioned dual
([#2851](https://github.com/CrocSwap/integer-mult-bounds/pull/2851)). It answers
preferred next20 and open question 2 of pending
`cursor/independent-walks-threerepeat-8q-60b9@94b14c36`.

No new kappa is claimed. Leave-alone packages through #2867 are not edited.
Pending three-repeat tip is not edited or competed.

## Setup

Retain queries `Q_j`, readouts `R_m: y_m += A_m z`, and paid source shears
`X_(s,t)`. A **restored walk** of length `n≥2` is an open slot list starting at
`0` whose closed completion has only nonzero edges.

A **partitioned independent dual** of total query count `Q = 9` is a pair of
valid restored walks of lengths `(n_0,n_1)` with `n_0+n_1=9` and `n_0,n_1≥2`,
distinct nonzero labels within each walk, and **independent dirt**. Legal dirty
cancellation requires even live-read parity on each walk separately. With even
subset tables `e_i` on walk `i`, the dual cost is

```text
R = Σ_{m=1}^{31} min_α (e0[α] + e1[α ⊕ m]).
```

Up to swap the only partitions are `(2,7)`, `(3,6)`, and `(4,5)`. Length-1
components are not restored. The abstract complete-call tariff at
`(b,a,x)=(38,2,2)` is `38·Q + 2·R + 2·X`.

The same-walk Q=9 path-lowered floor of
[#2677](https://github.com/CrocSwap/integer-mult-bounds/pull/2677) is
`R≥62` ⇒ tariff `≥466`. Beating the six-query endpoint `436` at nine queries
would require `R+X < 47`; every dirt-legal even covering already forces
`R≥62`, so the undercut question is settled once the partitioned dual census
shows its own floor lies at or above that regime.

## Fixture A: partition `(2,7)`

Short walk `(0,σ)` has `e[0]=0`, `e[σ]=2`. Dual cost collapses to

```text
R = Σ_m min( e1[m],  2 + e1[m ⊕ σ] ).
```

**Census.** Distinct-label pairs: covering count `20512576`; attainable
`R ∈ {80,82,86,88,92,100}` with histogram
`972160 / 2041536 / 6319040 / 8749440 / 972160 / 1458240`. Minimum `R = 80`.

Champion `((0,19),(0,1,2,4,8,15,16))` has independent `R = 80`, path `X = 26`,
tariff `554`. The `X = 0` figure `502` is the abstract lower bound from
`R = 80`.

## Fixture B: partition `(3,6)`

**Census.** Covering count `69370560`; attainable
`R ∈ {88,90,92,94,96,100,104}` with histogram
`3749760 / 20623680 / 11249280 / 5624640 / 21873600 / 5624640 / 624960`.
Minimum `R = 88`.

Champion `((0,1,2),(0,4,8,13,16,22))` has independent `R = 88`, path `X = 18`.

## Fixture C: partition `(4,5)`

**Census.** Covering count `122561600`; attainable
`R ∈ {92,94,96,98,100,104}` with histogram
`4166400 / 37497600 / 43747200 / 3472000 / 31248000 / 2430400`.
Minimum `R = 92`.

Champion `((0,1,2,4),(0,7,8,16,25))` has independent `R = 92`, path `X = 22`.

## Global consequence

The binding covering minimum across `(2,7)/(3,6)/(4,5)` is `R = 80` on
`(2,7)`. At `X = 0` the abstract tariff is

```text
38·9 + 2·80 + 2·0 = 502 > 436
```

and also `502 > 466` (same-walk Q=9 floor). Positive path `X` only increases
the bill. Therefore no covering partitioned independent dual at nine queries
undercuts the six-query endpoint after a complete dirty bill.

## Machine check

`verify.py` exhaustively recomputes all three covering histograms and matches
`CERTIFICATE.json`. `independent.py` recomputes the binding `(2,7)` census and
champion identities without importing `model.py`. Admission uses `need()` so
`-O` passes. Default verify is read-only.
