# Operator-valued paid control: explicit one-child word and a scoped stop

Local read/derive gate, 2026-10-23. No enumeration, solver, source evaluator,
native replay, emitter, compiler, Lean or public post was run. Source pins
and predecessor hashes are in INPUTS.json. This does not alter #5160 or any
previous frozen packet. Substantial OpenAI Codex assistance; no independent
human or formal-kernel acceptance is claimed.

## Decision

The explicit one-H1 operator-valued shear below is invertible, source-bound
and phase-correct at every width. Its first three controls coincide. The
direct fourth-control decoder costs too much: the complete additional
control price is 228 H1, against the conditional 44-H1 raw allowance before
finite work and compiler reserve.

A new scoped obstruction stops attempts to make that fourth control FREE
using arbitrary translation-valued gathers, scatters, bypasses and active
feedback around commuting X-Gaussian children: an invertible t0 then needs
at least 112 paid unary children. This includes genuine operator-valued
owner maps and the predecessor counterexample to scalar coefficient rank.
The proof uses a chronological free-input kernel, not coefficient rank.

This is NOT an obstruction for arbitrary monomial gathers, noncommuting
paid children, or an affordably PAID fourth control. No within-budget
construction for that broader class is supplied. The gate closes with
those explicit reopening conditions.

## Exact source and endpoint

Keep the 112-owner physical source at
4c0a359d88f22f05189d51f48387750b801a45d4, the 17 axes q+U+W, and

    C_s[i,j] = A[i,j] K_(s,i)^-1 K_(s,j).

The source A is invertible, has zero diagonal and 52 nonzeros per row and
column. The 112 directions q_i=G_i e_q are distinct. G_i are the actual
orthogonal binary normalizer matrices, read as rows, with their signed K_i
words retained. Each word is lifted columnwise; owner coefficients are
applied once. The four controls and exact ordered inverse formulas remain

    T=t0; S0=Q^-1 T Q; t=D3 T D3^-1;
    E=Q^-1 C3 t C1 Q^-1,
    E^-1=Q C1^-1 t^-1 C3^-1 Q.

The released identity is

    F3 J(T) F1 = [[0,t],[-E,0]] diag(G,G),
    J(T)=[[-T C1,T Q],[0,-C3 S0]], G=D1 D3 Q.

The monitor confirmed #5126 already allows operator-valued monomial
gathers, active feedback and free recodings for its named fresh-input
J, QP, PQ, Q U_mode and V_mode Q endpoints. Its 112-call theorem is not
automatically a theorem about arbitrary T. Dillon's chronological native
helper/centre lane remains excluded. The monitor found no matching current
claim on this bounded fresh four-control construction; this is not an
unpublished-novelty guarantee.

## One actual H1 child, with all-width maps and lifecycle

Embed the actual source q_i in q+U and let P_i=X_(q_i) be the Pauli-X
translation of that address, identically on all f columns. Put c_i=+1 for
owners 0 through 55 and c_i=-1 for owners 56 through 111. Define

    U_i=P_i, V_i=c_i P_i^-1, H=Q,
    T=I+U H V.

These are literal bit translations on existing axes, not a full-operator
oracle or a new address coordinate. P_i^-1=P_i. Since sum_i c_i=0,

    VU=0, (U H V)^2=0, T^-1=I-U H V.

The latter identity is ordered and needs no assumption that H is free.
All P_i commute with Q and D3, so S0=t=T and their inverses are T^-1.
Q is the actual rank-one Gaussian on the f-bit central row, Q^(tensor f)
in the one-column notation. It is not replaced by a scalar two-term
expansion after tensor lifting; Q^2 is the actual Pauli translation.

One application of T uses an owned zero field g:

1. Gather g=sum_i c_i P_i^-1 x_i before overwriting any x_i.
2. Apply one physical H1 child Q to g in place.
3. Scatter x_i <- x_i+P_i g for all 112 owners.
4. CLEAR/reset the owned g after its last read.

Original independent owners are not scratch. The inverse repeats the same
gather and Q, then subtracts the scatter. The cache earns no productive
credit. A conservative elementary implementation uses one additional
reusable zero field h for each translated COPY/ADD, then clears h. Per
application this gives one H1, 224 monomial translation passes, 224 COPYs,
224 signed ADDs, 225 owned CLEAR/reset operations and two peak scratch
fields. These are field-pass counts, not a bit-operation or precision tariff.
An indexed translated ADD can fuse some passes only with a separately
specified physical implementation. All initialization, movement, bit height,
rounding, stock and cleanup remain actual charged work.

For raw dual use transpose, not adjoint. Q^T=Q and P_i^T=P_i, so

    T^-T=I-V^T Q U^T.

Its literal word gathers sum_i P_i x_i, applies one Q child, then scatters
-c_i P_i g. T^T uses the plus sign. Thus both inverse and raw-dual control
words cost one H1 and retain all arbitrary inputs. No Q=Q^-1 shortcut is
used. These words apply on the source's normalized physical contact fields;
the native backward X-only Q^2 convention and D_s^2 corrections remain.

## Fourth control and complete conditional recursive invoice

No FREE program for E or E^-1 exists for this T by the obstruction below.
A literal paid program for E^-1, rightmost first, is

    Q on 112 fields;
    C3^-1;
    T^-1 using one H1;
    C1^-1;
    Q on 112 fields.

This implements the exact ordered inverse and costs 225 H1. E itself uses
the analogous two Q^-1 banks and T; inverse Gaussian banks have the same
recursive price, with their actual Q^2 Pauli correction charged ordinarily.
No input field or independent helper is silently replaced by a cache.

The main caller uses T twice in J, t^-1 once at the positive endpoint, and
the displayed E^-1 once at the negative endpoint. Its incremental Gaussian
price is therefore

    2 H1 + 1 H1 + 225 H1 = 228 H1.

The existing central query bank of 112 H1 is already in the released base
and is not added a second time. There are four source C/C^-1 recoding
macros in this direct control schedule, with the inherited macro cost each
224 K maps, 896 scalar ADDs and 16 CLEARs using eight reusable mode fields;
the inverse's division by 52 and precision work remain charged. The four
shear uses contribute their explicit ordinary work above. The two fresh
112-field Q banks can execute owner by owner where dependencies permit;
their full field passes, inverse-Gaussian Pauli passes and routing remain.

For two such shears, the same literal policy costs 232 H1. Its hypothetical
FREE-E price would be 3m H1 for m=1 or 2, but the theorem below excludes
that premise. The direct policy is not claimed to minimize a PAID E.

Conditioned on the inherited FULL and helper-completion contracts, the
one-child caller census is

    paid P={1:4836,2:838,3:1020,4:254,5:136},
    target T={9:816,17:224}.

All 1,040 original inputs remain: 224 main jobs and 816 distinct completed
helper jobs, counted once. No dependent query or scratch output is credited.
The 816-owner complement words, finite costs, compiler reserve and outer
admission are inherited/open obligations, not independently certified here.
The raw dual uses the explicit transpose/inverse control words and the same
Gaussian ranks. Positive inverse-Gaussian targets require their actual
Pauli correction passes. This invoice already loses before those costs.

## Scoped theorem: translation-valued controls still need 112 children

Let B_f be the phase-correct algebra of the fixed one-column Pauli-X
translations, lifted to f columns. Let A_f be the group algebra generated
by those translations and a fixed finite collection of X-Gaussians C_v.
Every group element commutes with every X translation. These groups are
finite projectively on the fixed 17 axes. Use the width-dependent cocycle
of the actual tensor lifts; scalar owner coefficients are never tensorized.

Allow arbitrary chronological linear circuits for T with every FREE bypass,
gather, scatter and feedback coefficient in B_f, including dense
operator-valued rows/columns. Permit arbitrary owned copies, saved fields,
fanout and resets. Every paid child is a same-width X-Gaussian in A_f; its
input may depend on previous responses. Require T invertible on all fresh
112-owner inputs at every width and E to have a fixed finite monomial
Clifford implementation. Then the circuit for T requires at least 112 paid
unary calls at every sufficiently large width.

### Source step: E FREE forces every translation component of T to vanish

A monomial operator commuting with all X translations must be a scalar
translation: commutation forces its permutation p(x+a)=p(x)+a and its
multiplier to be constant. Thus the monomial intersection of A is exactly
the translation subgroup, up to phase.

Consider a nonzero translation coefficient X_b of T[r,s]. Choose i,j with
A[i,r] A[s,j] nonzero. The corresponding endpoint word is

    Q^-1 K3_i^-1 K3_r X_b K1_s^-1 K1_j Q^-1.       (1)

Its symplectic linear part is the same as the translation-free word.
The disjoint q+U and q+W source argument says it can be monomial only if
s=j: otherwise G1_s^-1 q_j has a nonzero U component, which the stage-3
map cannot remove. But s=j would require a zero source diagonal coefficient.
Hence (1) is nonmonomial. Translation and phase changes do not remove this
witness.

If an A-letter H at another pair (r',s') has the same projective endpoint
word, then

    H = phase * K3_r'^-1 K3_r X_b K1_s^-1 K1_s'.    (2)

The right side is monomial, so H must be a translation. Its linear binary
part must be identity. Consequently

    G3_r'^-1 G3_r = G1_s'^-1 G1_s.

The left map is supported on q+W, the right on q+U. Their intersection is
identity on the single common binary axis; distinct source q_i then force
r'=r and s'=s. Equation (2) now forces H=X_b projectively. Thus no other
letter or owner pair cancels the chosen coefficient.

The fixed finite projective tensor-separation lemma from #5160 makes these
source words independent of every monomial endpoint word at sufficiently
large width. Therefore E FREE forces all translation coefficients of T to
be zero: projection_B(T)=0. This is stronger than vanishing only the scalar
identity coefficient and uses no scalar owner-rank claim.

### Chronological input cut

Normalize an r-call circuit by saving every paid response y_k. Its kth
input is b_k x+sum_(s<k) e_ks y_s and its output is

    T x = F0 x + sum_k l_k y_k,

where all b_k,e_ks,F0,l_k lie over B_f. Stack the direct input rows b_k.
If r<112, the complex-linear map B_f^112 -> B_f^r has a nonzero kernel
column w. Set the formal input x=w z. Induction makes every paid response
zero, regardless of active feedback, so

    T w = F0 w in B_f^112.

But projection_B(T)=0 means T is supported on nontrivial right cosets of
the translation subgroup in A. Right multiplication by w over B_f stays
in those nontrivial cosets. Hence T w is also in their direct sum, disjoint
from B_f^112, and T w=0.

At sufficiently large width the fixed group/coset support evaluates
faithfully. Thus w is a nonzero actual field embedding while T w=0,
contradicting actual invertibility of T. Therefore r>=112. This uses finite
vector-space dimension and coset direct sums; B_f need not be a division
ring and may have zero divisors.

Since every nontrivial paid Gaussian has price at least H1=1 on the stated
comparison interval, T alone exceeds the 44-H1 allowance. The bound covers
the one/two-child proposals and all larger affordable circuits within this
scope. It does not rely on rank of an extracted scalar coefficient, which
the predecessor operator-valued example correctly disproves.

## Reopening boundary and credit

To continue, supply an actual noncommuting monomial gather/scatter or a
paid E/E^-1 implementation with all four complete control uses, arbitrary
input restoration, raw dual and finite work within the remaining allowance.
An internal C_s or K_i outside the translation algebra changes the circuit
scope and requires a new source-specific kernel argument. Merely inserting
such a recoding does not establish a cheap conjugate control. A smaller
PAID-E implementation is also a distinct open route; the 228-H1 direct
policy is an upper bound, not a lower bound for that route.

Credit Dillon's released template and #5126 chronological input-kernel
argument; Dugongue/mdumitrean's #4929 source; the actual #4933 normalizers;
Cinna Davis/4694/4698, Cao Yifan, zxv, Jacob Sussman, Ryanson Jonathan and
all retained native/helper/compiler lineage. The paper worker checked the
module-cut logic under its stated scope; the source isolation and full
report still require separate review. The ordered nilpotent inverse is
elementary and consistent with the primary quasideterminant/Schur source
already documented by that worker; no paper theorem supplies a query saving.
