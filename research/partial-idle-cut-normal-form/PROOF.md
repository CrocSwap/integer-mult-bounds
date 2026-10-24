# Independent idle factors reduce to a common cut

Prepared for Cinna Davis (1337isnot1337) with substantial OpenAI Codex
assistance. Apache-2.0. The native path is zxv's; query thinning and the
selected joint-helper invoice are Cinna Davis's preceding contributions.

## Statement and scope

Fix any integer p >= 1. Keep the exact scalar bridges, swaps and central
queries of the query-thinned path controller. Its full native stages are
0, 1, 3, ..., 2p-1, 2p. All other stages are paid query shears. An initial
or terminal idle window may contain an arbitrary subset of the retained
stage factors originally available there. This strictly enlarges the
all-or-nothing whole-window family used by the predecessor search.

There are two admitted formal settings: independent commuting Laurent
indeterminates Q,D_s over a field; or the source BIT algebra
F2[(Z/2)^(2p+2)], where Q and all D_s are independent involutive generators.
Require invertible scalar input/output matrices, independent of these
generators, that turn the endpoint into independent monomial jobs.
These boundaries act on the 2p main roles at one port. Native helpers
remain separate arbitrary productive jobs; mixing them into the main
boundary is outside this model. The local paid inventory stays fixed. A main job
with k stage factors has physical rank 1+bk; an idle with k factors costs
rank bk. The complex values are b=8, with 112 ports; BIT uses b=7 and
111 ports. Every idle
factor on a pair costs two jobs, and every retained full call and thin
query remains charged.

**Theorem.** For every such exact scalar-diagonalizable partial-idle word,
there is a vertex c in {0,...,p-1} for which deleting idle factors produces
the ordinary minimal-cut word. This deletion cannot decrease target
moment minus paid moment for any nondecreasing concave rank price f with
f(0)=0. For f(r)=r^t, 0<t<1, each deleted factor strictly improves the
moment. Consequently independent stage-by-stage idle selection cannot
outperform the best ordinary cut at the same p and local inventory.

This is an all-p written proof, with separate finite source/identity
controls. It is not a new kappa, a global controller obstruction, a proof
that the p16 invoice is optimal over every p, or a theorem for arbitrary
geometric quotients that erase or identify native directions.
Changed stage alphabets, topology, native words,
joint non-diagonal output contracts and nonconstant boundaries are outside it.

## 1. The enlarged word and its triangular endpoint

Put j(s)=0 for s=0, j(s)=(s-1)/2 for odd s, and j(2p)=p-1.
Thus vertices 0 and p-1 each have two native factors (three when p=1);
each other vertex has one. Write d_j for the product of the native factors
at vertex j. For each stage s choose a set S_s of vertices containing
j(s). Membership i>j(s) means D_s occurs in vertex i's initial idle;
membership i<j(s) means it occurs in i's terminal idle. These are exactly
the p-1 available windows for that factor. No middle idle survives thinning.

Let I_i be the initial idle product at i and B_i its terminal idle product.
Initial idles occur immediately before a pair is first touched, so they
can be moved to the input of that pair. Just before the final reverse
bridge chain, direct substitution in the source shears gives

    a_j = -Q d_j I_j y_j - d_j a_(j-1),       a_-1=0,
    b_j = Q^-1 (d_j I_j x_j + I_(j+1) x_(j+1)),  j<p-1,
    b_(p-1) = Q^-1 d_(p-1) I_(p-1) x_(p-1).

The two special endpoint native calls are included in d_0 and d_(p-1).
The terminal idles replace (a_j,b_j) by (B_j a_j,B_j b_j).
The reverse bridges and final swaps return

    X'_j = sum_(k=j..p-1) (-1)^(k-j) B_k b_k,
    Y'_j = -(B_j a_j + B_(j-1) a_(j-1)).

Define N by N_(i,i+1)=1 and all other entries zero. Put
L=(I+N)^-1=I-N+N^2-... . The two endpoint blocks are therefore

    A_X = Q^-1 L diag(B) (diag(d)+N) diag(I),
    A_Y = Q (I+N^T) diag(B)
                    (I+diag(d) N^T)^-1 diag(d) diag(I).

There are no mixed X/Y entries. A_X is upper triangular and A_Y lower
triangular. Each has diagonal monomial Q^(-1) or Q times d_i I_i B_i.
All denominators in the second expression are polynomials: the strictly
lower matrix is nilpotent. At Q=D_s=1 the endpoint is the identity.

These formulas follow from the displayed recurrence for every p. The
verifier separately checks the source's literal event sequence and its
Laurent evaluation; it does not infer the recurrence from samples.

## 2. Each individual stage determines a projector

For j in {0,...,p-1}, set

    L_j = product_(i=0..j-1) (I-E_(i,i+1)),
    P_j(S) = L_j diag(1_S) L_j^-1.

L_0=I; L_j is L restricted to the leading j+1 block and identity
elsewhere. Set all factors except D_s=z to one and set Q=1. The endpoint
is exactly

    diag(I+(z-1)P_j(S_s), I+(z-1)P_j(S_s)^T),  j=j(s).

To see this directly, native insertion at j has X projector
L E_jj; an initial idle at i>j has projector E_ii; a terminal idle at
i<j has projector L E_ii (I+N). These are respectively the j, i>j and
i<j coordinate projectors in the L_j basis. They are pairwise orthogonal,
so the product of the chosen insertions is I+(z-1) times their sum.
The Y block is their transpose. This also proves that the single-stage
polynomial is affine despite having up to p chronological occurrences.

Explicitly, with v_i=1_S(i), the only off-diagonal entries of P_j(S) are

    (P_j(S))_(i,k) = (-1)^(k-i) (v_k-v_(k-1)),  i<k<=j,

and its diagonal is v. This formula is also used by the independent checker.

If constant scalar boundaries diagonalize the full multivariate endpoint,
its specialization at Q=1 does so too. Since the all-one endpoint is I,
the two scalar boundaries at that specialization are inverses (constant
nonzero output prefactors may first be absorbed into a boundary).
Comparing coefficients in each one-generator specialization makes its
projectors simultaneously diagonal, and hence pairwise commuting.
This does not use differentiation or four distinct scalar eigenvalues.
In particular, 1 and z remain linearly independent in F2[z]/(z^2-1),
even though that algebra is not semisimple. In the Laurent setting,
affineness forces each target's specialized exponent to be 0 or 1;
in the involutive setting those are the two monomials by definition. We use
only this necessity, and do not assume it is sufficient for arbitrary
partial-idle words.

## 3. Commutation is intersection of intervals

For S containing j, let C_j(S)=[l_j,r_j] be the maximal consecutive
interval in S containing j. For any j<=k,

    [P_j(S),P_k(T)]=0  iff  C_j(S) intersects C_k(T).

For j=k the projectors are diagonal in the same basis and their intervals
both contain j. For j<k, conjugate by L_j. The change of basis
L_j^-1 L_k equals (I+N)^-1 restricted to indices j,...,k, with identity
outside that block. In that block its conjugation of diag(1_T) has entry

    (-1)^(b-a) (1_T(b)-1_T(b-1)),  j<=a<b<=k.

It commutes with diag(1_S) exactly when, at every transition of T at b,
S is constant on [j,b]. Because j is in S and k is in T, this is
equivalent to r_j>=l_k: the initial all-one run of S must meet the final
all-one run of T. This is exactly intersection of their core intervals.
Disconnected extra members of S or T do not change that condition. The
nonzero entries in this argument are +1 or -1 and their signs; no division
by two occurs. Thus the criterion also holds in characteristic two.

Thus exact diagonalizability forces all the core intervals to intersect
pairwise. Finite intervals on a line have a common point: their maximum
left endpoint is at most their minimum right endpoint. Choose any integer
c in this intersection. For every s,

    [min(j(s),c),max(j(s),c)] is contained in S_s.

This supplies one common cut for every stage, including duplicate endpoint
stages. It is not a sampling or bounded-p assertion.

## 4. The reduced word is a valid exact controller

Delete every membership outside the displayed minimal segment. Then

    I_i = product_(j<i) d_j, B_i=1                  for i<c,
    I_c = product_(j<c) d_j, B_c=product_(j>c) d_j,
    I_i = 1, B_i=product_(j>i) d_j                 for i>c.

The diagonal stage products are prefixes through i when i<c, the full
product when i=c, and suffixes from i when i>c. Call them g_i.
Substitution in Section 1, or its adjacent-entry recurrence, gives

    A_X = Q^-1 L_c diag(g) L_c^-1,
    A_Y = Q L_c^-T diag(g) L_c^T.

The scalar boundaries L_c and its inverse/transposes therefore give
independent exact monomial targets. This is the ordinary minimal-cut
word, with each initial window below c and each terminal window above c
retained, and the same native/query stages as the source construction.

For completeness, target degrees cannot be reallocated to earn more
credit, including in the nonsemisimple binary group algebra. For each
zero/one signature sigma across stages, form the product of P_s or I-P_s
according to sigma. The factors commute. Its rank is the number of target
jobs with that signature in any simultaneous constant diagonalization.
The same product in the displayed triangular bases is an idempotent;
its rank is the number of diagonal ones. Those diagonals are exactly the
memberships i in S_s, in each of the X and Y blocks. Thus the full
signature multiset, with multiplicities, is fixed, rather than only its
first moments. This rank argument is over the coefficient field and does
not assume that the group algebra itself is semisimple.

Specializing every D_s to 1 leaves diag(Q^-1 I,Q I) in the Laurent case
and Q I in the involutive case. Consequently each target has exactly one
central rank-one factor under the stated monomial-job contract. Main rank
credit is therefore exactly the native-plus-initial-plus-terminal count
at each vertex, twice per port. Source BIT specialization is checked
against the actual retained group-ring emitter; this is not a new
physical scalar-extension or ordinary-BIT admission theorem.

## 5. Deletion improves every concave moment

At vertex i let n_i be its fixed number of native factors, a_i the number
of initial idle factors, and b_i the terminal count. Its target rank is

    R_i = 1 + b(n_i+a_i+b_i).

Its two idle ranks are b a_i and b b_i, with the same two-field/port
multiplicity as the target. The local helpers, native paid calls and thin
queries are fixed. Deleting one initial factor changes target R to R-b
and paid r=b a_i to r-b. The change in target-minus-paid moment is

    [f(r)-f(r-b)] - [f(R)-f(R-b)] >= 0,

because R>r and concave increments decrease with their starting point.
The terminal case is identical. Zero-rank idles disappear using f(0)=0.
For r^t with 0<t<1 the inequality is strict. Repeating the deletion reaches
the exact minimal-cut word from Section 4 without decreasing the moment.
No helper credit, duplicated output, uncharged query or scalar limit is used.

This proves the theorem. It closes this enlarged idle-selection route;
it supplies no ceiling for a different native word or controller topology.

## 6. The balanced cut dominates all cuts in this thinned pattern

For a cut c, the initial branch length is c and terminal length p-1-c.
All local-helper, native, query and full-interval target terms are independent
of c. The remaining surplus, divided by twice the port count, is

    sum_(j=1..c) Delta_j + sum_(j=1..p-1-c) Delta_j,
    Delta_j = f(1+b(j+1)) - f(b(j+1)).

Concavity makes Delta_j nonincreasing. Moving one unit from the longer
branch to the shorter branch therefore cannot decrease this sum. A balanced
cut c=floor((p-1)/2) is at least as good as every other cut. The result does
not cover a changed native-stage mask, where symmetry can be lost.

Combined with the theorem, at each p the balanced ordinary cut dominates
every exact scalar-diagonalizable independent partial-idle assignment in
the stated family. This statement needs no bound on p or numerical solver.
