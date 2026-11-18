P104: a conditional ceiling κ ≤ .0136564 covering the current frontier words (Lean, no κ)

Lean-only package, builds on #7656 (its modules are included unchanged; 13 new modules). No κ claim.

**Result.** `CongestionNative.ceiling_native`: F(1−t) < 0 for t in [.0136564, 1] on the 17-call invoice of the #7113 caller C(8|9), conditional on the named hypotheses in `PROVED.md` (copied from the Lean text). The hypotheses include at most 5 mixed public registers (the earlier restricted-class premise "every public register ends at V" is gone, via a two-sided I3 telescoping), the descent mass and rank conditions, the junk count |J| ≥ 1936, certified rational tables, and the Cap-class accounting. `CongestionNativeH.ceiling_native'` derives `hspMono`, `hcstMono`, `hdist` and `hcong*` from shape-DAG hypotheses and per-cell chart-path hypotheses (`path_cut`, the 48-law, `hcong_of_capclass` are proved and wired in). The monotonicity of c2 in t (superadditivity of x^s ln x) is proved in the kernel. All theorems print only propext, Classical.choice, Quot.sound; no `sorry`, no `native_decide`; every module was compiled fresh (`CHECK.txt`).

**Caveats, stated plainly.**
- The class-wide bound |J| ≥ 1936 is a conjecture (it rests on the rank-8, C = 56 decoder structure, whose rigidity is numerical; decoders with 9 or more rows and network decoders are open). The natives' value, |J| = 4962, is computed, not bounded.
- Word-level premises are computed by scripts that are not in the package (`NATIVES.md`: script, words, result). hcong*, hdist, hspMono and hst are paper theorems whose premises the natives meet; in Lean, hspMono, hcstMono and hdist are now derived from shape-DAG hypotheses, and hst and the register-machine facts (hconf, hstart, hvisit, hleg) remain hypotheses.
- Path-Cut is stated for the cancellation (arrival) path of a junk cell. `hconf` and `hstart` are what that arrival decomposition supplies, not free premises; the lemma is not claimed for arbitrary paths, since a path that re-enters the confinement region by a nested owned descent is an arrival, counted on the left, never cut. The decomposition itself is not formalised.
- Completeness of the 230-shape DAG for the natives' 104-port set was re-derived independently by exhaustive enumeration (identical); other port sets are not covered.
- The natives share one owned layer and one port set, so they are close to a single data point. The data files' fidelity to the word files rests on reading, and the link from the Lean invoice to each word's pricing is the pricing script's.

The premises under study are SYLforge's (#7616, #7620); the caller is rohanarun's (#7113). DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
