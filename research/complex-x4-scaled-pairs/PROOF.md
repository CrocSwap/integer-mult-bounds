# Nonunit power-of-two target pairs do not help this X4 panel

This is a scoped cost exclusion for the accepted PR799 scalar compensation
matrix, under its original binary-Horner lowering. It is not a lower bound for
complex suppliers, arbitrary dyadic circuits, or integer multiplication. The
finite census below and the universal elementary tail argument are separate.

## Exact class and complete bill

Write the compensation as `y <- y + C h`, with 112 target rows and 216 helper
sources. The 6,320 nonzero entries have integer quarter-coefficients in
`{-4,-3,-2,-1,1,2,3,4}`. These are the actual source-bound X4 entries, not the
historical 716-column `evidence/local` word. Targets and used helpers start in
frame zero. Helpers are arbitrary and are read without modification.

Choose ordered distinct target rows `(i,j)` and `lambda = s 2^e`, with
`s in {-1,+1}` and integer `e`. Let `T` perform `y_i += lambda y_j`. Replace this
pair's panel by:

1. Apply `T` to the arbitrary target inputs.
2. Add `(C_i + lambda C_j) h` to target `i`, and `C_j h` to target `j`.
3. Apply `T^-1` to the targets.

This is `T^-1 (T y + T C h) = y + C h`. Preparation cannot be omitted just
because a check initializes targets to zero. The inverse-transpose circuit
uses the inverse-transpose of each gate in the **same chronological order**.
All reads, signed accumulations, work preparation and clearing are charged.
No new helper, recursive call, nonzero-frame transition, or source mutation is
needed for this local algebraic mechanism. The exclusion already holds before
any additional precision, tape or integration expense is charged.

For nonzero reduced dyadic `q = +/- n / 2^d`, `n > 0`, the pinned emitter's
per-real-component cost is

```
H(q) = 3 + floor(log2(n)) + popcount(n) + d.
H(0) = 0.  [The zero matrix entry is omitted.]
```

This accounts for initial CLEAR and leading source ADD, binary doubles and
source additions, all denominator halvings, signed target accumulation, and
final CLEAR. This contribution does not replace that lowering with PR696's
shorter copy/unit lowering or share work across macros.

Define `H(row) = sum H(entry)`. Since row `j` is unchanged, the exact incremental
cost of the pair per real component is

```
Delta(i,j,lambda) = H(C_i + lambda C_j) - H(C_i) + 2 H(lambda).
```

The two basis shears cost `2 H(lambda) = 2 (4 + abs(e))`. Complex cost is twice
this entire bill. The census stores `saving = -Delta`, so a negative saving
means a loss. These are primitive counts, not measured runtimes or physical
memory-access counts.

## Finite core: all ordered rows, signs and exponents -3 through 3

There are `112 * 111 * 2 = 24,864` cases per exponent. The complete 174,048-case
census has these minimum incremental costs:

| Exponent e | Minimum extra real primitives (both components) | Profitable cases |
| --- | ---: | ---: |
| -3 | 630 | 0 |
| -2 | 368 | 0 |
| -1 | 106 | 0 |
| 0 | -744 | 2,978 |
| 1 | 20 | 0 |
| 2 | 196 | 0 |
| 3 | 372 | 0 |

“Real-component primitives” here counts both real coordinates of one complex
program, following the repository's `real_component_primitive_bound` field.
The certificate also gives per-single-component counts, the first maximizing
ordered pair/sign for each exponent, the minimum saving, and the digest of all
ordered records. Forward and inverse-transpose have the same panel bill: each
add is dualized to an add with the opposite sign, and `H(q)=H(-q)`.

Unit multipliers are deliberately retained as positive controls. The 2,978
profitable unit scores corroborate the census reported in ToikY's PR901 at
`dbe8dc01f8306bd7dab8d861a953b23e5cda6a70`; we neither import its implementation
nor claim a new unit schedule. Another synthetic quarter-grid panel with ten
entries `C_i=1/2`, `C_j=1/4` profits by 80 real primitives for `lambda=-2`.
Thus this exclusion depends on the X4 matrix, not just the dyadic alphabet.

## Infinite tails: exact affine cost for k >= 3

Each quarter-integer entry on either tail has the form

```
q_k = (a 2^k + b) / 2^D,    |a|, |b| <= 4,
D = 2      for e = +k,
D = k + 2  for e = -k.
```

For the positive tail take `(a,b)=(s Cj_quarters,Ci_quarters)`. For the negative
tail take `(a,b)=(Ci_quarters,s Cj_quarters)`. Handle absent entries as zero.

For any nonzero integer numerator `N`, before reduction the same price is

```
H(N / 2^D) = 2 + bitlen(abs(N)) + popcount(abs(N))
               + D - 2 min(v2(abs(N)), D).
```

If `a,b` are nonzero and `k>=3`, then `|b|<2^k` and
`v2(a 2^k+b)=v2(b)<=2`. The reduction term is therefore constant in `k`.
There is no zero numerator in this range.

* If `a,b` have the same sign, `abs(N)=|a|2^k+|b|`. Its binary blocks are
  disjoint: bit length grows by one per step, and popcount stays fixed.
* For opposite signs, `abs(N)=A2^k-B`, with `A=|a|`, `B=|b|`. Write it as
  `(A-1)2^k+(2^k-B)`. The low block has
  `popcount(2^k-B)=k-popcount(B-1)`; thus popcount grows by one. If `A>1`,
  bit length is `k+bitlen(A-1)`. If `A=1`, it is exactly `k`: for `k>=3` and
  `B<=4`, `2^(k-1) <= 2^k-B < 2^k`. This includes the boundary `k=3,B=4`.

Consequently the cost slopes, per component per increment of `k`, are:

| Entry case | Positive tail | Negative tail |
| --- | ---: | ---: |
| a=b=0 | 0 | 0 |
| a=0, b!=0 | 0 | 1 |
| a!=0, b=0 | 1 | 0 |
| ab>0 | 1 | 2 |
| ab<0 | 2 | 3 |

All slopes are nonnegative. Both basis shears together add another slope 2
per component. Hence every ordered pair's complete incremental cost increases
strictly along each tail, by at least 4 real primitives per exponent step.
The losing anchors at `e=+3` and `e=-3` therefore exclude every `|e|>=3`.
Together with `e=+/-1,+/-2`, this proves the claimed all-integer exclusion.
`verify.py` checks all 162 coefficient/direction families at seven exponents,
including 29 and 127; these finite tests corroborate, rather than prove, this
universal argument. The independent checker uses explicit Horner words.

## Consequence and boundary

Every nonunit power-of-two pair in this class strictly increases the original
panel cost by at least **20 real primitives per orientation**. In any family of
disjoint individually restored pairs, the costs add: removing each nonunit
pair and retaining the original rows strictly lowers cost. Therefore allowing
nonunit powers of two cannot improve the best attainable disjoint-pair cost
beyond the unit-only family. This does **not** identify that unit-family optimum.

Excluded from the statement: overlapping/sequential basis changes; multiple
shears before a joint restore; non-power-of-two dyadic multipliers; changes to
the helper basis; other compensation matrices; folding a boundary shear into
adjacent code; coefficient sharing; altered primitive lowering; or a different
frame, recursive or physical interface. We do not reject those mechanisms.
No candidate is installed and no prefix/precision improvement, new supplier,
new kappa, full native replay or proof-assistant result is claimed. The selected
construction's all-size/compiler, realization, hosting, precision/tape and
analytic assumptions remain as recorded in its maintainer review.
