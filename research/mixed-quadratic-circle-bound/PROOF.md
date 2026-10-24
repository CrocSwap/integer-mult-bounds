# Sharp inverse bounds for a mixed quadratic

This scoped proof is produced by Nick Petalas. The cyclic operator setting and
the general degree multiplier are credited to Ali Romman #621 and Rafael
Guevara #803. Geometric series, partial fractions and the triangle inequality
are classical. No literature-priority claim is made for those methods.

Let

    P(z) = c (z-a)(1-bz),   c != 0,   |a|=A<1,   0<|b|=B<1.

Thus P has exactly one root in the open unit disk and one outside its closure.
Put m=min(A,B) and delta=min_{|z|=1}|P(z)|>0. For an absolutely convergent
Laurent series, its Wiener norm is the sum of the absolute values of its
coefficients. Then

    delta ||1/P||_W <= (1+m)^2/(1+m^2) < 2.                 (1)

For every fixed 0<=m<1 the displayed factor is best possible among this
class with min(A,B)=m. Consequently the best factor independent of the roots
is two. In particular, the general degree-two multiplier 81 obtained by
substituting n=2 in #803 can be replaced by two on this subclass. This is a
strengthening of a bound, not a defect in that predecessor.

## Exact Laurent norm

It suffices to take c=1, since delta scales by |c| and the inverse norm by
its reciprocal. On the unit circle the two absolutely convergent geometric
series give

    1/((z-a)(1-bz))
      = 1/(1-ab) [ sum_{j>=0} b^(j+1) z^j
                    + sum_{h>=1} a^(h-1) z^(-h) ].        (2)

One can obtain (2) by multiplying the geometric series for each factor,
or by partial fractions. The positive and negative exponent sets are disjoint.
Since A,B<1, their absolute sums are geometric, so

    ||1/P||_W = (1-AB)/((1-A)(1-B)|1-ab|).                (3)

No cancellation or asymptotic estimate enters (3).

## The sharp upper bound

For 0<=x<=y<1 and every real theta,

    |1-y exp(i theta)| / |1-x exp(i theta)|
       <= (1+y)/(1+x).                                  (4)

To prove this, square the ratio and put t=cos(theta). Its derivative in t
has the sign of (x-y)(1-xy), which is nonpositive. The maximum is at t=-1.
This also proves (4) at x=0 and at x=y without division by a vanishing quantity.

Suppose first A>=B. Here A>0. Evaluate P at z=a/A and apply (4) with
x=AB, y=B and exp(i theta)=ab/(AB). Equations (3) and (4) give

    delta ||1/P||_W
       <= (1-AB)(1+B)/((1-B)(1+AB))
       <= (1-B^2)(1+B)/((1-B)(1+B^2))
        = (1+B)^2/(1+B^2).                               (5)

The second inequality follows because (1-x)/(1+x) decreases for x>=0
and AB>=B^2. If B>A, evaluate instead at z=conjugate(b)/B. The identical
argument with A,B interchanged gives (1). This also covers A=0 directly:
(3) and delta=1-B give product one. Finally
(1+m)^2<2(1+m^2) is equivalent to (1-m)^2>0.

## Attainment and the uniform factor

For any 0<r<1 take a=r and b=-r. For |z|=1,

    |(z-r)(1+rz)|^2
       = (1+r^2)^2 - 4r^2 (Re z)^2
       >= (1-r^2)^2.

Equality holds at z=1 and z=-1, so delta=1-r^2. Equation (3) yields

    delta ||1/P||_W = (1+r)^2/(1+r^2).                   (6)

This proves sharpness for every fixed m=r>0 and tends to two as r tends
to one from below. At m=0, use a=0 and any 0<B<1 to attain one. Thus two
is the least uniform constant, although no member of the class attains two.

## Cyclic operators and sharpness there

Let Z_L be a cyclic permutation matrix of any positive length L, let w be
any integer and let |tau|=1. Put U=tau Z_L^w. Every integer power of U has
induced infinity norm one. Substituting U in the absolutely convergent
series (2) therefore gives an inverse of P(U), with

    ||P(U)^(-1)||_infinity <= ||1/P||_W
       <= (1+m)^2/((1+m^2) delta) < 2/delta.             (7)

Multiplication by the finite polynomial P preserves absolute convergence,
and the Laurent coefficient identity proves both inverse identities. There
is no assumption that w is positive or coprime to L.

The factor in (7) is also sharp uniformly in cyclic length. Fix the Laurent
coefficient sequence (d_k) of 1/P, and take U=Z_L. The inverse has coefficients
q_j=sum_{k congruent j mod L} d_k. Its infinity norm is sum_j |q_j|, since
the first row has one entry at each residue and other rows are permutations.
For K>=0 and L>2K, the coefficients with |k|<=K have distinct residues.
Writing T_K=sum_{|k|>K}|d_k|, the triangle inequality in both directions gives

    ||1/P||_W - 2T_K <= sum_j |q_j| <= ||1/P||_W.

Since T_K tends to zero, these finite cyclic norms tend to the Wiener norm.
Apply this to the rational family in (6), first taking L large at fixed r,
then taking r towards one. No smaller uniform cyclic constant can work.

## Boundaries

The proof uses the exactly quadratic mixed-root factorization. It does not
improve #803's general arbitrary-degree theorem. It supplies no coefficient
preparation, rounded algorithm, source restoration, paid tape schedule,
physical supplier, new kappa or complete multiplication theorem. The finite
checks corroborate formulas and finite cyclic inverses; the universal result
rests on this written proof. Independent human and formal proof-kernel review
are unclaimed.
