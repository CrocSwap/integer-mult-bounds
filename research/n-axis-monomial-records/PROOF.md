# Record count of one n-axis monomial elimination

This is a proof about one synthesis. It is not a lower bound on every
recipe in the selected primitive alphabet, and it does not change κ.

## Normal form

Use the nine-axis shape from `research/final4610-independent-admission/SPECIALIZATION.md`,
with the axis count left free. An n-axis monomial is an invertible matrix
`A` over `F_2`, a translation `b` in `F_2^n`, a global phase `a` modulo 4,
linear coefficients `alpha_i` modulo 4, and off-diagonal bits `Q_ij` for
`i < j`. The diagonal of `Q` is carried by `alpha_i mod 2` and is not a
separate controlled-sign record. On a basis address the monomial applies
the quadratic phase and then the affine map `x -> A x + b`.

The selected-bit primitives used here are one row addition, one translation
of a single bit, one unit phase on a single bit, one controlled sign on a
pair of bits, and one global factor of `i`. A row swap is three row
additions: over `F_2`,

```text
u <- u+v,    v <- v+u,    u <- u+v
```

sends `(u, v)` to `(v, u)`. Two additions do not.

## Elimination

Start from `M = A`. For `k = 0, ..., n-1`:

1. Let `r` be the least index at least `k` with `M_{r k} = 1`.
2. If `r != k`, swap rows `r` and `k`.
3. For every `i != k` with `M_{i k} = 1`, add row `k` into row `i`.

**Block form.** At the start of column `k` the matrix is

```text
[ I_k    B ]
[ 0      C ]
```

with `C` of size `n-k`. Swaps are among rows `k, ..., n-1`, and those rows
have zeros in columns `0, ..., k-1`, so a swap does not change the finished
columns. Row `k`, once it holds the pivot, also has zeros in columns
`0, ..., k-1`, because that row was taken from the bottom block. Adding it
to other rows therefore does not change finished columns. Clearing column
`k` makes that column equal to `e_k`. By induction the algorithm ends at
`I_n` whenever every pivot exists.

**Pivot existence.** The elementary steps are invertible, so `A` is
invertible if and only if the current matrix is. In the block form that is
equivalent to `C` being invertible. The first column of an invertible `C`
is nonzero, so a pivot row `r >= k` exists. At `k = n-1` the only eligible
row is `n-1`, so the last column never swaps. Thus the number of swaps is
at most `n-1`.

**Column charge.** Fix column `k`. Let `s_k` be 1 if a swap occurs and 0
otherwise, and let `a_k` be the number of additions. There are `n-1` rows
other than the pivot.

- If `s_k = 0`, at most those `n-1` rows are cleared, so `a_k <= n-1`.
- If `s_k = 1`, then `M_{k k} = 0` before the swap. After the swap that
  zero lies in the row that was exchanged. That row is not cleared, so
  `a_k <= n-2`.

In both cases `a_k + s_k <= n-1`. Summing over columns,

```text
sum a_k + sum s_k <= n(n-1),    sum s_k <= n-1.
```

The address recipe replaces each swap by three additions, so its length is

```text
sum a_k + 3 sum s_k
  = sum (a_k + s_k) + 2 sum s_k
  <= n(n-1) + 2(n-1)
  = (n+2)(n-1).
```

The separate ceilings `sum a_k <= n(n-1)` and `sum s_k <= n-1` are true,
but adding them charges `3(n-1)` for the swaps on top of `n(n-1)`
additions and produces the longer count `(n+3)(n-1)`. The column charge
removes `n-1` from that count. For `n > 1` the two separate ceilings are
not achieved by one matrix: a swapped column has at least one uncleared
row. The exhaustive check for `n <= 4` records that fact. The inequality
above does not need it.

## Phase and translation

These records do not depend on `A`.

- `b` has at most `n` ones, one translation each.
- Each `alpha_i` lies in `{0,1,2,3}`, so at most `3n` unit phase records.
- At most one controlled sign for each of the `n(n-1)/2` pairs.
- The global phase `a` needs at most three factors of `i`.

Adding these ceilings to the address bound gives

```text
R(n) = (n+2)(n-1) + 4n + 3 + n(n-1)/2 = (3n^2 + 9n + 2)/2.
```

The numerator is even because `n(n+3)` is even, so `3n(n+3) + 2` is even.
The same count is an integer recipe length for every positive integer `n`.

## The bound is achieved by this synthesis

For `n = 1` the matrix `(1)`, the translation `1`, `alpha_0 = 3` and global
phase `3` emit `0 + 1 + 3 + 0 + 3 = 7 = R(1)` records.

For `n >= 2` define `A` by

```text
row 0 = e_{n-1},    row i = e_0 + e_i for i = 1, ..., n-1.
```

At the start of column `k`, for `0 <= k <= n-1`,

- row `i` equals `e_i + e_k` for every `i < k`,
- row `k` equals `e_{n-1}`,
- row `i` equals `e_k + e_i` for every `i > k`.

This holds at `k = 0`. If `k < n-1`, row `k` has a zero in column `k` and
row `k+1` has a one there, so the pivot is row `k+1`. After that swap,
clearing column `k` adds the pivot row to the `k` rows above it and to the
`n-k-2` rows below `k+1`, which is `n-2` additions, and produces the same
description at column `k+1`. At column `n-1` there is no swap, and each of
the `n-1` earlier rows has a one in the last column.

Thus the algorithm swaps on exactly the first `n-1` columns, performs
`(n-1)(n-2)` additions there and `n-1` additions on the last column, and
the address length is

```text
(n-1)^2 + 3(n-1) = (n+2)(n-1).
```

Choose every bit of `b` equal to 1, every `alpha_i` equal to 3, every
`Q_ij` equal to 1, and global phase 3. Then `alpha_i` is odd, so the
stored diagonal bit is 1, and no extra controlled sign is emitted for it.
This one monomial makes the synthesis emit exactly `R(n)` records.

Reaching `I_n` also shows that this `A` is invertible. The census for
`n <= 4` finds exactly one maximizer in each `GL(n, F_2)`, and it is this
matrix.

## Comparison with the published sufficient counts

The `#4610` specialization charges at most `n(n-1)` additions and at most
`n-1` swaps separately. That address length is `(n+3)(n-1)`, and the full
record ceiling is

```text
L(n) = (3n^2 + 11n)/2 = R(n) + (n-1).
```

At `n = 9` this is `96 + 9 + 27 + 36 + 3 = 171`, matching the published
line. The sharper count is `R(9) = 163`. Both are sufficient. The value
171 is not false; it does not use the column charge.

The operation list in section 6 of the `#7000` application review is
`n(n-1)+3n` row additions, `n` affine flips, `3n` unit phases,
`n(n-1)/2` controlled signs and three global phases. Its sum is

```text
S(n) = L(n) + 3 = R(n) + n + 2,
```

because `n(n-1)+3n` charges `n` swaps rather than `n-1`. At `n = 9` the
sum is 174. The review then uses the still larger per-map ceiling
`4(n+1)^2`. The gap is an integer:

```text
4(n+1)^2 - R(n) = (5n^2 + 7n + 6)/2.
```

It is positive for every positive integer `n`. At `n = 153`,

```text
R(153) = 35803,    4(154)^2 = 94864.
```

The review multiplies the square ceiling by its stated map count
`311304` and obtains `29531542656`, which is below `2^35` and therefore
below the stated `2^40`. The same map count times `R(153)` is
`11145617112`, which is below `2^34`. These are comparisons of the
integers already fixed by the formulas. They do not rederive the map
count 311304, and they do not change the admitted κ
`363005817/100000000000`.

## What is not claimed

The algorithm accepts exactly the invertible matrices: every successful run
ends at `I_n` by invertible steps, and every invertible matrix has a pivot
at each column. The exhaustive check for `n <= 4` matches `|GL(n, F_2)|`.
That census is not the proof for larger `n`.

`R(n)` is the exact length of this synthesis on one monomial. Another
factorization into the same primitives might be shorter. No such search is
claimed to be exhaustive. Assumption `precision_tape` is not discharged:
the proof bounds the record list that the retained tape tariff multiplies.
It does not prove the movement exponent, the storage prescription, or the
outer threshold calculation.
