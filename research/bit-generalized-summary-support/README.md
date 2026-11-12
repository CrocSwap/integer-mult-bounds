# Generalized support bounds for joint BIT summary replacements

**NO VERIFIED GAIN.** On the exact selected paired #7001 word,
no six- through nine-summary replacement under the fixed monotone
catalogue can save the target 5/3 paid units per native copy.
The final profile has ten rank-six collectors and one rank-one
collector. It fails even with an arbitrary extra line.

The summary code has minimum two-dimensional support 75 and
111 distinct nonzero columns. The proof combines generalized
support, column incidence and a projected rank test on all
16,110 distinct rank-six chart pairs. [Proof](PROOF.md)

## Replay

Use a clean checkout and CPython 3.12.

```sh
python3.12 -B scripts/research_package.py --package research/bit-generalized-summary-support
```

The verifier reconstructs the weights and chart masks from the
canonical pinned BIT word, exhausts the four histogram domains,
and checks all pair exclusions by rank of the uncovered columns,
including the effect of deleting any one column. Positive and
negative projection controls run from the same word.
The exact dependency is the existing selected BIT word. [Selected BIT package](../paired-query-only-bit/README.md)

## Scope and credit

[#7146](https://github.com/CrocSwap/integer-mult-bounds/pull/7146)
covers up to four summaries and the five-summary target scope.
This package covers larger joint changes with different support
bounds. Ali Romman's #5421 supplied the owned relations.
DreamingOfClouds, zxv, CubeJerry and the retained authors supplied
the native and paired-controller lineage. Substantial OpenAI Codex
and subagent assistance. Apache-2.0.

## Open next questions

Can an existing public MOVE be redirected to import a summary
row across a nonmonotone chart change? Start with a nested,
equal-paid-rank redirect in the literal word. Check source
availability, exact output rows and restoration before recomputing
the paid and ordinary invoices. This proof fixes monotone public
transport, so that changed source flow is outside its scope.
