# Primary bit-scalar and common-frame contract

The three unmodified source files in this directory are carried by Henry Grant / hcg890's PR234 snapshot:

- Repository: https://github.com/hcg890/integer-mult-bounds
- PR: https://github.com/CrocSwap/integer-mult-bounds/pull/234
- Exact snapshot commit: `af3fe331ca60c936229e060681ffccbc1c208678`
- Primary section path in that snapshot: `upstream/build/sections/03-motifs.tex`
- Accompanying source paths: `upstream/README.md` and `upstream/LICENSE`

The accompanying README identifies the primary work as **OpenAI, Integer multiplication below n log n, September 23, 2026** and records its original citation and publication link. It is retained as `UPSTREAM-README.md`. This is attribution to the primary source; the snapshot commit above belongs to the carrying repository and is not asserted to be an original OpenAI commit. These credits do not imply review or endorsement of this contribution.

The accompanying Apache-2.0 license is retained without modification as `LICENSE`. These files have not been edited, excerpted, or reformatted. The exact content hashes are:

| Bundled file | SHA256 |
| --- | --- |
| `03-motifs.tex` | `ed76761194988a01af77ead0ea6469cb5dcd29690ab985a0b5a4006b0f2b69bb` |
| `UPSTREAM-README.md` | `8d1ceff898a4e0e681679f91c4def485820be9e99f04e4861f2ce601a364723e` |
| `LICENSE` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` |

`03-motifs.tex` supplies the bit scalar ring at line50, the common-frame identity at lines149–177, the distinction between scalar and label fields at line225, and the rational-address bit frame contract at lines483–493. It is bundled as theorem evidence, not as a standalone compilable document. The accompanying [`../PARITY-CONTRACT.md`](../PARITY-CONTRACT.md) proves the parity-filter adaptation and records the finite verification obligations. No theorem dependency in that parity argument requires a machine-local path.

This provenance note and the parity contract were prepared with substantial OpenAI Codex assistance. Original source authorship and assistance disclosures remain separate from that disclosure.
