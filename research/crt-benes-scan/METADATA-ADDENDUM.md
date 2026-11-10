# README seal addendum

James Reed identified a README digest mismatch in the uniform Beneš arena-scan package at PR #4192 head `519d811cc48693ad9969d6d7994bef3940167005`. The README entries in `COLD-REPLAY.json` (`reviewed_hashes`) and `COST-REVIEW.json` (`primary_files_reviewed`) both record the earlier bytes. [Review finding](https://github.com/CrocSwap/integer-mult-bounds/pull/4192#issuecomment-6295405201)

| README version | Bytes | SHA-256 |
| --- | ---: | --- |
| Earlier version bound by both seals | 4,244 | `a27718895b2638555b9be078e5c265863d4d8075fd29506af3473b5deaa503cb` |
| Published at the reviewed PR head | 4,978 | `cc8548c969b0d1752f52f47e0348ac93c8d53932912fdf85127b42beba781ce2` |

Removing lines 57–68 from the published README, retaining all other bytes and line endings, reproduces the earlier digest exactly. The inserted block documents the six registered commands, the FIFO oracle and its initial review, the source-pinned cross-check, and the separate cost review. The published README has Git blob `33b8678615068e976299eab574e5b411d8de1ab9` in both the initial package commit `33676ef7ca7d3c2989a1a673b2d8961dc95fef1f` and the reviewed head. [Exact README lines](https://github.com/ToikY/integer-mult-bounds/blob/519d811cc48693ad9969d6d7994bef3940167005/research/crt-benes-scan/README.md#L57-L68)

Hashing the GitHub file bytes confirmed the four other package seals in each receipt, the cost review document and replay helper seals, both cost review source seals at base `12fa8c5c844be21bfefb38a19503fbd867a11244`, and all three `CROSS-CHECK.json` file seals. The original receipts remain the record of the earlier review and replay. This addendum records a documentation change verified by byte comparison. [Later SOURCES-scope audit](https://github.com/CrocSwap/integer-mult-bounds/pull/4192#issuecomment-6301455631)
