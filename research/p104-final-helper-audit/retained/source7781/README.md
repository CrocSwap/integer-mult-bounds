# Paid subdivisions on both suppliers

**Conditional κ ≥ 0.00386969949992** for a complete multiplication using 36 ordinary binary calls and the closed 48-call P104 complex supplier. The directed gain over the largest submitted predecessor’s joint raw upper endpoint is **0.00001073765744**. The construction starts from Ali Romman’s exact #7776 binary and complex words. [PR #7776](https://github.com/CrocSwap/integer-mult-bounds/pull/7776)

| Compared construction | Directed endpoint | Excess of the candidate’s finite lower |
| --- | ---: | ---: |
| Submitted dual supplier #7776, joint raw upper | 0.00385896184248 | 0.00001073765744 |
| #7776 complex word given the new binary service, complex raw upper | 0.00385932267588 | 0.00001037682404 |
| Fixed round target | 0.00386380485468 | 0.00000589464524 |

The original selected result was κ ≥ 0.00363005817 from #7000 when this package was prepared. The predecessor's finite lower is 0.00385896148992. Its unchanged binary word crosses below 0.00385896184248, and its unchanged complex word crosses below 0.00385932267588. Giving that complex word the new ordinary service yields the separate finite checkpoint 0.00385932267579. These comparisons use the same signed rank tariff, caller conventions and five outer assumptions. [First joint checkpoint](evidence/unchanged-complex-application.json) · [Selected result](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

## Construction and cost

An existing paid transfer can sometimes be subdivided at an intermediate chart. For each accepted subdivision the construction gives a local readout that retires an original arbitrary input, a calibrated independent input at the new chart, and an impulse that reaches the intended output. The verifier checks the later consumers and the full operator in both directions. It charges the two new paid legs and credits both productive legs in place of their original entries. The numerical saving comes from their different rank distributions under `H(r) = r^(1−κ)`. [Binary derivation](binary/PROOF.md) · [Rational derivation](complex/PROOF.md)

The binary word uses 21 subdivisions, checks all 672 independent public fields in both directions, and retains 36 caller invocations. The ordinary compiler admits **0.00386969950**. The rational carrier has 14 productive subdivisions on the #7776 word. The final fixed-boundary changes relocate four local scalar banks and replace two paid transfers of ranks 1 and 3 with one rank-4 return. A further same-chart split on owner 1164 creates an independent productive return without another paid transfer. The proof records each of these changes against its immediate parent.

| Complete bill | Binary | Complex |
| --- | ---: | ---: |
| Native calls | 36 | 48 |
| Paid positions | 107,532 | 283,488 |
| Productive positions | 20,418 | 52,032 |
| Ordinary record allowance used | 933,004,517,520 | 151,885,612,032 |
| Raw crossing | 0.003870038707744–0.003870038707745 | 0.00386981257852–0.00386981257853 |

The binary construction requires 6,998,328 owned fields. The complex accounting includes 1,288,991,232 scalar services and 142,464 odd conversions. The test covers 1,279 rational public outputs and their adjoints, overwritten sender fields, source-home cleanup, physical adapters, both finite compilers and a common root-envelope depth guard. [Complete signed and ordinary invoices](evidence/application.json) · [Binary finite certificate](binary/FINITE.json) · [Independent rational operator](complex/INDEPENDENT.json)

## Reproduce

The source lock binds the public #7776 scientific tree at `4f7c67ae387cc91580f469aeda4d508b372b9ec1` and the #7774 product-grid and directed-root routines at `22fff773f897e70a2c346d09de62515fadb1c445`. All checks use standard-library Python 3.12. From this directory, use fresh source and output directories for these commands.

```sh
python3 -IB prepare_sources.py /tmp/p104-birth-sources --fetch
for part in binary construction operator application charts-0 charts-1 charts-2; do
  python3 -IB verify.py --cache /tmp/p104-birth-sources --out "/tmp/p104-birth-$part" --part "$part" || exit 1
done
```

The pure rational birth journal records every replaced owner, paid sender, local coefficient and necessary return. The final coefficient journal checks each changed literal against its parent and validates the resulting topological order. The binary and complex operator checks mutate a paid read or return and exercise a dirty CLEAR. The physical catalogue checks the signed phases, including the relative maps between charts. [Source pins](SOURCE-LOCK.json) · [Frozen identities](CLAIM.json) · [Rational birth journal](complex/BIRTHS.json) · [Bank and sparse projection derivation](complex/REFINEMENTS.md) · [Final unpaid split](complex/FINAL-BIRTH.json)

## Open next questions

The conditional application retains native all-column correctness, owned erasure, the compiler model, precision-tape simulation and analytic recovery. The finite programs establish the listed instances inside that framework. Maintainers determine frontier admission. An independent next check is to pick the first rational birth in the journal, remove its paid return, and compare the affected arbitrary input and adjoint coefficient with the signed bill. A compiler or theorem review can then examine the shared outer and finite parameter inequalities. [Selected framework](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

Ali Romman supplied the dual construction and its eight binary punctures. Jerry Chen (CubeJerry), DreamingOfClouds, zxv, SYLforge, Rohan Arun, Cinna Davis, Douglas Colkitt, Clear1nsight and the cited predecessors supplied the selected application, callers, physical engines and compiler checks. Clear1nsight prepared this contribution with substantial OpenAI Codex assistance for construction, programming and independent computational review. [PR #7776](https://github.com/CrocSwap/integer-mult-bounds/pull/7776) · [PR #7774](https://github.com/CrocSwap/integer-mult-bounds/pull/7774) · [Notice](NOTICE)
