# Fixed-output validation of #7244

This archive records the cross-check of [#7244](https://github.com/CrocSwap/integer-mult-bounds/pull/7244) at `215f67247f395c0e15f5ea3980f6a3e4aed155af` against the #7161 scientific commit `e3f8d39c43b07063dfc5b800f71c5d21015259e6`. Both use the signed #7113 caller at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. The checker and receipt are byte-identical to the [original evidence export](https://github.com/Clear1nsight/integer-mult-bounds/tree/db81f377beac072c16d7fa2c6e2bc5f9b5781c7b/research/p104-two-cut-fixed-output-crosscheck).

The [receipt](RECEIPT.json) records exact scalar endpoints and a dirty COPY control, the [#7245](https://github.com/CrocSwap/integer-mult-bounds/pull/7245) census on both words, the complete 17-stage rank counts and directed rational price intervals. Both words have full row rank in all 2,229 quotient classes and all 978 target classes, with zero contact-free MOVE pairs. The verified conditional κ of 0.003645372367832 uses the changed productive fields and charges both new exits at every stage. [#7246](https://github.com/CrocSwap/integer-mult-bounds/pull/7246) addresses a complementary decoder that crosses target classes.

## Reproduction

Fetch the exact public source commits into the checkout. Use CPython 3.12 with assertions. The checker uses the pinned main-branch Clifford classifier and implements its own exact scalar replay, elimination modulo 65,521, invoice count and directed price arithmetic. The committed JSON records the SHA-256 digests of the input words, caller and classifier. The archive uses a manual replay because the exact candidate and caller come from public PR commits.

```sh
git fetch --no-tags https://github.com/CrocSwap/integer-mult-bounds.git \
  e3f8d39c43b07063dfc5b800f71c5d21015259e6 \
  07a76c5e2738882c0cb322278e56f6cae3c9885d \
  215f67247f395c0e15f5ea3980f6a3e4aed155af
GIT_NO_REPLACE_OBJECTS=1 python3.12 -I -B \
  research/p104-two-cut-fixed-output-crosscheck/check.py . > /tmp/p104-7244-cross-check.json
cmp /tmp/p104-7244-cross-check.json research/p104-two-cut-fixed-output-crosscheck/RECEIPT.json
```

## Open next questions

Use this replay alongside the registered #7244 replay to review the conditional frontier proposal. Maintainer selection and independent human or formal review of the [five retained assumptions](https://github.com/Clear1nsight/integer-mult-bounds/blob/215f67247f395c0e15f5ea3980f6a3e4aed155af/research/p104-two-cut-funded-split/PROPOSED-CLAIM.json) remain open. The [frontier review discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19542237) records the handoff.

Credit ToikY for #7245 and #7246, Clear1nsight and the retained #7161/#7244 lineages, Rohan Arun for #7113, and the canonical Clifford authors. Prepared for Clear1nsight with substantial OpenAI Codex assistance. Apache-2.0.
