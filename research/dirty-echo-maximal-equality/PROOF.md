# The maximal equality interval for reserved-scratch dirty echoes

This scoped combinatorial proof is produced by Nick Petalas. The tree model,
echo semantics and universal lower bound are inherited from Alexander
Schwartzman's [PR784](https://github.com/CrocSwap/integer-mult-bounds/pull/784).
Gareth Davidson's [PR887](https://github.com/CrocSwap/integer-mult-bounds/pull/887)
formalizes the preceding sufficient equality interval. Neither predecessor
claims that interval is maximal. The contribution here is the exact maximal
interval and the complete recursive equality characterization.

## Model and theorem

An ordered tree has no unary nodes. A leaf has factor count n=1, completed
call count N=1 and scratch requirement S=0. A node with k>=2 children obeys

```
n = sum n_i,
N = 2 N_1 + 4 sum_(1<i<k) N_i + 2 N_k,
S = k-1 + max S_i.
```

These are the static all-arity echoes that reserve every parent connector
throughout every child invocation. Factors stay ordered. All signed leaf
invocations, including inverse and restoration calls, are counted. Unit leaf
prices, sequential child execution and a disjoint deeper scratch pool are
part of the model. The inherited echo identity is not reverified here.

For a nonnegative integer budget s, define

```
B_s(n) = 2^(s+1)n - 4^s,
a_s = ceil(2^(s+1)/3).
```

The predecessor proves capacity n<=2^s and N>=B_s(n) whenever S<=s.
The new theorem is

```
there exists a tree with S<=s, n leaves and N=B_s(n)
    if and only if a_s <= n <= 2^s.
```

In this interval the exact minimum completed call count is B_s(n). Outside
it, no feasible tree attains that affine bound. The statement includes s=0,
where the unique equality tree is one leaf, and s=1, where it is a binary
pair. Every equality tree uses the full available budget.

For example s=4,n=11 has exact minimum 96. Its ternary root has child leaf
counts (4,3,4), child calls (16,8,16) and child budgets (2,2,2). Thus the
root bill is 2*16+4*8+2*16=96, with four reserved scratch arrays. The prior
sufficient interval at s=4 started at n=12. PR784 already tabulates finite
optima; this example illustrates the new general theorem and is not claimed
as a newly discovered numerical minimum.

## Exact slack identity and all equality trees

Let delta_s(T)=N(T)-B_s(n(T)). For a leaf,

```
delta_s(leaf) = (2^s-1)^2.
```

For an internal root of arity k, put r=s-k+1, p=2^r, t=2^(k-1),
and w_1=w_k=2, with interior weights w_i=4. Every child has S_i<=r,
so r>=0. Direct substitution gives the exact identity

```
delta_s(T) = sum_i w_i delta_r(T_i)
           + 2p sum_i (t-w_i)(p-n_i)
           + p^2 (t-2)(t-2k+2).                  (1)
```

Indeed sum w_i=4k-4 and 2^s=pt. Expanding the right side cancels the
constant and linear terms to N(T)-2pt sum n_i+p^2 t^2.
All three terms on the right are nonnegative: the predecessor's bound gives
child slack, capacity gives n_i<=p, t>=w_i, and t>=2k-2 for k>=2.
For k>=4, t>2k-2 and t>2, so the final term is strictly positive.
This extracts equality conditions from the inherited inequality without
assuming the predecessor's sufficient construction is exhaustive.

Consequently every equality tree, and only such a tree, follows these rules
with the indicated contextual budget:

1. At s=0 it is a leaf. A leaf at any s>0 is not tight.
2. A binary root at s>=1 has two equality children at budget s-1.
3. A ternary root at s>=2 has three equality children at budget s-2,
   and its first and last children each have exactly 2^(s-2) leaves.
4. No node with arity at least four occurs.

For rule 3, the endpoint coefficients t-w_i equal 2, while the middle
coefficient is zero. This proves necessity and sufficiency directly in (1).
A tree of capacity 2^r at budget r is the unique perfect binary tree of
height r. To see this, a root of arity k>=3 has at most
k*2^(r-k+1)<2^r leaves; a binary root must have both children at capacity,
and induction finishes. Thus the endpoint subtrees in rule 3 are uniquely
specified. The classification concerns ordered shapes, not uniqueness of
all equality trees or of schedules in a larger reversible-program class.
Induction on these rules also gives S=s for every equality tree.

## Exact interval, necessity and constructive sufficiency

Let E_s be the set of equality leaf counts. The classification yields

```
E_0 = {1}, E_1 = {2},
E_s = (E_(s-1) + E_(s-1)) union (2^(s-1) + E_(s-2)), s>=2,       (2)
```

where the first plus is the set of pairwise sums and the second translates
a set. Both directions of (2) are constructive because children occupy
consecutive factor intervals. Endpoint perfect binary trees use no extra
space beyond their prescribed child budgets.

Inductively suppose E_j=[a_j,2^j] over the integers for smaller budgets.
The binary part of (2) is the whole interval
[2a_(s-1),2^s]. The ternary part is
[2^(s-1)+a_(s-2),3*2^(s-2)]. The lower ternary endpoint equals a_s,
since subtracting the integer 2^(s-1) from 2^(s+1)/3 leaves 2^(s-1)/3.
The lower binary endpoint is either a_s or a_s+1. For completeness,

```
2 ceil(2^s/3) = a_s + 1, if s is even,
2 ceil(2^s/3) = a_s,     if s is odd.
```

Also a_s<=3*2^(s-2), because the expression on the right is an integer
at least 2^(s+1)/3. Hence these two integer intervals overlap or are
adjacent, their union is exactly [a_s,2^s], and no smaller leaf count is
possible. This proves the claimed maximal interval for every s.

An explicit constructor uses a binary root whenever n>=2a_(s-1).
Set the first child size to max(a_(s-1),n-2^(s-1)) and the second to the
remaining size. Both lie in [a_(s-1),2^(s-1)]. If this test fails, use a
ternary root with endpoint sizes 2^(s-2) and middle size n-2^(s-1).
The interval argument places that middle size in E_(s-2). Repeat down
to s=0. The implementation uses a bounded iterative worklist.

## Scope

This is an all-size written theorem about a specified tree grammar, with
finite exact corroboration. It supplies no new multiplication exponent,
physical supplier, tape implementation, weighted-price optimum, precision
bound, nonlinear-gate statement or full multiplication theorem. Connector
reuse, clean checkpoints, changing the echo word, interleaved lifetimes,
borrowing ancestor arrays and arbitrary reversible programs are outside it.
The predecessor's unfavorable full-supplier bill is unchanged. The proof is
not checked by a formal kernel; the earlier Lean theorem has not been
extended or rerun. No predecessor audit is a deliverable of this package.
