# Attribution and scope

This package adds no new local scalar operation. It combines two existing admitted providers under a new literal owner map:

- #571 (`research/structural-gain`, commit `b7bdc5a8de18fcf418cfb9c7d83a2b1097a5e4a3`): the combined-prefix width-seven provider word `frontier-composition/combined-prefix-word/FULL-WORD.json.gz`, its retained local (`frontier-composition/combined-prefix-local`), its dispatch of 63 width-seven and 9 plain calls, and the global admission scripts in `frontier-composition/global-code/`. #571 was prepared with OpenAI Codex assistance under Apache-2.0.
- PR568 (`research/complex-multicold`, commit `71c99ac935a33bb7b59a1b4a7af8725a939b0b90`): the eight-cold multi-cut eight-pivot provider word, rebuilt by its unchanged scripts. It replaces #571's four-cold plain provider on #571's nine plain calls.

Both packages are pinned external sources. `verify.py` checks their manifests and the exact file hashes it uses. It runs their unchanged scripts, rebuilds the width-seven local from #571's pinned word, and requires that rebuilt local to match #571's retained local byte for byte.

The scripts in `code/` are copied from #571's `frontier-composition/global-code/` with these changes:
- `bind_providers_portable.py` and `audit_allcold.py`: the plain provider (`fourcold_eight`) inventory and profile now pin PR568's eight-cold word (`{4:8,5:48,8:164,9:284}`, profile `{1:2332,2:436,3:448,4:192,5:56,6:56,8:8}`).
- `assemble.py`: pins this witness's provider values, owner geometry, idle remainders, profile, endpoints and kappa.

The literal owner map was nominated by a HiGHS window MILP at #571's fixed dispatch, adapted from PR569's `global/nominate_width7.py`. Lazy cross-time Hall cuts make every window literally decomposable. The admission scripts check the map independently.

The provider swap, literal owner assignment and this package were prepared by Claude Code (Anthropic) research agents. Apache-2.0 applies; LICENSE is included. All notices, licenses, source pins and AI disclosures of #571, PR568 and their ancestry are retained in those packages and are not replaced by this notice. All inherited conditional assumptions remain conditional.
