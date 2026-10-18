# First numerical capacity failure in the first-range caller

This is a written source proof for Jose Manuel/jmbarrancoml's PR2697,
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1`. Exact unchanged runtime files are
in `predecessor/vendor/`. The new step is the non-coefficient prefix obligation
left by PR2835. It does not claim new arithmetic constants or a complete
physical reserve. PR2825 previously composed these lifetimes for successful
calls; PR2831 identified why that premise alone was insufficient for capacity
admission. We do not infer a prefix bound from a successful test run.

## Domain and conclusion

At entry to `Consumer.apply`, residue and index arenas are distinct, fixed-width
canonical PR2697 arenas. For arena j let K_j be allocated slots and L_j all live
slots, including every borrowed resident, modulus, Ring.one, Context.cap,
incoming frame and unrelated suspended caller. Free slots are erased, have
head one, and partition K_j together with live slots; the free stack contains
no duplicate. Templates and incoming Words obey the source contracts.

Retain the unchanged source's legal input/program/field/ownership contracts:
dimension 64, `64 <= parent_size < 128`, ranks 1..42, fixed prime q and admitted
positive prime-power modulus, canonical residues and separately canonical
positive count extents, chronological generated finite programs with proper
child widths, valid source tables and index/value margins. Sources, observers,
specification lookups and payload factories allocate no numerical Words and do
not modify arena metadata. All source/program contents are fixed for this call.
No concurrent mutation, external Word construction or host allocation failure
is modeled. Noncapacity semantic validity and termination remain obligations;
actual selected catalogue membership is not established here.

For closed coefficient calls we use **PR2835's prefix contracts**, not the
older successful-call formulation: adapter `(37672,22)`, child `(20494,22)`
above all coefficient-entry residents, with one fresh returned residue and
normal-return restoration of all borrowed state. Its source proof covers
pending allocation requests; it corrects the halved extension interior to
eleven indices while preserving the complete child bound 22. The frozen proof
is `evidence/PR2835-PROOF.md`. Its semantic hypotheses remain premises.

Define demand at a request to `Arena.zero` as the current live-slot count plus
one, **before** it succeeds or rejects. The theorem is:

1. On every prefix before the first noncapacity error, including a pending
   allocation, the extra numerical demand above `(L_R,L_I)` lies in the union
   of the two upper rectangles `(37672,34)` and `(20494,41)`.
2. Therefore capacities
   `C_R >= max(K_R,L_R+37672)` and `C_I >= max(K_I,L_I+41)` exclude a first
   numerical inventory failure. No already successful complete reference run
   is a premise. If the independent noncapacity validity/termination contracts
   hold throughout, capacity cannot prevent the call from finishing.

The rectangles are upper bounds, not claims of joint sharpness. For complete
non-LEFT Word widths `r=b_R+1`, `i=b_I+1`, occupied numerical content, including
the two permanent templates, is bounded by

```
(L_R+1)r + (L_I+1)i + max(37672r+34i, 20494r+41i).
```

The new implication removes numerical-success circularity in this restricted
caller. It does not discharge the retained semantic or physical premises.

## Prefix reasoning

A component has prefix effect `(P,N)` if every ordinary state and next
allocation request adds at most P numerical Words and a normal return retains
N fresh Words. Sequential composition is
`(max(P1,N1+P2),N1+N2)`; alternatives use maxima. An iteration that restores its
numerical baseline does not accumulate P across iterations. A partial fixed-size
matrix owns at most its full planned number of slots. Borrowed aliases and
serialized copies on other tape types add no numerical Word.

For any finite prefix, split it into completed components and its final
incomplete component. Completed components supply their proved net effects;
the incomplete component supplies its prefix effect. This induction never
assumes a future successful return. The slot about to be requested is included
at its allocation site. The same argument applies to prefixes of nested loops
and generator suspensions. The only primitive resource premises are the
source-derived division/add/multiply/inverse prefix effects also proved in
PR2835: four/two/four/ten respectively (unsigned subtraction uses one).

## Directory and validation

In `directory.produce`, `high_power` completes before the first old-prefix or
odometer operation. Its radix iterator retains divisor and power and requests
at most four division temporaries, hence six residues. `old_prefix` decodes one
residue at a time and frees it before the next decode and before constructing
the odometer. The odometer builds at most 64 squared numerical digits; advance
mutates them in place. It is closed before the next old prefix. A partial
odometer constructor is bounded by its full 4096 slots, even if it never
finishes. No directory operation allocates index Words. Thus directory prefixes
have `(4096,0)` above apply entry, independently of the number of fields/rows.

Width setup holds divisor and one while division has prefix four, then frees
divisor/remainder. Adding depth to one leaves columns/fields. Geometry adds
one/two/leaf_cutoff, so there are five persistent caller indices before Layout.
Layout owns core, extra and total on return. During construction core,
remaining and the two-word multiplication interior coexist, giving four
Layout indices and **nine** total, although only eight survive setup. Geometry
aliases columns/depth; it does not copy them.

Validation's Callback starts with these eight indices live. Three Callback
constants, root/depth parsing, current/count, a level, the step's parent/child
and f, and the four division temporaries give at most fifteen more indices.
The halved branch retains f during a second division; omitting it would be
incorrect. Repeated program steps free parent/f/old current/old count before
the next step. Fields/code checks use sequential index scans. Callback's
prime-power context retains high_cap; root_unit adds a second residue and
inverse needs ten more, so its residue prefix is at most twelve. Validation
therefore has the loose rectangle `(12,23)`. Completed close returns to the
eight-index, zero-residue caller baseline. The statement is about all pending
requests in initialization/validation, not an inference from the earlier
finite PR2821 successful fixtures.

## Trace, layout and primitive phases

The actual trace's source-site inventory is reproduced independently in
`INDEPENDENT.md`. Briefly, adapter ADD suspensions own four trace indices above
the eight persistent caller indices. A good child ADD owns ten: its four
boundary Words, loop i, left/right, primitive a/b and copied request coordinate.
A fallback child owns one more, the pair command's computed **half=0**. Zero
value does not erase ownership. Thus adapter/good-child/fallback-child
coefficient entries have exactly 12/18/19 extra indices and no residue.

During construction, a leaf has at most nine trace indices before primitive
copies, ten with fallback half; last/tail are freed before the later ADD
suspension. Child interval-end checking frees end before allocating depth.
Division/point/reversal interiors are bounded by these same maxima. Each
previous event is closed before the next one is constructed. Return-event
dataclass copies alias existing Words. Identity/extent checks, rewind and
normal cleanup allocate no numerical Word. A completed child returns with
the parent's numerical residents intact under its retained contract.

`Layout.extents` first retains physical a/b (only a for a unary primitive).
The after/count or distance/count pair raises its index prefix to four binary,
three unary. Its radix arithmetic uses at most six residues. Those temporaries
are freed before an ADD coefficient or non-ADD body runs. Its input/output
extent objects use separate count tapes. `Layout.fibre` uses the same radix
effect and no numerical index. Therefore the non-coefficient ledger is:

| Phase | Residue prefix | Index prefix |
| --- | ---: | ---: |
| directory | 4096 | 0 |
| setup | 0 | 9 |
| validation | 12 | 23 |
| packet fibre | 6 | 8 |
| trace construction/suspension/return | 0 | 19 |
| ADD extents | 6 | 23 |
| swap extents | 6 | 22 |
| sign extents | 6 | 20 |
| non-ADD body | 6 | 18 |
| ADD outside coefficient | 6 | 19 |

For `atom_swap` and `sign_address`, `digit_suffix` invocations are exhausted
sequentially before the main radix loop. Every radix loop retains two residues
and temporarily requests four division Words; it frees the old power and
remainder before yielding. Digit-swap/complement bodies allocate no numerical
Words. Sign's `translate_one` requests one residue only after the radix pair
has been freed. These facts prove the six-residue prefix, including the first
division request, at every admitted positive exponent.

In each `stream.add_pass` traversal, coefficient evaluation precedes x and
offset construction. With its fresh coefficient and x retained, multiplication
needs four more residues: six total. After multiplication, offset and the
single subtraction result fit under six. Offset/leading and then x are freed
within their respective loops. The coefficient is freed before the second
traversal begins. Numerical-neutral counting, observation and copying cannot
increase this inventory. Consequently a restored fresh-result callback with
prefix `(R,I)` composes to `(max(R,6),I)`, not `(R+6,I)`.

## Composition and the first-failure contradiction

Applying PR2835 at the actual callback entries gives adapter `(37672,34)`,
good child `(20494,40)` and fallback child `(20494,41)`. The non-coefficient
rows are all dominated by the last rectangle. All phases use the same apply
entry baseline and all normal completed prefixes restore their listed resident
invariants. This establishes the two-rectangle prefix statement.

Suppose a first inventory-rejecting zero request exists before any other
error. All earlier successful arena operations preserve the canonical slot
partition. If a free slot exists, zero reuses it without a capacity rejection.
Otherwise all currently allocated slots K_t are live, and rejection requires
`K_t >= C`. The pending bound gives `K_t+1 <= L+B <= C`, a contradiction.
Entry feasibility also requires `K<=C`. Apply this argument separately to the
two arenas. It permits arbitrary canonical warm backing and free-stack order.
Error paths are not asserted to clean up completely; the first-failure proof
does not rely on cleanup after an error.

PR2831's separately proved backing recurrence then bounds retained numerical
Word.cells arrays, including erased slots, templates and LEFT/RIGHT positions,
by

```
(max(K_R,L_R+37672)+1)(b_R+2)
 + (max(K_I,L_I+41)+1)(b_I+2).
```

Each arena retains its own historical peak; substituting a simultaneous
weighted live peak would be unsound. An array under construction is covered
by the pending slot reservation. This is the arena's representation measure,
not total Python heap or a completed physical-tape reserve.

## Evidence and excluded implications

The primary checker reuses the credited frozen PR2825 source fixture/harness
and adds pre-allocation observation, fixed actual quotas, warm backing and
underquota failures. Coefficient bodies and full GL64 payload movement remain
abstracted in caller probes; synthetic 22-index child scratch tests composition
and is not an execution of a real full coefficient. Separate complete small
ADD/swap/sign fixtures execute Boolean payloads and literal arithmetic.

`independent.py` and `INDEPENDENT.md` are a separate AI source audit. Neither
finite evidence nor AI independence is a formal proof kernel or human review.
The all-parameter claim is the written conditional source argument above.
Payload/count/directory/program/continuation storage, allocator metadata,
physical placement/movement, recursive/outer borrowing, H2 and selected
supplier admission remain separate. No new exponent or frontier change follows.
