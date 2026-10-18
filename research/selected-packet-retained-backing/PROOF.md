# A simultaneous backing-array cut in the selected packet caller

This is a source-level result for Jose Manuel/jmbarrancoml's unchanged PR2697,
commit `a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. The relevant statements are
in `Consumer.apply`, `packet_engine.run`, `packet.read_prefix`, and `Tape.clear`
in the byte-identical exports. The finite fixture suite corroborates the written
argument; neither is a formal-kernel proof.

## Contract and metric

Take a successful sequential packet invocation with `N >= 1` prefixes, each
containing `F > 0` Boolean payload symbols; put `V=NF`. The borrowed source
array has length `K >= V+1`. It has its LEFT marker at address zero, the V
payload symbols at addresses 1 through V, a BLANK at the next address (possibly
implicit), and may have arbitrary inaccessible backing beyond that BLANK.
Count that complete retained array K. The directory has array length D and
every fresh complete prefix has length Q, including LEFT. Its representation
and successful parsing are premises here, previously supplied for the canonical
producer by the field-producer result. An arbitrary padded directory uses its
actual D, not the fresh-producer formula.

The caller retains the freshly read preflight `first` of length Q after
`first.clear()`. `prefix.tape` and the closed validation frame's field view alias
that same array. This is exactly the unchanged Consumer's local-binding pattern.
The source, directory, and preflight storage are distinct. Each factory call
returns a new native, unpadded Tape. The payload action preserves its local
input and returns a distinct fresh F-symbol Tape, or, in the explicitly more
general interface case, returns that input alias. The new arrays have length
F+1. No other alias between the named owners is allowed. Native ADD, atom-swap,
and sign paths return separate fresh arrays; the alias case is a control and
an explicit interface generalization. Arbitrary larger returned backing must
instead be charged at its actual length.

The metric is the sum of `len(Tape.cells)` over distinct named arrays. It
includes each LEFT marker and every erased retained cell. It does not count
CPython object headers, bytearray capacity beyond its visible length, implicit
blank head positions, allocator retention, or unlisted objects. A local result
about this metric is neither a physical tape allocation nor a machine-space
theorem.

Number primitive passes by t=0,1,..., ignoring enter/return events. Within pass
t, let j be the number of completed prefixes, 0<=j<N. Observe the cut when
`read_prefix(directory,field_count)` has completed but its result has not yet
been assigned to the outer `fields`. The fresh return value is still rooted
by the reader/return expression. The named cohort consists of source, current,
output, any stale local/changed, directory, first, any stale fields, and the
fresh return value. Other caller residents are excluded and must be added by
identity at this same cut in a later complete ledger.

## Exact cut identity

At the initial cut t=j=0, the exact sum is

```
B(0,0) = K + 1 + D + 2Q.
```

At every other cut, let delta be one if the *previous* completed action returned
a distinct changed Tape, and zero if it returned local itself. Then

```
B(t,j) = K + [t>0](NF+1) + (jF+1)
         + (1+delta)(F+1) + D + 3Q.
```

The previous action is prefix j-1 of pass t if j>0, or prefix N-1 of pass t-1
if j=0. Thus a change of action contract between passes must use the preceding
pass's delta. Counting the upcoming action's delta would be wrong at j=0.

Proof: a fresh Tape has one LEFT cell. Appending a symbols yields length a+1.
Clearing rewrites existing symbols and rewinds without shortening `cells`.
Initially `current is source`, so those roots contribute K only once. Once
a primitive pass has returned a new complete packet, current has V+1 entries,
distinct from the retained source. The next pass creates a separate output.
After j prefixes, precisely jF symbols have been appended to output, yielding
jF+1 entries. Every completed inner iteration clears local, changed and fields
but leaves their bindings in the suspended outer frame. The two payload roots
therefore retain (1+delta)(F+1) entries. They remain bound across the outer-loop
boundary too. During the next read's right-hand-side evaluation, the old fields
binding remains while the new Q-entry value is constructed. Together with the
retained preflight first and the directory, the record contribution is D+3Q.
Before the first inner iteration, local, changed and fields have never been
assigned; only directory, first and fresh fields contribute D+2Q. These facts
give the two formulas. Enter/return events do not overwrite these roots. This
proves the identity for all successful cuts under the stated contracts.

For all-distinct primitive outputs and at least two primitive passes, the
maximum **over this return-cut family only** occurs at any t>0,j=N-1 and is

```
K + (2N+1)F + 4 + D + 3Q.
```

For a fresh source K=NF+1 this is `3V+F+5+D+3Q`. This is not an upper bound
over primitive interiors, other caller phases, all reachable objects, or a
physical allocator. In particular it does not replace PR2731's separate
nonblank-payload peak `3v+3R`.

## Literal evidence and controls

The primary checker runs 18 cases: N in {1,2,4}; (w,before,suffix) in
{(1,1,1),(1,2,2),(2,1,1)}; and actual native sign or an alias interface control.
There are three primitive passes per case. q=3, M=3^w, F=before*M*suffix.
For N=2, the input includes one blank separator plus five inaccessible backing
cells. The literal source packet engine, reader, tape, binary counters, copying,
and native sign arithmetic run unchanged. Ordinary modular arithmetic separately
checks the output permutation. Synthetic layouts and headers are not admitted
selected GL64 geometry.

One additional witness executes actual Consumer.apply production and preflight
at dimension64, w=1, C=6507, h=0, old multiplicity2, with synthetic specifications.
Its astronomical selected payload seam is replaced by the unchanged packet loop
on two three-symbol fibres and two actual sign passes. Q=22894 and D=45787.
The four observed total named-cohort sizes are 91583,114488,114492,114495;
their payload portions are 8,19,23,26. This witnesses coexistence at actual
Consumer preflight bindings, not full selected payload or catalogue admission.
Primary coverage is 130 cuts including that witness.

The independent checker was written from source before reading the primary
proof/formulas. It tests the literal packet engine at 5,184 cuts in 864 cases,
including every length-three fresh/alias action word, padded source/directory
backing, and first-prefix transitions between passes. See INDEPENDENT.md for
its separate finite domain and explicit action/layout abstractions.

Accounting controls reject deleting cleared payload/field roots, missing LEFT
cells, double-counting source/current, and using the wrong changed/local alias
relation. Separate integrity controls reject altered source/manifest bytes,
preloaded modules and a typed-receipt substitution. These are distinct from
the all-parameter written proof. No independent human review is claimed.

## Remaining obligation

Add the Program, arena backing, count and continuation tapes, layout/event
objects, closed preflight internals, and retained outer payload/key owners to
the same identity ledger, then inspect the interior cuts. Finally provide an
actual erasure, last-borrower, placement and reuse contract. Unreachable arrays
and repeated fresh allocations cannot be declared physically reclaimed from
this local-root identity. No recursive reserve, failure cleanup, selected
supplier admission, full cold replay, or new kappa follows here.
