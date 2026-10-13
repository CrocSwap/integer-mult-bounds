# Attribution and scope of changes

Prepared for chafreaky with OpenAI Codex assistance. Apache-2.0; see LICENSE.
All notices in the inherited files are preserved. In particular, original
PR493/503/510 bit checker and invoice sources are copied from PR510, without
replacing contributor names or assistance notices.

- PR541 by Dugongue contributes the 60-preload construction and the static44
  local appendix, including its fixed selection and scalar controls. Their
  constructor and appendix are copied unchanged. The static44 appendix's
  local-only scope remains accurately described in its original README.
- PR542 by rohanarun contributes the suffix-response slicing method. Its
  227 zero-response gate deletions are recomputed exactly in `build_bit.py`.
- PR535 by icekylinx supplies the post-center rank-four baseline inside the
  static44 appendix. PR531 and its attributed PR484 lineage supply the complex
  geometry, gauges, kernel primitives, local/global checkers and data controller.
- PR493/503/510 and their credited predecessors supply the native bit checkers,
  mutable-source semantics, global hosting and exact invoice machinery.
- New here: ten fixed exact-cost bit frame changes, their exact replay; the
  static44 global owner allocation and complete phase/owner admission; and
  the composition and cold verification of both changed suppliers.

`run_native.py` and `run_global.py` adapt PR541's orchestration for the new
profiles and actual checked prefix. `assemble.py` adapts the attributed
PR531/535/541 assembly to both fresh invoices and a 192-bit charged bit prefix.
The retained two-level charge is 512 bits. The independent native, owner,
invoice, moment and outer checkers are unchanged. `code/run.py` and
`code/phases_full.py` are carried from our attributed PR538 package.
