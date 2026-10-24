# Autonomous B outputs and the exact all-p path obstruction

Prepared by Cinna Davis with substantial OpenAI Codex assistance. Apache-2.0.

## 1. Consume the actual type B, with every Q power retained

Use the supplied monomial wrappers of PR4654. Its normalized type-B forward
operator, on arbitrary independent fields X,Y, is

    F_B = diag(D,QD) S_y(Q^-1) = [[D,0],[D,QD]],

where D has rank seven, Q rank one, and they act on disjoint axes. Apply
one pointwise complex subtraction Y -= X **after** this invocation. Then

    [[1,0],[-1,1]] F_B = diag(D,QD).

Thus its two original fields are independent productive Gaussian jobs of
ranks seven and eight. This uses no clean input, no copied productive source,
and no additional Gaussian call. It adds one ordinary complex ADD for each
of 56 B pairs, with the source monomial wrapper work retained. Scalar work
is finite nonrecursive work, not a zero-cost physical instruction.

The correct inverse-transpose identity is

    [[1,1],[0,1]] F_B^(-T) = diag(D^(-T),(QD)^(-T)).

The backward boundary is therefore an **output** addition X += Y. It must
follow the source's supplied exact backward monomial conjugations; replacing
Q^-1 by Q is not used. The verifier checks these Laurent identities without
finite-order relations, and rejects wrong signs and an omitted dual shear.
At every fiber width, evaluate the same identity on its completed D,Q blocks;
scalar ADDs commute with that evaluation. No tensor power of a sum is assumed.
This consumes the given typed operator theorem; it does not re-prove its
underlying 632-row/phase certificate.

There remain 56 active type-A pairs. Add 56 rank-seven and 56 rank-eight
independent helper jobs to PR4654's 408 existing helpers. The new target
profile is

    H = {3:2, 6:7, 7:103, 8:195, 9:213},

with 520 fields and rank mass 4246. The unchanged complete local paid profile is

    P = {1:2177, 2:424, 3:389, 4:147, 5:50, 8:8},

with rank mass 5094. Both orientations are recounted directly from the
pinned native program, including every center and paid climb. The excess
beyond the active transverse work is

    E = 5094 - 4246 - 2*56*7 = 64.

## 2. Exact complete rank surplus for every path size and support

Price the remaining A pairs with the ordinary minimal-cut paired-path
controller, any p>=1, any split, and any native/thin stage subset S. Let
n=|S|, v=56, b=7, t=1-C. Charge every one of 2p+1-n copied query shears
at v rank-one jobs, delete its lost helper outputs and stage multiplier,
and retain every main and idle contribution. The exact complete moment is

    F(C) = n(H_t-P_t+v) - v(2p+1) + 2v(1+bn)^t
           + sum_arm 2v[(1+b(k+e))^t - (bk)^t - e b^t].

There are p-1 arm steps. Here k is the number of selected preceding bits
and e the next even bit, exactly as in the native/thin path invoice. Empty
idle rank zero contributes zero. Setting t=1 telescopes the rank differences:

    F(0) = (v-E)n-v = -8n-56 < 0.

This is a universal formula, not extrapolation from finite cases. The
verifier independently enumerates every complete split/support invoice
through p=4 to check its implementation against the formula.

## 3. Exclude every concave exponent, not only rank mass

Normalize by b^t=7^t. The normalized local replacement is
L(C)=(H_t-P_t+v)/7^t. Its derivative has upper bound

    L'(C) <= -(2177-56)/7 * log(7)
             + 2 log(7/3) + 7 log(7/6)
             + 8*(8/7) log(8/7)
           < -1980/7 < 0.

For the negative rank-one contribution use (1/7)^t >= 1/7. Each positive
helper derivative below rank seven is at most H_r log(7/r). All helper
terms at ranks seven and above have nonpositive derivative. Paid ranks
2..7 also have nonpositive derivative; the eight paid rank-eight jobs
have derivative bounded above by 8*(8/7)log(8/7). This accounts for the
paid rank above the separator rather than dropping it.

The final coarse rational bound follows from log(7)>1, log(7/3)<2,
log(7/6)<1 and log(8/7)<1. The exact interval engine checks all four and
a stronger strict lower bound for -L'. These elementary bounds can also
be deduced from 2<e<3.

For an arm step with k>=1, the normalized derivative is negative because
x^t log(x) is increasing for x>=1. At k=0,e=1 it is also negative.
Only k=e=0 can contribute positively; its derivative is
(1/7)^t log(7). At most p-1 steps contribute this term, with multiplicity
2v. The normalized query term contributes
-v(2p+1)(1/7)^t log(7), more than cancelling all of them.
For n>=1 the normalized long-main term has negative derivative. For n=0
its positive derivative leaves exactly -v(1/7)^t log(7). Consequently
F(C)/7^(1-C) is strictly decreasing on 0<=C<1 for every p and S.

Starting from F(0)/7=-(8n+56)/7 gives

    F(C) <= -(8n+56) * 7^(-C) < 0,  0<=C<1.

No exact native/thin support search in this unchanged A-path family can
produce a contracting moment, for any pair count. This says nothing about
a mixed-type controller using B ports actively, a different word, a phase
schedule, a new center recipe, or a different output contract.

## 4. Constructive threshold and next step

For this interface the general rank formula is (v-E)n-v. A strict rank
surplus at any n requires E<v=56. The current E=64 must therefore fall by
at least nine integer rank units per full call. Saving only eight gives
F(0)=-56 for every n and does not cross the threshold. Saving nine would
only remove this rank obstruction; it would still need a positive exact
moment, a real operator construction, strictification, compiler and outer
transfer. No such cheaper center or improved K is supplied here.
