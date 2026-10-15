# Preserved arithmetic dependencies

These four Python files are copied byte for byte and hash-pinned:

- `moment.py`, `base_two_moment.py`, `outer.py` from
  `research/complex-k492-owner-repair/vendor/multicold/engines/` in
  CrocSwap/integer-mult-bounds. Their inherited attribution is preserved in
  `ENGINES-NOTICE.md`; they are the same engines pinned by the current source
  assemblies.
- `price_profile_t16.py` from PR870 commit
  `b734850dc348800942f0ffd1f0723fdec7539b2b`, path
  `research/gauge44-barch-t16/independent/price_profile_t16.py`, retained
  unchanged through PR890. `PR870-NOTICE.md` and `PR870-UPSTREAM-NOTICE.md`
  preserve source credits and AI disclosures. The current checker imports
  only its pure arithmetic helpers; its historical standalone CLI and
  missing historical input tree are not invoked.

Apache-2.0 applies; the unchanged license is included. Hashes, source paths
and immutable source pins are recorded in the parent `SOURCES.json`. No
upstream attribution or inherited mathematical assumption is replaced.
