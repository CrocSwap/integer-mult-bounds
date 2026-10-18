# Independent caller and non-ADD lifetime audit

The proposed weighted envelope is valid for the named numerical-content model,
conditional on the PR2796 child and PR2781/PR2801 adapter contracts. The child
callback has **18 additional index Words in the good caller and 19 in fallback**
before the closed coefficient call begins. Its surrounding first-range phases
do not exceed the envelope

```
max(37672*r + 34*i, 20494*r + 41*i),  r = b_R+1, i = b_I+1.
```

This independent audit was prepared with OpenAI Codex as a storage-lifetimes
specialist. It uses the unchanged Jose Manuel/jmbarrancoml PR2697 runtime at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, exported through PR2801 and the
PR2821 handoff `78b0d364ec4441e46e6ccffc60bf341536cbd756`.
Nick Petalas's PR2759/2770/2781 and Arham Tahir's PR2796 supply
the credited component contracts. The primary verifier is not imported or
used by the independent checker. The inspected closed-call proof pins are
PR2781 `9fdbd4b0429dbfcb4569f7768b66d318deacab6b` and PR2796
`f9a6245cfdcae0b920fcbc9c79c4fb73a2706605`.

## Domain and common baseline

Fix distinct residue and index arenas, dimension 64, parent width
`64 <= n <= 127`, and a successful admitted `Consumer.apply` invocation. Good
ranks are 1 through 42. Program/history/source bindings, units, margins, prime
power and complete words satisfy the pinned source contracts. Canonical positive
count tapes may have arbitrary extents. All entry numerical residents remain
charged to the same baseline, including unrelated matrices, retained outputs,
context/Ring residents, parent width and depth. Specifications, plan binding
and observers allocate no numerical Words. Numerical execution is sequential.

The numbers below count *additional occupied arena Words*, not Python objects,
count tapes or all physical storage. With slot-count baseline `(L_R,L_I)`, the
complete occupied non-LEFT numerical-symbol bound adds
`L_R*r + L_I*i + r + i` to the displayed envelope; the final `r+i` charges the
two unchanged permanent arena templates. If those templates already belong to
the content baseline, do not add them again. LEFT markers, erased backing
capacity, payload, directory/count/program/continuation tapes and their physical
movement are outside this result.

## Suspended child callback

The first-range test fixes `columns=floor(n/64)=1`. At packet-engine entry the
caller owns eight index Words above baseline:

| Owner | Words |
| --- | ---: |
| `Consumer.apply`: columns and fields | 2 |
| `Geometry`: one, two and leaf cutoff | 3 |
| `Layout`: core, extra and total | 3 |

The temporary validation `Callback` is closed before engine entry. Directory
construction has already freed its high-field odometer. Neither leaves any
additional residue Word here.

At a child ADD yield, the suspended generator owns:

| Resident | Good | Fallback |
| --- | ---: | ---: |
| Child first, second and width | 3 | 3 |
| Child depth | 1 | 1 |
| Leaf loop index `i` | 1 | 1 |
| Retained left and right positions | 2 | 2 |
| Primitive copied operands `a,b` | 2 | 2 |
| Copied request coordinate | 1 | 1 |
| `pair_command` half-width | 0 | 1 |
| Total trace residents | 10 | 11 |

The half-width remains a live Word even though its value is zero. The two
half-child branches are skipped because `columns=1`. The unit and pair middle
children both retain this Word, so the callback entries are exactly `(0,18)`
and `(0,19)` above the common baseline.

`layout.extents` finishes before `add_pass.traverse` calls its coefficient
callback. Its returned extents are count tapes and all numerical temporaries
have been freed. `read_prefix`, the local payload copy, prefix counters and
`Fields` construction likewise retain no new arena Word. Thus PR2796's
above-all-entry `(20494,22)` allowance gives `(20494,40)` and `(20494,41)` at
these actual caller sites. No componentwise sharpness or simultaneous
attainment is asserted.

There is no omitted current-event Word. `active` aliases the enter boundary;
`replace(boundary, kind="return")` aliases its four Word-valued fields.
`event` and `request` are containers, and `page.columns` is borrowed. Primitive
cleanup erases the previous event's operands and coordinate before construction
of the next event. Retaining a Python reference to the erased Word object does
not leave its former numerical content occupied. It may retain backing cells,
which are expressly a different category here.

## Construction, non-ADD, return and cleanup

The following bounds cover all phases outside the closed coefficient calls.
Pairs are `(residue,index)` excess above the same `Consumer.apply` baseline.

| Phase | Bound |
| --- | ---: |
| Directory production | `(4096,0)` |
| Caller division, Geometry and Layout setup | `(0,9)` |
| Initial validation Callback, with eight caller indices retained | `(12,23)` |
| Packet-fibre count construction | `(6,8)` |
| Trace construction/advance/return/cleanup | `(0,19)` |
| Child ADD extents construction | `(6,23)` |
| Child atom-swap extents construction | `(6,22)` |
| Child sign extents construction | `(6,20)` |
| Non-ADD execution after extents construction | `(6,18)` |
| ADD traversal after callback return | `(6,19)` |

Here is the source lifetime justification, including the transient interiors.

* `directory.produce` completes `high_power` before creating an `Odometer`.
  `old_prefix` decodes at most one residue at a time and returns serialized
  data before the odometer exists. The odometer retains exactly `64^2`
  residues; advancement allocates none. It is closed before the next old
  prefix. `high_power` uses at most the six residues established below.
* Initial width division retains divisor and one beside four division
  temporaries. Later Geometry/Layout construction peaks at nine: five caller
  indices, `core`, and `remaining` coexist with the two-Word `times_small`
  interior constructing `extra`. After freeing `remaining`, the five caller
  indices, `core` and `extra` coexist with that interior constructing `total`.
  Eight survive the completed setup. The initial frame
  validation retains these eight indices and adds its source-bound `(12,15)`
  allowance. It is then closed. Its count is a component hypothesis also
  derived in the credited closed-callback lifecycle proofs.
* `radix_power` retains divisor and power beside at most four division
  temporaries, for six residues. Its successful exhaustion frees both. The
  surrounding cardinality operations use count tapes, not index/residue arena
  Words. A `Counter` copying an encoded Word does not allocate another Word.
* During two-position `Layout.extents`, the physical positions `a,b` coexist
  with either `after,count` or `distance,count`: at most four extra indices.
  During one-position extents the corresponding maximum is three. These
  indices can coexist with all six radix residues, so they are added, not
  maximized separately. The largest suspended atom-swap caller has 18 indices;
  the largest suspended sign caller has 17. All such indices are freed before
  `action` enters the payload primitive or ADD callback.
* `atom_swap` and `sign_address` first exhaust each `digit_suffix` call.
  Their main radix loop has at most six residues during division and two
  while the digit payload operation runs. Digit swap/complement and opaque
  copying allocate no arena Words. After the sign loop is exhausted,
  `translate_one` allocates just its single `leading` residue and later frees
  it. No radix pair survives into that translation.
* After an ADD callback, only its one returned coefficient remains. `x` adds
  one residue and multiplication uses at most four more, giving six. Computing
  `leading` is smaller. Every offset/leading pair and `x` is freed, and the
  coefficient is freed before the second traversal requests a fresh one.
* Within trace construction, good `first,second,width` coexist with at most
  the two-Word `times_small` interior. The disjointness `end` is freed before
  child depth is made. In a leaf, `i,left,last,tail,right` accompany the four
  boundary Words, giving nine trace Words, or ten with fallback half. `last`
  and `tail` are freed before the primitive copies and coordinate are made;
  the later ADD suspension is the larger ten/eleven. An adapter `point`
  calculation uses at most six trace indices including its retained loop and
  first endpoint. Fallback half-division and all pair endpoint calculations
  are smaller than eleven. Return frees the leaf loop/position/primitive
  residents before yielding its aliased boundary. Cleanup only frees or
  rewinds numerical Words.

Every row in this table is componentwise dominated by `(20494,41)`.
Conditionally taking PR2781/PR2801's complete adapter-action rectangle
`(37672,34)`, the two types of ADD callback and these disjoint remaining phases
therefore imply the displayed weighted maximum for every `r,i > 0`.
This is a maximum of *jointly applicable phase bounds*; it does not silently
combine incompatible sharp witnesses.

## Finite independent check and its limits

Run from the repository root:

```
python3 -I -B research/selected-child-caller-lifetime/independent.py
python3 -I -O -B research/selected-child-caller-lifetime/independent.py
```

`independent.py` pins the snapshot itself, authenticates all exported source
bytes by SHA256 and Git blob before execution, and compiles those bytes directly.
It uses the original `trace.execute`, actual binary Words, Geometry and Layout.
A separate integer oracle checks every yielded event's positions, width,
depth, child kind, pair reversal, coordinate and negative-inverse flag. It
counts actual live sets at every yield and source allocation peaks over the
complete runs, independently of the primary verifier. Every yield checks the
eight caller residents' bytes and restored heads; completed/closed traces
check exact restored ownership and erased released content.

The finite domain is good ranks 1--42 and a synthetic fallback command word
containing every ordered endpoint pair `0 <= first < second < 128` for each
of unit and pair children, every ordered ADD endpoint pair, and every sign
field 0--127. The synthetic command word is a control-path superset, not a claim
that this concatenation is one admitted normal-form plan. Parent width 127
and depth 3 are the executed representatives; first-range trace behavior is
width-independent because columns is always one. The proof above, not those
representatives, covers other widths, depths, extents and admitted histories.

Semantic controls require rejection of a charge of only 18 indices on the
fallback child ADD, an unclosed suspended generator, a corrupted borrowed byte
and a displaced borrowed head. These checks corroborate the trace census and
cleanup. The direct run passed 7,308 good events and 170,816 fallback events,
including source allocation peaks of respectively 18 and 19 indices above
baseline. Ordinary and optimized execution both passed; the final corrected
setup peak of nine was also checked during every optimized fixture setup.
These are finite trace measurements, not global sharpness of either inherited
rectangle. They do not replay PR2796's coefficient kernel or validate its constants,
run the complete GL64 payload, establish exception safety, or certify physical
storage. The all-domain statement is the written conditional source-lifetime
proof above; no formal-kernel proof is supplied. The complete physical reserve,
backing reuse and stronger supplier/kappa implications remain open.
