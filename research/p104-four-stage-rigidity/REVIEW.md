# Independent adversarial review of D's four-stage note

Worker B, prepared for @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. Source-aware AI review, not blind, human or proof-kernel review.

Reviewed `workers/d/FOUR-STAGE-NOTE.md`, including the new extreme-site
equality and all-even attainment sections, plus retained `SOURCE6717_PROOF.md`
and the literal source `SOURCE6398_ROOT.json`. No D file was edited.

**Finding: no mathematical gap found under the stated contract.** The coupled
normal form and forced odd projector are retained source dependencies. I
checked the new rank inequalities, joint sectors, all noncommuting block
orders, rectangular zero-product step and the all-even embedding argument.

## Pair inequalities and aggregation

For the zero-paired closures A,C, each dimension is 2q. Commutation with
P_i=E_i+F_i bounds the ranks of the leakage maps by rank(F_i)=e_i.
Their supported subspaces have dimensions at least 2q-e_i and zero pairing;
the source row/image inequality gives rank(Q)>=4q-2e_i. If the numerical
bound is negative it is merely weak, not invalid.

For a far endpoint rank(Q)=2q+f, e_i,f>=0 and 2e_i+f>=2q imply e_i+f>=q.
Equality requires e_i=q and f=0. For e_i<q the lower bound on f gives a
strictly larger sum; for e_i>q the sum already exceeds q. Applying the
closure in both orders for two odd sites gives the stated pair inequalities
and rank sum at least 16q/3. The closure formulas agree with SOURCE6717's
canonical prefix, where a_i starts at +1.

An even interior costs 4q and the other three stages cost 7q by the retained
theorem. Without an even interior, the possible distributions of four stages
have the stated pairings. In the two-odd/two-endpoint case j>=3 and i<=n-3
ensure both crossed endpoint pairs are far. Thus the aggregate 10q bound
and the equality ranks (2q,3q,3q,2q) at the four extreme sites follow.

## Equality sectors at arbitrary even n

The forced E_1 supports query 0 and E_(n-1) supports query n. Commuting
intersection projectors AB and CD therefore support the endpoint square-zero
queries. Their rank floors 2q, together with ranks A=D=2q, give A<=B and D<=C.

The union B-or-D supports queries 0,1,n. Their U and V spaces each have
dimension 3q, and their principal skew-sign Gram has rank 2q. Its rank is
therefore at least 4q. Since ranks B+D=5q, rank(BD)<=q. The cross endpoint
Gram has rank q and factors through AD, so AD<=BD and rank(AD)>=q force
AD=BD with rank q. The symmetric union A-or-C yields AD=AC. These are
equalities of commuting projectors, since containment plus equal rank suffices.

Joint diagonalization leaves exactly the empty sector and
AB, CD, BC, B-only, C-only, ABCD. In particular ABC and BCD sectors vanish;
this is stronger than the n=4 three-union observation. Write z=dim(BC).
The endpoint ranks make ABCD,AB,CD each q-dimensional. Each single B/C
sector has dimension q-z, so 0<=z<=q.

## Ordered block normalization and the rectangular contradiction

Let W=ABCD, X=AB and Z=CD. Endpoint pairings make all W endpoint blocks
invertible. A coordinate basis in W sets U_A,W=I; V_D,W=I follows from
V_D U_A=I. Set U_D,W=M; V_A U_D=-I forces V_A,W=-M^-1. Square-zero at A
gives V_A,X U_A,X=M^-1, so both X blocks are invertible. An X basis makes
U_A,X=I and V_A,X=M^-1. Similarly a Z basis gives U_D,Z=I, V_D,Z=-M.
No independent query gauge or block commutation is needed.

I checked the forced B/C blocks in the exact written order:

    U_B,W=I,        U_B,X=I-M,
    V_B,W=-M^-1,    V_B,X=I+M^-1,
    U_C,W=M,        U_C,Z=I-M^-1,
    V_C,W=I,        V_C,Z=-I-M.

For H_B=BC plus B-only and H_C=BC plus C-only, both of dimension q,
square-zero gives

    V_B,H_B U_B,H_B=M,      V_C,H_C U_C,H_C=-M^-1.

All four factors are square and invertible. The restriction V_B,BC from
the z-dimensional common sector is injective; the projection U_C,BC onto
that sector is surjective. Their composition has rank z. The cross Gram
equation V_B U_C=-I already receives -I from W and no X/Z/single-sector
contribution. It therefore requires V_B,BC U_C,BC=0 and forces z=0.
This rectangular argument is valid; it does not incorrectly infer that a
product of arbitrary rectangular nonzero matrices must be nonzero.

Thus the active sectors are q copies each of ABCD,AB,CD,B,C, with (n-5)q
empty coordinates. At n=4 this exceeds the ambient dimension, proving
equality impossible. The only cancellations used M and its own inverse.
The result does not assume unrelated internal q-by-q blocks commute.

## All-even attainment

The displayed S_n has n columns: four selected query images and n-4
difference vectors k_j. Eliminating coordinates 0,1,n-1 leaves the final
query column with entries (-1,+1,...,-1) on 2,...,n-2, whose ordinary sum is
-1. The differences form the full integer sum-zero lattice on those
coordinates. Thus S_n is unimodular, not merely rationally invertible.
Every selected V row is constant on the middle coordinates and annihilates
each difference. The first four columns carry the same skew-sign Gram as
at n=6; all other query blocks at the selected sites are zero. Therefore
the source six-dimensional stages embed by the stated direct sum and
conjugation, without assumptions on the unselected query sites.

The actual selected prefixes depend only on selected queries:
B_0=I-2R_0, B_1=(I-2R_1)(I-2R_0), B_(n-1)=-I-2R_n and B_n=-I.
The penultimate identity follows by inverting I-2R_n with I+2R_n.
Consequently prefix compatibility really transfers; it is not inferred from
compatibility with only the local query. Newly added coordinates see scalar
prefixes, so direct-summing zero stages is safe.

For the formal endpoint, at central character +1 all queries are identity.
At character -1, each full stage commutes with its complete chronological
prefix, allowing the standard conjugated-prefix factorization; the result
is minus the commuting stage product. The two central characters determine
the formal expression because 2 is invertible. Thus the claimed masks
ABCD,AB,CD,1,C,B plus n-6 empty masks follow.

I inspected the exact source JSON: input basis, output basis and all four
source projectors have integer entries. The stored input/output bases are
mutual inverses in the source check, so there is no hidden denominator at
an odd characteristic. Together with S_n unimodular this supports the
claimed characteristic-not-two scope. Tensoring proves attainment at every
q; the arbitrary-coupled lower bound was checked separately above.

## Minor exposition suggestions and boundaries

Specify a_i starts at +1 in the short note; its sign is opposite the final
query column U_n. Replace 'alternating sum of entries -1' in the S_n argument
with 'sum of its alternating entries is -1' to avoid suggesting a second
alternating weight. Both are wording points, not mathematical objections.

The n=4 integer conclusion is total at least 10q+1, not a uniform 11q
bound. The note correctly preserves that distinction. No native supplier,
physical cost, analytic transfer or improved kappa follows from the rank
and incidence results alone. This review did not independently replay all
inherited source packages or establish human/formal acceptance.

## Final lead review

The lead independently checked the final proof, SHA256 952c25f3f7e211887f2bfb98d426dc8f3510d291e84ea6e9668511a06a99bf3f, including the explicit alternating-vector sign and unit minors, the 21q/2 and 32q/3 placement bounds, and the all-even embedding. The 21q/2 linear combination gives a+b+c+3f/4 >= 5q/2; nonnegative f supplies the stated total. The ordered normalization uses only M and its own inverse, not commutation of unrelated blocks. No gap was found. The source-manifest filename was changed during packaging; no proof or retained-source bytes changed. This remains source-aware AI review.
