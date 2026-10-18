# A sharp stability-margin power for periodic scan rounding

The two-pass periodic scan in [PR628](https://github.com/CrocSwap/integer-mult-bounds/pull/628)
is sound under its stated hypotheses. Its proof gives the sufficient bound
`6(B+1)u/beta^3` and requires `u <= beta^2/2`.
Keeping a common geometric factor improves both conclusions.
This result concerns that scan, including its varying-coefficient extension.
It does not change the selected multiplication construction.

## Statement

Let `L >= 1`, `0 < beta <= 1`, and `B >= 0`.
For every cyclic sequence of exact complex coefficients and inputs, assume

```
|b_i| <= 1-beta,       |x_i| <= B.
```

Choose either cyclic orientation. Compute the zero-seed pass, the running
product, the closure division, and the second pass as in PR628.
Each completed complex operation has absolute rounding error at most `u`.
Assume `0 < u <= beta/2`. Then the rounded closure denominator is nonzero and

```
max_i |yhat_i - y_i| <= u (2B/beta^2 + 3/beta + 1)
                     <= 4(B+1)u/beta^2,
```

where `y_i-b_i y_(i-d)=x_i` is the unique periodic solution.
The bound is uniform in `L`, the orientation, and the coefficient pattern.
Nearest rounding of both components on a grid of spacing `u` meets the
operation-error hypothesis, since its complex error is at most `u/sqrt(2)`.
Coefficients are exact; coefficient approximation requires a separate budget.

## Proof

Relabel the chosen traversal as `1,...,L`.
Put `q_i=|b_i|`, `Q=product_i q_i`, and

```
G = sum_(j=1)^L product_(k=j+1)^L q_k.
```

An empty product is one. The exact affine return map is `s -> z+c*s`,
where `c=product_i b_i` and `z` is the last zero-seed value.
Thus the exact closure denominator is `d=1-c`.
The following identity is the key estimate:

```
1-Q = sum_(j=1)^L (1-q_j) product_(k=j+1)^L q_k >= beta*G.
```

Also `|d| >= 1-Q > 0`. Both rounded first-pass recurrences multiply
their previous errors by `b_i` and add one error of modulus at most `u`.
Consequently

```
|zhat-z| <= u*G,       |chat-c| <= u*G <= (u/beta)|d|.
```

With `dhat=1-chat`, the hypothesis `u <= beta/2` gives
`|dhat| >= |d|/2`. Computing `1-chat` is exact on the dyadic grid.
This is the step that avoids bounding the numerator and denominator with
two unrelated worst-case geometric sums.

The cyclic weighted shift has norm at most `1-beta` in the maximum norm.
Its Neumann inverse therefore has norm at most `1/beta`.
In particular, the exact periodic seed `s=z/d` satisfies `|s| <= B/beta`.
Before rounding the closure division,

```
|zhat/dhat-s|
  <= (|zhat-z| + |s| |dhat-d|)/|dhat|
  <= 2u/beta + 2B*u/beta^2.
```

Division rounding adds at most `u`.
At each output, the second pass attenuates the seed error by a factor at
most one and contributes at most `u/beta` from its own rounding errors.
This proves the first bound. The second follows from `beta <= 1`:

```
2B/beta^2 + 3/beta + 1 <= (2B+4)/beta^2 <= 4(B+1)/beta^2.
```

All statements include `L=1` and zero coefficients. No diagonalization,
probabilistic rounding assumption, or limit in `L` enters the proof.

## The inverse-square dependence is necessary for this algorithm

For every integer `k >= 2`, take a real one-entry input with

```
L=1, x=1, u=2^(-3k), a=2^(-k), beta=a+u/2, b=1-beta.
```

Use the implemented nearest rule, with ties toward positive infinity.
All inputs and coefficients are exact dyadics. The working grid is `u`.
The first-pass value is exactly one. Rounding the product `b*1` gives
`chat=1-a`, because `b` is exactly halfway between adjacent grid points.
The closure seed is exactly `1/a=2^k`.
The second-pass value is also exactly on the grid:

```
yhat = 1+b/a = 2^k-2^(k-1)u,       y = 1/beta.
yhat-y = b*u/(2*a*beta) >= u/(4*beta^2).
```

The inequality uses `a <= beta` and `b >= 1/2`.
Moreover `u <= beta^2/2`, so every example satisfies even PR628's older
precision admission. As `k` increases, `beta` tends to zero.
For any `q < 2`, no constant independent of `beta` can replace the error
bound by `C*u/beta^q` for this algorithm, even with `B=1` and `L=1`.
This is not a lower bound for other periodic solvers or a claim about an
optimally rounded exact closure product.

## Consequence for the existing factor cascade

Retain PR628's hypotheses and its exact certified factors.
An outer scalar or inner unit phase contributes at most one extra rounding
error `u` and has modulus at most one.
Thus each factor has error at most `5(B+1)u/beta^2`.
Put `n=r-1`, as in PR628. The unchanged exact prefix norm is bounded by
`r*beta^(-j)` after `j` factors. If `E_j` is the accumulated error, then

```
E_j <= E_(j-1)/beta
       + 5(r*beta^(-(j-1)) + E_(j-1) + 1)u/beta^2.
T_j = beta^j E_j
    <= (1+5u/beta)T_(j-1) + 5(r+1)u/beta.
```

For `u <= beta/(10n)`, the growth factor over `n` stages is at most
`(1+1/(2n))^n < 2`.
One elementary proof expands the binomial and bounds the degree-`j`
coefficient by `1/(2^j j!)`; the finite sum is strictly below
`sum_(j>=0) 2^(-j)=2`.
It follows that

```
E_n <= 10n(r+1)u*beta^(-(n+1)).
```

For `beta=2^-g`, the following sufficient fractional precision replaces
the execution budget in PR628's PROOF.md:

```
w_new = max(g + ceil(log2(10n)),
            p + (n+1)g + ceil(log2(20n(r+1)))).
```

It ensures `E_n <= 2^(-p-1)`. All coefficient, root, phase-oracle and
inverse-perturbation budgets stay as stated in PR628.
The original execution budget is

```
w_old = max(2g + ceil(log2(14n)),
            p + (n+2)g + ceil(log2(28n(r+1)))).
```

Both new terms are at most their old counterparts minus `g`.
Thus `w_new <= w_old-g`. This is a proved saving in a sufficient
execution-grid budget. It is not a measured speedup or a change to the
`O(p+r^4)` asymptotic precision and preparation bound.
The factor-cascade consequence inherits PR628's exact-factor and phase
assumptions; this package does not independently validate its factorizer.

## Attribution and status

PR628 by Chafik Boukhalfa supplies the algorithm, the original rounding
argument, its varying-phase extension, and the surrounding factor cascade.
Periodic affine closure and geometric error bounds are standard methods.
This note adds the shared-factor bound, the sharp family for this algorithm,
and the consequent execution guard. No literature-priority claim is made.
Prepared for Charles Bethin with substantial OpenAI Codex assistance.
No human peer review or proof-assistant verification is claimed.
New material uses Apache-2.0. Vendored notices remain intact.
