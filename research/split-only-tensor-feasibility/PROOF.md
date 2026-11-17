# Exact feasibility of tensoring with capped splitting

This scoped proof was produced by Nick Petalas. Apache-2.0.

Fix a real exponent 0<t<1. A finite nonempty paid multiset P consists of
positive integer ranks p, with repetitions counted. A finite nonempty target
multiset T is defined similarly. Write P_s=sum_(p in P) p^s and
T_s=sum_(r in T) r^s. Fix a positive integer cap base c. At tensor power v>=1,
each ordered v-tuple of original paid jobs supplies one job of rank equal to
the product of its ranks. These jobs remain distinct even when their ranks
coincide. Partition each such job separately into positive integer pieces
of rank at most J=c^v. Charge the sum of the pieces' t-powers. Targets stay
unchanged, so their tensor t-moment is T_t^v. There is no target completion.

## Theorem

Let S_v be the least possible total paid charge over these capped partitions.
Put A=P_t and D=P_1 c^(t-1). Then

```text
max(A^v,D^v) <= S_v <= A^v+D^v.
lim_(v->infinity) S_v^(1/v) = max(A,D).

There is a v>=1 with S_v<T_t^v
    if and only if max(P_t,P_1 c^(t-1))<T_t.
```

If a=max(A,D)/T_t<1, every positive integer v with 2a^v<1 works.
Thus the criterion is constructive. Equality in either necessary inequality
excludes a strict advantage at every power. Alternative partitions, irregular
piece sizes and more pieces cannot evade that conclusion in this model.

## One job

For positive integers R,J, write R=qJ+r with 0<=r<J. The least partition
charge is

```text
g_t(R,J)=q J^t+r^t, with 0^t=0.
```

If a partition has two pieces 0<a<=b<J, move mass from a to b until a
reaches zero or b reaches J. For 0<=x<=min(a,J-b), the function
(a-x)^t+(b+x)^t is nonincreasing. In the interior its derivative is
t((b+x)^(t-1)-(a-x)^(t-1))<=0, and continuity covers the endpoints.
Delete a zero piece. Each operation reduces the number of pieces strictly
between zero and J, so finitely many operations leave only full J-pieces
and at most one remainder. Their sum determines q and r uniquely. This
proves the minimum, including partitions with arbitrarily many pieces.

For any capped partition R=sum_i r_i, subadditivity and the cap give

```text
sum_i r_i^t >= R^t,
sum_i r_i^t >= sum_i r_i J^(t-1)=R J^(t-1).
```

Subadditivity follows from (a+b)^t<=a^t+b^t for nonnegative a,b.
For b>0 the derivative of (a+b)^t-a^t is nonpositive as a increases,
so the difference is at most b^t. Induction covers every finite partition.
The second inequality uses t-1<0 and 0<r_i<=J.

The quotient-and-remainder partition also gives the upper bound

```text
g_t(R,J)=q J^t+r^t <= R J^(t-1)+R^t.
```

Indeed qJ<=R and r<=R. These bounds apply when R<=J too. There is no
restriction to oversized jobs and no missing small-job term.

## Tensor sum and the strict boundary

Sum the two lower bounds separately over the ordered tensor jobs. Finite
distributivity gives sum R^t=P_t^v and sum R=P_1^v. Since J=c^v, their
two lower bounds are A^v and D^v. The same sums applied to the constructive
upper bound give A^v+D^v. Consequently

```text
max(A,D) <= S_v^(1/v) <= 2^(1/v) max(A,D).
```

The squeeze proves the limit. If S_v<T_t^v at any power, each lower bound
is strictly below T_t^v, so A<T_t and D<T_t. Conversely, if both are
strict, choose v with 2(max(A,D)/T_t)^v<1 and apply the upper bound. This
proves existence and the asserted uniform sufficient powers. If either
A>=T_t or D>=T_t, the corresponding lower bound excludes every power.
In particular, a limiting equality cannot be treated as a passing endpoint.

## Padding-free separation

Let k be the least original target rank. If 1<=c<k, every resulting paid
piece has rank at most c^v, whereas every tensor target has rank at least
k^v. Thus the same construction has strict paid/target separation. When
k>=2, a legal integer cap exists with a strict moment advantage at some
power exactly when

```text
P_t<T_t and P_1 (k-1)^(t-1)<T_t.
```

Necessity uses monotonicity in c and c<=k-1. Sufficiency chooses c=k-1
and applies the theorem. If k=1 no positive integer c<k exists. This is
only a criterion for this padding-free operation. Compilers that complete
targets or change the producer/consumer require a different criterion.

## Exact discriminating examples

All examples use t=1/2 and are abstract inventories, without claimed native
realizations.

* T={4,4,4}, P={9}. There is raw moment surplus 6-3=3 and rank-one
  surplus 12-9=3. At cap base c=2, D=9/sqrt(2)>6, so no tensor power
  works, even with arbitrary capped partitions. At c=3, D=3sqrt(3)<6
  and P_t=3<6. All targets exceed the cap base in both cases.
* T={81}, P={17}, c=4. The first power costs 4sqrt(4)+sqrt(1)=9,
  exactly the target charge. At power two the cost is
  18sqrt(16)+sqrt(1)=73<81. The criterion predicts existence, rather
  than a win at every positive power. Dropping the first remainder would
  falsely claim a first-power win of 8<9.
* T={16}, P={4,4}, c=9. A=T_t=4 and all jobs are unsplit, so S_v=4^v.
  T={64}, P={16}, c=4 instead has A=4<T_t=8 and D=T_t=8; full blocks
  give S_v=8^v. These distinguish the two equality obstructions.

## Relation to prior work and scope

zxv's PR4433 supplies the retained tensor splitting framework and sufficient
higher-moment paid-tail estimates. Cinna Davis's PR4412/4414/4416 supplies
chronological tensor product and completion; Jacob Alan Sussman supplies
the integer compiler. They retain all native, helper, controller, precision
and outer credit. None of those scientific programs is replayed here.

Nick Petalas's PR4832 and PR6390 optimize universal one-job upper-bound
coefficients; PR7135 concerns the distinct net splitting tax. Those results
are background, not premises of this proof. This theorem uses the elementary
two-sided bounds above to give an exact any-power feasibility criterion and
exponential rate for a fixed cap. It neither sharpens their coefficients
nor extends their optimizers to another exponent or target.

Concavity, finite products and the squeeze argument are classical. No global
literature-priority claim is made for those ingredients. The contribution
is this exact tensor feasibility screen and its strict-boundary application.

Only disjoint partitions within each original job are allowed. Cross-job
merging, target completion, additional charges, altered target credits and
physical interfaces require fresh arguments. This proof establishes no
native implementation, chronology/ownership admission, uniform compiler,
precision/tape bill, new kappa or complete multiplication theorem. All five
selected framework assumptions remain. Independent human and formal
proof-kernel review are unclaimed. The finite verifier corroborates this
written proof; it does not supply its all-real or all-power quantifiers.
