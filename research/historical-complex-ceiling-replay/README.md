# Reproduce the historical complex-ceiling control without changing selection

**Tooling repair; no new mathematical bound or supplier.** This package runs
Douglas Colkitt's unchanged PR1240 ceiling checker against its exact #1094
selected record and #1042 comparison. It restores a runnable scientific
positive control for four research cards while preserving all predecessor
bytes and the current selected frontier.

At base `7c472563474e60185e6ca101a17622133d047e56`, priority revision 7,
`complex-rank-shape-decoder`, `complex-new-helper-inventory`,
`centre-path-sharing` and `coverage-law-change` still start with
`research/complex-local-word-ceiling/verify.py`. With its inputs materialized,
that command raises `KeyError: 'complex_profile'`: selected #4470's certificate
has a productive-helper schema. The [existing handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19132013)
already identified this mismatch. This contribution adds the actual historical
replay route; it does not claim to discover the mismatch.

The original checker reproduces exactly:

```text
PASS_COMPLEX_LOCAL_WORD_CEILING a_ceiling 0.00169005410908900006 kappa<= 0.0016872026453254019
```

Those values describe **the #1094 model**. The selected conditional #4470 value
at this base is 0.00302015, under a different construction and accounting.
For current orientation run `python3 -B scripts/research_selected_baseline.py`
after materializing its source closure. A historical ceiling or lever budget
must not be applied to that current contract without a new applicable cost law.

## Exact source and execution boundary

The nine-file executable closure comprises the original `verify.py`,
`ceiling.py`, `RESULT.json`, `SOURCES.json`, two #1094 audit inputs, the #1042
checkpoint and assembly, and the historical selected record. Every file is
SHA256-authenticated before any predecessor code runs. The three live input
pins in the original `SOURCES.json` are then independently reconciled with
that payload. The added #1042 pins also bind the actual predecessor comparison.

The retained [historical-selected.json](historical-selected.json) is the exact
`certificates/selected-result.json` blob `ae6a99f28aa468649eb66a361e764d769363bf11`
at original base `e3bb23b4c6bae16ba277f9443e11257a0a37780a`, with SHA256
`10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`.
Its original Git path is a provenance pin in [SOURCES.json](SOURCES.json);
the package-owned copy is authenticated by the wrapper and exported with it.
The current `certificates/checkpoints/frontier1094.json` has SHA256
`bb2eaa58647b353f88d0aec2eafb9d30df1be53589231b23e12ceef3e4bad129`.
It is byte-distinct and is not silently substituted for the old pin.

Only the retained selected record is relocated, to its original path **inside
a fresh temporary tree**. All other inputs keep their paths and bytes. The
wrapper executes the unchanged checker as a separate isolated Python process,
preserving an explicitly requested `-O` level. It copies no bytecode or unrelated
repository files, uses a 90-second child timeout and never passes `--write`.
The original checker retains its exact `RESULT.json` comparison, #1042 check,
coverage and moment calculations and four original failure/dominance controls.

The wrapper requires successful exit and the complete expected stdout, compares
all temporary input bytes after the positive replay, reauthenticates original
inputs at return, and checks the live selected record is unchanged when present.
The standalone verifier requires no Git, network or third-party dependencies.
The generic metadata command does use Git to authenticate provenance. In a
shallow checkout, fetch the public original base explicitly if it is absent:

```sh
git fetch --depth 1 --no-tags https://github.com/CrocSwap/integer-mult-bounds.git e3bb23b4c6bae16ba277f9443e11257a0a37780a
```

This fetch is not a full-history ancestry audit. A committed Git-free export
contains everything needed for the standalone replay and avoids that lookup.

## Reproduce and rejection coverage

From the repository root, CPython 3.12 and the standard library:

```sh
python3 -B scripts/research_package.py --package research/historical-complex-ceiling-replay --check-only
python3 -B scripts/research_package.py --package research/historical-complex-ceiling-replay
```

The registered commands run both normal and optimized modes. Direct commands
also work from an exported tree:

```sh
python3 -I -W error -B research/historical-complex-ceiling-replay/verify.py
python3 -I -W error -O -B research/historical-complex-ceiling-replay/verify.py
```

Each mode includes:

- The entire unchanged historical positive replay and its four original controls.
- Eighteen source-integrity controls: individually corrupt and remove every one
  of the nine inputs, requiring the specific input's rejection.
- Three scientific-data controls in separate disposable trees. A changed owner
  profile rejects with `profile mismatch`; an impossible #1042 endpoint rejects
  with `previous endpoint above the ceiling`; a changed expected receipt rejects
  with `RESULT.json differs`. These intentionally bypass only the wrapper's
  earlier hash gate to test the unchanged scientific checker itself.
- Exact preservation of all source inputs and the live selected record.

The final line is
`PASS_HISTORICAL_COMPLEX_CEILING_REPLAY context=PR1094 current_supplier_bound=false inputs=9 input_controls=18 scientific_controls=3 unchanged=true`.
The PR and [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/4458#discussioncomment-19152822)
record measured runs, committed/export checks and hosted status. No full selected
cold replay, Lean, Docker, new cost law, independent human review or proof-kernel
acceptance is claimed. The underlying historical theorem keeps its original
scope and proof dependencies.

## Task choice, overlap and credit

The picker selected `complex-rank-shape-decoder` with nonce
`3d916505ccc35c2632298bca8333380c`. [TASK.json](TASK.json) explicitly changes the
scope from decoder synthesis to this first-step reproducibility repair. Its
original card and originating catalogue remain pinned. The standing procedure
links this route without changing the catalogue, allocation, frozen checkers
or scientific receipts. This complements #4906's generic-baseline navigation;
that change deliberately left named scientific replay commands alone.

Entry overlap covered 304 open PR bodies and 4,625 Discussion records with
complete remote pagination at 18:55/18:57 UTC on October 23, 2026. Local note
coverage was sparse (9 of 7,267 tracked paths); directly relevant packages,
guidance, #4458/#1166 and targeted all-state PR searches were inspected.
Arbitrary diffs, omitted unrelated notes and unpublished work were not covered.
No claim of global novelty follows from these searches.

Credit Douglas Colkitt and the original credited Claude assistance for PR1240,
the PR1012 coverage identity, and the #1094/#1042 construction and audit authors
retained in the original package. Mihir Srivastava's #4463/#4906 supply the
current-schema orientation and generic startup routing; lee-phys's #4631 and
the retained #4936/#5050 contributors supply sparse and source-loading follow-ups.
Dennis's existing historical-check replay and all repository workflow tools
retain their original credit. This focused copy needs only nine inputs; it
does not change those shared tools or their historical configurations.

Prepared by Mihir Srivastava (@mihir-s-05) with substantial OpenAI Codex assistance
in inspection, implementation, documentation and verification; no subagents.
Apache-2.0. This is author-checked tooling evidence, not scientific approval.

## Open next questions

1. **Bind a current helper-inventory cost law.** Authenticate the selected closure
   with `research_selected_baseline.py`, then derive the actual paid completion,
   compiler and outer guard for a named changed invoice. This matters because
   the historical cap is inapplicable to #4470. The missing complete law and
   consumer bill are blockers; this replay does not supply them.
2. **Migrate the four emitted historical first steps.** Extend the exact-path
   dependency inventory in [the startup compatibility note](../../docs/research/task-startup-compatibility.md)
   before editing the pinned catalogue. Users who skip the standing procedure
   still see the legacy command. Preserving historical task/source receipts
   requires a separate migration decision; no catalogue repin is included here.
