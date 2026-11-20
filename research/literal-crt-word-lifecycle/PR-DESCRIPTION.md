## Contribution and significance

#7596 makes the raw CRT arithmetic literal but retains Word allocation,
copying, erasure and owner metadata. This package supplies that local lifecycle
with a physically encoded ordered free stack and an explicit reservation
contract for the existing arithmetic provider.

One fixed 130,936-location R/W/M/J/H graph preserves eight protected Word
owners and manages the remaining 56. It allocates the actual top slot, copies
complete Words, erases before release, restores heads and selectors, and
retains every physical history. For precision P and m free slots, COPY costs
287P+97m+676 instructions and FREE costs 160P+61m+409; the paid source setter
adds 31. The proof gives exact counts for every entry and all legal traces.

## Verification and execution boundary

`python3 -B scripts/research_package.py --package research/literal-crt-word-lifecycle`

The source-authenticated primary checks cover 4,544 primitive packets, all
64 handles at every stack length, a 360-operation changing-stack trace,
three complete pinned current producer calls and ten controls. A wrong-owner
return is detected despite complete head and selector restoration.

Actual-source execution retains the raw arithmetic backend and replaces the
Word lifecycle. The existing literal arithmetic graph's two reservation
interfaces are matched by proof; its complete combined execution is not
claimed in this package. Original lifecycle providers are unavailable during
the positive producer/consumer checks.

## Scope and remaining obligations

Initial grants and framing, higher numerical control, the changing-Entry
wrapper and the complete arithmetic/row/radix caller remain open. Inactive
older tails must already be blank, and their retained capacity is never
refunded. Failure rollback and arbitrary dirty-work acquisition are not supplied.

No new kappa. This is a scoped precision_tape/owned_erasure interface result;
all five foundational assumptions and the selected conditional bound remain.

## Provenance and credit

Base: e54523517d0f03e58352e647c403a5af3e525a57. Immediate source: #7596 at
ee6005fe241ab947e511fe9f6d86f5f4fa58478b. Credit JoyboyBrian's #5053 CRT
producer, the Word/entry/owner lineage #5219, #5353 and #5505, and the literal
arithmetic predecessors retained by #7596. Source files and notices are unchanged.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The package contains the proof, exact source pins, full receipt, limitations
and concrete next questions. Model-assisted checks do not constitute human
peer review or formal-kernel acceptance.

## Independent review

A separate interpreter checks all 15,872 numeric-dispatch paths, 10,204
service packets, unequal historical capacities and 15 reservation packets.
All displayed formulas agree; controls reject equal-value wrong owners and
an extra paid jump. A dirty-tail witness confirms the necessary blank-tail
premise. REVIEW.md records the proof audit and the retained raw arithmetic
boundary; no full joined arithmetic replay or new stock proof is claimed.
