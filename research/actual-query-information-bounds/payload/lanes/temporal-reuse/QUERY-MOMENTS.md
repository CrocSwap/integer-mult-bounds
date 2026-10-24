# Fourth and fifth moments of the actual routed queries

For the nine actual charts, the simultaneous query space of one fixed
source has dimension at least

    (4104/73) N

from the first four moments. A separate fifth-moment calculation gives

    (15560/273) N = (57-1/273) N.

Here N is the dimension of one complete field in the full logical
regular-cover module. Thus a linear cache for all nine queries needs
at least 57 complete fields. If storage uses complete eight-field
cohorts, it needs at least eight cohorts, or 64 fields.

This result concerns all nine queries of the same arbitrary source.
The actual controller reads changing sources. This theorem does not
replace those reads by one simultaneous-query obligation. It is not a
native-child bound, an implementation invoice, or a supplier gain.

## Actual query module and source binding

Use the fixed sets

    A = [0,7,20,27,36,46,57,111],
    T = [21,37,47,76,81,87,92,110],
    U = complement(A union T).

There are 96 ordinary ports in U. Let r_p be column p of the actual
8 by 112 centre matrix R. Then

    sum_(p in U) r_p r_p^T = 48 I8,
    r_p^T r_p = 4.

The centre matrix is bound to the supplier word by the separate
reverse-propagation review in SPECTRAL-BOUND-REVIEW.json. The new
checker reads the actual port bases directly from the pinned
DATA-PHASES archive member. It does not import the root experiment or
the controller's route function.

Write the nine-dimensional base space as L. For each port p, its
orthonormal basis is (q_p,b_p1,...,b_p8). For s=1,...,8, let E_s be
the new eight-dimensional coordinate block at stage s. In this
paragraph only, E_s denotes a coordinate block, not a query projection.
The route rho_(s,p) exchanges b_pi with the corresponding axis of E_s.
It fixes q_p and all other exterior blocks. Set rho_(0,p)=I.

The checker verifies the following source facts:

- The 96 bases are the actual bases in DATA-PHASES.
- All nine routes are orthogonal involutions on 73 axes.
- All 36 pairs of stages have 96 distinct relative port routes.
- A common permutation of exterior blocks conjugates any positive
  stage to any other positive stage.
- Every one of the 96 port labels has its expected fresh-block
  action. The full test covers all 9,216 ordered port pairs.
- All 864 ordinary-port stage alignments agree as exact phase forms.
  This check uses every linear and quadratic coefficient. It is not a
  constant-payload sample.

Let G be the selected finite cover group. It contains these routes.
For a field f on G, define the right pullback

    [P_g f](d) = f(d g).

Then P_g P_h=P_(g h). On binary address vectors, the matrix g h acts
by h first, then g. In particular, B_s B_t* below uses rho_(s,p)
rho_(t,p), with vector route t first. The checker includes an order
control: on the first E_1 axis, rho_(1,p)rho_(2,p) and its reverse
have different images.

Take a payload space W and the full module C[G] tensor W. Its field
dimension is N=|G| dim(W). The logical owner routes act as P_g tensor I.
An honest payload representation V_g gives the same result: the action
P_g tensor V_g is unitarily equivalent to copies of the regular action.
For example, the change of coordinates [Uf](d)=V_d f(d) removes V_g.
Thus the normalized trace of a group element is zero unless g=I.
At g=I it is N.

These are the logical query operators after the accepted physical
chart maps have been removed. The exact phase alignment check binds
that chart identification on arbitrary payloads. A left unitary mode
gauge also cancels from the projections below. A fixed common unitary
source gauge conjugates all projections and leaves every moment
unchanged. The theorem does not cover different extra source gauges
at different stages without a new check.

A constant-payload subspace alone would not prove the complete-field
width bound: an unrestricted encoder could use other payload slots.
The bound here uses the full module just defined. Physical storage
outside that module or additional source reads are outside its scope.

## Projections and the singleton rule

Let D_s be block diagonal in the 96 ports, with block P_(rho_(s,p)).
Define

    B_s = R_U D_s,
    P_s = B_s* B_s / 48.

Since B_s B_s*=48I, each P_s is an orthogonal projection of rank 8N.
We use P_s for projections in the rest of this note. Its (p,q) block is

    (r_p^T r_q) P_(rho_(s,p) rho_(s,q)) / 48.

Expand a cyclic trace of a word in these projections. A port index is
attached to each edge of the cycle. If a positive stage v occurs once,
its unique group factor is rho_(v,p)rho_(v,q). Every other stage fixes
the fresh coordinate block E_v pointwise. If the complete group product
is I, this unique factor must fix E_v pointwise.

This forces p=q. In fact, rho_(v,q) sends an E_v basis axis to b_qi.
For rho_(v,p) to return all eight axes unchanged requires b_qi=b_pi
for all i. Their one-dimensional orthogonal complements are then the
same port line, so q_p=q_q and the actual ports are equal. The checker
verifies this condition on all actual ordered port pairs.

With p=q, that group factor becomes I and its scalar factor is
r_p^T r_p/48=1/12. The remaining port sum is exactly the shorter word.
Therefore:

    A positive stage which occurs once in a cyclic word can be removed
    at the exact trace factor 1/12.

This rule uses the fresh-block action. It does not assume free groups
or free projections. If all k stages in a word are distinct, at most
one is stage zero. Repeated use of the rule gives

    tr(P_(s1)...P_(sk))/N = 96/12^k,       1 <= k <= 9.

In particular, the distinct triple is 1/18 and the distinct fourth
moment is 1/216. A mixed word P_s P_t P_s P_u with three distinct
stages has a positive singleton among t and u. Its trace is therefore
(1/12) tr(P_s P_t)/N = 1/18, after cyclic idempotence.

## The alternating pair

Put A_p=r_p r_p^T and g_p=rho_(s,p)rho_(t,p). The unscaled product
(B_s B_t*)(B_t B_s*) has group coefficients

    sum_(p,q) (r_p^T r_q) r_p r_q^T [g_p g_q^-1].

For p=q, the identity coefficient is 192I8. For distinct p,q with
nonzero root product, the checker verifies that all 4,224 group words
are nonidentity and distinct. This is checked for the two stage types
(0,1) and (1,2). Common exterior-block permutations cover every other
type. Reversal does not change the alternating trace.

The squared Frobenius norm of each nonidentity coefficient is
2^2*4*4=64. The regular trace of the square is therefore

    [8*192^2 + 4224*64] / 48^4 = 23/216.

As a separate check, the coefficient supports for the three mixed-stage
types (0,1,0,2), (1,0,1,2), and (1,2,1,3) meet only at I. Their
Frobenius inner product is 8*192^2, which again gives 1/18.

## Fourth moment and rank

Set S=sum_(s=0)^8 P_s. Classify the fourth-order words by repeated
stage labels. Cyclic idempotence reduces adjacent equal labels. The
only unreduced two-label word is the alternating pair. The singleton
rule handles all three-label and four-label cases.

For k distinct charts, the fourth moment per field dimension is

    8k + 4k(k-1) + (23/216)k(k-1)
       + k(k-1)(k-2)/3 + k(k-1)(k-2)(k-3)/216.

At k=9 the first four moments are

    tr(S)/N = 72,
    tr(S^2)/N = 120,
    tr(S^3)/N = 244,
    tr(S^4)/N = 1649/3.

Use f(x)=13x-4x^2. On the nonzero eigenvalues, Cauchy's inequality gives

    rank(S) >= [tr f(S)]^2 / tr(f(S)^2)
            = 456^2 N / (11096/3)
            = (4104/73) N.

No positivity of f is needed. It vanishes at zero. This f is the
optimal linear combination of x and x^2 for this Cauchy bound, as can
be checked by inversion of the two by two moment matrix.

The range of S is the sum of all query row spaces. If all queries
factor through a linear cache of r complete fields, its dimension is
at most rN. Thus r>=57. Arbitrary borrowed inputs do not evade this
factorization bound: set those independent inputs to zero. Extra
source-dependent outputs or later source reads change the hypothesis.

## Bounded fifth-order extension

After cyclic idempotence and the positive-singleton rule, only one new
fifth-order type remains: P_a P_b P_a P_b P_0 with distinct positive
a,b. All such types are conjugate to (1,2,1,2,0).

The separate checker expands

    (B_1 B_2*)(B_2 B_1*) (B_1 B_2*)(B_2 B_0*)(B_0 B_1*)

and takes its regular trace. The first two factors have the 4,225-term
coefficient table already checked above. The last three factors have
terms

    (r_r^T r_s)(r_s^T r_t) r_r r_t^T
       [g_r rho_(2,s) rho_(1,t)].

Each ordinary port has 45 nonzero root products, including itself.
Thus there are 96*45^2=194,400 supported triples to check. Exactly
4,320 group terms match the required inverse coefficient support;
96 of these are identity terms. Exact integer coefficient contraction
gives numerator 2,260,992 and denominator 48^5. Hence this type has
trace 23/2592 per N. This finite aggregation is not a freeness claim.
All triples with s=t already match by the identity
g_r rho_(2,s)rho_(1,s)=g_r g_s^-1. There are 4,320 such supported
triples. The exact count therefore also proves that no other supported
triple matches.

The checker reduces all fifth-order words to the accepted cases. It
gives

    tr(S^5)/N = 47467/36.

Since 0<=S<=9I, apply weighted Cauchy with weight 9-x and
f(x)=19x-6x^2. Write r=rank(S)/N. Then

    sum_(lambda != 0) (9-lambda) = (9r-72)N.

The first five moments give the remaining weighted sums. Optimization
over linear combinations of x and x^2 gives

    r >= 15560/273 = 57-1/273.

For a direct check, the weighted trace of f is 5,016N and the weighted
trace of f^2 is 57,057N. Thus 9r-72 >= 5016^2/57057 = 40128/91,
which is the same bound.

This improves the real-valued rank bound. It does not raise the
complete-field or eight-field-cohort counts.

## Limit of the first-five-moment relaxation

The last bound is sharp in the continuous positive-measure moment
problem with spectrum in [0,9]. Consider nodes

    0, a=(19-2 sqrt(22))/12, b=(19+2 sqrt(22))/12, 9.

Give the nonzero nodes total mass r=15560/273 and node 9 mass 8/7833.
Choose the masses at a and b to match total mass and first moment 72.
Their weighted mean is strictly between 1 and 2. Since 0<a<1<2<b<3,
both masses are positive. Give node zero the remaining mass 96-r.
The specified mass at nine makes the second moment 120, since
the polynomial x^2-(19/6)x+91/48 vanishes at a and b.

The three nonzero nodes are roots of

    x^3-(73/6)x^2+(1459/48)x-273/16.

The moment sequence (r,72,120,244,1649/3,47467/36) satisfies the three
resulting recurrence equations exactly. It therefore matches all five
positive moments of S. This proves sharpness for that continuous
moment relaxation. It does not assert that the actual finite rational
operator has this spectrum, or that these masses are integer
multiplicities. A stronger actual rank bound needs other information.

The first five moments also equal the corresponding free-projection
moments at relative rank 1/12. The checker verifies this finite
comparison with the noncrossing moment recurrence: first solve for
the cumulants of the moments m_0=1 and m_j=1/12, then multiply each
cumulant by nine and reconstruct the first five moments. Only this
finite comparison is claimed. Equality of later moments, or freeness,
has not been proved.

## Replay, credit, and limits

Run these commands in order from the workspace root:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/temporal-reuse/check_query_fourth_moment.py
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/temporal-reuse/check_query_fifth_moment.py
```

The expected statuses are `PASS_ACTUAL_QUERY_FOURTH_MOMENT` and
`PASS_ACTUAL_QUERY_FIFTH_MOMENT`. Both checkers use exact integers and
fractions. Checks remain active under `-O`. The second checker imports
the pinned independent fourth checker; neither imports the root
experiment or a controller producer. No full cover matrix is built.

The root's exact group-coefficient experiment supplied the alternating
fourth-moment value and the fourth-moment target. The controller lane
supplied the actual 96-port query interface and the first two moments.
The cover-algebra lane supplied the distinct-triple argument. This
lane checked the actual route convention, proved the singleton rule,
checked the fourth moments independently, and derived the bounded
fifth-order extension and its moment-relaxation limit. OpenAI Codex
assisted with the research, proofs, and verification code.

No cache construction, native-child saving, changed-source controller,
hosting schedule, recursive invoice, or complete kappa result follows
from this note.
