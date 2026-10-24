# Compare the complete recursive invoice before extending a construction

The same local edit can save scalar instructions while worsening its recursive
bill. Conversely, owning a helper can remove paid work while also surrendering
a productive target. Compare **both** paid jobs and target credits first:

```sh
python3 -B scripts/compare_recursive_invoices.py OLD.json NEW.json
```

This standard-library tool uses integer arithmetic, without a root search or
contribution replay. It reports an exact certificate for every increasing
concave rank tariff with f(0)=0, including r^(1-C), 0<C<1. The method is classical
concave order, already used by mightyOil's
[T16 audit](../../research/t16-moment-order-audit/README.md) and its predecessors.
The shared interface adds signed target accounting; it is not a new theorem.
The concurrent [source-bound pricing oracle #5391](https://github.com/CrocSwap/integer-mult-bounds/pull/5391)
checks compatibility of reviewed physical, invoice, closure and funding receipts.
This comparator is an earlier arithmetic screen, not a replacement for that
evidence join or its trusted policies.

## Input and meaning

Both files use this schema, with identical declared accounting contracts:

```json
{
  "schema": "integer-mult-recursive-invoice/v1",
  "contract": {
    "model": "mixed-target-unnormalized-power-v1",
    "rank_semantics": "H_r costs r^(1-C); debit surrendered productive fields",
    "ambient_rank": 145,
    "boundary": "complete unit before the same mixed-target compiler"
  },
  "paid": {"1": 1, "8": 1},
  "targets": {"9": 1}
}
```

Ranks are canonical positive integer strings; counts are nonnegative integers.
The contract identifies the common pricing and consumer boundary. A change in
ownership can change targets inside that boundary, but requires its own legal
construction and complete debit. Different rank meanings, normalization rules
or transfer contracts require a separately justified comparison. Matching text
does not prove applicability.

The tool hashes the exact input bytes. It does **not** derive the invoice from
a circuit, detect an omitted target debit, or authenticate an author's source
claim. Keep the source word, extraction command and exact head with the invoice.
The [worked package](../../research/owned-relation-exhaustion/README.md)
independently reconstructs its complete source invoice before comparing it.

| Result | What it establishes | Next action |
|---|---|---|
| `uniformly_worse` | Larger paid-minus-target cost for every power 0<t<1. | Stop this raw-moment improvement claim; identify a changed charge or contract before expanding it. |
| `equal` | Identical net raw moment at every rank tariff. | Report scalar/compiler/implementation gains separately. Same invoice can still improve a funded compiler endpoint. |
| `uniformly_better` | Smaller paid-minus-target cost for every power 0<t<1. | Price the complete candidate and prove its source, ownership, phase and caller obligations. |
| `inconclusive` | Concave order does not decide the comparison. | Use a scoped exact power-moment calculation; mixed signs alone establish no crossing or failure. |

For general concave tariffs the order is weak: a linear tariff can give equality.
The strict power conclusion requires a nonzero signed difference. These results
do not imply circuit equivalence, an admitted supplier or a compiler endpoint.

## Recent discriminating examples

* [#5350](https://github.com/CrocSwap/integer-mult-bounds/pull/5350): the filtered
  151-ADD compression preserves the recursive invoice. Its unfiltered variant
  splits one H4 into two H2 jobs, a strict loss for every 0<t<1. Scalar event count
  alone chooses the wrong variant.
* [#5377](https://github.com/CrocSwap/integer-mult-bounds/pull/5377) and
  [#5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383): removing H1+H8
  and debiting H9 gives a strict gain, 1+8^t-9^t>0. Leaving the H9 target credited
  produces a much larger, unsupported budget.
* [#5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387) and
  [#5390](https://github.com/CrocSwap/integer-mult-bounds/pull/5390): compiler
  refinements retain the same recursive invoice. #5390 also reports a smaller
  sufficient compiler at a matched exponent. `equal` is therefore not a reason
  to dismiss a compiler or implementation contribution.

Run the source-bound current examples:

```sh
python3 -B scripts/compare_recursive_invoices.py \
  research/owned-relation-exhaustion/examples/source.json \
  research/owned-relation-exhaustion/examples/exchange-128.json
python3 -B scripts/compare_recursive_invoices.py \
  research/owned-relation-exhaustion/examples/source.json \
  research/owned-relation-exhaustion/examples/h4-split.json
```

The second is a declared single-H4 edit to the complete source invoice, illustrating
the unfiltered retiming's algebra; it is not a newly emitted physical supplier.

## Certificate and bounds

Set d_r=Δpaid_r-Δtargets_r. The report gives K(k)=Σ d_r min(r,k) at every support
breakpoint. Between breakpoints K is linear. If all K are nonnegative, every
increasing concave cost change is nonnegative; reversing the signs gives the
reverse order. The discrete-slope proof is in the script and the worked package.
No equal-rank-mass assumption is required.

Inputs are bounded to 1 MiB, 4,096 keys per histogram, ranks at most 10^9 and counts
at most 10^60. The implementation sweeps sparse support; it does not allocate an
array of ambient width. Duplicate keys, floats, booleans and differing contracts
fail with a diagnostic and exit code 2. Valid comparisons, including inconclusive
ones, exit 0: this is an arithmetic report, not an automatic acceptance gate.

Prepared for zxv with substantial OpenAI Codex assistance. Apache-2.0.
