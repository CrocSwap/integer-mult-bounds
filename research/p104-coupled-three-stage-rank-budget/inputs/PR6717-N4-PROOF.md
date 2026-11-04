# A sharp 7q stage-rank budget for five-query coupled roots

Prepared by **thu-nmrc with substantial OpenAI Codex assistance**.
Apache-2.0. This is an algebraic rank-budget result, with no native caller,
cost, kappa, or scientific-acceptance claim.

## 1. Statement and relation to the predecessor

Work over a commutative field K of characteristic different from two.
Let q>=1, and let R0,...,R4 be rank-q square-zero operators on a
4q-dimensional space E, with

    (I-2R4)(I-2R3)(I-2R2)(I-2R1)(I-2R0) = -I.

Write T_i=I-2R_i and B_i=T_i ... T0. At three distinct full sites take
idempotents P_i, of otherwise unrestricted ranks r_i, such that

    P_i R_i=R_i P_i=R_i,       [P_i,B_i]=0.

Suppose the three selected P_i commute pairwise. These are the normalized
projector and actual chronological-prefix conditions of the predecessor.
The rank of a full stage is allowed to exceed the native minimum 2q.

**Theorem. The sum of the three full-stage ranks is at least 7q. This
bound is attained for every q.** If site2 is selected, the sum is at
least8q instead.

A second statement used in the proof holds for every even n>=4: in an
n+1-query shortest tuple on nq fields, any such commuting full triple
that includes the endpoint-adjacent pair (0,1) or (n-1,n) has rank sum
at least7q. For n>4 this note does not prove the same bound for all other
triples.

Ali Romman's PR6398, section2 of
`mixed-projector-root-headroom/PROOF.md`, already gives the scalar q=1
local triangle obstruction and its all-even-n scope. For q=1, the
inequality7 follows from that result and integrality; it is not new here.
The source's image/row rank inequality and complete shortest-query normal
forms are also retained. The contribution here is the uniform **coupled
mixed-rank budget under the actual prefix conditions**, and the distinction
between that contract and compatibility alone. No scalar triangle,
canonical Gram, Mantel bound, or basic rank inequality is claimed as new.

The exact predecessor files, including all original notices, are copied
in `inputs/` and pinned by commit, Git blob and SHA256 in `SOURCES.json`.
There are no initialized or discarded main work fields in this contract.
An ordinary common normalization may mix all nq coordinates; the proof
does not assume that internal q-by-q coefficient blocks commute.

## 2. Retained Gram normal form and three elementary rank facts

Factor R_i=U_i V_i, with U_i of size nq by q, V_i of size q by nq,
and V_i U_i=0. The retained complete coupled normal form gives

    V_i U_j = sign(i-j) I_q,       i != j.

For clarity, its algebraic field scope uses only the following operations.
Concatenate U_i,V_i into U,V; put G=VU and let L be its strict block-lower
part. Chronological expansion gives

    product_i (I-2R_i) = I-2U(I+2L)^(-1)V.

The endpoint implies U(I+2L)^(-1)V=I. Thus `(I+2L)^(-1)VU` is a
rank-nq projector, and Z=I+2L-G has rankq and diagonal blocks I_q.
Write Z=AB with inner dimensionq. Each A_i B_i=I_q implies
B_i=A_i^(-1). Replacing U_i by U_i A_i and V_i by A_i^(-1)V_i leaves
R_i unchanged and gives the displayed Gram. No matrix blocks are
interchanged. This is predecessor material; this portion works in
characteristic different from two as well as characteristic zero.

Every even principal skew sign matrix has determinant one. A leading
2-by-2 Schur elimination leaves the smaller matrix unchanged, so this
follows by induction. Consequently every n selected U blocks are
independent, and every n selected V blocks are independent. For n>=4,
any selected triple has

    rank(U_a,U_b,U_c) = rank((V_a;V_b;V_c)) = 3q,
    rank((V_a;V_b;V_c)(U_a,U_b,U_c)) = 2q.             (1)

Compatibility of P_i implies P_i U_i=U_i and V_i P_i=V_i.
Let E_i=im(P_i). We will use these three rank facts.

**Single compatibility.** Any idempotent P compatible with a rank-q
square-zero R=UV has rank at least2q. Indeed U has image dimensionq,
V restricted to im(P) has rankq, and im(U) lies in its kernel. More
generally, the predecessor's image/row inequality is

    rank(P) >= a+c-g,                                  (2)

when P contains a column space of dimensiona, supports a row space of
dimensionc, and their pairing has rankg. This follows by counting the
kernel of that row map on im(P).

**Cross intersection.** If P_i,P_j commute, their product projects onto
E_i intersect E_j. The invertible cross Gram block V_i U_j factors through
this product, so

    dim(E_i intersect E_j) >= q.                       (3)

If both P_i,P_j are compatible with the *same* rank-q square-zero query,
their product is also compatible with that query; single compatibility
then improves the right-hand side of (3) to2q.

**Three-image dimension.** Put W=E_a+E_b+E_c. The three U blocks in (1)
map into W with rank3q. The three V blocks restrict to W with rank3q:
they vanish on the common zero eigenspace, which is a complement to W
because the selected projectors commute. Their product has rank2q.
The rank inequality for their product therefore gives

    dimW >= 3q+3q-2q = 4q.                             (4)

These facts apply to arbitrary coupled blocks, not only tensor products
of scalar choices.

## 3. Prefix conditions double one intersection

Here is the key promotion from compatibility to an actual prefix condition.
Suppose P is compatible with R_a and commutes with another query R_b.
The commutation preserves im(U_b), so P U_b=U_b C for a q-by-q map C.
Since V_a P=V_a and V_a U_b is invertible,

    V_a U_b C = V_a P U_b = V_a U_b

implies C=I. The equality P U_b V_b=U_b V_b P and injectivity of U_b
then give V_b P=V_b. Thus **P is compatible with R_b as well**.

For the first adjacent pair, compatibility makes P1 commute with T1.
The condition [P1,B1=T1 T0]=0 therefore implies [P1,T0]=0 and hence
[P1,R0]=0. The preceding argument shows that P1 is compatible with R0.
Since P0 is already compatible with R0, and P0,P1 commute,

    dim(E0 intersect E1) >= 2q.                        (5)

No rank-minimality or nesting assumption was used. In particular the
argument remains valid if all three ranks exceed2q by small amounts.

At the other end, B_(n-1)=-T_n^(-1). The condition
[P_(n-1),B_(n-1)]=0 gives [P_(n-1),R_n]=0. The same argument shows
that P_(n-1) is compatible with R_n, so

    dim(E_(n-1) intersect E_n) >= 2q.                  (6)

This is where the chronological prefix hypothesis is essential.

## 4. Boundary-pair rank budget

Consider a selected triple including one of the boundary pairs in (5)
or (6), and call its members a,b,c with
dim(E_a intersect E_b)>=2q. Equation (3) gives
dim(E_a intersect E_c)>=q. Hence

    dim(E_a+E_b) <= r_a+r_b-2q,
    dimW <= r_a+r_b+r_c-3q.

Together with (4), this proves

    r_a+r_b+r_c >= 7q.                                (7)

Equivalently, in the simultaneous zero/one eigenspace decomposition let
c be the common intersection dimension, a_ij the pair-only dimensions,
and b_i the single-only dimensions. If R is the rank sum, then

    R-dimW = t_ab+t_ac+a_bc,
    t_ab>=2q,       t_ac>=q,       a_bc>=0.

This dimension identity gives the same bound. It does not replace an
arbitrary subspace lattice by a distributive one; the commuting
projectors supply that decomposition.

## 5. The middle site on four blocks costs at least4q

Use the retained canonical n=4 scalar tuple, where

    u2=e2,             v2=(1,1,0,-1).

Direct multiplication gives

    B2 = [ 1  2  2  2]
         [-2 -3 -2 -2]
         [ 2  2  1  2]
         [ 0  0  0  1],
    B2 u2=(2,-2,1,0),     v2 B2=(-1,-1,0,-1).

In characteristic different from two, the invariant column and row spaces
contain respectively

    A=span(e2, (1,-1,0,0)),
    C=span((1,1,0,0), (0,0,0,1)).

Both have dimension2 and C A=0. At coupled widthq they are tensored
with I_q; their dimensions are2q,2q and their pairing remains zero.
Any P2 compatible with R2 and commuting with B2 contains A and supports
C. Equation (2) gives rank(P2)>=4q. The argument is invariant under
the ordinary common basis that produced the canonical tuple.

If the selected triple includes site2, the other two ranks are at least
2q each, so its sum is at least8q. Otherwise its three sites lie in
{0,1,3,4}. Every three-element subset of this set contains (0,1) or
(3,4), so (7) applies. This proves the theorem at **every positive q**.
No enumeration of bounded coefficients, matrix widths, or query tuples
establishes the universal statement.

## 6. Sharpness with a literal independent-stage endpoint

The following q=1 control supplies equality and an exact formal endpoint.
In the canonical n=4 tuple write

    u_i=e_i (i=0,1,2,3),       u4=(-1,1,-1,1),
    (v_i)_j=sign(i-j).

Conjugate the five queries by the unimodular ordinary matrix

    H = [1 1 1 0]
        [1 2 2 1]
        [0 1 2 1]
        [0 0 0 1].

At sites0,1,4 use diagonal projectors with masks3,7,9:

    P0=diag(1,1,0,0),
    P1=diag(1,1,1,0),
    P4=diag(1,0,0,1).

The selected columns and rows are

    u0=(1,1,0,0),     v0=(1,-1,0,0),
    u1=(1,2,1,0),     v1=(1,0,-1,0),
    u4=(-1,0,0,1),    v4=(1,0,0,1).

They have the required canonical cross Gram and independent triple
columns and rows. The projectors commute, have ranks(2,3,2), and are
compatible. P1 contains both query planes R0,R1, so it commutes with
B1. The two endpoint prefix conditions are automatic. The full
five-query product is -I4 by conjugation of the canonical tuple.

Make sites2,3 thin. Give the full sites independent central stage
variables A,B,C and act there by

    (I+(D_i-1)P_i)(I+(S-1)R_i),       S^2=I.

At S=+1 the literal chronological word is
diag(ABC,AB,B,C); at S=-1 it is its negative. Because2 is invertible,
these two character equalities establish the full formal S^2=I identity

    S diag(ABC,AB,B,C).

Tensoring every coefficient-space matrix with I_q gives ranks
(2q,3q,2q), all prefix conditions, and the same stage masks at everyq.
This is an explicit algebraic attainment control, not a priced physical
native module. It earns no central phase, helper return, or caller credit
by itself. No scalar attainment mechanism is claimed as new.

## 7. Why compatibility alone gives the wrong answer

The included `inputs/LOCAL13.json` is an exact rational n=4,q=2 shortest
tuple with three commuting compatible projectors of ranks(4,4,5).
It has eight independent input coordinates, both selected U/V ranks6,
all five square-zero query ranks2, and product-I8. Its rank sum13 is
below7q=14. All these facts are replayed by the small verifier.

Its prefix commutator ranks are(0,4,4), so it does not satisfy the
theorem's prefix hypothesis. This necessary control prevents treating a
local Gram/compatibility construction as an actual independent-stage
endpoint. The predecessor's scalar barrier and the exact rank-2q
triangle extension remain unchanged. The rank13 tuple is used here only
as a failed-prefix control; it supplies no native or price improvement.

## 8. Verification and limits

Run `python3.12 -I -B verify.py` and
`python3.12 -I -B -O verify.py`. The default is read-only; `--write`
authors RESULT.json. The standard-library checker authenticates every
included predecessor source and notice, checks the formal dimension
identity, rebuilds the middle-site rank spaces and sharp family at
q=1,2,3,4, multiplies the literal multivariate stage words at both central
characters, and independently replays the rank13 failed-prefix tuple.
Deleting the sharp middle's charged extra direction breaks an actual
compatibility equation. The uniform theorem follows from the proof,
not these finite controls.

The hypotheses are nq independent fields, exactly n+1 rank-q square-zero
queries, ordinary constant normalization over a commutative field,
projector compatibility, selected pairwise commutation, and actual
chronological prefix commutation. Extra query calls, initialized or
discarded inputs, other query ranks, stage-dependent scalar maps and
omitting S on selected outputs change the contract. Arbitrary separated
frame commutation before normalization is not the stated hypothesis.

The note does not prove a general all-n rank-sum bound for triples away
from the boundary, the open general noncommuting-projector thin bound,
a physical phase identity, a native supplier, a full invoice, a kappa
increment, or an integer-multiplication theorem. It does not discharge
the repository's inherited framework assumptions. These are AI-assisted
author checks and an independently discussed proof, not human review or
proof-kernel verification.

Ali Romman's scalar obstruction, image/row rank method and coupled
normal form retain their original credit, including Cinna Davis's
query/controller lineage and all retained contributors. All copied
original notices remain unchanged. New uniform prefix-conditioned
mixed-rank argument and bounded controls: thu-nmrc with substantial
OpenAI Codex assistance. Apache-2.0.
