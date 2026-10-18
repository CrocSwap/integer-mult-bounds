# Independent numerical lifetime audit

This audit derives the non-callback numerical allocation bounds directly from
the six frozen Python modules in `vendor/`. It does not import `verify.py`.
The source pin supplied for the package is PR2801
`e2564b80b86fb77610b4b78701e5446a76fbe962`, exporting the PR2697
`a53fdf4bcbe33c6732f0bec1badc8c023380f9d1` lineage.
`independent.py` separately guards all six source SHA256 hashes.
The predecessor authorship and licenses are retained in `vendor/NOTICE.md`.
This new audit was prepared with substantial OpenAI Codex assistance. It is
an independent derivation/executable method within the same assisted session,
not a claim of independent human review.

## Quantity and hypotheses

Fix the set of **all entry-live numerical Words**, including ring constants,
context state, caller scratch and unrelated live residents. Let `B_r` and
`B_i` be their respective sets in disjoint residue and index arenas. We count
the maximum number of additional occupied arena slots, i.e.
`|arena.live - B_r|` or `|index_arena.live - B_i|`, while preserving every entry
resident. A Word is categorized by its arena, not by a claim that its value is
always a canonical residue: the residue arena also holds the modulus and radix.

The following are premises of the successful-call theorem:

1. The supplied `Ring` is valid: `M > 1`, binary Words have the common extent
   `L = bit_length(M) + 1`, exactly one high zero bit, and canonical binary
   digits/delimiters. Borrowed operands are live, and the arena's unused slots
   are erased. Capacity is adequate for the stated peak. The permanent zero
   template is correct and has its canonical head. No allocator or tape
   operation fails. This is a bound on live numerical occupancy, not the
   count/size of allocated backing objects.
2. Every touched borrowed Word or tape starts at head 1. Successful helpers
   restore it to head 1. Thus the theorem restores canonical entry heads;
   it does not promise to preserve arbitrary initial head positions. Unrelated
   entry residents are never accessed and retain their own initial states.
3. For `directory.produce`, `q >= 2`, `M = q^w` with integer `w >= 1`, integer
   dimension `d >= 1`, `context.cap = M/q`, and the vocabulary is valid.
   `old_fields` is a canonical nonnegative count, `old_count` a canonical
   positive count, and `old` contains exactly that many physical prefixes,
   each with exactly `old_fields` records, valid codes, exactly `d^2` full-width
   high digits per record, each digit less than `cap`, and valid delimiters.
   All context residents already exist at entry, including any `highs` Count;
   constructing `Context` is outside this interval.
4. For `stream.add_pass`, the three spectator extents are positive binary
   counts, each encoded with its own single high zero margin. The input is a
   complete Boolean fibre of length `before * M * middle * M * suffix`.
   Use the default `Tape` factory, or an equivalent factory that returns
   distinct empty payload tapes and does not allocate numerical Words or
   mutate numerical entry state. An arbitrary user-supplied factory is outside
   the bound. Count and payload tape methods are likewise the frozen methods,
   without injected numerical side effects.
5. A coefficient callback terminates, preserves every entry resident, and
   leaves exactly one **new, owned, full-width residue-arena Word** holding a
   canonical coefficient. It cleans all other extra residue/index Words and
   restores borrowed heads. Returning a borrowed entry Word violates ownership:
   the stream unconditionally frees the returned Word. For the intended ADD
   permutation, the two callback results must have equal values. Equal values
   are not needed merely to derive the numerical bound.

No count tapes, payload symbols, serialized directory/program records,
continuations, descriptors, Python control objects, arena templates, erased
backing slots, retained bytearray capacity or physical movement are included in
this numerical category. Returned output and cardinality tapes also require
separate storage and disposal accounting. In particular, “zero index Words”
does not mean “zero counting storage.”

## All-parameter source derivation

`Unsigned.divmod` copies the numerator, allocates quotient and remainder,
and processes one bit at a time. During a shift, old remainder and shifted
remainder coexist. During conditional subtraction, shifted remainder and its
replacement coexist; old remainder has already been freed. Hence exactly four
additional Words suffice above its borrowed numerator/denominator, and four
are attained during the first shift. `compare`, `zero`, `msb`, and rewinding
allocate no Words. This argument covers every valid width `L`.

`cardinality.radix_power` retains its own divisor and power while calling
`divmod`. Its peak is therefore `2 + 4 = 6`. Returned quotient/remainder and
the old power coexist briefly, but total occupancy then is only four.
It frees old power and remainder before yielding; the finalizer frees divisor
and current power. For a valid prime-power relation with `w >= 1`, a division
is executed, so six is attained. Primality of `q` is not needed for this
lifetime calculation; the exact relation `M=q^w` is enough.

`directory.produce` first completes `high_power`, before beginning any old
prefix or odometer work. `high_power` sequentially exhausts `d^2` radix
generators. Their numerical lifetimes never overlap. For each old prefix,
`old_prefix` decodes and frees one numerical high digit at a time. Only after
it returns does `Odometer` allocate all `d^2` digit Words. Advancing the odometer
uses in-place increment, comparison and zeroing, with no additional numerical
allocation. All digits are freed before the next old prefix. Thus the phase
ledger is:

| Producer phase | Additional residue Words | Additional index Words |
| --- | ---: | ---: |
| Expected cardinality, including `radix_power` | 6 | 0 |
| Decode one saved old prefix | at most 1 | 0 |
| Enumerate one high matrix | `d^2` | 0 |
| Successful return | 0 | 0 |

Consequently the exact peak for every successful call under these hypotheses
is `max(d^2, 6)`. Both phases really execute, so this is sharp rather than only
an upper bound. For `d=64` it is 4096. If the interface were extended to `d=0`,
all numerical loops are absent and this exact-peak assertion would need the
separate value zero; the displayed upper bound would remain valid.

For `stream.add_pass`, each traversal calls `prepare_coefficient` before it
allocates `x`. At that call site the stream owns no numerical Words. In a
successful traversal, the returned coefficient survives until the traversal
ends, and `x` survives until its outer iteration ends. These are the two
retained Words during a product calculation.

`Ring.multiply` returns one Word immediately if either operand is zero or one.
Otherwise it retains `scan` and `result`/`doubled`. `Ring.add` creates a sum
Word, and if reduction is required creates its replacement before freeing
the sum. At that point `scan`, the old accumulator, sum and replacement
coexist: four additional multiplication Words above the two operands. After
the product returns, only its result remains, and producing `leading` adds
one Word. Counters, payload copies and `increment_in_place` allocate no Words.

| Stream phase outside callback | Additional residue Words | Index Words |
| --- | ---: | ---: |
| Returned coefficient only | 1 | 0 |
| Coefficient, `x`, and general multiplication | at most 6 | 0 |
| Coefficient, `x`, `offset`, and `leading` | 4 | 0 |
| Between traversals / successful return | 0 | 0 |

The uniform outside-callback bound is six. More precisely, its exact peak is
four if both returned coefficients lie in `{0,1}`, and six if either
coefficient `c >= 2`. To see the latter, use the traversal iteration
`x=M-1 >= 2`. The nontrivial multiplication branch executes, and
`c*(M-1) >= M`; hence some modular doubling/addition must reduce. Its sum and
replacement then coexist with the scan and old accumulator. A smallest witness
is `M=3,c=2,x=2`. Positive extents ensure that the iteration is reached.

Suppose each callback has additional residue peak at most `R` and additional
index peak at most `I`, measured above the same complete entry baseline, and
its result is included in `R`. Necessarily `R >= 1`. At the first callback
entry there are no stream-owned Words; at the second, the first traversal's
coefficient and `x` have both been freed, and every product/leading Word has
already been freed. Therefore the complete successful ADD has bounds

`additional residues <= max(R,6)`, `additional indices <= I`.

This is maximum composition of disjoint phases, not `R+6`. Payload split tapes
survive between the two traversals, so this numerical maximum does not give
an analogous maximum for payload memory. If the two calls have distinct
contracts `R1,I1` and `R2,I2`, substitute `max(R1,R2,6)` and `max(I1,I2)`.

Successful return preserves every entry numerical Word's value, identity and
canonical head. The directory's borrowed source/count tapes and the stream's
source/extent tapes also return unchanged at head 1. This is an induction over
the above helper lifetimes and the frozen helpers' successful head restoration;
it is not a statement that all tapes/backing objects cease to exist.

## Rejection and semantic boundaries

The frozen implementations are not general failure transactions. The executable
audit preserves the following exact counterexamples; it does not modify source:

| Input defect | Rejection | Extra residue Words left live |
| --- | --- | ---: |
| Stream: `M=3`, callback returns fresh value 3 | `canonical encoded coefficient` | 1 |
| Stream: `M=3,c=2`, positive unit extents, empty payload | `opaque payload bit` | 4 |
| Directory: `q=2,M=4,d=1`, one old field with a one-bit rather than full-width high Word | `complete encoded word` | 1 |

The directory leak occurs because `read_word` allocates its output and rejects
before returning; `old_prefix` enters its Word-freeing `try/finally` only after
`read_word` returns. A capacity rejection during `Odometer` construction is also
outside the inner cleanup `try`; a failing radix operation can retain internal
division temporaries. These latter observations are source-path qualifications,
not additional exhaustive failure tests. Stream traversal has no enclosing
failure cleanup for returned coefficients, `x` or arithmetic results.
Successful-path restoration cannot be extended to these paths by inspection
of outer `finally` blocks alone. Arbitrary callback failure likewise needs its
own cleanup contract.

Repeated coefficient equality is a separate semantic premise: for `M=3`, unit
extents, and a one-hot payload at zero-based input position 3, callbacks `(1,1)`
produce a one at output position 4, whereas `(1,2)` are accepted and produce a
one at position 5. Both executions restore numerical entry state and obey the
same lifetime bounds. Thus successful return does not itself validate repeated
coefficient equality or the intended fixed-coefficient ADD.

## Executable coverage and proof level

Run from the repository root:

```sh
python3 -I -B research/selected-stream-directory-numerical-audit/independent.py
```

The script compiles each pinned source file directly from checked bytes, bypassing
`.pyc` files. An `Arena` observer records every allocation/free event and snapshots
all entry-resident cells and heads. A separate plain-integer lifetime model,
which never executes Word/Tape methods, predicts the entire allocation/free
sequence. Equality is checked event-for-event, not only at the maximum.
The finite covered domain is:

- All 135 pairs `2 <= M <= 16`, `0 <= c < M`, with the same `c` in both
  traversals, unit spectator extents, and all-zero complete payloads. These are
  exhaustive coefficient cases in that bounded domain, not exhaustive payloads.
- Directory cases `(q,M,d,old_fields,old_count)` equal to
  `(2,2,1,0,1)`, `(2,4,1,1,1)`, `(3,3,2,1,2)`, `(3,9,2,0,1)`,
  `(2,2,3,1,2)`, using canonical zero high fields. These are selected fixtures,
  not an exhaustive enumeration of all directories.
- A symbolic lifetime-model evaluation of `(q,M,d)=(3,3,64)` with peak 4096.
  This script does not claim a literal `d=64` source execution; the companion
  primary verifier separately covers that case.
- Four callback-composition cases with `(R,I)=(1,0),(5,2),(7,4),(13,1)`,
  all at `M=3,c=2`. Measured combined peaks are respectively `(6,0)`, `(6,2)`,
  `(7,4)`, `(13,1)`, and both callback entries have the complete baseline.
- The three rejecting witnesses and the accepted unequal-coefficient witness
  above. Every successful fixture also checks zero index allocations and exact
  restoration of all entry numerical Words and borrowed source/count tapes.
- An in-memory negative control wraps multiplication in one extra, fully freed
  temporary. Values and final ownership are preserved, but the allocation-event
  oracle rejects the changed lifetime. The wrapper is removed in a `finally`
  block; no frozen source file is changed.

The all-parameter argument is a written proof for the explicit frozen-source
successful-call model. The script is exact finite computation with an independent
allocation model. Neither is a formal-kernel proof. No new kappa, full caller
reserve theorem, physical tape realization, supplier admission or multiplication
bound follows from this numerical component alone.

## Open next questions

1. If rejected inputs are in the intended interface, add and audit explicit
   ownership rollback around partial Word decoding, odometer construction and
   stream traversal. First reproduce the three retained failure witnesses;
   source changes require a fresh proof and new pin.
2. Instantiate the callback contract from its complete caller, including all
   entry residents and any retained program/continuation state. Verify that a
   coefficient is a fresh owned result and equal across both invocations.
3. Combine numerical slots with the separate count, payload, directory,
   continuation and backing-storage categories, including each category's width
   and physical erasure/parking costs. The numerical maximum does not settle
   those simultaneous lifetimes.
