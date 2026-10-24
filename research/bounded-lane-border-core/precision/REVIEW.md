# Independent review: bounded graded exact-grid closure

Scope: a conditional sufficient lemma and a counterexample to a weaker
endpoint-only hypothesis. This is not a certificate for the actual two-full
source, a paid-profile improvement, or a multiplication theorem.

## Sufficient hypothesis and height

For a dyadic Gaussian matrix M, use

    h(M) = max(denominator exponent of M, log2(max(1, ||M||_infinity))).

Use the induced row-sum norm over every live role/field, not entrywise maximum.
Then h(AB) <= h(A)+h(B), and a sum of q matrices has height at most
max(h(M_i))+log2(q). One should not define height as the sum of the denominator
and norm heights: their maxima can occur in different summands.

Fix N >= 2, an interface grade set {0,...,H}, and a finite recursive template.
The rank-e node invokes at most P completed rank-f children, f=floor(e/N).
Assume the COMPLETED endpoint admits a finite exact expansion by homogeneous
child factors such that every monomial contributing to output grade l uses
child factors whose positive grades sum to at most l. Coefficient/adaptor maps
have total fixed dyadic height and the number of monomials is uniformly fixed.
The assertion is about an exact identity; cancellation can prove it even when
individual raw gates do not preserve the filtration. It is not enough to know
the support of the returned endpoint.

The completed grade-zero child is exactly the intended Gaussian diagonal, so
C_0(f) <= f. Write E for the fixed coefficient height plus the logarithm of the
number of monomials, and assume finite positive-rank base cases. For l >= 1,

    C_l(e) <= max_{sum j_i <= l} sum_i C_{j_i}(f) + E.

There are at most P zero-grade factors. At most l factors have positive grade.
If C_j(f) <= K j f for positive j, the right side is <= K l f + P f + E.
Choosing K >= (P+E)/(N-1), enlarged to cover the finite base cases, establishes
C_l(e) <= K l e. Zero-rank base operations can instead be treated as part of
the fixed coefficient charge; do not claim C_l(0)=0 without that convention.

The full completed child consequently has height <= K H f + log2(H+1),
apart from the trivial H=0 case which retains the Gaussian bound f. A local
execution prefix contains only finitely many completed children before its
currently active child. Thus its actual intermediate height satisfies

    A(e) <= A(f) + P K' f + E',

for fixed K',E', including all local/raw scalar prefixes. This gives A(e)=O(e).
This step does not require the raw scalar circuit to preserve grades. It does
require bounded scalar coefficients, a fixed instruction count, the actual
same-realization child inverse when used, and an explicit representation of
private fields and their restoration. A small final endpoint alone cannot
bound its intermediate arithmetic.

## One-time dyadic conjugation and exact recovery

Suppose W_e = G_e + sum_{l=1}^H W_{e,l} is the completed map with the proved
height bound ||sum_l W_{e,l}|| <= 2^(K_H e+c_H). Let h_r be the fixed grade of
each interface role and D_delta = diag(delta^h_r). Then

    D_delta W_e D_delta^-1 = G_e + sum_l delta^l W_{e,l}.

Let the input have Gaussian dyadic coordinates on grid 2^-b, norm at most 1,
and let G_e have entries in 2^-e Z[i]. Its exact output lies on grid
2^-(b+e). Choose delta=2^-s with

    s >= b + (K_H+1)e + c_H + 2.

The error is smaller than one quarter of the target mesh, hence separately
rounding real and imaginary coordinates to that mesh recovers G_e x exactly.
Initial scaling D_delta^-1 increases magnitude to at most 2^(H s), while
leaving the incoming common grid 2^-b valid. If every unscaled intermediate
map has height <= A e, execute the entire recursion exactly on the ONE grid
2^-(b+ceil(A e)). Signed numerators need at most

    b + H s + 2 ceil(A e) + O(1) = (H+1)b + O(e)

bits per real coordinate. No child is rounded or re-encoded on return.

At the end, implement D_delta and recovery by integer shift-and-round directly
on each coordinate numerator. There is no need to materialize a much finer
common exact output grid. A bounded input integer-part exponent m adds O(m)
with an H-dependent fixed constant. For mere k-bit approximation, choose
s >= k + K_H e + c_H + 2 instead of using the exact recovery mesh.

These are bit-width statements. They do not themselves price scalar arithmetic,
field storage/movement, a growing rank-N precompiler, private banks, adapter
execution, or tape descriptors. They only support the fixed-template closure
once those interfaces and the global constant H have been established.

## Endpoint-height counterexample

Let U(a)=I+a E_12 on three roles. Let P cyclically permute basis vectors
1->2->3->1, and Q swap vectors 2 and 3. Define

    Phi(A)=Q [A, P A P^-1] Q^-1,
    [A,B]=A B A^-1 B^-1.

Direct multiplication gives Phi(U(a))=U(a^2). The word uses four calls to
A or its actual inverse. Applying Phi twice gives U(a^4), with 16 child calls
and fixed 0/1 free permutations.

Set S_1=U(2), and S_(2f)=Phi(Phi(S_f)). Then

    S_e=U(2^(e^2))  for e=2^d.

Every completed endpoint has identity Gaussian diagonal and only one
off-diagonal edge, so its endpoint support admits height 1. Its coefficient
bitlength is nevertheless e^2+1. In the completed degree-1 output, four
degree-1 child factors occur. The free relabelling resets a higher composed
degree to degree 1. Therefore no compatible graded-expansion hypothesis of
the form above holds. Endpoint acyclicity and a fixed finite template alone
do not establish O(e) guard bits.

The example can also have FULL Gaussian diagonals, not merely identity ones.
Choose a dyadic Gaussian G_1 of order four, e.g.

    G_1 = 1/2 [[1+i,1-i],[1-i,1+i]],  G_e=G_1 tensor-power e.

Define T_e=U(a_e) tensor G_e. Since T_f^4=U(4a_f) tensor I, conjugation by
R_+=diag(1/4,1,1) extracts U(a_f) tensor I in four child calls. The quartic
word therefore costs 64 calls. Conjugation by R_-=diag(-1/4,1,1) instead
extracts U(-a_f) tensor I, which cancels the shear of one further T_f call,
leaving I tensor G_f in five calls. Apply that Gaussian extractor separately
on the two disjoint f-axis halves (ten calls) and append the quartic shear.
This is a fixed rank-2, 74-call template yielding

    T_(2f)=U(a_f^4) tensor G_(2f).

Its grade-zero output is the exact full Gaussian diagonal, its endpoint
support has height 1 at every rank, and its coefficient norm still has
logarithmic growth at least e^2. The template is deliberately inefficient;
it is a counterexample to a sufficiency assertion, not a bound candidate.

## Verification

Run `python3 verify_counterexample.py`. It checks the square/quartic identities
and inverse words for six exact rational values, the shear extraction
conjugations, and the numerator growth through e=64. The general identities,
74-call construction and asymptotic statements above are algebraic proofs;
the finite examples do not substitute for them.

Prepared by an independent Codex subagent for the October 23 continuation.
