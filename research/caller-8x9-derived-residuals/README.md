# Derive both residuals of the exact 17-stage caller

This independent accounting proof derives the fixed caller terms in
`P = 17 H_native + K` and `T = 17 T_native + K_T`.
It reads the literal caller operations and declared output owners from
[PR 7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113), at
`07a76c5e2738882c0cb322278e56f6cae3c9885d`.
It does not obtain either constant by subtraction from a published invoice.
The complete multiplication exponent does not change.

The live [handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19664352)
from [PR 7628](https://github.com/CrocSwap/integer-mult-bounds/pull/7628)
asks for this derivation. The later
[PR 7639](https://github.com/CrocSwap/integer-mult-bounds/pull/7639)
also treats both residuals as measured constants.
The new coverage is the derivation of these fixed caller terms. The native
word census only checks the sum against the exact source invoice.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), and the exact copied
source inventory in [VENDORED.json](VENDORED.json).

## Result

| Rank | Paid residual K | Declared-root residual K_T |
| --- | ---: | ---: |
| 1 | 384 | 0 |
| 8 | 656 | 0 |
| 9 | 32 | 416 |
| 16, 24, 32, 40, 48, 56 | 416 each | 0 |
| 17, 25, 33, 41, 49, 57, 65 | 0 | 416 each |
| 64 | 208 | 0 |
| 73, 137 | 0 | 208 each |

The caller has 3776 paid positions and 3744 distinct root targets. Its
rank surplus is 57728. With the copied native word, the complete source
invoice has 110638 paid positions and 22172 productive fields.
All 4783 caller events are inspected. Every native call has 400 distinct
main contacts; the 17 calls occur in order. Each call has 1084 public
helpers. The verifier imports only the Python standard library.

Nine semantic controls cover omitted query cost, signed-idle rank,
changed target rank, duplicate ports, missing output declarations, aliased
native owners, stage order, repeated idle axes, and a wrong idle sign.
The controls change parsed objects after source authentication. Thus a
hash mismatch cannot substitute for a semantic failure.

## Scope and limits

The result is conditional on the declared native and caller operation
interfaces. It proves the accounting identity for this exact caller.
It does not replay the 72 formal output identities, native operators,
owned erasure lifetimes, physical contacts, ordinary cost, precision,
compiler, BIT branch, or outer reduction. The scalar operation counts in
RESULT.json are inventory counts, not a new ordinary-work estimate.

The root target ranks use the declared diagonal records. A signed query
axis has the same rank as its positive orientation after the specified
linear phase correction. This does not establish the caller endpoint.
A successor can use the residuals only after it proves that the exact
caller and its native contact interface remain the same.

The five inherited assumptions remain: `native_all_columns`,
`owned_erasure`, `compiler`, `precision_tape`, and `analytic_recovery`.
No selected frontier file is changed. The base is
`e54523517d0f03e58352e647c403a5af3e525a57`.
Its selected conditional kappa is `363005817/100000000000`.
The revision-8 catalogue describes an older selected result.

## Reproduce

Use Python 3.12. No third-party packages are needed.

```sh
python3.12 -B scripts/research_package.py --package research/caller-8x9-derived-residuals
```

Both registered commands must print `PASS_CALLER_DERIVED_RESIDUALS`.
The runner must print `PASS_REGISTERED_RESEARCH_PACKAGE`.
The commands use normal and optimized isolated Python processes.
The verifier reads no Git state and writes no files.

## Open next questions

Before a successor uses these constants, compare its caller bytes, port
partition, native contact interface, stage blocks and target owners.
A separate symbolic replay can check all 72 declared output identities.
[TASK.json](TASK.json) states the first step and limits for each question.

## Credit

Rohan Arun supplied the 8+9 caller and its source package, with OpenAI
Codex assistance. The caller README credits DreamingOfClouds for the native
and chain lineage, CubeJerry for the shared native, paired BIT and compiler,
ToikY for the signed rank-nine caller, and dillona and Ali Romman for helper
splitting. The exact retained NOTICE and INDEPENDENT-NOTICE.md preserve the
other source credits. fluorine supplied the independent recounts and the
specific residual-derivation handoff. Those recounts are related evidence;
this verifier does not import their code.

Ali Romman directed this independent accounting proof and verifier, with
substantial OpenAI Codex assistance. New work is Apache-2.0. The copied
source license and notices remain in source/.
