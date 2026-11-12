# Scalar ascent of a recovered commutative multiplication tensor

This constructive proof and certificate adapter were produced by Nick Petalas.
Apache-2.0. Restriction of scalars and normalization of a unital isotope are
classical. The contribution here is the explicit bridge between the existing
prime-field recovery interface and a general extension-field certificate.
No literature-priority claim is made for the underlying algebraic facts.

## Proposition and conventions

Let K/F be a finite field extension of degree d. The fields themselves need
not be finite. Let t:U x V -> Z be K-bilinear, with all three K-dimensions
equal to n > 0. Matrices act on column vectors. Restriction uses one fixed
F-basis of K and the same coordinate packing in each of U,V,Z.

The following conditions are equivalent.

1. t is K-isotopic to multiplication in a commutative associative unital
   K-algebra of dimension n.
2. Res(t) is F-isotopic to multiplication in a commutative associative
   unital F-algebra of dimension dn.

More precisely, suppose a certificate for condition 2 supplies an F-algebra
B, its multiplication table, and invertible F-linear maps

    Res(t)(P a, Q b) = S(ab).

The maps P,Q,S need not be K-linear and B is not initially supplied with a
K-vector-space structure. Let e be its unit, and pack the vectors P e and Q e
as u in U and v in V. Define K-linear slices

    R_v(x) = t(x,v),    L_u(y) = t(u,y).

Both slices are invertible. The explicit K-bilinear product on Z

    mu(x,y) = t(R_v^(-1) x, L_u^(-1) y)

is commutative, associative and unital, with unit t(u,v). Its K-table and
the three maps R_v^(-1), L_u^(-1), I_Z form a certificate for condition 1.
This construction requires no decomposition of the K-nucleus and no
Frobenius height computation.

## Proof

Condition 1 implies condition 2 by restricting every map and algebra operation
to F. For the converse, apply the given isotopy with b=e and with a=e:

    R_v P = S,    L_u Q = S.

Thus the restricted F-linear maps R_v and L_u are invertible. They are also
K-linear by the stipulated K-bilinearity of t. Their inverses are K-linear:
if A is a K-linear bijection, A(A^(-1)(lambda z)) = lambda z =
A(lambda A^(-1)z), and injectivity equates the two inverse values.

Now write x=S a and y=S b as F-vectors. The two displayed slice identities
give

    mu(S a,S b) = t(P a,Q b) = S(ab).

Consequently S is an F-algebra isomorphism from B to (Z,mu). Commutativity,
associativity and the unit S e are identities of the product and therefore
hold for every vector of Z, regardless of scalar presentation. The product
is K-bilinear by its formula. These facts make (Z,mu) a commutative
associative unital K-algebra. Finally S e=t(Pe,Qe)=t(u,v), and the formula
for mu is exactly the claimed K-isotopy. This proves the proposition.

In particular, the K-action on the recovered algebra could also be described
by a conjugated F-linear action through S. The adapter need not discover or
diagonalize that action. It uses the output coordinates already present in t.

## Recovering the unit and constructing the certificate

The source interface returns a multiplication table and P,Q,S, without a
separate unit vector. Solve the linear equations

    sum_i e_i B[i,j,k] = delta[j,k]

for e. A unital algebra has a unique solution, since two left identities in
a commutative algebra agree by multiplying them. The reference also checks
both unit identities, associativity, commutativity, every source basis
isotopy equality and invertibility of the three supplied maps. Invalid
certificates are rejected before ascent. This is certificate consumption,
not a call to an existing recognizer or a replay of its scientific suite.

Pack Pe,Qe into K-vectors using the fixed field basis. Compute the slices,
invert them over K and evaluate the product on all pairs of K-basis vectors.
The reference returns `table`, `unit`, `U`, `V`, `W`, with W the identity.
It checks the returned K-certificate as well. For a symbolic recognizer,
the forward implication and this adapter show that applying the general
F-recognizer to Res(t) is a necessary-and-sufficient K-recognition procedure.
The predecessor recognition theorem remains a cited premise.

The procedure is polynomial in n and d for a supplied exact field interface.
Dense source certificate validation costs at most O((dn)^5) F-operations
and the displayed slice/table construction at most O(n^5) K-operations
using literal contractions. These are loose operation bounds, not a speed
claim, bit-complexity bound or bound on constructing the field. The reference
has hard finite capacities listed in README.md.

## Two hypotheses that cannot be silently dropped

K-bilinearity is essential. With F=F2, K=F4, the map t(x,y)=x^2 y is
F-bilinear and F-isotopic to field multiplication, since squaring is an
invertible F-linear map. It is not K-linear in its first argument:
t(a,1)=a^2 differs from a t(1,1)=a for a outside F2. Composing with
invertible K-linear factor maps cannot change that failure of K-bilinearity.
Thus an arbitrary F-tensor with a guessed K-coordinate grouping is outside
the proposition.

The general commutative recognizer is required. It cannot be replaced by the
prime-field local characteristic-power truncated-polynomial recognizer.
For example, K=F4, n=1, t is K multiplication. Res(t) is multiplication in
the reduced F2-algebra F4 of dimension two. The only dimension-two nonempty
truncated model over F2 is F2[x]/x^2, which has a nonzero square-zero element.
These algebras are not isomorphic. They are not isotopic either: for unital
commutative associative algebras, any isotopy normalizes to an isomorphism
by multiplying its output by the inverse of the images of the two units.
Equivalently, field multiplication has every nonzero slice invertible,
whereas multiplication by x in the dual numbers is a nonzero singular slice.
The reference checks this reduced/nilpotent boundary directly.

This proposition does not transfer a prescribed algebra-class label, a
special-linear determinant label or an automorphism count through restriction.
Those tasks require their own scalar-aware arguments.

## Relationship to prior recognition

Ali Romman's #5540 supplies general prime-field recovery, including
nonreduced algebras, and asks for an extension-field input layer. Its
necessity/sufficiency theorem and source implementation are not rechecked.
Ali Romman's #5637 implements a direct extension-field recognizer for local
characteristic-power truncated polynomial algebras. Its README explicitly
leaves general residue fields and products outside that implementation.

Nick Petalas's older #6464 already gives a general recognition theorem over
any supplied exact field, using a different cyclic-module construction.
No claim to extend that theorem is made here and its construction is not
used. The new artifact is a scalar-restriction certificate adapter. It
allows the existing prime-field recovery contract to supply K-linear output
without implementing nucleus decomposition over K. Neither its proof nor
its implementation imports a predecessor executable.
