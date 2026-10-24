# A controller for reciprocal native responses

This note gives a complete ordered content controller for reciprocal
responses. It includes the original phase terminal. It also lists each
additional code operation and its required cut. Thus a native construction
can test a finite set of access conditions.

The current interior packet proves a forward response E and a backward
response E^T. It does not prove a backward response E^-1. This note does
not identify these two matrices. Its new construction has an explicit
reciprocal-response premise.

## 1. Required local contract

Let X and Y be arbitrary productive banks. Each bank has 112 fields with
the complete cover and payload coordinates. At stage s, let E_s be an
invertible operator on this whole bank space. In the original logical
frames, assume that the following native words are available:

    F_s(x,y) = (x, y + E_s x),
    B_s(x,y) = (x - E_s^-1 y, y).

Only F at even stages and B at odd stages is needed. Each native word must
restore every arbitrary helper and every private field according to its
own contract. Both words must have the original X-line/Y-hole input and
output frames. An inverse as an abstract matrix does not meet this premise.

The E_s in this note is the routed operator on the complete bank. Equality
of two local 112-by-112 coefficient matrices is not sufficient to give
E_s=E_t. The cover routes are part of this equality.

Code operations such as X<-E_t^-1 E_s X also need an implementation.
Sections 3 and 5 state their locations. No new child count is assigned to
an operation merely because the matrix is invertible.

## 2. The retained scalar controller

Use m pairs and 2m+1 local calls. First apply F0 to pair zero. For each
i=0,...,m-1, apply B_(2i+1) and then F_(2i+2) to pair i. If a next pair
exists, put a plus bridge before this F and a minus bridge after it:

    plus:  X_i += X_(i+1),  Y_(i+1) -= Y_i,
    minus: X_i -= X_(i+1),  Y_(i+1) += Y_i.

The next X bank reaches FULL at the preceding odd stage before the plus
bridge. It reaches the next even level before the minus bridge. Keep the
old idle native jobs at those sites.

After the local calls, keep the old idle tails. In descending i order,
apply the final full bridges

    X_i += X_(i-1),  Y_(i-1) -= Y_i.

For unit local responses, this word gives (-y_i,x_i) on every pair.
One proof uses the values before the final bridges. Put w_-1=0. The
completed X values obey w_i=-y_i-w_(i-1). The retired Y values are
x_i+x_(i+1), with x_m=0. The descending bridges give -y_i and x_i.

For m=4, the checker reads the pinned source recipe directly. It verifies
all 19 content events and all ten idle sites. It does not replace the
source recipe with an unrelated network.

## 3. A complete code placement for arbitrary E_s

Use the local responses from section 1. Insert the following operations
in the listed order. Every multiplication below acts on the left.

1. Before F0, apply Y0<-E0 Y0. After F0, apply X0<-E1^-1 X0.
2. Immediately before B1, apply Y0<-E0^-1 Y0.
3. After each B_s, where s=2i+1, apply
   X_i<-E_(s+1)^-1 E_s X_i.
4. At the first FULL cut of the next idle X bank, before the plus bridge,
   apply X_(i+1)<-E_(s+1)^-1 X_(i+1).
5. After the minus bridge at stage t=2i+2, apply
   X_(i+1)<-E_(t+1)^-1 E_t X_(i+1).
6. After the old idle tails and before the final descending bridges,
   apply X_i<-E_(2i+2) X_i for every pair.

Steps 4 and 5 are absent for the last pair. There are 4m+1 code factors.
The exact four-pair table is in CHECKS.json. The table separates a Y entry
stage from a completed X level.

### Ordered proof

Compare the changed state with the unit-response network in section 2.
After step 1, X0 carries code E1^-1 and Y0 carries code E0. Step 2 removes
the Y code. Thus B1 subtracts the correct ideal Y from the coded X.

Before B_s, the active X carries E_s^-1 and the active Y is plain. The
backward call gives E_s^-1(x-y), with Y unchanged. Step 3 changes this X
code to E_(s+1)^-1. Step 4 gives the same code to the next X bank. Both
parts of the plus bridge therefore act on the correct ideal contents.

At F_(s+1), its response cancels the X code. Its Y output is the ideal
sum, with no residual code. The X code remains E_(s+1)^-1. Both parts of
the minus bridge are valid. Step 5 changes the next X code to the inverse
required by its next backward call. This proves the invariant by induction.

Each retired X bank has code E_(2i+2)^-1. Step 6 removes all these codes
before the final bridges. Those bridges now act on plain ideal contents.
The complete preterminal endpoint is exactly

    X_i=-y_i,  Y_i=x_i.                              (1)

This proof treats all X and Y inputs as independent. No input, query, or
helper baseline is set to zero. The native helper contracts remain a
separate premise; the code factors act only on productive banks.

## 4. Common routed response: ten code factors for four pairs

If every global E_s is one common operator E, the two transition factors
in steps 3 and 5 are identities. The construction needs only 2m+2 code
factors. For four pairs these are:

| Code | Cut | Number |
| --- | --- | ---: |
| E on Y0 | Original I input before F0 | 1 |
| E^-1 on X0 | FULL after F0 | 1 |
| E^-1 on Y0 | Current I entrance before B1 | 1 |
| E^-1 on each next X | First FULL cuts, levels 1,3,5 | 3 |
| E on every X | Final FULL, before the three tail bridges | 4 |

After B1, all X banks that take part in a bridge carry E^-1 and all Y
banks are plain. This is why every original bridge can remain unchanged.
The final X decoding is at FULL. There is no Y-hole terminal decoding.

If E and E^-1 have admitted scalar/cover graph circuits at these cuts,
these factors need no additional native child. Their scalar work, views,
temporary fields, and precision are still part of the supplier bill.
The note does not supply such a circuit or bill for the actual E_s.

There is also a shorter one-pair identity. In chronological order, use

    F_E;
    B_(E^-1), then X<-E^-1 X;
    Y<-E^-1 Y, F_E, then X<-E^2 X.

Its output is (-y,x). The three code factors are at a completed X cut,
a current Y input, and a completed X cut. This is an ordered identity
for one common routed response. It does not authorize repeated native
calls on one stage, nor does it prove that repeated calls advance new axes.

## 5. The exact stage-access obligation

The general construction places most unresolved work on completed X.
Its first tests in the actual four-pair word are:

| Code | Required cut | Issue not removed by invertibility |
| --- | --- | --- |
| E1^-1 | X0 FULL at level0 | A future-stage code |
| E0^-1 | Y0 current entrance at stage1 | A past-stage Y code |
| E2^-1 E1 | X0 FULL after B1, level1 | A future-stage transition |
| E2^-1 | X1 first FULL, level1 | A future-stage preparation |
| E3^-1 E2 | X1 FULL after the minus bridge, level2 | A future-stage transition |
| E4^-1 E3; E4^-1 | Active and idle X at level3 | The next transition and preparation |
| E5^-1 E4 | Next X at level4 | A future-stage transition |
| E6^-1 E5; E6^-1 | Active and idle X at level5 | The next transition and preparation |
| E7^-1 E6 | Next X at level6 | A future-stage transition |
| E8^-1 E7 | Active X at level7 | The last transition |
| E2,E4,E6,E8 | Final FULL at level8 | Past/current code circuits |

This is a finite construction hypothesis. An implementation can use a
different circuit for a product; it need not execute its factors
separately. The table does not claim that these products are free.

The three-call calculation also gives an exact test for other wrappers.
Write the forward wrappers as pre-Y b0/post-X a0 and pre-Y b2/post-X a2.
Write the backward wrappers as pre-Y b1/post-X a1. For arbitrary
invertible a0,b0, closure to (-y,x) is equivalent to

    b1 = E1 a0 E0^-1,
    a1 = E2^-1 a0^-1,
    b2 = a0^-1 E1^-1,
    a2 = b0^-1 E0 E2.                              (2)

These equations follow by setting all four ordered endpoint blocks to
the target blocks. They show where a different boundary choice moves a
code. A future E2 in a1 cannot be dropped because the desired endpoint
has a dyadic inverse.

## 6. The physical terminal

Let Q be the diagonal intrinsic port-line operator and q=Q^-1. The raw
original input is W(x,y), with W=diag(Q,I). Before the old terminal, the
physical frames are F V, with V=diag(I,q). Suppress the common F in the
following equation. The retained terminal is

    A = [[0,Q^2],[-I,0]].

Let J0=[[0,-I],[I,0]]. Then the exact physical equation is

    A V J0 = W.                                   (3)

Consequently (1), together with the stated native phase contract, gives
the original FULL transform on the raw original inputs. No E crosses Q
in this proof. No encoded representation passes into an unchanged outer
twiddle or pointwise product.

In contrast, substitute a common E into the raw controller and omit the
codes in section 4. The logical endpoint is

    [[0,-E^-1],[E,0]].

After the old terminal, its code relative to the raw original inputs is

    diag(Q E Q^-1, E^-1).                          (4)

The first code is not E. It cannot be decoded by an untyped FULL scalar
E^-1 operation. The actual interior E has 564 nonzero entries, all off
the diagonal. All 112 port directions are distinct. For each nonzero
entry e_pr, a one-column Fourier character separates Q_p from Q_r.
Thus every nonzero entry supplies a nonzero commutator term with Q.
The checker verifies these 564 actual-source witnesses. It does not use
the older H-response obstruction as a substitute.

Leaving (4) as an outer representation needs a new contract. With an
unchanged twiddle T, the input and output codes must satisfy the exact
intertwining equation C_out T=T C_in. A common code must commute with T.
The pointwise product also needs its own encoded multiplication identity.
A matrix inverse alone proves neither condition. A changed terminal or
encoded outer operation can be useful, but its execution and price must
be supplied separately.

## 7. Complementary centre responses

The root's separate construction uses RK=14I and a centre projection P:

    E = I-K[I-(12/13)P]R,
    E^-1 = I-K[I-(12/13)(I-P)]R.

This is a reciprocal pair over a ring that contains 1/13. Its native
emission and centre-child bill belong to the root's separate packet.
The controller proof above applies if its stated global and cut
conditions hold. It does not require a dyadic-only coefficient ring.

For every such P, both centre eigenvalues differ from one. Hence

    im(I-E_s) = im(K_s).

A change of P cannot make two global E_s equal when their routed K_s
images differ. It changes the centre splitting, not the response image.
This observation does not rule out a paid transition or a changed native
response. It only prevents a false use of the common-E corollary.

## 8. Verification and remaining work

Run one process from the campaign directory:

    OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python3 -I -B lanes/encoded-controller/reciprocal-response-20261018/check_reciprocal_controller.py

Expected output:

    PASS_RECIPROCAL_RESPONSE_CONTROLLER

The checker uses free ordered invertible symbols. It checks every input
block for one through eight pairs, the common and distinct-stage cases,
the general three-call identity, the exact retained recipe, equation (3),
and equation (4). Mutation controls remove required codes and reverse a
transition order. It reads the actual interior matrix for the Q tests.
It does not import or run another lane's proof engine.

The induction proves the all-m statement. The finite checks do not replace
that proof. The complete supplier still needs reciprocal native words,
the stated cut circuits, owner admission, all scalar/native/precision
costs, and recursive hosting. No complete kappa improvement is claimed.
