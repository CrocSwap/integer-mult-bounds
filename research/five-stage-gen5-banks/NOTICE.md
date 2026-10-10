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
  finite-bill checks, and `verify.py`. In this package they are rebound to the gen5 helper's constants;
  the logic is unchanged.
- **Banks:** Evan McKinney's PR197 completed-bank method. Rohan Arun's PR237 published the width-120
  application first.
- **Complex supplier:** Avi Eisenberg (ikeboy)'s PR193 helper, inside Sussman's five-stage certificate.
  The original disclosures are in `inputs/complex`.
- **Physical-word classes:** Chafik Boukhalfa (chafreaky)'s PR200 `bit/word.py` and `bit/base_word.py`,
  vendored unchanged in `gen5bit/bit`. `gen5bit/NOTICE-PR200` is PR200's own notice.
- **Checker:** eumemic's PR168-v4 `check_paired_cube_bit.py`, vendored unchanged.
- **Paired-cube framework and its developments:**
  - icekylinx's PR144: paired-coordinate/shared-core framework and configurable local channels.
  - PR161/PR168 (eumemic): annealed modules, nested schedules and the generator.
  - James Chang's PR166 and PR162's carrier rule.

## New in this package

**The gen5 modules** (on top of #276's gen4 word): `data/pair_module_p12.json` (pair + centre, debt 164) and
`data/qmod_p12.json` (all-but-one, debt 11), annealed against the exact one-instance compile cost with exact
closed-form rank evaluators; the new frozen arcs `data/arcs_p12.json`; and the `--bank-parity` option of the
pair producer.

**The gen4 bit word** (from #276, retained). This covers:

- the arc-aware per-cube local design (`local_design()` recipe trees and `data/local_design_p12.json`);
- the centre-sharing pair-module patch in `finish()`.

**Its physical-layer producers.** `gen5bit/producer/make_physical.py` and `descent.py` are new
implementations of PR200's stated rules.

**Package integration.** This covers:

- `prepare.py` and `virtual_check.py`;
- the rewritten `scalar_check.py` controls;
- the rank-21, rank-18 and rank-17 geometry checks;
- the odd-coefficient choice in the `scalar_check.py` controls;
- the gen5 bank patterns and documentation.

All of this was prepared by DreamingOfClouds with Anthropic Claude assistance. The circuit and module
search was run by Claude agents (simulated annealing, CP-SAT and exact one-instance compiles), and every
reported number was re-run with the exact generator. No exclusive priority is claimed for any inherited
design or theorem interface.

The concave-descent frame retiming stages (`descent_transform.py`, `descent-selection.json`, `descent2-selection.json`, `raw_ledger.rebind_descent`, `raw_ledger.rebind_descent2`), the target-prefix selection (`target-selection.json`; the transform `target_transform.py` is eumemic's from PR268, Apache-2.0, with only the stream count generalized) and this package's rebinding were prepared by Rohan Arun (rohanarun) with Anthropic Claude assistance, Apache-2.0. The gen5 bit word and the five-stage completed-bank package are DreamingOfClouds' and eumemic's work with the notices above retained unchanged.
