# Five rank-three calls for five A2 longest-element targets

This contribution was produced by Nick Petalas. Apache-2.0.

## Statement and model

Let K be any field and W=S3 have simple involutions s,t with sts=tst.
Write w0=sts. Fix any finite r>=5. Work coefficientwise in M_r(K[W]);
every role has arbitrary initial data. The required complete endpoint is

    T = diag([w0],[w0],[w0],[w0],[w0],1,...,1).

A paid call is F_u(A)=I+([u]-[e])A, where u is s or t and
1<=rank_K(A)<=3. Scalar GL_r(K) maps may be interleaved for free.
Couplings A need not be projectors or invertible. There are no other free
address operations, clean allocations, resets or discarded outputs.
Every spectator and every off-diagonal formal coefficient must be restored.

Let f on {0,1,2,3} be nonnegative, nondecreasing and discretely concave,
with f(0)=0. The cost of a paid call is f(rank A), the same for both labels.
Then the exact formal tariff is

    optimum = 5 f(3).

In particular, the minimum number of paid invocations is five, by taking
f(k)=1 for k>0. This is a formal call price, not a native or recursive bill.

## Attaining support schedule

Number productive roles 0 through 4, and let E_B be the diagonal projector
on B. Execute the following calls chronologically:

| Call | Label | Support B | Rank |
| --- | --- | --- | ---: |
| 1 | s | {0,1,2} | 3 |
| 2 | t | {0,1,4} | 3 |
| 3 | s | {0,3,4} | 3 |
| 4 | t | {2,3,4} | 3 |
| 5 | s | {1,2,3} | 3 |

On roles 0,1,2,3 the chronological subsequence is s,t,s. On role 4 it is
t,s,t. Both are palindromes equal to w0, so the rightmost-first convention
for multiplying column-vector operators gives the same endpoint. A call
acts as its group label on its support and as identity everywhere else.
All role matrices are diagonal. Thus the full group-algebra product is T,
including every zero off-diagonal and the identity on every spectator.
This is valid over every field, including characteristic two. It uses no
scalar mixing, dirty helper, preparation, restoration or extra call.
All five calls have rank three and cost 5 f(3).

## Matching lower bound

Use the all-field root-cut rank bound in zhaobenny's
[PR6817, proof section 2](../coxeter-capped-concave-tariff/PROOF.md),
building on David Arias's [PR2738](../coxeter-root-tariff/PROOF.md).
Its hypotheses are exactly the formal factors, scalar maps and complete
dirty endpoint above. The A2 simple roots form one root orbit, and w0
has three inversions. Five targets therefore force

    sum_j rank_K(A_j) >= 15.

This inequality is an inherited theorem, not re-proved or replayed here.
Its allowance of arbitrary scalar couplings and arbitrarily many restored
dirty spectators is needed for the lower bound, even though the attaining
word uses diagonal projectors and no spectators.

Concavity and f(0)=0 give f(k)>=k f(3)/3 for k=1,2,3. Consequently every
legal finite circuit has cost at least

    sum_j f(rank A_j) >= f(3)/3 sum_j rank A_j >= 5 f(3).

The support schedule attains this bound. No classification of circuits,
finite-field extrapolation or numerical root calculation is required.
For unit invocation prices, the same rank bound rules out four calls,
since four rank-three calls supply at most twelve rank units.

## Improvement and relation to prior work

The direct fixed partition into a three-role block and a two-role block
applies the three-letter word separately, costing 3 f(3)+3 f(2).
The displayed schedule saves exactly 3 f(2)-2 f(3), which is nonnegative
by concavity and positive for every strictly concave f. At f(k)=k/(k+1),
the exact price is 15/4 instead of 17/4, saving 1/2. This comparator is an
explicit construction, not a claimed optimum of any enlarged model.

Nick Petalas's [PR5083](../rank2-swap-batching/README.md) already gives
three longest-element targets at rank cap two using changing supports.
That idea and schedule are credited, not claimed again. The present new
instance has five targets, cap three and five full-rank calls. PR6817's
divisible theorem does not cover 3 not dividing 5, and its cap-two st
correction has a different target. ToikY's
[PR6821](../a2-st-all-cap-tariff/README.md) settles repeated st at every
cap; it does not settle repeated w0. We answer one instance of PR6817's
explicit nondivisible-target question. No claim of literature priority
for support scheduling, concavity or the root-cut method is made.

## Evidence and limits

The standalone verifier multiplies full signed coefficients in K[S3].
It also checks the full left regular action using a separate GL2(F2)
address representation. Finite gauges mix productive and dirty roles,
with explicit entrance and exit scalar maps. These are corroborating
examples; the displayed word and cited lower bound give the universal proof.
The verifier does not run any predecessor's scientific program.

Scalar coupling rank is not recursive child rank. Native realization,
the price of scalar maps, routing, storage, ownership, precision, stock,
hosting, compilation and the complete supplier invoice remain unknown.
No new kappa, supplier admission, selected-frontier change, independent
human review, formal-kernel acceptance or complete multiplication theorem
is claimed. The five selected framework assumptions remain.
