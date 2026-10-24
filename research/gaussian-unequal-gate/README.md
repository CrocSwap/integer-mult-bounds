# One section error and one global tail fit the same gate

**Claim type:** an explicit absorption bound for one unequal sum.
**No new κ.** The section error, the global tail, and the ceiling `9 p^2`
stay hypotheses. The selected record remains `23/10000`.

## Question

#4523 separates the tails and asks whether the restricted gate absorbs one
section error `p^6 exp(-p^2)` and one global tail `p^{10} exp(-p^2)`. The
named step is to place the factor `1 + p^4` in the exponent. The factor 2
from two equal errors is not this sum.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
g (9 p^2)^{g-1} p^6 (1 + p^4) exp(K p - p^2) < 2^{-C p}.
```

The case `K = 0` is the monomial in the question. The factor `1 + p^4`
contributes `4 L + 1`. The exponent is at most `-C p - 1`. Whenever
`g log p = o(p)`, every fixed pair `K, C` satisfies the gate for all large
`p`. At `g = p^2` the monomial is greater than 1 for every integer `p ≥ 2`.

The coefficient still needs four bits, because `9 < 16` and `9 > 8`.

## Proof

The two tails add on the `p^6` scale:

```text
p^6 exp(-p^2) + p^{10} exp(-p^2) = p^6 (1 + p^4) exp(-p^2).
```

The section term is the strict within-cell majorant. The global term is
HALO's closed majorant. Their sum is therefore strictly below the right-hand
side. At `p = 2` the integer shadow is `64 + 1024 = 64 · 17`.

#4496 places

```text
g (9 p^2)^{g-1} p^6 exp(K p - p^2)
```

strictly below `2^{E_0}`, where

```text
E_0 = 2 g L + 4 g + 5 L - 3 + 2 K p - p^2
```

and `E_0 ≤ -C p - 3` under this gate. Since `p ≤ 2^L` and `p^4 > 1`,

```text
1 + p^4 < 2 p^4 ≤ 2^{4 L + 1}.
```

The comparison is strict even when `p` is a power of two. Four powers of
`p` alone are not enough: at `p = 2`, `1 + 16 = 17 > 16`. The new exponent is

```text
E = E_0 + 4 L + 1 = 2 g L + 4 g + 9 L - 2 + 2 K p - p^2.
```

Clear eight times `E + C p`. The pieces scale as `8 · 2 g L = 16 g L ≤ p`,
`8 · 4 g = 32 g ≤ 2 p` because `L ≥ 1`, `8 · 9 L = 72 L ≤ 9 p` because
`8 L ≤ p` for every integer `p ≥ 64`, and `8 (2 K + C) p ≤ 4 p^2` once
`p ≥ 4 K + 2 C`. The constant `-2` contributes `-16`. The sum is at most

```text
-4 (p^2 - 3 p + 4).
```

At `p = 2` the polynomial equals 2, and the step to the next integer is
`2 p - 2 ≥ 2`. Eight times `E + C p` is therefore at most `-8`, and
`E ≤ -C p - 1`. The monomial is strictly less than `2^E`, hence strictly
less than `2^{-C p}`.

The same induction `8(m + 1) ≤ 2^m` for `m ≥ 6` gives `8 L ≤ p`. Its base
is `8 · 7 = 56 ≤ 64`.

At `g = p^2` the monomial is `(1 + p^4)` times a quantity already greater
than 1 in #4496, and `1 + p^4 > 1`. The gate is not optional for every `g`.

## Not covered

- A proof of either tail. The section bound needs the ideal-gap gauge.
  HALO assumes `||H^{-1}||_2 ≤ p^{10}` and this package does not prove it.
- A proof that every tensor factor is at most `9 p^2`. A trailing global
  factor may only be known up to `p^{10}`.
- Editing the #4100 notes. They still say `p^{10} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-unequal-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-unequal-gate
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:28:17Z and was
that commit.

Overlap snapshot: open PRs fetched 2026-10-22T03:29:09Z (309 records) and
discussions fetched 2026-10-22T03:29:52Z (3402 records). A search for
`1 + p^4`, `unequal` and `p^6 (1 + p^4)` returned #4523, which asks this
question, and this draft. The word `unequal` also hits unrelated endpoint
and cycle packages. No result places `1 + p^4` in the four-bit exponent.
A search miss is not a novelty certificate. #4496 is the fold. #4523 is
the tail separation. HALO is the written global tail.

## Open next questions

1. **Does the gate absorb the heaviest slice when a trailing factor is
   `p^{10}` rather than `9 p^2`?** The bound above keeps every ceiling at
   `9 p^2`. HALO's written inverse bound is `p^{10}`. The first step is to
   test the slice `(p^{10})^{g-1} p^6 (1 + p^4) exp(-p^2)`. Do not prove
   `||H^{-1}||_2 ≤ p^{10}`.

## Credit

- The fold exponent `-C p - 3` is #4496's.
- The equal-error factor 2, which this sum replaces, is #4520's.
- The separation of the two tails is #4523's.
- The within-cell `p^6` majorant is #4452's.
- The written global tail is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
