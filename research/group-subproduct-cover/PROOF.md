# Ordered subproducts determine the relaxed gate count

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Exact model

Let K be any field and G any group, with identity e. Use the formal group
algebra K[G]. Its basis elements [g] are linearly independent, also when
K has positive characteristic. Matrices act on column vectors on the left.
Products below are in matrix order; the rightmost factor acts first.

A circuit has finitely many registers. Free operations are fixed matrices
with entries in K, tensored with the identity address action [e]. They may
change the register count, be singular, copy inputs, discard registers, or
set registers to zero. They cannot depend on the input data or apply an
address map. A paid gate on R registers is

    D(N,g) = (I_R-N)[e] + N[g],     N in M_R(K), N^2=N.

Each gate costs one, at every rank of N. The allowed group labels form an
explicit set L. This is an optimistic relaxation of a rank-one gate model.
In particular a rank-two projector costs one here, not two.

The required data block is diag([t_1],...,[t_d]). Any extra clean or dirty
workspace is finite. If dirt is present, the data block must be correct for
all dirt, and the chosen upper construction leaves it unchanged. For the
lower bound we even allow arbitrary changes to workspace. Thus a rule that
requires restoration can only make the lower bound stronger.

For a word w=(g_1,...,g_k) in L, define its ordered subproduct set

    S(w) = {g_1^b_1 ... g_k^b_k : b_j in {0,1}}.

This set always contains e. Define c_L(T) as the minimum k for which one
such word has {t_1,...,t_d} contained in S(w). Set it to infinity if there
is no such word. Repeated labels and repeated target entries are allowed.

## 2. The exact cover theorem

**Theorem.** In this model the minimum paid count for the diagonal target
is c_L(T). Extra finite scalar workspace and free scalar maps do not lower
it. A minimum cover has a construction on the data registers alone, with
diagonal projectors and no free operations.

**Lower bound.** Combine consecutive free maps. A circuit with k gates
has a data block of

    C_0 D(N_1,g_1) C_1 ... D(N_k,g_k) C_k,

where the C_j are scalar matrices. Initial embeddings, final selections,
and any zero workspace are included in the endpoint scalar maps. For dirty
workspace, take the columns that correspond to data input. Rectangular C_j
are permitted wherever the register count changes.

Expand each paid factor into its two terms. Each summand is a scalar
matrix times one basis element

    [g_1^b_1 ... g_k^b_k].

Scalar entries commute with all group-algebra entries. Matrix dimensions
and the order of group labels are preserved in this expansion. The support
of every output entry is therefore contained in S(w). Equal products can
cancel, but cancellation cannot add a group label. Each target [t_i] has a
nonzero coefficient on its own diagonal, so t_i must lie in S(w). This
proves k >= c_L(T). Invertibility of the free maps is not needed. The same
argument holds even without the idempotent condition on the paid N_j.

**Upper bound.** For each target position i choose one mask b(i) whose
ordered subproduct is t_i. For paid position j set

    N_j = diag(b(i)_j : 1 <= i <= d).

These are idempotents over every field. On data register i the j-th gate
is [g_j] if b(i)_j=1 and [e] otherwise. The full product is [t_i]. All
cross-register entries vanish. Extend every N_j by zero on any workspace;
then every workspace register is restored without a read, copy or clear.
The construction has exactly k declared gates. A zero projector can be
deleted; if that happens in a shortest cover it contradicts minimality.
This proves equality, including the infinite case.

The expansion is the prior formal subword-support method. The result here
uses the simultaneous target cover and supplies its converse in the stated
arbitrary-rank unit-cost class. It does not assert a new general expansion
identity or literature priority for subset-product methods.

## 3. A sharp three-label decision

Now let L=G without e, and take three distinct nonidentity target labels.
Zero and one gate are impossible. Two gates have support contained in

    {e,g,h,gh}.

Thus two gates are possible exactly when the unordered target triple is
{g,h,gh} for some ordered pair of distinct target members. The three
nonidentity elements must be distinct; g=h or gh=e cannot cover the target.
Conversely the cover theorem realizes this triple in two gates. In target
order (g,h,gh), use

    N_1 = diag(1,0,1),     N_2 = diag(0,1,1).

If there is no such relation, three direct coordinate gates attain the
lower bound. Therefore the exact count is either two or three. This is a
proof for every field and group, not an extrapolation from the tables.

## 4. Sharp projector ranks in a two-call realization

In the two-call case the four labels e,g,h,gh are distinct. Write the data
block as C_0 D(N,g) C_1 D(M,h) C_2. The coefficient matrices satisfy

    A_g + A_gh = C_0 N C_1 C_2,
    A_h + A_gh = C_0 C_1 M C_2.

These follow by adding the two expanded terms and using (I-M)+M=I and
(I-N)+N=I. Rectangular or singular scalar maps do not affect the identities.
For the three-label diagonal endpoint, each left side is a diagonal matrix
with exactly two entries equal to one, up to a data permutation. Its rank
is two over every field. Matrix-rank subadditivity is not needed: the rank
of a product is at most the rank of each factor. Therefore rank N >= 2
and rank M >= 2. The diagonal construction in section 3 attains both bounds.

**Corollary.** Every triple of distinct nonidentity group labels has exact
rank-one gate count three, over every field, with arbitrary finite scalar
workspace and fixed free scalar maps. In the unrestricted alphabet three
direct coordinate gates attain the bound. A shorter word is either excluded
by support or needs rank at least two in each of its two gates. If each gate
is instead charged its projector rank, the exact total rank cost is also
three. Zero-rank gates do nothing; total rank cost below three permits at
most two nonzero gates and cannot implement the target. In a two-call
implementation the total rank cost is at least four, so its smaller call
count is not a saving under rank charging.

This corollary extends both finite predecessor triple minima to arbitrary
scalar workspace. It does not establish rank-one additivity for four or
more target labels, repeated labels, or restricted address alphabets.

## 5. Actual boundaries

In G=C7 semidirect C3, use a^7=b^3=e and bab^-1=a^2. The predecessor target
is (a,a^2,a^4). Products of two distinct members have exponents 3,5,6 modulo
7. None is the remaining member. The exact count is three, over every
field and with all the scalar workspace and paid projectors in section 1.
Its direct gates have rank one. Consequently its old rank-one count three
also survives arbitrary finite scalar workspace and free scalar maps.
This removes those hypotheses as possible two-call escapes for this target.

For Q8, i*j=k. The triple (i,j,k) therefore takes two rank-two gates here.
The rank-cut corollary extends its earlier rank-one minimum three to all
fields and arbitrary finite scalar workspace. The two-call rank-two result
is not a rank-charged saving. In particular the
symbol [-k] is a different group basis element from [k], even in F2[Q8].
Reversing the two gate labels changes the third target to [-k].

With three distinct targets, the theorem can give more than the maximum
individual address word length. In the unrestricted alphabet each separate
nonidentity target has word length one; the order-21 triple still costs
three. The single-target support floor alone does not give this conclusion.

## 6. Faithful action and cost limits

A regular action of K[G] is faithful: apply a group-algebra element to the
basis vector at e to recover its coefficients. For infinite groups use the
space of finitely supported vectors. Thus the proof also applies to exact
regular-action endpoints. A group representation that is faithful on group
elements need not be faithful on their linear combinations.

For the order-21 group, the natural action x -> 2^j*x+i on seven addresses
is faithful as a group action. However,

    sum_(i=0)^6 [a^i] - sum_(i=0)^6 [a^i b]

is a nonzero formal element and acts as zero in that seven-dimensional
permutation representation: each sum acts as the all-ones matrix. The
regular action detects it over every field. A natural matrix check cannot
replace the formal endpoint used by the theorem.

The proved bill is an abstract gate count. Scalar maps are free by an
explicit relaxation; physical source access, scalar maps, high-rank gates,
frame conversion, precision, recursive children, hosting and cleanup are
not priced. The upper construction needs no workspace, but no native
supplier realizes these arbitrary group gates here. No complete kappa
calculation changes. Data-dependent control, free address operations and
unfaithful address representations are outside the theorem.
