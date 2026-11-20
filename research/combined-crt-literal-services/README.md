# Execute joined CRT arithmetic and Word lifecycle

**One fixed 70-role graph now executes both providers on the same current CRT
Word inventory.** It joins the unchanged #7596 numerical graph to the published
literal lifecycle graph and executes a complete pinned small producer invocation
with the old arithmetic and Arena lifecycle providers unavailable.

The addition is the executed source-bound join, its selector/lifetime protocol,
and exact combined bills. It does not lower the higher controller or construct
blank grants.

## Result and sources

| Component | Pinned source |
|---|---|
| Canonical scientific base | e54523517d0f03e58352e647c403a5af3e525a57 |
| Numerical arithmetic | CrocSwap/integer-mult-bounds#7596, CubeJerry head ee6005fe241ab947e511fe9f6d86f5f4fa58478b |
| Literal lifecycle | CubeJerry commit 39c309f1aa72af12669d37ae055da0ece1ae0e7d, research/literal-crt-word-lifecycle |
| Union | 1,435,098 fixed R/W/M/J/H states, 70 fixed roles |

Numerical roles 0..63 retain identity. Four arithmetic selectors occupy
64..67; lifecycle reuses selectors 64/65 and places the template/stack at
68/69. Every lifecycle branch receives the same fixed state offset.
No generated instruction has a variable tape operand.

The full source fixture uses seven-bit Words, left [(5,1)] and right [(7,2)].
An independent integer CRT oracle gives lower 1, product 5, and output
(offset,updated)=(3,5). The run executes:

- 82 ADD calls, including 63 aliased doublings;
- 63 comparisons, 14 divisions, and 6 subtractions;
- 2,723 literal service calls totaling **3,515,628 instructions**;
- zero old arithmetic or lifecycle fallback calls in the producer/consumer
  interval.

The remaining native symbol bill is 2,518, including 468 actions for the
original Entry.close. Word predicates, record operations, controller work,
and blank acquisition remain explicit. The graph has 70 roles; this complete
source fixture has 76 actual owners after counting its guide and record tapes.
All capacity lists and per-role touched intervals are in RESULT.json.

## A concrete integration constraint

The original Entry.close still queries arena.live. Therefore the ordered
stack must remain active until those physical liveness queries finish.
The correct terminal order is producer/consumer, retained Entry.close,
then literal lifecycle CLOSE. A negative control demonstrates rejection
when metadata is retired first.

The other controls check physical backing aliasing, an active old-provider
sentinel, and a returned carry corruption that completes normal arithmetic
and head restoration.

## Exact arithmetic tariffs

For precision P and initial free-stack length m, complete arithmetic service
includes two paid live queries, physical reservations, four setters, and the
numerical body:

| Service | Exact instructions |
|---|---:|
| COMPARE, same handle | 125P+122m+754 |
| COMPARE, distinct handles | 247P+122m+968 |
| ADD/SUBTRACT, same handle | 279P+158m+1256 |
| ADD/SUBTRACT, distinct handles | 401P+158m+1470 |
| DIVIDE | 402P^2+923P+194m+1986+(278P+245)c |

Here c is the number of one bits in the quotient. The division formula is
derived directly from the unchanged long-division paths in PROOF.md.
All lifecycle formulas transfer unchanged under the role/state map.

These are exact local literal costs, not a whole-caller physical tariff.

## Reproduction

CPython 3.12, standard library, approximately 520 MiB peak memory.
For a cold checkout, fetch only the exact pending predecessor commits needed
by the source-history metadata gate; vendored direct checks remain offline:

```sh
git fetch --depth=1 --filter=blob:none https://github.com/CubeJerry/integer-mult-bounds.git ee6005fe241ab947e511fe9f6d86f5f4fa58478b
git fetch --depth=1 --filter=blob:none https://github.com/CubeJerry/integer-mult-bounds.git 39c309f1aa72af12669d37ae055da0ece1ae0e7d
```

Then run:

    python3 -B scripts/research_package.py --package research/combined-crt-literal-services

Or run the main replay directly:

    python3 -I -B -W error research/combined-crt-literal-services/verify.py

The registered normal and optimized runs reconstruct the graph and compare
the complete deterministic receipt. The generated graph remains in memory
and is not committed. Fourteen pinned source files total only 141,987 bytes.

The primitive suite checks every four-bit operand pair for all three simple
operations, every aliased four-bit input, all four-bit numerators against
divisors 1..7, and explicit wider cases at P=7,19. It covers 972 numerical
primitive calls amid allocation, copying, freeing and reuse, with unequal
historical capacities. The complete suite executes 18,380 public literal
calls and 31,886,648 literal instructions.

Measured primary replay took approximately 28 seconds, including approximately
7 seconds of graph construction. ENVIRONMENT.json records the actual runtime
and resource observations. These measurements are verifier costs.

## Independent root cross-review

[REVIEW.md](REVIEW.md) records the separate mathematical and implementation
review. Its verifier checks every one of the 1,435,098 instructions by inverse
relocation and recovers both immutable predecessor graph hashes. A separate
raw-cell interpreter, using none of the author runtime, Tape, WordPort or Audit
classes, checks complete service traces at new precisions 5, 9 and 17, including
shared selectors, actual stack reservation, carry/borrow, exact division,
suspended heads and unequal retained histories. It rejects an omitted template
role relocation. The primary full-source replay remains separately registered.

## Scope and remaining premises

PROOF.md gives the local all-admitted-traces composition argument. Finite
executions check the implementation and one complete exact-source invocation.
The original numerical admission/live-stock proof remains credited.

The sealed interval blocks compare, add, subtract, divmod, shift_add_bit,
Arena.zero/copy/free and Word.erase. Original Entry.close is subsequently
executed as a separately priced retained service. No broader claim that every
Word or record method is literal is made.

All five selected framework assumptions remain. The selected conditional
kappa 0.00363005817 is unchanged. No complete multiplier, changing-Entry
wrapper, human review, or formal-kernel result is claimed.

## Files

- PROOF.md: role/state simulation, ownership, terminal order, exact tariffs,
  historical storage, source substitution and limits.
- join.py: small authenticated generator, 70-role interpreter and typed adapter.
- verify.py: complete semantic/ownership/head/history oracle and source replay.
- RESULT.json: exact deterministic domains and receipts.
- SOURCE-PINS.json and SOURCES.json: compact dependency closure and provenance.
- NOTICE.md: original source and predecessor credit.

## Open next questions

1. Attach this exact union across the changing-Entry caller, preserving the
   final-query/metadata-retirement ordering and every physical history.
2. Lower the retained Word predicates, record interfaces and controller under
   a common physical tariff; first enumerate their remaining actions.
3. Supply compatible blank grants and framing, including dirty-history
   obligations, rather than inferring clean stock from this replay.

Prepared for Jerry Chen / @CubeJerry with substantial OpenAI assistance.
The original current CRT source is JoyboyBrian's; #7596 and the published
lifecycle package retain their numerical, compiler and ownership credit.

