# Attribution and scope

Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance. Apache-2.0.
This package claims no exclusive priority over concurrent work.

What this package contributes: the censuses of twin dirty helpers at PR #259's earliest cut and of shared donors,
the 387 added kernel families (`inputs/candidates.json.gz`, rounds "union-early-cut", "headroom-2", "shared-donor"),
the rebinding of the two published retiming selections to this transcript, the regenerated receipts, and the
discovery scripts in `discovery/`. Everything else is retained and credited:

- Dugongue (OpenAI Codex assistance): PR #254 (the response-kernel pair rewrite, projector charts, native checkers),
  PR #259 (multi-cut kernel condensation, the generic exact chart audit, the seven checkers, the pricer and the
  finite invoice, used here unchanged except one `std::stable_sort`; its notes kept as README-PR259.md,
  PROOF-PR259.md, KERNEL-PROOF.md, BANK-PROOF.md, COPY-PROOF.md, FINITE-PROOF.md, REVIEW.md), PR #267 (chronological
  donor sharing, the idea behind the shared-donor families).
- rohanarun: PR #263 (the concave-descent frame retiming stage `code/descent_retiming.py` and its 25-gate selection,
  used verbatim), PR #237/#209 (five-stage bit supplier, width-120 banks), PR #269.
- utcorvusvolat-dotcom: PR #270 (the 24 reuse pairs and two e = 2 planes, the plateau retiming stage
  `code/plateau_retiming.py` with `verify_frames.py`, `verify_plateau_spans.py`, `verify_frame_tables.py` and the
  29-block selection, and the rebinding of PR #263's selection by scalar-core alignment, all used verbatim).
- eumemic (Anthropic Claude and OpenAI Codex assistance): PR #249/#244/#251 (the source527 bit word, entrance
  banks, retimed source pairs, transported entrances) on PR #210's helper and PR #168's modules; PR #268.
- hcg890 PR #234 (five-stage bit and complex suppliers); sennemmi PR #230/#261/#265; evmckinney9 PR #271.
- The PR #249 lineage as credited in vendor/UPSTREAM-NOTICE.md and below.

---- PR #259's notice follows unchanged ----

# Attribution and scope

New response-kernel rewrite, native checks and packaging prepared with substantial OpenAI Codex assistance. No personal byline is added.

Based on CrocSwap/integer-mult-bounds PR249 at commit 96495746c786d6d0339dbb38c7f553d4af3f88ed. The original sources and license notices are preserved in vendor/pr249-source.zip; see vendor/UPSTREAM-NOTICE.md for upstream contributors and mechanisms. Those historical public credits are retained.

New code is distributed under Apache-2.0 (LICENSE). The vendored nlohmann JSON single header retains its own MIT license and attribution. Boost is an external build dependency, under the Boost Software License. Existing third-party files retain their original terms.

This is a finite construction with exact checks, conditional on retained public all-size interfaces. It is not a Lean/kernel certificate or an unconditional integer-multiplication theorem.
