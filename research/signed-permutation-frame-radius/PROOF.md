# Exact radius for conjugated signed-permutation frames

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped written mathematical proof with exact finite corroboration.

## Statement

Let d>=1, let P belong to GL_d(Z), and let B_d be the group of all signed
permutation matrices. Set G=P B_d P^{-1} and

    L(P) = max_i sum_j |P_ij|.

For an integer m>=2, consider **every** function
q:(1/m)Z^d -> Z^d satisfying q(gx)=gq(x) for every g in G and every input x.
No linearity, continuity, coordinatewise behavior, translation symmetry or
identity-on-integers condition is imposed in this minimization. Then

    min_q sup_x ||q(x)-x||_infinity = floor(m/2) L(P) / m.       (1)

The minimum is attained by one rule, independent of m, which also fixes every
integer input. On all of R^d, with integer outputs, the exact minimum is

    min_q sup_x ||q(x)-x||_infinity = L(P)/2.                   (2)

For grid spacing delta>0, replacing the source and output grids by
(delta/m)Z^d and delta Z^d multiplies (1) by delta. Requiring the identity
on the output grid does not change either optimum.

## One simultaneous attaining rule

Let r:R->Z be nearest-integer rounding with half ties away from zero, and
apply it componentwise to vectors. It is odd, fixes integers and commutes
with every signed permutation: r(sy)=s r(y) for s in B_d. Define

    q_P(x) = P r(P^{-1}x).                                   (3)

Since P and P^{-1} are integer matrices, (3) has integer outputs, preserves
the complete refined grid as its input domain, and fixes Z^d. For
g=P s P^{-1}, direct substitution gives

    q_P(gx)=P r(s P^{-1}x)=P s r(P^{-1}x)=g q_P(x).

This is one rule for the entire group, including inputs with nontrivial
stabilizers. In particular, if gx=x, the displayed identity forces
g q_P(x)=q_P(x); no independent orbit choices or incompatible ties occur.

Put c_m=floor(m/2)/m. Every coordinate of y=P^{-1}x is in (1/m)Z, so
|r(y_j)-y_j|<=c_m. Thus

    ||q_P(x)-x||_infinity
      = ||P(r(y)-y)||_infinity <= c_m L(P).

The same argument on real inputs uses |r(y_j)-y_j|<=1/2. This proves both
upper bounds with the same explicit rule.

## Stabilizers force the matching lower bound

Choose a row i maximizing its absolute row sum. Choose a sign vector
v in {+1,-1}^d with v_j equal to the sign of P_ij when P_ij is nonzero;
either sign is allowed at a zero entry. Then

    ||Pv||_infinity = L(P).                                  (4)

Indeed the i-th coordinate equals its absolute row sum, and every other
coordinate is bounded by its own row sum.

Write D_v=diag(v). The subgroup H=D_v S_d D_v of B_d fixes v, where S_d
denotes all ordinary permutation matrices. Its common fixed vectors are
exactly the line R v: D_v sends that fixed space to the vectors with all
coordinates equal. This includes d=1, where the line is the full space.

Take x=c_m Pv. It is a valid input because P is integral. Every element
of P H P^{-1} fixes x. Any G-equivariant q must therefore have q(x) in
the fixed space P R v. Moreover P^{-1}q(x) is integral by unimodularity.
An integral vector on R v is n v for an integer n, since every coordinate
of v is +1 or -1. Consequently

    q(x)=n Pv,
    ||q(x)-x||_infinity=|n-c_m| L(P) >= c_m L(P),

because 0<c_m<=1/2. This lower bound applies even to arbitrary coupled,
nonlinear q, and proves (1). For real inputs take x=Pv/2 and repeat the
argument with c=1/2 to prove (2). Both lower bounds are attained at an
actual point, rather than only approached as a supremum. Scaling x and
q by delta proves the grid-spacing statement.

## The released sheared-dihedral example

For P_k=[[1,k],[0,1]], G has eight elements and

    R_m(P_k)=(|k|+1) floor(m/2)/m,
    R_real(P_k)=(|k|+1)/2.

In particular the P_2 example in PR5079 has radius 3/2 on the half-grid
and on R^2, and radius 1 on the third-grid. Krzysztof Wojt's PR5122 already
gives the same lower value for its reflection subgroup A_(2k); that
subgroup value is not new here. The new conclusion supplies a compatible
rounder for all eight frames simultaneously, and the exact formula for
every unimodular P in every dimension. It answers a class of PR5122's
larger-finite-group question, not the question for every finite integer group.

## Evidence and boundary

The all-input and all-dimension claims rest on this proof. The executable
checks a bounded domain using two different arithmetic methods. Its integer
orbit oracle constructs all eight physical frame matrices, finds every
point stabilizer, and enumerates every integer output in a box containing
any improvement on a supplied feasible output. It tests the full orbit
error and literal stabilizer constraints. It imports no radius formula or
rounder. Its returned minima corroborate the lower and upper bounds.

No source claims that a current multiplication supplier reaches these
maximizing inputs. The domain is the complete grid or all real vectors.
The result supplies no paid rounding circuit, dirty-state restoration,
native realization, physical movement, stock, precision/tape or complete
signed supplier invoice. It does not change kappa or settle any of the
five selected framework assumptions. No formal proof-kernel or independent
human acceptance is claimed.
