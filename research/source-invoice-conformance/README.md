# Extract recursive invoices from actual word and caller sources

This opt-in checker derives the recursive paid/target invoice from the literal
native word, its ownership contract and the literal p16/a7 caller. It does not
read author pricing functions, declared native paid profiles or caller invoice
tables to decide what to charge. A source-bound claim is compared against the
extracted result, with an event ledger for every bin.

The current [#5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383)
and [#5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387) words both
produce **64148 paid calls / 10800 productive targets**, including 128 lost H9
helper credits. Their backward scalar allowances are **158744 and 158776**,
respectively. Equal recursive histograms therefore do not identify their
implementations or ordinary costs. The checker preserves both differences.

The original selected-word calibration produces 64404 paid / 10928 targets.
All three exact histograms match separately retained author claim data.
This is independent extraction and symbolic protocol checking, not a new
construction, discovery of those known deltas or selected-frontier update.

## Use on a new recipe

Python 3.12, standard library only. Export the literal word and caller in the
supported schemas; no predecessor evaluator is imported.

```sh
python3.12 -I -B research/source-invoice-conformance/conform.py \
  --word path/to/WORD.json.gz --controller path/to/CONTROLLER.json \
  --write-invoice /tmp/extracted-invoice.json \
  --write-audit /tmp/source-event-audit.json \
  --write-claim /tmp/proposed-invoice-claim.json
```

The first run reports `EXTRACTED_RECURSIVE_INVOICE`. Review the proposed claim
and compare it with the intended pricing input. To check an existing claim,
add `--expect path/to/CLAIM.json`; a successful match reports
`PASS_SOURCE_INVOICE_CONFORMANCE`, and mismatches exit nonzero with per-rank
claimed/extracted counts. Output paths refuse to overwrite existing files.
For example, an omitted debit reports `targets H9: claimed 5868, extracted 5740`.

The invoice output uses the signed preflight schema of
[#5397](https://github.com/CrocSwap/integer-mult-bounds/pull/5397). The audit
contains actual native event IDs, actual caller call IDs, explicit surrendered
targets, outer query/idle charges, derived main targets, scalar/native/adapter
obligations and exact source/checker hashes. Local templates and call-site
lists factor repeated events without losing multiplicity. The complete
recursive-ledger hash includes local, outer and main contributions.

The claim format is `source-invoice-claim/v1`: `source_binding` holds the SHA256
of canonical compact JSON for the word and caller, and `invoice` holds the full
preflight object. Canonical hashes exclude whitespace and the final newline;
they are different from raw decompressed-payload or gzip hashes. No algorithm
executes source-supplied Python. JSON rejects duplicate keys and floating-point
numbers; rational strings use bounded integer/ratio notation. Supported table
and symbolic-term limits are explicit in the interpreters.

## What the pass establishes

[PROOF.md](PROOF.md) specifies the interpretation and accounting argument.

* Exact sparse rows check every borrowed main/helper endpoint, owned erasure,
  CLEAR/COPY ownership, and every zero-retag's full zero row.
* Binary subspace images check each declared native map's frame transport;
  paid ranks are independently derived from nested frame dimensions.
* Exact Laurent replay executes both scalar boundary programs and all caller
  events, checks every stage occurrence and derives the whole diagonal.
* Actual LOCAL orientations multiply local event ledgers. Query/whole-idle
  calls and main targets are derived directly from the caller. Owned helper
  inputs earn no autonomous target credit.

This is **symbolic source-protocol and recursive-invoice conformance**. The
caller stage labels are independent formal variables; the input format does
not supply a proof of their physical fresh-stage/coordinate embedding. Absolute
native phase, precision/tape implementation, ordinary-work funding, recursive
compiler and analytic recovery remain separate, explicit report obligations.
The checker does not independently resolve the physical-reference/embedding
failure classes discussed in
[#5349](https://github.com/CrocSwap/integer-mult-bounds/pull/5349) and
[#5380](https://github.com/CrocSwap/integer-mult-bounds/pull/5380).

The compatibility/funding oracle in
[#5391](https://github.com/CrocSwap/integer-mult-bounds/pull/5391) consumes trusted
independent evidence. This package supplies a preceding source-extraction tool;
it does not replace that oracle, its reviewer policy or its scientific engines.
Hashes identify artifacts and code, not the truth of an unchecked physical claim.

## Reproduce the calibrations

```sh
python3.12 -B scripts/research_package.py --package research/source-invoice-conformance --check-only
python3.12 -B scripts/research_package.py --package research/source-invoice-conformance
python3.12 -B scripts/check_research_commit.py --package research/source-invoice-conformance
```

Normal and optimized checks compare the full typed RESULT.json. `verify.py
--emit` prints a fresh receipt without changing the committed one. Three
complete source calibrations, 24 semantic/interface controls and a full CLI
round trip exercise the tool. [EVIDENCE.md](EVIDENCE.md) records exact source
pins, provenance, environment, coverage and unrun obligations.

## Open next questions

1. Bind a generated physical caller's coordinate/tape maps to these formal
   stages. Start with one actual LOCAL/IDLE transition; embedding and absolute
   native phase remain required before any physical supplier conclusion.
2. Emit this source ledger directly from a current generator and add a consumer
   to the evidence oracle under a separately reviewed policy. The first step
   is byte-bound recipe export; a generator's own histogram is insufficient.
3. Add another ownership/target ABI only after stating its endpoint contract.
   Coupled helper outputs require an explicit new adapter, not autonomous
   target credit inferred from their count or rank.

## Attribution

[@intqwq](https://github.com/intqwq) supplied the selected native word in
[#4610](https://github.com/CrocSwap/integer-mult-bounds/pull/4610),
[@aliromman](https://github.com/aliromman) supplied the changed owned-relation
word in [#5383](https://github.com/CrocSwap/integer-mult-bounds/pull/5383),
and [@Dugongue](https://github.com/Dugongue) supplied the successor in
[#5387](https://github.com/CrocSwap/integer-mult-bounds/pull/5387).
[@Clear1nsight](https://github.com/Clear1nsight)'s
[#5241](https://github.com/CrocSwap/integer-mult-bounds/pull/5241) and
[#5391](https://github.com/CrocSwap/integer-mult-bounds/pull/5391) retain their
independent admission/oracle credit. The source schemas, formal-row convention,
caller, dyadic allowance and mixed-target tariff retain Cinna Davis, zxv,
Jacob Alan Sussman, the native Clifford/controller/analytic/ordinary-BIT lineage
and original contributor credit. This independent tool imports none of the
producer engines. New implementation by [@zxv](https://github.com/zxv), with
substantial OpenAI Codex assistance in code, source analysis and assisted review.
Review shares source context; no independent human or formal-kernel acceptance
is claimed. Apache-2.0.
