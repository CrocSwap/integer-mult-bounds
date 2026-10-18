# Exact forest cost for arbitrary power-of-two parent weights

The fixed panel is `y <- y + C h`. Its 112 targets and 254 used helper
registers are distinct and start in frame zero. Every entry of C is an integer
multiple of 1/4 with numerator in `{-4,-3,-2,-1,0,1,2,3,4}`. These premises
are checked against the historical PR626 canonical word, emitted programs
and SPEC; helpers and target inputs may contain arbitrary dirt.

## Forest model and complete price

Each nonroot t chooses one distinct parent p(t) and coefficient
`lambda_t = s_t 2^e_t`, where `s_t` is ±1 and `e_t` is any integer. The parent
graph is acyclic. Different branches may share a parent, and a register may
be both child and parent. Define

```text
(T y)_t = y_t - lambda_t y_p(t)    at nonroots,
(T y)_t = y_t                    at roots.
```

Apply the nonroot additions in decreasing depth order: each parent still
contains its original input when read by a child. Inject every nonzero entry
of `T C`, then apply the basis operations in reverse order with opposite
coefficients. This realizes `T^-1(T y + T C h) = y + C h`. The forest makes T
unit triangular after a permutation, so inversion is valid over the rationals.
No helper is written during this forward panel. Its inverse transpose uses
the dual of each elementary gate in the same chronological order.

For a nonzero reduced dyadic `q = a / 2^d`, the fixed emitter charges

```text
p(q) = 3 + floor(log2 |a|) + popcount(|a|) + d;   p(0) = 0.
```

This includes private-work clearing, binary numerator construction, source
reads, denominator halvings, signed target accumulation and final clearing.
The independent checker executes these instructions and compares the count
with the pinned emitter function. Let `P(r) = sum_j p(r_j)`. Then

```text
root cost at t          = P(C_t),
parent edge cost at t   = P(C_t - lambda_t C_p(t)) + 2 p(lambda_t),
Delta(t,p,s,e)          = parent edge cost - P(C_t).
```

Both basis operations are included: `2 p(s 2^e) = 8 + 2 |e|` per component.
The complete forest cost is the sum of these child costs. Crucially, a child's
residual uses its parent's **original** row C_p, not its transformed row.
The cost at t therefore does not depend on the choice of p(t)'s parent. This
separability would fail for a different, sequentially transformed-row class.

## Finite core and infinite tails

The finite certificate computes every Delta for all ordered distinct target
rows, both signs and `e=-3,...,3`. Its nonunit minima per component are
467, 275, 71, 10, 145 and 278 at exponents -3, -2, -1, 1, 2 and 3 respectively.
Thus every nonunit core edge costs at least 10 more than its child's root.

The tail argument follows ToikY's PR909, with a different source matrix and
new CK anchors. Each quarter-grid residual entry on a tail can be written

```text
q_k = (a 2^k + b) / 2^D,    |a|, |b| <= 4,    k >= 3,
D = 2 for the positive tail; D = k+2 for the negative tail.
```

For `e=k`, take `a=-s C_p_quarters, b=C_t_quarters`. For `e=-k`, take
`a=C_t_quarters, b=-s C_p_quarters`. Before reduction, for nonzero numerator N,

```text
p(N/2^D) = 2 + bitlen(|N|) + popcount(|N|) + D - 2 min(v2(|N|),D).
```

If a and b are both nonzero, `|b| < 2^k` and
`v2(a 2^k+b)=v2(b)<=2`, so the reduction term is constant. With equal signs,
the high and low binary blocks do not overlap: bit length grows by one and
popcount stays fixed. With opposite signs, write
`|N| = (A-1)2^k + (2^k-B)`, where A=|a| and B=|b|. The low block has
`popcount(2^k-B)=k-popcount(B-1)`, so popcount increases by one at each step.
Bit length increases by one too: for A>1 it is `k+bitlen(A-1)`; for A=1 it
is k because `2^(k-1) <= 2^k-B < 2^k`. The boundary k=3, B=4 is included.
There is no zero numerator in this range. Zero a or b is handled directly.

The exact per-step coefficient cost slopes are:

| Entry case | e=+k | e=-k |
|---|---:|---:|
| a=b=0 | 0 | 0 |
| a=0, b!=0 | 0 | 1 |
| a!=0, b=0 | 1 | 0 |
| ab>0 | 1 | 2 |
| ab<0 | 2 | 3 |

All are nonnegative. Summing residual entries and adding the two basis gates
adds a further slope 2. Each complete edge penalty is therefore strictly
increasing along either tail, by at least two per component per exponent.
The strictly losing ±3 anchors cover every `|e|>=3`; the remaining nonunit
exponents ±1 and ±2 are in the finite core. Every signed nonunit power of two
is thus covered. The 162 finite coefficient-family checks and distant-exponent
literal replays corroborate this argument; they are not its universal proof.

## Edge deletion closes overlapping forests

Consider any allowed forest containing a nonunit edge from child t to parent
p. Remove that edge and make t a root. The result remains an acyclic rooted
forest. Every descendant of t retains the same parent coefficient and
original row in its residual; every other target is unchanged as well.
Only t's contribution changes, by exactly Delta(t,p,s,e), which is at least
10 per component. Preparation and restoration are re-ordered by the new
depths; their individual costs and the panel identity remain as above.

Repeat for all m nonunit edges. This produces a signed-unit forest and lowers
cost by at least 10 m. The argument covers simultaneous different exponents,
shared parents and arbitrary tree depth; it does not require disjoint pairs.
It excludes cyclic or multiple-parent bases, which are different classes.

## Attained exact floor

For unit weights the edge price is symmetric, since
`C_p - s C_t = -s(C_t - s C_p)` and `p(q)=p(-q)`. Add a superroot with an
edge of cost `P(C_t)` to each target. An allowed unit forest corresponds to
a spanning tree of this signed multigraph, and conversely, with the same
cost. This is PR816's credited reduction following the binary forest work.

The pinned PR816 tree has weight 16,364. The verifier recomputes every edge
price and checks all 12,544 fundamental-cycle inequalities: no graph edge is
cheaper than the maximum tree edge on its endpoint path. The spanning-tree
exchange argument proves the tree is minimum. A separate Prim implementation
finds the same cost using independently calculated dense/literal prices.
The retained recipe and its two arbitrary-input panel orientations are also
rechecked; the six-root witness is feasible in the original frame-zero class.

Any forest with m nonunit edges costs at least `16,364 + 10 m` per component.
The unit witness attains 16,364, so the minimum over **all signed power-of-two
parent forests** is exactly 16,364. The 10 m term is a valid uniform bound,
not a claim that the minimum with exactly m nonunit edges attains it.

This result concerns a scalar panel and its fixed separately cleared Horner
invoice. It supplies no new supplier, prefix saving or multiplication exponent.
It does not exclude other dyadic numerators, multiple-parent matrices,
helper-basis changes, inter-macro work sharing, different lowerings or folded
boundary operations. All-size compilation, physical realization and global
supplier admission remain outside this finite cost theorem.
