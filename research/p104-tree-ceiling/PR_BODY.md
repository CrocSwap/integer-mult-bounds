P104: node-partition refinement of the frontier-word ceiling, κ ≤ .0116750 (Lean, conditional, no κ claim)

Lean-only package, builds on #7668 (its 46 import-closure modules are included unchanged; 148 new modules). No κ claim and no word claim in Lean: all objects in the two theorems are abstract, and nothing in Lean ties a word to the hypotheses.

**Results.** Two theorems in `Nov15/CongestionTree.lean`, each proving, for `t ∈ [t0, 1]` (that is, `t0 ≤ t ≤ 1`), `Finv (1 − t) (invoice (caller 6 7) n 17) < 0` (caller `caller 6 7`, L = 17) under the hypotheses listed in `PROVED.md` (copied from the Lean text):
- `ceiling_tree_CG`: t0 = .0117694 (`a0CG` = 58847/5000000). Node-partition tree bound: the I2 paths of each source contain an out-tree of charts over the 230-shape DAG (`cgR`, root `cgr0`), each nested move is charged c2/n(A) per source tree, with the minimum over source counts (|J| ≥ 4962, ≤ 48 partners per source, ≤ 104 sources).
- `ceiling_tree_GD`: t0 = .0116750 (`a0GD` = 467/40000). The same with `|S| ≤ 104`, `Bset ⊆ S`, `48 ≤ |Bset|`: sources in `Bset` use `gbR`/`gbr0` (the shape edges `E48` realised by concrete nested charts), sources in `S \ Bset` use `gaR`/`gar0`.

Both sit on top of `ceiling_native_J` (t0 = .0118103, #7668): on [.0118103, 1] they apply it with its own hypotheses, and on [t0, .0118103] they use two kernel-certified tree pieces. Kernel-checked here: row soundness of three 230-row DP tables (one `decide +kernel` per row, no float, no shrinking), the tree cost bound for any out-tree, the double-counting reduction, the Lagrange line bound, a certificate that the integer move weights lower-bound c2 on the window, and the per-piece numeric certificates. All theorems print only propext, Classical.choice, Quot.sound; no `sorry`, no `native_decide`; every new module was compiled fresh (`CHECK.txt`).

**Scope.** One 104-port set. The 230 shapes, `E48` and the 48-port class were computed for that port set only. Five word files share it (st1, #7637, x1t2a, #7660, and `t7669`, our reproduction of the word of #7669, not that file); the word-level numbers in `NATIVES.md` are for these five.

**Hypotheses.** All new hypotheses are in `PROVED.md`. In short:
- Binders: the 32 explicit binders shared with `ceiling_native_J` (after the implicit `{ι : Type*} [DecidableEq ι]`) are textually identical to that theorem; new are `σ ρ μ`, `T : TreeData`, and `hcstMonoT`, `hcst0`, `hcst1`, `hP1`, `hP2`.
- `cstF` premises: `hcstMonoT` (monotone on [a0, 1/10]), `hcst0`, `hcst1` (two brackets at the new breakpoints).
- `TreeData` fields: `hJS`, `hScard`, `hfib`, `hJcard`, `hB`, `hBcard` (`48 ≤ |Bset|` in GD), `hcell`, `hxk`, `htreeA`, `htreeB`, `hnd`, `hMv`, `hcap`, `hMsub` (`Mv ⊆ Mreg ∪ Mun`), `hdim` (`1 ≤ dA < dB ≤ 8`).
- **Tree premises** `Tr` out-trees (`htreeA`, `htreeB`), `hcap`, `hnd`, `hP1`, `hP2`, `hcell`: open hypotheses, **not verified on any word** (no script was run for them). They are new statements, not consequences of `hcong`, although they rest on the same families (nested moves, I2 capacity, I2 charge). `T`, `T.J` and `J` are separate abstract objects.

**Caveats, stated plainly.**
- Earlier (non-Lean) computations gave .0117604 and .0116675 using measured count profiles. The digits certified here are weaker by 9.0e-6 (.0117694 − .0117604) and 7.5e-6 (.0116750 − .0116675), because Lean takes only the stated counts. The certificate generator reported negative margins one digit lower (.0117693, .0116749); that is a generator output, not a Lean statement.
- The count behind `E48` (the (3,4,12) and (5,8,6) charts cover only 1,344 of the 4,992 even cells) is neither in Lean nor script-checked for this package. `NATIVES.md` recomputes the realised edge sets with an independent program (`e48.c`: all 29,212 subspaces, 2,350,136 nested pairs, all 4,992 even cells): three port classes of 24, 32 and 48 ports, and the 48-port class equals the `gbR` mask exactly (`cmp.py`); `cgR` has the same shapes and masks as `gaR` (`cgcmp.py`).
- Word-level premises are computed by programs that are not in the package (`NATIVES.md`: premise × word table). `aud.py` replays modulo two primes (2^61 − 1 and 2^64 − 59); the others are exact integer or rational computations. `aud2d.py` was reused from #7668, as were the `aud2a.py` entries for st1, w7637, x1t2a and the `hc12.py` entries for all words but `t7669`. The owned layers agree in mass 56/56 but not in shape: `t7669` has 23 rises / 23 descents and `len ks` = 36, the other four 23 / 24 and 37. Everything inherited from #7668 keeps its status there (`hcong`, `hdist`, `hspMono`, `hcstMono`, the brackets, the 8-row decoder constants; the bound |J| ≥ 4962 is a conjecture outside the known words).
- The hypotheses lists in `README.md` and `PROVED.md` are generated from the Lean binders (`gendocs.py`, `hyps.py`).
- `CHECK.txt`: the 148 new modules were compiled fresh, one at a time under a 3.5 GB guard. The 46 modules inherited from #7668 were not rebuilt for this package; their oleans are those of #7668's build of the same sources (prebuilt oleans).

The premises under study are SYLforge's (#7616, #7620); the caller is rohanarun's (#7113). DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
