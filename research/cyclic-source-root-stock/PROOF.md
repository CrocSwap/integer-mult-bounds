# Exact root stock for a repeated cyclic source order

This is a scoped proof in the arbitrary-dirty binary connector model. The
finite replay corroborates it; the universal quantifiers come from this proof.

## The contract and the theorem

There are n immutable sources x_j, arbitrary dirty roots z_p, and one distinct
arbitrary dirty target y_m for every nonzero mask m in F2^n. The requested map is

    y_m += A_m(sum_j m_j B_j x_j).

All roots and sources must restore. Every B_j and A_m occurs exactly twice.
The source projection of the chronological word is fixed to

    w_n = 0,1,...,n-1,0,1,...,n-1.

Source/output ports may vary per occurrence. Arbitrarily many invertible
scalar binary root frames are permitted. For the lower bound their cost is
relaxed away. The upper construction emits and charges actual root XORs.
No target feedback, source mutation, extra child call, clean full row or
matrix-valued mixing inside a root is admitted. Every complete child preserves
other rows, restores its private scratch, and meets its required frame and
head-return contract. All data and root rows are excluded from child scratch.
Targets remain unobserved until the full batch completes. The A_m and B_j are
arbitrary compatible linear maps; singular, rectangular and noncommuting maps
are allowed. Special identities between fixed maps are outside generic necessity.

**Theorem.** The minimum number of roots for this fixed source order is

    k(n) = 1       for 1 <= n <= 3,
           2       for n = 4,
           n-1     for n >= 5.

More precisely, for n>=5, a binary reader-support code H containing the all-ones
vector is feasible if and only if codim(H)<=1. This does not determine the
minimum over other source orders. For example, conorholds's PR2182 already
attains n-3 roots for n>=4 using a different source word.

## The credited root-code reduction

We use Arham Tahir's PR2795 feasibility criterion, built on conorholds's
normalized source axes in PR2182 and Mason Hale's mandatory-mask method in
PR2282. This is a cited predecessor result, not a rechecked deliverable.
Here is the notation needed for this application.

In normalized coordinates, the two occurrences of source j inject the same
nonzero axis v_j. Otherwise the arbitrary independent source response would
remain in the restored roots. Let V have these columns and put H=rowspace(V).
Let q_t be the parity vector of source labels in the prefix through cut t, and
D(w)={q_s+q_t}. The two readouts of one A_m must have the same incoming-dirt
covector r, so their source mask is

    m = h AND d,   h=rV in H,   d=q_s+q_t in D(w).

The exact unrestricted-frame feasibility criterion is

    {h AND d : h in H, d in D(w)} = F2^n.                 (1)

The all-ones mask forces ones in H and ones in D(w). Also dim(H)<=k when there
are k roots. Sufficiency is constructive using paid binary frame changes.
The explicit upper program below realizes the particular code used here
without invoking the predecessor compiler.

## Repeated order gives exactly the cyclic arcs

Identify source positions with the cycle C_n. The parity of a contiguous
substring of w_n is a cyclic arc, the empty set, or the full set. A substring
longer than n has the same parity as the complementary shorter cyclic arc,
since a full traversal contributes ones. Every proper nonempty arc occurs as
a substring within the two traversals. Therefore D(w_n) consists exactly of
all cyclic arcs, including empty and full. For n>=1 its size is n(n-1)+2.

This derivation is specific to the repeated order. Arbitrary paired source
words do not have the same difference set.

## A rank-two quotient forces a missing mask

Suppose n>=5 and a feasible H has codimension at least two. Choose a surjective
linear map phi:F2^n -> F2^2 that vanishes on H. Write a_i=phi(e_i). Since
ones belongs to H,

    sum_i a_i=0.                                       (2)

If i,j are nonadjacent positions of C_n and a_i,a_j are distinct and nonzero,
consider m=ones+e_i+e_j. Any arc d containing the support of m is one of
ones, ones+e_i, ones+e_j. It cannot omit both isolated zero positions, because
the complement of an arc is an arc. Consequently any h with h AND d=m is one
of

    m, ones+e_i, ones+e_j.

Their images under phi are a_i+a_j, a_i and a_j, respectively. All three are
nonzero. None belongs to H, contradicting (1). Thus feasibility requires that
positions with distinct nonzero a_i values are adjacent in C_n.

There cannot be three different nonzero values among the a_i: representatives
of all three would form a triangle, absent from C_n for n>=4. Surjectivity
therefore forces exactly two distinct nonzero values a,b. They are linearly
independent over F2. By (2), each occurs an even number of times, hence at
least twice. Every a-position must be adjacent to every b-position. Selecting
two of each would give a K2,2 subgraph, a four-cycle. A cycle C_n for n>=5 has
no such subgraph. This contradiction proves codim(H)<=1 and k>=n-1.

The proof supplies an explicit missing mask for every rank-two quotient;
it is not an extrapolation from a finite source-count census.

## Every eligible hyperplane is feasible

Let H=ker(u dot -) with nonzero u and u dot ones=0. For any m in H, choose h=m
and d=ones. If m is outside H, then

    u dot (ones+m)=1.

Hence some position j with m_j=0 has u_j=1. Put h=m+e_j and d=ones+e_j.
Then h belongs to H, d is a cyclic arc, and h AND d=m. Thus every hyperplane
containing ones is feasible. Full space is feasible as well. Combined with
the obstruction, this proves the stated classification for n>=5.

## An explicit attaining dirty-root program

For n>=5, take k=n-1 roots and the code H={h:h_0=h_1}. Inject B0 and B1 at
root zero and inject B_j at root j-1 for j>=2. Repeat these exact ports in
the second source traversal. All roots restore after the two traversals.

For each nonzero m, choose the following h and two source cuts s,t.

- If m_0=m_1, take h=m and (s,t)=(0,n).
- Otherwise let j be the missing position in {0,1}; take h=m+e_j and
  (s,t)=(j+1,j+n).

In the first case q_s+q_t=ones. In the second it is ones+e_j. Both give
h AND (q_s+q_t)=m. The reader covector in the k roots is

    r=(h_0,h_2,h_3,...,h_(n-1)).

It is nonzero. Choose the first nonzero position p of r. To read A_m at
one of its cuts, execute z_p+=z_q for every other position q in support(r),
read A_m from z_p, then undo those XORs in reverse order. This restores the
entire root vector after each readout block. Both readouts see exactly the
same root-dirt combination and cancel it. The residual is precisely the
requested A_m applied to the B_j responses. All target blocks can coexist
at their designated source cuts because targets are distinct and every
readout block leaves the roots unchanged.

This argument retains A_m B_j in the correct order. It never commutes the
maps or assumes clean dirt. Root shears act only between equal-sized root
rows; arbitrary compatible source and output dimensions are allowed.

The exact child incidence is 2n B calls and 2(2^n-1) A calls. Each output
pays 4(wt(r)-1) root XORs across its two readouts. Summing over all nonzero
m gives

    sum_m wt(r) = 3*2^(n-2)+(n-2)*2^(n-1),
    root XOR count = (2n-5)*2^n+4.                       (3)

The first term counts masks having either low bit set. The other terms count
each independent higher bit. Every mask except zero contributes the minus
one in wt(r)-1. These are attaining counts for this program, not an optimal
transfer tariff.

Let c_Bj(p), c_Am(p), and c_X(p,q) be complete actual-port call prices, including
required access, updates, private-scratch cleanup, head returns and frames.
Let I pay admission, root reservation, scheduling and any initial layout;
P pay reusable preparation; D pay actual instruction storage, reads and
dispatch. With p_m the pivot above, the complete abstract bill is

    I+P+D + 2 sum_j c_Bj(port_j) + 2 sum_m c_Am(p_m)
          + 4 sum_m sum_(q in support(r_m), q!=p_m) c_X(p_m,q).

Reserve (n-1)L dirty root cells, all source/target rows, and each child's
separate private scratch. The instruction template is O(n*2^n) records and
is generated from the explicit mask/cut formulas. No control generation,
head movement, preparation or physical hosting cost is assigned zero.
An actual recursive caller and its profitability remain unknown.

## Small exceptions

At n<=3, every mask is a cyclic arc, so H=<ones> and one root suffice.
An active source and nonzero requested output require at least one root.
For n=4, D(w_4) omits exactly 0101 and 1010. A one-dimensional code containing
ones is <ones>, so it fails. The two-dimensional code spanned by 0101 and
1010 succeeds: all arc masks use h=ones; the two missing masks use h=m and
d=ones. This also explains why the no-four-cycle step must exclude n=4.
The verifier emits actual two-root readout blocks for this exception.

## Verification boundary

The written proof is uniform in n and positive row size. The replay checks
all 3,290 codes containing ones at n=1..7; every rank-two quotient killing
ones at n=5..9, totaling 85,818; cyclic-arc equality and literal dirty-root
programs at n=1..10; and all 236 single-operation omissions at n=5. The
n=5,6 quotient witnesses also undergo direct full kernel/difference checking.
These are original fixed-order instances, not predecessor minima replays.
The root program uses free response symbols and separate A_m image spaces,
so root dirt, target dirt and noncommutative map order remain explicit.

No physical implementation, complete recursive invoice, supplier admission,
new kappa, arbitrary-word root minimum or full multiplication theorem follows.
Independent human and formal proof-kernel review are unclaimed.
