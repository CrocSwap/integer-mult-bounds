# A restored cofactor stream for dense quadratic phases

This scoped constructive proof was produced by Nick Petalas. Apache-2.0.

## Proposition and accounting model

Let L be any nonnegative integer, N=2^L, and let all coefficients below
belong to Z/4. On Boolean arguments define

```text
q(x) = c + sum_i a_i x_i + sum_(i<j) b_ij x_i x_j.
```

The coefficients may be completely dense. There is a stream producing q(x)
in increasing binary-address order, with bit zero varying fastest, using

```text
N emitted residues,
4N - 2L - 4 additions/subtractions in Z/4,
2(N - L - 1) reads of quadratic coefficients,
4N - 3 control events,
at most 3L + 1 pending event records.
```

The current constant and L current linear coefficients return to their
entry values after complete exhaustion. Quadratic coefficients are read-only.
There is no N-entry phase table. Besides the supplied quadratic coefficient
table, mutable coefficient state is L+1 residues, with O(1) additional
temporary residues for an update. Event records contain one
of three tags and a level in 0..L, so their storage is O(L log(L+2)) bits.
The input table occupies O(L^2) bits. Initialization, input validation and
the O(L) copy of the linear coefficients are additional, bounded by O(L^2).

An addition or subtraction of two residues followed by reduction modulo four
is one arithmetic update. Indexing, coefficient reads, stack operations,
output delivery and coefficient preparation are not free physical actions.
The event/read counts above expose part of that work; they are not a tape
tariff. In particular this is not a speed comparison with #5375's physical
action count. Even zero-valued updates are executed and included.

## Restored cofactor invariant

At a visit with j free low bits, fix the higher bits according to the path.
The mutable constant C and linear array A satisfy

```text
q(x_low, fixed_high)
  = C + sum_(i<j) A_i x_i + sum_(i<k<j) b_ik x_i x_k.
```

The quadratic part on the remaining variables never changes. To enumerate
this subcube, first visit x_(j-1)=0 using the current state. When that visit
returns, enter the one branch by performing

```text
C       += A_(j-1)
A_i     += b_(i,j-1)       for 0 <= i < j-1.
```

These j updates give exactly the cofactor with x_(j-1)=1. Visit the remaining
j-1 low bits. On return subtract the same quantities to restore the state.
The lower visit never changes A_(j-1), so the final constant subtraction
uses precisely the same residue as the earlier addition. The higher linear
coefficients are also untouched.

Induction on j proves both correctness and restoration. At j=0, output C.
At j>0, the zero branch and then the one branch cover the two consecutive
binary-address halves exactly once. Each child restores its entry state,
and the explicit subtractions restore the parent's entry state. No
zero-initialization of the coefficient values is used. Every entry residue,
including the constant, may be arbitrary. The event storage itself is newly
allocated bookkeeping, not arbitrary dirty workspace supplied for free.

For a Gaussian phase, the emitted q is interpreted as i^q. The proof keeps
the constant c and hence absolute phase. General Z/4 cross coefficients are
allowed. Restricting cross coefficients to 0 and 2 gives the usual Boolean
quadratic Clifford phase subclass. This inclusion does not establish that
every general phase in the larger class is a native Clifford operation.

## Nonrecursive execution and exact counts

An event is visit(j), enter-one(j) or leave-one(j). Expanding visit(j), j>0,
schedules the following chronological sequence on a last-in-first-out stack:

```text
visit(j-1), enter-one(j), visit(j-1), leave-one(j).
```

The reference pushes these in reverse order. A leaf emits a single residue.
The complete binary tree has N leaves and N-1 internal vertices. Each
internal vertex contributes one visit and two update events. Thus the exact
number of processed events is N+3(N-1)=4N-3. This supplies an explicit loop
bound; no recursive Python call is used.

There are 2^(L-j) internal vertices with j free bits. Each executes j updates
on entry to its one branch and j on exit. Therefore

```text
U_L = 2 sum_(j=1..L) j 2^(L-j)
    = 4*2^L - 2L - 4.
```

For example the identity follows from U_0=0 and U_L=2U_(L-1)+2L.
It proves fewer than four arithmetic updates per emitted phase, uniformly
in L. The linear-coefficient updates, and hence quadratic coefficient reads,
number

```text
R_L = 2 sum_(j=1..L) (j-1) 2^(L-j)
    = 2(2^L-L-1).
```

Each initial descent through an internal visit replaces one pending event by
four, increasing stack length by three. The first leaf therefore reaches
exactly 3L+1 pending events immediately before its visit. No later descent
can exceed it: at most three pending siblings/update events remain at each
ancestor level, plus the current visit. This also covers L=0, when the sole
pending event is visit(0).

There are 2(N-1) reads of the current top linear coefficient for constant
updates, R_L reads of current lower linear coefficients, and U_L writes of
current residues. These are abstract array accesses. Their movement on a
fixed tape, the binary representation of levels, source serialization and
output-consumer costs are not certified here.

Every implementation which explicitly emits N phase symbols requires at
least N output actions in a unit-output model. This construction has
O(L^2+N) abstract work, including initialization, and is order-optimal in
that model. The exact arithmetic constant is an upper bound, not a proved
minimum. No fixed-tape order-optimality follows.

## The completed-return boundary

Python yields at each leaf. After the last yield, the remaining leave-one
events still need execution. The return theorem therefore requires complete
iterator exhaustion, including the call that observes StopIteration.
Merely requesting exactly N yielded values does not meet that condition.
The verifier exercises this distinction. If a consumer stops early, cleanup
of the suspended stream's private cofactor state is unclaimed. Immutable
public input tuples are preserved at every prefix regardless.

The mathematical construction works for every L. The supplied reference
intentionally validates 0<=L<=20 to bound executable memory and iteration
counts. Its finite checks establish only their enumerated cases; the
induction and sums above establish the quantified proposition.

## Predecessors, new scope and remaining work

Ali Romman's [#5375](https://github.com/CrocSwap/integer-mult-bounds/pull/5375)
supplies the physical sequential monomial phase producer, with fixed recipe
dimension, borrowed mask, complete counter and coefficient bills. Its
source-specific correctness and bills are cited results, not replayed here.
That package credits Jose Manuel / jmbarrancoml #2250, JoyboyBrian #5329,
Cinna Davis and Ryanson Jonathan #4325, together with their native lineage.
Their results and notices retain their attribution.

Dugongue's [#4538](https://github.com/CrocSwap/integer-mult-bounds/pull/4538),
Theorem 2, already proves O(N+L) phase generation when cross coefficients
are even. Its representation packs the binary matrix columns and gradient
into address-width words, using one whole-gradient XOR per bit flip.
Ryanson Jonathan #4555 supplies a separate finite check of that theorem.
The published theorem is a cited predecessor, not a replay target.

The new project contribution covers arbitrary Z/4 cross coefficients,
including odd coefficients, gives an exact count of individual unpacked
residue updates, and restores the cofactor state explicitly. It does not
claim the first linear-time phase stream or a faster packed-word algorithm.
Polynomial cofactoring and Shannon expansion are classical; no
literature-priority claim is made for those methods. We do not claim that
the input-matrix representation improves #5375's physical implementation.

The three frozen predecessor documents are hashed live context inputs. No
predecessor executable is imported, and no selected source is changed.
Native recipe acquisition, fixed-tape source access and control, output
rotation, affine routing, common-grid/rounding, owned storage, the complete
caller invoice and all five multiplication-framework assumptions remain.
There is no new kappa, supplier admission or complete multiplication theorem.
