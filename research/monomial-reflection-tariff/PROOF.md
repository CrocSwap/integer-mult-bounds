# A full monomial reflection alphabet has an additive register tariff

## Exact model

Let K be a field with an element zeta of exact finite order m, and let n>=1.
Write G=G(m,1,n) for the monomial matrices with nonzero entries in <zeta>.
The notation also covers m=1. Encode an element g=(p,a) by

    g e_j = zeta^(a_j) e_(p(j)),     a_j in Z/mZ.

Let b(g) count the cycles C of p for which sum_(j in C) a_j=0 mod m.
These are the balanced cycles, including balanced fixed coordinates.
The ordinary reflection-length formula n-b(g) is classical; see
[Jian-yi Shi](https://www.sciencedirect.com/science/article/pii/S0021869307003882) and
[Briana Foster-Greenwood, Section 3](https://arxiv.org/html/1202.0266v1#S3). Section 2 gives
its elementary construction here, so no external classification is needed.

Use the full formal group algebra K[G], with R>=W finite register roles.
All inputs are arbitrary. Free scalar operations are GL_R(K) matrices.
A paid unit operation is

    D_N(t) = I + ([t]-[e]) N,
    rank_K(N)=1, N^2=N, rank_K(t-I)=1, t in G.

The address alphabet is every monomial reflection, not just adjacent swaps.
It consists exactly of:

- a phase multiplication zeta^a on one coordinate, a!=0 mod m;
- a swap of coordinates i,j with phases zeta^a,zeta^(-a).

Indeed, Section 1 shows that displacement rank one allows either one
unbalanced singleton, or one balanced two-cycle, with every other coordinate
balanced and fixed. Phase operations may have order greater than two.
The inverse of each operation is in the same paid alphabet. Idempotence
also gives D_N(t)^(-1)=D_N(t^(-1)), so all paid factors are invertible.

The required complete endpoint is

    F = diag([g_1],...,[g_W],[e],...,[e]) in M_R(K[G]).

Every spectator is restored, and every off-diagonal entry vanishes. Scalar
preparation and restoration are free only in this explicit optimistic model.
Every address operation, including undoing one, is counted. No address map,
reset, erasure, or clean state is free.

**Theorem.** The minimum paid-call count is

    sum_(j=1)^W (n-b(g_j)),

for every finite number of arbitrary restored dirty spectators. Identity
and empty target lists are allowed. A common positive unit price multiplies
the formula. This is a scoped formal-algebra theorem, not a native supplier.

## 1. Displacement rank and the lower bound

On a permutation cycle, a fixed vector satisfies

    x_(p(j)) = zeta^(a_j) x_j.

After one circuit this gives x_j=zeta^(sum a) x_j. The fixed space on that
cycle has dimension one exactly when the cycle is balanced, and zero
otherwise. Distinct cycles use independent coordinates. Hence

    rank_K(g-I)=n-b(g).

This proof also covers characteristic two when the stated roots exist.
No real ordering, semisimplicity, or division by |G| is used.

We use the augmentation normalization and displacement-rank method of
Gareth Davidson's PR1333. They are prior methods, not new principles here.
Augmentation sends every [g] to 1 and every D_N(t) to I. It sends F to I.
Move every scalar basis change to the right of the chronological product.
Conjugation only replaces N by B N B^(-1), still a rank-one idempotent.
The remaining scalar product is I by augmentation. Therefore the endpoint
has a normalized factorization entirely into paid factors of the same count.

Apply the natural monomial representation to the group algebra. A normalized
paid factor becomes

    I + N tensor (t-I).

Its difference from I has rank exactly one, by the rank formula for a
Kronecker product. For invertible A,B, the elementary identity

    AB-I = A(B-I)+(A-I)

gives rank(AB-I)<=rank(A-I)+rank(B-I). The represented diagonal endpoint
has displacement rank sum_j rank(g_j-I), since its blocks are independent
and its spectators have zero displacement. Iterating the inequality proves
the claimed lower bound for every R. Scalar mixing and dirty helpers do not
remove any term from it.

The natural representation is only a necessary lower-bound image. Equality
in that image is never used to certify a formal endpoint. For example, when
m=3,n=2 over C, the nonzero group-algebra norm sum_(g in G)[g] maps to zero:
for each possible nonzero matrix position its three phases sum to zero.
An off-diagonal norm leak is still a dirty leak in the formal model.

## 2. An attaining cycle splitter

Use composition g h = g after h. Start with a cycle containing i and
j=p(i), with j!=i. Right multiply by the weighted swap t defined by

    t e_i = zeta^(a_i) e_j,
    t e_j = zeta^(-a_i) e_i.

Then

    (g t)e_j = e_j,
    (g t)e_i = zeta^(a_i+a_j) e_(p(j)).

Thus j becomes a balanced singleton and the old cycle loses one coordinate,
while its total phase is unchanged. Repeating on an original cycle of length
ell takes ell-1 weighted swaps and leaves one singleton carrying that cycle's
phase. A balanced cycle is now fully fixed. An unbalanced cycle needs exactly
one diagonal phase operation, its inverse phase, to reach the identity.
The number of right peels is ell-1 or ell respectively, hence n-b(g) in total.

If g t_1 ... t_L=e, then

    g=t_L^(-1) ... t_1^(-1).

Execute t_1^(-1),...,t_L^(-1) chronologically on one coordinate register.
The full formal product is [g]. This uses no scalar mixing or spectator.
For several targets, concatenate their independent coordinate-register
words. The full endpoint is F in K[G], with exactly the lower-bound bill.
This proves simultaneous attainment and the theorem.

## 3. First new example and interpretation

Take m=3,n=2 and g e_0=zeta e_1, g e_1=e_0. Its only cycle is unbalanced,
so it costs two paid reflections. The two-register endpoint diag([g],[g^-1])
costs exactly four with any finite restored dirty workspace. The splitter
uses one phase-weighted swap and one phase operation per target. The inverse
phase operations are paid units too. This is an address alphabet absent from
the simple-reflection Coxeter model, and its scalar field contains a genuine
third root of unity.

Allowing all nonadjacent phase-weighted swaps and higher-order phases does
not create a sharing saving under this unit-reflection invoice. A productive
escape must change a further hypothesis, for example give selected higher-rank
operations a concave price, or supply a different free-operation boundary.
This conclusion does not exclude those changed models.

## 4. Proof and certificate boundaries

The all-parameter conclusion is the written argument above. The finite
verifier independently enumerates small groups, runs an unpruned Cayley
search, computes displacement ranks, and checks the new splitter's words.
Its complete rational group-algebra fixtures mix a dirty spectator through
oblique projectors, check all off-diagonal entries, and run the literal
inverse. They do not enumerate all register circuits; the lower-bound proof
covers those.

No native address implementation, scalar/routing/storage cost, child-rank
moment, compiler/hosting admission, precision/tape bound, new kappa, or
complete multiplication theorem is supplied. Independent human and formal
proof-kernel review are unclaimed. The selected frontier and its five
framework assumptions are unchanged.
