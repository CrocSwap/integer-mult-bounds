# Complete local rounded tables for the current native word

This package constructs every ADD and SCALE coefficient table for the
exact [PR 7660](https://github.com/CrocSwap/integer-mult-bounds/pull/7660)
native candidate. It binds all 143376 local scalar occurrences to the
constructed tables. No complete recursive dispatcher or new kappa is
claimed.

The source head is `d12b854d4825e9edfa3a3466909e1abf3525e929` and its decoded
word SHA256 is `f0753b6614b2d351723dddc307a39b6ecd748a43008c6fdb9335b01feeec9669`.
The source has no COPY opcode. The caller's scalar operations are outside
this native catalogue.

The unchanged [PR 6988](https://github.com/CrocSwap/integer-mult-bounds/pull/6988)
SCALE compiler and [PR 6990](https://github.com/CrocSwap/integer-mult-bounds/pull/6990)
compact ADD compiler supply the literal tables and their all-size proofs.
Those packages left full local coefficient construction open. The new
work completes that finite coverage on this current word and gives its
occurrence-weighted physical scalar bound.

## Checked coverage

| Quantity | ADD | SCALE |
| --- | ---: | ---: |
| Exact local occurrences | 139227 | 4149 |
| Distinct coefficient tables | 2196 | 74 |
| Constructed literal rows, before sharing | 33462625 | 94164 |
| Constructed states, before sharing | 14551636 | 42076 |
| Largest table, in rows | 63503 | 14219 |
| Literal signed/range cases | 6588 | 148 |
| Successful cases | 2608 | 107 |
| Correct range rejections | 3980 | 41 |

The [ADD catalogue](CATALOGUE-ADD.json) and
[SCALE catalogue](CATALOGUE-SCALE.json) record each coefficient, occurrence
count, first and last clock, complete token hash, complete graph hash,
construction receipt and literal execution cases. Each graph is built,
checked and executed before the next graph. The verifier does not retain
all graphs at once or run the full native program on numeric payloads.

The local key is `("local", clock, complete_event_tuple)`. Each group maps
all its exact keys to the actual immutable table object. A forward chart
and lifetime scan checks every source event. A separate reverse raw-opcode
census agrees with every coefficient multiplicity. The registry covers
every selected source clock once. It is a finite local registry certificate,
not a production recursive table loader.

Every ADD coefficient receives a fitting signed cancellation case, a late
whole-field overflow case and a width-one endpoint case. Every SCALE
coefficient receives fitting signed inputs and width-one endpoints.
The unchanged literal lifecycle fixture checks source/context preservation,
head return and successful work retirement. Failure protects the entire
public target and may leave work or heads dirty. ADD endpoint cases also
reuse the work left by the preceding failed case.

Wrong coefficient tables fail the independent integer oracle for both
classes. Nonunit tape moves fail the graph checker. Wrong raw event keys
are absent from every group. Runtime graphs contain only the retained six
opcodes and exactly two private work ports.

## Positive cost bound

The native ADD coefficients have bit length at most 18, denominator
power of two at most 11 and odd denominator at most 25. Their compact
numerator extension is at most 20 bits. The SCALE maxima are 8, 6 and 9.
All coefficients fit the retained compiler domains. No compiler is changed.

Let S bound each field's numeric virtual extent, including delimiters,
and let R bound its real component count. Let A_i be the total old dirty
physical work length for scalar invocation i, and Q_i its borrowed context
count. If every invocation meets the retained service's shape, range and
physical preconditions, the complete native scalar sequence is bounded by:

```text
748695040(S+1) + 4241749760R + 7 sum_i A_i + 16 sum_i Q_i
```

These are physical reads, writes, unit moves and executed control rows.
[COST.json](COST.json) separates ADD and SCALE. A reverse per-event source
calculation and the forward weighted construction receipts give the same
coefficients. [PROOF.md](PROOF.md) states the per-call formulas and storage.

This bound covers the local scalar services. It excludes native MOVEs,
owned lifetime services, row delivery, full recursive dispatch, caller
operations and outer recovery. The unshared fixed catalogue has 33556789
literal rows and 14593712 states. Its positive setup/control representation
is separate. No common-bank layout or exchange rate into the old ordinary
model is assumed.

## Scope and limits

The operation is nearest-up rounding, with success exactly when all final
signed outputs fit. This does not prove that every actual recursive input
meets that range contract. Public and work tapes must be distinct; input
formats, matching grids, origin heads, contiguous old scratch and blank
historical tails remain explicit premises. Successful retirement does not
release historical backing capacity.

The all-size numerical and lifecycle proofs are retained predecessor
results. The new verifier independently checks finite coverage and integer
oracles; its cases are not a new proof over every input or width. No full
native/caller execution, all-column provider, complete owned backing,
common physical supplier tariff or rounded outer recovery is established.
The five inherited assumptions remain. The selected frontier is unchanged.

## Reproduce

Use Python 3.12 and the standard library:

```sh
python3.12 -B scripts/research_package.py --package research/current-native-rounded-catalogue
```

Four registered commands construct ADD and SCALE catalogues under normal
and optimized isolated Python. Each prints
`PASS_CURRENT_NATIVE_ROUNDED_CATALOGUE`. The runner must print
`PASS_REGISTERED_RESEARCH_PACKAGE`. Normal replay writes no files and uses
no Git, network or solver. The explicit `--write` option only creates an
initial receipt and refuses to overwrite one.

## Open next questions

Bind recursive row delivery, input ranges and the whole physical tariff
before caller admission. The complete graph hashes can also support a
separate state-sharing construction with its own delivery cost and proof.
[TASK.json](TASK.json) states the boundaries and first steps.

## Credit

CubeJerry supplied both unchanged compilers, the lifecycle executor,
physical fixtures and general proofs. Their declared source closure and
headers preserve their predecessor licenses and credit. Clear1nsight
supplied the exact candidate and review request; the copied source NOTICE
preserves the DreamingOfClouds, SYLforge, Ali Romman and Rohan Arun lineage.
Nick Petalas's [PR 7268](https://github.com/CrocSwap/integer-mult-bounds/pull/7268)
is related residue-graph work; this package uses the unchanged merged
compact compiler. [PR 7662](https://github.com/CrocSwap/integer-mult-bounds/pull/7662)
checks a different implication: the exact half-ADD consumer and its isolated
terminal error. No code from that package is imported.

Ali Romman directed the new catalogue, cost aggregation and verification
with substantial OpenAI Codex assistance. New work is Apache-2.0. The base
is `e54523517d0f03e58352e647c403a5af3e525a57`.
