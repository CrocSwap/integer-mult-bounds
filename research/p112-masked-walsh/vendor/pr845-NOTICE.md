# Attribution and license

Prepared for Mihir Srivastava (@mihir-s-05), with substantial OpenAI Codex
assistance in the proof, experiments, implementation, verification and
writing. No independent human review or proof-assistant verification is
claimed. New work is under the repository's Apache-2.0 license.

- DreamingOfClouds' PR717, pinned at
  `4150829a2cb66b823f4282da98985959ee448a90`, supplies the P112 decoder
  model, root and simple-basis conventions, and the open mixed-beta question.
  `reference/pr717_e8model.py` is an unchanged copy. `geometry.py` adapts
  its geometry definition using exact standard-library arithmetic.
  `reference-geometry.json` is a snapshot of its arrays as described in
  SOURCES.json. The original notice is retained in
  `reference/PR717-NOTICE.md`, including its Claude assistance disclosure.
- Joel Pulikkan / GamingPuzzled's PR620 records the coordinate P112 copy
  cost 64. This contribution claims neither priority for that value nor
  verification of all other claims in that package.
- DreamingOfClouds' PR446 Theorem C supplies the inherited copy-tree
  interpretation. Its proof and physical correspondence have not been
  newly audited here.
- Jacob Sussman, Zhihao Chen (jacklightChen), Dylan Crow
  (utcorvusvolat-dotcom), icekylinx, eumemic, Jeremy Kothe, Chafik Boukhalfa
  and the wider cited community retain credit for the E8 geometry,
  label/frame calculus, supplier and compiler lineage. The selected
  #741/#589 construction is context, not a result of this package.

The new contribution is the single-lift annihilator obstruction, its compact
functional-support reduction, exact finite certificates, independent
checking implementation and scoped proof. All source-specific notices and
the repository license continue to apply.
