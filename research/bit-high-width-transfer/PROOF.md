# From bounded scalar width to every diagonal endpoint

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
This is a source-composition theorem with an exact finite dependency, not a
proof-kernel verification or a new multiplication construction.

## 1. Model and claim

Let G be torsion-free abelian, let A_1,...,A_k be nonzero elements of G, and
work in M_n(F_2[G]). Each paid factor is

    D_j = I + ([A_j]-1) x_j y_j^T,
    x_j,y_j in F_2^n, y_j^T x_j = 1.

Suppose the whole product equals diag([C_1],...,[C_n]) on arbitrary inputs.
Every diagonal endpoint is permitted; none is designated as disposable. Call
an endpoint *high* if C_i is neither zero nor any of the +/- A_j. Count high
registers with multiplicity, even when their endpoint addresses coincide.

**Inherited width reduction.** Put t = |{i:C_i != 0}|. Then t <= k. After a
coordinate permutation, the same ordered frames admit an exact word on at
most k registers, with all t nonidentity endpoints and some identity endpoints.
Every scalar pairing is preserved. Thus the multiset of high endpoints and
the integral relation lattice are unchanged. This is the image restriction
already present in Nick Petalas's PR #2900, with every nonidentity endpoint
promoted to the active set; its more refined bound is at least as strong.

PR #6760 additionally gives width t+w with w<=floor((k-t)/2). That stronger
comparison is useful but is not needed for the finite cutoff below.

**Five-call consequence.** If k=5 and the frame relation lattice has rank at
most two, every diagonal endpoint, at any finite scalar width, has at most
two high registers. Two are attainable. This consequence uses the complete
W<=5 finite census of Josie Elliston's PR #6055; the new step removes its
scalar-width restriction by image-space restriction, or by PR #6760's
sharper compression. It does not replace that census by
a purely symbolic classification.

## 2. Inherited image restriction, with the endpoint partition explicit

The finitely generated subgroup H=<A_1,...,A_k> is free abelian. Every C_i
belongs to H: a nonzero endpoint coefficient appears in the subset expansion
of the product. Work in the Laurent polynomial domain F_2[H] and its fraction
field K. Permute coordinates to put all nonidentity endpoints first. This
includes any originally named dirty auxiliary output that is nonidentity.
Only exact identity endpoints go in the helper block.

Let S=span_F2(x_1,...,x_k). Every factor preserves S, and the image of P-I
over K is contained in S extended to K, by the ordered rank-one expansion.
For a diagonal monomial endpoint that image is precisely the nonidentity
coordinate space E over K. Binary matrix ranks do not change under field
extension, so E is contained in S already over F2. Write H_0 for the
identity-endpoint coordinate space. Then

    S = E direct_sum (S intersect H_0).

Subtracting a vector's E component leaves its H_0 component still in S.
Choose a binary basis matrix B for S beginning with the active coordinate
vectors and continuing with a basis of S intersect H_0. Let Q be any binary
left inverse of B. Since every x_j belongs to S, BQx_j=x_j. Set

    x'_j = Qx_j,     y_j'^T = y_j^T B.

Then y_j'^T x'_j=1, D_j B=B D'_j, and induction gives P B=B product D'_j.
The endpoint in this chosen basis is exactly

    diag([C_i]: C_i != 0, I_(dim S-t)).

Every factor remains a legal binary rank-one idempotent, every pairing is
preserved because y_i^T BQx_j=y_i^T x_j, and the width is dim S<=k. The active
parts of both scalar vectors are unchanged because the extra basis vectors
are helper-only. The t=0 case is allowed. For k>0, S is nonzero because every
self-pairing equals one. This is a formal-word existence result, not a claim
that arbitrary physical scalar changes of basis are uncharged.

This proof restates the active/dirty-adapted image restriction of PR #2900,
which builds on Tuafo's identical-target image argument and PR #468's model.
That source proves the sharper dim S<=k-d+q<=k-d+s using first-order
augmentation, where d is paid-frame span, s is target-frame span, and q is
the binary span of the target classes in the actual generated lattice.
We only need dim S<=k. No novelty is claimed for the width method itself.

All ordered A_j and all nonzero C_i are literally unchanged. Therefore the
integral frame relation lattice, any rational rank-one address realization,
and the predicate C_i not in {0,+/-A_1,...,+/-A_k} are unchanged. Deleted
identity endpoints are never high. In particular, high multiplicities survive.
This is the precise transfer needed for the new arbitrary-width corollary.

For comparison, applying the paired-rank theorem of PR #6760 to the same
partition gives w=rank_F2(V^T U)<=floor((k-t)/2), preserving the same full
endpoint and pairings. This is a second route to width<=k. Its sharper helper
bound is credited to that source and is not a necessary dependency of the
five-call theorem.

More generally, an obstruction depending only on the ordered frame list and
nonidentity endpoint multiset transfers from all widths at most k to arbitrary
width, through this inherited restriction. The present new application is the
high-count census below, not a new general width lemma.

## 3. Applying the exact five-call census

PR #6055 enumerates the formal product in F_2[Z^5/L], for every saturated
frame relation lattice L of rank at most two. Its actual computation is
independent of any embedding as rational matrices: the matrix rank-one
hypothesis enters only when interpreting a high endpoint as a potential
invertible target. We use precisely this formal classification, with binary
rank-one idempotent scalar factors and nonzero A_j.

The source reduction first retains L's cube part: differences of subset
indicators lie in {-1,0,1}^5, so only those relations affect the product.
Saturating their rational span preserves every coefficient fiber in the
multilinear product. A target low in the lifted quotient is low in the
original quotient; therefore the original number of high endpoints is no
greater. The enumeration covers 4,060 rank-two lattices with nonzero frames,
and 117 possibilities of rank at most one. Its derivative restriction and
register-permutation orbits prune words without discarding any diagonal
endpoint. The accepted endpoint must be a whole diagonal monomial matrix.

For each W=2,3,4,5 the exact census returns zero words with at least three
high endpoints. The W=5 row matters here: promotion may give t=5 and no
helpers, so the width-transfer lemma alone does not limit the test to W=4.
An n'=1 word can be padded by an unused identity coordinate and is covered
at W=2. A positive-length word on zero scalar coordinates cannot contain a
rank-one idempotent; no omitted width-zero case exists.

Now compress an arbitrary-width hypothetical five-call diagonal word with
at least three high endpoints. Width transfer gives a word with n'<=5,
the same frames and relation lattice, and the same high endpoints. Padding
if necessary puts it in the W=2,...,5 census, a contradiction. This proves
the five-call consequence, including arbitrary nonidentity auxiliary outputs.

## 4. Sharpness and relation to the rank-two target problem

Let E11,E22,E12 be the usual rational 2-by-2 matrix units. Use coordinate
scalar projectors to apply these five frames:

    register 1: E11, E22
    register 2: E11, E22
    register 3: E12.

The endpoint is diag([I_2],[I_2],[E12]); there are exactly two high registers.
All five frames have rational rank one, the frame span is three and the
relation rank is two. Unused dirty coordinates can be appended, and remain
exactly identity. Thus the universal bound of two is attained even with a
genuine rational rank-one realization. Equal high addresses are counted twice.

For three invertible rational 2-by-2 data targets, each is high. At five calls,
span at least three gives relation rank at most two and is excluded here.
Span at most two is excluded by the retained arbitrary-register low-span
lemma. Therefore six calls are necessary and sufficient with arbitrary
diagonal auxiliary outputs. This is a second proof route to JoyboyBrian's
already merged PR #5481, which proved the same rank-two target result by
conic incidence and the inherited three-register theorem. That floor and the
span-four application are not new claims of this package.

## 5. Dependencies and limits

The new inference combines the inherited endpoint-preserving width restriction
with PR #6055's stronger finite high-count census. This application answers the
arbitrary-W extension in PR #6055 Open next question 1 through a finite
dependency. A purely symbolic proof of the at-most-two-high classification
remains open here. The result does not depend on the conic geometry of
PR #5481 or the three-register finite classification used in PR #720.

Torsion-free addresses, nonzero frames, rank-one scalar idempotence, exact
whole diagonal monomial endpoints and arbitrary-input correctness are part
of the contract. A nondiagonal auxiliary block cannot simply be promoted or
discarded under this proof. A zero-initialized-only helper is a different
contract. At six calls three high endpoints are possible, so the five-call
bound is not silently extended. Relation rank greater than two is not covered
by the finite consequence. Larger scalar fields require their own finite base.

No native routing, scalar-mixing price, physical cleanup tariff, recursive
invoice, supplier admission, complete multiplication theorem or new kappa is
claimed. All five selected framework assumptions remain.

Credit Nick Petalas and Tuafo for the inherited image-restriction method;
Josie Elliston and Claude for PR #6055's census and cube-lattice
reduction; @CubeJerry and OpenAI Codex for PR #6760's exact helper compression;
JoyboyBrian and OpenAI Codex for PR #5481's prior floor; and Ali Romman,
eumemic, waynenilsen, David Govea, unpaidmoon, Hanson Sun, woklerx and huxint
for the retained model, factorization, arbitrary-register and pattern lineage.
