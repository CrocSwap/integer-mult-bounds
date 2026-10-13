# Attribution and assistance disclosure

Sagar Thakrar (@thakrarsagar), PR753 at
`2b30b63789f6d9948233fc67d9d79bca6b185c5b`, previously used restored helper
stars in historical R420 phase-A decoder totals, with substantial OpenAI
Codex assistance. It is an earlier mechanism precedent, found in the final
overlap refresh; its code and savings are not imported or composed here.
Ross Richardson (@RossRichardson) independently published PR965 at
`6292e3774abd82f2d5202190b498f35cc1628c39` during this work, before this PR.
His general GL(3,2) extensions of frozen PR926 pairs save 140 ADDs. This
different global star pass saves 197 but has less precision margin. PR965
discloses substantial OpenAI Codex assistance. No priority for three-helper
bases, imported PR965 code, or independent replay of its package is claimed.

New work is Apache-2.0, prepared for Sricharan Vagvala (@theon199) with
substantial OpenAI Codex assistance in research, mathematics, implementation,
verification and writing. One parent agent performed the work. Algorithmic
independence of the verifier does not imply independent human review.

This package changes the helper-basis class from disjoint pairs to disjoint
stars with at most two leaves. It makes no priority claim for basis changes,
conjugation, XOR synthesis, semantic D substitution, or the inherited E8 unit.

Gareth Davidson (@bitplane) supplied PR915's target-basis circuit at
`e9daefe320a0043000bd9746664ed02c3287d056` and PR926's disjoint helper-pair
construction (mathematical head `1e9c43ee8dbeeb9aca0e8fdecbf9769db4f4a29e`,
published head `0f216a345c37bc71cc0e22030ef11ec31b26a69e`). They disclose
substantial OpenAI Codex assistance. `common.py` and `native.py` are adapted
from the pinned in-tree PR926 files; the builder generalizes its pair scan
and exact positive guards. Literal-stream/source-check patterns follow that
package; the set-valued reconstruction and complete endpoint replay are
separately implemented here. Both complete predecessor circuits are
replayed, not merely accepted from their summary values.

The original notices, proofs and licenses remain verbatim in the repository
and are bound by SOURCES.json:

- `../r439-target-compensation/NOTICE.md`, `PROOF.md`, `LICENSE`.
- `../r439-two-sided-compensation/NOTICE.md`, `PROOF.md`, `LICENSE`.
- `../e8-bit-p111-tuned/NOTICE.md`, `LICENSE`.
- `../e8-bit-carrier-skeleton/NOTICE.md`, `LICENSE`.

The selected bit word is DreamingOfClouds' PR589
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`, tuning eumemic's PR555/543.
DreamingOfClouds disclosed Claude Opus 5.5 via Claude Code; eumemic's retained
notice discloses Anthropic Claude assistance. Dugongue's PR541/548 and
rohanarun's PR542 supplied transport precedents. This candidate changes only D.

Earlier mechanism credit remains with Scott Woolsey Biggart (@swbiggart),
PR733, for two-sided binary composition; Greer Guthrie, PR694, for simultaneous
helper-basis changes; Mikhail R. Gadelha, PR686, for semantic D substitution;
commdata2338, PR794, for guarded target-basis search; Scott Woolsey Biggart,
PR713, and Sagar Thakrar, PR716, for target pairs; and Dugongue, PR476/478,
for reversible target factoring. Navinor's PR848 concerns the barrier under
unchanged syntactic H2; this package explicitly requires a different semantic
contract. Gareth Davidson's PR941 matching bound is comparison metadata only.

The native harness follows Sagar Thakrar's
`research/r420-decoder-sharing/native.py` pattern. Unchanged owning tools
retain their notices: eumemic for the punctured checker; Dylan Crow /
utcorvusvolat-dotcom (PR370, Anthropic Claude assistance) for exporter,
staging and native-checker lineage; DaysSky (PR381, Claude assistance) for
bridged-stage checking; Zhihao Chen / jacklightChen (PR386, OpenAI Codex
assistance) for portability and the common-label lineage; DreamingOfClouds
for nine-stage accounting; Chafik Boukhalfa and the other retained contributors
for hosted compilation and physical audits. Jacob Sussman introduced the E8
unit. Niels Lohmann and contributors retain the MIT header in `json.hpp`.

No predecessor source or notice is modified. External Boost headers used in
validation retain the Boost Software License and are not distributed here.
The package's LICENSE is the repository's Apache-2.0 license.
