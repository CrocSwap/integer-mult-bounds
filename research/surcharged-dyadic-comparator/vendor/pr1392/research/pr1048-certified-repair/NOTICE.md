# Attribution and license

New work: Brian Ross, with substantial OpenAI Codex assistance, including
separate GPT-6 Astra agents at xhigh for bounded coverage and independent
review/rerun. New code and documentation follow this repository's Apache-2.0
license. Separate-agent review is not independent human peer review.

Original search, profile replay and rational interval routines are flemhhh's
PR1048 at `07730cd8302c378607259a9ad0efb73e0b57a2f2`. The entire research
package is retained byte-for-byte in `research/bit-profile-pair-audit/`, with
its original LICENSE, NOTICE and substantial DeepSeek assistance disclosure.
Its historical exactness and completeness claims are disputed evidence, not
claims endorsed by this wrapper.

Endpoint-certified three-way bisection and default-precision false-bracket
examples are woklerx's PR1182 at `0213b8911bfeefd5c81ddf320bac6a0fb7e86215`.
Its package is retained byte-for-byte in `research/profile-bracket-audit64/`,
including original vendor license, notices, provenance and AI disclosure.
The pricing adapter imports that repair rather than claiming a new bisection.

The arbitrary-fixed-exponent counterexample is Douglas Colkitt's existing
maintainer audit, with OpenAI Codex assistance, in
`research/community-batch1099-audit/check_pr1048_counterexample.py`. Its
reproduction here is not a new discovery. The corrected reference-root
comparison also responds to the maintainer's explicit deferred-1048 request.

The word, source geometry and supplier remain credited to eumemic's PR555/543,
DreamingOfClouds's PR545/589, the PR510 pricing chain and all retained notices.
No source ownership, supplier construction or multiplication-bound credit is
transferred by this audit.

Methodological adaptation, **no copied code**:

- Brian Ross's [Krenn independent verifier](https://github.com/brianross93/Krenn/blob/ab446724a61a293a3268c63b9e9e721c6a360561/experiments/krenn_quantum_graph/independent_verifier.py)
  and [semantic corruption controls](https://github.com/brianross93/Krenn/blob/ab446724a61a293a3268c63b9e9e721c6a360561/tests/test_krenn_artifacts.py): reconstruct semantics independently; reject corrupted claims even when container hashes are refreshed; require complete input inventories.
- Brian Ross's [ThetaTwist exact arithmetic](https://github.com/brianross93/thetatwist/blob/b4ec6c13088b89961834cc675b44b81372199b02/src/thetatwist/core.py): exact rational identities, explicit residuals and bounded claim scope. ThetaTwist is MIT licensed, copyright Brian Ross 2026. Its source is read as a methodological reference and is not vendored or copied.

A root `LICENSE` could not be retrieved for the pinned Krenn tree (404); no
Krenn implementation is redistributed or adapted at the code level. Its
independent-reconstruction and semantic-control methods are credited above.
