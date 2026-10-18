# Notice and provenance

New code and documentation are Apache-2.0. Prepared for Gareth Davidson
(@bitplane), with substantial OpenAI Codex assistance. One AI agent performed
the work; no separate human review is claimed.

The 95 replacements and candidate are derived from **DreamingOfClouds's
PR589 tuning of eumemic's PR555** selected R439 word, at
`a5afc8c6169ea61ba7c51dfd3cade02cc7b13b46`, retaining
its E8 geometry, port selection, frame system, decoder and raw interface.
`candidate.json.gz` is a modified derivative of that word. The input word and
unchanged `xcheck_p.py` are consumed from `research/e8-bit-p111-tuned`.
That package's `NOTICE.md` and `LICENSE` are included in the pinned source
closure and preserve its substantial Anthropic Claude assistance and further
PR543/545/493/510/425/370 lineage. DreamingOfClouds prepared PR589 with
Claude Opus 5.5 (Anthropic), via Claude Code, using the transport mechanisms
of Dugongue's PR541/548 and rohanarun's PR542. The package LICENSE here is
copied verbatim from the input package.

**Jeffrey Cox (@namredips), PR754**, is credited for exact small-GL resynthesis
with both-order positive domination and disjoint interval selection. This
submission reimplements that method for the selected R439 A/B prefix and
rebuilds paired literal cleanup. No PR754 code is imported; its original
scope was historical R420 C-only cleanup with a semantic H4′ certificate.

`native.py` adapts the source-pinning, compilation and replay harness pattern
from **Sagar Thakrar's `research/r420-decoder-sharing/native.py`**, prepared
with substantial OpenAI Codex assistance. Changes parameterize for v=111,
R=439; run 5/9/11 stages; compare per-register movements and COPY/ERASE;
and report the new complete bill and bounds.

Native exporter, staging and checkers are used byte-identically from
`research/e8-bit-carrier-skeleton`, whose notice and license are pinned:

- **Dylan Crow / utcorvusvolat-dotcom**, PR370, with Anthropic Claude
  assistance: record exporter, staging, generalized native legality checker
  and the inherited PR266 checker lineage.
- **DaysSky**, PR381, assisted with Claude: `columns_k.cpp` and its bridged
  stage extension from PR363.
- **Zhihao Chen / jacklightChen**, PR386, with OpenAI Codex assistance:
  portable `bits/stdc++.h`.
- **Niels Lohmann and contributors**: `json.hpp`; its MIT license is retained
  in the unchanged header.
- **eumemic**, with substantial Anthropic Claude assistance: the carrier
  skeleton package and its source notices. **Jacob Sussman** introduced the
  E8 unit; **Zhihao Chen** supplied the mutable-source scalar-interface lemma.

SOURCES.json hashes every consumed source and both packages' notices/licenses.
They are existing repository files, not re-vendored or edited in this change.
