# Exact collision density over an arbitrary cyclic axis

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and result

Let m >= 2 be an integer. Let D be a nonempty finite list of integer pairs
d=(a,b), each satisfying gcd(a,b,m)=1. Repetitions are permitted. A projection
coefficient v=(x,y) in (Z/mZ)^2 is safe when

    ax+by != 0 mod m       for every (a,b) in D.

For each divisor q>1 of m, reduce D modulo q. Its elements remain primitive.
Identify pairs that differ by multiplication by a unit of Z/qZ. Write d_q
for the number of represented classes, and phi(q) for Euler's totient.
Then the exact number of safe coefficient pairs is

    A_m(D) = m^2 - 1 - sum_{q|m, q>1} phi(q) d_q.              (1)

The exact number of safe primitive coefficient pairs is

    A_m^prim(D) = J_2(m) - phi(m) d_m,                       (2)
    J_2(m) = m^2 product_{p|m, p prime} (1 - 1/p^2).

Put psi(m)=m product_{p|m}(1+1/p)=J_2(m)/phi(m). A safe pair exists if and
only if d_m < psi(m). Whenever one exists, a primitive one exists and the
construction below finds it. Consequently psi(m) is the exact minimum
number of primitive demand classes needed to block every projection pair.
Taking all classes attains the threshold. These are quantified algebraic
statements, not empirical extrapolations.

The empty list instead has A_m(empty)=m^2 and A_m^prim(empty)=J_2(m).
Subtracting the origin in (1) requires the nonempty hypothesis.

## Primitive kernels

Work in R=Z/qZ. If d=(a,b) is primitive, Bezout gives u,v with ua+vb=1
in R. The map t -> t(-b,a) is a bijection from R to the kernel of w -> d.w.
It is injective because t(-b,a)=0 implies t=0 by Bezout. The dot map is
onto, again by Bezout, so its kernel has q elements and this injection
supplies them all. Moreover gcd(-tb,ta,q)=gcd(t,q). Exactly phi(q) kernel
vectors are primitive.

If a primitive w lies in the kernels of primitive demands d and e, apply
the same statement to w. Both d and e are unit multiples of (-w_2,w_1),
so they represent the same projective class. Conversely, unit multiples
have the same kernel. Distinct demand classes thus have disjoint kernels
within the primitive coefficient pairs. Their full kernels can intersect
in nonprimitive vectors. These intersections prevent direct reuse of a
prime-field line count with the prime replaced by m.

There are J_2(q) primitive pairs. Exclude pairs whose two coordinates are
divisible by any prime dividing q; inclusion-exclusion gives
q^2 product_{p|q}(1-p^-2). The unit action on primitive pairs is free,
because a unit fixing a primitive pair equals one by Bezout. Its orbits
have phi(q) elements, giving psi(q)=J_2(q)/phi(q) classes.

Therefore exactly

    J_2(q) - phi(q) d_q                                   (3)

primitive coefficient pairs modulo q are safe for the reduced demands.

## The divisor decomposition

Every nonzero v in (Z/mZ)^2 has a well-defined

    g=gcd(v_1,v_2,m) < m,    q=m/g > 1.

The map w mod q -> g w mod m is a bijection from primitive pairs modulo q
to this stratum, and

    d.(g w)=0 mod m  iff  d.w=0 mod q.

Apply (3) to every stratum. The origin fails every nonempty demand list.
Hence A_m(D)=sum_{q|m,q>1}[J_2(q)-phi(q)d_q]. The same partition of all
nonzero pairs gives sum_{q|m,q>1}J_2(q)=m^2-1, proving (1). The g=1
stratum gives (2). Primitivity of each demand at every divisor is essential.

## Existence, a witness and the sharp threshold

If d_m<psi(m), choose a primitive c=(a,b) in an unrepresented class. Set
v=(-b,a). If a demand annihilated v, the primitive-kernel argument would
make it a unit multiple of c, a contradiction. This gives a primitive
safe witness and proves sufficiency.

Reduction from primitive pairs modulo m to primitive pairs modulo q|m is
onto. Split m into prime powers. At primes dividing q, any lift of the
local pair remains primitive. At primes not dividing q, choose (1,0).
CRT combines these local choices. Reduction on projective classes is
therefore also onto. If D represents every class modulo m, it represents
every class modulo q. Every term in (3) vanishes, so A_m(D)=0. This proves
necessity, including nonprimitive coefficient pairs.

Each primitive demand represents just one class modulo m. At least psi(m)
distinct classes are needed to block every pair; a complete class list
does block them all. This is a threshold for primitive demand lists, not
a claim that each such list is the full difference set of a prescribed
point configuration.

## Projection interpretation and examples

Let S be a finite subset of (Z/mZ)^2 with every difference between distinct
points primitive modulo m. Select one sign for each unordered difference
to form D. The projection s -> v.s is injective on S exactly when v is safe
for D. Divide (1) by m^2, or (2) by J_2(m), for its exact success probability
with uniform unrestricted or primitive coefficients. Translation of S
does not change D. A singleton S uses the separate empty-list case.

For m=9 and D={(1,0),(1,3)}, d_3=1 and d_9=2, giving

    81 - 1 - 2*1 - 6*2 = 66.

Keeping only the q=9 term would give 68. Treating distinct full-modulus
classes as field lines would give 64. Both substitutions are wrong.
With D={(1,0),(0,1)}, both class counts are two and the correct count is 64.
For S={(0,0),(1,0),(2,3)}, all differences are primitive, d_3=1 and d_9=3;
exactly 60 of the 81 projections are injective.

For m=p^e, formula (1) becomes

    p^(2e)-1 - sum_{j=1}^e (p^j-p^(j-1)) d_(p^j).

A square axis therefore needs class data at both p and p^2. This is the
arithmetic information the scoped collision-avoidance step must retain.
No numerical resampling or recovery guarantee follows from this count.

Nonprimitive demands are excluded. The single demand (3,0) modulo 9 has
54 safe pairs, while a primitive single demand has 72. The executable
rejects this domain instead of applying (1) to it.

## Evidence and attribution

The proof is self-contained. The checker constructs complete kernel bitmasks
by evaluating every literal dot product. Its oracle uses no projective class
formula and imports no predecessor verifier. It checks every subset of the
literal kernel representatives for moduli 2 through 9. Larger declared shapes
check empty/full lists, every singleton, every full-list single deletion and
every pair among the first twelve representatives. The generated receipt
enumerates each shape and comparison count. Finite checks corroborate the
code and examples; the all-modulus statement rests on this written proof.

David Ganz / Dugongue's PR5564 poses the composite-axis continuation. Its
grid construction and exact CRT statements are cited context, not claims
rechecked here. The new step is the explicit all-divisor collision count,
existence test and constructor for this projection interface. No general
literature priority is claimed. Bezout, CRT, Euler/Jordan totients and
projective lines over residue rings are classical. For background see Hans
Havlicek and Metod Saniga, *Projective Ring Line of an Arbitrary Single Qudit*,
[sections 2 through 4](https://www.geometrie.tuwien.ac.at/havlicek/pub/generalqudit.pdf).
Their modular projective geometry and vector layers predate this contribution.
The proof above uses no imported theorem from that paper.

Credit ToikY's guard-safe bands, Jose Manuel's tensor caller, Tekalign's CRT
streams and the retained native/CRT lineage. Nick Petalas's PR6273 concerns
the same permutation on both Fourier indices; its square-unit criterion
addresses a separate contract and is not a source theorem for this count.
