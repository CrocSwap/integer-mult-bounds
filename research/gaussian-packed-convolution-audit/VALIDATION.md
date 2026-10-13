# Recorded validation

Local platform: Darwin arm64, CPython 3.9.6 (Xcode's Python), standard library
only. These are local execution results, not GitHub CI or human peer review.

## Mathematical and source-bound replay

The initial explicit bootstrap generated EXPECTED.json. A subsequent fresh
verification compared the complete recomputed result and wrote a separate
receipt outside the checkout:

```sh
python3 -B research/gaussian-packed-convolution-audit/verify.py --output /absolute/new/packing-replay.json
```

Observed:

```text
PASS_INDEPENDENT_SIGNED_PACKED_CONVOLUTION
integer_products=180960
max_input_numerator_bits=128
max_operand_bits=8219
negative_output_coordinates=41858
output_coordinates=183212
source_calls=45240
vector_pairs=22620
zero_output_coordinates=99385
semantic mutants rejected=8; admission controls=3
```

The original and freshly compared receipt were byte-identical, with SHA256:

```text
8ca661b0127a3a469186f3c2adcde105781d02a958ee44bfd6cc8a0edde1a0c7
```

The tested checker has SHA256:

```text
3feae2be75462f6e7e983f7db1f1f3c6dc61eceff20463b5747797ee73c4e48a
```

Vendor source/license bytes were checked directly against `git show` at
PR489 head `8922e3b3f0fd7772b0fb42028eb2532984c3ab42` when retained.
The checker independently rechecks their SHA256 and Git blob hashes before
and after its calls. No network or historical checkout is required to replay.

## Relocation and fail-closed package tests

```sh
python3 -B research/gaussian-packed-convolution-audit/test_package.py
```

Passed with `PASS_PACKED_CONVOLUTION_PACKAGE_CONTROLS`.
`PACKAGE-CHECKS.json` records the actual six subprocess dispositions:

- A full `-I -B` replay from an unrelated temporary directory with spaces
  passed and produced the byte-identical complete receipt.
- Optimized `-O` execution was refused before relying on inherited assertions.
- Changed vendor bytes were rejected specifically by the source SHA256 check.
- Changed expected evidence was rejected by complete receipt comparison.
- Missing expected evidence caused failure rather than silent bootstrapping.
- An existing output file caused failure and its sentinel bytes were preserved.

These packaging failures are intentional controls. They are distinct from
the eight semantic mutants, which must execute and produce demonstrably
incorrect arithmetic outputs.

## Selected-record and repository boundary

```sh
make selected-record-check
```

Passed:

```text
PASS selected record, exact kappa, original source inventory and proof supplement: 51110230636731/31250000000000000
```

At the validation refresh, upstream main remained
`66849e1475c930fd7732b1a0067ffee7e1e95f60` and the audited PR489 head remained
unchanged. The overlap review was refreshed through PR687. Concurrent PR684
studies Gaussian chirp domain/window/precision budgets and explicitly excludes
packing; it is distinct and supplies no dependency here. Other nearby work
concerns cyclic inverses, factory circuits, owner maps or symbolic identities.

All additions are confined to this research directory. The selected record,
its providers, existing generators, `upstream/`, and other research packages
are unchanged. The root-wide regenerating `make verify`, selected supplier
cold replay, Linux execution, GitHub CI and Lean were not run for this
standalone addition. No success of those checks is asserted.

The ordinary `git diff --check` passed during development. The final
`git diff --cached --check` passed, all 12 staged paths were inside this
package, and a direct base comparison confirmed that `upstream/` is unchanged.
The arithmetic result is limited exactly as stated in README.md and PROOF.md.
