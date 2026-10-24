# Two global obstructions for controllers without idle work

Cinna Davis / 1337isnot1337, with substantial OpenAI Codex assistance.
Apache-2.0. These are written binary-algebra proofs, supported by finite checks;
there is no formal-kernel or independent human acceptance claim.

## Contract

Let n=2p main fields, Q a central involution, and work over
`F2[Q,D_1,...,D_f]/(Q^2-1)`. Every full native call has its **own independent**
commuting multiplier D_i and is

    (I+(D_i+1)P_i)(I+Q N_i),

with P_i a binary rank-two projector, N_i a rank-one nilpotent, and
`P_i N_i=N_i P_i=N_i`. A thin call is `I+Q N_i`. Arbitrary invertible binary
basis changes between calls are allowed and absorbed by conjugation. There
are no idle multipliers or repeated/specialized stage variables.

Success means constant invertible binary L,R give independent main jobs:

    L M R = diag(Q*m_1(D), ..., Q*m_n(D)),

where every m_j is a monomial. This is an algebraic prerequisite of the
retained native/query supplier model, not a native implementation theorem.

**Theorem A.** If every call is full, success requires at least 3p calls.
For a fixed local inventory, its target-minus-paid concave moment **per full
call** is no larger than that of a three-call unit. Thus it cannot admit a
larger raw saving than the disjoint three-call construction.

**Theorem B.** Every successful controller needs at least 2p+1 query-bearing
calls. If it uses exactly 2p+1 and p>=2, at most **two** calls can be full.
For the retained BIT inventory, its complete target-minus-paid moment is at
most **-15 for every exponent t in [0,1]**, so it cannot supply a recursive
saving. The binary theorem is not asserted for arbitrary complex words.

Thus both all-full controllers of arbitrary length and minimum-query mixed
controllers fail to supply the hoped-for large improvement by deleting idles.
The changed premise still open is a mixed controller with additional queries,
a changed target, dependent stage multipliers, or a different local family.

## Common tangent and projector identities

Set all D_i=1 and write Q=1+e with e^2=0. Normalize the derivative by the
invertible constant operator at e=0. A call's contribution is a conjugate

    R_i = u_i v_i^T,  v_i^T u_i=0,

of its nilpotent. The desired endpoint gives

    sum_i R_i = I_n.                                      (1)

For a full call, differentiate in its unique D_i and normalize on the right.
At D=1 its projector is conjugated by the later query calls. Since the desired
endpoint is independently diagonal, these normalized projectors E_i are
constant in Q, have rank two, commute pairwise, and satisfy

    E_i R_i = R_i E_i = R_i,
    [E_i, sum_{j>i} R_j] = 0.                             (2)

The second identity is the Q derivative of the conjugated projector. Each
R_j is written in the same final coordinate system. These are necessary
identities; no converse or free physical implementation is assumed.

## Proof of A: edge parity

Use the common binary output basis diagonalizing all full projectors E_i.
Each E_i selects two coordinates. Its R_i is therefore supported on that
coordinate pair and is one of the three nonzero rank-one nilpotents

    [0 1;0 0],  [0 0;1 0],  [1 1;1 1].

For any unordered coordinate pair, (1) requires zero off-diagonal sum.
Consequently the parity of the number of each of these three types is equal.
If that common parity is odd, there are at least three calls on the pair,
and the pair contributes one to both diagonal entries. Otherwise it contributes
zero to the diagonal. Every coordinate must meet an odd number of the former
pairs. There are at least n/2=p such pairs, and hence at least 3p calls.
Disjoint three-call swaps attain the call bound.

For the moment claim let f be the number of full calls, v the local port count,
b the transverse block rank, and t in (0,1). Each independent D_i occurs with
total degree two in the determinant, so `sum_j degree(m_j)=2f`. Jensen gives

    main target moment <= n*v*(1+2*b*f/n)^t.

Put a=f/p>=3. Dividing by f bounds this by
`(2v/a)*(1+b*a)^t`. Its derivative in a has the sign of
`(t-1)*b*a-1`, which is negative. The bound is therefore at most
`(2v/3)*(1+3b)^t`, exactly the per-call main moment of disjoint three-call
units. Helper targets and paid jobs are f copies of the same fixed local
inventory, so adding them preserves the comparison. This is a global bound
within the declared no-idle, all-full contract, not a bound on other families.

## Proof of B: the minimum-query simplex

If there are at most n rank-one terms in (1), rank already forces exactly n.
Writing U for their columns and V for their rows gives UV=I with both square.
Then VU=I, contradicting the zero diagonal `v_i^T u_i=0`. Thus there are
at least n+1 calls.

At exactly n+1, U has n+1 columns and V has n+1 rows. VU is a rank-n projector
of corank one. Write `VU=I+a b^T`. Its zero diagonal forces `a_i b_i=1` for
every i. Over F2, both a and b are the all-one vector. Hence

    v_i^T u_j = 0 if i=j, and 1 otherwise;
    sum_i u_i = 0,  sum_i v_i = 0.                        (3)

Every proper subset of at most n of either frame is independent.
Index the queries 0,...,n. For an interior position s, put

    k=n-s,  U_s=sum_{j>s}u_j,  V_s=sum_{j>s}v_j^T.

Commutation (2), applied to u_s and v_s^T, forces the image of E_s to contain
u_s,U_s and its row space to contain v_s^T,V_s. Both pairs are independent.
Their pairing matrix is `[0 k; k 0]` over F2. If k is even it is zero, so no
rank-two projector exists. If k is odd, the projector is uniquely

    E_s = u_s V_s + U_s v_s^T.                            (4)

In particular s must be odd, since n is even.

Two distinct interior positions s<t cannot both be full. Formula (4) gives

    E_s u_t=U_s,  E_t u_t=u_t,  E_t U_s=0.

Their commutator is nonzero on u_t.

If the initial position 0 and an interior s>1 were both full, their commuting
projectors would force the image of E_0 to be
`span(u_0,u_s+U_s)` and its row space to be
`span(v_0^T,v_s^T+V_s)`. These two independent pairs have **all four pairings
zero**, contradicting idempotence. Thus an initial full call can coexist with
an interior full call only at s=1.

Similarly, a terminal full call at n can coexist with an interior full call
only at s=n-1. Otherwise its forced image is `span(u_n,U_s)` and its forced
row space `span(v_n^T,V_s)`, again with all pairings zero.

For n>=4, the single possible interior full call cannot be both at 1 and n-1.
There are therefore at most two full calls: either both endpoints, or one
interior and one endpoint. For n=2 this exception disappears and the familiar
three-full-call controller is permitted, as it must be.

For the retained BIT profile, with L=2p+1 calls and f full calls, independent
stage degrees give first-order surplus

    2*p*111 - 63*f - 111*(L-f) = 48*f - 111.

At f<=2 this is at most -15. Here we can also exclude every interior concave
moment, rather than relying only on that first-order calculation. The BIT
helper profile is 439 jobs of rank 8, and its paid profile is
`{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}`. Let P(t) be its paid moment.
The n monomial degrees are nonnegative integers summing to 2f. Since n>=4
and f<=2, concavity maximizes their main moment by putting degree one on
2f fields and zero on the others. The full margin is consequently at most

    f B(t)-111,  B(t)=661*8^t-P(t)-111.

For every t in [0,1],

    B'(t)/8^t >= 661*log(8)-sum_{r=2}^7 P_r log(r) > 0.

The last strict inequality is the exact integer comparison
`8^661 > product_{r=2}^7 r^(P_r)`, checked without floating point.
Thus B(t)<=B(1)=48, and the margin is at most `48f-111<=-15`.

## Verification and unproved extensions

`global_check.py` checks the simplex pairings, forced-projector formulas,
noncommutators and endpoint degeneracies through 32 pairs. It independently
exhausts the two-coordinate nilpotents and their parity table, tests the n=2
exception, and checks a real n=4/f=2 factored word that attains the full-call
bound. The exact logarithmic-product inequality certifies the all-t BIT
rejection. The original complete n=4 search supports, but does not replace, the
written all-p proof.

The proof uses characteristic two and constant binary boundaries. It does not
reduce arbitrary complex dyadic operators modulo two. It also leaves mixed
words with more than 2p+1 calls open. Repeated or dependent D_i, nonmonomial
outputs, nonbinary boundaries and changed recursive suppliers are outside its
scope. No kappa improvement is claimed.
