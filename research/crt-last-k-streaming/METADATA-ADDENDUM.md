# README seal addendum

James Reed identified a README digest mismatch in the CRT last-K streaming package at PR #4187 head `45fc0750436ae5cc14b95fba81c030a3d7df3412`. The README entry in `PRIMARY-REVIEW.json` (`reviewed_hashes`) records the earlier bytes. [Review finding](https://github.com/CrocSwap/integer-mult-bounds/pull/4187#issuecomment-6295357409)

| README version | Bytes | SHA-256 |
| --- | ---: | --- |
| Earlier version bound by the review seal | 6,129 | `7b120762e00fd1b2a820ada45ec86e5fd1194faf2e05cae9978995bc95e94ff4` |
| Published at the reviewed PR head | 6,574 | `e51db1a7aafab19383738bae9077572e5a7ae2efdcb4e87c1554386b2ff2b80a` |

Removing lines 80–86 from the published README, retaining all other bytes and line endings, reproduces the earlier digest exactly. The inserted block documents the six registered commands, the endpoint oracle, the one-bit payload control, and the review receipt. The published README has Git blob `026ead110b3b632c7d6d139113ca0b8f24ccf008` in the package’s single PR commit at the reviewed head. [Exact README lines](https://github.com/ToikY/integer-mult-bounds/blob/45fc0750436ae5cc14b95fba81c030a3d7df3412/research/crt-last-k-streaming/README.md#L80-L86)

Hashing the GitHub file bytes confirmed the four other `reviewed_hashes` entries, both `REPORT.json` file seals, and the verifier and script digests associated with the one-bit payload control. The original receipts remain the record of the earlier review and replay. This addendum records a documentation change verified by byte comparison. [Later SOURCES-scope audit](https://github.com/CrocSwap/integer-mult-bounds/pull/4187#issuecomment-6301436464)
