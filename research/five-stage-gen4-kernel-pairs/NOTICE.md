# Attribution and scope

Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance. Apache-2.0. Inherited files retain
their original notices and assistance disclosures. This package claims no exclusive priority over concurrent work.

What this package contributes: the twin-helper census on the gen4 word with per-pair cuts, the 424-pair selection
and its entrance lines, `kernel_transform.py` (eumemic's #268 kernel stage adapted to per-pair cuts),
`raw_ledger.rebind_kernel`, the (23⁴, 4⁷) bank tiling for rank-23 residuals at 60 replicas, the pin plumbing
(`pins.py`, `expected/kernel-pins.json`) that turns every changed literal of #276's checkers into a recomputed
pinned value, the composition with #279's descent stage, `KERNEL-PROOF.md`, and `discovery/`. Everything else is
retained and credited:

- DreamingOfClouds (Anthropic Claude assistance): PR #276, the gen4 bit word and its package
  (`research/five-stage-gen4-banks`), used unchanged except the pinned values listed in KERNEL-PROOF.md; its notes
  are kept as README-PR276.md, PROOF-PR276.md, BANK-PROOF.md, PR-STATEMENT.md and the files under proof/ and
  notices/.
- rohanarun: PR #279, the concave-descent frame retiming stage (`descent_transform.py`, `descent-selection.json`,
  `raw_ledger.rebind_descent`, 880 gates), vendored unchanged; PR #263/#273 on the earlier word.
- eumemic (Anthropic Claude and OpenAI Codex assistance): PR #268 (the kernel_transform.py mechanism for
  response-kernel pairs in this pipeline, and its pinned-value form for bank, math and finite checks), the source527
  five-stage package (PR #251/#249/#244/#210) that #276 carries, PR #168 modules.
- Dugongue (OpenAI Codex assistance): PR #254 (response-kernel helper pairs) and PR #259 (multi-cut condensation),
  the mechanism's origin; PR #207/#216 finite and bank admissions.
- hcg890 PR #234 (five-stage layout), Jacob Sussman (five-stage construction, gcert/1), Evan McKinney PR #197 and
  rohanarun PR #237 (completed width-120 banks), ikeboy PR #193 (complex helper), icekylinx PR #144, James Chang
  PR #166, sennemmi PR #230, Chafik Boukhalfa PR #200 (physical-word classes vendored in gen4bit/bit).
- The full inherited lineage follows in #276's notice, unchanged.

---- PR #276's notice follows unchanged ----

# Attribution and licence

Apache-2.0 applies. Original headers, licences, notices and AI-assistance disclosures are preserved. The
credits below do not imply review or endorsement.

## Inherited, unchanged or with rebound constants

- **Five-stage architecture and finite interface package:** Henry Grant (hcg890), PR234, and Jacob
  Sussman's five-stage construction and gcert/1 export. The complete inherited five-stage credits are in
  `UPSTREAM-PR234-NOTICE.md`.
- **Package machinery:** eumemic's source527 package, prepared with substantial OpenAI Codex assistance,
  with its lineage: Dugongue's PR207/PR216 finite and bank admissions, Rohan Arun's PR211 and sennemmi's
  PR230 frame work, and eumemic's PR210. Their notices are retained verbatim in `notices/`.
  This covers the scalar program `scalar/word.py` (byte-identical), the physical event emitter, the parity
  fusion, the raw-ledger census, the stage-private bank template and checker, the moment, prime and
  finite-bill checks, and `verify.py`. In this package they are rebound to the gen4 helper's constants;
  the logic is unchanged.
- **Banks:** Evan McKinney's PR197 completed-bank method. Rohan Arun's PR237 published the width-120
  application first.
- **Complex supplier:** Avi Eisenberg (ikeboy)'s PR193 helper, inside Sussman's five-stage certificate.
  The original disclosures are in `inputs/complex`.
- **Physical-word classes:** Chafik Boukhalfa (chafreaky)'s PR200 `bit/word.py` and `bit/base_word.py`,
  vendored unchanged in `gen4bit/bit`. `gen4bit/NOTICE-PR200` is PR200's own notice.
- **Checker:** eumemic's PR168-v4 `check_paired_cube_bit.py`, vendored unchanged.
- **Paired-cube framework and its developments:**
  - icekylinx's PR144: paired-coordinate/shared-core framework and configurable local channels.
  - PR161/PR168 (eumemic): annealed modules, nested schedules and the generator.
  - James Chang's PR166 and PR162's carrier rule.

## New in this package

**The gen4 bit word.** This covers:

- the arc-aware per-cube local design (`local_design()` recipe trees and `data/local_design_p12.json`);
- the re-annealed all-but-one module (`data/qmod_p12.json`);
- the centre-sharing pair module (`data/pair_module_p12.json` and the patch in `finish()`);
- the frozen arcs (`data/arcs_p12.json`).

**Its physical-layer producers.** `gen4bit/producer/make_physical.py` and `descent.py` are new
implementations of PR200's stated rules.

**Package integration.** This covers:

- `prepare.py` and `virtual_check.py`;
- the rewritten `scalar_check.py` controls;
- the rank-21 geometry check;
- the gen4 bank patterns and documentation.

All of this was prepared by DreamingOfClouds with Anthropic Claude assistance. The circuit and module
search was run by Claude agents (simulated annealing, CP-SAT and exact one-instance compiles), and every
reported number was re-run with the exact generator. No exclusive priority is claimed for any inherited
design or theorem interface.
