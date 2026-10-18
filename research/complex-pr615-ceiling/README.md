# Exact ceiling for the PR615 supplier family

Every 72-call choice of PR615's two native suppliers, and every whole-helper packing into its fixed owner capacity inventory, has conditional κ below

`1628658892827744394867 / 1001628658892827744394867`

under the inherited native moment and outer conversion. This is less than **0.001626010676080313339617167**. The proof allows arbitrary call times as a relaxation and includes fragmented idle capacity. It uses integer pattern weights and rational interval arithmetic, without a solver. See [PROOF-CEILING.md](PROOF-CEILING.md).

The same construction certifies **κ = 0.001626010676080313339567** on a finer output grid. This improves the printed PR615 value by exactly `339567/10^24`, entirely through rounding. No native word, recipe, owner assignment, moment endpoint, bootstrap step, or strict outer inequality changes. The next-grid negative control now rejects the next `10^-24` tick. The certified value is within `51/10^24` of the family ceiling.

This is a ceiling for a specific construction family and proof interface. It does not bound other suppliers, geometries, compilers, moment inequalities, outer conversions, or multiplication algorithms. It does not establish κ = 1 or remove any inherited all-size assumption.

## Reproduce

Python 3.11+ and a C++ compiler with Boost headers are required by the inherited full replay. All pinned source files are bundled; no source downloads or Python packages are needed.

```sh
bash research/complex-pr615-ceiling/verify.sh /tmp/pr615-ceiling-fresh
```

The output directory must not exist. The wrapper checks declarations, runs the unchanged primary verifier with fresh baseline and local constructions, then runs the exact ceiling and independent outer-refinement checks. The ceiling checker remains active under `python -I -O`; the inherited primary and outer checkers require assertions. Package and source hashes are checked before replay.

The primary result retains the PR615 dispatch (68 JP8, 4 ATM3), local programs and paid profile `{1:179504, 2:24192, 3:33248, 4:13408, 5:5040, 6:2016, 8:576, 48:2032}`. Comparison files preserve the original PR615 assembly and assembly source. Historical documentation is under `history/`; its optimization claims and old invocation paths are historical, not the new ceiling proof.

The construction source is [PR615](https://github.com/CrocSwap/integer-mult-bounds/pull/615), frozen at `bf8a49a34350599763cced8592db81dc62c2c1c0`. Construction credit belongs to jeremykothe2, DreamingOfClouds, and the earlier contributors identified in [NOTICE.md](NOTICE.md). The exact ceiling and fine-grid refinement were prepared with OpenAI Codex. A four-branch fresh-context search selected the refinement; this was an application of [Fork, Select and Continue](https://arxiv.org/html/2610.07447v1), not a controlled efficiency comparison or a reproduction of the paper's scheduling benchmark.
