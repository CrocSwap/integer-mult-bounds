# Independent constructive review

Status: **PASS for the construction and the matching-class sharp bound**.
This is an AI mathematical review with an independently written integer model,
not a proof-assistant certificate. The reduction from completely arbitrary
rounding maps to this matching class is outside this review. No other worker's
or parent checker's implementation was read or imported.

Write a Gaussian integer as a vector in `Z^2`. Let

\[
J(x,y)=(-y,x),\qquad
H=\begin{pmatrix}1&1\\1&-1\end{pmatrix},\qquad
C(u,v)=\left({s+Jd\over2},{s-Jd\over2}\right),
\quad s=u+v,\ d=u-v.
\]

The norm throughout is the Euclidean norm on the ordered Gaussian pair,
`sqrt(|u|^2+|v|^2)`. Thus the error bound 1 is a **pair** bound. Each output
coordinate separately has error at most `1/sqrt(2)`.

## 1. The matching covers the entire half-grid

Partition the square rings of `(Z+1/2)^2` into consecutive pairs with inner
radius `a=2m+1/2` and outer radius `a+1`, for `m>=0`. Join

\[
(a,a)\longleftrightarrow(a+1,a)
\]

and its three quarter-turn images. These four disjoint edges use all four
inner corners and four outer near-corner points. On the inner ring the
remaining canonical top arc is

\[
(a-1,a),(a-2,a),\ldots,(-a+1,a),
\]

with `4m` vertices. On the outer ring the canonical top arc is

\[
(a+1,a+1),(a,a+1),\ldots,(-a+1,a+1),
\]

with `4m+2` vertices. Pair the first with the second, the third with the
fourth, and so forth on each arc, and rotate these arcs by all four powers
of J. These arcs are disjoint and cover exactly the unused ring vertices.
The empty inner arcs at `m=0` cause no exception. The outer arc still has
two vertices. Consequently this rule is defined on every half-grid point.

Every edge has length 1. Every vertex has exactly one mate, so `M^2=id`.
The connector rule is invariant under J, and the four arc rules are rotated
copies of a single rule. Hence `M J = J M`. In particular `M(-t)=-M(t)`.
Every unit horizontal or vertical move flips the checkerboard color.

The executable represents `t` by its odd integer pair `2t`. If its maximum
absolute coordinate is `r`, the inner scaled radius is `r` for `r=1 mod 4`
and `r-2` for `r=3 mod 4`. The canonical arc is found with at most four
quarter-turns, and its mate index is `index xor 1`. There is no enumeration
depending on the radius in the implementation of M. This observation is
only about this integer model; no physical-machine cost is asserted.

## 2. Gaussian closure, exact sum and error

If the two coordinates of s have equal parity, define `d'=Jd`. The parity
relation `d=s mod 2` implies `d'=s mod 2`. In this case define F=C exactly.

Otherwise put `t=HJd/2`. Both coordinates of t are half-integral. Define

\[
d'=HM(t),\qquad
F(u,v)=\left({s+d'\over2},{s-d'\over2}\right).
\]

Since `H^2=2I`, `Ht=Jd`. This has its two component parities opposite to
those of s. The difference `M(t)-t` is one signed coordinate unit vector,
so `H(M(t)-t)` has both coordinates odd. It follows that `d'=s mod 2`,
and both outputs are Gaussian integers. Their sum is s exactly.

In the mixed case the difference from the ideal C output is

\[
F-C={1\over2}\bigl(H(M(t)-t),-H(M(t)-t)\bigr).
\]

The vector `H(M(t)-t)` has squared norm 2. Thus each Gaussian output error
has squared norm `1/2`, and the complete pair error has squared norm 1.
In the equal-parity case both errors are zero.

## 3. The square identity and the inverse

The identities `HJH/2=-J` and `HJ=-JH` give the transformed half-grid
coordinate on the next application as

\[
t_{\rm next}={HJd'\over2}=-JM(t).
\]

Because M is an involution commuting with J,

\[
M(t_{\rm next})=-Jt,\qquad
d''=-HJt=JHt=-d.
\]

The unchanged sum therefore gives `F^2(u,v)=(v,u)`. The equal-parity branch
has the same identity because `J^2=-I`. The branch is unchanged by applying
F, since its sum stays s. It follows that `F^4=id`, F is a bijection, and

\[
F^{-1}=\operatorname{swap}\circ F=F\circ\operatorname{swap}.
\]

The last commutation also follows from `M(-t)=-M(t)`. The implementation
checks both left and right inverse identities. It also checks commutation
with simultaneous multiplication of both Gaussian inputs by i.

The ideal C has `C^2=swap` as well, hence `C^{-1}=swap C`. Therefore the
inverse error against the ideal inverse is the norm-preserving swap of
`F-C`: it too is at most 1, with the same exact 0-or-1 squared pair error.

## 4. Exact radial upper bound

In the mixed case, with `c=|s|^2/2`, orthogonality gives

\[
\|(u,v)\|^2=c+|t|^2,\qquad
\|F(u,v)\|^2=c+|M(t)|^2.
\]

The mixed sum is nonzero, so `c>=1/2`. For a tangential edge on a square
ring with radius b, the changing coordinate x stays in `[-b,b]`. The
derivative of `sqrt(b^2+x^2+c)` has absolute value strictly less than
`1/sqrt(2)`. Integrating over an interval of length 1 proves that each
tangential edge has radial jump strictly below `1/sqrt(2)`.

For a connector at inner radius a the positive radial jump is

\[
\delta(a,c)=\sqrt{2a^2+2a+1+c}-\sqrt{2a^2+c}.
\]

This decreases as c increases. At the smallest possible `c=1/2`, write
`delta(a)=delta(a,1/2)`. Its derivative has the sign of

\[
(2a+1)^2(2a^2+1/2)-4a^2(2a^2+2a+3/2)
=-2a^2+2a+1/2.
\]

Thus it decreases for `a>(1+sqrt(2))/2`, in particular for every `a>=5/2`.
The only earlier allowed value is `a=1/2`. The comparison

\[
\delta(5/2)>\delta(1/2)
\iff \sqrt{19}+1>\sqrt{13}+\sqrt3
\]

follows by squaring the positive sides twice, reducing to `sqrt(19)>4`.
The maximum over the allowed sequence `1/2,5/2,9/2,...` is therefore

\[
\beta=\delta(5/2)=\sqrt{19}-\sqrt{13}.
\]

Furthermore `beta>1/sqrt(2)`: squaring reduces this to
`sqrt(247)<63/4`, and `16*247=3952<3969=63^2`. Consequently **all** edges
give `|norm(F(u,v))-norm(u,v)|<=beta`. The inverse has the same bilateral
bound because swap preserves the norm and `F^{-1}=swap F`.

## 5. Attainment and the matching-class lower bound

For `u=-2i`, `v=3i`, the sum is i and `t=(5/2,5/2)`. Its mate is
`(7/2,5/2)`, so

\[
F(-2i,3i)=(3+i,-3).
\]

The squared norms are 13 and 19. Thus the forward upper slack is at least
beta for this construction. Applying F once more gives `(3i,-2i)`, which
also attains the negative radial change. Both signs occur for the inverse
as well. This is an exact equality witness, not a floating-point estimate.

There is also a short lower bound for **any** quarter-turn-equivariant
unit-neighbor perfect matching on the complete half-grid. The square
`maxabs<=5/2` contains 36 vertices. An undirected unit edge has a four-edge
orbit under quarter-turn. A one-edge orbit would require a nonzero point
fixed by J or J^2. A two-edge orbit would require an antipodal unit edge;
its length is at least `sqrt(2)` on this half-grid. Both are impossible.
Since matching edges are equal or disjoint, an internal orbit uses eight
vertices. The number 36 is not divisible by eight, so some matching edge
must leave the square.

Every such unit edge changes one coordinate from absolute value `5/2`
to `7/2`; the other has absolute value at most `5/2`. At `c=1/2` its radial
jump is minimized when the other coordinate has absolute value `5/2`.
That minimum is exactly beta. Each endpoint can be represented by a
Gaussian input pair for one of `s=1` or `s=i`: `d=-JHt` is integral with
one odd and one even component, so choose the unit sum with its parity.
Thus the common-matching class has worst-case slack at least beta.

This paragraph does not reduce a completely arbitrary F to one global
quarter-turn-equivariant matching. Such a reduction can involve the
dependence on s and the relation between the two checkerboard colors.
That separate theorem is explicitly not certified by this review.

## 6. Inverse by conjugation is incompatible

The constructed output at `(1,0)` is `(i,1-i)`. Its inverse output is
`(1-i,i)`, while conjugating F's output gives `(-i,1+i)`.

More generally suppose exact sum, `F^2=swap`, and `KFK=F^{-1}` all hold,
where K conjugates each Gaussian coordinate. Since `F^{-1}=swap F`, at the
real input `(1,0)` the output `(a,b)` would satisfy
`(conj(a),conj(b))=(b,a)`. Exact sum then requires `2 Re(a)=1`, impossible
for a Gaussian integer. The proposed square identity requires this change
from an inverse-by-conjugation contract.

## 7. Executable evidence and boundaries

`check.py` exhausts all half-grid points with scaled odd coordinates from
`-257` to `257`, separately checks all 129 ring-pair arc partitions through
`m=128`, and exhausts Gaussian inputs whose four components lie in `[-7,7]`.
It also checks deterministic signed inputs with 64,127,256,1024,4096-bit
components and huge corners/connectors/arc endpoints. Radial comparisons
use integer `isqrt` intervals at 128 fractional bits, never subtraction of
floating-point square roots. Equality `(13,19)` is checked exactly. All
checks use explicit exceptions and remain active under `python -O`.

Seven negative controls cover a diagonal connector, an incorrect arc mate,
a unit-neighbor involutive patch breaking quarter symmetry, its resulting
failure of F^2, an omitted parity move, a wrong attaining direction, and
the rejected inverse-by-conjugation identity. The asymmetric-square control
uses `(0,i)` so it actually reaches the changed quadrant; `(1,0)` would not
exercise that mutation. This choice was corrected during test development
before freezing.

The finite tests support the formulas; the all-size conclusion rests on
Sections 1–6. This package supplies no reversible tape schedule, selected
source recipe, complete arithmetic cost, caller admission, recursive-rate
claim, kappa change, arbitrary-map reduction, or literature-priority claim.
