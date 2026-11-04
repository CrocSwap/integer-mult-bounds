# A sharp all-even coupled stage-rank budget

Prepared by **thu-nmrc with substantial OpenAI Codex assistance**.
Apache-2.0. This is a coefficient-space rank theorem, with no physical
native module, paid invoice, kappa increment, or scientific-acceptance claim.

## 1. Statement and precise contribution

Let K be a commutative field of characteristic different from two.
Let n>=4 be even and q>=1. On an nq-dimensional space let
R0,...,Rn be rank-q square-zero operators such that

    (I-2Rn) ... (I-2R0) = -I.

Write T_i=I-2R_i and B_i=T_i ... T0. At three distinct selected sites
let P_i be idempotents satisfying

    P_i R_i = R_i P_i = R_i,       [P_i,B_i]=0.

Suppose the three selected P_i commute pairwise. Their ranks may exceed
the minimum2q; no rank-minimality assumption is made.

**Theorem. The sum of the three selected ranks is at least7q. The bound
is attained for every even n>=4 and every positive q.**

These are normalized ordinary coefficient-space operators in the shortest
query contract. The nq inputs are independent. No initialized extra main
input or discarded independent input is allowed. Arbitrary constant
ordinary basis changes mixing all nq coordinates are permitted through
the common normalization. Internal q-by-q coefficient blocks need not
commute. The prefix in the hypothesis is the actual complete chronological
query prefix, rather than merely the query at that site.

This extends the n=4 result in PR6717. Ali Romman's PR6398 section2 already
proves the scalar local commuting-triangle obstruction for every evenn;
the scalar rank-sum-seven consequence is old. Its section3 supplies the
image/row rank inequality and the forced minimal odd projector
`A(CA)^(-1)C`, including scalar six-field closure tables. The complete
scalar and coupled shortest-query normal forms are also predecessor
results. Ali Romman's `alternating-caller-closure/PROOF.md` further treats
the fixed minimal odd interior at every evenn and everyq, with explicit
projector blocks, total curvature and a generic low-rank commutator
correction bound. Those all-length fixed-interior tools are retained as
well. None of those mechanisms is claimed as new here.

The contribution is the **uniform all-even-n, all-q quantitative bound on
extra stage dimensions**, using odd-projector commutators and a rank-defect
estimate at a far endpoint, together with a literal all-n attaining word.
The generic low-rank commutator estimate itself is an inherited tool;
the new scope is its arbitrary-three mixed-rank threshold application
combined with endpoint leakage, rather than a fixed-interior exclusion.
The proof does not infer arbitrary coupled projectors by tensoring scalar
classifications. The q=2 rank13 compatibility-only example is retained
as a failed-prefix control, with its distinct contract made explicit.

Original source files and notices are included unchanged in `inputs/`.
`SOURCES.json` pins their commits, Git blobs and SHA256 values, including
the exact published PR6717 proof.

## 2. Retained normal form and rank lemma

Factor each query as R_i=U_i V_i, with U_i of size nq byq, V_i of sizeq
by nq and V_i U_i=0. The retained complete coupled normal form gives

    V_i U_j = sign(i-j) I_q,       i != j.

Here is the source argument needed to specify its field scope. Concatenate
the factors into U,V; put G=VU and let L be its strict block-lower part.
Chronological expansion gives

    product_i (I-2R_i) = I-2U(I+2L)^(-1)V.

Thus U(I+2L)^(-1)V=I. The matrix `(I+2L)^(-1)VU` is a rank-nq
projector, so Z=I+2L-G has rankq and diagonal blocks I_q. Write Z=AB
with inner dimensionq. Each A_i B_i=I_q makes both square blocks
invertible. Replacing U_i by U_i A_i and V_i by A_i^(-1)V_i gives the
displayed Gram. No matrix blocks are commuted. The leading even skew
sign matrix is invertible, yielding a common basis in which the full
tuple is the scalar canonical tuple tensored with I_q:

    u_i=e_i (0<=i<n),          u_n=(-1,1,-1,1,...),
    (v_i)_j=sign(i-j),         R_i^can=(u_i v_i) tensor I_q.

These source operations use only inverses of2 and invertible field
matrices, so this portion works in characteristic different from two.

We also retain the basic image/row inequality. If an idempotent P contains
a column space A of dimensiona, supports a row space C of dimensionc,
and their pairing has rankg, then

    rank(P) >= a+c-g.                                      (1)

Indeed the row map on im(P) has rank at leastc, and its kernel contains
an (a-g)-dimensional subspace of A. In particular a projector compatible
with a rank-q square-zero query has rank at least2q.

All subsequent calculations take place in the canonical common basis.
They are unchanged by conjugating back to the original ordinary frames.
The symbol tensor I_q refers to coupling of coefficient ports, not to a
physical column-width or Gaussian phase lift.

## 3. Uniform chronological prefixes

For i<n define the following scalar vectors and rows of lengthn:

    a_i=(1,-1,1,...,(-1)^i,0,...,0)^T,
    h=(1,...,1),
    h_i=(1,...,1,0,...,0),       with ones through indexi,
    tail_i=(0,...,0,1,...,1),    with ones after indexi,
    v_i=h_(i-1)-tail_i,         h_(-1)=0,
    J_i=diag(-I_(i+1), I_(n-i-1)).

The scalar prefix has the exact closed form

    B_i = J_i+2a_i h,       0<=i<n.                       (2)

For example, if (2) holds at i-1, then
`v_i B_(i-1)=e_i^T-(-1)^i h`. Multiplication by I-2e_i v_i changes
J_(i-1) to J_i and a_(i-1) to a_i. The initial step is the same identity
with B_(-1)=I. This proves (2) by induction. The final full prefix is
B_n=-I by the query endpoint. At widthq, tensor every displayed scalar
coefficient-space matrix with I_q.

## 4. Every even interior full site costs at least4q

Let i be even with2<=i<=n-2. Formula (2) gives

    B_i e_i=-e_i+2a_i,
    v_i B_i=-h_(i-1)-tail_i.

If P_i is compatible and commutes with B_i, its image contains
`A=span(e_i,a_i)` and its row space contains
`C=span(h_(i-1),tail_i)`. Both spaces have dimension2. Their pairing is
zero: the tail misses both columns, and the even alternating prefix has
sum zero before indexi. Their coupled dimensions are2q and2q. Equation
(1) therefore gives

    rank(P_i) >= 4q.                                     (3)

Any selected triple containing such a site already has rank sum at
least8q, since every other compatible projector has rank at least2q.
It remains to treat odd interior sites and the two endpoints.

## 5. Forced minimal odd projectors and extra dimensions

For odd i, define the scalar rank-two projector

    E_i=e_i h_i+a_i v_i.

Put A_i=(e_i,a_i) and C_i=(h_i;v_i). Since
`C_i A_i=I2`, E_i=A_i C_i is an idempotent of rank2. This is the
uniform expression for the predecessor's forced odd minimal projector.
The all-length fixed odd projector and explicit block mechanism is also
retained from `alternating-caller-closure`; this formula is not claimed
as a newly discovered minimal projector.

Formula (2) gives

    B_i e_i=-e_i+2a_i,       v_i B_i=2h_i-v_i.

Thus compatibility and prefix commutation force P_i to contain A_i and
support C_i. Consequently, after tensoring with I_q,

    P_i E_i=E_i P_i=E_i,
    F_i=P_i-E_i is an idempotent,
    rank(F_i)=e_i^extra := rank(P_i)-2q >=0.                (4)

To avoid confusion, e_i without a superscript continues to mean the
standard basis column; an extra dimension is denoted by e_i^extra.
The minimal projector itself commutes with B_i: on A_i and C_i the
prefix acts through the same matrix `[[-1,0],[2,-1]]`.

### Two odd sites force at leastq extra dimensions

For odd i<j put `t_j=e_j^T+tail_j`. Direct ordered multiplication gives

    E_i E_j = -a_i t_j,
    E_j E_i = (e_j+a_j) h_i.                              (5)

The two columns a_i and e_j+a_j are independent: the second has a
nonzero coordinate between i+1 and j-1, while the first has none.
The rows t_j and h_i are nonzero with disjoint supports. Therefore

    rank([E_i,E_j])=2                 in the scalar form,
    rank([E_i,E_j])=2q                at coupled widthq.   (6)

Since P_i,P_j commute, the following identity retains every matrix order:

    [E_i,E_j] = -[P_i,F_j]-[F_i,E_j].

Each commutator with F has rank at most twice rank(F). Hence

    2q <= 2(e_i^extra+e_j^extra),
    e_i^extra+e_j^extra >= q.                             (7)

Any selected triple with two odd interior sites therefore has rank sum
at least7q. This argument permits fully noncommuting internal block
coefficients; no exchange of E_i,F_j or other matrices has occurred.

## 6. A sole odd site leaks extra rank to a far endpoint

The remaining selected triple consists of the two endpoints0,n and one
odd interior sitei. Write P=E_i+F, with rank(F)=e. At least one endpoint
has the following zero-paired closure under E_i.

For the left endpoint, if i>=3, canonical substitution gives

    E_i u0=e_i+a_i,       v0 E_i=-(e_i^T+tail_i).

The columns `(u0,E_i u0)` and rows `(v0;v0 E_i)` both have rank2,
and their pairing is zero. The ranks use a coordinate strictly between
0 andi, which exists because i>=3.

For the right endpoint, if i<=n-3, substitution gives

    E_i u_n=-a_i,        v_n E_i=h_i.

The columns `(u_n,-a_i)` and rows `(h;h_i)` both have rank2 and pairing
zero. The ranks use a coordinate afteri. Since n>=4 andi is odd, at
least one of i>=3 and i<=n-3 holds. Thus a **far endpoint always exists**,
including i=1 and i=n-1. At widthq the two closure spaces have dimensions
2q,2q and still have zero pairing.

Let Q be the selected far-endpoint projector and write its query factors
as U,V. It is compatible, so QU=U and VQ=V. Since Q commutes with P,

    (I-Q)E_i U = -(I-Q)F U,
    V E_i(I-Q) = -V F(I-Q).                              (8)

The right sides have rank at moste. For the column closure
`A=span(U,E_i U)`, equation (8) implies

    dim(A intersect im(Q)) >= 2q-e.

For the row closure `C=span(V,V E_i)`, it similarly implies

    dim(C intersect row(Q)) >= 2q-e.

The inherited zero pairing C A=0 persists on these subspaces. Applying
(1) to Q gives the quantitative rank-defect bound

    rank(Q) >= 4q-2e.                                    (9)

This bound is for arbitrary Q and P of the given ranks, not scalar
projector classifications tensored with I_q. It follows from ranks of
the actual leakage maps in (8).

Write rank(Q)=2q+f. Compatibility also gives f>=0. Therefore

    f >= max(0,2q-2e),
    e+f >= e+max(0,2q-2e) >= q.                         (10)

The last step has two elementary cases: if e>=q it is immediate;
if e<=q, the left side is at least2q-e>=q. The third selected projector
has rank at least2q. This proves the total rank bound7q in the sole-odd
case without a separate boundary-pair or nesting argument.

The cases (3), (7), and (10) exhaust all triples: without even interior
sites, a triple either has at least two odd interior sites or consists
of both endpoints and one odd interior site. The theorem is proved for
every evenn>=4 and everyq>=1.

## 7. Exact all-n attainment

Here is one ordinary unimodular basis giving equality, rather than a
finite search for small dimensions. In the first four coordinates define

    c0=(1,1,0,0),     c1=(1,2,1,0),
    c2=(1,2,2,0),     t=(0,1,1,1).

Let H have first four entries of columns0,1,2 equal to c0,c1,c2;
every columnj>=3 has first four entries t. In the remaining coordinates,
for3<=j<=n-2 let columnj have the unit entry in rowj+1, and let the last
column have the negative alternating sum

    -sum_(j=3)^(n-2) (-1)^(j+1) e_(j+1).

All other extra entries are zero. There are n-4 terms in this sum, an
even number. Add their indicated alternating columns to the last column:
its extra entries cancel and its first four entries remain t. Subtract
this last column from each columnj=3,...,n-2. After an even column
permutation, the result is

    H4 direct-sum I_(n-4),
    H4=[[1,1,1,0],[1,2,2,1],[0,1,2,1],[0,0,0,1]].

H4 has determinant1, so H has determinant1 over the integers. In
particular this is valid over every allowed field.

Conjugate all n+1 canonical query matrices by H. The selected sites0,1,n
then have the same columns and rows in the first four coordinates as
the prior n=4 attaining control:

    u0=(1,1,0,0),      v0=(1,-1,0,0),
    u1=(1,2,1,0),      v1=(1,0,-1,0),
    u_n=(-1,0,0,1),    v_n=(1,0,0,1),

with zeros elsewhere. The remaining coordinates of these selected
columns and rows vanish by the alternating-column construction. Put

    P0=diag(1,1,0,0,0,...),
    P1=diag(1,1,1,0,0,...),
    Pn=diag(1,0,0,1,0,...).

Their ranks are(2,3,2). They commute and are compatible. P1 supports
both R0,R1, so it commutes with B1; the endpoint prefix conditions are
automatic. Make all other sites thin. Give the selected stages three
independent central variables A,B,C and use their literal full-site
operators

    (I+(D_i-1)P_i)(I+(S-1)R_i),       S^2=I.

At S=+1 the full chronological word equals
`diag(ABC,AB,B,C,I_(n-4))`. At S=-1 it is its negative, using the
prefix conditions and the full shortest-query endpoint. Since2 is
invertible, these two characters establish the exact formal identity

    S diag(ABC,AB,B,C,I_(n-4)).                           (11)

Tensoring these coefficient-space matrices with I_q proves attainment
with ranks(2q,3q,2q) for everyq. All nq input fields remain arbitrary
and independent. A zero stage selector on an extra coordinate means
that the stage does not act there; it does **not** initialize that input
to zero. Such extra outputs receive the central factor S in (11).

This is an abstract exact query/stage word. It supplies no physical
native routing, absolute Gaussian phase, helper interface, operation
allowance, or price by itself. No scalar attainment mechanism is claimed
as new; the all-n extension is included as a sharpness construction.

## 8. Failed-prefix controls and the n=6 next gate

The frozen rational q=2 compatibility-only tuple in
`inputs/LOCAL13.json` has three commuting projectors of ranks(4,4,5),
both selected U/V ranks6, and a full five-query product-I8. Its prefix
commutator ranks are(0,4,4). Thus compatibility without the actual
prefix hypothesis genuinely permits a rank sum below7q.

There is also a direct next-gate check at n=6. Cyclically order its
three local queries as old(1,2,0) and apply factor signs(1,1,-1), so
their canonical chronological sites are0,3,6 and the rank5 projector
is the middle one. With x=(1,0), the actual target local data have

    P_middle (U0+U6)x=0.

But the canonical seven-query source has

    V3 B3 U0=I2,        V3 B3 U6=I2,
    V3 B3(U0+U6)x=2x !=0.

If P_middle commuted with B3, and V3 P_middle=V3, the last expression
would equal `V3 B3 P_middle(U0+U6)x=0`, a contradiction. Adding four
extra independent coordinates with zero selected-stage projectors
does not change this equation. This source-prefix invariant blocks
all completion choices for that fixed local model before a GL search.
It is not inferred from a scalar-history span or from the old n=4
adjacency lemma. The universal theorem above separately covers all
rank13 candidates satisfying its full hypotheses, not only this model.

## 9. Verification and limits

`python3.12 -I -B verify.py` and
`python3.12 -I -B -O verify.py` are read-only standard-library checks.
`--write` authors the receipt. The verifier authenticates every included
source byte and notice; retains the prior n=4 sharp and failed-prefix
controls; checks the uniform prefix, odd projector, ordered product and
far-endpoint closure formulas; checks an ordered free-word commutator
identity; and verifies the all-n attaining word by literal multiplication
with three independent stage variables at S=+1,-1. The finite fixtures
are n=4,6,8,10,12 with several coupled widths, includingq=3. They
corroborate conventions. The proof, rather than a finite grid, supplies
alln/allq and the characteristic scope.

The hypothesis is a shortest n+1-query tuple with rank-q square-zero
queries, nq independent fields, ordinary constant normalization,
selected compatibility, actual prefix commutation and selected pairwise
commutation. More query calls, different query ranks, initialized or
discarded main fields, stage-dependent ordinary maps, or different
central/output conditions change the model. Arbitrary pre-normalization
frame commutation is not the hypothesis. No general noncommuting-stage
thin-call bound is proved.

This theorem gives a coefficient-space stage-dimension inventory, not
a minimum number of physical Gaussian calls or a cost lower bound for
every implementation. There is no native supplier, complete invoice,
kappa increment, integer-multiplication theorem, discharge of the
inherited framework assumptions, or frontier selection in this note.
These are AI-assisted author proofs and checks, not human review or
proof-kernel verification.

Ali Romman's scalar obstruction, forced minimal odd projector/closure
method, image/row rank lemma, complete coupled normal form, and
all-length fixed alternating-interior/curvature/low-rank commutator tools retain
their original credit, including Cinna Davis's query/controller lineage
and all retained contributors. The prior n=4 result in PR6717 remains
credited to thu-nmrc with substantial OpenAI Codex assistance. New
uniform extra-rank commutator/leakage extension and all-n sharp controls:
thu-nmrc with substantial OpenAI Codex assistance. All copied original
notices remain unchanged. Apache-2.0.
