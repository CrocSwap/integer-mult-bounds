# Conditional κ = 0.003645669928698 from a terminal-cut rechart

The exact native operator and both complete directed price engines improve
[#7274](https://github.com/CrocSwap/integer-mult-bounds/pull/7274) at
`ff79af7a208132e16d51ceca3e1428444894367e` by **0.000000196706982**.
This is a conditional proposed bound, with the same signed 17-stage caller and
five framework assumptions. Full verification is initially pending in this draft.

The change moves 24 scalar/ownership events and two helper outputs from chart 245
to chart 127, preserving every normalized scalar event and its order. Rebuilding
all transports removes one paid movement. Per native, the productive change is
`T8 -2, T9 +2`; the paid change is `P1 -1, P4 -3, P5 +3`.
The complete signed invoice has 22,461 productive positions, 110,536 paid
positions, rank surplus 1,424 and zero empty-root credits. See [PROOF.md](PROOF.md).

`source.py` authenticates the complete exact 7274 package, including every nested
archive, reconstructs its word from exact 7244, and supplies the retained engines.
`construct.py` reconstructs the entire new word from [WITNESS.json](WITNESS.json).
[EARLY-RESULT.json](EARLY-RESULT.json) records the source-bound exact operator and
complete pricing gate. [VERIFY.json](VERIFY.json) registers the remaining native,
caller and frontier checks; they will be frozen and replayed before ready status.

Run `python3 -I -B research/p104-terminal-cut-rechart/verify_early.py`.
Once all receipts exist, run
`python3 scripts/research_package.py --package research/p104-terminal-cut-rechart`.

The five inherited assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`. Local/hosted scientific
checks do not establish independent human or formal acceptance or maintainer
selection. Selected records are unchanged. [TASK.json](TASK.json) contains the
original task card, changed scope and open next questions. The packing relaxation
in the early receipt is a scoped upper bound, not a claim of a global optimum.

## Open next questions

Complete and independently review the registered source-aware replay for frontier
selection. For a later improvement, pin this exact word and test a different
coupled timing/boundary change with the full invoice; the discovery search ending
at an existing-frame local optimum proves no universal barrier.

Prepared by Rohan Arun with substantial OpenAI Codex assistance, Apache-2.0.
Retains Clear1nsight's 7274/7244 construction, dillona's 7161 and 7155 lineage,
Rohan Arun's 7156 and 7113 caller, and all Ali Romman, CubeJerry, ToikY,
DreamingOfClouds and other inherited notices. See [NOTICE](NOTICE) and the complete
source archive. The floating search only nominated this exact witness.
