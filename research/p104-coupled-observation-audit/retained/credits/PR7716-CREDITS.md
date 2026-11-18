# Attribution and exact source pins

Ali Romman prepared the fixed-graph composition, its constructive
checker and scoped evidence with substantial OpenAI Codex assistance.
New work is Apache-2.0. Source proofs and code were read; this is
author checking, not blind, human or formal-kernel review.

DreamingOfClouds supplied the two literal readouts and injections in
[PR #7712](https://github.com/CrocSwap/integer-mult-bounds/pull/7712),
head `5001d95a5c1decfb2b0d64d13c130300797e722a`.
The [causal split proof](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/5001d95a5c1decfb2b0d64d13c130300797e722a/research/p104-banked-cf6a-splits/PROOF.md),
[literal circuit](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/5001d95a5c1decfb2b0d64d13c130300797e722a/research/p104-banked-cf6a-splits/data/CIRCUIT.json.gz)
and [source notice](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/5001d95a5c1decfb2b0d64d13c130300797e722a/research/p104-banked-cf6a-splits/NOTICE)
identify the original construction and Claude Opus 5.5 assistance.
That source's charts, witnesses and split identity are prior work.
The new result transports the two surviving witnesses to the changed
quotient graph and verifies their joint compatibility. The third
source split is excluded; its known collision is not claimed as new.

Ali Romman's separate workstream supplied all 33 restrictions in
[PR #7713](https://github.com/CrocSwap/integer-mult-bounds/pull/7713),
scientific commit `06b75fde21f4231a2bd0725542c3ba60a908d83b`, published
head `52e7eb424b9ae9f2e6002eb17e475bce6195d848`.
Its [constructor](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/quotient.py)
exports the frozen compact input. Its
[application receipt](https://github.com/aliromman/integer-mult-bounds/blob/06b75fde21f4231a2bd0725542c3ba60a908d83b/research/p104-helper-quotients/results/application.json)
supplies the unchanged fixed caller and root rows.
The [compatibility handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19711980)
asks for a separate construction before the source gains can combine.

Ali Romman's [PR #7715](https://github.com/CrocSwap/integer-mult-bounds/pull/7715),
head `4517ad2a3e9f06ca369a2625f652de4f57be2fb9`, supplies the
[exact basis engine](https://github.com/aliromman/integer-mult-bounds/blob/4517ad2a3e9f06ca369a2625f652de4f57be2fb9/research/helper-quotient-basis-audit/verify.py),
copied unchanged as basis_engine.py. That package checked the compact
endpoint and complete restriction debits. Its result is not repeated
as a new contribution here. The earlier unsplit positive-control graph
is from [PR #7708](https://github.com/CrocSwap/integer-mult-bounds/pull/7708),
scientific commit `f0e2db5b5b46b139da17d2b32fab6633164443a9`.

The retained notices credit Clear1nsight for the causal split method
in [PR #7697](https://github.com/CrocSwap/integer-mult-bounds/pull/7697),
role-1256 relay in [PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704),
and role-230 reroute; SYLforge for the word and signed caller in
[PR #7700](https://github.com/CrocSwap/integer-mult-bounds/pull/7700);
Ali Romman for the banked circuit and recodings; Rohan Arun, Jerry
Chen / CubeJerry, Douglas Colkitt and repository contributors for
predecessor constructions and the selected framework; and mightyOil
for concave comparison. The source notices under credits/splits and
credits/quotients, and the PR #7715 credit, retain their exact bytes.

[SOURCE-PINS.json](SOURCE-PINS.json) records all retained bytes and
original Git blobs where applicable. The parent and compact graphs
are explicit source-constructor exports. No source constructor or
source split checker is imported by the replay. Copies are committed
in this package, so no unmerged predecessor history is needed.
[SOURCES.json](SOURCES.json) pins the base catalogue and selected
record as provenance; it does not claim that pending source commits
are ancestors of this branch.
