# The restricted monomial keeps the four-bit gate

**Claim type:** an explicit absorption bound for one scalar monomial.
**No new κ.** The ceiling `9 p^2` and the section error `p^6 exp(-p^2)`
stay hypotheses. The selected record remains `23/10000`.

## Question

#4517 bounds the kept core outputs by

```text
2 g M^{g-1} ε,
```

and asks whether that scalar, at `M = 9 p^2` and `ε = p^6 exp(-p^2)`,
still lies below `2^{-C p}`. The named step is to replace the base
`9 p^2 + ε` in #4506 by `9 p^2` and recheck the four-bit gate.

## Lemma

Let `p ≥ 2`, `g ≥ 1`, `K ≥ 0` and `C ≥ 0` be integers, and let
`L = ceil(log2 p)`. If

```text
p ≥ max(64, 4K + 2C)    and    16 g L ≤ p,
```

then

```text
2 g (9 p^2)^{g-1} p^6 exp(K p - p^2) < 2^{-C p}.
```

The case `K = 0` is the monomial in the question. The factor 2 is one bit.
The exponent is at most `-C p - 2`. Whenever `g log p = o(p)`, every fixed
pair `K, C` satisfies the gate for all large `p`.

Four bits still majorize the coefficient, because `9 < 16`. Three bits do
not: `9 > 8`. Removing `ε` from the base does not change that count. It
removes the separate room `p^6 exp(-p^2) < 1/2` used by #4506.

At `g = p^2` the monomial is greater than 1 for every integer `p ≥ 2`.

## Proof

The series `1 + 1 + 1/2 = 5/2 > 2` gives `e > 2`, so `exp(-p^2) < 2^{-p^2}`.
For `k ≥ 2`, `k! ≥ 2^{k-1}`. The tail of `e` is then at most a geometric
series of ratio `1/2`, so `e < 4` and `exp(K p) < 2^{2 K p}` whenever
`K p > 0`. At `K = 0` the factor is 1.

#4496 places the telescoping monomial strictly below `2^{E_0}`, where

```text
E_0 = 2 g L + 4 g + 5 L - 3 + 2 K p - p^2,
```

and proves `E_0 ≤ -C p - 3` under this gate. The identity behind that
exponent is `g (9 p^2)^{g-1} p^6 = g (9 p^2)^g (p^4 / 9)`, with
`p^4 / 9 < 2^{4 L - 3}` because `9 > 8` and `p ≤ 2^L`. The factor 2 in
the present monomial multiplies that bound by `2^1`, so the new exponent is

```text
E = E_0 + 1 = 2 g L + 4 g + 5 L - 2 + 2 K p - p^2.
```

Clear eight times `E + C p`. The pieces scale as `8 · 2 g L = 16 g L ≤ p`,
`8 · 4 g = 32 g ≤ 2 p` because `L ≥ 1` turns the gate into `16 g ≤ p`,
`8 · 5 L = 40 L ≤ 5 p` because `8 L ≤ p` for every integer `p ≥ 64`, and
`8 (2 K + C) p ≤ 4 p^2` once `p ≥ 4 K + 2 C`. The constant `-2` contributes
`-16`. The sum is at most

```text
-4 (p^2 - 2 p + 4).
```

At `p = 2` the polynomial equals 4, and the step to the next integer is
`2 p - 1 ≥ 1`. Eight times `E + C p` is therefore at most `-16`, and
`E ≤ -C p - 2`. The monomial is strictly less than `2^E`, hence strictly
less than `2^{-C p}`.

The same induction `8(m + 1) ≤ 2^m` for `m ≥ 6` gives `8 L ≤ p` on
`p ≥ 64`. Its base is `8 · 7 = 56 ≤ 64`.

The three-bit comparison still reverses: `(9 p^2)^g > 2^{3 g} p^{2 g}`.
At the legal point `p = 128`, `L = 7`, `g = 1`, both the three-bit and
four-bit exponents are negative, while `9 p^2 > 8 p^2`.

At `g = p^2` the monomial is twice the #4496 monomial. That smaller
monomial is already greater than 1, because `(9 p^2)^{p^2} > 4^{p^2}`
and `4 > e`, while `p^4 / 9 > 1`. The extra factor 2 keeps it above 1.

## Not covered

- A proof of the restricted tensor bound in #4517. This package absorbs
  the scalar only after `M = 9 p^2` and `ε = p^6 exp(-p^2)` are granted.
- A proof that `||C_i|| ≤ 9 p^2`, or that `||P_glob - C_i||_2 < ε`.
- Either ideal-gap hypothesis.
- Editing the #4100 notes. They still say `g p^{10 g} exp(-p^2)`.
- Any new κ.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-restricted-gate --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-restricted-gate
```

Base `f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc`, priority revision 7, selection
refresh κ = `23/10000`. Upstream was fetched at 2026-10-22T03:18:46Z and was
that commit.

Overlap snapshot: open PRs fetched 2026-10-22T03:21:17Z (305 records) and
discussions fetched 2026-10-22T03:21:59Z (3397 records). A search for
`restricted bound`, `(9 p^2)^{g-1}` and `Cp - 2` returned #4496, which
absorbs the monomial without the factor 2, and #4506, which absorbs the
factor 2 only after the base has grown by `ε`. The other hits are the
predecessor gate and unrelated restricted bounds. No result charges the
factor 2 against the fold slack of 3. A search miss is not a novelty
certificate. #4496 is the fold. #4506 is the larger base. HALO is the
written error.

## Open next questions

1. **Is `||P_glob - C_i||_2` below `p^6 exp(-p^2)`, or only the written
   `p^{10} exp(-p^2)`?** The restricted monomial uses the section error.
   The global tail in HALO is `p^{10}`. Replacing the section error by
   that tail would add `4 L` to the exponent. The first step is to compare
   `P - H^{-1} = -Q^J H^{-1}` with the within-cell `p^6` bound, and not
   to put `p^{10}` into this gate yet.

## Credit

- The fold exponent `-C p - 3`, and the factor `p^4 / 9`, are #4496's.
- The face-factor inequality with base `9 p^2 + ε` is #4506's.
- The restricted scalar `2 g M^{g-1} ε`, and this question, are #4517's.
- The four-bit gate is #4495's.
- The written error `g p^{10 g} exp(-p^2)` is #4100's.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
