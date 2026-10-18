# Retained numerical cell arrays of the pinned Arena

This is a written source proof for `vendor/words.py`, unchanged from Jose
Manuel/jmbarrancoml's PR2697, exported by Ross Richardson's PR2825. `INPUTS.json`
pins all consumed source and predecessor proof bytes. The proof concerns the
lengths of `Word.cells` arrays, including erased cells, LEFT and RIGHT positions.
It excludes Python list/set/object capacity, temporary constructor lists,
allocator overhead, encoded slot tables, physical placement and head movement.
It is therefore a numerical backing component, not a complete memory theorem.

## Single arena invariant

Let the fixed integer digit width be `b>=2`, so each Word has `b+2` cells.
Every arena capacity is an integer `C>=1`, as required by its constructor. Assume a
canonical entry state reachable by successful legal Arena operations: there
are `K` slots in `words`, numbered `0..K-1`; `live` and the duplicate-free
`available` stack partition those slots; free slots contain LEFT followed by
`b+1` blanks and have head one. The separate permanent template has LEFT, b
zero digits and RIGHT, with head one. Live Words obey the head/data contracts
of their invoked operations; other suspended live heads need not be one.
Borrowed entry Words are included
in `live`. No external code creates additional Words, changes arena bookkeeping,
resizes cell arrays or corrupts/frees a borrowed object. Source arithmetic may
change live digits and move heads without changing this allocation invariant.

Expand higher-level operations into sequential `zero` and `free` calls. After
each complete call let `L_t` be live slots and `B_t=len(words)`. Include entry
as t=0, and put `H_t=max(L_0,...,L_t)`. Then

```
B_t = max(K,H_t),
retained Word-array cells = (max(K,H_t)+1)(b+2).
```

The +1 is the permanent template, not an allocatable slot.

**Induction.** A free erases the Word, removes its live slot and appends that
slot to `available`; it neither shrinks `words` nor allocates another Word.
If `zero` finds a free slot, it pops that slot and restores its complete zero
encoding. Here `L_before<B_before`, so `L_after<=B_before`; B and `max(K,H)`
remain unchanged, although H itself can rise below a warm entry K. If the free
stack is empty, partition implies
`L_before=B_before`; `zero` checks `B_before<capacity`, creates slot B, appends
it, and marks it live. Both B and L increase by one. This proves the equality
and preservation of the partition. Each Word's fixed array length gives the
cell equality. Literal construction, copy, free_many and successful rollback
are compositions of these operations; they do not alter the invariant.

At an interior Python statement, the new Word may already have its array,
but have not yet been appended or marked live. Thus an assertion of the same
equality using **only the instantaneous live set** at every statement is false.
Count the one pending new-slot reservation, or measure H at completed allocation
boundaries. The cell peak during a successful operation is no larger than its
post-operation high-water bound: construction creates at most the one array;
initialization and erasure only overwrite existing cells. The constructor/write
probe explicitly observes the pending-array case. This does not count temporary
Python buffers used to construct the bytearray.

## Capacity replay, with an explicit noncircular premise

Fix an independently specified legal request trace, including a choice of live
slot for each free, and assume its noncapacity preconditions hold. Equivalently,
take a successful reference execution whose trace is fixed before choosing a
target capacity. If its maximum live demand is H, a canonical entry with K
slots can replay the trace in capacity C exactly when

```
C >= max(K,H).
```

Necessity includes representing the existing K slots. Sufficiency follows by
induction above: a new slot is requested only when all previous slots are live,
and its resulting live count is at most H. Hence the guard cannot be the first
failure. Reuse requires no extra slot. Free-slot order, object identity, cells
and heads are independent of a capacity parameter that never rejects. Other
errors, arithmetic margins, provider behavior and allocation failures of the
host language remain outside the theorem.

A statement that **successful calls** obey a live bound does not alone establish
the independently legal trace premise. In particular, PR2825 assumes successful
admitted execution and sufficient capacity. We do not turn that conditional
statement into a new unconditional proof of actual caller success.

## Distinct arenas retain distinct historical peaks

For two arenas with fixed widths `b_R,b_I`, entry backing `K_R,K_I` and running
live maxima `H_R(t),H_I(t)`, the exact retained-cell count at complete-operation
boundaries is

```
(max(K_R,H_R(t))+1)(b_R+2)
  + (max(K_I,H_I(t))+1)(b_I+2).
```

Both terms are nondecreasing, so for a finite trace the endpoint is the maximum
retained cell count even after every temporary has been erased. Different
phases can determine the two historical maxima. A maximum of phase-weighted
live contents generally undercounts the retained arrays.

A literal witness uses three four-cell residue Words, frees them, then uses
two five-cell index Words and frees them. The templates occupy nine cells.
Maximum simultaneous live-cell content including templates is
`9+max(3*4,2*5)=21`, while retained arrays occupy `9+3*4+2*5=31` cells.
Both comparisons include LEFT, isolating retention from marker accounting.

Entry history is also essential: a three-digit arena with seven erased slots
and no live Words occupies 40 cells, versus five for a fresh empty arena. After
one allocate/free pair, those totals are still 40 and ten. For arbitrary K,
no formula using only current live count and current-call scratch can bound
already retained arrays independently of the prior allocation cap/history.

## Conditional PR2825 consequence

Retain every successful first-range caller premise and component contract from
the pinned `evidence/PR2825-PROOF.md`: distinct arenas; all entry residents;
dimension 64, width 64<=n<128; admitted canonical programs, fields, margins and
sources; numerical-neutral providers/observers; and restored coefficient calls.
It gives the coordinatewise live bounds

```
H_R <= L_R + 37672,       H_I <= L_I + 41.
```

Here L_R,L_I count all live caller-entry Words. Therefore the numerical arrays,
including blank cells and every LEFT/RIGHT position and both templates, satisfy

```
T <= (max(K_R,L_R+37672)+1)(b_R+2)
       + (max(K_I,L_I+41)+1)(b_I+2).
```

If entry slots are all live (K=L), this simplifies to
`(L_R+37673)(b_R+2)+(L_I+42)(b_I+2)`. More generally the same simplification
is a valid upper bound when K_R<=L_R+37672 and K_I<=L_I+41. The cold condition
is sufficient, not necessary. A successful capacity-independent reference trace
meeting the inherited bounds can be replayed at capacities
`max(K_R,L_R+37672)` and `max(K_I,L_I+41)`; caller existence/termination and
the other premises remain inherited.

PR2825's finer **occupied non-LEFT content** bound remains correct in its
declared measure. Its maximum of adapter rectangle (37672,34) and child
rectangle (20494,41) must not be reused as a retained-array bound. These two
rectangles permit a synthetic legal allocator trace visiting each in turn,
which attains both coordinate maxima historically. The literal test constructs
that relaxed schedule with nonzero borrowed parents. This proves sharpness of
the implication from those rectangles alone, not that the actual selected
caller realizes either entire rectangle or both sharp maxima.

Repeated calls sharing these arenas need no cumulative factor for total
allocation count if their live-demand bounds have one common baseline/ceiling:
apply the same historical maximum to their concatenated trace. Suspended parent
state belongs to that ceiling. Creating fresh arenas or changing widths is
outside this corollary; no recursive stock coefficient follows without those
bindings.

## Evidence and remaining obligations

The primary checker exhausts the reachable allocation-state quotient for each
capacity 1..5 at digit widths 2 and 5, including arbitrary free-slot orders and
all outgoing legal zero/free edges. This is finite exhaustive coverage of that
specified all-zero, restored-head domain. It is not an exhaustive test of all
Word values or all callers. Arbitrary widths, histories and live digits are
covered by the written induction, with separate literal/copy/rollback fixtures.
The independent checker/proof is a separately implemented AI audit; neither
proof is a formal-kernel or independent human proof.

The exact newly counted objects are numerical Word arrays. Payload/count/key
tapes, programs, serialized continuations, bookkeeping metadata, physical
slot/tape mapping, parking, head movement, larger recursive grants, stronger
H2 bounds, outer reserve and supplier admission remain separate. This does not
modify PR2769/2809's physical work or PR2758's continuation analysis. There is
no new kappa or selected-frontier change.
