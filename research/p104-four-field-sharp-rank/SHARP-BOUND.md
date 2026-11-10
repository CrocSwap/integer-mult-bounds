# Sharp four-field coupled stage rank

Prepared for Jerry Chen (@CubeJerry), 2026-11-06, with substantial OpenAI
Codex assistance. Analytic derivation: workstream B. Apache-2.0.

## Statement and scope

Retain exactly the actual-prefix/full-query hypotheses of CubeJerry's #6773,
head `10ecaad298e6a6af7416fbd2baca15674fcadf5b`,
`research/p104-four-stage-rigidity/FOUR-STAGE-NOTE.md`. In particular the ground
field K is commutative and has characteristic different from two; n=4; the
five rank-q square-zero queries act on all 4q arbitrary independent inputs;
their full chronological product at the negative central character is −I;
the four full-stage idempotents at sites 0,1,3,4 commute pairwise, support
their queries on both sides, and commute with their ACTUAL prefixes.
The inherited coupled normal form has the ordered query Gram blocks
`V_i U_j = sign(i−j) I_q`. No internal q by q matrices need commute.

Then the total stage rank is at least `ceil(21q/2)`. The q=2 rank 21 fixture
constructed independently by worker D attains 21q/2; the scalar rank 11
fixture supplied by the lead, together with direct sums, attains the ceiling
for every positive integer q. Thus the formerly open interval (10q,11q)
is nonempty for every q>=2. This is a coefficient-space theorem, not a native
supplier, a paid invoice, a physical-port construction, or a multiplication
theorem. All five selected framework assumptions remain.

## 1. Endpoint trimming and joint sectors

Name the four stages A,B,C,D. Here is the retained actual-prefix implication directly. Write Q_i=I−2R_i.
Because B supports R_1, it commutes with Q_1. Its commutation with the
actual prefix Q_1 Q_0 therefore implies commutation with R_0. The invertible
cross-Gram blocks V_1 U_0 and V_0 U_1 then force B U_0=U_0 and V_0 B=V_0:
apply B to R_0 R_1 on the left and to R_1 R_0 on the right. Thus B supports
both queries 0 and 1. At site 3, the actual prefix is −Q_4^-1=−I−2R_4, so C
commutes with R_4. Its support of R_3 and the analogous invertible cross-Gram
blocks force support of R_4. Thus C supports both queries 3 and 4.
Replace A by AB and D by CD. Pairwise commutation makes these idempotents;
the replacements still support the endpoint queries, and their ranks cannot
increase. The site 0 prefix is `I−2R_0`, so compatibility already ensures its
commutation. The site 4 prefix is −I. Thus trimming is legal. It suffices to
prove the lower bound with `A<=B` and `D<=C`.

The four selected query columns give an invertible 4q by 4q matrix U: their
Gram is the invertible four-site sign matrix. Use them as coefficient basis.
Writing a,b,c,d for selected query indices 0,1,3,4, the row matrix is

    K = [[ 0,-I,-I,-I],
         [ I, 0,-I,-I],
         [ I, I, 0,-I],
         [ I, I, I, 0]],
    K^-1 = [[ 0, I,-I, I],
            [-I, 0, I,-I],
            [ I,-I, 0, I],
            [-I, I,-I, 0]].

Because B contains the first two query columns and C the last two, B union C
is the full ambient space. The commuting idempotents therefore split it into
joint sectors. A query column and its row can occur only in sectors carrying
its required stages: AB for a, B for b, C for c, and CD for d.

For a joint-sector projector E put M=K E. Both rows and columns of M vanish
outside the query indices allowed in that sector, and

    M K^-1 M=M,       rank M=rank E.                 (1)

A B-only sector lacking A allows only b. Since the bb block of K^-1 is zero,
(1) makes it zero. Similarly C-only lacking D vanishes. The only possible
nonzero sectors, with their dimensions, are

| Sector | AB | BC | CD | ABC | BCD | ABCD |
|---|---:|---:|---:|---:|---:|---:|
| Dimension | x | y | z | h | j | w |

Their dimensions sum to 4q. The endpoint cross-Gram `V_a U_d=−I` passes only
through ABCD; consequently `w>=q`. The total stage rank is

    T=2(x+y+z)+3(h+j)+4w
     =12q−(x+y+z)+w.                                (2)

It remains to prove `x+y+z<=5q/2`.

## 2. The separated-pair capacity x+z<=2q

Let M_X,M_Z be the 2q by 2q supported blocks of the AB and CD sectors.
Put `J=[[0,I],[-I,0]]`, `v=(I,−I)^T`, and `t=(0,I)^T`.
Each block satisfies `M J M=M`. Since `J=v t^T−t v^T`,

    rank M <= rank(Mv)+rank(v^T M).                 (3)

The cross blocks of K^-1 between these separated pairs are `−vv^T` and
`vv^T`. Orthogonality of the sector projectors therefore gives

    (M_X v)(v^T M_Z)=0,  (M_Z v)(v^T M_X)=0.

For two maps whose product is zero, their ranks sum to at most the dimension
of the middle space. Each middle space here has dimension q. Sum the two
inequalities and use (3) to obtain

    x+z<=2q.                                        (4)

As a separate consequence, the two odd-stage ranks sum to at least 6q,
because B=I−E_CD and C=I−E_AB after combining sectors as appropriate; more
generally the proof of (4) applies to the full B-only and C-only projectors,
which are supported on pairs ab and cd. Then `rank B+rank C=8q−x−z>=6q`.

## 3. Three-sector reduction

Let M_X,M_Y,M_Z now denote the supported blocks for the three low-cost
sectors AB,BC,CD. Define ordinary idempotents on one 2q-dimensional space by

    P_X=M_X J,  P_Y=M_Y J,  P_Z=M_Z J.

The order `M J` is essential. It follows from (1) that these are idempotent.
The cross block of K^-1 for either adjacent pair of these two-query supports
is `T_0=[[I,−I],[0,I]]`. Define

    F=J^-1 T_0=[[0,−I],[I,−I]],       F^3=I,
    P=P_X,  Q=F P_Y F^-1,  R=F^2 P_Z F^-2,
    N=[[I,0],[I,0]].

Multiplying the six ordered cross-block orthogonality equations gives

    PQ=QP=QR=RQ=0,
    P N R=0,             R(I−N)P=0.                (5)

For clarity, the last two multipliers are obtained from
`D=J^-1(−vv^T)`: `D F=N` and `F^2(−D)=I−N`.
All are ordered matrix identities; no internal matrices are exchanged.
The ranks of P,Q,R are x,y,z.

Split off imQ. The other two projectors act on `H_0=kerQ`, whose dimension
is `m=2q−y`. Let L be the compression of N to H_0 along imQ. Equation(5)
becomes `P L R=0` and `R(I−L)P=0` on H_0.

Let `I_0=imP intersection imR` and `J_0=rowP intersection rowR` on H_0.
For u in I_0 and phi in J_0,

    phi L u = phi P L R u=0,
    phi(I−L)u = phi R(I−L)P u=0.

Thus `phi u=0`: these common column and row spaces pair to zero. Both have
dimension at least `x+z−m`. Applying the retained idempotent rank lemma
inside P and inside R gives

    x>=2(x+z−m),  z>=2(x+z−m),
    3(x+z)<=4m=4(2q−y).                            (6)

This also holds when x+z−m is negative: the preceding inequalities then
follow from nonnegative dimensions. The rank lemma used here says that an
idempotent containing a column space U and a row space V has rank at least
`dim U+dim V−rank(VU)`. To see this directly, restrict the rows V to
the r-dimensional image of the idempotent. They remain independent because
V P=V, so their common kernel there has dimension r−dim V. Its intersection
with U has dimension dim U−rank(VU), which cannot exceed that kernel
dimension. All divisions of rank inequalities in this proof are inequalities
of ordinary integers/rationals, not division in the ground field.

Combine(4) and(6). If y<=q/2, then `x+y+z<=2q+y<=5q/2`. If y>=q/2,
then(6) gives `x+y+z<=(8q−y)/3<=5q/2`. This proves the required capacity.
Equation(2) and w>=q now give `T>=12q−5q/2+q=21q/2`.

## 4. Equality profile

Equality 21q/2 forces equality in both capacity bounds, hence

    x=z=w=q,   y=q/2,   h+j=q/2.

In particular q must be even. Trimming must have preserved the original
stage ranks, so A<=B and D<=C already hold for an equality tuple. Its stage
ranks are

    (2q+h, 3q, 3q, 2q+j),  h+j=q/2.

Worker D's q=2 fixture realizes h=0,j=1. Reflecting the query order realizes
h=1,j=0. Direct sums realize every integer split h+j=q/2 for even q.
For odd q the exact integer minimum follows by adding the scalar rank 11
fixture to (q−1)/2 copies of the q=2 rank 21 fixture. Direct sums preserve all
query ranks, square-zero identities, the full endpoint, actual-prefix
commutation, and simultaneous stage masks. Reflection uses
U'_i=U_(4−i), V'_i=−V_(4−i), and reverses the four projectors; it preserves
the sign Gram and changes each query factor to the inverse of its reversed
predecessor. The full endpoint remains −I. More precisely, for j=4−i the reflected
prefix is B'_i=−B_(j−1), with B_(-1)=I. The original P_j commutes with
B_(j−1) because it commutes with B_j and with Q_j, so reflected actual-prefix
commutation follows. No classification of all
odd-q ceiling-equality profiles is claimed. Both base fixtures have integral
matrices and an integral inverse for their input basis H. Their exact
identities therefore hold over every allowed field; stage ranks follow from
the diagonal masks, and query ranks follow from the unit cross-Gram blocks.

For any other choice of four sites among 0,1,2,3,4, site 2 is included. The
retained #6717 even-interior 4q floor and three-stage 7q theorem then give 11q,
as already aggregated in #6773. Consequently ceil(21q/2) is also the global
minimum over all four-stage placements at n=4. This last corollary inherits
those two predecessor bounds; it does not reprove them.

## 5. No removable idle sector at the minimum

Let a legal four-stage tuple attain the minimum ceil(21q/2). Fix one of its
selected sites i and a joint-sector projector E_sigma whose mask contains
stage i. There cannot be a row a, a column b, and a scalar lambda satisfying

    a=a E_sigma,  b=E_sigma b,  ab=1,
    a B_i=lambda a,  B_i b=lambda b,
    a R_i=0,  R_i b=0,

where B_i is the actual chronological query prefix. The relevant central
characters often give lambda=+1 or −1, but the argument permits any scalar.

Indeed F=ba is a rank-one idempotent. Sector support gives
E_sigma F=F E_sigma=F, so F lies under P_i and commutes with every stage
projector. The matching left and right prefix eigenvalues give
B_i F=F B_i=lambda F. Both-sided query idleness gives FR_i=R_iF=0.
Consequently P_i−F is idempotent, supports R_i on both sides, commutes with
its actual prefix and every other stage, and has rank rank(P_i)−1. All
queries and the full endpoint are unchanged. This contradicts the minimum.

Thus every optimal coupling excludes this class of no-cost local retirement
immediately before a full stage. This statement concerns exactly the displayed
rank-one trim within one joint sector, with the same left and right prefix
eigenvalue and with both query products zero. It does not exclude arbitrary
native internal splits, paid modifications, or changes that mix output masks.

Both-sided idleness is essential to that trim argument. For the local control
P=I_2, R=E_01, F=E_00 and prefix −I_2, all projector and commutation conditions
hold and RF=0, but FR=R. Then (P−F)R=0 rather than R: left query support is
lost. This is a control of the local trimming implication, not a complete
root satisfying the theorem's full-query assumptions.

## Provenance and limitations

The canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`.
The coupled normal form, endpoint support implication, rank lemma, and prior
10q/no-equality result are retained from #6773 and its explicitly credited
predecessors: Ali Romman; thu-nmrc #6717; ToikY #6721/#6734; and Cinna Davis
and the original query/controller contributors. The analytic three-sector
capacity proof above is worker B's contribution. The rank 21 witness is
worker D's independent construction; the scalar rank 11 fixture is the lead's
construction. The independent B derivation was sealed before opening D's
files, with delivery timing recorded in DERIVATION-DRAFT.md.

This proof is over every field of characteristic !=2, subject to the inherited
normal-form contract. It is not a claim of human or proof-kernel review.
The exact checker audits fixtures and the ordered coordinate reductions;
the universal conclusion rests on the written argument, not finite sampling.

## Open next questions

1. Does another query count or a changed native boundary turn this sharp
   coefficient-space inventory into a profitable complete paid invoice?
   First price every output mask against the current strongest located root;
   rank 21 alone does not improve kappa.
2. Classify odd-q ceiling equality, including all possible endpoint and common
   sector dimensions. Start from the two capacity inequalities and integer
   slack; the even-q classification above does not settle this.
3. Identify a compact canonical block decomposition for every equality word,
   beyond its incidence inventory. The proof permits arbitrary internal
   coupling and does not claim tensor-factor classification.
