# Exact scalar-shadow row recurrence

**A universal interface lemma; no new multiplication bound or κ is claimed.**
For any semiring `K`, register type `ι` with decidable equality, label type `Λ`,
finite event prefix `es`, appended event `e`, and row/column indices `r,j`,
`S_append_event` gives the exact update to row `r` of the scalar-shadow matrix
`S (es ++ [e])`. It handles all five `LemmaG.Event` constructors:

| Appended event | Updated scalar-shadow row |
|---|---|
| `relabel _ _ _` | unchanged |
| `add t s q` | row `t` becomes row `t + q · row s` |
| `scale t q` | row `t` becomes `q · row t` |
| `copy c s _` | row `c` becomes row `s` |
| `clear c _` | row `c` becomes zero |

The Lean theorem is universal over every finite prefix and every coefficient in
`K`; it assumes no field, commutativity, label admissibility, exact recipe,
finite register count, or selected-word hypothesis. `scalRun_append` proves the
event-order composition used by the recurrence. The proof reduces each case to
Lemma G's scalar event semantics and is checked by Lean's kernel.

## Why this interface matters

The hyperplane-ended helper theorem in
[`hyperplane-end-lean/PROOF.md`](../hyperplane-end-lean/PROOF.md) takes a unit-row
certificate `hS` as an instance hypothesis. This recurrence makes the exact
row-by-row update available as a proved Lean interface, so a future source-bound
word proof can derive `hS` by composing its event trace instead of treating the
matrix update as an external implementation convention.

This result does **not** instantiate the recurrence on a complete emitted
helper, prove any particular `hS`, discharge the recipe or footprint hypotheses,
or change the selected exponent. The complete emitted-word-to-Lean event binding
and supplier obligations remain separate.

## Reproduce

From this directory, with Lean 4.21.0 and network access for Mathlib's cache:

```sh
lake exe cache get
lake build
lake env lean PrintAxioms.lean
```

From the repository root, the registered replay and metadata check are:

```sh
python3 -B scripts/research_package.py --package research/stream-shadow-row-update --check-only
python3 -B scripts/research_package.py --package research/stream-shadow-row-update
```

The package uses Mathlib v4.21.0 and the local, source-pinned Lemma G package.
`SOURCES.json` pins the exact interface and hyperplane-end hypotheses at the
base commit. No numerical experiment is used as proof evidence.

## Open next questions

Can `S_append_event` derive the unit-row hypothesis for one complete,
source-pinned emitted helper? This would connect a concrete event transcript to
the `hS` premise used by the hyperplane-end theorem. First bind the emitted
events and their ordering to Lean `Event` values, then fold the recurrence and
prove the resulting row equals the basis row. The binding from serialized
records to Lean events is the remaining blocker; this package does not attempt
that bridge.

## Credit

The scalar-shadow semantics and `S` matrix are from Lemma G, PR #484, authored
by DreamingOfClouds with Claude Opus 5.5 assistance, and retained in the
source-pinned `e8-lemma-g-lean` package. This contribution adds only the
left-to-right composition and one-event row recurrence. Prepared by
1337isnot1337 with OpenAI Codex assistance. Apache-2.0.
