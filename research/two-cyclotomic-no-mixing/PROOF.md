# Cubic and quintic sectors cannot mix

This proof was produced by Nick Petalas. Apache-2.0.

## Statement and credit

Let M be a positive integer. Let U be a unitary Clifford on M qubits,
with every entry in Q(i), and suppose the actual matrix on the entire bank
satisfies

    (U² + U + I)(U⁴ + U³ + U² + U + I) = 0.

Then exactly one of the two factors is zero. Consequently U has exact order
three or five, and its binary Pauli symplectic matrix S satisfies

    rank(S-I) = 2  in the cubic case,
    rank(S-I) = 4  in the quintic case.

Its native B-block rank is at most min(M,4), and at most min(M,2) in
the cubic case. The quintic case requires M >= 2.

The new implication is the exclusion of mixed sectors under the product
relation. This settles the explicit Phi3/Phi5 test in Open next question 2 of
[Nick Petalas's #6192](https://github.com/CrocSwap/integer-mult-bounds/pull/6192).
The pure-factor defect formulas above are cited consequences of that package,
not new formulas or an audit. Ross Richardson's
[#4081](https://github.com/CrocSwap/integer-mult-bounds/pull/4081)
supplies the earlier cubic Clifford trace gate and its Pauli-character method.
Cyclotomic irreducibility and the character calculation are classical tools;
no literature-wide priority claim is made for them.

## Spectral multiplicities

For odd n, the fields Q(i,zeta_n) and Q(zeta_(4n)) coincide: primitive roots
of coprime orders 4 and n generate the same compositum. Classical cyclotomic
irreducibility gives

    [Q(i,zeta_n):Q(i)] = phi(4n)/2 = phi(n).

See [Romyar Sharifi, Abstract Algebra, Theorem 6.6.11](https://www.math.ucla.edu/~sharifi/notes/algebra-ch06.html)
for the irreducibility theorem over Q. The displayed degree argument gives
the extension to Q(i); it is also the field argument retained in #6192.
In particular Phi3 and Phi5 remain irreducible over Q(i), with degrees
two and four.

Their product is squarefree. The assumed annihilation therefore decomposes
the Q(i)[X]-module into copies of the two simple modules. Equivalently, there
are nonnegative integers a,b, not both zero, such that

    characteristic_polynomial(U) = Phi3^a Phi5^b,
    2a + 4b = 2^M,
    Tr(U) = -a-b.

The trace follows because the sum of the primitive roots is -1 for each
of the primes three and five. In particular the trace cannot vanish.
This is a spectral statement about the actual whole-bank matrix and its
actual global phase, rather than a relation modulo phase or on a subspace.

## Clifford trace restriction

Here is the short Pauli argument from Richardson's trace gate. Label
Hermitian Paulis by v in F2^(2M). Clifford conjugation has the form

    U P_v U* = epsilon(v) P_(Sv),  epsilon(v) in {+1,-1}.

On K=ker(S-I), the sign epsilon is a character. To see this, conjugate
P_v P_w for v,w in K. Its Pauli multiplication phase is the same before
and after conjugation, so epsilon(v+w)=epsilon(v)epsilon(w). Thus the trace
of conjugation on the matrix space is either zero or |K|. The same map is
represented by U tensor conjugate(U), with trace |Tr(U)|². Hence

    |Tr(U)|² is zero or a power of two.

Since a+b is a positive integer, (a+b)² being a power of two forces a+b
itself to be a power of two. Unique prime factorization proves this last
step, including that the exponent of the square is even.

## The new no-mixing step

Suppose a>0 and b>0. From 2a+4b=2^M one obtains

    2^(M-2) < a+b < 2^(M-1).

The left strict inequality is equivalent to 2a>0; the right one is
equivalent to 2b>0. There is no power of two strictly between these two
consecutive powers. This contradicts the Clifford trace restriction.
Thus ab=0. If b=0, the minimal polynomial is Phi3, so Phi3(U)=0;
if a=0, it is Phi5, so Phi5(U)=0. The two alternatives cannot both hold
because the polynomials are coprime and the bank has positive dimension.
This proves the new implication at every M without finite extrapolation.

The rank consequences now follow directly from #6192's pure-factor theorem:
its exponent a in phi(n)=2^a is one at n=3 and two at n=5. This use of the
letter a in the cited theorem is separate from the cubic multiplicity above.
The native B block is a submatrix of S-I, so its rank has the stated cap.
No mixed-product rank or native implementation theorem is assumed.

## Boundary examples and exact checks

The checker uses the cubic Clifford

    C3 = (-I + iX + iY + iZ)/2

and the four-by-four quintic matrix displayed in #6192's proof, denoted C5.
The matrices serve as positive fixtures, not as new constructions. It checks
unitarity, the polynomial relations, exact orders and all Pauli generator
images using Gaussian rational arithmetic. No predecessor verifier is run.

Two eight-dimensional examples explain the scope of the implication:

* diag(C3,C3,C5) is Gaussian rational and unitary, satisfies the product
  relation, and satisfies neither individual relation. Its multiplicities
  are (a,b)=(2,1), trace -3 and squared trace 9. It fails the Pauli-normalizer
  test, so unitarity and the coefficient field alone do not suffice.
* C3 tensor C5 is a Gaussian-rational Clifford of exact order fifteen.
  It fails the product relation. Thus order dividing fifteen alone cannot
  replace the stated annihilator hypothesis.

An arithmetic control at dimension twelve, a=b=2, passes the trace test
despite having two sectors. This is only a control for the power-of-two
dimension argument; no twelve-dimensional Clifford construction is claimed.

The finite census enumerates every nonnegative solution of 2a+4b=2^M for
1 <= M <= 18. It tests the trace square as an integer and checks that
exactly the pure endpoints pass. The written proof supplies the unbounded
quantifiers. The matrix examples do not classify other cyclotomic products.

## Limitations

There is no emitted physical caller, productive-target credit, full paid bill,
dirty-helper contract, precision/tape realization, supplier admission or new
kappa here. The selected result and its five inherited assumptions are
unchanged. Several factors, other degree pairs, restricted-input relations,
different coefficient fields and approximate identities are not covered.
Independent human and formal proof-kernel review are unclaimed.
