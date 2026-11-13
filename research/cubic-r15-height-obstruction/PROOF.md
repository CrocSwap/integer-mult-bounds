# A coefficient-height obstruction at arity 15

Produced by Nick Petalas. Apache-2.0.

## Statement and exact contract

Use the exact dyadic cubic-reader contract of Armin Pourshafeie / apoursh,
PR #6212. The distinct registers y,a,b have arbitrary incoming values Y,A,B.
Retain all fifteen children, in their original order:

```text
y += a^3
a += b
```

The eager endpoint is (Y+15A^3,A,B). The deferred endpoint is
(Y+sum_{i=0}^{14}(A+iB)^3,A+15B,B). An appended repair may use any fixed
invertible dyadic linear source changes on a,b alone and signed dyadic
weighted cube queries, with both sources restored. There is no output feedback, child
fusion, nonlinear source change or output recoding. This is the inherited
contract, not a new physical implementation.

For a nonzero dyadic source row (alpha,beta), write it as t(a,b), where
(a,b) is a primitive integer pair, a>0 or a=0<b, and t is nonzero and dyadic.
Define its primitive height as max(|a|,|b|). This height is invariant under
nonzero dyadic rescaling of the source row whenever that rescaling is legal.

**Theorem, finite certificate with a scoped algebraic proof.** Any exact
three-query repair at arity 15 has at least two source directions of
primitive height greater than 64. The third direction is unrestricted.
This does not prove that a three-query repair exists, or that four queries
are necessary. The bound 64 is not asserted to be sharp.

The new computational content is a complete pair exclusion over 5,040
primitive directions and 12,698,280 unordered pairs. For each pair an exact
algebraic reduction determines its only possible third direction, without
a height cutoff on that direction. Two full implementations find no
dyadic triple containing a pair from this domain. The theorem depends on that finite
execution. It is not a proof-kernel formalization.

## Normalize all possible source rows

The output defect, credited to Nick Petalas's PR #6200, is

```text
D15 = 315 A^2 B + 3045 A B^2 + 11025 B^3.
```

Every source row reached by a product of dyadic source changes has dyadic
entries. Clear powers of two from a nonzero row and divide the resulting
integer pair by its gcd, choosing the sign above. The resulting scale t is
dyadic, so gamma(alpha A+beta B)^3 becomes
(gamma t^3)(aA+bB)^3 with a dyadic weight. Conversely, a primitive integer
row has a determinant-one integer completion by Bezout's identity. Thus
excluding primitive weighted-cube decompositions excludes the corresponding
source programs even without imposing chronological restrictions.

Two rational cubes cannot represent D15. In a two-cube representation,
A^3 cancellation and the nonzero A^2 B coefficient force both A coefficients
and both weights to be nonzero. Normalize their forms to A+sB and A+tB.
The coefficient comparison from PR #6200 / apoursh's PR #6212 gives

```text
s+t = 3045/315 = 29/3,
s^2+s*t+t^2 = 11025/105 = 105,
(t-s)^2 = 4*105 - 3*(29/3)^2 = 419/3.
```

A rational square has a square reduced denominator; 419/3 has denominator
3. Hence zero, one or two cubes are impossible, even over Q. In a
three-query representation the weights are therefore nonzero and the
three primitive directions are distinct. Repeated directions would combine
to at most two cubes.

## Determine the unrestricted third row

Write the normalized moments of D15 as

```text
(s0,s1,s2,s3) = (0,105,1015,11025).
```

For three distinct rows (a_j,b_j), the homogeneous version of the node
condition in Nick Petalas's PR #6653 is

```text
s1*(b1*b2*a3 + b1*a2*b3 + a1*b2*b3)
- s2*(b1*a2*a3 + a1*b2*a3 + a1*a2*b3)
+ s3*a1*a2*a3 = 0.                                      (1)
```

One direct derivation applies the commuting differential operators
(a_j partial_B - b_j partial_A) to D15. Their product annihilates every
one of the three proposed cubes, since one factor annihilates its own
source form. Applied to D15, the product is six times the left side of
(1). This also proves (1) when a row is the pure-B direction (0,1), with
no division by its A coefficient. For finite slopes it is precisely the
credited node condition after homogenization.

Fix the first two rows u=(a,b) and v=(c,d). Put

```text
E = s1*b*d - s2*(b*c+a*d) + s3*a*c,
F = s1*(b*c+a*d) - s2*a*c.
```

Equation (1) says E*a3+F*b3=0. Unless E=F=0, its unique projective solution
is the primitive normalization of (F,-E). The verifier explicitly rejects
an E=F=0 pair as an incomplete certificate; none occurs in the finite domain.
It discards a repeated third direction using the two-cube argument above.

For any remaining candidate triple, a row j with a_j != 0 has the unique
weight

```text
gamma_j = [s2*a_k*a_l - s1*(b_k*a_l+a_k*b_l)]
          / [a_j*(b_j*a_k-b_k*a_j)*(b_j*a_l-b_l*a_j)].     (2)
```

Here {j,k,l}={1,2,3}. To derive (2), apply the moment functional
L(1)=0, L(x)=s1, L(x^2)=s2 to the degree-two Lagrange polynomial for the
three finite slopes, then undo the a_j^3 normalization. If one direction
is (0,1), the same formula for the other two follows directly from A^3
and A^2 B comparison. Its remaining weight is
s3 minus the two finite rows' B^3 contributions.

A nonzero rational numerator/denominator is dyadic exactly when the
absolute denominator after gcd reduction is a power of two. The primary
checker uses this integer test before constructing fractions. Every
accepted control also undergoes all four exact moment checks.

## Complete finite domain and result

The height-64 projective integer box is exactly

```text
{(0,1)} union {(a,b): 1<=a<=64, -64<=b<=64, gcd(a,b)=1}.
```

It has 5,040 rows. Distinct canonical primitive rows are distinct projective
directions, so every unordered pair is independent. The primary checker
visits all 5,040*5,039/2 = 12,698,280 pairs and obtains:

| Classification | Pairs |
| --- | ---: |
| Unique third direction repeats one of the pair | 17 |
| Unique distinct triple has a non-dyadic forced weight | 12,698,263 |
| Undetermined third direction | 0 |
| Admissible dyadic triple | 0 |

These are per-pair classifications, not a classification of every failed
search method or every global representation. The third primitive row can
have arbitrarily larger height than the pair cutoff; it is never clipped.
A separate positive control with two height-one rows forces a third row of
height 129 and is accepted, testing that distinction.

If an exact three-query repair had two directions of height at most 64,
their unordered pair would occur in the census. Its unique third direction
and forced weights would pass. None does, proving the theorem.

## Separate coordinate proof and checker

The second checker does not import the primary one or use (1) or (2).
For each pair u=(a,b), v=(c,d), put X=aA+bB, Y=cA+dB and delta=ad-bc.
Expand

```text
delta^3 D15(A,B) = P(X,Y) = p0 X^3+p1 X^2 Y+p2 X Y^2+p3 Y^3
```

by substituting A=(dX-bY)/delta and B=(-cX+aY)/delta.
A third cube, together with arbitrary X^3 and Y^3 terms, must account for
both mixed coefficients. If exactly one of p1,p2 vanishes, this is
impossible. If both vanish, D15 would be two rational cubes, already
excluded above. Otherwise the third form is proportional to p1 X+p2 Y,
and the forced weights on the first two primitive rows are

```text
(3*p0*p2-p1^2)/(3*delta^3*p2),
(3*p3*p1-p2^2)/(3*delta^3*p1).
```

If g=gcd(p1*a+p2*c,p1*b+p2*d), the third primitive-row weight, before
canonical sign correction, is g^3/(3*delta^3*p1*p2). The second checker
checks these dyadic denominators over the same complete pair domain.
Its different intermediate classification is recorded by its own output;
both implementations must reject all 12,698,280 pairs.

## Scope, credit and next step

The question comes from apoursh's PR #7475 and its remaining-arity opening;
its r=24 construction is not rerun here. apoursh's #7479 proves modular
solubility for every odd modulus, and #7478 classifies a fixed equal-weight
family. Neither result is contradicted by a coefficient-height restriction
on one global dyadic representation. The new pair reduction and complete
height-64 exclusion are this contribution. The fixed reader, general-frame
contract, node lemma and earlier constructions retain their named credit.
No predecessor executable is imported or executed.

There is no repaired word, physical query price, favorable invoice or new
kappa. Native caller compatibility, chronology, restoration costs, routing,
precision, storage and the five selected framework assumptions remain
outside this finite coefficient result. A larger unrestricted search must
allow at least two primitive rows beyond height 64; it may instead seek a
stronger global valuation argument. Neither path is reserved here.
