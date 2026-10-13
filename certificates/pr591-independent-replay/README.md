# Independent replay of PR591

**Conditional κ = 0.001609915765452068** (conservative value `0.001609915762605935`). This is an independent clean replay of [CrocSwap/integer-mult-bounds#591](https://github.com/CrocSwap/integer-mult-bounds/pull/591), head `e53c9973ab5b075bc0b2f748fcd2c267342eeb74`.

The replay rebuilt the baseline and all three final provider words from the PR's pinned source packages. It completed 49 top-level stages plus the nine nested baseline stages in 272.5001600839896 seconds. All stage logs and 48 output artifacts match the generated receipt hashes. The result is `PASS_HPEQ1_NATIVE_COMPLEX_AND_CITED_BIT`.

The replay checked actual scalar words, arbitrary dirty restoration, both reflected ledgers, phase edges and wrappers, owner/profile data, a fresh invoice, exact assembly, two exact moment engines, 47 outer constraints, 147 assembly controls, and timing controls. The resulting profile is `{1:181612,2:35160,3:23384,4:14024,5:4032,6:4032,8:576,12:1,48:1949}` with provider dispatch `ck=66`, `jp8=1`, `atm3=5`.

The construction ends selected width-8 helpers on certified hyperplanes, changing their residual width to 7 and pairing them with width-9 owner slots. It is a complex-side paid-profile improvement over PR588; the rank deficit is unchanged.

The replay used only the standard-library verifier in PR591, with immutable source pins for PR568, PR569, PR571, PR575 and PR583. The PR591 package retains its original provenance and AI disclosure: Claude Opus 5.5 (Anthropic) performed the submitted PR work, while this replay was performed with OpenAI Codex assistance.

This remains conditional on the inherited all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape/exact recovery, and analytic transfer. It is not an unconditional theorem or full Lean certification.
