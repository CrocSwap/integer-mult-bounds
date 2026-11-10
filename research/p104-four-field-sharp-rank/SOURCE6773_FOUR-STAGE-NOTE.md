# Four-stage rank budget and coupled extreme-site incidence rigidity

Local mathematical work for @CubeJerry with substantial OpenAI Codex assistance.
Apache-2.0. Source-aware AI derivation, not human or proof-kernel review.

## Contract

K is a commutative field, char(K) != 2. On nq independent coordinates,
n>=4 even, q>=1, rank-q square-zero queries R_i obey
`(I-2R_n)...(I-2R_0)=-I`. A selected full stage is an idempotent P_i with
`P_i R_i=R_i P_i=R_i` and `[P_i,B_i]=0`, where
`B_i=(I-2R_i)...(I-2R_0)` is its ACTUAL chronological prefix. Selected
projectors commute pairwise. Ordinary changes of coefficient basis are allowed.
The inherited complete coupled normal form is
`U_i=e_i tensor I_q` for i<n, `U_n=(-1,1,...,-1,1)^T tensor I_q`,
`V_i=(sign(i-j))_j tensor I_q`; no internal q-by-q blocks are assumed to commute.

## Results established here

1. Any four selected stages have total rank at least **10q**. The placement
   bounds are11q with an even interior;21q/2 with exactly one endpoint and
   three odd interiors;32q/3 with four odd interiors. Thus equality10q
   requires both endpoints and two odd interiors.
2. For distinct odd interior sites i,j, write r_i=2q+e_i and r_j=2q+e_j.
   Then **2e_i+e_j>=2q and e_i+2e_j>=2q**, hence `r_i+r_j>=16q/3`.
3. At extreme sites0,1,n-1,n, total rank **10q forces the complete incidence
   profile**: q outputs each with ABCD,AB,CD,B,C, and (n-5)q empty outputs.
   Thus the active stage union has dimension5q; coupling does not improve
   this incidence profile at the aggregate minimum. At n=4, total10q is
   impossible for everyq. The integer total is at least10q+1; this does not
   yet prove a uniform11q bound.
4. The 10q four-stage bound is attained for every even n>=6, using an
   explicit extension of the credited #6398 six-field pattern (2,3,3,2),
   tensored by I_q. The source and extensions have been independently
   rebuilt and checked, including the full formal endpoint. This is an
   abstract coefficient-space word, not a new physical or paid supplier.

The aggregate bounds combine retained local tools, not a new leakage lemma
or caller mechanism. The new structural conclusion is the arbitrary-coupled
extreme-site incidence classification and its n4 consequence. The existing
scalar n6 attainment and its paid implementation remain Ali Romman's credit;
the all-even extension is a sharpness construction for this theorem.

## Local tools and four-stage aggregation

#6717 retains Ali Romman's rank lemma: if an idempotent contains column space A and
row space C, then `rank(P)>=dim(A)+dim(C)-rank(CA)`. It also supplies the
canonical prefix and, at odd i, the forced rank-2q projector
`E_i=(e_i h_i+a_i v_i) tensor I_q`. Here e_i is the standard basis column,
`a_i=sum_(j=0)^i (-1)^j e_j`, `h_i=sum_(j=0)^i e_j^T`, and
`tail_i=sum_(j=i+1)^(n-1) e_j^T`; in particular a_i starts with+1 and
has zeros after i. Every compatible prefix stage at i satisfies
`P_i E_i=E_i P_i=E_i`. Therefore `F_i=P_i-E_i` has rank e_i.

If Q is another compatible stage commuting with P_i, and its query has
factors U,V, let A=span(U,E_i U), C=span(V,V E_i). Whenever both dimensions
are2q and CA=0, commutation gives
`(I-Q)E_iU=-(I-Q)F_iU` and `VE_i(I-Q)=-VF_i(I-Q)`.
Each right side has rank<=e_i. Consequently A intersects im(Q) and C
intersects row(Q) in dimensions at least2q-e_i. Their pairing stayszero,
so `rank(Q)>=4q-2e_i`. This leakage step is retained from #6717 and independently
reviewed in #6721; #6734 applies it to odd pairs under weaker hypotheses.
Writing rank(Q)=2q+f gives

    2e_i+f >= 2q.                                     (L)

For an endpoint Q this closure holds when i is far: left endpoint0 if
i>=3; right endpointn if i<=n-3. Thus any far odd/endpoint pair has rank
sum>=5q, with equality only when odd rank=3q and endpoint rank=2q.
For two odd sites the same closure holds in BOTH orders. For i<j,
`E_i U_j=-a_i`, `V_j E_i=h_i`; for i>j,
`E_i U_j=e_i+a_i`, `V_j E_i=-(e_i^T+tail_i)`.
The two displayed columns and rows have rank2q with zero pairing in each
case. Here are field-independent minor certificates. For i<j, column rows
(j,0) give `diag(1,-1)` and row columns(i+1,0) give `[[1,1],[0,1]]`.
For i>j, column rows(j,j+1) give `[[1,-1],[0,1]]` and row columns(0,i)
give `[[1,-1],[0,-1]]`. Distinct odd sites ensure these coordinates exist.
The left-far endpoint uses column rows(0,1) and row columns(1,i), both
with determinant+1 or-1. The right-far endpoint uses rows/columns(0,i+1),
also with determinant+1 or-1. Tensoring these minors gives invertible
block minors over every allowed field. All four pairings vanish in each
case by the displayed contractions and even-length alternating sums.
Applying (L) in both directions proves item2. This is stronger than
#6717's commutator-only odd-pair5q consequence; #6734 retains only ONE prefix
and therefore cannot invoke both directed inequalities.

For four stages containing an even interior, #6717's even-site4q floor
plus its three-stage7q theorem gives11q. Otherwise there are two to four
odd interiors and zero to two endpoints. Four odds can be split into two
odd pairs. Three odds plus an endpoint can be split into a far odd/endpoint
pair and the remaining odd pair. Two odds i<j plus both endpoints can be
paired as (0,j) and (i,n): j>=3 and i<=n-3. Every pair costs at least5q.
This proves10q. In the last case equality forces endpoint ranks2q and odd
ranks3q by the equality statement after (L).

The stronger placement bounds follow from the directed inequalities. For
four odd sites, sum both directed inequalities for every pair to obtain
total extra rank at least8q/3, hence total rank at least32q/3. For three
odd sites and one endpoint, choose two far odd sites (at most one odd site
can be near that endpoint). Let a be the remaining odd extra rank, b,c the
two far extra ranks, and f the endpoint extra rank. Take weight1/4 on each
of `2a+b>=2q`, `2a+c>=2q`, and weight3/8 on each of
`2b+f>=2q`, `2c+f>=2q`. This gives
`a+b+c+3f/4>=5q/2`, hence total rank at least21q/2. These weights and
divisions concern real/integer ranks, not arithmetic in the ground field.

## Extreme-site equality forces the scalar incidence profile

Suppose the sites are0,1,n-1,n. Equality forces ranks(2q,3q,3q,2q), in that
order. Name stages A,B,C,D. E_1 supports both queries0 and1; E_(n-1)
supports both queriesn-1 andn. Therefore P_B supports R_0 and P_C supports
R_n. The commuting intersection projector
P_A P_B is compatible with R_0, so has rank>=2q=rank(P_A). Thus A<=B.
Likewise D<=C.

Every three selected query columns and rows are independently3q-dimensional:
extend them to any four query sites, whose ordered four-site sign Gram has
determinant1 before tensoring. Their principal three-site Gram has rank2q
(its scalar determinant is0 and it has a unit two-by-two minor).
Their union projector must therefore have
rank at least3q+3q-2q=4q. In particular B union D supports queries0,1,n,
so `rank(BD)<=rank(B)+rank(D)-4q=q`. But AD<=BD, and V_A U_D=-I passes
only through AD, so rank(AD)>=q. Consequently AD=BD has dimensionq.
Likewise AD=AC. Common diagonalization now leaves, besides the empty sector,
only sectors

    AB, CD, BC, B, C, ABCD.

Here ABCD has dimensionq. The endpoint ranks give AB and CD dimensionq
each. If BC has dimensionz, then the ranks of B,C give each B-only and
C-only sector dimensionq-z. Thus0<=z<=q. We provez=0 below.

Write the q-dimensional sectors as W=ABCD, X=AB, Z=CD, and write Y=BC.
Each query's U,V has support only in its stage. Pairings V_D U_A=I and
V_A U_D=-I make all W blocks of endpoint factors invertible. Use independent
coordinate bases in W,X,Z to normalize

    U_A,W=I, V_D,W=I, U_D,W=M, V_A,W=-M^-1,
    U_A,X=I, V_A,X=M^-1, U_D,Z=I, V_D,Z=-M,

where M is invertible. The X/Z normalizations follow from endpoint
square-zero equations. No internal matrices have been exchanged.

The ordered Gram equations now force

    U_B,W=I, U_B,X=I-M,
    V_B,W=-M^-1, V_B,X=I+M^-1,
    U_C,W=M, U_C,Z=I-M^-1,
    V_C,W=I, V_C,Z=-I-M.

Let H_B=Y direct-sum B-only and H_C=Y direct-sum C-only; each has
dimensionq. The square-zero equations give
`V_B,H_B U_B,H_B=M` and `V_C,H_C U_C,H_C=-M^-1`.
All four factors are squareq-by-q and invertible. Thus V_B,Y is injective
and U_C,Y is surjective, so their product has rankz. But the cross Gram
equation V_B U_C=-I has W contribution already equal to-I, so it requires
`V_B,Y U_C,Y=0`. Thereforez=0. The profile is exactly q each of
ABCD,AB,CD,B,C, plus (n-5)q empty outputs. No diagonalization of internal
q-by-q blocks was assumed. This proves item3 for arbitrary coupledq.

For n4, any total10q tuple must avoid the even interior and therefore has
exactly these four extreme sites. The required active union5q exceeds its
ambient4q, a contradiction.

## Attainment for every even n>=6

For canonical queries let

    S_n=[u_0,u_1,u_(n-1),u_n,k_2,...,k_(n-3)],
    k_j=e_j-e_(n-2).

This integer matrix is unimodular. Coordinates0,1,n-1 eliminate the first
three displayed columns. On remaining coordinates2,...,n-2, the sum of
the last query column's alternating entries is-1, while the k_j form the
standard difference basis of the sum-zero lattice. Consequently the
determinant is+1 or-1. All selected query rows annihilate every k_j.
Their Gram on the first four displayed columns is the same invertible
ordered four-site sign matrix, independently ofn. Thus in S_n coordinates
each of the four selected query matrices is its S_6-coordinate matrix
direct-summed withzero on n-6 coordinates.

Let P_i^(6), H_6 be the #6398 source projectors and input basis. Set

    P_i^(n)=S_n[(S_6^-1 P_i^(6) S_6) direct-sum 0_(n-6)]S_n^-1,
    H_n=S_n[(S_6^-1 H_6) direct-sum I_(n-6)].

Map source sites0,1,5,6 to0,1,n-1,n. All other sites are thin. This preserves
idempotence, compatibility, commuting stages and ranks. Prefix commutation
also transfers: B_0=I-2R_0, B_1=(I-2R_1)(I-2R_0),
B_(n-1)=-I-2R_n (because the complete query product is-I), and B_n=-I.
On the newly added coordinates these are scalar operators. Therefore the
four actual prefix identities follow from the exact n6 source identities.

H_n has the source six-coordinate stage masks plus n-6 empty masks. At
S=+1 the literal word is their diagonal stage product; at S=-1, move each
stage past its complete prefix to obtain the negative of that product.
The two characters give the formal identity because2 is invertible:

    S diag(ABCD,AB,CD,1,C,B,1,...,1).

Tensor every coefficient matrix with I_q. This proves attainment for every
allowed field, even n>=6, and q>=1. All nq inputs are independent; empty
stage masks do not initialize or discard their coordinates.

## Verified source attainment and limits

Source #6398: Ali Romman, head dee2663ba0918be86993fd9d63c8d64b020f4c83,
`research/mixed-projector-query-root/ROOT.json`, Git blob
b59f1ea89aca17f0a76131743c12f2c724421df8. Full sites0,1,5,6,
supports{0,1},{0,1,5},{0,2,4},{0,2}; ranks2,3,3,2. The six outputs are
`S diag(ABCD,AB,CD,1,C,B)`. All inputs remain independent and arbitrary.
`python3 -I -B check.py` uses fresh Fraction matrix operations, imports no
predecessor executable, and verifies all16 monomial matrices at BOTH central
characters, in addition to compatibility, idempotence, commuting projectors,
the literal query endpoint and actual prefixes. Six attaining fixtures
(n,q)=(6,1),(8,1),(10,1),(12,1),(6,2),(6,3) additionally check192 complete
formal coefficient matrices. The checker reconstructs420 zero-paired
closures at n=4,6,...,20; exhausts the stated integer sector constraints
for q1 through5; checks20 ordered coupled-block cases; and executes three
false-hypothesis controls plus two full-word omission controls. These finite checks corroborate the
written universal arguments; they do not prove every n/q by enumeration.

No complete cost model, kappa improvement, physical supplier, native phase,
ownership, all-size precision/compiler/analytic discharge or selected-frontier
change follows. q2 rank19 is ruled out at every evenn; q2 rank20 is ruled out
at n4. Rank21 at n4 remains open. The three-stage theorem and attainment are
not repeated as new work. No publication was performed.

## Open next questions

Can n4 coupled total10q+1 be attained, or does a quantitative version of the
four-sector obstruction force11q? First test q2 total21 with the true prefix
and full endpoint. Can a larger field root use the attained10q pattern with
a better complete paid invoice than existing roots? The rank budget alone
does not decide that supplier question.
