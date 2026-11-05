# A minimal shared forward dispatcher

## Model and inherited graph

Fix `a,b` in `{1,...,12}`. The four output labels are ordered `00,01,10,11`.
Use zxv's ordered-coin graph from [PR #6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072),
at `9011bf83e85ecd0443c789cf03259442f750877d`. This section states the graph
definition so the new result has no runtime dependency on that pending PR.
Its sampling law and expected-bit optimality are inherited, not new claims.

Put `D=169`, `L=156` and

\[
w=((13-a)(13-b),(13-a)b,a(13-b),ab),\qquad
r_{i,k}=2^k w_i\bmod D,\qquad
n_k=\frac{\sum_i r_{i,k}}D.
\]

Internal states are `(k,j)` with `0<=k<L`, `0<=j<n_k`, ordered by phase and
then node. The root is `(0,0)`. Let `d_i=floor(2 r_{i,k}/D)`. Form a list of
the output labels `i` with `d_i=1`, in increasing order. From `(k,j)`, coin
`u` selects child index `v=2j+u`. If `v<sum_i d_i`, return the label at
zero-based index `v` in that list. Otherwise go to
`((k+1) mod L, v-sum_i d_i)`. This is the subtraction rule
of #6072 written as an ordered list. Each pair has 312 internal states.

Take the disjoint union for all 144 ordered pairs, and identify only the four
matching output labels. Its internal states are `s=312*(12*(a-1)+b-1)+q`,
where `q` is the local phase/node index. There are 44,928 internal states and
four output states. Add absorbing self-loops at each output for the proof.
They are not stored as transition rows in the emitted table.

A state has observation `pending`, `00`, `01`, `10` or `11`. Equivalence means
equal observation after **every finite binary continuation**. Thus it preserves
the first stopping depth, output, and also nontermination for every infinite
tape. The configuration may be used to select an entry state. After entry,
all information governing transitions must be in the counted state. The model
does not grant a separate free parameter oracle, output relabelling or coin
reordering.

## Stable refinement is exact equivalence

Let `P_0` group states by their empty-word observation. Obtain `P_(k+1)` by
grouping states with the same observation and the same two `P_k` successor
classes. Induction on `k` proves that two states share a `P_k` class exactly
when all continuations of length at most `k` have equal observations.

These partitions refine monotonically. If two consecutive partitions have
the same number of classes, they are the same equivalence relation. Successor
classes then define a well-defined quotient. Induction on continuation length
proves equality of all finite observations in each quotient class. Conversely,
each pair separated during refinement already has a finite distinguishing
continuation. Thus the stable partition is exactly the required equivalence.
This is classical Moore state minimization, not a new minimization algorithm.

The complete finite refinement certificate gives these class counts, including
the four distinct output labels:

```text
depth     0   1   2    3     4     5      6      7      8      9     10
classes   5  15  56  282  1850  7426  14824  20274  22450  22486  22486
```

Consequently the minimal quotient has **22,482 internal states**. The verifier
checks every refinement using separately sorted signatures, every original
transition under the quotient map, all 144 entry pointers, output separation
and reachability of every state from the entries. It checks all 89,864 original
edges including the eight artificial absorbing edges. These are complete finite
checks, not a statistical sample.

All distinct residual behaviors have a distinguishing continuation of length
at most nine. Nine is needed: states 244 and 8149 share their depth-eight class
but separate at depth nine. The verifier extracts continuation `111111100`
and checks their different observations directly.

## Minimality in this model

Every original state is reachable from some entry by a finite coin prefix.
Suppose a deterministic forward dispatcher implements all 144 same finite-tape
functions. If two such prefixes reach the same counted internal state, their
remaining finite-tape observations must agree. Therefore distinct residual
classes cannot share that state. The 22,482 reachable pending classes require
at least 22,482 internal states. The quotient attains the bound.

This is a state minimum for these **fixed ordered-coin functions**, not a
minimum among all samplers with the same probability law, a ROM byte minimum,
or a lower bound for a machine with extra uncounted registers. Four terminal
codes are included in the encoding; a physical implementation need not retain
four halted controller states.

## Packed bank and exact preservation

Assign consecutive codes to the quotient's internal states and then its four
outputs. All 22,486 codes fit 15 bits. Each of the 22,482 internal states has
two stored targets. The transition payload therefore has

\[
\left\lceil\frac{2\cdot22482\cdot15}{8}\right\rceil=84308
\]

bytes. Lexicographically ordered entries for all 144 pairs use
`144*15/8=270` bytes. The complete packed bank payload is **84,578 bytes**.
The separate resident bank in #6072 uses `144*702=101088` bytes, with the
configuration selecting its table and every local entry equal to zero.
The shared payload saves **16,510 bytes**, including the new entry table.
These counts omit interpreter code and headers on both sides.

Every code is packed and independently unpacked in the replay. Since the
quotient preserves each original transition and preserves pending versus
output, induction on consumed coins preserves output and stopping depth on
every tape. Hence any inherited sampling law and expected number of draws
are unchanged. The separate 36,864 eight-coin tape comparisons are controls;
the complete homomorphism is what covers arbitrary tape length.

The quotient certificate does not require predecessor uniqueness. No reverse
transition or transfer of [PR #6102](https://github.com/CrocSwap/integer-mult-bounds/pull/6102)'s
cleanup contract follows. No bounded stopping time, fresh returned randomness,
physical lookup/selection tariff, complete caller or new kappa is proved.
