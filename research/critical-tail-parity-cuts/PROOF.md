# The sharp critical-tail macro-cut envelope

Produced by Nick Petalas. Apache-2.0.

## Statement

Let N be a positive power of two and let

```text
f(z) = 1 + sum_(j=1)^(N-1) f_j z^j,     sum_(j>=1) |f_j| <= 1,
```

with real or complex coefficients. Let T_N(f) be multiplication by f modulo
z^N in coefficient order. Use the exact parity compiler defined below.
A macro is one complete Toeplitz shear. The right shear precedes both
children; the left shear follows both children. The two children may use
any interleaving preserving their own macro orders.

At any complete-macro cut, including the two endpoints, write T_N(f)=QP,
where P has executed and Q remains. Then

```text
max(||P||_infinity, ||P^-1||_infinity,
    ||Q||_infinity, ||Q^-1||_infinity) <= N.                 (1)
```

For each dyadic N this common bound is optimal. The quantifier includes
arbitrary coefficients in the stated tail ball and every legal schedule.
It excludes cuts inside a shear's implementation.

## Definition and attribution of the compiler

The retained construction is section 3 of Cinna Davis / PR4100's
`vendor/SHALLOW-TOEPLITZ.md`, following Vlado Vojdanovski / PR1673.
James Reed / PR4699 supplies the earlier one-level shared-budget estimate.
The following factorization is retained construction, not a new identity.
We write it out to specify every cut and prove the new boundary estimate.

For N=2m, in the even/odd coordinate order, put

```text
f(z) = e(z^2) + z o(z^2),       k = o/e mod z^m,
s = e - z o^2/e mod z^m,       E = T_m(e), S = T_m(s), K = T_m(k),
U = [ I ZK ; 0 I ],            L = [ I 0 ; K I ],
T_N(f) = L diag(E,S) U,
```

where O=T_m(o) and Z=T_m(z). Multiplication verifies this identity because E,O,K,Z
commute and EK=O. All inverses exist as finite formal power series since
each symbol has constant term one. A one-coordinate leaf is the identity.
Coordinate permutations have infinity norm one and preserve the argument.

## The unit tail ball is closed under both children

Let a=||e-1||_1 and b=||o||_1 for coefficient l1 norm. Then a+b<=1.

If a<1, the finite inverse of e has norm at most

```text
sum_(j=0)^(m-1) a^j <= 1/(1-a).
```

Indeed e-1 has zero constant term, so its m-th power vanishes modulo z^m.
Coefficient norm is submultiplicative and truncation cannot increase it.
Consequently

```text
||k||_1 <= b/(1-a) <= 1,
||s-1||_1 <= a + b^2/(1-a) <= a+b <= 1.                  (2)
```

If a=1, the budget forces b=0. Then o=k=0 and s=e. Both conclusions of
(2) still hold. This branch uses no division by 1-a. The even child also
has tail at most one. Thus every descendant is again in the same unit
tail ball, including its critical boundary.

It follows that each of U,L,U^-1,L^-1 has infinity norm at most two.
The inverse shear changes only the sign of its off-diagonal block;
||K||_infinity<=||k||_1 and ||ZK||_infinity<=||k||_1.

## Induction at every cut

For N=1, all four operators are the identity. Assume (1) at dimension m.
During the child phase, let P_e,P_s be the child prefixes and Q_e,Q_s
their remaining suffixes. The exact four operators are

```text
P    = diag(P_e,P_s) U,
P^-1 = U^-1 diag(P_e^-1,P_s^-1),
Q    = L diag(Q_e,Q_s),
Q^-1 = diag(Q_e^-1,Q_s^-1) L^-1.
```

The infinity norm of a coordinate direct sum is the maximum of its
summands' norms. Each displayed diagonal factor has norm at most m by
induction and (2). The neighboring shear or inverse shear has norm at
most two. Submultiplicativity gives 2m=N for every displayed operator.

Every pair of legal child cuts can occur in a legal parent interleaving:
execute each child's chosen prefix, then each remaining suffix, preserving
the order inside each child. Conversely every parent cut in the child
phase specifies such a pair. This covers arbitrary legal interleavings,
including either child empty or complete. Parallel disjoint macros may be
serialized, so parallel-layer boundaries are included as well.

The only other cuts are the initial and final endpoints. At N>=2,
||T_N(f)||_infinity<=2<=N. Writing A=T_N(f)-I gives A^N=0 and ||A||<=1,
so the exact finite identity

```text
T_N(f)^-1 = sum_(j=0)^(N-1) (-A)^j
```

gives ||T_N(f)^-1||_infinity<=N. The endpoint identity factors have norm
one. This completes the induction without a strict-tail assumption.

## Sharpness and scope

For N>=2 take f=1-z. Its inverse is I+Z+...+Z^(N-1). The last row has
N entries equal to one, so its infinity norm is exactly N. This inverse
is P^-1 at the final cut and Q^-1 at the initial cut. At N=1 the identity
already attains one. Therefore no smaller bound can control all four
operators for each N. This elementary endpoint witness is credited prior
context; the new step is the universal upper bound at every macro cut.

Brian / PR4731 already supplies the four-cut bound 1/(1-eta) at eta<1,
and PR4737 supplies the sharper forward-prefix bound 1+eta at eta<=1.
Nick Petalas / PR4831 gives the exact binomial forward-suffix law. None
of those narrower bounds is claimed as new here. The proof above starts
from the compiler definition and the finite inverse, and executes no
predecessor verifier. It concerns the full critical tail ball, rather
than just a binomial family or the forward-prefix operator.

This bound permits a log2(N) macro amplification allowance at the critical
boundary. It does not admit that boundary to the original Gaussian caller,
whose other hypotheses remain strict. No claim prices internal shear
gates, rounding events, fixed tapes, preparation, storage, dirty restoration,
native realization, recursive invoices or the outer algorithm. This is a
scoped written proof, not a proof-kernel certificate or a complete
multiplication theorem. No new kappa is claimed.
