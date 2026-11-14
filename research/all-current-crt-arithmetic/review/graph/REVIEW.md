# Independent review of the current-source arithmetic graph and owner join

Status: PASS. Normal and optimized independent receipts agree exactly. Prepared for Jerry Chen / @CubeJerry with
substantial OpenAI assistance. Canonical base:
`e54523517d0f03e58352e647c403a5af3e525a57`.

## Result and independence boundary

The fixed graph correctly implements the three newly lowered unsigned
primitives, including actual same-owner doubling, on the admitted P-bit Word
interface. Its finite return tags and one-output reservation compose with the
previously reviewed all-division weak owner relation. No defect was found in
the new emitter, dispatch relocation, binder or successful ownership contract.
The result remains a source-bound raw-provider substitution with retained Word
lifecycle, finite owner metadata, grants and higher source control. It does not
establish a complete literal producer, common full-system tariff or new kappa.

This review complements A's source call-count and complete cost/meter audit.
It does not repeat the author's broad nonleaf/payload replay. It uses the frozen
independent B10 sparse CPU and the independent B11 source/CRT boundary oracle,
then adds direct integer arithmetic, new graph-path checks, exact one-output
allocation checks and returning controls. Neither new author hardware nor an
old numerical provider supplies results in the independent actual-source run.
Its original source modules still supply the explicitly retained surrounding
controller and Word/record lifecycle.

`FREEZE.json` records the scientific and reviewer hashes. The combined graph is
`8911a498e8e36409ca3b48395e7d754f49b4e452c273db821756867cea95a045`, with
1,304,162 physical instructions and 68 distinct physical owners. Published B11
at `9700fc89e2582a1fb358a4c6d0d0387076192adc` supplies the unchanged
all-division binding, and B10 at `c4ab5dab6914a04cb86d1fe54eb763b35cc7eeb1`
supplies the unchanged divider and selector ABI.

## Universal digit and alias proof

I derived the three loop invariants independently before inspecting the emitter.
After k digits, addition satisfies

    output_k + 2^k carry_k = a_k + b_k,

and subtraction satisfies

    output_k - 2^k borrow_k = a_k - b_k.

Here a_k and b_k are the low-k input residues, and the flag is binary. The
emitter implements every finite input-bit/flag case of these identities. The
final output is therefore the exact P-bit modular result, with the correct
carry or borrow, including wraparound cases that the higher CRT source normally
excludes. Comparison retains the sign of the highest differing bit encountered;
a new unequal higher bit dominates all previous lower bits. The final sign is
correct, including equal words and arbitrarily many leading zeroes.

The alias classifier reads all six descriptor bits and both delimiters, keeps
a finite unequal flag and returns both selector heads. Equal descriptor values
name one physical input. The alias path reads that input once per digit and
advances its head once. Thus addition doubles it, while subtraction returns
zero and comparison returns equal. Distinct owners with equal values still
take the distinct path. No runtime host-identity arithmetic shortcut is used.
Two literal distinctness checks exclude either output/input alias before any
output write.

Both paths check LEFT guards and require at least four digits before RIGHT.
The fifth progress state loops for all remaining digits; this gives the all-P
argument rather than extrapolating finite replay. Distinct inputs must reach
RIGHT together. Output digits and RIGHT are each written only into checked
blank cells. Full input/output head returns and all four selector retirements
precede a finite halt tag. The wrapper maps those seven tags to fixed
comparison/carry/borrow values. Malformed paths can halt after partial work;
no failure rollback theorem is inferred.

The exact source also preserves the stronger head-at-one entry condition
needed by the new graph. Record reads, zero/copy/literal creation and every
successful raw return yield head-one Words. The inverse loop's zero test
returns its scanned remainder before any division. The only Words deliberately
left at a moving scan position in multiply/product are separate copies;
raw arithmetic receives the result/left Words, not those scan copies. The
modulus and product high-bit probes explicitly rewind before reuse. These
facts induct through each source loop and all sixteen raw call sites, including
short-circuited validity checks. This matters because the old raw routines can
rewind an operand themselves, while the new primitive requires its typed
head-one entry. No arbitrary-head primitive extension is being inferred.

## Exact dispatch and physical ownership

The entire first 336,150 instructions have the frozen B10 graph hash. All old
addresses and targets are unchanged. I independently projected every new
logical instruction to its physical expansion and walked all 65,792 numerical
instruction/slot paths, using direct six-bit slot strings. Every path reads its
own eight-cell selector, returns its head, and reaches the correct fixed
numerical owner and relocated continuation. Non-dispatch branches and halts
are checked too. A wrong-new-port mutation is rejected by this static check.
This is new lowering coverage; the old B10 dispatch suite was not rerun.

The graph writes only its selected output and selector bodies. Input bytes,
LEFT markers, old blank tails and all unrelated owner states are preserved.
All accessed numerical positions lie in [0,P+1]; selectors stay in their
explicit eight-cell grants. Unaccessed heads need not all equal one: the actual
source may retain a separate scan word partway through its body. The new
interface preserves those spectator heads exactly.

The binder verifies the actual 64-slot live/free partition, eight protected
roles and operand object identities. Comparison allocates nothing. For addition
or subtraction, exactly the last available owned slot is removed, marked live,
and returned as the complete output. That equals the original Arena.zero
allocation choice under the existing slot bijection; only its replaced
initialization actions differ. Template contents and head are preserved.
Aliasing is respected by the injectivity of the slot bijection. Matching frees
and the inherited division boundary preserve the relation, with the same B11
rebuild after unordered final cleanup. No physical history is reassigned when
that logical bijection changes.

The returned output stays live. Later Word.free work belongs to the retained
caller and cannot be confused with selector retirement. Reused blank capacity
remains on its physical owner. The proof explicitly keeps per-owner maxima and
additional full-history transport/retirement services; it does not replace
arbitrary incoming histories by the present P.

## Local instruction accounting

An independently counted full numerical rewind from RIGHT costs 62P+92 physical
instructions. The alias classifier costs 52, each successful distinctness check
costs 51, all selector clears and the halt cost 121, and four setters cost 124.
A numerical read costs 30; a numerical write or move costs 31. Counting the fixed
per-digit paths gives the same complete entry formulas as the proof:

| New call, including setters | Exact literal instructions |
|---|---:|
| comparison, aliased input | 125P+512 |
| comparison, distinct inputs | 247P+726 |
| add/subtract, aliased input | 279P+859 |
| add/subtract, distinct inputs | 401P+1073 |

Returned finite-flag delivery and owner metadata remain separately charged
service units. The four setters are already literal actions. The surrounding
Word initialization, free, source transport and complete grant/history services
are still present in the full vector. Source-wide call counting and outermost
old-provider subtraction are A's complementary review scope. I checked that
the proof keeps that distinction and does not claim a complete raw-action
ceiling for the whole physical caller.

## Executed independent evidence and negative controls

`independent_primitives.py` executes 876 complete sparse-tape packets. The
finite domain contains all 256 ordered P=4 value pairs for each primitive,
16 explicit P=4 physical-alias cases per primitive, and selected P=5,9,17,67
boundary words with old blank histories up to 8193 cells. The positives execute
2,274,754 primitive instructions. They check every numerical owner, head,
spectator, exterior and selector cell, not merely decoded outputs. All seven
finite return tags occur. The arbitrary-P claim rests on the loop proof.

Twelve controls check the verification boundary. Wrong carry, borrow and
comparison halts still return but fail the semantic flag oracle. A mutation
skipping the actual selector-origin erasure returns with the correct numeric
comparison and fails the whole-selector oracle. A well-formed stale operand
binding returns but fails the intended source-value oracle. A wrong-new-port
mutation fails the independent static lowering check. Other controls are short
input, unequal extent, dirty output, missing LEFT, short selector and output /
input alias. Structural rejection does not assert rollback.

`independent_join.py` performs a small complete source roundtrip: two records
with widths 3,3, moduli 5,7 and initial coordinates 1,2. It uses actual source frames
and ports, not a mock numerical arena. All four old numerical providers and
shift_add_bit are unavailable. The run verifies 302 new primitive boundaries,
126 actual alias calls and 28 inherited division boundaries, executing 1,657,724
literal instructions. At every new call it checks exact source call site/type,
direct integer results and flags, complete one-output or no-output allocation,
all live/free body and head identities, template preservation, selector
restoration and actual numerical-meter inclusion once. The retained independent
CRT-idempotent oracle checks both producer results. The source returns to its
initial bytes/head; every actual 83-owner caller set retires completely at each
direction's end.

Six scope controls reject each new provider outside an active producer or on a
foreign arena before any literal action. Two more controls let the literal
entry return successfully and then detect a wrong host comparison-flag delivery
or an output reservation improperly retained on the free stack. These challenge
the new source/binder seam. They are failure detection fixtures, not successful
machine protocols or failure cleanup theorems.

Both scripts are read-only by default, accept `--package`, and use `--write`
only when output recording is requested. Run normal and optimized:

```sh
python independent_primitives.py --package PATH_TO_PACKAGE
python -O independent_primitives.py --package PATH_TO_PACKAGE
python independent_join.py --package PATH_TO_PACKAGE
python -O independent_join.py --package PATH_TO_PACKAGE
```

Keep the exact `review_core.py` and `review_all_source.py` beside them. They are
frozen earlier independent review code, not new author numerical implementations.
The final freeze compares normal and optimized receipts byte-for-byte.
`SOURCE-CHECK.json` records exact inherited-source validation.

## Termination, instrumentation and remaining boundaries

The final proof clarifies that admission/success refer to the original source.
Each new primitive terminates on its typed P-bit input. Induction over the
original finite source trace supplies the same finite returns, next branches
and physical boundary relation, so replacement success is a conclusion rather
than an extra premise. This resolves a potential vacuity in informal wording.

The transcript arrays, optional observations, simple_kind field, cumulative
counters and replay watchdog are removable instrumentation. I checked the new
binder's data dependencies: operation choice comes from the fixed called method;
only the finite halt status affects continuation. Numeric/selector instruction
counts feed recording, and recorded lists do not select operands or ports.
Actual current-source, acquisition and owner/live/free metadata remain retained
control. Erasing the supplied observational instrumentation preserves symbol
actions and finite results; arbitrary state-mutating callbacks are excluded.
The finite emitted machine theorem does not use a Python watchdog as its
stopping rule or count unbounded transcripts as part of its fixed-owner stock.

No broad nonleaf/payload replay or whole-source meter proof is claimed for this
review; those have separately identified author and A evidence. Numerical
producer admission, physical Entry ownership, finite allocator/flag services,
Word lifecycle, source acquisition, common tariff and recursive/global
composition remain explicit. A complete raw-provider replacement makes
progress on an interface obligation; it does not discharge the five foundational
assumptions or improve the selected multiplication bound.
