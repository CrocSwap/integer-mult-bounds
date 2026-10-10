# Attribution and scope

This package (`five-stage-gen5-restore`) is the `five-stage-gen5-kernels-descent` package of PR #291 with one added
stage: PR280's early restoration of cleanup helpers (utcorvusvolat-dotcom, gen4), re-derived on the gen5 word
(`restore_transform.py`, `restore-selection.json`, `RESTORE-PROOF.md`, `raw_ledger.rebind_restore`), together with the
five-stage admission of helpers that retire below the full frame (endpoint-aware completions in `code/global_lowering.py`
and `code/geometry527.py`, residual-width families and (σ, E) charts in `bank_check.py`/`bank_template.py`, completion
subtraction in `math_check.py`/`finite_check.py`), the regenerated pins and manifest, and this package's README/PROOF.
That addition was prepared by Rohan Arun (rohanarun) with Anthropic Claude assistance, Apache-2.0; no exclusive priority
is claimed. The early-restoration rule and its integer commutation argument are PR280's. The notices of #291 and #290
follow unchanged.

---

# Attribution and scope

This package (`five-stage-gen5-kernels-descent`) is Chafik Boukhalfa's PR #290 package with one added stage: a second
run of rohanarun's `descent_transform.py` after the kernel entries, with the frozen `descent2-selection.json` (89 gates,
32 constructed bases), `raw_ledger.rebind_descent2`, the regenerated pins and manifest, and this package's README/PROOF.
That addition was prepared by Rohan Arun (rohanarun) with Anthropic Claude assistance, Apache-2.0; no exclusive
priority is claimed. #290's own notice follows unchanged.

---

# Attribution and scope

Prepared by Chafik Boukhalfa with substantial Anthropic Claude assistance. Apache-2.0. Inherited files retain their
original notices and assistance disclosures. This package claims no exclusive priority over concurrent work.

What this package contributes: the twin and collective censuses on the gen5 word after #287's descent and target
stages, the 450-entry selection (260 twin pairs, 190 multi-donor families) with its entrance bases,
`kernel_transform.py` (eumemic's #268 kernel stage generalised to per-entry cuts, entrances of any dimension and shared
donors, first shipped in #282), `raw_ledger.rebind_kernel`, the (r⁴, 4³⁰⁻ʳ) tiling for every pivot residual width,
the per-rank geometry sample, the pin plumbing (`pins.py`, `expected/kernel-pins.json`), `KERNEL-PROOF.md` and
`discovery/`. Everything else is retained and credited:

- DreamingOfClouds (Anthropic Claude assistance): PR #285, the gen5 word (compile-cost-annealed pair and all-but-one
  modules) and its package, on PR #276's gen4 word and package.
- rohanarun: PR #287 (the 904-gate descent stage and the 220 target squares on gen5, the package this extends), PR #279,
  PR #273/#263.
- eumemic (Anthropic Claude and OpenAI Codex assistance): PR #268 (target-prefix compression and the kernel stage form
  in this pipeline), the source527 five-stage package lineage (PR #251/#249/#244/#210), PR #168.
- Dugongue (OpenAI Codex assistance): PR #254/#259/#272/#283 (response-kernel pairs, multi-cut and collective kernels,
  the (r⁴, 4³⁰⁻ʳ) tiling rule).
- hcg890 PR #234, Jacob Sussman (five-stage construction), Evan McKinney PR #197, ikeboy PR #193, icekylinx PR #144,
  James Chang PR #166, sennemmi PR #230, utcorvusvolat-dotcom PR #270/#280, Chafik Boukhalfa PR #200/#282/#284.
- The full inherited lineage follows in #287's notice, unchanged.

---- PR #287's notice follows unchanged ----

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

The concave-descent frame retiming stage (`descent_transform.py`, `descent-selection.json`, `raw_ledger.rebind_descent`), the target-prefix selection (`target-selection.json`; the transform `target_transform.py` is eumemic's from PR268, Apache-2.0, with only the stream count generalized) and this package's rebinding were prepared by Rohan Arun (rohanarun) with Anthropic Claude assistance, Apache-2.0. The gen5 bit word and the five-stage completed-bank package are DreamingOfClouds' and eumemic's work with the notices above retained unchanged.
