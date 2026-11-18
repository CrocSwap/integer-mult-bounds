# The sharp Gaussian radial budget at exact period

Let `s=x+y` and `d=x-y` for Gaussian integers `x,y`. The ideal
positive half-transform sends the pair to `((s+i*d)/2,(s-i*d)/2)`.
A rounder must map Gaussian pairs to Gaussian pairs, preserve `s`
and have Euclidean pair error at most one. Its forward outward slack
is the supremum of `max(0, ||F(z)||-||z||)` over Gaussian pairs `z`.

**Theorem.** A rounder of finite global least period `m` exists exactly
when `4` divides `m`. For each such `m`, let `R` be the least odd
integer at least five that does not divide `m`. The minimum forward
outward slack at exact least period `m` is

```text
beta_R = sqrt((R^2+2R+3)/2) - sqrt((R^2+1)/2).
```

The same construction has absolute radial change and inverse outward
slack at most `beta_R`.

## Starting map and lower bound

Ali Romman's PR #7714 supplies two premises for rounders satisfying
the prescribed iterate identity `F^m=id`. It rules out such a map
unless `4` divides `m`, and in the divisible case proves the lower
bound `beta_R` and constructs a total rounder `F_0` attaining it
with absolute radial change at most `beta_R`. Since a map of least
period `m` satisfies the iterate identity, the necessity and lower
bound carry over. We use the stated results of #7714 directly.
[Finite iterate proof](https://github.com/aliromman/integer-mult-bounds/blob/ba5e006ed70119b23d6ef9e2e8627e43a3f4f18b/research/gaussian-finite-iterate-optimum/PROOF.md)

Only the sum-one fiber will change. Use the doubled half-grid
coordinates `(X,Y)` of #7714, with source color

```text
A = {(X,Y) : X and Y odd, X+Y = 0 mod 4}.
Q(X,Y) = (Y,-X).
```

For difference `d=d_r+i*d_i`, the coordinate vector is
`(d_r-d_i,-d_r-d_i)`. This is a bijective coordinate change on
the sum-one fiber. The pair squared norm at `(X,Y)` equals
`1/2+(X^2+Y^2)/4`. An edge in these coordinates has error one
exactly when undoing `Q` on its output makes that output an
axial neighbor of the input at distance two. For example, the
inverse coordinates give `d_r=(X-Y)/2` and `d_i=-(X+Y)/2`.
The ideal edge sends the doubled coordinates to `Q(X,Y)`.
Changing the output by a vector of length two therefore changes
the difference by length sqrt(2) and the pair by length one.

On the tail rings with doubled radii `(R+4j,R+4j+2)` for
`j >= 0`, the predecessor uses `g_0=Q M`. Here `M` is the
annular matching adapted from Jerry Chen's PR #7570. It commutes
with `Q` and satisfies `M^2=id`, so `g_0^2=Q^2=-id` on these
rings. Every orbit there has length four.
[Annular construction](https://github.com/CubeJerry/integer-mult-bounds/blob/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding/proof/PROOF.md)

## A column of tangential pairs

Write `q=m/4` and set

```text
a = R+4(R(2q+4)+1)
y_k = a+2k, 0 <= k < q
x_0 = a-4, x_1 = a-2.
```

Each ring of radius `y_k` has the top-side pair
`(x_0,y_k) <-> (x_1,y_k)` in the predecessor matching. To see
this directly, on an inner ring of doubled radius `y` the
ordered top-side list runs from `-y+2` to `y-2` by twos. On an
outer ring it runs from `y` to `-y+4` by minus twos. Pair
consecutive entries starting at the first entry. For `y=y_k`,
the horizontal pairs in increasing order start at residues
`a mod 4` in either case. Both selected coordinates are in
the corresponding list, since `y >= a`, and `x_0 = a mod 4`.

Let `p_k` be the point of this pair in `A`, and `u_k` its mate.
The orbit is `(p_k, Q u_k, -p_k, -Q u_k)`. These are `q`
distinct orbits because their points stay on rings of distinct
radii. The points `p_k` and `-p_k` are on opposite sides of
the ring and both belong to `A`.

## Splice the cycles

For each `k=0,...,q-2`, exchange the successors of
`p_k,p_(k+1)` when `k` is even. When `k` is odd, exchange the
successors of `-p_k,-p_(k+1)`. Consecutive switches use opposite
sides of their shared ring. Thus every changed source has its
original successor up to the time that successor is exchanged.

Two odd horizontal coordinates separated by two have opposite
residues modulo four. The source therefore changes horizontal
coordinate from one top-side pair to the next. Before applying
`Q`, the two exchanged successors are consequently vertical
neighbors of the new sources. Negating the pairs preserves this
fact on the bottom side. Every new edge has Gaussian error one.
The edited permutation remains in the sum-one fiber.

Exchanging the successors of two points in distinct cycles
merges those cycles. Starting at the first changed point, the
new orbit follows the second cycle until its changed point,
then follows the first cycle back to the start. In increasing
order of `k`, switch `k` joins the orbit containing rings
`0,...,k` to the untouched cycle on ring `k+1`. This produces
one cycle of length `4q=m` and leaves every other orbit of
`F_0` intact. For `q=1` the selected orbit already has length
four. The full new map has `F^m=id` because every untouched
orbit already has length dividing `m`. The constructed orbit
forces the least period to be exactly `m`.

For example, at `m=8` the first incompatible odd radius is
`R=5`. The splice on rings 169 and 171 gives the cycle

```text
(167,169), (171,-167), (-165,-171), (-171,167),
(165,171), (169,-165), (-167,-169), (-169,165).
```

## Radial cost of a switch

Rotation and negation preserve norm, so each new edge has
the absolute radial change of a vertical neighbor pair with
horizontal magnitude `x >= a-4` and vertical magnitudes
`y,y+2` for `a <= y < a+2q`. Rationalizing gives

```text
(y+1)/(sqrt(1/2+(x^2+(y+2)^2)/4)+sqrt(1/2+(x^2+y^2)/4))
    <= (y+1)/sqrt(x^2+y^2)
    <= (a+2q)/(sqrt(2)(a-4))
    <  (1+1/(4R))/sqrt(2).
```

The second inequality uses the actual inner ordinate
`y <= a+2(q-2)` of a switch. For the last inequality,
`a-4 > 4R(2q+4)`.

The bound on these edges is strictly below `beta_R`. In fact

```text
sqrt(2)*beta_R - 1
  = 2/(sqrt((R+1)^2+2)+R+1) - 1/(sqrt(R^2+1)+R)
  > 2/(2R+3) - 1/(2R)
  >= 1/(4R).
```

Here `sqrt((R+1)^2+2) < R+2` and `R >= 5`. The old edges
have absolute radial change at most `beta_R` by #7714. The
lower bound from the iterate theorem forces equality for the
new map's forward outward slack. The predecessor's attaining
cycle at radii `R,R+2` is outside the splice and supplies
equality for the absolute and inverse outward bounds as well.

This proof uses the exact-sum error-one contract and one mixed
sum fiber. A physical caller, tape and stock price, and any use
in a complete multiplication bound remain open.
