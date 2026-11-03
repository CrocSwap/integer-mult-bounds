# Complete automorphisms for the unequal cutoffs (2,3)

Let K be a finite field, q=|K|, p=char K, and
A=K[x,y]/(x²,y³). We classify unital K-linear algebra automorphisms, using the
ordered basis (1,x,y,xy,y²,xy²). This answers the first unequal-cutoff question
released in Nick Petalas's PR #6682. It does not claim an all-cutoff family,
algebra recognition, semilinear symmetry or a physical implementation.

## Normal form and necessity

Every automorphism has exactly the form

X = a*x + alpha*x*y + beta*y² + gamma*x*y²,
Y = c*x + d*y + delta*x*y + epsilon*y² + zeta*x*y²,

where a,d are nonzero, all higher displayed coefficients are arbitrary, and

2*beta=0, 3*c=0 in K.

Thus beta is free only in characteristic 2, and c only in characteristic 3.
The five always-free coefficients are alpha,gamma,delta,epsilon,zeta. No y
linear term in X is permitted.

To prove necessity, the ideal m=(x,y) is the nilradical and unique maximal
ideal: its fourth power is zero, and any element with nonzero constant term is
a unit by a finite geometric series. An automorphism preserves m and m², so
its induced map on m/m² is invertible. Initially write

X=a*x+b*y+alpha*x*y+beta*y²+gamma*x*y²,
Y=c*x+d*y+delta*x*y+epsilon*y²+zeta*x*y².

The coefficient of y² in X² is b²; no other product contributes that monomial.
Since K is a field, X²=0 forces b=0. The tangent matrix is then
[[a,c],[0,d]], so a,d are nonzero. With b=0, direct multiplication gives

X²=2*a*beta*x*y²,
Y³=3*c*d²*x*y².

All other monomials vanish modulo x²,y³; terms involving a degree-two or higher
coefficient in Y³ have degree at least four. The nonzero a,d now give exactly
the two displayed characteristic restrictions. This also rules out an
unequal-variable swap, even though a swap has invertible linear tangent.

## Every allowed lift is an automorphism

For any coefficients satisfying the normal form, X²=Y³=0. Substitution
x->X,y->Y therefore defines a unital K-algebra endomorphism of A. The radical
filtration has graded bases

A/m: (1),
m/m²: (x,y),
m²/m³: (xy,y²),
m³: (xy²).

The four associated-graded blocks of substitution, in that order, are

1; [[a,c],[0,d]]; [[a*d,2*c*d],[0,d²]]; a*d².

Indeed XY=ad*xy modulo m³, Y²=2cd*xy+d²*y² modulo m³, and
XY²=ad²*xy². Higher coefficients do not enter these graded blocks. The full
six-dimensional matrix is block triangular along the filtration and has

det(phi)=(a*d)*(a*d³)*(a*d²)=a³*d^6,

which is nonzero. Thus the endomorphism is a bijection of the six-dimensional
K-space and hence an algebra automorphism. This proves sufficiency of every
allowed nonlinear lift, not merely a necessary tangent restriction. Generator
coefficients uniquely determine the map, so the parametrization has no repeats.

## Order and determinant image

There are (q-1)² nonzero choices of (a,d), five always-free field coefficients,
and one additional free coefficient in characteristic 2 or 3. Consequently

|Aut_K(A)| = (q-1)²*q^6 if p is 2 or 3,
|Aut_K(A)| = (q-1)²*q^5 otherwise.

The exact determinant image is the cube subgroup H3={u³:u in K*}. Every
allowed determinant is (a*d²)³, and every u³ is attained by x->u*x,y->y.
No higher coefficient changes the determinant. Fibers of this character have
equal size by multiplication in the finite automorphism group. These are
statements about K-linear automorphisms; a nontrivial automorphism of K itself
is not included.

Characteristic 2 admits the genuinely nonlinear x->x+y². Characteristic 3
admits the triangular y->y+x. Both preserve the defining relations in exactly
the stated characteristics. A diagonal-tangent test alone misses the nonlinear
restriction in odd characteristic, while a monomial-tangent assumption misses
the characteristic-three family.

## Finite evidence and its limits

The written proof covers every finite field. The executable census is restricted
to the four frozen fields F2,F3,F4,F5, with F4 encoded as
F2[t]/(t²+t+1), polynomial mask 7. The primary constructs the normal form, checks
both defining relations by literal quotient multiplication and calculates every
actual 6x6 determinant by field Gaussian elimination. It stores all accepted
pairs' ten coefficients, not just an asserted count, in ACCEPTED-MAPS.json.gz.
Decompressed canonical rows determine the mathematical value; gzip container
bytes are not a cross-environment equality gate.

The independent oracle starts from all radical generator images, tests the
relations by its own multiplier and accepts invertible substitutions. The
profile compares the actual complete accepted-set digest and full determinant
histogram, not only agreement with a predicted group order. The four census
sizes are 64,2916,36864,50000, totaling 89844. The additional 180 nonlinear
witnesses in F7 and F13 cover all ordered nonzero diagonal scalars for their
fixed lift; they are not exhaustive automorphism censuses in those fields.

Selected nonlinear maps also check all 36 basis products, composition of their
substitution matrices, forbidden swaps and both exceptional characteristic
restrictions. These finite controls corroborate the theorem. No predecessor
checker is imported or executed, and no formal proof-kernel or independent
human acceptance is claimed.

## Exact predecessor boundary

Nick Petalas's PR #6682 supplies the equal non-Frobenius cutoff result and
explicitly releases the unequal (2,3) tangent/determinant question. Ali Romman's
PR #5316 covers the one-variable case and retains PR #5252's covariant/nilpotent
question and David Ganz's atlas lineage. Ali Romman's #5459 and Petalas's #6578
cover characteristic-power cutoff families; (2,3) cannot consist of powers of
one characteristic. Their radical/lift/count/determinant methods are prior.
The new result is this fixed unequal algebra's complete normal form, order and
determinant image. Classical local-algebra filtration and determinant arguments
are not new principles.
