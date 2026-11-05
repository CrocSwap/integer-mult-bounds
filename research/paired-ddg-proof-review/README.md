# External all-depth audit of the paired decision graph

This is a source-bound written proof-to-code audit of zxv's [PR6072](https://github.com/CrocSwap/integer-mult-bounds/pull/6072), original head `9011bf83e85ecd0443c789cf03259442f750877d`. Its proof README and literal `make/census/run` code have identical blobs at current canonical main `7c49fe32`. The original author supplies the sampler, product law, optimal expected draw count and finite catalogue. This package adds external written review evidence and a structural explanation of the existing resource ledger; it does not introduce a sampler or a new count.

The contract is two fixed probabilities `a/13,b/13`, with `a,b` in `1..12`, known before drawing any bits, and an independent unbiased incoming bitstream. No free initial random state or entropy reservoir is supplied. The decisions have the exact four-outcome product law. Adaptive second probabilities, correlated incoming bits, physical table/tape access and cleanup need their own contracts.

## Evidence and reproduction

Read [REVIEW.md](REVIEW.md), the separately authored [review notes](reviews/), the inert [source proof](inputs/README.md) and [literal controller](inputs/verify.py). [SOURCE-PINS.json](SOURCE-PINS.json) records all three exact source objects, including the license. [SOURCES.json](SOURCES.json) binds eight guidance and three scientific-source provenance objects through canonical main. The original proof/code blobs are `615c4890ec797561fd4287445ceb1019905175bc` and `eda448fbda7b6a78f340086fcaac6e7556bf1383`.

No scientific source was imported or executed. There is deliberately no scientific VERIFY hook. Original 144-table checks, literal tapes and the displayed large exact mean are source evidence, not newly executed results. [VALIDATION.md](VALIDATION.md) separates written derivation, code association, metadata/byte/export checks and any original hosted helper outcome. A helper pass or agreement between AI drafts is not mathematical or kernel acceptance.

[TASK.json](TASK.json) records the explicitly changed formal-interface card and unmet original kernel gate. Both written roles are source-aware and seal their first drafts before cross-review; no blind, human or proof-kernel independence is claimed.

## Open next questions

- Can this exact all-depth invariant and code binding be formalized? It would add a different kind of evidence. Begin with the phase/node invariant, periodic root return and depthwise stopping bound. No kernel environment or development is supplied here.
- Can a complete physical caller exploit the expected-bit reduction? Start from the actual `/52` ABI and completed numerical caller, then price the complete table selection/access, random tape movement, owned stopping/cleanup and full caller bill. Those physical contracts remain outside this review. An abstract draw saving is not a paid runtime saving.

## Credit and limits

zxv/PR6072 supplies the graph, existing 312-state/624-transition/702-byte ledger and catalogue/means, with substantial disclosed Codex assistance. Dyadic distribution-generation trees and depth-count optimality are classical. JoyboyBrian's PR5037/5069 inverse lineage, PR6096 actual `/52` classification and PR6102 reversible fixed-pair protocol retain their credit. Nick Petalas supplies PR6026 stochastic-prefix context and PR6124/6127 bank-sharing/counterless refinements. PR6546 already supplies a complete same-grid numerical caller; PR6547 supplies its distinct recovery-capacity result. This review does not call those joins missing or claim their coverage as its own.

Prepared for ToikY with substantial source-aware OpenAI Codex assistance, separate written derivation/code roles and coordinator reconciliation. Source headers, [NOTICE.md](NOTICE.md) and the exact [Apache-2.0 license](inputs/LICENSE) are retained. All selected native, ownership/erasure, compiler, precision/tape, analytic/outer obligations remain. No physical supplier, multiplication theorem, κ/frontier/adoption change or merge is established.
