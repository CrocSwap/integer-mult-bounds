# The constant-1 evaluator on accepted reservoir layouts

This is a counting proof for one binding step inside Cinna Davis's PR #4100,
`CRT.md` §2–§4. It connects two merged packages. It is not an acceptance of
that construction, and it does not change κ.

- PR #4377 (`research/crt-uniform-evaluator`) proves that the control
  evaluator costs at most `E(p, ell) = 2^{4 ell} (p+2)^{16}` bit-steps,
  so `C_E = 1`. Its domain is `p >= 2`, `ell >= 1`, a CRT group of bit
  length `W <= p`, and a batch of at most `A <= 8(p+2)` target axes.
- PR #4174 (`research/crt-reservoir-placement`) constructs the layouts
  and the reservoir batches of `CRT.md` §3.

PR #4377 left the use of `C = 1` inside §3–§4 open, first at the `H >= G`
comparison, because placement geometry was not yet an input. PRs
#4921 and #4923–#4926 then carried the coefficient `C_E` through the product line
without evaluating it. This note supplies that binding.

## Setting

The #4174 constructor `Layout(p, ell, widths)` accepts exactly when

```text
p >= 1,  ell >= 2,  ell >= λ := ceil(log2(p+2)),
d = len(widths) is a power of two at least 51200,
every width is ell-1 or ell,
r_max = floor(L / (100 G)) >= 1,
```

where `L` is the sum of the widths and `G = 64 (ell + λ)`. It sets
`H = r_max G`. Every plan has at most `r_max` active axes. Every control
group is the complete left child of a tree node, which is a set of logical
axes.

The extra hypothesis is

```text
(A)   L <= p.
```

PR #4328 introduced (A) for the absorption step, and #4646 uses it. At the
actual #4100 caller it holds: #4377's size paragraph shows that the dyadic
length satisfies `log2 T <= b + 1 <= p` with `p = 6b`, and `log2 T` is the
sum of the axis widths. The #4174 production plan has `p = 6L`.

## Theorem

Let `Layout(p, ell, widths)` be accepted, and assume (A). Then:

1. `ell >= 21`, `λ >= 21`, `p >= 1310720`, and `G >= 2688`. All four
   bounds are attained together by `p = 1310720`, `ell = 21`,
   `d = 2^16` and every width 20.
2. Every #4377 hypothesis holds: `p >= 2`, `ell >= 1`, every control
   group has `W <= L <= p`, every batch has at most
   `r_max <= floor(p / 268800)` axes, and the layout has at most
   `d <= floor(p / 20)` axes. The last two are below `8(p+2)`. So one
   evaluation costs at most `E(p, ell) = 2^{4 ell} (p+2)^{16}` bit-steps,
   with `C_E = 1`. This holds whether #4377's batch is read as one
   reservoir batch or as all axes.
3. `H >= G`, and

   ```text
   2^{-H} E  <=  2^{-G} E  <=  2^{-60 ell - 48 λ}  <=  2^{-2268}.
   ```

   The maximum `2^{-2268}` of `2^{-G} E` over these layouts is attained
   at `p = 2^{21} - 2`, `ell = 21`, `d = 2^16` and every width 20.
4. For `r <= r_max` targets with digit failures `2/B` and either window
   term, `β = 2 (2^G - 2) 2^{-64G}` or the published `8B/2^K`, the
   bad-key evaluation charge per record satisfies

   ```text
   r (2/B + window) E  <  (p / 89600) 2^{-G} E  <  2^{-2263}.
   ```

   With `C_E = 1`, this replaces #4646's printed
   `(C_E p / 6400) 2^{-60 ell} (p+2)^{-48}`.

Without (A), part 2 fails for an accepted layout. `p = 2`, `ell = 2`,
`d = 2^19` and every width 2 is accepted with `L = 2^20`, `G = 256` and
`r_max = 40 > 32 = 8(p+2)`. Its root control group has `W = 2^19 > p`.

## Proof

**Part 1.** `d` is a power of two at least 51200, so `d >= 2^16`. Every
width is at least `ell - 1`, so `L >= 2^16 (ell - 1)`. By the definition
of `λ`, `2^λ >= p + 2 > p`. With (A) and `ell >= λ`,

```text
2^16 (ell - 1) <= L <= p < 2^λ <= 2^ell,
```

so `ell - 1 < 2^{ell - 16}`. For `2 <= ell <= 16` the right side is at
most 1, and `ell - 1 >= 1`. For `17 <= ell <= 20` the right side is at
most 16, and `ell - 1 >= 16`. Both cases are contradictions, so
`ell >= 21`. Then `p >= L >= 2^16 · 20 = 1310720`. Since
`p + 2 >= 1310722 > 2^20`, `λ >= 21` and `G = 64(ell + λ) >= 2688`.

For the witness, `λ = ceil(log2 1310722) = 21 = ell`. Also
`L = 1310720 = p`, `G = 2688`, and `r_max = floor(1310720 / 268800) = 4`.

*Remark.* The actual caller gives the stronger `L <= b + 1` with
`p = 6b`. Then `6 (2^16 (ell - 1) - 1) <= p <= 2^ell - 2`. This fails for
`ell = 23` (`8650746 > 8388606`) and for every smaller `ell`, so
`ell >= 24` there. The #4174 production plan `p = 9240576`, `ell = 24`
attains it. The theorem below uses only (A).

**Part 2.** By part 1, `p >= 2` and `ell >= 1`. A control group is a set
of axes, so `W <= L <= p`. By part 1, `100 G >= 268800`, so
`r_max = floor(L / (100G)) <= floor(p / 268800)`. Also
`d <= L / (ell - 1) <= p / 20`. Both are below `p < 8(p+2)`. Thus
#4377's proposition applies with `C = 1`.

**Part 3.** The constructor requires `r_max >= 1`, so `H = r_max G >= G`.
#4174's PROOF.md derives the same fact from `d >= 51200`. Then
`2^{-H} E <= 2^{-G} E`. Using `G = 64 ell + 64 λ` and `p + 2 <= 2^λ`,

```text
2^{-G} E = 2^{-60 ell - 64 λ} (p+2)^{16} <= 2^{-60 ell - 48 λ}.
```

This is at most #4100's display `2^{-60 ell} (p+2)^{-48}`, since
`(p+2)^{-48} >= 2^{-48 λ}`. With `ell, λ >= 21` it is at most
`2^{-2268}`. Equality needs `ell = λ = 21` and `p + 2 = 2^{21}`. The
witness `p = 2097150` is accepted with `L = 1310720 <= p`, `G = 2688` and
`r_max = 4`.

**Part 4.** `2/B = 2^{1-G}`. The sharp window is `β < 2^{1-63G}`.
The published window is `8B/2^K = 2^{3-63G}`, with `K = 64G`. Either way,

```text
2/B + window <= 2^{-G} (2 + 2^{3-62G}) < 3 · 2^{-G}.
```

By (A) and part 1, `r <= r_max <= p / (100G) <= p / 268800`. So
`r (2/B + window) < 3p 2^{-G} / 268800 = p 2^{-G} / 89600`. Multiply by
`E`. By part 3, `2^{-G} E <= 2^{-60 ell - 48 λ}`. Since `p < 2^λ`,

```text
(p / 89600) 2^{-G} E < 2^{-60 ell - 47 λ} / 89600 <= 2^{-2247} / 2^{16}
                     = 2^{-2263}.
```

**Counterexample without (A).** `p = 2` gives `λ = 2`, so `ell = 2` is
allowed and `G = 256`. Here `d = 2^19 >= 51200`. With every width 2,
`L = 2^20`, so `r_max = floor(2^20 / 25600) = 40 >= 1`. The constructor
accepts it. `8(p+2) = 32 < 40`. The root left child has `2^18` axes and
`W = 2^19`. ∎

## What this does not prove

- The ordinary H-bit interchange callee and its `O(V H^{1-a} + V)` bill.
- Sparse repair sorting, reinsertion or fixed-tape radix passes.
- The finite range that falls back to elementary multiplication.
- The #4377 bit-step model itself. It is used as stated, not replayed.
- Any statement about layouts that violate (A).
