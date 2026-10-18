# Independent source audit of the numerical prefix implication

The two closed-entry allowances survive removal of the assumption that an
execution has already succeeded, or that a completed reference execution
exists. For the unchanged PR2697 implementation at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, the adapter allowance is
37,672 residue Words / 22 index Words and the delegated child allowance is
20,494 / 22. They bound each pending numerical allocation as well as the
allocations that actually succeed. With the well-formed allocator invariant
below, these allowances rule out a first inventory rejection.

One subordinate statement needs correction: `children.extend` can require
**11**, rather than 10, index Words above the closed entry. The correction is
strictly below the child's overall 22. The independently implemented literal
witness below distinguishes the two values using actual source capacities.

This is a separate AI-assisted source audit and written argument. It is not
independent human review or a formal-kernel proof. It reads the original
modules directly; its finite witness imports neither the primary package's
fixtures nor its verifier. No complete predecessor replay was performed for
this audit. The constants and their successful-execution derivations are
credited predecessor results, not new constants here.

## Quantifiers and scope

Let a call of `numeric.selected_coefficient` use the seven byte-identical
runtime modules pinned in `INPUTS.json`. Assume:

* The residue and index arenas are distinct ordinary source `Arena` objects.
  They are used sequentially, with fixed capacities and no concurrent
  mutation, numerical-allocating observer, substituted routine, or overridden
  arithmetic method. Every actual numerical Word allocation uses `Arena.zero`.
* At entry, for each arena, the allocated slot set `range(len(words))` is the
  disjoint union of `live` and `available`; `available` has no duplicates.
  Word identities agree with their slots. Available Words are erased and
  positioned for reuse, and the permanent template is valid. The entry state
  is reachable by the ordinary allocator, so `len(words) <= capacity`.
* The dimension is 64. Every good rank and every source rank used by the
  program is between 1 and 42. The fixed source matrices have their prescribed
  square dimensions; request labels, source/plan bindings, chronological
  programs and frozen field encodings have the stipulated source shapes.
  These conditions exclude arbitrary malformed Python containers or aliases
  in places where the implementation assumes distinct matrix Word ownership.
* The Ring is initialized over an admitted odd prime power, Words are complete,
  residue operands are canonical, and the primitive arithmetic and index
  margins hold whenever the relevant routine is entered. These retain the
  predecessor algebraic/input hypotheses; they do not assert successful
  execution, arena sufficiency, or existence of a successful reference run.
  Borrowed entry Words, templates and input tapes initially have their
  prescribed heads. Source tables and input bytes are not changed concurrently.

Count **all** numerical Words live before the closed call as `L_R,L_I`.
This includes Ring constants, coordinates, unrelated matrices, retained
outputs and suspended callers. The statement covers every finite prefix
before a first noncapacity error and the numerical demands made up to a
possible first inventory error. In particular it does not assume that all
future noncapacity checks will pass. An ordinary nonunit return from
`Ring.inverse` is included. If an explicit source guard rejects, the reached
state still obeys the prefix bound; the ensuing source cleanup allocates no
Words. Arbitrary Python exceptions, malformed-word recovery and overall
semantic success are not claimed.

The only capacity conclusion is for the two numerical arenas. Serialized
programs, field tapes, pending/value stacks, LEFT markers, templates, physical
backing arrays, Python objects, total caller residents and movement costs
remain distinct accounting obligations. The entry counts cannot be set to
zero without a caller analysis.

## Why the proof can be about prefixes

Use a local contract `(P,O)`: at every pending `zero` call, current live count
plus its requested Word is at most the local entry count plus `P`; if the
routine returns normally, it leaves `O` owned output Words and preserves its
borrowed live set. A routine may have several normal exit values of `O`, such
as unit/nonunit inversion. At a nested call, add the currently retained local
Words to the callee's prefix bound. At a branch take the larger case. At a
loop, verify the number of retained Words at the loop header and that every
completed iteration restores it before repeating. Any unfinished iteration is
covered by its phase bound. No future free is used to pay for an earlier
allocation; no terminating reference execution is used.

`zero` requests one Word, `copy`, `literal` and `read_word` reach that same
allocator, and `free`, `free_many`, `rollback`, tape writes, tape clearing and
tape rewinding request no numerical Word. Partial list comprehensions and
partially decoded stack operands count immediately, even if Python has not
yet assigned the completed container to its destination variable.

## Primitive and matrix audit

Direct allocation order in `vendor/words.py:192` through `:415` gives these
prefix allowances above all local entry residents:

| Routine | Pending peak | Normal returned Words |
| --- | ---: | ---: |
| Unsigned add/subtract/shift | 1 | 1 |
| Unsigned division | 4 | 2 |
| Unsigned times_small | 2 | 1 |
| Ring add/subtract | 2 | 1 |
| Ring negate | 3 | 1 |
| Ring multiply / literal | 4 | 1 |
| Ring inverse | 10 | 1 for a unit; 0 for a nonunit |

Division holds scan, quotient and remainder before requesting a fourth
replacement. It frees the old remainder before the optional subtraction.
Multiplication holds scan and result and calls at most two-Word addition;
the old result is freed before the next addition. Inversion holds four
Euclidean Words at its loop header. Division leaves quotient and remainder,
so multiplication sees six retained Words and requests at most four more.
The iteration frees quotient, product and the two replaced Euclidean Words
before its next header. A nonunit exit frees the final coefficient too.
Thus failed unit candidates do not accumulate a coefficient from one candidate
to the next, and the bound does not require successful inversion.

In `vendor/matrices.py:69`, the identity entries are the right halves of the
augmented rows, so they contribute `d^2` Words once; copied input contributes
another `d^2`. Partial copying is smaller. Pivot inversion gives the prefix
bound `2d^2+10`; failed candidates return no output. Normalization and row
elimination use at most six more than stored elimination entries. Matrix
multiplication allocates its output and at most four additional Words.

For `Callback.prepare` the simultaneous excesses, including the freshly read
high matrix, are:

| Phase | Residue prefix allowance |
| --- | ---: |
| Raw header and its palette | `3m^2+5` |
| Preparation constants and palette | `max(4m^2,3m^2+11)` |
| Header multiplication | `4m^2+4` |
| Projector inversion | `4m^2+10` |
| Final projector multiplication | `4m^2+4` |

There are at most `m^2` distinct palette entries. While preparing an entry,
at most `m^2-1` earlier entries coexist with numerator, denominator and ten
inverse scratch Words. During copying, at most a full palette and a full
output coexist. This covers partial matrix/palette construction and invalid
unit candidates up to their explicit rejecting guard. Only the `m^2`
projector remains on normal return. These are all below `4m^2+10` at `m=64`.

For `good_form` (`vendor/forms.py:79`), put `S=2mr-r^2`. The chronological
pivots and row/column scalars never exceed `S`, including zero scalars. The
consecutive prefix allowances above its entry are

```
3m^2+S+10, 4m^2+S+10, 5m^2+S+10,
5m^2+S+4, 5m^2+mr+S+4, 5m^2+2mr+S+4,
5m^2+2mr+S+3, 6m^2+2mr+S+10.
```

They correspond to initial elimination, the two inversions, `lp`, `a0`, `b`,
negation and cross construction. The last is
`G(r)=6m^2+4mr-r^2+10`. The seven intermediate matrices remain counted until
the actual final frees; slices merely alias existing entries. Normal output
has `m^2+S` distinct Words.

For `fallback_form` (`vendor/forms.py:140`), put `n=128`. At column `j`, the
residual's `n^2` Words coexist with at most `j(n-1)` prior shear coefficients.
Pivot inversion is at most `n^2+(n-1)^2+10`. Row updates can hold every
`n(n-1)` shear, one inverse and four multiplication scratch Words. Residual
construction adds at most four; determinant processing adds at most five
before earlier entries are freed. Consequently the selected-dimension maximum
is `F=2n^2-n+5=32645`. Normal output has `n^2` Words. This maximum is not
asserted for small `n`, where pivot inversion can be the larger phase.

## Callback, pending frames and closed composition

`Stack.push` serializes the existing Words and allocates none. `Stack.pop`
(`vendor/records.py:133`) materializes at most two indices for VALUE or one
residue for the other tags. The partial second operand is included. At a
`Callback.weight` loop header, all earlier ancestor matrices, pivots and
diagonals have been freed after serialization. Pending/value records retain
symbols, not live arena Words. Their number may grow with depth.

A VALUE expansion retains at most one projector. Its good processing fits
`2m^2+r+9`; its fallback processing retains the `m^2` projector plus the
`4m^2` residual and ten inverse scratch Words. CONSTANT, MULTIPLY and PAIR
materialize respectively at most one, two and three residue operands; PAIR's
inverse therefore reaches at most 13. These phases yield `5m^2+10` above
the weight entry. Index expansion retains level, coordinate, parent, child,
`f` and slot, then at most four division Words, yielding ten. Seeks need at
most three while fewer addresses are retained; pair address construction
fits nine. A rejected guard prevents the next loop iteration, so its live
temporaries cannot accumulate across later iterations.

A completed Callback owns two residue Words and six indices. Constructor
prefixes use at most 12 residues and 15 indices: root-unit inversion has the
two residue residents plus ten; chronological validation's largest index
phase has constants/root/current/count, level/parent/child/`f`, and the four
temporaries of halved division. Previous step addresses are freed before
repeating. This reasoning also covers a constructor that has not returned.

Adding the actual simultaneous closed-entry residents gives:

| Adapter phase | Residues | Indices |
| --- | ---: | ---: |
| Callback construction | 12 | 15 |
| Current projector | `4m^2+12` | 11 |
| Good construction with borrowed projector | `m^2+G(r)+2` | 7 |
| Fallback construction with borrowed projector | `m^2+F+2` | 7 |
| Adapter evaluation | `9m^2+13` | 22 |

The evaluation row includes the retained form, callback residents, one
already computed bank numerator and the nested weight. A bank keeps its
base and position during weight; the Page/callback baseline is ten indices.
For `1<=r<=42`, the largest residue row is
`7m^2+4mr-r^2+12 <= 37672`. Closing the form/Page/Callback only frees Words.

| Delegated child phase | Residues | Indices |
| --- | ---: | ---: |
| Parent construction | 12 | 15 |
| Extend, retaining parent | 2 | **11** |
| Leaf construction, retaining parent | 14 | 21 |
| Leaf weight, retaining both callbacks | `5m^2+14` | 22 |
| Optional negative inverse | 15 | 12 |

The correction follows directly from `vendor/children.py:20`: after dividing
the parent size by 64, `f` remains live while `divmod(f,two_index)` requests
four Words. There are six parent indices, so the demand is `6+1+4=11`.
The source does not free `f` until after this call. Two complete callbacks
retain four residues and twelve indices, which gives the stated overall
`20494/22` child bound.

## Rejection paths and the first-inventory argument

`Callback.__init__` catches ValueError after its stacks are created and calls
`abort`. Failures during its earlier constant allocations instead reach the
closed wrapper. The adapter wrapper snapshots its entry sets before entering
`selected_page`; if that function has not returned its tuple, `incoming` is
still None but the outer rollback still reaches every new numerical slot.
The child wrapper similarly handles a partially constructed leaf and a
partially completed extension. Nested abort first preserves the parent, then
the parent/outer rollback can erase that remaining owned state. `abort`,
`rollback`, `close` and tape cleanup contain no `zero` calls. Thus cleanup
cannot create an inventory failure or exceed the prefix numerical count.
This is a monotonic numerical-liveness observation, not a proof of arbitrary
exception safety or physical-tape cleanup.

Let `K_R,K_I` be the numbers of allocated slots on entry. Suppose capacities
satisfy `C_R>=max(K_R,L_R+Q_R)` and `C_I>=max(K_I,L_I+Q_I)`, for the branch
allowance above, and consider a putative first `fixed register inventory`
error. Thus each capacity includes the entry backing as well as the requested
live allowance. The prefix analysis applies to its pending allocation. If `available`
is nonempty, `zero` takes its reuse branch and does not test capacity. If it
is empty, the allocator partition gives `len(words)=len(live)`. Failure
requires `len(words)>=C`, whereas the pending demand gives
`len(live)+1<=L+Q<=C`, a contradiction. This works for fresh and reused
arenas and uses no completed execution. Capacity sufficiency does not turn
an invalid pivot, coordinate, source binding or arithmetic margin into a
valid one.

The partition is necessary to connect a live-Word theorem to the actual
source guard: if a caller removes erased slots from `available`, the arena
may have no reusable slots while `len(live)` is small. Such a corrupted state
is outside the normal allocator's invariant. The proof must not silently
equate backing length and live count without the empty-available condition.

## Independent finite witness and coverage

Run from the repository root:

```
python3 -I -Werror -B research/selected-coefficient-capacity-prefix/independent.py
```

The two literal executions use F3, ten-bit index Words, root size 256,
depth zero and a halved unit extension. The closed entry owns one coordinate;
the Callback adds six distinct indices. The observer records demands before
the original `Arena.zero`, including the failed request. With actual capacity
`L_I+10`, the source rejects at pending excess 11; with `L_I+11`, it returns.
The witness uses explicit `parent.abort` after the naked `extend` failure
because that subroutine has no cleanup wrapper. It checks borrowed-coordinate
preservation and erases all owned numerical Words. These two fixtures passed
in ordinary and optimized Python.

This finite witness corroborates the corrected extension row only. It does
not enumerate all legal inputs or establish the all-parameter prefix theorem
by computation. That theorem rests on the preceding source-lifetime argument.
The primary verifier supplies the separate closed-entry literal boundary
fixtures. No new supplier, total reserve, selected-record admission, new
kappa, formal verification or independent human review follows.

Credit: Jose Manuel/jmbarrancoml supplies the unchanged PR2697 source;
Nick Petalas supplies PR2759/2770/2778/2781's primitive, evaluator,
constructor and adapter bounds; Arham Tahir supplies PR2796's closed child
composition. Their exact reviewed source pins are preserved in INPUTS.json.
This audit adds the explicit pending-allocation/first-failure argument and
the correction to the extension sub-phase. Prepared by OpenAI Codex as a
separate mathematical audit worker; Apache-2.0.
