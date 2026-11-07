Title: Prove no subset of ≥97 E8 lines has a rank-8 complex realisation (minimum hitting set 24, spectral + local certificate; no κ)

No κ claim. This adds `research/p104-e8-rank8-closure/`, a registered research package for the card `p104-side-correction`. It extends the 14-port
Hall obstruction of #6846 from the 104 ports of one word to every subset of the 120 E8 lines.

**Result.** Assume the complex label pattern of #6846: each line `T` carries `k × d` label matrices `U_T, W_T` over a field, the pairing `W_S U_T^T`
vanishes on every non-orthogonal pair of lines, and every diagonal block is invertible. Then no set of 97 or more of the 120 E8 lines has a
realisation of inner dimension exactly `8k`, over any field. The minimum number of lines meeting every member of the 13-line witness family is exactly 24
(the family has 1,209,600 members: an 8-clique of the forced-zero graph plus five pair lines on four of its coordinates, each Hall-deficient with `lam <= 4/5`).

**Proof.** (1) The forced-zero graph is SRG(120,56,28,24) and `M = 2A + 8I − J` satisfies `M² = 24M`, so any 23-line set contains at least 87 forced-zero
edges. (2) A local lemma at one line (a CNF with 998 variables whose unsatisfiability is certified by a DRAT proof that `drat-trim` verifies) says that a hitting set of at
most 23 lines that avoids a line `x` contains at least 12 of `x`'s 56 neighbours; nine E8 reflections carry it to every line, and a direct run at each of the 120 lines agrees.
(3) Counting edges between a 23-line hitting set and its 97 complement lines gives `97·12 = 1164 > 56·23 − 2·87 = 1114`. A 24-line set meets every witness with equality in both bounds, so 24 is exact.

**Checks.** `check.py` (standard library, about a minute) regenerates the lines, the graph, the spectral identity, all 1,209,600 witnesses with a Hall-deficiency test on
each instance (sha256 pinned), a `k = 1` exhaustive control over F2 and F3, the reflections, the local CNF (sha256 pinned) and the retained proof (sha256 pinned), the counting inequality and the
24-line set. `./verify.sh --drat` also runs `drat-trim` on the retained proof (`s VERIFIED`).

**Scope.** The label pattern is a hypothesis. Only subsets of the 120 E8 lines with this mask are covered; ranks strictly between `8k` and `9k`, other masks,
and sets of at most 96 lines are not covered (a 96-line set avoiding the family exists). Nothing is priced. Open questions are listed in the package.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
