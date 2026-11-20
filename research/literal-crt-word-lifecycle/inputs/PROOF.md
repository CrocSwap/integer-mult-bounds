# Complete current-source raw arithmetic provider closure

## 1. Exact source, result and retained premises

The canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`. The current
producer is #5053 at `ef9da0a9ac29cf86610a52e3a183bdb28508aa74`, file
`research/encoded-current-crt/producer.py`, blob
`a327b0161eca57a1cc44ec2aa8e3defed2167ddc`. Its `Unsigned` implementation is
`words.py`, blob `8d4ba37e2778acb35b34e0719df2caf138fbeb50`. The inverse file
retained by #7388 at `d6f4a69202ad0bba4a915f4d4f3eaba1fe431c86` changes one
scientific line: a valid right coordinate uses modular subtraction instead
of addition. `SOURCE-PINS.json` authenticates every retained source byte.

The immediate predecessor is the published all-division substitution,
CubeJerry commit `9700fc89e2582a1fb358a4c6d0d0387076192adc` (B11). Its
unchanged physical divider and binder originate in published commit
`c4ab5dab6914a04cb86d1fe54eb763b35cc7eeb1` (B10). The entry, persistent owner,
current header, row/key and payload interfaces are inherited with their
exact pins and notices. No predecessor mathematical or implementation
claim is asserted as new here.

**Theorem.** For every admitted, successful forward or inverse invocation
of the pinned current producer, at the eager physical Entry boundary,
all calls to raw comparison, addition, subtraction and division can use
the fixed graph emitted by `arithmetic.py` through `binding.py`. No old
raw arithmetic provider is required. Numerical source outputs, finite
branch results, borrowed values and source exit semantics agree with the
original producer, up to the inherited weak live/free Word-slot relation.
All accessed input and output heads return; every selector frame is erased
and its head returns at each primitive exit. Complete new instruction,
metadata and physical-history bills are given below. This is a source-bound
provider substitution, not a literal implementation of the whole producer.
Here successful/admitted refers to the original producer. Induction over its
finite source trace replaces each old provider call by the terminating
per-digit primitive proved below; equal finite returns choose the same next
source branch. This proves replacement termination and success, rather than
assuming them as a premise.

The retained Entry ABI has exactly eight protected guard roles0..7 and56
owned numerical roles8..63, each with a distinct actual backing and head.
This physical ABI is narrower than #5053's numerical theorem, which permits
up to eight protected live Words. The guard contents may be arbitrary and
unused; they are not implicitly assumed to be numerical operands. Each
actual operand is a complete P-bit Word, P>=4, with LEFT at0, digits at1..P,
RIGHT atP+1 and head1. The current entry supplies that typed extent; the
new graph never decodes P or obtains it as a host loop counter.

Four additional selector owners have explicit paid eight-cell grants and
heads at their origins. They carry `L six little-endian slot bits R` when
bound and eight blanks when inactive. The finite64-slot metadata binder,
owner acquisition, input framing, current precision/guide, Word lifecycle
and higher source controllers remain supplied and charged. The hypotheses
of the current numerical theorem, including coprime moduli and complete
product below2^(P-1), remain in force. Fault-injection source modes are
outside the successful theorem. No kappa or full foundational-assumption
removal is claimed.

## 2. Literal primitive semantics, including aliasing

The graph has1,304,162 R/W/M/J/H locations and68 physical ports, independent
of P, data, source length and allocation history. Its first336,150
instructions are exactly the B10 graph. Every old entry, setter, branch and
literal operand keeps its old address. The newly compiled segment is
relocated once by adding that constant prefix length to all of its R/J
targets. No old target can enter the new segment. The additional logical
graph has4,503 locations; constructor arithmetic operates only offline on
fixed states and bits. Runtime has no arithmetic opcode or decoded-value
callback.

At the new comparison entry the first two descriptors name the operands.
At addition/subtraction the third names the fresh result. The fourth frame
is unused numerically but is still validated and erased at exit. The
actual binder supplies `(a,b,a,b)` for comparison and `(a,b,out,out)` for
addition/subtraction. Physical ports remain distinct even when descriptor
values coincide. Existing division continues to require four distinct
operand/output descriptors and uses its unchanged graph.

A six-bit literal equality scan classifies whether a and b name the same
physical Word. It restores both selector heads before entering either
arithmetic path. This is essential: the actual producer doubles by
`add(result,result)`. On the alias path there is one operand head movement
per digit, while the distinct path moves each operand once. Equal values
in distinct Words use the distinct path. For addition/subtraction, two
literal distinctness tests first require the output slot to differ from
each input. The finite binder separately establishes that this output is
an inactive owned role; numerical input/output separation alone does not
prove ownership.

The primitive checks the LEFT guards, then scans the operands from least
to most significant digit. Five finite progress states distinguish0,1,2,3
and at least4 digits; RIGHT is accepted only in the last state. Every read
digit is0 or1 and both distinct operands must end together. An aliased
comparison also scans and validates its one complete operand. It does not
use the source method's immediate alias shortcut. For legal head1 inputs
both return zero and preserve the same state.

For comparison the finite state initially0 is replaced by +1 or -1 at
any differing digit, and retained at an equal digit. After processing i
digits, this is the ordering of the low i-bit prefixes. A later differing
digit has larger binary weight than their entire preceding difference,
so the induction holds. At RIGHT this is the ordering of the full Words.
On the alias path every digit agrees and the state stays0.

For addition, with carry c in{0,1}, the next bit is `(x+y+c) mod2` and the
next carry is its quotient by2. For subtraction, with borrow b in{0,1},
the next bit is `(x-y-b) mod2` and the next borrow is1 exactly when the
integer is negative. These are fixed finite transition tables. The usual
prefix identities prove the result modulo2^P and the terminal carry or
borrow. In the alias cases y=x; the same induction applies. No signed or
half-range premise is needed for these three primitives.

Each result digit is written directly into a checked blank output cell;
the complete RIGHT marker is also written into a checked blank. No source
Arena.zero routine is called to initialize the result. The head then
returns over the full just-written extent. Every input head returns over
its unchanged extent. Each selector's L, six bits and R are read and
erased, and all four heads return to their origins. The final halt state
is CMP_NEG/EQ/POS, ADD_C0/C1 or SUB_B0/B1. Fixed dictionaries deliver these
finite tags to the retained source controller; their tariff is explicit.

Only the result body changes. All unrelated Words, input contents, LEFT
markers, exterior cells and historical tails remain unchanged. The result
is returned as a live owned Word: its later numerical erasure is performed
and charged by the retained actual Word.free path, not by this primitive's
selector retirement. Malformed input can halt after partial work; no
failure-path restoration theorem is asserted. The success theorem is
separate from the bounded rejection controls.

## 3. Source coverage and physical ownership simulation

Each exact producer file has16 raw call expressions, using only compare,
add, divmod and subtract_exact. The last delegates to subtract plus the
finite no-borrow check. That check remains unchanged and receives the exact
new borrow tag. There is no additional call from this producer to
Unsigned.times_small or increment_in_place. The only reachable use of
shift_add_bit was inside the old division body, which B11 removes entirely.
The other source calls are Word/Arena methods, record reads/writes and the
new Arithmetic controller methods. They remain explicitly outside this
raw-provider lowering.

Source admission, already proved in #5053, ensures complete P-bit operands,
modular additions without carry when required, exact-subtraction premises,
and division denominators0<D<2^(P-1). These numerical facts are credited
premises. This package adds no new domain restriction to those raw calls.
In particular the aliased doubling calls at producer lines45 and74 are now
physically implemented, and arbitrary legal nonzero carry/borrow results
are also supported by the primitive contract.

The B11 wrapper marks exactly one current producer active and records its
Arena identity. Each new provider wrapper checks both facts before any
physical work. It does not use the source's current half, a call ordinal,
word values, widths or an optional observer to decide the operation. The
finite operation tag comes directly from the called source method. The
new wrappers are installed around the unchanged B11 division wrapper and
are restored on exit. Original methods are stored only to restore those
bindings; no positive execution invokes an old provider.

`reserve_simple` validates the complete64-slot live/free partition,
uniqueness of the free stack, all Word slot/arena identities and all eight
protected guard slots. It also verifies that the actual operand objects
are their bound live Words. Comparison reserves nothing. Addition and
subtraction pop one free owner and mark it live without initializing its
body. The literal graph performs all output construction. The unchanged
physical Program check requires64 numerical and4 selector backings to be
distinct; this checks real backing, not merely different wrapper names.

Let pi be the inherited B11 bijection between original and replacement
slots at a source boundary. It fixes incoming live values and relates the
ordered free stacks and all live Word references. For comparison no
allocation occurs, so pi is unchanged. For addition/subtraction, original
Arena.zero and the new reservation pop corresponding last free slots.
Extend the live relation with those two output references. The primitive
lemma supplies equal complete digits, RIGHT marker, head and finite flag.
The original template copy leaves its template unchanged and returned;
the new graph leaves that same template untouched. All other roles retain
their complete contents and heads. Thus pi remains a valid boundary
relation after the one-output call. Since a bijection is injective, source
object aliasing is equivalent to equality of the two encoded slot handles.

Division uses the unchanged B10/B11 weak simulation, including its
transient old allocation schedule and rebuilt ordered free-stack relation.
Source method composition preserves this relation: all numerical branches
receive equal finite results, Word/record operations are slot-equivariant,
and control has no arithmetic dependence on the numeric slot labels. The
current source's unordered finally erasures commute on disjoint owned
bodies; after them the free-stack bijection is rebuilt as in B11. The
returned lower/product words and numerical output stream therefore agree,
and all borrowed source and guard values are restored. The new comparison
adds no live Word and add/subtract each use exactly one output, so the
prior32-live upper bound remains sufficient. No stock is inferred from a
successful finite run.

## 4. Exact primitive counts and complete source subset

One successful descriptor alias classification costs52 logical instructions.
One inherited distinctness test costs51, so add/subtract pay102 for the
two output checks. A numeric LEFT check costs3 logical instructions.
A return from RIGHT atP+1 to body cell1 costs3P+3. Erasing and returning
all four selector frames costs121, including the terminal halt.

The alias/distinct per-digit bodies cost4/5 for comparison and7/8 for
addition/subtraction. The entry guard, initial jump, terminal RIGHT checks
and output marker give these exact totals for every legal input:

| Entry | Logical instructions | Numeric reads | Numeric writes | Numeric moves |
|---|---:|---:|---:|---:|
| comparison, alias |7P+181|2P+3|0|2P+4|
| comparison, distinct |11P+188|4P+6|0|4P+8|
| add/subtract, alias |13P+291|4P+6|P+1|4P+8|
| add/subtract, distinct |17P+298|6P+9|P+1|6P+12|

Every dispatched numerical read costs30 physical instructions; each
numerical write or move costs31. Other logical instructions cost one.
Consequently the physical count is L+29R+30(W+M), yielding respectively
125P+388,247P+602,279P+735 and401P+949. Four unchanged literal setters add124.
Thus every complete simple call costs at most401P+1073. These counts include
all descriptor reads, equality/distinctness checks, all output-cell writes,
full input traversal, head returns, selector retirement and finite halt.
They do not omit a hidden output initialization or a pointer jump.

Let m,t be the left/right record counts, v the number of valid right
coordinates, and E the sum of Euclidean loop lengths. Let J count raw
divisions and H count the other three raw providers outside the replaced
old division body. B11 proves exactly

    J = 3m + 2t + v + 2E <= (P-2)(4P+5).

A modular multiplication executes P doublings and at most P further
modular additions. Each such addition calls raw add, compare, and at most
one subtraction, hence at most6P simple providers per multiplication.
A modular subtraction uses compare and subtract, and at most one add;
a full unsigned product uses at most2P raw additions.

Each Euclidean iteration therefore adds at most6P+3 simple providers.
For each left record, the remaining scaled multiplication costs6P, the
two full products cost4P, the adjustment costs3, reconstruction costs1,
and admit/value/unit comparisons cost3. For each right record, offset
multiplication costs6P, full product2P, valid update at most3, and the
three comparisons cost3. This covers the inverse update too. Short-circuit
left validity only decreases the count. Therefore

    H <= (6P+3)E + m(10P+7) + t(8P+6).

The prior numerical proof gives E <= (m+t)(2P+1) and m+t <= P-2. It follows
by substitution and expansion that

    H <= (P-2)(12P²+22P+10) < 12(P+2)³.

This is a source-loop proof for every admitted size, not an inference from
observed counts. It includes the output-side comparisons and additions,
not just the Euclidean component.

One selector lifetime pays the unchanged89-instruction ACQUIRE once.
Using the inherited division ceiling, the complete new literal subset is

    T_literal <= 89 + J(930P²+1395P+14322) + H(401P+1073).

Put U=P+2>=6. B11 bounds the first two terms by2^15 U^4. Also
401P+1073=401U+271<447U, so the final term is below5364U^4.
In particular the entire new raw arithmetic subset is below2^16 U^4.
For a sequence of current invocations with varying widths, sum the actual
per-invocation terms and pay acquisition once per actual descriptor
lifetime; do not use a final smaller width to price earlier calls.

The complete source invoice is explicitly a vector of models:

- Literal arithmetic: the displayed T_literal, including every numerical
  and descriptor action and finite literal control instruction.
- Residual native source/record actions: the exact unchanged same-workload
  source action count minus the outermost old arithmetic provider actions.
  Retained Word.zero/copy/free, source initialization, source-prefix scans,
  result serialization, higher controllers and later output retirement
  remain charged. The inherited fresh-Entry source-body theorem gives its
  conservative2^20(P+2)^4 source-operation ceiling; larger retained history
  services and external source setup keep their own stated charges.
- Finite metadata and returned flags: the conservative service invoice
  `256 + 32I + 16400J + 16408H`, for I current invocations in one descriptor
  lifetime. Each new provider pays16 for the scope/dispatch check,16384 for
  bounded64-slot validation/reservation/binding control, and8 for its fixed
  return tag. The actual selector setters are already literal, not charged
  again as symbol actions. These are retained service units, not a claim
  that the finite metadata itself has been lowered to tape instructions.
- Explicit physical grant and lifecycle services: selector grant extension,
  backing ownership, source framing and any full-history transport/sweep
  required by the retained caller, at their actual charged extents.

No common physical tariff for all these components is inferred. All four
old providers form one nested call family: the original divmod internally
calls comparison and subtraction. Its complete old action bill must be
subtracted once at the outermost provider boundary, not once again for its
nested calls. The source verifier tracks this depth explicitly and compares
the resulting residual to the new actual numerical meter. New numeric
accesses use Word methods charging arena.meter; backing Port meters do not
also charge them. Selector actions charge their separate marker ports.
At the header/key/payload join, the unchanged predecessor overlaps are
removed exactly once; the additional selector overlap is removed once.

## 5. Actual physical histories and inherited interfaces

Every numeric operation remains inside cells0..P+1 of its selected Word.
All other physical numerical owners are untouched. Each selector stays
inside its explicitly granted eight-cell interval. Thus for any previous
per-role span H_s, the arithmetic history is bounded by the union of that
previous span and [0,P+1] for each accessed numeric role, and the previous
span and the fixed eight-cell grant for each selector. For owned numerical
stock a conservative fixed-bank bound is

    sum_{s=8}^{63} max(H_s,P+2) + sum_{four selectors} max(H_s,8),

with any previously charged protected/source owners retained separately.
Only actual existing physical roles are counted. No new owner is created
per raw call, no history is reset by clearing, and no old per-slot history
profile is transported for free through the weak bijection. Repeated
invocations retain the maximum previous extent of each physical role.
The theorem does not replace these maxima by O(P) when incoming histories
are arbitrarily larger. Any actual full-history retirement or transfer
adds the relevant retained service bill.

The actual source joins keep the input/header/current-coordinate premises
of the pinned caller. B11's source-only Endpoint traversal uses83 physical
roles including four selector owners; the source/payload caller uses100
roles per leg. These stocks are reported separately. The payload interface
still uses the fixed13-bit codeword with arbitrary12-bit payload. The
retained header/key and radix services, literal row/key graphs and their
inverse/physical-position premises are unchanged. A complete source-only
roundtrip is not a proof of a general payload transform or of a complete
CRT/multiplication implementation.

## 6. Evidence, limits and reproduction

`test_core.py` checks all256 ordered four-bit pairs for each of three
entries, all16 aliased four-bit inputs per entry, and24 additional cases
through P257 with retained histories of1025 cells. These840 packets execute
2,635,200 literal instructions. Each checks exact integer semantics,
finite flags, all inputs and exteriors, all heads, every selector cell,
and both exact logical and dispatched formulas. The old336150-instruction
prefix is compared instruction by instruction. Domain controls cover short
Words, nonbinary digits, unequal extents, dirty outputs and malformed
selectors. Returning carry, borrow and comparison-tag mutations complete
all head/selector restoration but are rejected by the semantic oracle.

`verify_source.py` executes a complete current Endpoint traversal in both
directions, including nonleaf groups, and a padded actual source/payload
roundtrip. Positive execution blocks all four old raw providers and the
obsolete shift_add_bit provider. It executes1135 comparisons,1510 additions,
107 subtractions and192 divisions;1258 simple calls alias their inputs.
The total is22,179,316 literal instructions. Exact source outputs and full
source/payload/key roundtrips agree with the predecessor. Direct integer
CRT and arithmetic oracles, one-output ownership checks, inherited division
counterfactual relations, actual backing/head identities, history cleanup
and the exact outermost action subtraction pass. Old arithmetic is used
only in baseline or counterfactual checks outside the actual replacement
legs; it never supplies positive runtime results. Eight scope/foreign-Arena
controls and a deliberately reintroduced old-provider call are detected.

`source_check.py` authenticates all exact dependencies, audits source call
coverage and the new dispatch bodies, verifies every old instruction and
entry, and checks every new relocated control target. Scientific source
code and bound derivations, rather than tests alone, support the all-P
claim. Separate independent graph/owner and source/cost reviews are
packaged by the lead; their evidence is identified separately.

All primary scripts are read-only and use the standard library. Run normal
and optimized variants as registered in VERIFY.json. Constructor loops and
all exact-integer decoding, snapshotting, receipts, counterfactual clones
and optional observers are verifier/offline work, not runtime primitives.
There is an explicit erasure projection of this instrumentation. Delete
`simple_calls`, the inherited call/transcript/receipt arrays, optional
observer calls and their `simple_kind` field, and cumulative action,
history, invoice and allocation-meter recording. No retained source or
binder arithmetic/branch decision reads these recorded values: reads of
them occur only in further recording or in the verifier/optional observer.
The retained binder consumes only the finite halt status from Program.run;
its accesses to numerical instruction counts feed transcripts, not a
continuation choice. Keep the actual owner/live/free structures, physical
ports, fixed operation tag, active-source guard and acquisition Boolean.
Their behavior is unchanged by erasure. This projection concerns the
supplied observational verifier callbacks; arbitrary callbacks that mutate
physical state are outside it. Likewise remove the replay
watchdog and CPU statistics when interpreting the finite graph theorem.
The projected execution has the same symbol actions, finite return states
and source continuation; transcript storage is therefore not silently
counted as part of the constant physical-owner stock.

The inherited Python Program.run has a20,000,000-step per-entry watchdog;
it can stop sufficiently large admitted inputs. The universal theorem is
about the emitted finite graph without that bounded replay watchdog.

Remaining obligations include literal Word lifecycle and higher producer
control, encoded owner/free-stack metadata and acquisition, a common paid
physical tariff for the full source/radix/recursive caller, and all retained
selected-theorem assumptions. This package makes no assertion that these
obligations follow merely from complete raw-provider elimination. No
selected certificate, supplier acceptance or multiplication kappa changes.
