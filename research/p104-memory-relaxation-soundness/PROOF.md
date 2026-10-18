# Soundness of the repaired subspace-memory relaxation

The result is a necessary support test for a fixed linear correction contract.
It closes the recurrence implication left open by PR3214. It does not construct
coefficients or a correction supplier.

## Contract and theorem

Work over a field, with independent source blocks `X_s`, independent helper
initial values, and arbitrary target initial values. Consider a finite linear
program for the **increment** of its targets. Assume:

1. Sources are immutable. Each source may be read at specified frame snapshots.
   The relaxation grants every such snapshot without requiring its original
   time. Sources never acquire another source's value through helper writes.
2. Targets are unread sinks. Their initial contents do not contribute to the
   correction increment. A write can occur at any specified target snapshot.
3. Helper `h` has one actual nested flag `F(h,0) < ... < F(h,9)` in `F_2^9`,
   with `dim F(h,d)=d`. At every dimension used by the test,
   `L(h,d) <= F(h,d) <= U(h,d)`. A helper never returns to a smaller dimension,
   changes its frame at fixed dimension, reloads at an earlier frame, or uses
   unlisted storage. Logical transports act within that helper and do not
   create dependence on other input blocks.
4. A linear operation can transfer dependence between registers only at one
   common actual frame. The relaxation grants arbitrary such mixing. There
   are no other registers with source-dependent initial data. Initial helper
   dirt has zero dependence on each independent `X_s`.
5. Source snapshots have dimension at least one and target writes have
   dimension at most eight. Hence helper layers zero and nine create no
   additional source-to-target paths. Helpers may be interleaved in any
   chronological order. A global dimension order is not assumed.

The theorem also applies in a smaller binary space with fewer layers. The
actual flags must fit all the bounds; existence of compatible individual
intervals alone is not asserted to give a common flag assignment.

**Theorem.** Delete only the output-loop `break` immediately after
`outputs[t] |= 1 << s` in PR3182's
`propagate_with_subspace_memory_bitmap`. Initialize `direct[t]` with every
source having a common source/target snapshot. Use complete untimed snapshot
reads and writes and the interval contacts below. In either memory mode,
every nonzero source block of any program satisfying this contract occurs in
the returned target support. Thus a returned missing coefficient is a valid
exclusion under this contract.

This is not a theorem about programs reading Y, helper descents, mutable X,
additional correlated helpers, unequal-frame operations, or a complete
multiplication implementation. In particular, the original channel's other
intermediate helper values are not additional free sources in this model.

## Recurrence

Treat frames as literal binary subspaces. For dimension `d`, two helper
intervals admit a contact exactly when

```
L_h + L_w <= U_h intersect U_w,
dim(L_h + L_w) <= d <= dim(U_h intersect U_w).
```

A common frame must contain the sum and lie in the intersection. Conversely,
extend a basis of the sum to dimension d inside the intersection. This
criterion only permits a contact; different permitted contacts need not be
simultaneously realizable.

For each helper and source, retain a collection of remembered subspaces `S`.
Let `state` be the collection after dimension `d-1`. Construct `next` at d:

- Carry every old memory forward without filtering it. This is permissive.
- For every source snapshot `V` fitting helper h's d-interval, insert V in
  full-memory mode, or `L(h,d)` in one-step mode.
- For every contact `h -> w`, use **old** `state[h,s]`. A memory S can relay if
  `T = S + L(h,d) + L(w,d)` lies in `U(h,d) intersect U(w,d)` and that
  intersection contains a d-space extending T. Insert T in full-memory mode,
  or `L(h,d) + L(w,d)` in one-step mode. Self contacts need only the carry.
- For every target snapshot V fitting helper h's interval, output **every**
  source s with some memory `S <= V` in `next[h,s]`.

At insertion, discard a candidate containing an existing memory. Otherwise
remove old proper supersets of the candidate and retain the candidate. The
remaining memories form a subset-minimal antichain. A resource-cap failure in
our new implementation raises an error; it never yields a passing exclusion.

These are the retained routine's operations after the one-break deletion.
The separate implementation uses point sets and literal span extension; the
retained routine uses integer bitmaps and subspace-cardinality identities.

## Proof

Expand the finite linear program into its chronological dependence graph.
A nonzero source-to-output block has a directed path from that source to a
write of the target increment. Cancellation can delete a contribution, but
cannot produce dependence without a path. Independent helper dirt and unread
target inputs do not create additional source paths.

Along such a path, dimension never decreases. Partition its helper portion
into maximal runs at each dimension. All equal-dimension relay steps in a run
use the same **actual frame** V: adjacent registers have equal frames, and a
helper cannot change frame without increasing dimension. Therefore the run's
first and last helper share V, even when intermediate helpers have different
permitted intervals. A direct first-to-last interval contact is granted.
This is path compression for a necessary test, not a proposed replacement
program or a change to its price.

Induct on dimension, maintaining the following witness property: for every
actual source path reaching a helper at its current frame F, a retained
memory representative S exists with `S <= F`.

If a path starts with a source read at dimension d and then relays in that
same dimension, its final receiving helper also has the read frame V. The
**complete untimed** snapshot relation therefore grants that receiver a
direct read of the same immutable source. Full-memory acquisition inserts V;
one-step acquisition inserts its lower bound, a subspace of V. This explains
why the routine may relay only old state without losing freshly acquired
paths. The assertion would be false for an arbitrary incomplete read mask.

For a path carried upward without a relay, the old representative remains a
subspace of the helper's enlarged actual frame. The unconditional carry in
the recurrence preserves it.

Otherwise the dimension-d run starts with source dependence carried from a
lower dimension at helper h and ends at helper w, at shared frame V. The
inductive representative S satisfies `S <= V`. Both lower bounds also lie
in V and both upper bounds contain V. Consequently

```
S + L(h,d) + L(w,d) <= V <= U(h,d) intersect U(w,d),
dim(S + L(h,d) + L(w,d)) <= d <= dim(U(h,d) intersect U(w,d)).
```

The recurrence grants the compressed relay. Its full-memory representative
is the left-hand sum; its one-step representative forgets S. Both lie in V.
A run beginning and ending on the same helper uses the carry case instead.

Subset-minimal pruning preserves this induction. Whenever an S is removed
or omitted, a retained `S' <= S` replaces it. Such a replacement remains a
subspace of V. Every future relay guard and write guard is monotone under
replacing a memory by a subspace: its required sum can only decrease.
Repeated pruning therefore preserves an adequate representative.

Finally, at an actual target write in frame V, the final helper has a memory
`S <= V`. The complete snapshot relation grants this write, and the repaired
output loop unions its source bit. A path with no helper uses `direct`.
Every nonzero source block is covered, proving the theorem in both modes.

## What the result does and does not certify

The proof is universal over finite linear words satisfying the stated
contract. The finite checks below test its implementation and source binding;
they do not replace that proof or provide a formal-kernel verification.

Our P104 replay reconstructs the raw data paths and PR3019 endpoint pairing,
checks the required `C[98,1]=-1/2` from the ordered E8 roots, and retains
PR3214's literal X1-H201-Y98 path at source cut 594 and target cut 4058.
Its full flag is nested and fits the fixed bounds. Both repaired bitmap
outputs agree with a separate point-set recurrence on all 104 targets.
The path itself grants arbitrary helper dirt and does not restore it, exactly
as in the predecessor's support calibration.

The complete small domain has all 21 full flags in `F_2^3`, every ordered pair
of helper flags, and all 16 choices of revealing their dimension-one/two
frames. At each unrevealed layer, use the nearest revealed lower and upper
frame, with zero and the whole space always revealed. All 14 nontrivial
subspaces are independent source and target snapshots. For every fixture,
BFS on the two actual flags is contained in both recurrence outputs. With
all frames revealed, both recurrences equal the literal graph. There are
7,056 interval fixtures, two modes, and 196 source/target pairs per fixture.
The archived repaired core agrees on every fixture. This is a small exhaustive
implementation check, not a search over P104 matchings or joint full flags.

Additional controls separate a complete fresh-read relation from an arbitrary
one, preserve two independent output sources, check a restored six-ADD dirty
shear, reject an incompatible carried full-memory frame, and exercise
subset-minimal pruning. In the incompatible-frame example, one-step memory
allows a false positive by forgetting history. That is consistent with a
necessary relaxation and is not a realizable correction.

Chronological feasibility of the optimistic paths, simultaneous flags,
coefficients, helper restoration, native compilation, physical hosting,
precision and the completed consumer bill remain separate obligations.
No new kappa, lifetime floor, matching census or selected-frontier update is
established. The family decision is to finish this implication and stop.
