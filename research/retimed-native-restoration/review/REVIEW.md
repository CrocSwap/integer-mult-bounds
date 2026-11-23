# Independent review: native restoration-list storage

## Decision and source freeze

Accept the scoped theorem at PROOF.md SHA256
3855699c96e5369b5dbb767d6033757ab83832d3818cf8314c03dba946a914b5,
with codec_restores.py
74595056e8eb70bacece544442844f07f4dbcbaf400fc3cdb7075adfa97a3727.
It prices ordered restoration values and four reusable image roles at a fixed
production height. It does not price all native service state, route time,
dispatch, Python memory, or cross-height history. All canonical assumptions
remain retained.

## Independent method

The review neither imports nor runs check_restores.py or source_loader.py.
independent_basis.py is an unchanged copy of this reviewer's earlier
independent storage review, used only for source authentication and named
definition extraction. review.py independently constructs ordered targets,
expands lifts, inverts elementary words, applies them modulo 6561, constructs
serialized bit fields as binary strings, and verifies the normalized budget.
Only immutable source definitions and the codec under test serve as producers.

Run `python -B review.py --package /path/to/native-restores --output RESULT.json`
and the same command with `-O` and RESULT-OPT.json. The package argument makes
the review portable. Exact source bytes are authenticated before extraction.

## Target closure, coefficient width and word chronology

The independent enumeration has all 18,906 ordered target tags and agrees
with the original tagged constructor. There are 2,120 distinct target
requests. Root targets use the actual joint and diagonal stages; helper
targets use the actual start/final difference. Every target base belongs
to the existing 595-word library; the largest target base has 52 operations.
The checker compares 4,240 exact lifts at columns 1 and 4. The all-size
claim follows from the literal operation-major, lane-minor lift rule, which
repeats each base operation once per column, rather than from that finite
sample alone.

The inherited input Job closure bounds source.word by 61N. The target
closure gives the same conservative bound. matcher_to appends at most one
swap in each of its N iterations, then concatenates source.word, swaps,
and inverse(target.word). It does not multiply coefficients. Consequently
123N is a valid bound, unchanged under inversion.

Independent inversion of every library word agrees with the source.
The complete original/inverse census needs six signed numerator bits and
five denominator bits. In particular, pair (45,388), operation 39, has
scale 7/20; its reciprocal 20/7 cannot fit a five-bit signed numerator.
The independent check catches the corrupted value -12/7. Inversion introduces
no other coefficient operation besides add negation and scale reciprocation.

All 1,190 tested matcher/inverse images agree bit-for-bit with an independent
field concatenation, and decode exactly. Each matcher followed by its
independent inverse restores a complete ambient modular test row, providing
a separate chronology check.

## Actual source retention and reverse return

The original BinaryWord.native, StrongBinarySource.raw and BinarySource.inner
run against a bank observer whose numerical payloads are abstracted. The
first paid suspension has exactly 18,906 saved entries, equal in order to
the first 18,906 entrance routes. Exhausting the source produces 104,904 paid
calls and 53,796 route calls. Its final 18,906 routes equal independent word
inversion of the saved list in reverse order. Original productive owners
remain, while temporary private owners retire. This does not establish the
numerical restoration or zero hypotheses, which remain inherited.

There is exactly one append site, during entrance processing. Private INIT
registers and later private route words do not append. The list remains
retained through closing until native return, so the inclusive context bound
must cover initialization and closing; the final proof says so explicitly.

ActiveCatalogue's overriding initializer assigns seven fields and never
calls the older Catalogue initializer that installs cached methods. The
instance dictionary stays unchanged throughout the complete target census.
The active_catalogue factory is uncached. The fixed zero-argument chart cache
is separately counted. This is a precise instance-cache distinction, not a
claim that all runtime caches are bounded.

## Universal storage and history calculation

An operation uses 2h+13 bits. With w=128h and P=18,906, one full list uses

    L = w + P*(2w + 123N*(2h+13)).
    L/(Nh) = 128/N + P*(256/N + 246 + 1599/h).

Every nonconstant term decreases for h>=3000 and N=2^h. Exact rational
evaluation at the lower endpoint proves L<2^23 Nh universally. Four roles,
two-bit symbol coding and C=2N^83 slots give

    total = 8CL + 2048Cw;
    total/(N^84 h) = 16*(L/(Nh)) + 524288/N < 2^28.

Since 28<9h, this is less than BNh=N^93 h. The inherited W>=B*9^N and
9^N>Nh give BNh<W. The bit count is compared with the numerical byte count
W, so no missing factor eight weakens the inequality.

The final proof allocates four fixed tapes with C reusable segments. A
context keeps its slot through its last inverse route and completed return,
then clears/releases it. Successive contexts reuse those physical segments.
Thus history does not grow with the number of context identifiers. Segment
offsets fit w: log2(CL)<24+84h+log2(h)<128h. The scalar reserve covers bounded
occupancy and framing values. Full sequential scans suffice; their time is
not part of this theorem. A three-slot, 27-call control explicitly distinguishes
fixed-role history from invalid fresh allocation on every call.

## Controls and excluded scope

Nine negative controls catch numerator, denominator and coordinate overflow,
zero scale, truncation, five-bit reciprocation, forward list order, missing
word inversion, and fresh-role history growth. Normal and optimized receipts
are required to agree before freeze.

Matcher-construction arrays, caller port arrays, active dictionaries, inner
registers, generator frames, other route words, allocator state, numerical
route bodies, and dispatch/access time remain outside this accepted theorem.
This is a partial discharge for one previously excluded native value class;
the remaining service representation and paid-cost composition still require
separate proof before any canonical assumption can be removed.
