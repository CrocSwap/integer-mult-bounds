# Sharp active-row counts for a mixed-width CRT tree

This contribution was produced by Nick Petalas. Apache-2.0.

## Interface and claim

Jerry Chen / CubeJerry's [PR7152](https://github.com/CrocSwap/integer-mult-bounds/pull/7152),
head `66adbede4bd4ab603ba3e0a7f6708403905b753c`, defines its schedule
in `research/crt-whole-tree-state/tree.py`, functions `commands` and
`WholeTree.step`. Take its activity predicate as the interface premise.
No numerical, ROM, physical-tape or traversal theorem is reproved here.

Let `d=2^h`, `h>=1`, and `ell>=2`. Each axis width is `ell-1` or `ell`.
Let `S` be the indices of the long axes, and `k=|S|`.
For each level `j=1,...,h`, and each aligned block of `2^j` axes, the
schedule visits rows `0,...,2ell-2`. Every row is active except that rows
`ell-1` and `ell` are inactive when the block's right half has no long axis.
An inactive row makes no provider invocation in that interface.

Write `F(S)` for the number of aligned right halves containing a mark in S.
Then the exact number of active invocations in one traversal is

```
A(S) = (2ell-3)(d-1) + 2F(S).
```

The sharp extrema at fixed k are

```
min F = max(0,k-1),
max F = sum_{j=1}^h min(k,2^(h-j)).
```

Both total bounds have explicit attaining placements described below.
One maximizing placement attains every levelwise upper bound simultaneously.
These are scoped all-size combinatorial statements, not
a complete CRT cost optimum or multiplication theorem.

## Exact invocation count

At level j there are `d/2^j` nodes. Summing over the levels gives `d-1`.
Each node contributes `2ell-3` ordinary rows. Its two exceptional rows
are active exactly when its right child subtree contains a marked leaf.
This proves the displayed formula for A, including ell=2 and k=0.
Reversing the command order changes none of these counts, since widths
are immutable at this boundary. A forward/reverse pair has count `2A`.

## Lower bound and a minimizing placement

If k=0, F=0. Suppose k>0. Prune every subtree with no marked leaf from the
complete binary tree, retaining the original root and paths to the marks.
In this rooted tree, let b be the number of vertices with two children,
and let u_L and u_R count vertices retaining only their left or right child.
The number of leaves is k. Counting edges both by outgoing degree and by
vertices minus one gives

```
2b + u_L + u_R = b + u_L + u_R + k - 1,
```

so `b=k-1`. A vertex contributes to F exactly when it retains a right child.
Consequently

```
F(S) = k-1 + u_R >= k-1.
```

This also characterizes equality: every occupied right child must have
an occupied left sibling. The prefix `S={0,...,k-1}` has that property at
every node, and therefore attains the lower bound for every k>0.
The empty prefix attains the k=0 boundary.

## Upper bound and one placement attaining every level

The aligned right halves at level j are disjoint and number `2^(h-j)`.
At most k of them can contain a mark. Thus their contribution is at most
`min(k,2^(h-j))`, proving the sum upper bound.

For an integer i in `[0,d)`, let `rev_h(i)` reverse its h binary digits,
including leading zeros. Choose

```
S_max = {d-1-rev_h(i) : 0 <= i < k}.
```

Reversal and complementation are permutations, so these are k distinct
valid leaves. Fix a level j and put `m=2^(h-j)`.
For each `i<m`, bit `h-j` of i is zero. In `d-1-rev_h(i)`, bit `j-1`
is therefore one, so this leaf lies in an aligned right half at level j.
Its upper `h-j` bits are the complemented reversal of the lower `h-j`
bits of i. As i ranges over `[0,m)`, these upper bits run through every
block index once. The first m leaves therefore hit every right half
exactly once. The first k leaves hit k different right halves if k<=m,
and already hit all m if k>m. Their contribution is exactly `min(k,m)`.
This argument applies to every j with the same S_max, proving attainment.

For a closed form when k>0, let `t=floor(log2 k)`. Splitting the sum at
the power-of-two capacities gives

```
max F = (h-t-1)k + 2^(t+1)-1.
```

The formula includes k=d, when it reduces to d-1. For k=0 use zero.

## Consequences and limits

At d=16, ell=3 and k=4, the sharp active-row extrema are 51 and 67.
The minimizing placement is `{0,1,2,3}`; the maximizing construction
gives `{15,7,11,3}`. The finite checker computes these values, rather than
treating them as handwritten evidence.

Each actual row can have a different cost. Width placement also changes
node precisions and coefficient geometry. This theorem therefore does not
minimize the complete `row_bound` sum, claim a physical saving from freely
reordering moduli, or remove the supplied-topology implementation obligation.
Axis/modulus transport, exact numerical providers, source preservation,
restoration, precision, binary lowering and the five selected framework
assumptions remain separate. No new kappa or selected-frontier change is claimed.

The binary-tree identities and bit reversal are elementary combinatorial
methods. The new contribution is their exact binding to this mixed-width
CRT activity predicate, the sharp placement extrema and the reproducer.
Credit CubeJerry #7152 for that predicate and caller boundary; Ali Romman
#5353/#5625, JoyboyBrian #5053/#5219/#5092/#5496/#6100, ToikY #4195,
Cinna Davis #4100, commdata2338 #5519 and the retained numerical, row-entry,
workspace and CRT lineage. No predecessor executable is imported.
