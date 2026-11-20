# A literal arithmetic/lifecycle union for one eager CRT Entry

## Claim and exact sources

Canonical scientific base:
e54523517d0f03e58352e647c403a5af3e525a57.

The numerical arithmetic source is CrocSwap/integer-mult-bounds#7596 at
CubeJerry commit ee6005fe241ab947e511fe9f6d86f5f4fa58478b.
Its generator emits 1,304,162 fixed R/W/M/J/H locations on 68 roles, with
graph digest 8911a498e8e36409ca3b48395e7d754f49b4e452c273db821756867cea95a045.

The lifecycle source is the published CubeJerry commit
39c309f1aa72af12669d37ae055da0ece1ae0e7d, package
research/literal-crt-word-lifecycle. Its 130,936-location graph has digest
48863284a4af10cdbb4d16cbecba07dfbadabc57ee8d21f635181acc7e0d0d73.
It explicitly left an executed arithmetic union open. Its local proof and
the #7596 numerical proof are credited inputs, not new arithmetic algorithms.

Fourteen authenticated files, totaling 141,987 bytes, form the compact source
closure. They include the two graph generators, inherited divider generator,
lifecycle port/Owner adapters, and the unchanged Word, record, Entry and
current CRT producer sources. SOURCE-PINS.json records original paths,
commits, Git blobs, and SHA-256 hashes. The generated million-state graph is
recreated in memory; it is not a committed input or output.

**Scoped composition theorem.** For any admitted same-precision trace on one
supplied eager Entry, the fixed union graph and the declared typed wrappers
implement ordered reservation, ZERO, COPY, FREE and IS_LIVE together with
comparison, modular add/subtract with finite carry/borrow, and distinct-input
division. Selected words have complete P-bit framing and the indicated ready
heads, P>=4; division requires 0<D<2^(P-1). The source's stock/admission
premises remain. Both graphs' instruction paths are preserved by finite
renaming. Every successful working head returns, unselected owners and their
heads are preserved, and histories stay attached to the same physical roles.

The union has exactly **1,435,098 locations and 70 roles**, independently of
precision, data, trace length, and old backing sizes. Its canonical graph hash
is 31ce4975d2189002ad03f2279eabe34d99d97da6c5f5a40f9642734b3e9ec148.

A complete pinned seven-bit producer invocation and its result consumer run
with all four old arithmetic providers, Arena.zero/copy/free and Word.erase
made unavailable. This is actual combined execution, strengthening the
lifecycle predecessor's raw-arithmetic replay.

The higher Python controller, encoded-width/record interfaces, ordinary Word
predicates, supplied blank grants and original Entry.close remain separate.
The changing-Entry wrapper is not constructed here. No common whole-caller
physical tariff, foundational-assumption discharge, or new kappa follows.

## 1. Fixed roles and state renaming

The numerical roles retain their actual identities 0..63. The arithmetic
selectors remain 64..67. The existing Entry template is role 68; the ordered
free-stack tape is role 69.

| Lifecycle local role | Union role | Meaning |
|---:|---:|---|
| 0..63 | 0..63 | Same numerical owners |
| 64 | 68 | Existing zero template |
| 65 | 69 | Ordered free stack |
| 66 | 64 | Lifecycle source selector |
| 67 | 65 | Lifecycle output selector |

The map is injective. The two other arithmetic selectors, roles 66 and 67,
are not touched by lifecycle instructions. All four selectors have separate
eight-cell backing; the stack has its separate 338-cell backing. The runtime
rejects any repeated backing identity among the 70 roles.

The arithmetic graph is an unchanged prefix. If A=1,304,162, a lifecycle
state q becomes A+q. Every lifecycle R target and J target receives this same
offset, and every R/W/M role receives the fixed table above. H tags do not
change. No instruction receives a runtime-computed tape index. The union
introduces no new primitive arithmetic or selector operation.

Induction on individual instructions gives a step-for-step simulation:
corresponding heads and cells produce the same read branch; writes and moves
affect the corresponding fixed owner; jumps reach the corresponding state;
halt tags and path lengths agree. No renamed branch crosses into the other
segment. Thus inherited success proofs and exact costs transfer unchanged.

A:RETIRE remains in the frozen numerical segment because that segment is
preserved byte-for-byte. It is not an admitted public Word-release service
of this wrapper and is never called. Word retirement uses L:FREE, which
updates the live/free partition as well as erasing the body.

## 2. Shared-selector protocol and ownership

At a service boundary the ordered stack consists of distinct six-bit codes
from {8,...,63}. Live slots are its complement, so the eight protected slots
remain live. Every free numerical owner has its retained L marker and a blank
suffix through its whole historical backing.

A successful lifecycle service leaves its two selectors blank; the other
two arithmetic selectors remain blank. Arithmetic first receives four paid
setters, then erases all four selector frames before its successful halt.
The typed wrapper never calls a lifecycle service while an arithmetic frame
is bound, or a numerical arithmetic entry while a lifecycle frame is live.

Initialization executes the original 89-instruction arithmetic ACQUIRE,
then the original 2,744-instruction lifecycle INIT. Their overlapping blank
writes are real charged work. Blank capacity is supplied by the entry
contract; neither call infers allocation from a successful tape move.

The unchanged lifecycle Owner is presented with its original 68-role ABI.
LifecycleView checks each physical backing against the fixed map and routes
the call into the single union program. Finite ALLOC_s tags select existing
Word objects. There is no host free stack or live set selecting an output.

For an arithmetic call the wrapper performs two actual liveness queries,
then zero, one or two TAKE calls. TAKE removes the actual top free record,
marks that owner live by the complement convention, and leaves its body blank.
The numerical graph constructs the complete output before the wrapper returns.

Thus outputs are distinct from all live operands and, for division, from
each other. Simple arithmetic permits the same input object twice; division
requires distinct inputs. Equal numerical values do not merge owners.

A reserved blank owner is temporarily live but incomplete. No COPY/FREE or
external numerical operation is allowed on it before the promised output
constructor returns. This is a short typed phase within the wrapper, not
permission to treat membership as a completion predicate.

### Suspended heads

The source's multiplication loops keep a separate scan Word at a current
digit while operating on other Words. Its head need not be 1. The active
operands and outputs satisfy their ready-head contracts; unselected owners
may retain any admitted head position.

The generated dispatch reaches numerical instructions only on the selected
roles. Therefore arbitrary unselected head positions are irrelevant to the
path and are preserved exactly. The combined verifier compares every incoming
head after every call, including these suspended scans. It does not impose
an incorrect global-head-at-one invariant mid-producer.

### Ordered free stack and historical identity

For every actual request sequence, the old abstract LIFO operations and
literal TAKE/FREE have the same ordered effects. COPY's source is checked live
before its fresh output is popped. FREE erases its whole active body before
pushing the owner, so no dirty active Word is advertised as free.

Original source finally blocks enumerate an unordered host live set, whereas
the physical live view enumerates fixed handles. When comparing different
cleanup orders, use the predecessor's weak slot bijection and slot-equivariant
numerical source semantics. Do not infer identical old and new host set
iteration orders. The execution oracle tracks the new trace's actual order.

A slot bijection is a proof relation, not a physical transport. Actual old
backing always remains with its physical role and is charged there.

## 3. Source-bound substitution and terminal order

The four installed arithmetic methods are exactly compare, add, subtract and
divmod. Every call checks the bound Arena, uses the physical reservations,
runs four literal setters, and enters the unchanged numerical graph. Results
come only from output tapes and finite halt tags.

The source bytes are unchanged. Arena.literal and free_many dynamically call
the new zero/free methods. The inherited higher Word operations and record
loops are retained. In particular, Word.zero is the existing Boolean
zero-test scan; it is not Arena.zero allocation.

During the positive producer/consumer interval the old compare/add/subtract/
divmod/shift_add_bit functions, Arena.zero/copy/free, and Word.erase are
replaced by throwing sentinels before the new wrappers are installed.
The sentinel counter is zero. The old methods are retained only for restoring
bindings afterward, not as a positive path.

The local graph theorem composes with #7596's already proved source arithmetic
simulation and the lifecycle theorem. For the same legal request order,
reservations and numerical outputs have the same owner relation. Source
branch decisions therefore receive the same values and flags. The retained
numerical admission and live-stock theorem supply the legal domains and
enough owners; finite peak observations do not reprove those premises.

**Terminal ordering matters.** The original Entry.close queries arena.live
before removing numerical L markers and retiring the template and record
owners. The ordered stack must therefore remain active through those last
queries. The successful order is:

1. Execute the producer and consume its returned numerical and record outputs.
2. Leave the sealed provider interval and execute the original, separately
   charged Entry.close, including its physical IS_LIVE queries.
3. Execute lifecycle CLOSE and verify all four selectors and stack are blank.

Closing the metadata first makes the subsequent live query fail. An executable
negative control retains that integration failure. No rollback after malformed
use is claimed.

Entry.close uses retained Word/template retirement and is explicitly outside
the sealed producer/consumer interval. The result is not a claim that all
original Entry or record services have been lowered into the union graph.
After Entry.close removes the original numerical L markers, only metadata
CLOSE remains. It never reads a numerical or template role, so its proof
requires no numerical framing at this final boundary. Reopening that retired
Entry is not admitted.

## 4. Exact primitive costs

All costs below count R, W, M, J and H, including head returns and finite
control. Setters are paid calls of 31 instructions each.

The inherited lifecycle costs are unchanged. At entry free-stack length m,
and for a found bottom-index k:

| Entry | Exact instructions, excluding an external source setter |
|---|---:|
| INIT | 2744 |
| TAKE | 36m+155 |
| ZERO | 165P+36m+417 |
| COPY | 287P+97m+676 |
| FREE | 160P+61m+409 |
| IS_LIVE absent | 61m+90 |
| IS_LIVE found | 61k+89 |
| CLOSE | 1395 |

COPY, FREE and IS_LIVE additionally require one 31-instruction source setter.
The inherited proofs give the legal m domains and show equality/bit branches
have equal lengths.

### Numerical graph bodies

The exact simple bodies, before four setters, are:

| Body | Same input handle | Distinct input handles |
|---|---:|---:|
| COMPARE | 125P+388 | 247P+602 |
| ADD or SUBTRACT | 279P+735 | 401P+949 |

Division depends only on P and c=popcount(floor(N/D)), the number of successful
subtract steps in the binary long division. Its exact body cost is

    T_div = 402P^2 + 923P + 1346 + (278P+245)c.

Here is an independent path derivation. The predecessor's logical count is

    L_div = 18P^2 + 36P + 458 + (12P+9)c.

Its six distinctness checks cost 306; initialization costs 17P+27; each
of the P input iterations costs 18P+19 before an optional subtraction;
each successful subtraction costs 12P+9; the final return costs 125.

The numerical instruction counts are:

| Segment | Reads | Writes | Moves |
|---|---:|---:|---:|
| Initialization | 6P+10 | 2P+2 | 6P+14 |
| Each input iteration | 6P+7 | P+1 | 6P+8 |
| Each successful subtraction | 4P+4 | P | 4P+4 |
| Final return | 2 | 0 | 2 |

Therefore

    R = 6P^2+13P+12+(4P+4)c,
    W = P^2+3P+2+Pc,
    M = 6P^2+14P+16+(4P+4)c.

The arithmetic dispatcher charges 30 per numerical read and 31 per numerical
write/move, so physical cost is L_div+29R+30(W+M), giving T_div above.
This dispatcher differs by one instruction from the lifecycle dispatcher;
their tariffs must not be confused.

### Complete arithmetic service: reserve, bind, execute

The two physical liveness queries cost 122m+242, including their setters.
Adding zero, one or two TAKE calls gives respectively 122m+242, 158m+397,
and 194m+516. Four arithmetic setters add 124.

The complete prices are consequently:

| Complete service | Exact instructions |
|---|---:|
| COMPARE, alias | 125P+122m+754 |
| COMPARE, distinct | 247P+122m+968 |
| ADD/SUBTRACT, alias | 279P+158m+1256 |
| ADD/SUBTRACT, distinct | 401P+158m+1470 |
| DIVIDE | 402P^2+923P+194m+1986+(278P+245)c |

Here m is the free count before reservation, not the count at the numerical
body. The verifier independently reconstructs that initial count and checks
each complete reservation/setter/body receipt.

These prices exclude retained higher-controller operations and physical
grant acquisition. They price the actual literal subset, not a complete
source or multiplication tariff.

## 5. Per-role history and the source invoice

For each numerical role s, charge max(H_s,P+2), and separately the same
maximum for the template. Add max(H_s,8) for each of four selectors and
max(H_stack,338) for the stack. Sum these maxima by physical owner.
Erasure and shorter future uses do not refund old capacity.

The source oracle checks every role's backing identity and full contents
after every literal call. All inactive tails in admitted fixtures are
already blank. No current-body routine is credited with cleaning an
arbitrary dirty older tail. The supplied numerical/metadata windows do
not grow during literal execution.

The graph itself has 70 roles. The complete one-Entry source fixture has
76 actual roles, because its guide, two borrowed canonical streams and
three retained owned record streams are additional. Their storage and native
actions are reported separately; they are not silently included in the
70-role graph claim.

The source's Word ports count their native R/W/M actions in existing meters.
The union counts those same arena actions, including template actions,
separately. Subtracting that exact subset from the measured native symbol
actions prevents double counting. The remaining vector is:

- All literal service instructions, including metadata and finite graph control.
- Residual retained source/Word/record/Entry symbol actions.
- Supplied grants, initial framing and higher-controller work, still premises.

No conversion of this vector to one whole-caller physical tariff is inferred.

## 6. Executed domains, controls, and resource scope

The primitive suite covers every pair of four-bit operands for all three
simple operations, every aliased four-bit input, and every four-bit numerator
with divisor 1..7. Additional complete packets use P=7 and P=19, with zero,
maximum values, carry, borrow, equal distinct values, quotient all-ones and
nontrivial remainder cases. RESULT.json lists every operand pair.

There are 972 numerical primitive calls across these packets. They are
interleaved with real ZERO/COPY/FREE, reservation, noninitial free-stack order,
and unequal retained historical tails. Together they execute 15,657 public
literal calls and 28,371,020 literal instructions.

The pinned producer invocation uses P=7, left [(5,1)] and right [(7,2)].
An independent integer CRT characterization gives lower=1, product=5,
and output record (offset,updated)=(3,5). Both providers are literal in that
execution. It makes 82 ADD, 63 COMPARE, 14 DIVIDE and 6 SUBTRACT calls, and
2,723 total public literal calls, costing 3,515,628 literal instructions.
The observed live peak is a finite diagnostic, not a stock theorem.

Its residual native symbol bill is 2,518, including the separately retained
Entry-close bill of 468. The 70 union roles retain 8,719 backing cells in this
fixture. The complete 76-role capacity list is recorded.

Controls reject shared physical metadata backing, demonstrate the old
lifecycle sentinel is actually active, reject premature metadata CLOSE, and
detect a returned carry mutation even though its arithmetic body and head
returns complete normally.

Normal replay generated the union in about 7.1 seconds and completed the full
suite in about 28.4 seconds, with about 510 MiB peak RSS in this environment.
These are verifier resource observations, not asymptotic machine-cost claims.
The graph is never committed or written as a generated artifact.

## Open next questions

- Attach and retire this exact union across the changing-Entry wrapper while
  preserving the last liveness-query ordering and actual per-role histories.
- Lower the retained Word predicates, record interfaces and controller under
  one physical tariff. First enumerate the remaining source symbol/control
  actions; do not treat their finite receipt as a fixed instruction graph.
- Construct compatible blank grants and framing, including any dirty-history
  acquisition obligation, rather than inferring clean capacity from this replay.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
JoyboyBrian's current CRT source/admission and the credited entry/ownership
lineage remain unchanged. #7596 and the published lifecycle package retain
their graph and proof credit. Finite state union and binary long division are
classical methods. This is an executed source-bound compatibility result,
not new arithmetic, human peer review, or proof-kernel acceptance.

