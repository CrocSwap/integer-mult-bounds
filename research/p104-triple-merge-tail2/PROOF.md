# A rank-two tail makes a source-retaining triple merge cost at least 22

This is a scoped proof with a finite geometric certificate. The cost is the
sum of paid binary frame-dimension drops. It is not a concave power-tariff
comparison, a physical construction, or a multiplication theorem.

## Model and cited premises

Use the eight fixed carriers of Matarener's
[PR6315](https://github.com/CrocSwap/integer-mult-bounds/pull/6315), on
DreamingOfClouds's PR6030 word. Work in the binary frame space V = F2^9.
The carrier contents t_c are independent rational scalars. Their source
normals g_c and delivery lines l_c are read from the pinned PR6315 receipt.
The selected 104 port vectors p are read from the pinned word.

We use the predecessor's fixed-code decoder support as a premise. At port p,
the required coefficient d_pc of t_c is nonzero exactly when p.l_c = 0.
Its sign and nonzero magnitude will not enter our certificate. The inherited
geometric identity is

    span(g_c, {p : d_pc != 0}) = H_c = l_c^perp,
    dim H_c = 8, and g_a.l_c = 1 for a != c.

Neither the decoder's uniqueness nor the complete source word is reverified
here. PR6315 retains the fragmentation, owned-boundary and carrier-uniqueness
lineage on which these premises depend.

Choose three distinct carriers U = {a,b,c}. Each travels on its own pure
pre-merge information walk, with union subspace Z_i and integer paid rank p_i.
All three meet at dual frame W and form one scalar

    u = lambda_a t_a + lambda_b t_b + lambda_c t_c,

where every lambda_i is a nonzero rational. There is one common tail with
union T and paid rank tau = 2. The cited walk bound supplies

    dim Z_i <= p_i + 1,       dim T <= dim W + 2,
    W <= Z_i intersect T.

We impose the additional hypothesis G = span(g_a,g_b,g_c) <= W.
This is source-normal retention. CubeJerry's
[PR6323](https://github.com/CrocSwap/integer-mult-bounds/pull/6323) explains
why it cannot be inferred from a common frame after arbitrary public relays.
Our theorem assumes it explicitly.

For a deliberately permissive receiver model, port p may use any pure t_i
whose path union contains p, and may use u if p belongs to T. It may combine
these values with arbitrary rational coefficients. It must obtain the fixed
required decoder row on these three independent contents. Other carrier
coordinates can be given for free. There are no additional mixtures involving
these three contents. The model grants access throughout each union, even if
no single chronological node provides that access. Thus a negative result in
this relaxation also excludes any pure single-merge program satisfying these
conditions. Arbitrary feedback, public-dirt cancellation, extra mixtures and
multi-stage merges are outside the model.

## 1. A necessary two-path cover

For two chosen carriers i,j define

    N_ij = {p in P : exactly one of d_pi,d_pj is nonzero}.

If p is outside both Z_i and Z_j, the receiver has neither pure t_i nor pure
t_j. Its only possible access to those two coordinates is a multiple of
(lambda_i,lambda_j) from the tail, or zero if the tail is absent. Both entries
of lambda are nonzero. This cannot have exactly one nonzero entry. Independence
of the carrier scalars therefore requires

    N_ij <= Z_i union Z_j.

This necessary condition holds for every choice of nonzero merge coefficients.
It ignores all receivers whose two demands are both nonzero, making the
exclusion weaker and independent of their signs.

## 2. The new quotient certificate

For every one of the 56 triples, the three source normals are independent,
so dim G = 3. Let q : V -> V/G be the quotient. For each of the three pairs
inside each triple, the verifier enumerates the distinct cosets q(N_ij).
Across the 168 cases their cardinalities are

| Cardinality | Cases |
|---:|---:|
| 39 | 72 |
| 46 | 72 |
| 47 | 24 |

The implementation constructs each coset as the explicit eight-element set
{p+g : g in G}. No predecessor executable or decoder replay is used.

Suppose dim Z_i and dim Z_j are both at most seven. Because they contain G,
their images in the six-dimensional quotient have dimension at most four.
Extend both to four-dimensional subspaces A,B if necessary. Then
dim(A intersect B) >= 2 and

    |A union B| = 16 + 16 - 2^dim(A intersect B) <= 28.

But |q(N_ij)| >= 39. The necessary cover in section 1 is impossible.
Consequently, no two pre-merge unions can both have dimension at most seven.
The finite certificate depends only on the fixed ports, normals and decoder
zero supports, not on the tail geometry or merge coefficient ratios.

## 3. Paid-rank consequence

Receiver coverage and the cited hyperplane identity give H_i <= Z_i+T.
For another chosen index j, source-normal retention gives g_j in W <= Z_i+T.
Since g_j lies outside H_i, we obtain Z_i+T = V. Therefore

    9 + dim W <= dim Z_i + dim T
                <= p_i + 1 + dim W + 2,

so p_i >= 6 for each of the three paths.

If two paths had p_i <= 6, the walk bound would give dimension at most seven
for both unions, contradicting section 2. At least two paths thus have
p_i >= 7. Including the paid tail,

    total = p_a + p_b + p_c + 2 >= 6 + 7 + 7 + 2 = 22.

Separate delivery costs 3*7 = 21 by the cited predecessor. Hence this
source-retaining, full-support, rank-two-tail merge cannot save paid rank.
We do not claim that 22 is attainable or optimal. Rank mass alone does not
order concave recursive moments, so no power-tariff or kappa exclusion follows.

## Verification boundary

The universal lower bound follows from the argument above plus the finite
168-case certificate. The verifier also enumerates all 651 four-spaces of
F2^6 through their annihilators and all 423801 ordered pairs, corroborating
the sharp abstract cover bound 28. Explicit quotient fixtures, invalid-input
controls and integer-cost boundary checks run in normal and optimized Python.
These controls concern this new certificate. They do not audit PR6315,
PR6323, the selected native word, or the full supplier.

The result was produced by Nick Petalas. Apache-2.0.
