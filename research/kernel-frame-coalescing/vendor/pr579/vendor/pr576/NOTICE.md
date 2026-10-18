# Attribution and scope

This package combines three providers under a new literal owner map (54 P571, 8 P571K, 10 E8 calls):

- #571 (`research/structural-gain`, commit `b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3`): the combined-prefix width-seven provider word `frontier-composition/combined-prefix-word/FULL-WORD.json.gz`, its retained local (`frontier-composition/combined-prefix-local`), its dispatch of 63 width-seven and 9 plain calls, and the global admission scripts in `frontier-composition/global-code/`. #571 was prepared with OpenAI Codex assistance under Apache-2.0.
- PR568 (`research/complex-multicold`, commit `71c99ac935a33bb7b59a1b4a7af8725a939b0b90`): the eight-cold multi-cut eight-pivot provider word, rebuilt by its unchanged scripts. It is rebuilt by PR568's unchanged scripts and serves as the plain provider (E8).
- P571K: #571's combined-prefix word with twelve additional multi-cut cold kernels, built by PR568's unchanged `code/build_multicut_kernels.py` from `data/P571K-MULTICOLD.json` (recipe derived by a greedy kernel search over #571's word), with PR568's unchanged omission controls `code/audit_multicold_controls.py`.

Both packages are pinned external sources. `verify.py` checks their manifests and the exact file hashes it uses. It runs their unchanged scripts, rebuilds the width-seven local from #571's pinned word, and requires that rebuilt local to match #571's retained local byte for byte.

The scripts in `code/` are adapted from #571's `frontier-composition/global-code/`. Every witness-specific value, including provider inventories, profiles, artifact and program hashes, dispatch, owner geometry, idle remainders, endpoints and kappa, is read from `data/WITNESS-SPEC.json` through `code/witness.py`. The spec was generated from audited global outputs, not hand-copied.

The literal owner map was nominated by a HiGHS window MILP with large-neighbourhood search, adapted from PR569's `global/nominate_width7.py`. Lazy cross-time Hall cuts make every window literally decomposable. The admission scripts check the map independently.

The kernel recipe, provider mix, literal owner assignment, spec-driven admission code and this package were prepared by Claude Code (Anthropic) research agents. Apache-2.0 applies; LICENSE is included. All notices, licenses, source pins and AI disclosures of #571, PR568 and their ancestry are retained in those packages and are not replaced by this notice. All inherited conditional assumptions remain conditional.
