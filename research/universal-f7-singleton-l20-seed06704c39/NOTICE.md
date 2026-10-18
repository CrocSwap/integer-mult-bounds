# Notice and attribution

* PR943 prefix-walk model, the query interface `D(w) = {q_s xor q_t}`, and the
  first exact values: **Ross Richardson**, `research/universal-connector-boundary`
  (https://github.com/CrocSwap/integer-mult-bounds/pull/943).
* Pinned five/six-source record (`f(5) = 12`, `f(6) = 16`, the `f(7)` gap,
  counting bounds and Gray constructions), and the byte-exact EXPECTED.json
  reproduced here: **Douglas Colkitt**,
  `research/universal-connector-six-source`
  (https://github.com/CrocSwap/integer-mult-bounds/pull/1185).
* Length-18 exclusion (`f(7) >= 20`), the restricted-growth cycle census
  engine (`engine.py`, vendored here byte-exact, SHA-256
  `82e4c407b58864c74ffd14d47f00b6b1675005ee0e0173909b7bd092491175e4`,
  git blob `210bd817b19beb20ed474d8946ea87a22121ac1c` at head
  `3b6011d2400f50ab0ad9e105c7c55a18f3cef4cf`), the pair-representation
  identity (`lemma_a_table`), and the proved-necessary census prunes:
  **Aaron Wang, with help from opencode**,
  `research/universal-f7-singleton-seedb859517b`
  (https://github.com/CrocSwap/integer-mult-bounds/pull/2542). This package
  re-runs that census in full and reuses the engine byte-exact; the reuse is
  pinned in SOURCES.json and enforced by a test.
* Community set-level fact re-derived in PR 2542 as a control (nine-point
  five-bit census, `r[(C2)^6] = 14` after Gavrylkiv): published at
  https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18931315.

This package (search campaign, template lemmas, covering-set artifacts, the
resumable simple-20-cycle census) is by **Aaron Wang, with help from opencode**
(substantial AI assistance in scoping, implementation, verification and
writing; no model named; no independent human review claimed).

Repository and source licenses are unchanged; `research/universal-connector-six-source/LICENSE`
and the repository LICENSE both remain in force.
