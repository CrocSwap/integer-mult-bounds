# The fixed-kernel102 ceiling survives removal of fallback charges

This is a theorem about the finite packing model in [PR525](https://github.com/CrocSwap/integer-mult-bounds/pull/525)
at `71acd0c35ee81de848316b3f2b4c3bd15b219c51`. Its local profile and inventories
are hypotheses; their realization by the supplier is outside this audit.

There are 72 calls, dimension `m = 73`, and live stock `W = 7680`. One call has
the following paid rank profile and whole-helper widths:

| Rank | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Multiplicity | 2537 | 192 | 506 | 88 | 298 | 68 | 1 | 17 |

| Helper width | 7 | 8 | 9 |
|---|---:|---:|---:|
| Multiplicity per call | 18 | 164 | 378 |

The original idle children have ranks 8, 16, 32, 48 with respective counts
5760, 3840, 3840, 3840. Every helper is assigned once, wholly inside one idle
child. Each child leaves at most one paid remainder. We drop timing, owner,
and chart constraints, and allow nonnegative real pattern multiplicities.
Every physical allocation satisfying these hypotheses is in this relaxation.

For a bin rank `R`, a pattern is `(n7,n8,n9)` of nonnegative integers with
`7*n7 + 8*n8 + 9*n9 <= R`; its leftover is `s = R - 7*n7 - 8*n8 - 9*n9`.
The verifier enumerates all 112 such patterns, including the empty pattern.

At `b = 6981767/5000000000`, put

```
c_b(0) = 0
c_b(s) = s*((73/s)^b - 1), s > 0.
```

Use these rational dual multipliers:

| Bin rank R | eta_R |
|---|---:|
| 8 | 3447293/500000000 |
| 16 | 3447293/250000000 |
| 32 | 5515669/200000000 |
| 48 | 1756813/62500000 |

| Width w | lambda_w |
|---|---:|
| 7 | -10847507113/1000000000000 |
| 8 | -1723646571/250000000000 |
| 9 | -183854091/62500000000 |

The lambda values are PR525's published dual. Each eta is its published value
rounded downward to a multiple of `10^-9`. These small reductions allow the
positive fallback costs used by PR525's original checker to be omitted.

For every pattern, exact arithmetic proves

```
c_b(s) >= eta_R + n7*lambda_7 + n8*lambda_8 + n9*lambda_9.
```

Multiply each inequality by its nonnegative pattern multiplicity and sum. The bin-count
equalities yield `sum_R stock_R*eta_R`; the helper-count equalities yield
`72*sum_w widths_w*lambda_w`. This is weak duality, including for fractional
allocations. No solver or assertion about an optimizer is needed.
The negative lambda values are valid because every helper count is an equality,
not a one-sided capacity inequality.

The remainder rank mass is invariant:

```
sum_R R*stock_R - 72*sum_w w*widths_w = 66240.
```

Adding the local rank mass gives `73*7680 - 2496 = 558144`. Therefore the ideal
moment of every relaxed allocation has lower bound

```
[558144 + 72*sum_r profile_r*c_b(r)
        + sum_R stock_R*eta_R + 72*sum_w widths_w*lambda_w] / (73*7680).
```

The verifier proves this exceeds `1 + 7/10^10`. The smallest certified pattern
slack exceeds `2/10^11`; the exact rational values are in `EXPECTED.json`.

## Independent rational arithmetic

For `1 <= y <= 2`, set `z = (y-1)/(y+1)`. The identity

```
log(y) = 2*sum_{j>=0} z^(2*j+1)/(2*j+1)
```

has nonnegative terms. Its first 20 terms are a lower bound. Write `x = 2^k*y`
with `1 <= y < 2` and add `k` times the same lower bound for `log(2)`.
For `t >= 0`, the first nine terms `sum_{j=0}^8 t^j/j!` are a lower bound for
`exp(t)`. Monotonicity of exp lets us use the lower log bound as its argument.
Both stages round downward to multiples of `2^-128`. Thus every computed
cost is rigorously at most `c_b(s)`. No tail estimate is needed for these
one-sided inequalities. Rank zero is handled separately with exact cost zero.
The implementation uses only integer arithmetic and `fractions.Fraction`.

## Consequence and limits

The ideal moment is strictly increasing in `b >= 0`, since all positive ranks
are below 73. Any endpoint passing the strict moment test must satisfy

```
b < 6981767/5000000000.
```

Under the same outer relation `kappa <= b/(1+b)` used for PR525's ceiling,
this implies `kappa < 6981767/5006981767`, about `0.001394406315999672`.
Adding any nonnegative fallback
charge preserves the exclusion. The obstruction is already present in the
ideal rank moment; it does not depend on those charges.

This is the same numerical ceiling as PR525, with a weaker cost assumption and
an independent short proof. It does not exclude changed local words, changed
helper widths or idle stocks, split-helper contracts, different paid-remainder
models, or other multiplication algorithms. It neither improves the selected
construction nor certifies PR525's scalar, physical, outer-assembly, or all-size
obligations. The frozen word hash is provenance, not a reconstruction here.
