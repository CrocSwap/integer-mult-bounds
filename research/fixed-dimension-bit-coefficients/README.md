# Encoded coefficients for every fixed dimension

This package supplies an actual dimension-matching numerical consumer for the
chronological whole-high field format of #6903. It specializes the retained
binary Callback, Fields, Matrices and arithmetic modules at **every fixed N≥2**,
preserves all N² digits and global source labels, and reuses the same four
continuation tapes across closed calls. Seventeen explicit source edits are
authenticated against their base bytes; no runtime numeric oracle replaces
the coefficient evaluator.

The callable entry is `Workspace.open`, followed by the returned callback's
method and `close`. The retained legacy `controller.selected_offset` wrapper
does not pass borrowed stack roles and is outside this package's interface.
Only the current live callback may be used. Closed or aborted handles are
permanently retired; the exclusivity flag is not a generation validator for
stale Python objects retained across later calls.

The written source-arena proof bounds the pending allocation **before its
capacity guard** by `16N²+128` residue Words and `128` index Words over all live
entry residents. It separately counts already allocated erased slots, full
chronological Program/Fields prefixes, and the four separate historical stack
maxima. Every admitted descriptor contracts its extent by at least `(N−1)/N`;
the resulting explicit consumer bill is polynomial in w and the actual root size.

**No new κ.** This is a source-arena and format-interface lemma. The selected
`.0034` base's actual catalogue/label generation, exact root-size map, emitted
finite-table interface and changing-precision physical bank remain unproved.
All five foundational assumptions of the selected multiplication bound remain.

## What was added

| Review target | Evidence |
| --- | --- |
| Actual specialized runtime and fixed continuation roles | [consumer.py](consumer.py) |
| All-depth semantics, noncircular capacity, history and complete local cost | [PROOF.md](PROOF.md) |
| Separate determinant/cofactor and integer elimination oracle | [check_consumer.py](check_consumer.py) |
| Exact examples and meaningful rejection controls | [RESULT.json](RESULT.json), [verify.py](verify.py) |
| Isolated corrupted-source/receipt/budget checks | [test_boundaries.py](test_boundaries.py) |
| Source and predecessor scope comparison | [OVERLAP.md](OVERLAP.md), [SOURCES.json](SOURCES.json) |

The actual examples cover dense N=2/3 fields, widths 1/2/3, mixed Good/Pair/Unit
histories including a halved Unit, inverse offset and leaf calls, erased warm
backing, and repeated use of the same continuation roles. N=44/rank43 crosses
the historical rank guard; N=65 crosses the field reader limit; N=130 reaches
target row 129 and crosses the separate index-multiplier limit. These synthetic
catalogue examples corroborate the universal written
proof; none is represented as the actual selected large compiler instance.

## Reproduce

From the repository root, Python 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/fixed-dimension-bit-coefficients --check-only
python3 -B scripts/research_package.py --package research/fixed-dimension-bit-coefficients
```

The registered replay is read-only and includes normal/optimized execution and
isolated failure controls. [VALIDATION.md](VALIDATION.md) records executed
coverage and its limits. `verify.py --write-result` explicitly regenerates
the receipt; normal verification compares all typed fields. Source pins use
base `e54523517d0f03e58352e647c403a5af3e525a57`.

## Open next questions

1. Bind the completed `.0034` controller's exact catalogue and chronological
   labels to this consumer; begin with its compiler output and all branch kinds.
2. Prove its actual `root_size≤e` coupling and the counted coefficient calls
   per charged fibre before using the conditional exponential absorption lemma.
3. Install the fixed roles across changing precision, charging all ancestor
   records, producer STATE/PREFIX copies, payload access and restoration.

## Credit

Prepared for @CubeJerry with substantial OpenAI Codex assistance. Jose Manuel
(@jmbarrancoml) supplied the retained arithmetic/matrix/record/evaluator lineage;
Ross Richardson's #2835 supplied the prefix-capacity proof method, building on
Nick Petalas and Arham Tahir's lifetimes. #5404 supplied the historical backing
distinction; #6879 and #6896 supply separate helper/recursive capacity results.
The generic-N chronological producer is credited to #6903 and its #5829/#6719
predecessors. See [NOTICE.md](NOTICE.md) for the full retained source notice and
scope. New work is Apache-2.0; no formal-kernel or independent human review is
claimed.
