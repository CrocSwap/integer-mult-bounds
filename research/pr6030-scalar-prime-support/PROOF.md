# Scalar prime support of the selected PR6030 word

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
No new κ. Assumption ID: `analytic_recovery`. This is one finite implication on the selected caller. It is not that assumption, and it is not any of the other four.

## 1. Proposition

Let the selected word be `research/p104-helper470-twin-rung-removal/WORD.json.gz` on canonical main `7c49fe32c55de02c2c873655c804b16e4c3fef0a` (PR #6030, κ = 781451/250000000). Its schema is `p104-accumulated-block-composition/2`. It has 770 public registers, 29 owned registers and 22,803 events.

Let `Q` be the multiset of rational coefficients on its 18,404 `ADD`, 861 `SCALE` and 23 `COPY` events (19,288 coefficients).

**Proposition.** Every `q` in `Q` is nonzero, and in lowest terms the only primes dividing its numerator or its denominator lie in `{2, 3, 5, 7}`. Writing `q = σ · 2^v · m` with `σ ∈ {±1}`, `v ∈ ℤ` and `m` a positive odd integer,

- `m ∈ {1, 3, 5, 7, 9}`,
- `v ∈ {-4, -3, -2, -1, 0, 1, 2, 3, 4}`.

The same census gives four sharp corollaries.

1. `16q` is an integer for every such `q`. The least positive integer with that property is 16, because both `1/16` and `-1/16` occur.
2. `|16q| ≤ 256` for every such `q`. The bound is attained at `q = -16` (three `ADD` events). The coefficient `+16` does not occur.
3. The odd-part histogram is `1` (19,162), `3` (114), `5` (9), `7` (2) and `9 = 3^2` (1). No coefficient has odd part `15`, `21`, `25`, `27`, `35`, or any prime at least 11.
4. Every `COPY` coefficient is `+1`. The denominator-16 witnesses and `q = -16` are `ADD` events.

This is the scalar-tape input an exact integer recovery of these coefficients would use: clear the denominator 16, then the only odd primes left are 3, 5 and 7. It does not prove analytic decomposition, fine-prime avoidance for Gaussian entries or `MOVE` charts, or the retained outer framework.

## 2. The 31 values

Each factorization is the reduced form of that rational. The count is the number of scalar events, summed over opcodes. `verify.py` pins the opcode-resolved multiset, whose 43 pairs add up to these rows.

| Coefficient | Count | Factorization |
|---|---:|---|
| `-16` | 3 | `- 2^4` |
| `-8` | 6 | `- 2^3` |
| `-4` | 107 | `- 2^2` |
| `-3` | 3 | `- 3` |
| `-9/4` | 1 | `- 2^{-2} · 9` |
| `-2` | 578 | `- 2` |
| `-3/2` | 16 | `- 2^{-1} · 3` |
| `-5/4` | 6 | `- 2^{-2} · 5` |
| `-1` | 2621 | `- 1` |
| `-3/4` | 32 | `- 2^{-2} · 3` |
| `-1/2` | 3271 | `- 2^{-1}` |
| `-3/8` | 2 | `- 2^{-3} · 3` |
| `-1/4` | 2736 | `- 2^{-2}` |
| `-1/8` | 179 | `- 2^{-3}` |
| `-1/16` | 3 | `- 2^{-4}` |
| `1/16` | 2 | `2^{-4}` |
| `1/8` | 171 | `2^{-3}` |
| `1/4` | 2960 | `2^{-2}` |
| `3/8` | 1 | `2^{-3} · 3` |
| `1/2` | 2657 | `2^{-1}` |
| `3/4` | 38 | `2^{-2} · 3` |
| `1` | 3319 | `1` |
| `5/4` | 1 | `2^{-2} · 5` |
| `3/2` | 16 | `2^{-1} · 3` |
| `7/4` | 2 | `2^{-2} · 7` |
| `2` | 452 | `2` |
| `5/2` | 1 | `2^{-1} · 5` |
| `3` | 6 | `3` |
| `4` | 75 | `2^2` |
| `8` | 22 | `2^3` |
| `10` | 1 | `2 · 5` |

The row sums are 19,288. The odd parts that are not 1 are exactly the rows containing 3, 5, 7 or 9, and those rows sum to 114 + 9 + 2 + 1 = 126. The two rows with denominator 16 sum to 5. The single row `-16` is the unique place where `|16q| = 256`.

The 2-valuation histogram, read off the same table, is

| Valuation | Count |
|---:|---:|
| `-4` | 5 |
| `-3` | 353 |
| `-2` | 5,776 |
| `-1` | 5,961 |
| `0` | 5,949 |
| `1` | 1,031 |
| `2` | 182 |
| `3` | 28 |
| `4` | 3 |

Valuation `+4` occurs only at `-16`. Valuation `-4` occurs only at `±1/16`.

## 3. Binding

`verify.py` checks SHA256 `7834725d9e34ee846a9ccc615221ea81e0201613938afa185d2eda0c9a6c232f` of the gzip word, requires schema `p104-accumulated-block-composition/2`, and requires the opcode-resolved multiset of every `ADD`, `SCALE` and `COPY` coefficient. It recomputes the odd part and the 2-valuation of each published value and requires the two histograms above. A coefficient whose reduced denominator is odd, whose odd part is outside `{1, 3, 5, 7, 9}`, whose valuation is outside `[-4, 4]`, or whose cleared absolute value exceeds 256 is rejected. The controls are the rationals `0`, `11`, `1/3`, `1/32`, `32`, `15`, `27` and `1/48`.

The argument is this finite identification. It is not an all-size statement about every caller, and a match at one word does not discharge `analytic_recovery`.

## 4. What this does not use

`#6635` proves that these same scalar instructions act by one width-free matrix at every column multiplicity. That argument treats the coefficient as an arbitrary nonzero rational that factors out of the tensor power. It does not classify the rationals. `#6293` is the `MOVE` phase factor. `#6522` is the coordinate-envelope exponent `2^(10^9+240152f)`. The selected review says dyadic coefficients obey the primary's fixed bounds and does not record this prime support or the constant 16.
