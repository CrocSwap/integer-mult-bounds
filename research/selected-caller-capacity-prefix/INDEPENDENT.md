# Independent caller allocation-prefix audit

The proposed numerical capacities are sufficient in the stated first-width
domain:

```
C_R >= max(K_R, L_R + 37672),
C_I >= max(K_I, L_I + 41).
```

This conclusion uses PR2835's **closed coefficient prefix** contracts as an
explicit premise. It does not assume a completed successful reference execution
of `Consumer.apply`. The non-coefficient sites of unchanged PR2697 have the
prefix bounds below, including an allocation which has been requested but has
not yet passed the capacity test. No counterexample to those bounds was found.

This is a separate source derivation and finite witness implementation prepared
with OpenAI Codex, not an independent human review or a formal-kernel proof.
The unchanged runtime is Jose Manuel/jmbarrancoml's PR2697 at
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`, exported by the frozen PR2825
predecessor at `b553e912bcddef550d9fae6033041ff683399ebe`.
The successful-call bounds and allocation inventory are credited to PR2825,
PR2821, PR2815, PR2810 and their component predecessors. The strengthening here
is the source-site prefix argument, not a new sharp constant. PR2835 at
`a06f5339a1ee22017f6099cb1dfc1c93c212c424` supplies the separate coefficient
premise; PR2831 at `741e4c852b39fb05ee5343bd2b41cf3d9b8b4a6c` supplies the
backing-capacity comparison. Their recorded proofs are not treated as a fresh
acceptance or proof of changed source.

## Domain and precise assertion

The dimension is 64, `64 <= parent_size < 128`, and good rank is 1 through 42.
Programs, fields, low specifications, requests, units, prime powers, numerical
widths/margins and separate positive cardinality tapes satisfy the unchanged
source's admission and representation contracts. Program depth, the number of
physical prefixes, positive count extents and all finite loop lengths may be
arbitrary within those contracts. This does not certify membership of any
particular real selected catalogue.

The residue and index arenas are distinct, have fixed widths, and start in a
canonical state: their `K_j` allocated slot identities partition into `L_j` live
slots and a duplicate-free free stack. Free slots are erased with restored heads.
`L_j` counts **all** entry residents, including unrelated matrices, Ring/Context
Words, parent size/depth, retained caller outputs and suspended parent data.
Arena templates are permanent separate arrays. Execution is sequential; no
external Word construction, resizing, arena-metadata mutation or host allocation
failure is in scope. Specifications, plan/binding providers, observers and
payload factories allocate no numerical Words and satisfy their semantic
contracts. Merely restoring an observer's final live set would be insufficient.

Before `Arena.zero` performs its test, let its demand be the current live-slot
count plus one, whether it will use a free slot or request a new backing array.
At all ordinary numerical states count the current live slots. The assertion
is that every such prefix up to the first source/host error is bounded by
`(L_R+37672,L_I+41)`. If all separate noncapacity validity and termination
contracts hold, the displayed capacities rule out a first numerical inventory
failure and hence capacity is not an additional success premise.

This statement does not assert exception safety. In particular directory,
Geometry and Layout constructors can allocate before their caller enters its
cleanup `try`; a too-small quota can leave numerical objects behind. The proof
prevents that rejection at the stated quotas rather than relying on cleanup to
repair it. After a first error no continuing valid execution is claimed.

## Why a prefix proof is different

Use an effect `(P,N)`: every prefix, including a pending allocation, uses at most
P additional Words; a normal return has N retained outputs and preserves its
borrowed entry residents. Sequence has effect

```
(P1,N1);(P2,N2) = (max(P1,N1+P2), N1+N2).
```

For a finite prefix, take the last component which has already returned. Use
its established net effect, and the prefix effect of the unfinished component.
No future normal return is assumed. A loop whose completed iterations restore
the same numerical boundary has the maximum iteration peak, independent of its
iteration count. A constructor allocating k cells has all partial list prefixes
bounded by k, even if its kth allocation is the one which would fail.

The source primitives in `predecessor/vendor/words.py` have prefix peaks: copy,
literal, unsigned add/subtract each one; `times_small` two; unsigned division
four; modular multiplication four; modular inverse ten. Each returned numerical
output is included. Division keeps scan, quotient and an old remainder while
requesting its replacement. If a subtraction is needed, the old remainder is
already freed before the subtraction output is requested. Multiplication keeps
scan and its current result/double beside an at-most-two-Word modular addition.
Inverse has a four-Word Euclidean invariant, then retains returned quotient and
remainder beside a four-Word multiplication; its later replacement/cleanup is
smaller. All completed iterations restore these invariants before their next
allocation. Zero values still own Words. Compare, increment, erasure, free,
rewind and close do not allocate numerical Words.

The remaining source audit below uses these prefix effects. The closed
coefficient premise is precisely PR2835's prefix effect `(37672,22)` for an
adapter or `(20494,22)` for a delegated child, each retaining one fresh residue
on normal return and restoring all its other owned numerical state. It is not
inferred from the older successful-call-only contracts.

## Directory, setup and validation

`directory.produce` first completes `high_power`. Each `radix_power` keeps its
divisor and power while division requests at most four Words, hence residue
prefix six; successful exhaustion frees both. Each subsequent `old_prefix`
materializes one old residue at a time, serializes it, and frees it before the
next. It returns before the high odometer is constructed. The nested odometer
list comprehensions request at most `64*64=4096` live residues, including their
last pending request. Advancement allocates none. The odometer is closed before
the next old prefix is decoded. No part of this phase allocates an index Word.
Thus directory production is `(4096,0)` above the apply entry.

The initial width division retains divisor and one beside at most four division
Words. It frees divisor and remainder, constructs fields, frees one, then
Geometry retains three more indices. Exactly five new indices are then retained:
columns, fields, Geometry's one, two and leaf cutoff. In `Layout.__init__`,
`core` and `remaining` coexist with the two-Word `times_small` constructing
`extra`; later `core,extra` coexist with the two-Word construction of `total`.
The pending peak is therefore `5+4=9`, while the constructor retains only
`5+3=8`. A budget of eight misses a real pending allocation. All prefixes of the
initial arithmetic/Geometry construction fit this nine-Word bound.

For initial validation, the actual `Callback` constructor needs at most
`(12,15)` above its entry, as follows directly from `controller.py` and
`records.py`. `_prime_power_context` has at most its divisor, high cap and test
beside four division scratch: seven residues. After it returns, high cap and
the decoded root unit remain; the latter's inverse takes at most ten extra
residues, for twelve. The rest of validation allocates no residues.

The constructor owns five persistent indices during the main validation loop:
one, 64, two, root size and depth. Current and count give seven; a new level
gives eight. `Program.step` seeks using at most three more indices, frees those,
then decodes parent and child, giving ten. The first four-Word division peaks
at fourteen. After its remainder is freed, f remains; a halving unit step's
second division therefore peaks at **fifteen**. A good step's `times_small`
and an unhalved step's copy are smaller. Expected child is freed before the
field-code seek; that seek has at most fourteen. Replacing current/count with
child/level restores the seven-index loop boundary. The final after/seek/check
phase has at most ten, including at depth zero. These are allocation-site
prefix bounds for all finite histories, not statements about a future return.
The normal closed frame retains six indices/two residues and frees them all.

The caller's eight retained indices add to this constructor, giving `(12,23)`.
Read-prefix copies, `Fields` construction and record/count tapes allocate no
numerical Words. On reaching the packet engine, exactly the eight caller
indices and no caller-owned residue scratch remain. The validation frame's
rollback paths add no allocation, but no global rollback guarantee is needed.

## Trace construction and suspended events

The first-range check gives `columns=1`. Trace lifetimes are source-local and
independent of program depth and count extents; Geometry aliases the borrowed
depth/columns, rather than copying them.

An adapter callback suspends the trace with loop coordinate j, target, source
and request coordinate: four indices above the eight caller residents. During
`point`, base/last/reverse/result can coexist; with j and a previously returned
endpoint this is at most six trace indices. Hence construction is at most
fourteen total, while callback entry is twelve. PR2835's 22 extra indices give
the complete adapter interval `(37672,34)`.

For a child the four boundary Words are first, second, width and depth. In the
leaf loop, i, left, last, tail and right can coexist with that boundary, giving
nine trace indices. Last and tail are freed **before** primitive operands a,b
and the copied request coordinate are allocated. At a child ADD suspension the
owned list is

```
first, second, width, depth, i, left, right, a, b, request.coordinate.
```

There are ten in a good child. Fallback `pair_command` additionally retains
half, which equals zero in this width range. It stays live throughout the
middle unit/pair child, while the half-child stages are skipped. Consequently
good and fallback callback entries have exactly 18 and 19 indices above apply
entry, respectively. The closed child prefix therefore composes to
`(20494,40)` or `(20494,41)`.

The remaining trace constructions fit the same nineteen-index cap. Good child
first/second/width construction uses at most the two-Word `times_small` effect;
the disjointness end Word is freed before depth is allocated. Fallback initial
half-division uses four scratch, retains half, then middle-child endpoint
construction uses at most two scratch. Leaf operand construction adds two
copies, and ADD requests its coordinate only after those copies. Sign frees a
before yielding b; atom swap retains both a and b. Thus atom-swap suspension
has at most eighteen total indices, sign at most seventeen.

Return construction `replace(boundary, kind="return")` copies object fields,
not numerical Words. The leaf's i/left/right and primitive copies have already
been freed before that return yield. Packet-engine `active` aliases the entry
boundary. Return comparison/rewind allocates nothing, then the boundary Words
and fallback half are freed while unwinding. A retained Python reference to an
erased previous event does not revive its slot; the still-allocated backing
array is a separate category below. Generator close, successful loop cleanup
and the caller's final cleanup allocate no numerical Words.

## Layout, ADD and non-ADD execution

`Layout.fibre` uses only nonnumerical count tapes and `radix_power`'s six
residues; the eight caller indices remain. `Layout.extents` has a binary
four-index peak: a,b coexist with either after,count or distance,count. Its
unary version has a,after,count, hence three. The `physical` methods and their
partial prefixes are smaller. All these indices can coexist with the six
radix residues; the categories must be added. They are all freed before
`action` invokes ADD or a non-ADD primitive. The extents returned by Layout
are count tapes and own no arena Word.

Each ADD traversal calls its coefficient once before allocating x. The fresh
returned coefficient and x coexist with at most four multiplication scratch,
giving six residues including the coefficient. After multiplication returns,
offset and a newly requested leading Word give only four total. Every inner
offset/leading pair is freed before the next source atom, x before the next
outer block, and the coefficient before the second traversal requests another.
No coefficient scratch coexists with the later six-Word interval. Payload
copying and count decrement/normalization allocate no numerical Words.

`atom_swap` first fully exhausts its two separate `digit_suffix` calls, and
`sign_address` exhausts its one. Their main radix loop requests at most six
residues, retaining only divisor and power during each digit payload operation.
Digit swap/complement and opaque copying allocate no numerical Words. After
the sign radix loop exhausts, its divisor and power are freed **before**
`translate_one` requests its one leading Word. Thus both complete non-ADD
primitive prefixes are at most six residues and zero new indices and restore
their numerical entry state on normal return.

The complete non-coefficient ledger is consequently:

| Phase | Residue demand | Index demand |
| --- | ---: | ---: |
| Directory, including partial odometer | 4096 | 0 |
| Width, Geometry and partial Layout construction | 0 | 9 |
| Initial validation with caller retained | 12 | 23 |
| Packet fibre | 6 | 8 |
| Trace advance, construction and return | 0 | 19 |
| Child ADD extents | 6 | 23 |
| Child atom-swap extents | 6 | 22 |
| Child sign extents | 6 | 20 |
| Atom-swap/sign after extents | 6 | 18 |
| ADD outside coefficient calls | 6 | 19 |

Every entry includes pending allocation requests above the same apply-entry
baseline. These are coordinatewise bounds, not assertions of simultaneous
attainment. Adapter extents are smaller than the corresponding child rows.
All rows are dominated by the child rectangle `(20494,41)`. With the separate
adapter and child coefficient contracts the whole prefix lies in the union of
the rectangles `(37672,34)` and `(20494,41)`. Thus the earlier weighted envelope
also bounds prefix demand for all positive complete Word widths; it is not
necessary to weaken it to the single enclosing rectangle.

## Capacity contradiction and backing implication

Assume a first inventory rejection. Earlier completed allocation/free operations
preserve the canonical partition; unfinished erasure adds no demand. If a free
slot exists, `zero` reuses it and cannot reject for capacity. Otherwise all
currently allocated slots are live. The proved demand bound gives

```
K_current + 1 = live_current + 1 <= L_j + B_j <= C_j,
```

contradicting the literal guard's rejection condition `K_current >= C_j`.
The premise `C_j >= K_j` also admits all entry backing arrays. This proof uses
only the already executed prefix and the next requested slot. It applies to
arbitrary canonical warm free-stack order and requires no successful reference
execution, high-water measurement, or clean/empty entry arena.

The same induction gives allocated arrays at most `max(K_j,L_j+B_j)` at
allocation boundaries. A Word being constructed before append/live insertion
is covered by its pending reservation. Including the permanent template and
both marker positions, the numerical Word-array capacity is bounded by

```
(max(K_R,L_R+37672)+1)*(b_R+2)
  + (max(K_I,L_I+41)+1)*(b_I+2).
```

This charges erased arrays as well as live ones. It is the numerical backing
component, not a whole Python heap bound, packed physical tape theorem, all-size
recursive reserve or selected-supplier admission. Payload, count/directory/
program/continuation tapes, keys, object metadata, physical placement and head
movement retain their separate obligations. No new kappa follows.

## Independent finite witnesses and limits

`independent.py` imports neither the package's verifier nor any predecessor
verifier. It checks the fixed SHA256 of `predecessor/runtime.py`, which checks
the frozen source inventory by SHA256 and Git blob and compiles the authenticated
bytes. Its arena subclass observes `live+1` **before** delegating to the unchanged
`Arena.zero` guard; it does not replace the source quota test with a simulated
success. The finite witnesses exercise actual constructor/primitive/trace sites.

The positive fixtures use literal capacities at the named local bound. Separate
one-slot-short controls are required to encounter the actual inventory guard at
the claimed next request. This includes the incomplete 4096-Word odometer, the
nine-index Layout constructor, 10/14/15-index validation classes, binary/unary
extents, the sixth radix/primitive residue, and the 18/19-index child ADD trace.
The validation failure controls additionally check the constructor's own abort
restoration. Other undersized controls do not claim rollback restoration.

The finite domain is three validation histories (depth zero, one unhalved unit,
one halved unit), modulus 5/root unit 2; directory construction at dimension 64;
radix modulus 27; width-127 Layout with unit count extents; good traces at ranks
1,21,42 using the literal compiler; a ten-child fallback control-path word using
five endpoint pairs and both unit/pair kinds, plus adapter/sign; and complete
ADD/swap/sign payloads of 25/81/9 bits. Good/fallback trace checks use width127,
depth3; they execute no closed coefficients or full Boolean selected packet.
The synthetic fallback word is a control-path superset, not an assertion that
it is an admitted complete normal form. The written source argument covers all
admitted finite programs, widths 64..127, ranks 1..42 and count extents; the
finite fixtures do not enumerate that domain.

Run from the repository root:

```
python3 -I -B research/selected-caller-capacity-prefix/independent.py
python3 -I -O -B research/selected-caller-capacity-prefix/independent.py
```

The checker prints its measured finite counts and explicit coverage limits.
Both commands passed on 2026-10-16. Each run covered 15 positive fixtures and
13 one-slot-short literal rejection controls. The three complete good traces
yielded 36,938 events and the fallback control word yielded 102; pending peaks
were respectively 18 and 19. All three validation classes measured residue
peak12 and index peaks10/14/15. Full small ADD, swap and sign each measured six
residue Words. These observations are not claims that the full caller's
37672/41 rectangle is jointly sharp.
Its evidence is finite corroboration of a conditional all-parameter written
source proof. There is no formal-kernel proof, fresh coefficient verification,
complete physical reserve, new supplier admission or new exponent claim.
