# Sources and attribution

Ali Romman prepared this range proof, exact basis audit, scalar witnesses
and package with substantial OpenAI Codex assistance. Apache-2.0 applies.
The l1 formula for a linear form on a cube is elementary; it is not
claimed as a new general norm theorem.

Clear1nsight supplied the role-1256 graph and physical analysis in
[PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704),
head `e29a5ae8591243c1178067727f12ce4abefa0b93`.
The exact [graph](https://github.com/Clear1nsight/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/data/CANDIDATE-GRAPH.json.gz)
is copied without change. Its compressed SHA-256 is
`0177c25371181e3b1f2c13325eb8434fbf6384a9ab99a612849efd5d0f6ab2cc`;
its decompressed SHA-256 is in PROOF.md and in the checker.
The original [physical code](https://github.com/Clear1nsight/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/physical.py)
and [receipt](https://github.com/Clear1nsight/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/evidence/PHYSICAL.json)
give the separate-product triangle bound and the source's physical scope.
They were read, but are not imported by this checker. This package does
not rerun or certify the complete physical application.

The [source notice](https://github.com/Clear1nsight/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/NOTICE)
identifies SYLforge's nine-swap word in
[PR #7700](https://github.com/CrocSwap/integer-mult-bounds/pull/7700)
as the word source. It also credits DreamingOfClouds, Ali Romman, Rohan
Arun, Jerry Chen (CubeJerry), Douglas Colkitt and the retained caller,
native, bank and selected-framework contributors. The source's notice,
all eight files in its credits directory, and license are preserved here.
Their historical selected checkpoints remain historical.

Ali Romman's
[PR #7702](https://github.com/CrocSwap/integer-mult-bounds/pull/7702)
gives [row-atomic arithmetic](https://github.com/aliromman/integer-mult-bounds/blob/785860501b03893eaa9f5279f978287e75d3f3af/research/chart595-row-atomic-arithmetic/PROOF.md)
on a different chart-595 graph. It is related work, not a consumed
range bound. It allows independently bounded donors. This package keeps
the role-1256 graph's entrance dependencies and its separate divisions.
Its W therefore has a different meaning. No code from that package is
copied here.

Douglas Colkitt and the repository contributors supplied the package
workflow and main-branch provenance machinery. SOURCES.json binds the
selected record and task catalogue at the base commit. The unmerged
graph is bound by its explicit source commit and byte hashes above;
it is not represented as an ancestor of main.
