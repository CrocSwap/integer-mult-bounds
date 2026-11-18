# Credit and exact source custody

Ali Romman prepared this audit with substantial OpenAI Codex assistance
in research, implementation, verification and writing. New work is
Apache-2.0. The source proof and code were read. This is author checking,
not blind, independent human or formal-kernel acceptance.

Ali Romman's separate workstream supplied the 46 certificates, recoding
methods and complete application in
[PR #7708](https://github.com/CrocSwap/integer-mult-bounds/pull/7708).
The consumed scientific commit is
`f0e2db5b5b46b139da17d2b32fab6633164443a9`; its published head is
`7017edbe4bc5ed1b6d5b6defedbc7e472d83c65c`.
Read its [proof](https://github.com/aliromman/integer-mult-bounds/blob/f0e2db5b5b46b139da17d2b32fab6633164443a9/research/p104-relay-cut-recoding/PROOF.md),
[constructor](https://github.com/aliromman/integer-mult-bounds/blob/f0e2db5b5b46b139da17d2b32fab6633164443a9/research/p104-relay-cut-recoding/recoding.py),
[cut certificate](https://github.com/aliromman/integer-mult-bounds/blob/f0e2db5b5b46b139da17d2b32fab6633164443a9/research/p104-relay-cut-recoding/CUTS.json)
and [notice](https://github.com/aliromman/integer-mult-bounds/blob/f0e2db5b5b46b139da17d2b32fab6633164443a9/research/p104-relay-cut-recoding/NOTICE).
The retained constructor is reused unchanged. The new checker compares
all intermediate bank values with separate exact basis expansions.
The feedback and pivot methods are source work, not new discoveries.

Clear1nsight supplied the role-1256 relay and banked realization in
[PR #7704](https://github.com/CrocSwap/integer-mult-bounds/pull/7704),
commit `e29a5ae8591243c1178067727f12ce4abefa0b93`.
Its [constructor](https://github.com/aliromman/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/construct.py)
and [notice](https://github.com/aliromman/integer-mult-bounds/blob/e29a5ae8591243c1178067727f12ce4abefa0b93/research/cf6a-banked-role1256-relay/NOTICE)
identify the reused parent and attribution. The raw fold, source CLEAR
certificates and relay proof remain inherited dependencies.

The exact basis evaluator is copied unchanged from Ali Romman's
[PR #7715](https://github.com/CrocSwap/integer-mult-bounds/pull/7715),
commit `4517ad2a3e9f06ca369a2625f652de4f57be2fb9`.
Its [checker](https://github.com/aliromman/integer-mult-bounds/blob/4517ad2a3e9f06ca369a2625f652de4f57be2fb9/research/helper-quotient-basis-audit/verify.py)
supplies the integer-vector arithmetic, separate graph order and rank
checks. That audit treated the completed PR7708 graph as its parent;
it did not check the 46 recodings reviewed here.

DreamingOfClouds supplied the related grouped-hub method in
[PR #7705](https://github.com/CrocSwap/integer-mult-bounds/pull/7705)
with Claude Opus 5.5 assistance. The separate
[PR #7712](https://github.com/CrocSwap/integer-mult-bounds/pull/7712)
reports another reconstruction of the PR7708 parent. It is related
corroboration, not an imported checker in this package.

The retained notices credit SYLforge for the nine-swap word and caller
in [PR #7700](https://github.com/CrocSwap/integer-mult-bounds/pull/7700),
Rohan Arun for the signed caller lineage, Jerry Chen / CubeJerry for
the selected complex and BIT applications, Douglas Colkitt and the
recorded contributors for the framework, and mightyOil for the concave
invoice comparison. The signed caller engine is reused unchanged.
The tail-sum calculation here supplies an explicit comparison for the
fixed count delta; it does not claim priority for concavity methods.

[SOURCE-PINS.json](SOURCE-PINS.json) gives the original Git blob and
SHA-256 for each retained file. All notices remain under credits/.
The package has no external replay input. Base provenance is in
[SOURCES.json](SOURCES.json). No retained source byte is changed, and
no source commit is falsely declared to be an ancestor of this branch.
