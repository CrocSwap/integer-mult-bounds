# The integral square obstruction

Let `C` be a nonempty subset of `F_2^16`, with no repeated words, such that
`x + 1` belongs to `C` for every `x` in `C`. Here `1` is the all-ones word.
Suppose every distance between distinct words is in

```text
S = {2,6,8,10,14,16}.
```

Write `N = |C|`. Antipodality partitions `C` into `N/2` distinct pairs.
We prove `N <= 632`.

## The inherited nonnegative square identity

For a mask `u`, define the integer character sum

```text
F(u) = sum_(x in C) (-1)^(u.x).
```

For `k = 0,...,16`, the binary Krawtchouk polynomial is

```text
K_k(d) = sum_j (-1)^j binom(d,j) binom(16-d,k-j).
```

Counting masks by their intersection with the support of `x+y` gives
`sum_(wt(u)=k) (-1)^(u.(x+y)) = K_k(d(x,y))`. Expanding the square therefore
gives, without any averaging or transitivity assumption,

```text
sum_(wt(u)=k) F(u)^2 = sum_(x,y in C) K_k(d(x,y)).
```

Use the three nonnegative weights from PR5206's dual identity, and put

```text
f(d) = 25 K_2(d) + K_6(d) + 2 K_8(d),
W = 25 sum_(wt(u)=2) F(u)^2
       + sum_(wt(u)=6) F(u)^2
     + 2 sum_(wt(u)=8) F(u)^2.
```

The binomial formula yields the complete needed table:

| d | 0 | 2 | 6 | 8 | 10 | 14 | 16 |
|---|---:|---:|---:|---:|---:|---:|---:|
| f(d) | 36748 | -116 | -116 | -116 | -116 | -116 | 36748 |

Each word has exactly one partner at distance zero, itself, and one at
distance sixteen, its antipode. Thus the ordered-pair identity is

```text
W = 2N*36748 - 116*N*(N-2)
  = N*(73728 - 116N).                                      (1)
```

Nonnegativity of `W` gives the inherited real bound `N <= 18432/29`.
Since `N` is even, `N <= 634`. This is the existing cap of 317 spinor lines;
the new step below is the integral square floor at the remaining endpoint.

## The new integral floor at 317 pairs

Suppose `N = 634`. Choose one representative `r` from each of the 317
antipodal pairs. If `wt(u)` is even, the two words of a pair have the same
character value, because `(-1)^(u.1)=1`. Hence

```text
F(u) = 2 sum_(317 representatives r) (-1)^(u.r).
```

The inner sum has an odd number of summands, each equal to `+1` or `-1`.
It is an odd integer. Consequently `F(u) = 2 mod 4`, and `F(u)^2 >= 4`,
for every even-weight mask. All three weights in `W` are positive, so

```text
W >= 4*(25*binom(16,2) + binom(16,6) + 2*binom(16,8))
   = 4*(25*120 + 8008 + 2*12870)
   = 146992.                                               (2)
```

But (1) gives

```text
W = 634*(73728 - 116*634) = 116656.
```

This contradicts (2), by `146992-116656=30336`. Thus `N` cannot be 634;
the inherited bound and evenness give `N <= 632`.

## Geometric corollary and limits

In PR2244's D16+ roots-plus-spinors family, each spinor line is one antipodal
pair of sign words. The specified allowed-distance model is exactly the
one above, and the root contribution is 240 lines. Therefore this family
contains at most `316` spinor lines and at most `556` total lines.
This uses the predecessor's model identification as a cited premise.

At 316 pairs the number of representatives is even; the inner character
sum may vanish. The new square floor therefore does not exclude that case.
Neither attainment nor a sharp code-size theorem is claimed. Other line
systems, other spinor compatibility rules, compensation and every physical
supplier obligation are outside this proof. No new kappa follows.
