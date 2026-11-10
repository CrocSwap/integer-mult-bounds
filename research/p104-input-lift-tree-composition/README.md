# Conditional kappa 0.00314980 from the lifted source in the binary tree

This package composes the four input lifts in [PR6349](https://github.com/CrocSwap/integer-mult-bounds/pull/6349)
with the binary query tree in [PR6348](https://github.com/CrocSwap/integer-mult-bounds/pull/6348).
The new conditional claim is **kappa 0.00314980**, an increase of **0.00000047
(approximately 0.0149 percent)** over PR6348. This is a small gain. The donor's
one-percent breakthrough target remains unmet.

The tree has 19 native calls, 16 thin queries and 16 paired whole idles. Its
caller word is unchanged. The exact local source has 770 public inputs and
17,452 events. The complete composition has 70,542 paid jobs, 14,214 productive
jobs and rank-mass surplus 808. All four helper target debits are included.
[PROOF.md](PROOF.md) states the interface and complete signed changes.

The verifier regenerates the source word and caller, checks all arbitrary input
columns and native phases, counts the full invoice, and uses two rational price
engines. It also checks the completion, compiler and all 58 outer predicates.
[RESULT.json](RESULT.json) is the complete retained receipt.
[VALIDATION.md](VALIDATION.md) records which publication checks have run.

```sh
python3.12 -B scripts/research_package.py --package research/p104-input-lift-tree-composition
python3.12 -I -B research/p104-input-lift-tree-composition/verify.py
python3.12 -I -O -B research/p104-input-lift-tree-composition/verify.py
```

Expected status: `PASS_P104_INPUT_LIFT_TREE_KAPPA_00314980`.

The five inherited framework assumptions remain. The uniform word and rounded
multiplier are not materialized. Hosted CI and independent scientific review
are distinct from author replay. No selected-frontier change is made.

## Open next questions

- Independently check the source/caller interface, independent helper inputs and
  complete signed invoice. Author replay does not establish independent review.
- Test a new exact source or caller only after it passes its own native and
  arbitrary-input checks. The larger target remains open. Structured questions
  and scope boundaries are in [TASK.json](TASK.json).

## Attribution and coordination

Prepared by Ali Romman with substantial OpenAI Codex assistance; no subagents.
The contribution is the complete composition. PR6348 and PR6349 supply the
unchanged constructions. DreamingOfClouds supplies PR6314 with Claude Opus 5.5
assistance. Cinna Davis supplies the query caller and thin-query interface.
[NOTICE](NOTICE) retains the full native, helper, recursion, compiler, BIT and
outer-source credit. Apache-2.0.

[Canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19209322).
[Scope handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19341992).
The active joint input-direction search in Discussion5645 is excluded.
