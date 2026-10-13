# Several reusable clean checkpoints

This extends FanPUYen's clean-root interface
([PR714](https://github.com/CrocSwap/integer-mult-bounds/pull/714),
`efad8a40094ab453c0525efef0b0eff2a5d8b850`) and
nightangelflowerwin-ops' reusable single-clean interface
([PR788](https://github.com/CrocSwap/integer-mult-bounds/pull/788),
`ff8251519e009a01ede6b27e3f5af703eaa70132`). The extension permits another
clean connector while a clean ancestor remains reserved. It changes the
initial-space contract; it supplies no new multiplication exponent.

## Contract and restoration

Payloads form an abelian group. A leaf is a deterministic, zero-preserving
increment `f_j`: its positive instruction adds `f_j(source)` to the target;
its negative instruction subtracts the identical value. Neither changes
the source nor reads the target to compute that value. Parameters are
immutable. Source, target and scratch arrays are pairwise distinct.

There are `s` scratch arrays: `c` initially zero, `s-c` arbitrary. Every
invocation restores its entire scratch pool. A connector stays reserved
throughout its node invocation; descendants cannot borrow it, an ancestor
connector, or any other ancestor role. The remaining pool is available to
each child sequentially, including its remaining clean arrays.

Write `B` for the left child's increment and `A` for the right child's
increment, with their shared initial scratch state held fixed. A dirty
connector `z`, initially `z0`, implements

```text
z += B(source)
target += A(z)
z -= B(source)
target -= A(z)
```

Its net increment is `A(z0+B(source))-A(z0)`. The connector returns to
`z0`; both child calls restore the rest of the pool. The increment is
independent of the initial target and vanishes at source zero.

A clean connector starts at zero. Omit the fourth call because `A(0)=0`.
The resulting increment is `A(B(source))`, and the connector returns to
zero. Its children receive `s-1` arrays with `c-1` clean. A dirty connector
instead leaves `c` clean arrays in the child pool. Every child restores
these arrays to zero before its sibling uses them. This proves reuse even
when another clean array remains reserved above them.

Induction proves restoration, target independence and zero preservation
for arbitrary deterministic leaves satisfying the contract. Reversing the
entire instruction sequence and negating each sign gives its exact inverse.
This reverses instruction order, not merely signs in the forward order.

For linear leaves the dirty increment also equals `A(B(source))`.
Consequently every legal tree realizes the ordered product
`f_(n-1) ... f_1 f_0`, with no commutation assumption. For nonlinear or
rounded leaves, increments may depend on the tree and dirty scratch.
Restoration still holds; equality between different trees does not follow.
On a fixed grid, addition/subtraction must be exact and free of overflow.
The negative leaf subtracts the same rounded increment; separately rounding
a negative expression is insufficient if rounding is asymmetric.

## Exact optimization within the stated class

Let `V(I,s,c)` be the minimum signed-leaf charge for a nonempty contiguous
factor interval `I`. Each factor has positive integer price `t_j`, bounding
both signs at one common precision. A singleton costs `t_j`, including when
`s=0`. Invalid resources and impossible nonleaf states cost infinity.
For every nonempty contiguous split `I=L R`, consider

```text
dirty connector, s > c:  2 V(L,s-1,c)   + 2 V(R,s-1,c)
clean connector, c > 0:  2 V(L,s-1,c-1) +   V(R,s-1,c-1).
```

`V` is their minimum. A legal decorated tree has one of these root choices
and two legal children. Conversely each finite candidate composes legal
children under the restoration contract. Induction on interval length
therefore proves exact optimality over ordered binary trees with reserved
connectors. It does not optimize arbitrary reversible programs, higher
arities, or schedules that borrow live ancestor arrays.

Equivalently, every root-to-leaf path has at most `c` clean nodes and at
most `s-c` dirty nodes. Both constraints matter: depth at most `s` and at
most `c` clean nodes alone permit too many dirty reservations. A leaf's
multiplicity is the product of its edge multipliers: two on every left
edge, two on a dirty right edge, one on a clean right edge. This gives a
separate decorated-tree enumeration criterion.

No tree has more than `2^s` leaves. Conversely every count from one through
`2^s` is feasible: take a full-depth binary tree, label `c` levels clean
and the others dirty, then prune sibling subtrees until the desired count
remains. Hence `n <= 2^s` is the exact feasibility condition.

At fixed total scratch, extra clean arrays cannot increase `V`. For `c<s`,
turn a legal `(s,c)` tree into an `(s,c+1)` tree by recoloring the first dirty node on
each path clean. These first nodes form an antichain. Each affected path
loses one dirty reservation and gains one clean reservation, meeting the
new capacities; unaffected paths had no dirty reservations. Recoloring
only reduces right-edge multipliers. This also explains why treating a
known-clean connector as dirty cannot improve the optimum: its fourth
child call has zero increment and positive cost.

### Full-capacity theorem

For `n=2^s` unit-price leaves,

```text
V([0,n),s,c) = 4^(s-c) * 3^c.
```

Depth at most `s` forces a perfect binary tree, so both root children have
`2^(s-1)` leaves. Induction starts at `s=0`, with cost one. A dirty root
multiplies the child value by four; a clean root multiplies it by three.
Both choices give the displayed expression. Thus every feasible decoration
has that charge, and changing one dirty array to clean gives exactly a
three-quarter factor at full capacity. This is an all-size class theorem,
not an inference from a finite table.

### Seed-selected comparison

For 50 unit-price factors and six scratch arrays, the exact minima for
zero, one and two initially clean arrays are respectively
`2752`, `1728` and `1248`. The frozen one-clean witness executes
`1728` leaves, `575` dirty nodes and `1` clean node. The two-clean witness
executes `1248` leaves, `243` dirty nodes and `259` clean nodes.

With a common complete leaf price `t` and per-invocation internal prices
`g_D,g_C`, the two-clean witness saves

```text
480*t + 332*g_D - 258*g_C
```

before additional provisioning, admission, routing and preparation costs.
For equal internal prices `g`, this becomes `480*t+74*g`. These are exact
counts for the supplied witnesses; optimizing the leaf bill need not
optimize an unequal-dispatch bill. No elapsed-time improvement is asserted.

## Complete work and storage

At a specified common precision and magnitude capacity, `t_j` must include
leaf arithmetic, source/target scans, coefficient and phase access, local
preparation, local scratch restoration and leaf dispatch. Use the maximum
of the two sign prices when they differ. For a fixed tree, the complete
recursive execution charge is

```text
R(leaf j) = t_j
R(D(L,R)) = 2 R(L) + 2 R(R) + g_D
R(C(L,R)) = 2 R(L) +   R(R) + g_C.
```

Internal prices cover descriptor access, dispatch, controller operations
and checks actually performed per invocation. External work remains:

```text
parameter preparation + clean provisioning + clean admission scans
+ tree optimization + tree validation + R(tree)
+ instruction/routing/access work not already included.
```

If these prices depend only on the interval and remaining resources, the
same interval recurrence with the appropriate `g_D` or `g_C` added also
optimizes that enlarged bill. The supplied optimizer minimizes leaf prices.

The second clean array is an explicit input resource. Clearing borrowed
unknown data would violate restoration. Its provider must supply a genuine
zero array and account for initialization or preservation of displaced
information. If fresh storage may be initialized by writes, `c` length-`L`
arrays require `cL` writes and a full admission scan requires `cL` reads.
Such a scan establishes zero; it does not create it.

Data scratch occupies `sL` payload words. Source and target add `2L`;
immutable factors, arithmetic workspace and controller storage are
additional. Each word includes magnitude bits as well as fractional bits.
The reference is an indexed-RAM implementation, not a fixed-tape routing
or physical-hosting construction.
All scheduled arrays share one payload group, length and common grid width.
Different source/target widths require a separately priced conversion and
restoration contract; the scheduler supplies none.

With `d=s-c`, reachable resource states have remaining clean count at most
`c` and remaining dirty count at most `d`. The optimizer uses
`O(n^2(c+1)(d+1))` scalar/backpointer entries and
`O(n^3(c+1)(d+1))` comparisons, with integer bit costs additionally charged.
Counts exceeding `n-1` of either resource are irrelevant and may be capped.
The implementation's immutable tree tuples share child references; the
selected tree has `O(n)` nodes.

The emitter freezes and validates the tree before returning a streaming iterator. For
`N` emitted leaf instructions and height `h <= min(s,n-1)`, recursive
generator propagation takes at most `O(Nh)` controller work. Retained
scratch-pool slices use `O(hs)` role references. Materializing the stream,
as verification may do, instead adds `O(N)` instruction storage. Clean
admission and leaf implementation remain caller obligations; an arbitrary
leaf failure is not transactional.

## Conditional precision recurrence

Assume each ideal leaf is linear with operator norm at most `K >= 0`, and
each signed numerical leaf has local error at most `a*u*(B+1)` for input
norm at most `B`, where `u=2^-w`, `a>0`, and `a*u <= 1`. These are assumed
leaf bounds; this package does not prove PR628's numerical accuracy.
Let all initial array norms be at most `D0`, and put `G=2+K`.

For the maximum norm `M_j` of all arrays after `j` leaf instructions,

```text
M_(j+1)+1 <= G*(M_j+1) <= G^(j+1)*(D0+1).
```

Let `e_j` be the maximum difference from executing the same instruction
word with ideal leaves, from identical initial data. Then

```text
e_0 = 0
e_(j+1) <= (1+K)*e_j + a*u*G^j*(D0+1)
e_N <= N*a*(D0+1)*u*G^(N-1).
```

Thus one sufficient precision for execution error at most `2^(-p-1)` is

```text
w >= p+1 + ceil(log2(N*a*(D0+1))) + (N-1)*ceil(log2(G)),
```

together with `a*2^-w <= 1` and inherited stability conditions. Magnitude
capacity must cover `G^N*(D0+1)` at completed leaf boundaries. Each leaf
implementation must separately bound and provision its transient arithmetic
magnitudes and workspace; the local output-error assumption does not bound
those internal states. If preparation also perturbs initial data by at most
`eta`, add `(1+K)^N*eta` to the error
bound; coefficient preparation must establish the assumed uniform local
leaf error. Other preparation errors require their own propagation bound.

Costs must be evaluated at this precision and magnitude capacity. A common
precision sufficient for both compared words gives a valid count comparison;
different per-word precision costs require repricing. This conservative
bound supplies no better asymptotic precision order or supplier moment.

The executable finite checks support the written inductions and reject
specific failure modes. They do not establish leaf accuracy, clean-space
supply, routing, all-size physical compilation, analytic transfer, or the
full multiplication theorem. PR673's integration obstruction remains an
external obligation; the selected result is unchanged.
