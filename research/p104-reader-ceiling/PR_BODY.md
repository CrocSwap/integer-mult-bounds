P104: per-reader endpoint charge, frontier-word ceiling κ ≤ .0115428 (Lean, conditional, no κ claim)

Lean-only package, builds on #7678 (the tree ceiling, t0 = .0116750): the four #7678 modules the new files import (`CTreeCore`, `CongestionTreeCore`, `CongestionTreeW`, `CongestionTreePiece`) and the 46 modules of #7668 are included unchanged; 274 new modules. No κ claim and no word claim in Lean: every object in the three theorems is abstract, and nothing in Lean ties a word to the hypotheses.

**Results.** Three theorems, each proving, for `t ∈ [t0, 1]` (that is, `t0 ≤ t ≤ 1`), `Finv (1 − t) (invoice (caller 6 7) n 17) < 0` (caller `caller 6 7`, L = 17) under the hypotheses listed in `PROVED.md` (copied from the Lean text). They differ in the bound on one named hypothesis, `ω ≤ w0` (the net G'-token rank that owned rows absorb), which sets the allowance `NDL = 15 + w0`:
- `ceiling_reader_GD_w10` (headline, `CongestionReaderW10`): `ω ≤ 10`, t0 = .0115428 (`a0RF` = 28857/2500000).
- `ceiling_reader_GD` (`CongestionReader`): `ω ≤ 0`, t0 = .0115262 (`a0RD`).
- `ceiling_reader_GD_w16` (`CongestionReaderW16`): `ω ≤ 16`, t0 = .0115528 (`a0RE`).
For comparison `ceiling_tree_GD` (#7678) is .0116750. On `[.0118103, 1]` each applies `ceiling_native_J` with its own hypotheses; on `[t0, .0118103]` it uses two or three kernel-certified `reader_piece`s. Certified digits are 1.1e-6 to 1.2e-6 above the paper digits (.0115417, .0115250, .0115516), because t is quantised to 1e-7 and the line constants and weights are rounded outward. The paper digits are reproduced by the master-LP script (.011541666, .011525001, .011551596). Lean proves: the register identity and `tied_rho` (a register tied to a reader has residual at least `delta = 7^s + 2^s − 8^s − 1`), the payer summation `sum_c2_pay`, the reader line bound `tree_lower_reader`, the piece lemma, soundness of six 230-row DP tables (one `decide +kernel` per row) and all per-piece numerics. All theorems print only propext, Classical.choice, Quot.sound; no `sorry`, no `native_decide`; every new module was compiled fresh (`CHECK.txt`).

**What the charge is.** Each reader (104) that is tied to a distinct public register (Z-class, 0 → 8, or V-class born at dim 1, ending at 9, with a stop at a dim in [2, 7]) adds `delta` to the budget; the readers that are not tied and not fully transported (at most 5 mixed registers, at most 10 owned last movers, plus `ω`) are priced by an allowance of `delta` each.

**Scope.** One 104-port set. Five word files share it (st1, #7637, x1t2a, #7660, and `t7669`, our reproduction of the word of #7669, not that file); the word-level numbers in `NATIVES.md` are for these five.

**Hypotheses.** All in `PROVED.md`. The 32 explicit binders shared with `ceiling_native_J` are textually identical to that theorem and to `ceiling_tree_GD` (compared by script). New or changed: `T : TreeData` (now the readers' tables), `hcstLo`, `hcstMonoT`, `hcst0`, `hcst1` (and `hcst2` in `ceiling_reader_GD`), `hP1`, `hP2` on the new window, `ω`, `hω`, `Q`, `Uo`, `hUo`, `hUc`, `hQ`, `hcase`, `π`, `hπR`, `hπinj`, `hTied`.
- **`ω ≤ 10` is proved on paper but is a named hypothesis in Lean.** Premises of the paper proof: no owned register rises from dim ≤ 7 into V, every owned lifetime ends in a CLEAR; both hold on all five words, where `ω = 0` (exact replay modulo two primes). The CLEAR certificates are not wired into this package.
- **`hTied`, `hcase`, `hUc`: open (paper).** `tied_rho` is proved, so the residual bound is not a hypothesis; the existence and uniqueness of a tied register per tied reader is. On all five words every reader has a Lean-`Tied` register on its final chart and a maximum matching of readers to registers has size 104 / 104.
- **`T` (IN side) is open.** The IN DP table is the reflection of the OUT table (paper); the Lean-kernel IN table rfiR differs from gbR in the edge masks of 89 of 230 rows (dim, n, m agree in all 230; the numeric g/ge lists differ in 225 rows); rfaR and gaR have identical masks (corrected; an earlier version of this text said 18 of 230). After opening, the IN-side reader trees were extracted from all five words and every word-checkable IN-side premise passes (two primes; see `NATIVES.md`); the OUT-side tree premises of #7678 were re-checked on all five words (both primes).
- `hcstLo : 0 ≤ cstF` on `[a0, 1/10]` is a hypothesis; on paper it follows from `cst(t) ≥ c2(7, 8) > 0`.

**Caveats, stated plainly.**
- The F2 lemma as first posed (a paying register inside the reader's visit set) is false: a five-register token-swap counterexample exists. The statements use the corrected count form (payers ≥ N_high − 15 − ω), proved on paper for the class; Lean uses only the existence of a tied register per tied reader and the count bound on `Uo`. The clause "only public registers hold G' tokens" is false on the natives (15 to 28 owned registers hold tokens) and is not used.
- The 5-allowance paper figure (.0115086) is not formalised: owned moves can end at dim-8 charts without a public payer, so 10 owned last movers are added (NDL = 15).
- The word-level premises are computed by scripts that are not in the package (`NATIVES.md`: premise × word table, methods, which were re-run). Nothing in Lean ties a word to the hypotheses. `hmix = 5` is tight on all five words; the five words are close to one data point (one port set).
- The Lean-certified digits are weaker than the paper digits by about 1.1e-6 to 1.2e-6.
- The docstrings of the final modules had a wrong digit for t0 in the working copy; corrected in this package (comments only).
- `CHECK.txt`: all 274 new modules were compiled fresh, one at a time under a 3.5 GB guard. The 50 inherited modules were not rebuilt; their oleans are those of the build of #7678's package (same sources).

The premises under study are SYLforge's (#7616, #7620); the caller is rohanarun's (#7113). DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
