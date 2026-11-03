# Read-only documentation review

Reviewed README.md, EXTERNAL-REVIEW.md, PRICING-SOURCE-MAP.md, ENDPOINT-REVIEW.md and pricing_binding.py against the supplied external audit text. No scientific verifier or artifact-regenerating command was run. The extended checker hash in ENDPOINT-REVIEW.md matches the current file (`3b15f6c17d2e7a941c97a29cd4269388cd07f824a4d8df16fc22a62c1515fcf8`). Publication receipts are intentionally outside this interim check.

## Findings to resolve

1. **Minor factual source-map correction — PRICING-SOURCE-MAP.md, paragraph beginning “The candidate's verify.py”.** It says `native_word`, `local`, `native`, and `L` all pass to both the predecessor invocation and the new price calculation. Exact candidate code passes `(native_word, old_caller, local, native, L)` to `source_candidate.run` at line 88, but only `(local, native, word, physical, L)` to `price.run` at line 136. The native word instead goes to `physical(..., native_word, L)` at line 131. Suggested replacement: “The candidate's `verify.py` `Extension.run` passes the same `local`, `native` and `L` objects to the predecessor invocation at line 88 and the new price calculation at line 136; the same `native_word` is supplied to the physical-map check at line 131.” This does not alter the cancellation conclusion.

2. **Attribution clarity — README.md, Pins and independence final paragraph.** The sentence “The reviewer made the conceptual suffix argument's implicit invertibility premise explicit…” follows the Claude paragraph, so a reader can attribute that original internal-review finding to Claude. Earlier internal review supplied it. Change “The reviewer” to “The internal skeptical reviewer” (or name that role explicitly). Claude's six documented findings and later Codex implementations are otherwise cleanly distinguished.

## Checks with no issue found

- Claude Code / Claude Opus 5.5 is credited for the external audit and findings; GPT-6 Astra through Codex is credited for the lead/internal roles and follow-up implementation. No independent human or formal-kernel review is claimed.
- External results are explicitly **reported** at `13e880a734cc03f2a52c82a412a9a0e6ac2b1f0c`; unpublished scripts/logs are not represented as locally replayed evidence. The later full-fiber checker is correctly separated from that external snapshot.
- The external report's early contradictory progress wording (“caught” versus “accepts”, “passes” versus “past” the decay) is resolved using its final substantive findings: four suffix changes passed the old cut check, and the candidate ratio exceeds 31/32.
- The additional local full-endpoint coverage and four suffix rejection controls are identified separately from the old cut check; redundant guards are not falsely described as independently mutation-covered.
- Physical tariff validity remains inherited. The exact 232,960 ordinary allowance increment is presented as arithmetic under the pinned formula, not a proof of physical rates or supplier admission.
- Local-manifest integrity is distinguished from external Git-object provenance, with an explicit trusted-publication/checker boundary. The AST matching helper calls its fragments copied source contracts, not independently derived physical semantics.
- `research/20261103-open-obligation` is correctly the branch, and `research/pr6551-retirement-audit` the package directory. The external report's initial branch confusion was corrected and is not repeated.
- The old 20-file/53-file external snapshot and current 22 retained sources are distinguished. Historical receipts are labelled; this review intentionally does not flag pending final publication receipts.

No blocking scientific or scope-overstatement issue was found in these documents. Resolve the two small factual/attribution edits before publication, then let the lead's serial validation and final receipt process complete.

Lead resolution: both wording findings were corrected before the scientific follow-up commit. The source-map line now distinguishes the shared pricing arguments from native_word passed to the physical checker; README names the internal skeptical reviewer. No scientific code or receipt changed.
