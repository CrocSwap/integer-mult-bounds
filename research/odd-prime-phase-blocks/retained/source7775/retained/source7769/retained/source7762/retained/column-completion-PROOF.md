# One-column cyclotomic completion

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement

Write mu_m for the mth roots of unity. Let m,n>=2 and let A be an
n-by-(n-1) matrix with entries in mu_m and A* A=nI. Then its unique
orthogonal flat completion whose new column starts with 1 is

```text
w = (nI-AA*) e_1,       H = [A w].                         (1)
```

It satisfies H*H=nI and has entries in mu_lcm(2,m). Moreover:

1. If m is even, every entry of w belongs to mu_m, for every n>=2.
2. If m is an odd prime power and n>=3, every entry of w belongs to mu_m.

Thus composite even alphabets and odd prime-power alphabets retain their
original alphabet. Both the matrix order n and alphabet order m are arbitrary
under these hypotheses; they need not agree. This extends the prime-order
statement B097 of David Ganz's atlas, PR2849. That result and PR2855's
prime pilot application are cited rather than reverified here.

The n>=3 condition in the second conclusion is necessary. For any odd m,
the valid two-row input A=(1,1)^T has normalized completion (1,-1)^T.
Even allowing a global phase cannot put both entries in mu_m, since their
ratio is -1. The doubled-alphabet conclusion is therefore sharp without
a restriction on n. No sharpness assertion is made for odd composite m
and n>=3.

## The flat column and its integral entries

Set C=nI-AA*. Since A*A=nI, C is Hermitian, C^2=nC, and rank C=1.
Every diagonal entry of AA* is n-1, so C has diagonal 1. A rank-one
Hermitian positive matrix with C_11=1 satisfies C=C e_1 e_1* C.
Consequently C=ww*, |w_i|=1 and w_1=1. Also A*C=0, so A*w=0.
The squared norm of w is n, proving H*H=nI. The orthogonal complement
of A's columns has dimension one, proving normalized uniqueness.

For i>1 the formula is explicitly

```text
w_i = -sum_(j=1)^(n-1) A_ij conjugate(A_1j).              (2)
```

Hence w_i belongs to Z[zeta_m] and is an algebraic integer. No division by
n or a determinant denominator occurs. This is the useful integrality
property behind the alphabet extension.

## The classical cyclotomic facts

We use cyclotomic irreducibility and [Q(zeta_r):Q]=phi(r). Here are the
remaining arguments, to make their exact use explicit.

If alpha in Z[zeta_m] satisfies |alpha|=1, then alpha conjugate(alpha)=1.
All automorphisms of Q(zeta_m) commute with complex conjugation, since this
Galois group is abelian. Applying an automorphism therefore shows that
every algebraic conjugate of alpha has modulus one. Kronecker's theorem
implies that alpha is a root of unity.

For completeness, the needed Kronecker argument is finite. If alpha has
degree d, each power alpha^k is an algebraic integer of degree at most d,
and every conjugate still has modulus one. Coefficients of its monic
minimal polynomial are integer elementary symmetric sums, bounded in
absolute value by the corresponding binomial coefficients of degree at
most d. Only finitely many such polynomials exist, and each has finitely
many roots. Thus the sequence alpha,alpha^2,... has finitely many possible
values. Two powers agree; alpha!=0 then implies a positive power equals 1.

Put M=lcm(2,m). The roots of unity in Q(zeta_m)=Q(zeta_M) are exactly
mu_M. Indeed, if a primitive tth root lies in this field, the compositum
with Q(zeta_M) is Q(zeta_l), l=lcm(M,t). Thus phi(l)=phi(M).
Because M is even and M divides l, the product formula for phi shows
that increasing any existing prime exponent or adjoining any new odd
prime strictly increases phi. It follows that l=M and t divides M.
The reverse inclusion is immediate, using zeta_2m=-zeta_m^((m+1)/2)
when m is odd. These are classical facts, not new number-theory claims.

Applying them to every entry in (2) proves w_i in mu_M. For even m,
M=m, proving the first conclusion.

## Removing the sign for odd prime powers

Let m=p^a for an odd prime p and a>=1. Evaluation at zeta_m=1 followed
by reduction modulo p defines a ring map

```text
rho: Z[zeta_m] -> F_p,        rho(zeta_m)=1,
```

because Phi_(p^a)(1)=p. If n>=3, A has two distinct columns. Their
orthogonality is a sum of n elements of mu_m equal to zero. Applying
rho shows p divides n. Applying rho to (2) now gives

```text
rho(w_i) = -(n-1) = 1 in F_p.
```

Every element of mu_2m is either zeta_m^k or -zeta_m^k. Their images
under rho are respectively 1 and -1, which differ because p is odd.
Therefore each w_i lies in mu_m. The first entry already equals 1.
This proves the second conclusion and completes the theorem.

## Sources and scope

David Ganz's atlas B082/B097 in PR2849 supplies the one-column and
prime-order setting and explicitly leaves the composite alphabet outside
its proof. The prime-phase pilot application in PR2855 supplies the exact
recovery context. Their original files and credit remain unchanged.
Kronecker's theorem, cyclotomic irreducibility, cyclotomic field degrees
and the prime-power reduction are classical. Richard Stanley's
[Algebraic Combinatorics, Theorem 12.14](https://math.mit.edu/~rstan/algcomb/algcomb.pdf)
and Eric Moorhouse's
[Cyclotomic Fields with Applications](https://ericmoorhouse.org/handouts/cyclotomic_fields.pdf)
are accessible mathematical precedents for the integrality argument.
The proof above supplies the actual implication used here.

The contribution is the stated extension of this project's completion
interface and its exact finite corroboration. Global literature priority,
independent human and formal proof-kernel review are unclaimed. More than
one missing column, approximate data, physical preparation, paid consumption,
supplier admission and complete multiplication-theorem obligations remain
outside scope. No new kappa or selected-frontier change follows.
