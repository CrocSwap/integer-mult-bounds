# Fifteen-owner equality can have four six-cycles

**A finite graph classification with a written coverage proof; no new kappa.**

The fifteen-owner equality hypotheses do **not** force girth eight.
[WITNESS.json](WITNESS.json) gives a connected cubic bipartite graph on 15+15
vertices with no four-cycles and exactly four vertex-disjoint six-cycles.
Moreover, every graph under these hypotheses containing a six-cycle is
isomorphic to this witness. Thus the possible six-cycle counts are exactly
**0 and 4**; counts 2, 3 and 5 do not occur. The known zero-cycle example
retains predecessor credit; its uniqueness is not a new claim here.

This resolves the explicit remaining question in Nick Petalas's
[PR5182](https://github.com/CrocSwap/integer-mult-bounds/pull/5182), whose
structural result excluded one six-cycle but left counts 2–5 open. The
[released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145292)
and our [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/3062#discussioncomment-19145989)
record the scope. Future actual-route searches cannot discard the six-cycle
case on the basis of these abstract hypotheses alone.

## Proof and exact evidence

[PROOF.md](PROOF.md) gives the complete reduction around a distinguished C6.
Three matching sizes in {1,2}, six small attachment choices and a free 3-by-3
Boolean block specify every possible graph with a C6. Relabeling reduces
the domain to 2,997 attachment patterns and 4,309 cubic completions. Exactly
1,428 are C4-free and 16 meet the C6 cap. Sixteen explicitly listed vertex
permutations identify the entire survivor set with one witness.

Two separately implemented checks corroborate the computation:

- `independent.py` keeps all eight matching-size patterns and every free-side
  labeling: 91,125 attachment patterns, 134,469 cubic completions, 42,948
  C4-free graphs and 432 admissible labeled graphs. Every survivor has four
  C6s and receives a literal cycle-walk check. It uses adjacency-walk counts
  rather than the primary triple-intersection predicate.
- `literal_check.py` checks the displayed witness by all-root simple-path
  DFS, including exact cycles, disjointness, connectedness and the nonzero
  signed defect from PR5182. It also checks the predecessor's classical
  duad/perfect-matching positive control and malformed, omitted-cycle,
  omitted-root and degree-preserving-switch controls.

The universal coverage rests on the written reduction. Program agreement
alone is not a completeness argument. The explicit counterexample is
independently checkable even without accepting the classification proof.
Substantial AI assistance, including separate Luna supporting implementations,
is disclosed; no independent human or proof-kernel review is claimed.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py --package research/centre-equality-six-cycles
```

The manifest runs all three standalone verifiers in ordinary and optimized
mode. Each prints deterministic JSON and writes no files. Expected markers
include `PASS_CENTRE_EQUALITY_SIX_CYCLES` and the runner's
`PASS_REGISTERED_RESEARCH_PACKAGE`. The same three scripts run directly in a
Git-free export. Publication-byte, source-history, export and mutation-check
evidence is recorded in the PR; CI execution is separate from scientific
acceptance. There are no network or third-party solver dependencies.

## Scope, sources and credit

This is a scoped override of the `centre-path-sharing` card to its abstract
equality obstruction. The original card, selected context and exact base
`ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c` are retained in
[TASK.json](TASK.json) and [SOURCES.json](SOURCES.json), priority revision 7.
The mathematical predecessor files are cited provenance, not imported
executables or replayed censuses. No frozen package is modified.

| Predecessor | Exact head | Retained contribution |
|---|---|---|
| Sagar Thakrar, [#3291](https://github.com/CrocSwap/integer-mult-bounds/pull/3291) | `5d027c3c8724aec4501e0e2876388bebefa00ef7` | Sharp abstract fifteen-owner floor, local path inequality and duad example; `research/centre-block-moore-bound/PROOF.md` |
| Nick Petalas, [#5182](https://github.com/CrocSwap/integer-mult-bounds/pull/5182) | `a4a8956cb9c769cddd593d00b4c294d307b5fac5` | Cubic equality reduction, disjoint cycles, signed defect and exclusion of one C6; `research/centre-fifteen-owner-equality/PROOF.md` |

PR5182's proof was inspected at SHA256
`c73687ff86616e90db6828726745e6dcc22bfffeca6fcec0d728958f5b9dc9c4`.
It is an explicit citation; the cited Git commit is not a runtime dependency.
Also retain Matarener #3656, dcharb78 #3147, Ross Richardson #3071,
Gonzalo Mier #3097, Sudarsh Chaturvedi #3168, Aaron Wang/navinor, ywz65 and
their original selected-source lineage. The new work is the realized
six-cycle example and complete classification of the nonzero-cycle branch,
not a re-audit of their route censuses, lower bounds or physical models.

Actual route labels and scalar coefficient equations remain unconstructed.
Acquisition, routing, arbitrary dirty restoration, frames, hosting, precision,
stock, recursive costs, all-size compilation and outer transfer remain
outside this result. There is no supplier-admission, new-kappa or
selected-frontier claim. No literature priority for the abstract graph is
asserted. Prepared for Krzysztof Wójt with substantial OpenAI Codex assistance;
Apache-2.0, with predecessor attribution retained.

## Open next questions

Can the displayed graph with four six-cycles carry the actual selected route labels
and scalar coefficient equations? It is now a necessary second branch beside
the zero-cycle incidence. A first step is to impose the exact six-edge route
relations on these four cycles and the remaining edges, then solve the
coefficient compatibility equations. The graph alone does not satisfy those
contracts, and a physical construction needs a complete favorable cost and
restoration budget before expansion. This task is unreserved.
