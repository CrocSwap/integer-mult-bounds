# Credit and source custody

Ali Romman prepared this application with substantial OpenAI Codex
assistance in research, implementation, verification and writing.
New work is Apache-2.0. This is author checking with source engines.
It is not blind, independent human or formal-kernel review.

The fixed normalized composition is prior work in
[PR #7716](https://github.com/CrocSwap/integer-mult-bounds/pull/7716),
head `1636b3c9b922d23b222b60dd52e005e60c592491`.
Its [construction proof](https://github.com/aliromman/integer-mult-bounds/blob/1636b3c9b922d23b222b60dd52e005e60c592491/research/quotient-causal-split-composition/PROOF.md)
and [constructor](https://github.com/aliromman/integer-mult-bounds/blob/1636b3c9b922d23b222b60dd52e005e60c592491/research/quotient-causal-split-composition/verify.py)
supply the graph. Its source credit is retained in credits/PR7716-CREDITS.md.

Ali Romman's [PR #7713](https://github.com/CrocSwap/integer-mult-bounds/pull/7713),
scientific commit `06b75fde21f4231a2bd0725542c3ba60a908d83b`, supplies the
[application](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/application.py),
[catalogue check](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/catalogue.py)
and unchanged vendor files. The new wrappers adapt those checks to the
1470-field graph, its two fresh helper owners, new grid and complete bill.
The [source notice](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/NOTICE)
identifies the authors and retained lineage.

Clear1nsight supplied the banked execution and relay in
[PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704),
commit `e29a5ae8591243c1178067727f12ce4abefa0b93`.
The [physical argument](https://github.com/CrocSwap/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/PHYSICAL.md)
and [physical engine](https://github.com/CrocSwap/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/physical.py)
are material dependencies. The engine is copied unchanged through PR #7713.
The original hard-coded 1501-field reader is not called. common.py checks
the actual 1470-field namespace before it calls the generic engine functions.
No frozen source check is patched or disabled.

DreamingOfClouds supplied the literal split witnesses in
[PR #7712](https://github.com/CrocSwap/integer-mult-bounds/pull/7712),
head `5001d95a5c1decfb2b0d64d13c130300797e722a`, with Claude Opus 5.5 assistance.
Clear1nsight supplied the causal split method. SYLforge supplied the word
and caller in [PR #7700](https://github.com/CrocSwap/integer-mult-bounds/pull/7700).
Rohan Arun supplied the caller lineage. Jerry Chen / CubeJerry supplied the
selected complex and BIT application. Douglas Colkitt and the credited
contributors supplied the framework, compiler and exact comparison tools.
Retain mightyOil's concave comparison credit.

The base [shared-wire notice](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/shared-wire-split-composition/NOTICE)
credits DreamingOfClouds, Ali Romman and Jerry Chen / CubeJerry for the
retained operator engines and their extensions. It also credits unpaidmoon
for the phase convention and icekylinx for the odd-grid precedent.
All copied notices retain their source bytes. SOURCE-PINS.json gives their
Git blobs and SHA-256 values. SOURCES.json pins the four base inputs and
the selected record; it does not claim that pending dependencies are ancestors.
