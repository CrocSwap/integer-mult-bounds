# Exact even-subset readout floor at seven queries among X = 6

This is a scoped obstruction and sharpness statement in the five-source
common-B mutable-source alphabet of
[PR1898](https://github.com/CrocSwap/integer-mult-bounds/pull/1898).
It does not claim a new kappa, physical supplier tariff, or readout optimum
outside the even-subset connector-state class.

It answers open question 1 of
[CrocSwap/integer-mult-bounds#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643)
(`research/seven-query-xor-floor`): what is the minimum readout count `R`
among restored seven-query words with `X = 6`? Under even-subset readout on
connector states, the answer is **exactly 82**.

## Setup

Retain five distinct arbitrary-dirty F₂ source rows, thirty-one outputs, a
connector, and private scratch. Complete calls are `Q_j`, `R_m`, and paid
`X_(s,t)` as in PR1898. Straight-line words are data-independent; sources and
connector restore.

Each query contributes an effective F₂⁵ mask (the current linear form of the
queried source). Connector restoration forces those seven masks to sum to
zero, so the connector state follows a **closed walk of length 7** in F₂⁵.
Even-subset readout prices a slot list `(s₀,…,s₆)` with `s₀ = 0` by

```text
R = Σ_{m=1}^{31} min{|T| : T ⊂ {0,…,6}, |T| even, ⊕_{i∈T} s_i = m}.
```

Zero query edges are forbidden, so consecutive slots differ and the return
edge to 0 is present (`s₆ ≠ 0`).

## Classification of covering walks

A covering slot list must realize every nonzero mask, so the F₂-span of its
slot values is all of F₂⁵. Hence it uses at least five linearly independent
nonzero labels. With only six slots after the leading 0, the covering cases
are:

1. **Six distinct nonzero labels.** The intermediate slots are a permutation
   of those labels (Hamilton walks on `{0} ∪ S`). Exhaustive even-subset
   census over all `C(31,6)` choices yields covering sets only, with
   attainable totals **`R ∈ {82, 88}`** (histogram `97216` / `486080`).
2. **Five spanning nonzero labels with exactly one repeated vertex.** Any
   such spanning 5-set is `GL(5)`-equivalent to the standard basis
   `{1,2,4,8,16}`, and the even-subset total `R` is `GL(5)`-invariant.
   The basis census of valid one-repeat walks (extra visit to `0`, or one
   basis vector doubled) covers in every case with **`R = 96` only**
   (`1680` walks).
3. **Fewer than five independent nonzero labels.** The even-subset image lies
   in a proper subspace, so some masks are missed. Explicit dependent samples
   stay at image size `≤ 16`.

Therefore every covering Q=7 even-subset schedule has `R ∈ {82, 88, 96}`, and
the global minimum is **82**.

## Minimum R among X = 6

Open [#2643](https://github.com/CrocSwap/integer-mult-bounds/pull/2643) proves
that every restored seven-query word needs `X ≥ 6` (sharp). Combined with
`R ≥ 82` in the even-subset class, every restored seven-query word with
`X = 6` has even-subset `R ≥ 82`.

The credited path-lowered champion

```text
(0, 1, 2, 6, 12, 24, 16, 0)
```

attains `7 Q / 82 R / 6 X` (abstract tariff **442** at `(b,a,x)=(38,2,2)`).
Dirty root and inverse identities hold. Thus the minimum is **exactly 82**.

## Tariff consequence

At `Q = 7` and `X = 6`, tariff `38·7 + 2R + 2·6 = 278 + 2R` undercuts the
six-query endpoint **436** iff `R ≤ 78`. The floor `R = 82` gives tariff
**442** and blocks that undercut inside the even-subset class.

## Scope limits

- No claim about readout alphabets cheaper than even-subset connector-state
  combinations (odd-cardinality schedules, output mixing, extra connectors).
- Leave-alone objects through #2643 (including #2593 triadic and the XOR
  floor package) and pending `mutable-source-789q-invoice` are not edited.
- No physical common-B hosting, precision, tape, or new kappa.

## Relation to predecessors

| Prior | Already proves | This package adds |
|---|---|---|
| PR1898 | Min `Q = 6`, endpoint tariff 436 | — |
| PR2455 (open) | `X ≥ 8` at `Q = 6` | — |
| 789q invoice (fork) | Path-class distinct-slot `R ∈ {82,88}` at `Q = 7` | — |
| #2643 seven-query XOR floor | `X ≥ 6` at `Q = 7`, sharp; OQ1 asks min `R` at `X = 6` | — |
| **This** | — | **Min even-subset `R` at `Q = 7` is 82 even with repeats; hence min `R` among `X = 6` is 82** |
