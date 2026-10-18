# Affine recoding on the smallest quadratic five-port cube

This is a finite algebraic theorem with a separately stated conditional
accounting consequence. It is not an all-size multiplication theorem or a
physical implementation of the displayed totals.

## Object and exact scope

Take five coordinate pairs and all 32 ports that select one coordinate from
each pair. Identify a port with its orientation `x in F2^5`. If ports `x,y`
have intersection `j=5-|x XOR y|`, use Ross Richardson's PR958 quadratic
Gram matrix

```
G[x,y] = 2(j-1)(j-3).
```

The common labels are rational and may realize this Gram matrix in a larger
space. The coordinate-star decoder matrix is binary:

```
B[x,y] = j mod 2 = 1 + p(x) + p(y),
p(x) = x_0 + x_1 + x_2 + x_3 + x_4  (over F2).
```

The remaining source corrections have `j in {1,3}`. Hence their binary
matrix plus `B` is exactly the identity. This is the inherited five-port
decoder identity, not a new identity attributed to this contribution.

The coordinate-star observation code on this particular cube is

```
C = { f(x)=a_0*x_0+...+a_4*x_4+c : a_i,c in F2 }.
```

It has dimension six: the star for coordinate `2i+1` evaluates to `x_i`
and the other coordinate's star evaluates to `1+x_i`. In contrast, the
decoder matrix `B` has binary rank two, with row and column space

```
U = span_F2 {1,p},   U\{0} = {1,p,1+p}.
```

This distinction is essential. Requiring six nonzero delivered terms from
the observation rank would incorrectly exclude a two-total decoder.

Allow **any finite, possibly redundant** binary rank-one factorization

```
B[x,y] = sum_(i=1..n) f_i(x)*g_i(y)  (over F2),
0 != f_i,g_i in C.
```

Zero factors can be discarded. Invertible, nonsymmetric basis recodings
and overcomplete decompositions are included. The equality is required on
every one of the 1,024 source/target entries. It is not only a masked
identity on the correction graph. Let `R_i=support(f_i)` and
`S_i=support(g_i)`. Define the **algebraic pairing-rank objective**

```
c_i = rank_Q G[R_i,S_i],  C_total = sum_i c_i.
```

Under the inherited per-total copy-tree rule this objective is a lower
bound on additive paid copying. A decomposition attaining the objective
does not itself realize that paid cost: source access, gathers, endpoints,
frames and restoration still need a construction.

**Theorem.** Every such factorization has `C_total >= 32`. This is sharp.
The minimum possible largest term rank is eight, also sharp. Both optima
are attained simultaneously by the four-total factorization below.

## Complete finite rank certificate

Encode an affine form by a six-bit integer: bits 0 through 4 are its linear
coefficients and bit 5 is its constant. The nonzero forms are exactly
`1,...,63`. Both checkers explicitly enumerate all **3,969 ordered pairs**.
`verify.py` uses elimination over the checked prime 65,521; a nonzero
modular minor gives a rational rank lower bound. `independent.py` computes
the same ranks by integer elimination with gcd normalization, without
importing the modular checker. It confirms equality over Q everywhere.

The complete rank table is retained in `CERTIFICATE.json`.

| Rank | Ordered pairs | Maximum `|R intersect S|` |
|---:|---:|---:|
| 6 | 30 | 0 |
| 8 | 480 | 8 |
| 10 | 1,230 | 8 |
| 11 | 1,530 | 16 |
| 13 | 690 | 16 |
| 16 | 9 | 32 |

Every nonzero term has rank at least six. Every rank-six pair has disjoint
supports. The nine pairs with both forms in `U\{0}={31,32,63}` have rank
16. A pair with one form in this set and the other an arbitrary nonzero
affine form has rank at least 11. The whole quadratic Gram has rational
rank 16.

These are exhaustive finite facts about the specified 32-port object,
not an extrapolation to larger five-port families. The modular lower
bounds alone suffice for the lower-bound argument; exact rational ranks
are additionally needed for the sharp witnesses and reported census.

## Lower bound, including arbitrary redundant factorizations

Suppose `C_total < 32`. The six-per-term lower bound forces `n <= 5`.
Let `A` and `D` have the evaluated reader and source forms as their
columns, so `B=A*D^T` over F2. Write `r_A=rank A`, `r_D=rank D`.
Both ranks are at least two and Sylvester's rank inequality gives

```
r_A+r_D <= n+rank(B) = n+2.
```

For one term, binary rank alone is impossible. For two terms, both factor
spaces equal `U`; each term costs 16 and their sum is 32. For three terms,
one factor space has dimension two and equals `U`. Every term has one
nonzero form in `U`, so each costs at least 11 and the sum is at least 33.
This reasoning does not require distinct factors or a minimal observation
basis.

For four and five terms use the diagonal. Because `B[x,x]=1` for every
port, each port must occur in an odd, hence positive, number of the sets
`R_i intersect S_i`. Therefore

```
sum_i |R_i intersect S_i| >= 32.
```

The census table implies that at total cost at most 31, four terms can
cover at most 24 diagonal entries, counting repeated coverage, and five
terms can cover none. One way to check the first assertion is the exact
budget recurrence in `verify.py`: start with `{cost 0: coverage 0}` and
add one independently chosen table type per term, retaining the largest
coverage at each integer cost up to 31. This relaxation permits every
type combination and ignores correlations between actual forms. Its
maxima are 24 and zero. `independent.py` separately enumerates all six
rank-type sequences of length four and five and obtains the same maxima.
Both contradict the necessary diagonal coverage of 32.

Six or more terms already cost at least 36. These cases exhaust every
finite affine-code factorization and prove `C_total >= 32`.

For the peak claim, a factorization whose term ranks were all below eight
could use only rank-six terms. Their supports are disjoint, so their
combined diagonal is zero. Thus at least one term has rank at least eight.

## Sharp algebraic witnesses

The two parity totals give

```
B[x,y] = p(x)*p(y) + (1+p(x))*(1+p(y)).
```

The two restricted Grams both have rank 16. This attains total 32 but
has peak 16.

Put `h(x)=x_0`, `q(x)=x_1+x_2+x_3+x_4`, so `p=h+q`. Then

```
B[x,y] = h(x)*q(y)
       + q(x)*(1+h(y))
       + (1+h(x))*(1+q(y))
       + (1+q(x))*h(y).
```

The reader/source form pairs are `(1,30),(30,33),(33,62),(62,1)`.
Each restricted Gram has rational rank eight. The sum is 32 and the
peak is eight. Both checkers verify every source/target coefficient,
including off-diagonal entries, and compute all four ranks exactly.
This changes the total basis and pairing geometry, while leaving the
copy-rank sum unchanged from the two-total optimum.

As optional corroboration, `independent.py --exhaustive-factorizations`
enumerates the reduced subspace cases that could possibly violate the
floor: for `n<=5`, one factor span has dimension at most three and contains
`U`; there are exactly one dimension-two and 15 dimension-three choices.
Repeated reader forms can be merged without increasing cost, since XOR
support is contained in the union and restricted Gram rank is subadditive
under concatenation. After merging, enumerate distinct readers and every
binary source assignment solving the full matrix identity. This secondary
experiment is not needed by the simpler diagonal proof, and does not
claim to enumerate factorizations with six or more terms.

## Conditional complete-budget obstruction

Assume the inherited per-replica stage accounting with `v=32`, stage count
`s>=3`, additive per-total copy charges at least the pairing ranks, and

```
D <= (s-1)*v - s*C_total.
```

Then even the favorable complete budget that grants source access,
gathers, decoder arithmetic, helpers, frame changes, restoration, idle
work, precision and all other nonnegative expenses zero satisfies

```
D <= (s-1)*32-s*32 = -32.
```

The inherited pressure equation for a positive saving has nonnegative
child terms `z_r*r*((m/r)^gamma-1)` for `0<r<m`, and nonnegative fallback
only makes admission harder. It cannot equal a negative deficit. Thus
affine recoding does not rescue this **smallest cube** in the stated
stage/copy model. No larger-p theorem is claimed.

Changed Gram pairings, non-affine source or reader supports, nonlinear or
interactive messages, masked decoder identities, information retained
across stages and a different copying ledger remain outside scope. A
physical implementation of either witness remains unprovided. The selected
construction's all-size/compiler, common-label/mutable-source, whole-call
hosting, precision/tape, bit H1-H5 and analytic obligations are unchanged.
