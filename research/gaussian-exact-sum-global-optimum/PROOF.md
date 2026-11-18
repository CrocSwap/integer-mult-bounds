# The global exact-sum Gaussian radial optimum

Let G=Z[i]. For x,y in G, write s=x+y and d=x-y. Set
`C_+(x,y)=((s+i*d)/2,(s-i*d)/2)` and use the Euclidean pair norm.
An admissible map F:G^2 -> G^2 is injective, preserves s exactly and has
`||F(z)-C_+(z)||<=1` for every input. Its forward outward slack is
`sup_z max(0,||F(z)||-||z||)`.

**Theorem.** The minimum forward outward slack is `1/sqrt(2)`.
An explicit bijection attains this supremum. Its inverse approximates
C_- with error at most one. Its inverse outward and absolute radial
suprema are also `1/sqrt(2)`. Every individual radial change is strictly
smaller than this value. No phase, period, square identity or surjectivity
premise is needed for the lower bound.

The earlier finite lower bounds are `sqrt(5)-sqrt(3)` in
[Nick Petalas's PR #7652](https://github.com/CrocSwap/integer-mult-bounds/pull/7652)
and `sqrt(13)-3` in
[Ali Romman's PR #7673](https://github.com/CrocSwap/integer-mult-bounds/pull/7673).
They are the first two positive members of the square family below.
The new result is the full family, its limiting lower bound and global
attainment. The finite witnesses retain their prior credit.

## 1. The exact half-grid graph

Identify complex numbers with real two-vectors. Define

```text
J(a,b)=(-b,a), B(a,b)=(a+b,a-b), T=B/2.
B=T^-1, ||T v||^2=||v||^2/2.
```

The output difference f(d) must have the component parities of s.
The pair norm squared is `|s|^2/2+|d|^2/2`. The error squared is
`|f(d)-Jd|^2/2`. If the component parities of s agree, the ideal output
is integral. Exact sum makes the two Gaussian errors e and -e, so the
error condition forces e=0.

If the parities differ, both components of `f(d)-Jd` are odd integers.
Their squared sum is at most two only when both are ±1. Put
`t=T Jd` and `u=T f(d)`. Both lie in `L=(Z+1/2)^2`, and u is one of the
four unit neighbors of t. These points have opposite colors, where the
color of a point is its integer coordinate sum modulo two. The norm
squared is `c+|t|^2` at the input and `c+|u|^2` at the output, with
`c=|s|^2/2>=1/2`.

For the sum-one fiber, input points t have even color and output points
u have odd color. The changes of coordinates are bijections on these
cosets. Thus every admissible injection gives an injection from the even
color to the odd color, using only unit edges. This reduction uses no
surjectivity or order identity. The half-grid formulation is credited to
[CubeJerry's pinned proof](https://github.com/CubeJerry/integer-mult-bounds/blob/053c42c68165cf24fd4e8bc33c2b20d6ac3d399b/research/sharp-order-four-gaussian-rounding/proof/PROOF.md).

## 2. A growing family of Hall obstructions

Let `r=k+1/2`, for an integer k>=1. Take all even-color points S_r in
the square `D_r={t in L:max(|t_1|,|t_2|)<=r}`. Each color has
`2(k+1)^2` points. Exactly two corners have odd color. Each such corner
can be reached from inside D_r only by an edge from `(r-1,r)`, up to
coordinate signs and exchange. Its forward radial cost at sum one is

```text
a(r) = sqrt(2r^2+1/2) - sqrt(2r^2-2r+3/2).
```

Every edge from D_r to its exterior changes a boundary coordinate r to
r+1 in absolute value. Its radial cost is smallest when the other
coordinate also has absolute value r. Thus its cost is at least

```text
b(r) = sqrt(2r^2+2r+3/2) - sqrt(2r^2+1/2) > 1/sqrt(2).
```

For the last strict inequality, set `A=2r^2+1/2`. The squared-radius
increment is `2r+1`. Comparing its square-root gap with `1/sqrt(2)`
by positive squaring reduces to
`(2r+1/2)^2>2A`, or `2r>3/4`. This holds for r>=1/2.

Also `a(r)<1/sqrt(2)`: it is a tangential edge of a square ring, covered
by the upper bound in Section 4. If the forward slack were less than
a(r), no output of S_r could be outside D_r or at either odd corner.
At most `2(k+1)^2-2` outputs would remain for `2(k+1)^2` inputs.
This violates injectivity. Therefore every admissible injection has
forward slack at least a(r), for every k>=1.

Rationalization gives

```text
a(r) = (2r-1) /
       (sqrt(2r^2+1/2)+sqrt(2r^2-2r+3/2)).
```

Its limit as r tends to infinity is `1/sqrt(2)`. The lower bound follows.
No passage from finite successful matchings to a global map is used.
The cases r=3/2 and r=5/2 give the credited eight-to-six and
eighteen-to-sixteen witnesses. Larger squares prove strictly stronger
necessary bounds; the limit is a global obstruction, not a search result.

## 3. An explicit bijection on every sum fiber

Each point of L lies on exactly one square ring of radius `r=k+1/2`.
Traverse that ring from `(r,r)` along the top, left, bottom and right
sides. Each side contains its first corner and excludes its final corner.
The cycle has `8k+4` vertices. Pair entries 0 with 1, 2 with 3, and so on.
The even cycle length makes this a perfect matching. Each edge has unit
length and stays on the ring. Write M for the resulting involution on L.
It exchanges the two colors. It also satisfies `M(-t)=-M(t)`: the
half-turn shifts the cycle index by `4k+2`, an even integer.

This construction uses individual rings. The paired-ring construction in
[PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570)
serves its stronger square-to-swap contract. Its connector edges and
quarter-turn symmetry are not imposed here.

For equal-parity sums use the exact ideal difference `f_+(d)=Jd`.
For mixed sums set

```text
f_+(d) = B M(T Jd),
F_+(x,y) = ((s+f_+(d))/2,(s-f_+(d))/2).
```

To check parity, write d's component parities as `(p,1-p)`.
The coordinate sum of `T Jd` has parity `1-p`. M changes it to p.
For a half-grid point of color p, B produces components of parities
`(p,1-p)`. The output halves are therefore Gaussian integers. The map
preserves s. Its error is exactly one in every mixed fiber, since M
moves a point by one and B multiplies squared norm by two.

The inverse difference map is explicit:

```text
f_-(d) = -J B M(T d)                 [mixed sums],
f_-(d) = -Jd                        [equal-parity sums].
```

Using `T B=I`, `(-J)J=I` and `M^2=I` proves both inverse identities.
The same color check proves that f_- stays in the required coset.
It has error one from -Jd in a mixed fiber. These formulas give a total
bijection on every fiber and hence on G^2. They do not choose unrelated
finite matchings or require a limiting existence theorem.

## 4. Uniform radial bound and exact suprema

An edge in a ring has one fixed coordinate of absolute value r.
A sign change between -1/2 and 1/2 has zero radial change. Every other
edge has absolute changing coordinates u and u+1, with `u>=1/2` and
`r>=u+1`. Its lower squared radius is `A=c+r^2+u^2`; the increment
is `2u+1`. Positive squaring shows that its radial gap is less than
`1/sqrt(2)` exactly when

```text
(2u+1/2)^2 < 2A.
```

Since `c>=1/2` and `r>=u+1`, the right side is at least
`4u^2+4u+3`, while the left side is `4u^2+2u+1/4`.
The inequality is strict. This proves the absolute radial bound on every
mixed sum fiber; equal-parity fibers have zero change. The inverse uses
the same undirected edges, so the same bound applies.

For every integer k>=1 the formulas give

```text
F_+(-k*i,1+k*i) = (k+1,-k),
F_-(1-k*i,k*i)  = (-k,k+1).
```

In the first case the matching edge is `(r-1,r)` to `(r,r)`;
in the second it is `(-r+1,r)` to `(-r,r)`, with `r=k+1/2`.
Both inputs have squared norm `2k^2+1`, and both outputs have squared
norm `2k^2+2k+1`. Their outward gaps are a(r), which tend to
`1/sqrt(2)`. Thus the forward, inverse outward and absolute suprema
of this explicit map all equal the lower bound. None is a maximum at
a finite input. The inverse conclusion uses these actual pairs, without
assuming that an arbitrary injective positive provider has an inverse.

## 5. Contract, verification and limitations

The map commutes with wire swap because M is odd. It commutes with common
Gaussian translation because d and the sum parities do not change. It
is exact on all integral ideal images and fixes equal-input pairs.
Global phase covariance and the square-to-swap identity fail; explicit
four-coordinate counterexamples are in RESULT.json. They are not promised
interfaces. The inverse is the stated formula, not an assumed square or
conjugation rule. No tensor commutation or native-graph identity is claimed.

The checker constructs 129 complete rings by a separate directed walk,
compares their 66564 points with the direct index formula, and checks
matching, colors, oddness and exact radical inequalities. It checks both
providers, direct four-real-coordinate errors, inverse identities and
radial bounds for all 14641 pairs in [-5,5]^4 and 80 additional signed
inputs through 4097 bits. Thirty-two complete Hall squares check the
corner and exterior edges. Three separate rational-threshold neighborhood
censuses and one larger symbolic count corroborate the deficits. Invalid
domains, zero slack and the excluded algebraic identities are controls.
All arithmetic is integral. These checks support the written all-input
proof; they do not replace it.

No finite-width physical schedule, scratch restoration, tape cost, native
tariff, caller error recurrence or analytic recovery is supplied. The
selected kappa and all five selected assumptions remain unchanged. The
construction can serve only a caller that accepts its stated inverse and
missing symmetries. Full predecessor replays, the selected cold replay,
Lean and Docker were not run. Independent human and formal-kernel review
are unclaimed.

Prepared by Ali Romman with substantial OpenAI Codex assistance.
[CREDITS.md](CREDITS.md) gives the exact source roles. The proof and code
are new; prior half-grid geometry and finite witnesses retain their credit.
Apache-2.0.
