P104: tiered ceilings for words meeting the native-class hypotheses (incl. the frontier words), Lean only

Lean-only package, builds on #7656 and #7659 (their modules are included unchanged; new modules: the T1 pieces `CongestionNativeJ*`, `JunkLawA`, `JunkLawACeiling`, the N96 and Z0 pieces `CongestionNativeN*`, `CongestionNativeZ*`). No κ claim and no word claim in Lean.

**Results.** Each theorem proves `Finv (1 − t) (invoice (caller 6 7) n 17) < 0`, the F-form of the 17-call invoice of the #7113 caller C(8|9), for every t with t0 ≤ t ≤ 1, under its full hypothesis list in `PROVED.md` (copied from the Lean text; the same hypotheses are also listed by script in `README.md`).
- **T1**, `ceiling_native_J`: t0 = .0118103 (`tJ0`). Hypotheses include the junk count `hJ : 4962 ≤ J.card`.
- **T2a**, `ceiling_noHJ`: t0 = .0151027 (`tN0`). No junk-count hypothesis (`96 ≤ |J|` is derived in Lean from Law A, `JunkLawA.lean`), but it needs `m : LawAModel K 104 D` (`hspan`, `hdiag`, `hodd`, `hpart ≤ 48`), `hD : D ≤ 56` and `hJdef : J = junkSet m.M`.
- **T2b**, `ceiling_native_Z0`: t0 = .0151869 (`tZ0`). No junk-count hypothesis and no upper bound on owned mass (none of T1, T2a, T2b bounds `ks.sum` from above; all keep `hmass : 56 ≤ ks.sum`).

"For the frontier words" means: the frontier words satisfy all the hypotheses of these theorems (computed, `NATIVES.md`, a table of premise × word → result and script). Checked on all four of `st1` (#7641), the #7637 word, `x1t2a` and the #7660 word: |J^arr| = 4962, rank M = 11, D = 24, the LawAModel premises, hmono, hd9, hmix = 5 (tight), hk, hmass, hmd, hmr, hY, hF, hEex, hst, the Cap class, and the legal-path and Cap-margin ingredients of hcong / hdist. They share one owned layer and one port set, so this is close to a single data point. The link from the Lean invoice to each word's pricing is the pricing script's. Nothing in Lean ties a word to the hypotheses.

Law A as proved in Lean is `lawA_96`: for `m : LawAModel K 104 D` with `D ≤ 56` (premises `hspan`, `hdiag`, `hodd`, `hpart ≤ 48`, P = 104), `96 ≤ m.J`. Behind it, `maisBound` (Caro-Wei, needs `hdiag`) gives Σ_t 1/(j_t+1) ≤ rank M, and rank M ≤ D by `hspan`. The general inequality J ≥ 2(P − D) is not stated in Lean. All theorems print only propext, Classical.choice, Quot.sound; no `sorry`, no `native_decide` (`CHECK.txt`).

**Caveats, stated plainly.**
- T1 covers only words with |J^arr| ≥ 4962. A word with less arrival junk (rank 9, 10, 11 decoder matrices with J = 4336, 3728, 3168 exist; whether any is realisable as a word is open) is covered by T2a or T2b only if it meets all their other hypotheses (hmix ≤ 5, hmono, hd9, hk, hmass, hmd, hmr, hY, hF, hst, hEex, hcong, hdist, and for T2a the LawAModel premises, `hD`, `hJdef`). Those are not checked for any such word, and hmix = 5 is tight on the known words. The same holds for a word with D > 56 and T2b.
- T1 and T2 hard-code the 8-row decoder constants (`corrC ≤ 8 · cH`, `capC ≥ unLo / 48`). Decoders with 9 or more rows are outside the model; rank 9, 10, 11 matrices that need that many rows are not covered.
- `hJdef : J = junkSet m.M` is not a naming link only: it forces `hcong` and `hdist` (real-valued statements) to hold on exactly the off-diagonal support of `m.M`. In T1, `J` is any finset with `hJ`; in T2b, `J` and `distF` are still quantified and `hcong`, `hdist` are assumed (even for `J = ∅`). Lean does not tie `J` to `J^arr` of a word.
- `hcong`, `hdist`, the spF / cst brackets and the monotonicity `hspMono`, `hcstMono` (a paper theorem) are hypotheses in Lean, as are the Law A premises. `NATIVES.md` computes their ingredients on the four words; the step from the computations to the Lean statements is not formalised.
- "Owned mass > 56 never pays" is a paper argument and not in Lean. `hD` in T2a is the size of any spanning set of arrival vectors, so in effect rank M ≤ 56 (the words have rank 11, D = 24). Intermediate ceilings for 56 < D < 104 were not built.
- `CHECK.txt`: 65 of the 66 modules were compiled fresh. `CongestionI3Cfg` (unchanged from #7656, where it built fresh) was stopped by the 3.5 GB memory guard at about 3.44 GB, twice, so its prebuilt olean from the earlier build was used for the modules that import it.

Premises under study are SYLforge's (#7616, #7620); the caller is rohanarun's (#7113). DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
