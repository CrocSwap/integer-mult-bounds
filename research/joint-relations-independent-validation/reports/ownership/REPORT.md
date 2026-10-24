# Independent joint-relation ownership and chronology audit

Candidate: Ali Romman's #5383, exact head `4bd6efa51a495a7c7b7754915cf0244e7e60969e`.
Canonical base: `1ec1119972c9aefe42525172d07b332fcff81cb4`.
This is the ownership/runtime-contract component of the independent audit.
It neither changes selection nor independently accepts a kappa or full physical theorem.
Forward-transpose extensions are outside this assignment.

## Evidence and method

`check.py` imports only Python standard-library modules. It reads literal
source/candidate words and the pinned source phase receipt. It does not import
any candidate Python, call a source row engine, consume WITNESS.json or RESULT.json,
or trust candidate relation_basis, paid_profiles or claimed counts. The author
README/native.py were read to identify the asserted interface; their routines
are not the oracle. `SOURCES.json` binds actual consumed working bytes.

The source/candidate event zipper proves a stronger chronological fact than
comparing per-kind event multisets: after the explicitly recognized prefix,
snapshot pairs, center triples, zero retags and return clears, every source
event occurs in its original order and with identical bytes. Any missing
retained operation, added borrowed clear or changed phase marker is rejected.
The event/frame pass checks real GF(2) frame inclusion, all scalar current
frames and role distinctions, paid rank differences and every final L frame.
It derives the eight owned pivots and lost rank-nine helper targets from the
actual ownership/preparation/return contract and source endpoints.

The cheap structural pass plus twelve controls passed under hard 15-second CPU
and wall limits and 128 MiB address-space limit in about 7.1 seconds. See
`STRUCTURE.json`; this receipt explicitly marks exact endpoint replay false.
The root executed the full rational free-word replay through its serial queue.
`RESULT.json` records **PASS_EXACT_RUNTIME_OWNERSHIP** for #5383, with all
641 backward and 633 forward arbitrary entry columns and all twelve controls
checked. No heavy check was launched by this worker.

## Actual bank and def-use chronology

Indices below are zero-based. Birth/use/retirement are emitted candidate-word
indices; snapshot production and center are original source indices. A
snapshot is copied immediately after the named source climb has produced the
copied role in precisely the recorded frame.

| Bank | Source production / role | Frame | Candidate birth | Candidate unique read | Candidate clear | Source center |
|---|---|---:|---:|---:|---:|---:|
| C1 | 11205 / L92 | 254 | 11269 | 11411 | 11412 | 11332 |
| C2 | 11218 / L57 | 274 | 11284 | 11439 | 11440 | 11358 |
| C3 | 11231 / L81 | 619 | 11299 | 11467 | 11468 | 11384 |
| C4 | 11244 / L224 | 279 | 11314 | 11495 | 11496 | 11410 |
| C5 | 11257 / L11 | 621 | 11329 | 11523 | 11524 | 11436 |
| C6 | 11270 / L240 | 280 | 11344 | 11551 | 11552 | 11462 |
| C7 | 11283 / L9 | 624 | 11359 | 11579 | 11580 | 11488 |
| C8 | 11306 / L288 | 281 | 11384 | 11607 | 11608 | 11514 |

Every birth is preceded immediately by a legal clear of that bank; every read
is followed immediately by its legal clear. At candidate index 11384 all eight
saved values are simultaneously live and none has yet been consumed. Thus a
single sequential scratch bank cannot implement this word. The checker
rejects reusing C1 for the C2 snapshot even if both corresponding clear/COPY
destinations are consistently changed. C0 is a separate owner: its first clear
is 11387 and its final read/clear are 11609/11610. Clearing C0 before each
replacement is legal and does not touch a borrowed helper or a live snapshot.

The eight pivot lifetimes are also simultaneous with the snapshot lifetimes.
They are existing helper-role slots, while C1..C8 are eight additional slots.
No pivot is used as a preparation source for another pivot. Their inputs are
retained independent cold helpers in frame 0, so there is no dependency cycle
or pivot read before production.

| Owned helper | First clear | Last read | Final clear | Return frame |
|---|---:|---:|---:|---:|
| L225 | 0 | 21375 | 21543 | 1 |
| L227 | 7 | 21147 | 21544 | 1 |
| L229 | 19 | 21146 | 21545 | 1 |
| L230 | 27 | 15685 | 21546 | 1 |
| L241 | 32 | 21138 | 21547 | 1 |
| L245 | 40 | 21135 | 21548 | 1 |
| L257 | 48 | 21311 | 21549 | 1 |
| L288 | 56 | 21121 | 21550 | 1 |

The final clears occur strictly after the last reads. These helpers have no
productive output credit: each is an owned temporary and returns zero. In
particular L288 remains an owned pivot even though its intermediate value is
also the source of C8. C8's copy does not transfer ownership of L288 or make
its final helper target available for credit.

## Arbitrary input and output contract

Backward entry consists of 224 arbitrary main fields, 400 arbitrary retained
helpers, eight arbitrary owned helper entries, and nine arbitrary owned C
entries. There are 641 independent entry symbols in the direct-sum row model.
Every owner is seeded with its own symbol, just as each borrowed field is.
An owner is cleared before any read; no entry is silently initialized to zero.
After clear/preparation the pivots are prescribed linear combinations of the
400 retained helper inputs, not new borrowed inputs and not productive targets.

The exact replay initializes a separate basis column for all 641 entries,
tracks rational coefficients and freely reduced native operator words, and
checks the complete endpoint for each retained role. Backward outputs are
`L_i -> L_i-L_(i+112)` for `0<=i<112`; L112..L223 and the 400 retained helpers
are restored in their exact source final frames. All 17 owned outputs are zero.
The unchanged forward word has 632 retained inputs plus arbitrary owned C0,
with the opposite main shear and all retained helper outputs restored. Native
left multiplication is injective on reduced words, so the implementation's
warp dictionary transformation cannot silently overwrite colliding terms.

Read/write/frame checking alone cannot prove a zero retag's zero value or a
correct snapshot's content. Those are tested by exact mode and proved uniformly
by the independent algebra lane's sixteen unrestricted source identities.
A structure-only PASS must never be promoted to the full algebraic contract.

## Constructive proof at every positive tensor multiplicity

Fix an allowed positive multiplicity f and a caller satisfying the selected
native, ownership, compiler and precision/tape hypotheses. Each logical role
is a separate complete slot in its stated actual frame, interpreted in the
source f-fold internal vector space. Preparation uses only rational scalar
ADDs in frame 0 and legal erasures of the eight owned pivot slots. The
independent algebra proof of the joint reduced system therefore sets all
eight relations to zero while leaving the other 624 inputs unrestricted.
This applies to arbitrary correlated vectors as well as independently chosen
ones; the formal columns are a proof device for a universal linear identity.

Proceed by induction through the source chronology. A retained event is the
identical source event. After a snapshot production, legal clear/COPY stores
that exact vector in a disjoint owner of the same actual frame. All following
source events preserve this bank as a spectator until its unique use. At a
center replacement the source center output minus the saved vector is the
proved relation multiple, hence zero on the prepared domain. The clear/COPY
triple therefore produces exactly the old center output, in the identical
output frame. At a zero replacement the source input vector is exactly zero;
the physical identity leaves it zero and supplies the old job's zero output
in the declared target frame. The source state on every continuing role is
therefore preserved at each replacement. Final retained outputs follow from
the source endpoint, and each owner is legally cleared after its last use.

For the tensor lift, evaluate each free generator at its exact source
f-fold native operator, including its absolute phase, and each inverse at
that operator's inverse. Evaluation is a rational algebra homomorphism on
finite formal sums of free words. Rational ADD coefficients stay outside
the tensor substitution. The sixteen identities and complete endpoint
identity therefore hold for this f. No tensor power of a scalar sum or
register matrix is taken. Backward inverse-transpose generators are treated
as their own generators and have the same lift argument.

The zipper preserves every native map, phase marker, adapter and retained
paid event in position relative to all continuing state. Canonical actual
frames/maps are identical. The source absolute-phase receipt is bound to
the exact decompressed word. New operations are same-frame scalar actions on
owned slots and identity on a proved zero vector. Consequently no new native
phase recipe is required. Source phase lowering is reused at these exact pins,
not freshly rerun or inferred from a binary tableau.

## Recursive suspension and constructive allocation handoff

At a recursive event, suspend the parent chronological state, including all
live pivot and snapshot slots. Use the retained supplier contract on the
named target field in its actual input frame, with every other parent role
and every external spectator untouched. In particular C1..C8 remain separate
spectators across every intervening child call. A supplier that may overwrite
one of these banks fails this contract even if it later claims a numerically
correct target.

A constructive address assignment is `(call path, local role)` for each
private slot, with disjoint tagged coordinate ranges for the parent's
persistent fields, its C banks, and every active child. While a child is
active, no other frame at that depth uses its private range. Depth-first
execution returns the child owners as zero before that range can be reused
by a later sibling. The active stack therefore uses a sum of the local
simultaneous bank demands across its ancestor frames. It does not reuse a
live ancestor range, take a maximum in place of that sum, or count eight
snapshots as one slot. This construction is an induction on the finite
recursive execution/compilation tree: distinct path prefixes give disjoint
live private ranges; a completed subtree releases only its own range.
The selected recursive compiler/allocation premise supplies the actual
finite physical hosting and stock bounds for this address construction.

The changed local caller requires 17 simultaneously owned roles: eight owned
existing helper slots, C0, and eight added C slots. Existing 624 retained roles
remain borrowed and restored. Every child's scratch is additional to these
live parent slots. The physical/precision lane must fund expanded routing,
complete slot sizes, suspended ancestor storage and actual stock/precision
bounds using this template. This report proves the handoff contract and
provides an explicit nonaliasing allocation; it does not substitute the old
numerical template cap or a newly assumed free gather/decoder for that funding.

## Rejection controls and scope boundary

Twelve structural mutants reject borrowed erasure, missing initial pivot
clear, duplicate declared ownership, reuse of a live snapshot bank, wrong
snapshot frame or source, missing owned return, removal of a retained output
operation, undeclared storage, changed source phase marker, wrong final owned
frame and wrong center COPY gauge. These tests operate directly on in-memory
candidate event data and run without hash gates, so a freshly recomputed hash
cannot turn a semantic failure into a pass.

Price, compiler, expanded stock, scientific kappa acceptance and selection are
separate obligations. The event replay gives no credit to the eight owned
helper outputs. No finite replay alone establishes a physical all-size theorem.
The uniform argument above is conditional on the unchanged quantified source
premises and on the independently established joint identities. Ali Romman
retains construction credit; Cao Yifan supplied the source word; Chris R,
Cinna Davis, zxv, ToikY and earlier contributors retain the source/audit credit
recorded in the frozen notices. This audit uses substantial OpenAI Codex assistance.

## Separate audit of PR5387's actual word

The execution scope was expanded to Dugongue's #5387, exact head
`b1ab650d36f59e5be682a813145b7c67e219e341`, package `research/eight-owned-relations`.
Its README explicitly credits Ali Romman's public predecessor for the
mechanism and disclaims priority. Its row/price engines are adaptations of
that predecessor, so running those engines would not give independent
ownership evidence. This checker instead processes #5387's own actual word
with `--candidate .../WORD.json.gz --candidate-head ...`. The consumed bytes
are separately pinned in SOURCES.json. #5387 has a different native witness;
an identical recursive invoice does not license reusing #5383's complete
runtime proof.

Its independently derived pivots are 225, 227, 229, 230, 241, 245, 257, **261**.
The eighth snapshot is **L256**, copied after original source event **11296**
in actual frame 281. It is born at candidate event **11376**, read at **11609**,
and cleared at **11610**; the original center is still source event 11514.
The eighth zero retag is **L256 at original source event 17233**, emitted
candidate event 17329. Thus the #5383 L288/source11306/source17580 identity
is explicitly inapplicable to this eighth replacement.

The first seven snapshot births/reads/clears are each two candidate events
later than the #5383 table; the source production roles/events and actual
frames for those seven are unchanged. All eight #5387 snapshots are live
by candidate index 11376, preceding the first read at 11413. C0 has first
clear 11389 and final read/clear 11611/11612. Pivot L261 is cleared at 56,
last read at 21316, and finally cleared at 21552 in frame 1. The other seven
pivot first-clear positions are the same as #5383; their last reads and
final clears are two events later. `STRUCTURE-5387.json` records every value.

The separate #5387 structure/frame pass and all twelve mutation controls
passed under hard 15s/128MiB limits. The root separately executed its independent exact mode through the serial
queue: RESULT-5387.json records **PASS_EXACT_RUNTIME_OWNERSHIP**, all twelve
controls rejected, with 641 backward entry columns and 633 forward entry
columns checked. This is a fresh actual-word proof rather than a proof
transfer from #5383. The uniform direct-sum/tensor argument
and constructive recursive address allocation above apply to this separately
checked chronological contract, conditional on #5387's own unrestricted
identities and the unchanged source framework. Extra prep scalars are
charged by the invoice/physical lanes; no price conclusion follows here.
