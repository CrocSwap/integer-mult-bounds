# Multiple-host residual hosting (Task A)

This package proves the abstract multiple-host generalization and recovers the
previous single-host theorem exactly. **It does not establish a physical source
invocation.** That separate obligation is tracked in `../lean-multi-host-source`.

`MultiHosting.lean` retains every selected physical stream and all remaining
observed state. Residuals may act on several hosts during one invocation. The
pending-mask containment and disjointness conditions are checked per host. The
physical adapter quantifies over arbitrary dirty auxiliary inputs and threads
actual auxiliary outputs through subsequent invocations.

`SingleHostRecovery.lean` defines inverse embeddings for a singleton host and
derives the exact previous operator theorem from `MultiHosting.multi_hosting`.
It also recovers the previous physical theorem using its projection lemmas.
`MultiHostControls.lean` proves that cross-host mixing and aliased physical
owners can invalidate a proposed source refinement.

The endpoint contracts remain premises. A host denotes a distinct physical
stream, including its cover owner, with a fixed coordinate chart. Any output
whose equality or restoration matters must be retained. This work supplies no
new bound and does not assume PR448's missing split interface.

## Build

Use official Lean 4.33.0; no Mathlib is needed for Task A:

```sh
python3 research/lean-multi-host-framework/replay.py \
  --lean /path/to/lean-4.33.0-linux/bin/lean \
  --receipt /tmp/multi-host-framework-replay.json
```

The offline replay checks source hashes, builds all six modules from source in
a fresh temporary directory with `lean -t 0`, audits all 21 new named theorem
closures, and requires only `propext` and `Quot.sound` (or no axioms). The three
unchanged dependencies are from `../lean-whole-residual-hosting`. The two
boundary inequalities are checked proofs, not merely failed test executions.

See `REVIEW.md`, `replay-result.json`, `proof-manifest.json`, and
`overlap-audit.json` for review, validation, and exact source versions.

Apache-2.0, following the repository license. Prepared with substantial OpenAI
Codex assistance; the existing WholeHosting authorship and source attribution
are retained in the sibling package and unchanged dependencies.

The [external-review delivery](../lean-external-review/README.md) includes all
three WholeHosting dependencies and both tasks in one patch from the public
base, with a portable source archive and fresh reproduction command. The
human contributor initiated and coordinated the AI-assisted effort; they do
not claim independent derivation or personal checking of the mathematics.
