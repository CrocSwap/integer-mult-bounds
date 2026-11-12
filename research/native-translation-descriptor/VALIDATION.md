# Executed verification and frozen scope

The scientific implementation and accepted proof are frozen at:

- `translate.py` SHA256
  `e2750fef8c2b9c8019d67285df3ca0d04340cd241782c7845665b7de621ca3bd`.
- `PROOF.md` SHA256
  `6b76d348203aed15cbc30d104c59571111ccf6cb7bb4592936e9170f736b68e0`.
- Generated graph SHA256
  `7a439b8fd62e932fe148859d62a091f11ffac3118e41c60b3166ee7989916940`.

## Completed author checks

`bind_source.py` passed under normal and optimized isolated Python; its
parsed receipts are identical. It authenticates nine retained local inputs,
recomputes the actual source lowering, checks all 512 monomial basis states
for the post-matrix coordinate-zero translation, and rejects a changed axis.
The retained compiler/interpreter are credited source engines, not newly
claimed independent implementations.

The complete normal `verify.py --write` run passed. RESULT.json contains nine
complete successful executions, 702,464 payload bits and 57,517,967 local
transitions, including a full actual m=9,f=2 packet. It also records 104
encoder exact-census cases, three malformed boundary controls, three semantic
program mutants and retained-object history tests. A separate development
`--quick` run omitted f=2 and is not treated as complete evidence or included
as a scientific receipt.

The author uses the unchanged retained instruction interpreter with its own
source-coordinate expected-value formula. Rerunning that interpreter would
be regression testing, not an independent execution proof. The separately
written reviewer CPU supplies the independent runtime evidence below.

## Completed independent review

The lead independently inspected the all-size source/axis, Gamma, quotient,
geometric doubling, complete instruction census and history proof and accepted
its exact scope. All eleven commit:path source/provenance bindings were
retrieved and authenticated independently; the record is
`independent/SOURCE-BINDINGS.json`.

The reviewer's dense byte-array CPU does not call the author's interpreter or
oracle. Its separately derived exact instruction count matches ten complete
packets and 54,801,743 transitions, including actual m=9,f=2. Four malformed
cases and three mutations are checked. A functionally correct added instruction
is rejected by the exact cost census. Grow/shrink/regrow retains the same
physical byte arrays and their historical spans.

The reviewer executed both normal and optimized modes, producing identical
receipts. After copying all five frozen review artifacts unchanged into this
package, the author ran

```sh
python -I -W error -B research/native-translation-descriptor/independent/check.py research/native-translation-descriptor/translate.py
```

That relocated receipt is byte-identical to both independent originals and
is retained as RELOCATED-RESULT.json. VERIFY.json registers the complete author
run, both source-binding modes and both independent runtime modes.

## Package gates and limits

The canonical `scripts/research_package.py --package
research/native-translation-descriptor --check-only` passes with
`PASS_PACKAGE_METADATA_AND_PINS`. It is a metadata/source-pin gate, not
mathematical acceptance. No full repository cold replay, unrelated historical
suite, hosted CI or proof-assistant acceptance is claimed.

The full staged whitespace check reports the final blank line already present
in the exact retained C3 `reverse.py` and `PROOF.md`. Those two frozen files
remain byte-identical to their independently authenticated published sources.
The staged whitespace check excluding the retained reference directory passes;
new author files have no reported whitespace defects. No source was silently
normalized to suppress a provenance-preserving difference warning.

All successful execution costs are local reads/writes/unit moves/jumps/halt;
verifier counters, fixture generation and expected values do not feed runtime
branches. The universal conclusions follow from the written loop invariants
and exact census. Complete finite f=2 coverage is not proof by extrapolation.

The five-Gamma physical entry owner and layout remain supplied. The source
matrix, other native factors, full caller, owned allocation and multiplier
remain outside this result; no selected assumption or kappa is changed.
