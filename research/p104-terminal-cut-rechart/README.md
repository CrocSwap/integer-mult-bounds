# Conditional κ = 0.003645669928698 from a terminal-cut rechart

The exact native operator and both complete directed price engines improve
[#7274](https://github.com/CrocSwap/integer-mult-bounds/pull/7274) at
`ff79af7a208132e16d51ceca3e1428444894367e` by **0.000000196706982**.
This is a conditional proposed bound, with the same signed 17-stage caller and
five framework assumptions. All direct early, full native, full caller and frontier checks passed locally.
All four registered commands also passed against unchanged scientific files.
The replay used two invocations after a sparse-checkout interruption, documented
fully in [REPLAY.txt](REPLAY.txt) and [REPLAY-INTEGRITY.json](REPLAY-INTEGRITY.json).

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
complete pricing gate. [VERIFY.json](VERIFY.json) registers the early, native, caller and frontier checks. The full receipts are
[NATIVE-RESULT.json](NATIVE-RESULT.json), [RESULT.json](RESULT.json), and
[PROPOSED-CLAIM.json](PROPOSED-CLAIM.json). The caller verifies all 3,036 physical
maps, 104 boundaries, 54 strict and four functional outer predicates, ordinary
cost 782,522,276 below 10^9, and precision coefficient 2,430. All native owned
lifetimes, peak, and ascent mass are preserved; the fresh grid is 1,125 / F25.

Run `python3 -I -B research/p104-terminal-cut-rechart/verify_early.py`.
To reproduce all registered stages, run
`python3 scripts/research_package.py --package research/p104-terminal-cut-rechart`.

The five inherited assumptions remain `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`. Local/hosted scientific
checks do not establish independent human or formal acceptance or maintainer
selection. Selected records are unchanged. [TASK.json](TASK.json) contains the
original task card, changed scope and open next questions. For fixed productive profile, 17 native words and ambient-145 remainder mass,
the retained packing relaxation gives a crossing in [0.00580766609709,
0.00580766609756], leaving about 0.002161996168 of relaxed headroom. This is
a scoped upper bound, not a claim of a global optimum.

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

The branch also retains the exact upstream [#7257](https://github.com/CrocSwap/integer-mult-bounds/pull/7257)
navigation/historical-replay prerequisites with original author credit. The six
navigation tests pass locally. The separate historical audit is left to hosted
CI because the local partial clone cannot supply its shared-clone objects; it is
not counted as a local pass. Selected records are unchanged.
