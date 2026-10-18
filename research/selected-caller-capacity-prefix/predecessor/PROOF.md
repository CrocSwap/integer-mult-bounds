# Child entry and the remaining numerical phases

The result concerns unchanged PR2697 `Consumer.apply`, with source hash pins
in `evidence/PR2801-SNAPSHOT.json`. All statements below are conditional on
successful, sequential execution satisfying the original source contracts.
The permanent Ring, directory Context and incoming numerical objects already
exist on entry. Let `(L_R,L_I)` count **all** live residue/index Words then,
including unrelated borrowed matrices and suspended parent data.

The arenas are distinct. Dimension is 64, parent width is `64 <= n < 128`, good
rank lies in `1..42`, and all programs, source bindings, residues, units, prime
powers, index margins and separately canonical positive count extents are
admitted by the pinned sources. Specifications, observers and payload factories
allocate **no numerical Words**. Merely restoring an observer's entry state is
insufficient to bound its transient scratch. Successful coefficient calls obey
the separately pinned fresh-result and restoration contracts. This is not an
exception-rollback statement.

Every new Word is initialized by `Arena.zero`; frees erase before reusing a
slot. Therefore a live-slot upper bound gives an occupied-content upper bound
at every intermediate cell operation: incomplete initialization and erasure
cannot exceed the complete Word content. Erased backing cells and LEFT markers
are excluded from this particular measure.

## Exact child callback entry

After initialization and validation the caller retains eight indices:
`columns, fields`, Geometry's `one,two,leaf_cutoff`, and Layout's
`core,extra,total`. Geometry aliases columns and depth; it does not own copies.
The preceding directory and validation frame leave no residue scratch. This
is the entry convention established by PR2801 and PR2821.

For a good child the trace retains `first,second,width,depth`, loop coordinate
`i`, `left,right`, primitive copies `a,b`, and the copied request coordinate:
ten distinct indices. Fallback `pair_command` additionally retains its computed
`half`. Here columns is one, so half is zero and the half-child stages are
skipped. The zero-valued Word is nevertheless owned until the middle child
returns. This gives exact child callback entry increments

```
good:     (0,8+10) = (0,18)
fallback: (0,8+11) = (0,19).
```

The same counts hold for both split and merge callback invocations. The actual
`action` first completes `Layout.extents`; every numerical temporary is freed
before ADD calls its callback. Extents, prefix copies, fields and counters are
serialized/count tapes, not arena Words. The coefficient has not yet been
returned when the callback starts. Both completed ADD traversals free their
coefficient before another callback begins.

The active child, boundary, current event and request objects alias the above
Words. `replace` on the return event copies the dataclass fields, not their
Word contents. A previous primitive is closed and its Words erased before the
generator constructs the next event; retained Python references to erased
objects are backing-storage obligations, not occupied numerical content.

PR2796 proves that the closed child coefficient uses at most `(20494,22)`
above **all** its entry residents and returns just one fresh residue. Thus the
complete child ADD interval has conditional allowance `(20494,40)` for good
and `(20494,41)` for fallback, using PR2810's sequential ADD composition.
This instantiates the previously unspecified caller entry. It neither reruns
the full child arithmetic nor claims that these composed maxima are sharp.

## All other phases

The following is a coordinatewise upper ledger relative to the same
`Consumer.apply` baseline, not a list of simultaneous sharp peaks.

| Phase | Residue Words | Index Words |
| --- | ---: | ---: |
| Directory production | 4096 | 0 |
| Width, Geometry and Layout construction | 0 | 9 |
| Initial validation, caller retained | 12 | 23 |
| Packet fibre construction | 6 | 8 |
| Trace advance, construction, return and cleanup | 0 | 19 |
| Child ADD extents | 6 | 23 |
| Child atom-swap extents | 6 | 22 |
| Child sign extents | 6 | 20 |
| Atom-swap/sign execution after extents | 6 | 18 |
| ADD outside its callback | 6 | 19 |

Directory and validation bounds are credited to PR2810 and PR2821. The loose
validation rectangle is sufficient here; PR2821 gives the finer joint prefix
bound. Setup briefly reaches **nine**, despite retaining only eight: five
pre-Layout indices coexist with Layout's four-index constructor peak. Counting
only completed owners would miss this transient.

Trace construction requires no residue Word. In a leaf, before making
primitive copies, the four boundary Words coexist with `i,left,last,tail,right`.
That is nine trace indices, ten with fallback half. `last,tail` are freed before
the later ten/eleven-index ADD suspension. Child disjointness frees `end`
before allocating depth. The two-Word multiplication, four-Word half division,
adapter point/reversal interiors and all return/cleanup paths are smaller.
The complete source-site argument and independent integer event census are in
[INDEPENDENT.md](INDEPENDENT.md).

`Layout.extents` has a four-index binary or three-index unary peak, above its
entry, and six residues during radix operations (PR2815). The largest suspended
child swap owns 18 indices, sign 17, and ADD 19. Hence the three extents rows.
These temporaries finish before any coefficient or primitive execution.

For the non-ADD routines, `radix_power` retains divisor and power while division
uses at most four additional residue Words. Six is exact, including its first
division. It keeps only two between yields and frees both on successful
exhaustion. `digit_suffix` calls are exhausted sequentially before the main
loop. Digit swap/complement and opaque copying use no numerical Words. After
the sign radix loop ends, `translate_one` allocates one leading-count residue;
the radix pair is no longer resident. Thus both complete primitives use exactly
six additional residue Words and zero indices for every valid positive radix
exponent; after return they restore the numerical entry state.

ADD's six-residue bound already includes its returned coefficient (PR2810):
coefficient plus x plus at most four multiplication temporaries. Coefficient
evaluation is a disjoint phase and cannot be added to those six. Return events
compare/rewind borrowed words without allocating. Successful final cleanup
only frees caller numerical state and clears or rewinds separate tape types.

## Conditional whole-call numerical corollary

PR2781/2801/2810/2815 give the complete adapter-action allowance `(37672,34)`;
the preceding derivation gives child allowance `(20494,41)`. Every other row
is componentwise dominated by the latter. With positive complete Word widths
`r=b_R+1`, `i=b_I+1`, occupied non-LEFT numerical content is therefore at most

```
(L_R+1)*r + (L_I+1)*i + max(37672*r + 34*i, 20494*r + 41*i).
```

The two `+1` terms charge the permanent arena templates exactly once. In
particular the coordinatewise allowance is `(37672,41)`. The maximum retains
the stronger fact that different phases supply the two controlling rectangles.
Its branch changes at `7*i = 17178*r`; this is arithmetic about a conditional
upper bound, not a new time/precision tradeoff or sharpness claim.

This written source proof covers all admitted finite depths and extents in the
first width range. The finite checks corroborate it; they do not enumerate all
programs or establish actual selected catalogue membership. The inherited
coefficient proofs remain explicit premises. No whole-node reserve follows:
payload, records, counts, continuations, directory keys, LEFT markers, retained
backing capacity, physical banks, head motion, larger recursive invocations and
the outer borrowing interface all require their own simultaneous accounting.
There is no formal-kernel proof, selected supplier admission or new kappa.
