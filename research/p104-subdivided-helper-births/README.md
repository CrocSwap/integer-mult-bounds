# Paid subdivisions on the leading P104 and ordinary BIT suppliers

Twenty-one paid binary subdivisions introduce independently returned helper fields in the exact residual word published by Ali Romman in PR #7776. The complete 36-call ordinary BIT saving is **0.00386969950**. Combining it with the original #7776 complex carrier gives a finite joint lower bound of **0.00385932267579** under the five retained assumptions. This checkpoint exceeds the predecessor's joint raw upper endpoint 0.00385896184248 by **0.00000036083331**. [Binary proof](binary/PROOF.md) · [Full application](evidence/unchanged-complex-application.json)

The signed binary bill contains 107,532 paid positions and 20,418 productive positions. Width and housekeeping account for 933,004,517,520 ordinary records and 6,998,328 backing fields. The signed raw crossing is [0.003870038707744, 0.003870038707745]. The compiler verifies the smaller ordinary saving over its full interval. [Native reconstruction](binary/replay.py) · [Finite certificate](binary/FINITE.json)

## Reproduction

This package uses standard-library Python 3.12. The source lock pins the mathematical code and inputs from PRs #7776 and #7774. The first command downloads only those files. Run these commands from the package directory.

```sh
python3 -IB prepare_sources.py /tmp/p104-subdivision-sources --fetch
python3 -IB binary/replay.py --source-root /tmp/p104-subdivision-sources/source --write-json /tmp/p104-binary.json
python3 -IB binary/finite.py --upstream /tmp/p104-subdivision-sources/source --supplier /tmp/p104-subdivision-sources/source --native-report /tmp/p104-binary.json --out /tmp/p104-finite.json
python3 -IB qualify_complex.py --upstream /tmp/p104-subdivision-sources/source --supplier /tmp/p104-subdivision-sources/source/research/p104-dual-supplier-lift --peer /tmp/p104-subdivision-sources/peer --binary-finite /tmp/p104-finite.json --out /tmp/p104-application.json
```

The original round target is 0.00386380485468. The remaining complex shortfall for this checkpoint is 0.00000448217889. The current selected result is maintained separately by CrocSwap. The finite construction inherits native all-column correctness, owned erasure, the compiler model, precision tape and analytic recovery. [Selected application review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)

Ali Romman supplied the dual construction, including its eight binary punctures and closed 48-call P104 application. Jerry Chen (CubeJerry) supplied the selected #7000/#7001 lineage. DreamingOfClouds supplied the paired caller and shared-native infrastructure, zxv and collaborators supplied the finite compiler and earlier binary word, and the #7774 contributors supplied calibrated paid restorations and exact product-grid checks. Clear1nsight prepared the new constructions and independent checks with substantial OpenAI Codex assistance. Maintainer review and human or proof-kernel acceptance remain open. [PR #7776](https://github.com/CrocSwap/integer-mult-bounds/pull/7776) · [PR #7774](https://github.com/CrocSwap/integer-mult-bounds/pull/7774)

