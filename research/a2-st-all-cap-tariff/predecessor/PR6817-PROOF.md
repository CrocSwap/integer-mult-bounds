# Packed-rank bounds and sharp divisible batch tariffs

## Model and inherited input

Let K be any field and let W,S be a Coxeter system with finitely many simple
generators. W may be infinite. There are r finite scalar roles, all with
arbitrary input. Work coefficientwise in M_r(K[W]). A paid factor is

    F_s(A) = I + ([s]-[e]) A,   0 < rank_K(A) <= b.

A need not be a projector. This relaxation even permits singular factors.
Arbitrary interleaved GL_r(K) scalar maps are free. There are no free address
maps, resets, clean allocations or discarded outputs. The complete endpoint is

    T = diag([w_1], ..., [w_d], 1, ..., 1).

Every spectator returns its input and all off-diagonal entries vanish.
For each root orbit O, a call with simple root in O costs f_O(rank A).
Assume f_O on {0,...,b} is nonnegative, nondecreasing, f_O(0)=0, with
nonincreasing successive differences. Thus the theorem includes the sampled
values of every nondecreasing concave real function vanishing at zero.
Prices must be constant on root orbits, as in the predecessor.

We cite David Arias's PR2738, retained at the source pins in SOURCES.json,
for the root facts and root-cut method. Its PROOF.md sections 2 through 5
provide the geometric root action, finite inversion sets, root-orbit reduced
letter counts and the full formal coordinate construction. Those facts and
the rank inequality are inherited. Its binary rank-linear tariff does not
price the batches here. No predecessor executable is a dependency.

## 1. Integer packing lemma

For an integer M>=0 define

    P_(b,f)(M) = floor(M/b) f(b) + f(M mod b).

If 1<=k_j<=b and sum_j k_j>=M, then

    sum_j f(k_j) >= P_(b,f)(M).                         (1)

To prove it, include zero parts temporarily. If two parts satisfy
0<a<=c<b, transfer delta=min(a,b-c) from a to c. Each unit transferred
replaces f(a)-f(a-1) by f(c+1)-f(c), which is no larger by concavity.
The sum of f never increases; one part becomes zero or b. Repeat until
at most one part lies strictly between zero and b. The resulting cost is
P_(b,f)(sum k_j). Finally P_(b,f) is nondecreasing. Between multiples of b
this follows from monotonicity of f; the step to a multiple of b uses
f(b)>=f(b-1). This proves (1), including b=1 and zero demands.

This is a standard concave concentration argument, not a new optimization
principle. The contribution below applies it to the complete root-cut bill.

## 2. General orbitwise lower bound, over every field

Write i_O(w) for the number of positive roots in orbit O that w sends
negative, and M_O=sum_j i_O(w_j). Then every legal word costs at least

    sum_O P_(b,f_O)(M_O).                              (2)

Here is why the binary predecessor's root cuts apply over K. Use the
algebraic direct sum of K-basis vectors indexed by the real roots in O.
Positive and negative roots remain distinct labels in every characteristic.
The W action permutes these labels. Tensor with K^r. Let q_O(U) be the rank
of U's block from positive-root inputs to negative-root outputs. For two
operators the block identity

    (UV)_-+ = U_-+ V_++ + U_-- V_-+

gives q_O(UV)<=q_O(U)+q_O(V). Each block has finite rank: every formal
entry is a finite sum of group elements, each with finitely many inversions.
This also justifies the argument for infinite W without truncation.

A free scalar map has crossing rank zero. A simple s crosses just its own
positive simple root, so F_s(A) has crossing rank rank_K(A) in O(s), and
zero in the other orbits. The minus identity term does not cross the cut.
The target has crossing rank M_O. Consequently the sum of paid ranks in
orbit O is at least M_O. Apply (1) to that orbit. Sum its actual price
bound over the finitely many orbits to prove (2). No idempotence,
invertibility of paid factors, binary parity or faithful algebra
representation was used. Endpoint equality is required in the full algebra;
passing the root-action image alone does not establish it.

## 3. Sharp identical-target theorem

Suppose all d productive targets equal w and b divides d. With any finite
number of restored dirty spectators, the exact cost is

    (d/b) sum_O i_O(w) f_O(b).                         (3)

Indeed M_O=d i_O(w) is divisible by b, so (2) equals (3). For attainment,
partition the productive roles into d/b blocks of size b, and let E_B be
the coordinate projector of one block. For all g,h in W,

    [I+([g]-1)E_B] [I+([h]-1)E_B]
        = I+([gh]-1)E_B.

A reduced expression for w, applied on that block, uses rank-b legal
projectors, with i_O(w) calls in orbit O. Repeat on the disjoint blocks.
The formal product is exactly T; spectators are untouched. All calls,
including preparation or restoration if used, are subject to the same cap
and tariff. The upper construction needs neither. For power prices
f_O(k)=c_O k^theta, 0<theta<=1, (3) is

    d b^(theta-1) sum_O c_O i_O(w).

Thus batching saves against separate rank-one calls when the price is
strictly concave, and arbitrary dirty workspace cannot improve that saving
under this explicit rank cap. This is a formal tariff, not a recursive
invoice or native implementation result.

## 4. Nondivisible single-reflection case and bounds elsewhere

If w=s is a single simple generator, (2) is P_(b,f_O(s))(d), and batching
into floor(d/b) full blocks and one remainder attains it for every d.
For a general identical w without b|d, the same construction supplies only

    sum_O P_(b,f_O)(d i_O(w)) <= optimum
        <= sum_O i_O(w) P_(b,f_O)(d).                  (4)

These bounds can differ without indicating an open optimum. Nick Petalas's
retained `research/rank2-swap-batching/README.md` already gives the five-call
profile (2,2,1,2,2) for d=3, b=2 and the A2 longest element. It attains the
packed lower bound f(1)+4f(2). Its diagonal supports also work over every
field. We credit that schedule and its binary cap-two tariff; they are not
new here. The following different remainder target exhibits a genuine
chronological cost beyond the packed root bound.

## 5. Exact chronological remainder tariff for the A2 two-letter target

Let W=A2=S3 with simple generators s,t, let w=st, d=3 and b=2. In the
same all-field model with any finite restored dirty spectators, write
c1=f(1), c2=f(2), so 0<=c1<=c2<=2c1. The exact cost is

    2c1+2c2.                                          (5)

The root bound gives only 3c2. Formula (5) is strictly larger when c2<2c1.
For f(k)=k/(k+1), the exact cost is 7/3, above the root floor 2.

First normalize the free scalar maps by conjugation and augmentation, as
in the predecessor. This preserves each paid rank and leaves no final
scalar residue. Any three-call word has labels among the eight words on
s,t. Denote its scalar couplings A,B,C. Its coefficient at [st] is

    sss: 0                 tss: 0
    sst: (A+B-2AB)C         tst: (I-A)BC
    sts: AB(I-C)           tts: 0
    stt: A(B+C-2BC)         ttt: 0.

Each displayed coefficient has rank at most two, since it factors through
one of A,B,C. All shorter words also have [st] coefficient of rank at most
two; the only two-letter possibility is st with coefficient AB. But the
required coefficient is diag(I_3,0), of rank three. At least four calls
are necessary. This proof permits non-idempotent and singular couplings,
and does not specialize the scalar field or bound spectator count.

The inherited root rank floor gives q1+2q2>=6. Combine it with q1+q2>=4.
If q2<=2, the cost is at least
6c1-(2c1-c2)q2 >= 2c1+2c2. If q2=3, at least one rank-one call is needed
and 3c2+c1>=2c1+2c2. If q2>=4, the cost is at least
4c2>=2c1+2c2. These cases include zero prices. For attainment, apply s on
the first two roles and then the third, and do the same for t, in written
product order. The rank profile is (2,1,2,1) and the formal endpoint is
exactly diag([st],[st],[st],1,...,1). This proves (5).

This is a chronological remainder obstruction. It concerns st, not the
predecessor's longest element sts, for which changing the role supports
attains the packed bound. It does not classify other nondivisible targets.

The rank cap is part of the theorem. With d=b=2 and a single s,
f(k)=k/(k+1), the sharp cost is 2/3, whereas two rank-one calls cost 1.
The predecessor's rank-linear cost cannot be reused at this concave price.
If d=4 and a declared cap b=2 is silently relaxed to 4, one rank-four
call costs 4/5 rather than the capped optimum 4/3. Restored spectator count
and allowed paid rank are different resources. Formula (3) does not settle
an unbounded-rank primitive whose rank cap grows freely with workspace.

## Scope and credit

The new result is the packed orbitwise lower bound and its exact divisible
and single-reflection consequences under concave rank prices, together with
the exact chronological two-letter remainder tariff (5). Credit the
Coxeter root and rank-linear result to David Arias, retaining Adam Gall,
Ross Richardson, ywz65 and the eumemic/Ali Romman/Gareth Davidson model lineage
credited there. PR6613 by Nick Petalas changes the monomial reflection
alphabet and retains unit prices; it is related context, not a dependency.
The concentration argument and field-independent rank inequalities are
standard. No literature-priority, independent human review or proof-kernel
acceptance is claimed.

Produced with OpenAI GPT-6.1 Sol at high reasoning effort through Codex.
New work is Apache-2.0, prepared for Benny Zhao / zhaobenny.
