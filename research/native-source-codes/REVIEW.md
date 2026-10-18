# Final independent review of the input source-code package

Result: **PASS_INDEPENDENT_INPUT_ONLY_PACKAGE**. No material local
finding remains in the reviewed files. This is an independent agent
review with substantial OpenAI Codex assistance, not a human review.

## Final file binding

The final six implementation files were compared with the reviewed snapshot.
Five files are byte-identical. The only change in `source_data.py` removes
one extra newline at the end of the file. Its full Python AST is identical.
The final source hash is shown in the table below. The proof, README,
source manifest, and notice are byte-identical to the accepted documents.

The complete independent numerical review below ran on the original,
semantically identical bytes. The coordinating agent then ran the final
bytes into a fresh output directory. This reviewer checked the final code
hashes, status, and every emitted artifact hash. All four mathematical
output files, including the literal program gzip, are byte-identical to
the independent cold replay. The final `REPLAY.json` hash is
`afc99b0548ec30eee16d0f8a7a09f0a239477377c0b4e471bb02b86135a6dafa`.

The separate final binding receipt is `FINAL-INPUT-ONLY-PACKAGE-REVIEW.json`.
The original independent receipt and note remain unchanged. The final
binding does not claim a second independent numerical run on the changed
EOF bytes; it combines exact byte and AST comparison with the checked
final replay outputs.

## Frozen inputs and reproduction

The review binds the six implementation files and the final documents
listed in `INPUT-ONLY-PACKAGE-REVIEW.json`. The principal SHA-256 values
are:

| Item | SHA-256 |
| --- | --- |
| `certificate.json` | `f9ab470df50d7a9f9bc1e03fc0c1d30976c8f45f7bcbc0fb3ee371befdced652` |
| `input_logger.py` | `5da28577c3bd837652a363766c8662aecf4cd4a93bbe63aff2aa0bd72ebd5424` |
| `verify_input_logger.py` | `d09fccd2330e6258f5f47c81cef70ba16abfe8259bc3a0a542c4b4f3f95b0c75` |
| `native_verify.py` | `3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38` |
| `source_data.py` | `d23924511e3aed41e5e64511ca70126a636d91c8aa02e656cb61d6ceca1fe0a0` |
| `replay.py` | `f3304207dd664c98deb3a1a5bf4ea6e07cb64c86c79e9c26a5a4bafeb4d8a3ee` |
| `PROOF.md` | `8c62215f88ff4fcedb64d3761553d16a957b5520e7b8806fdd28ff41816c8972` |
| `README.md` | `b2d0877b54366dec25f801e652a5077d640ef226d1c1bb43a54d52710ae537b1` |

Before the EOF normalization, a fresh copy of the portable package was run against the isolated Git
checkout at commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. The exact
command was:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/package-review-input-only/package/replay.py \
  --repo /Users/aliromman/.codex/worktrees/native-source-codes/IntegerMultiplicationBounds \
  --out /Users/aliromman/Projects/IntegerMultiplicationBounds/work/centre-encoding-campaign-20261014/lanes/interface-proof/package-review-input-only/cold-output
```

The output was:

```text
PASS_INPUT_ONLY_SOURCE_CODES
All 712 formal input columns and 4096 new native Gaussian columns passed.
The complete supplier and kappa calculation are unchanged.
```

The `REPLAY.json` hash is
`8b5bf7a70e36e5083b4ded37ad186bf5075cd4b0461a6fed3ac9de7f42fa0dd1`.
The decompressed program payload hash is
`da312b84be11c580c129e284736dee81d55d63716d77611d839178c29ad25600`.
The package command in `README.md` reproduces this portable replay.

The reviewer also ran this separate workspace command:

```sh
python3 -I -O -B work/centre-encoding-campaign-20261014/lanes/interface-proof/review_input_only_package.py
```

It returned `PASS_INDEPENDENT_INPUT_ONLY_PACKAGE`. This external checker
has SHA-256
`d5786af2761628fd7f450a593a41920d69ad705fc045b5207474c394ab25ce18`.
It uses frozen workspace inputs and earlier independent review tools.
It is not a second portable package entry point. It imports neither the
package producer nor its verifier. The portable replay and this external
review are separate checks.

## Mathematical and implementation checks

The reviewer derived K, P, L, Z, Q, and J from the pinned actual R. The
review checks the two disjoint minors, `RZ=LZ=I`, `QZ=0`, and
`JZ=-13P`. It also checks that Z has rank eight and that the 104 off-A
rows of J have rank 104. No inverse of 13 or of 3 is used.

The general proof was checked over Z[1/2], including a non-scalar RK.
The order `Z=K-P(RK-I)` is required. The proof of
`ker J_offA=im Z` uses the dyadic inverse of R_A. It establishes the full
fixed-support source group, its inverse criterion, and its composition
law. It does not require an inverse of RK-I. Composition preserves the
eight-row native support; scalar costs can increase.

All four emitted streams were reconstructed independently from the
input matrices. Each literal prelude and complete word matches that
reconstruction. Exact reverse propagation checks all 712 formal input
columns, all 480 arbitrary helper contents, and all private outputs.
Forward propagation checks the source snapshots and private lifetimes.
The logger uses c0; the general pair uses eight snapshots. An inverse
prelude restores arbitrary persistent inputs in both orders. Used private
fields end at zero, while unused private fields are unchanged. Each
complete retained call clears all eight private fields.

The native check compares all eight added recipes on every one of the
512 computational basis inputs, with exact Gaussian dyadic arithmetic.
The result is the positive intrinsic C_p input operator, before the old
entry adapters. This is not an assumption that C_p equals the canonical
rank-one frame. Wrong inverse signs and scalar phases are rejected.
The exact tensor identities apply at every positive tensor size; native
scalar phases are raised to that tensor power.

The 5056 retained native events stay in their original order. Their
previous exact native review is reused; this audit does not repeat every
retained child kernel. The input-boundary dependency is the independent
receipt `INPUT-COMPENSATION-NATIVE-REVIEW.json`, SHA-256
`ebf14b2eccffc0b3a2f03858a84c72792d27d7dd4a177f0b02609921f6258144`.
That review checked all 112 intrinsic lines and all 112 actual entry
adapters. Physical helper jobs retain their original native transforms
and endpoints. Restoration of their canonical contents is not physical
identity of each helper job.

Both inverse prelude orders, repeated logger parameter addition, and a
noncommutative group composition pass. A full backward call is not its
inverse prelude, because it still applies the target shear.

The non-diagonal timing control moves the first complete source scatter
before the second snapshot. It keeps the same event multiset, scalar
cost, and legal frame accesses. Independent propagation gives exactly

    DeltaY=Z_1 R_0 Y,       DeltaX=-J Z_1 R_0 Y.

The joint error has rank one and is nonzero. Missing target preparation,
a missing input child, an inverse native sign, and a global phase change
are also rejected.

## Local cost and limits

| Word | Complete scalar allowance | Private fields used |
| --- | ---: | ---: |
| Query logger | 218794 | 1 |
| Inverse source code | 218794 | 1 |
| Non-diagonal source code | 222846 | 8 |
| Inverse non-diagonal source code | 225794 | 8 |

All four words have child profile
`{1:2420, 2:418, 3:432, 4:142, 5:82}`, with mass 5530. Each adds eight
rank-one children and 16 explicit address maps to the retained word.
The literal scalar counts agree with the matrix cost formula, including
all private clears. No extra array field is used.

The review checked all ten pinned Git source files in `SOURCES.json`
and the copied notice hashes. Live GitHub link and Markdown rendering
checks are publication tasks; they were not part of this numerical
review. The external checker and its workspace inputs are not included
as a portable reproduction claim.

The accepted result is a local original-complex source-code family.
This review does not establish output query access, restoration across
different routed charts, a complete address or precision allowance,
recursive hosting, a complete supplier invoice, or a new kappa bound.
