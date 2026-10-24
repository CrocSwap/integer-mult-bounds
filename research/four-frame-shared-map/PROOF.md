# Four graph-frame images: criterion, construction and multiplicity

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This derives a scoped shared-map contract from classical similarity and
finite-length module algebra. It claims no literature priority for that algebra.
The universal argument below is a written proof, not a proof-kernel certificate.

## Exact domain and normalization over every field

Let F be any field. Let U=A direct-sum B with dim A=dim B=r, and let C,D
be r-dimensional subspaces of U. Require C to meet A and B trivially, and
require D to meet B trivially. D may meet A or C, so singular and nonsemisimple
relative operators are included. All four subspaces must lie in U. For an
ambient space V=U direct-sum E, fix dim E=s but impose no frame inside E.
The ordered target quadruple has the same domain and dimensions, with primes.
This is not a classification of unrestricted four-subspace systems.

Choose bases in A,B. Projection onto A gives

```
C = {(x,Lx): x in F^r},   D = {(x,Mx): x in F^r},   L invertible.
```

Similarly obtain L',M' for the target, and put T=L^-1 M, T'=L'^-1 M'.
The normal coordinate quadruple is (A,B,graph(I),graph(T)); normalization is
the B-coordinate change y -> L^-1 y. All matrices here act on column vectors.
Bases and graph matrices are recovered by ordinary elimination, not a search.

**Theorem.** There exists an invertible common map carrying each ordered source
frame to its target if and only if T and T' are similar. Given an invertible
intertwiner S with S T=T' S, its active block matrix is

```
G_active = diag(S,Q),  Q=L' S L^-1.
```

Proof: the first two frame contracts force an active map to be block diagonal
diag(S,Q), with both blocks invertible. Mapping graph(L) to graph(L') forces
Q L=L' S. Mapping graph(M) to graph(M') forces Q M=M' S. Substitution gives
S L^-1 M=L'^-1 M' S, exactly S T=T' S. Conversely this equation and the
displayed Q give both graph contracts, hence all four images. Undo the chosen
source and target bases to get the map in the original coordinates.

For r=0 the unique active map is the empty identity. No assumption about
invertibility of M, T, T-I or their target counterparts was used.

## A finite constructive all-field criterion

View F^r as an F[t]-module with t acting by T. Its presentation is the cokernel
of tI-T. Compute Smith normal form over the Euclidean domain F[t]:

```
P(t) (tI-T) Q(t) = diag(d_1,...,d_r),
```

with P,Q unimodular, and monic d_i ordered by divisibility; unit d_i contribute
zero modules. The nonunit invariant factors determine similarity over every
field. This uses polynomial gcd/division and field operations; no splitting
field, eigenbasis or factorization into linear factors is required. The usual
effective-field interpretation supplies equality and arithmetic operations.

For completeness, the construction specifies the cyclic vectors, rather than
merely naming a normal form. The presentation map sends a polynomial vector
sum_k t^k v_k to sum_k T^k v_k. Multiplication by P gives the isomorphism from
the original cokernel to the diagonal cokernel. For each nonunit d_i, take
the polynomial vector P^-1 e_i and apply that presentation map to obtain v_i.
The vectors

```
v_i, T v_i, ..., T^(deg(d_i)-1) v_i
```

over all nonunit factors form a basis B. In this basis T is the direct sum
of the companion matrices of the d_i. This follows directly from the basis
1,t,...,t^(deg(d_i)-1) of F[t]/(d_i). Apply the same steps to T'. If the
ordered invariant factors differ no module isomorphism exists. If they agree,
their common companion matrix R satisfies T B=B R and T' B'=B' R, so
S=B' B^-1 is an explicit invertible intertwiner in the required direction.

Smith normal form and the structure theorem for finitely generated torsion
modules over a PID are classical background. This proof uses them as exact
algebraic theorems. The bounded reference in core.py uses a different finite
algorithm: prime-field primary partitions plus elimination of S T=T' S and
at most 4096 coefficient tuples. That finite enumeration is not asserted to
implement the preceding algorithm on arbitrary infinite fields.

## Exact finite-field active count, including nonsemisimple cases

Now let F=F_q for any finite field, including nonprime q. If compatibility
fails the count is zero. Otherwise, after fixing one intertwiner S0, all
intertwiners are S0 Z for Z in C_GL_r(F_q)(T), so it suffices to count units
of End_(F_q[t])(F_q^r).

Write the primary module for a monic irreducible p of degree d as

```
M_p = direct-sum_a F_q[t]/(p^(lambda_a)).
```

Let m_j be the number of parts lambda_a equal to j, and let h_l be the number
of parts at least l. A homomorphism from a length-a cyclic summand to a
length-b summand is multiplication by an element annihilated by p^a, hence
has F_q-dimension d min(a,b). Thus the endomorphism algebra E_p has dimension

```
e_p = d sum_(a,b) min(lambda_a,lambda_b) = d sum_l h_l^2.
```

Put k=F_q[t]/(p). Reduce each block between summands of the same length j
modulo p, and discard blocks between different lengths. This gives a surjective
ring homomorphism

```
pi: E_p -> product_j M_(m_j)(k).
```

Indeed, a path from length a through a different length b back to a contains
a factor divisible by p: the step towards the longer summand contributes
p^|a-b|. Therefore off-length terms disappear modulo p in the same-length
diagonal block of a product. Arbitrary quotient matrices lift entrywise in
each isotypic block, proving surjectivity.

Here is an explicit nilpotence argument for J=ker(pi), so no diagonalizability
assumption is hidden in counting units. Let m be the largest primary length.
A block from length a to length b is represented by a multiplier divisible
by p^max(b-a,0). A factor in J between equal lengths has one further p.
In any length path through l factors of J, let A be the total increase of
length and let E be the number of equal-length steps. Its multiplier is
divisible by p^(A+E). The number of increasing steps is at most A, and the
number of decreasing steps is at most A+m-1, since total decrease cannot
exceed total increase plus the initial length minus one. Consequently
l <= 2A+E+m-1. If l=3m, then A+E>=m. Every such product vanishes in its
target summand, whose length is at most m. Expanding a block product as a
sum of these paths shows J^(3m)=0.

An element is a unit exactly when its image under pi is a unit. Necessity is
immediate. For sufficiency, lift a quotient inverse. The resulting products
are 1 modulo J and are invertible by the finite geometric series for a
nilpotent ideal; this supplies both a left and right inverse. Each quotient
fiber has |J|=q^[e_p-d sum_j m_j^2] elements. Hence

```
|C_GL(T)| = product_p q^[d*(sum_l h_l^2 - sum_j m_j^2)]
                         * product_j |GL_(m_j)(F_(q^d))|,
|GL_b(F_Q)| = product_(i=0)^(b-1) (Q^b-Q^i),   |GL_0|=1.
```

There are no cross-primary homomorphisms: coprimality of powers of different
irreducibles and Bezout's identity force such a map to vanish. Thus the algebra
and its unit count split over p. The argument includes p=t, repeated cyclic
blocks, and mixed primary components.

For binary dimension three the counts for 0, J3(0), J2(0)+J1(0), and an
irreducible cubic are respectively 168, 4, 8, and 7. In dimension four, for
p=t^2+t+1, companion(p^2) has count 12 whereas companion(p)+companion(p)
has count 180, despite identical characteristic polynomials.

## Retained unused ambient complement

Every realizing G preserves the active sum U setwise relative to U'. In
chosen decompositions U+E and U'+E', all and only the extensions are

```
G = [[G_active, K], [0,H]],  K arbitrary of size (2r) by s, H invertible.
```

The frame contracts impose nothing on K,H; triangularity makes invertibility
equivalent to that of G_active and H. Therefore the exact finite-field count
is the active count multiplied by q^(2rs)|GL_s(F_q)|. This is algebraic map
freedom, not a free physical operation, erasure or unpriced restored register.

## Incidence data fail to decide this domain

Over F2 take companions of t^3+t+1 and t^3+t^2+1. These cubics are distinct
irreducibles: neither has a binary root, which suffices for degree three.
For each T, both T and T-I are invertible. Thus A,B,graph(I),graph(T) are
pairwise complementary r=3 frames. Every nonempty intersection has dimension
3 for a singleton and zero otherwise; every sum has dimension 3 for a
singleton and 6 otherwise. All incidence dimension data therefore agree,
but characteristic polynomials differ, so no common ordered map exists.
Embedding the active six-space with an unused three-space gives a literal
nine-dimensional example. Its compatible self-case has exactly
7 * 2^18 * 168 = 308281344 completions.

A stronger nonsemisimple control uses companion(p^2) and two companion(p)
blocks for p=t^2+t+1. Both give pairwise complementary graph quadruples and
the same characteristic polynomial, but their primary partitions are (2)
and (1,1), so they are incompatible. Thus even incidence data supplemented
by characteristic polynomial cannot replace invariant factors.

## Application boundary

This settles the complementary-graph first case of Open next question 2 in
Nick Petalas's three-frame shared-map package (#4919), retaining its distinct
three-frame scope. Cao Yifan's pinned helper_line_milp.py and constrained_map.py
motivate a shared G but are authenticated as context, not executed or audited.
No actual emitted operator with four independent graph-frame contracts has
been established. Symplectic constraints, individual vector actions, absolute
phase, a complete native word, owners, restoration, precision, tape prices,
supplier admission and any kappa improvement remain separate obligations.
