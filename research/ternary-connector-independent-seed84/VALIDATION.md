# Validation record

Local verification on 2026-10-13, starting at 23:08 UTC, from exact base
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

The complete new replay passes on CPython 3.14.8 and on CPython 3.11.15 with
`-I -O -B`. There are no runtime dependencies beyond the standard library.

```sh
python3 -I -O -B research/ternary-connector-independent-seed84/verify.py
```

Expected result:

```
PASS_TERNARY_CONNECTOR_INDEPENDENT matrices=19683 obstructed_minimum=13 orbit_replays=1728 source_paths=5760 leaf_replays=12 controls=170
```

The complete finite domains are 720 paired source paths and 5040 paths with one
source used three times. The three-read case checks all nondecreasing triples
of source boundaries, with repetition and both common signs. The 19,683 matrix
classification has 288 exceptions to the twelve-query bound, all with six
verified thirteen-query repairs. The receipt preserves exact coverage and trace
digests. No random pruning or time-based partial coverage is used.

The independent exploratory DFS of source-count vectors gave the same six
feasible-path counts `84,84,48,280,280,224` as the shipped permutation/insertion
implementation. This is corroboration of that finite census, not a separate
formal proof of the reduction.

All 170 mathematical controls pass with assertions disabled. External package
checks also passed:

- Relocated replay from an unrelated working directory with package and pinned
  inputs read-only.
- Three changed receipt fields, a changed receipt word sign, a changed source
  certificate and a missing source certificate each reject.
- Deterministic `--emit` output agrees with the committed JSON after parsing.
- An unsupported command-line option rejects.
- All eight live-input and historical-context hashes agree with their exact
  base-commit Git blobs. Only the five live sources are runtime inputs; future
  selected-frontier changes do not invalidate this independent result.

The unchanged predecessor command also passes, including its original
characteristic-zero minimum fourteen, 19,683 matrices, 720 source paths,
22 mathematical controls and 308-leaf canonical word:

```sh
python3 -I -O -B research/signed-connector-obstruction/verify.py
```

The selected binding check passes with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY` and the unchanged PR1094 kappa:

```sh
python3 -B scripts/research_baseline.py
```

At 23:13:49 UTC the repository overlap helper completed pagination over 831
open PRs and 76 discussion records, plus 326 local records. Its two matches
were this package and PR944's retained README. A separate connector/fanout
body search inspected nearby work, including @Arham-Tahir64's concurrent
PR1340 at `f1dcab36fa63f8226f70dd07e26f44afb9d39b51`. That contribution adds
temporary F2 source mutations; this one keeps sources read-only and checks
the F3 coefficient-field boundary. No mathematical result from it is used.
The main fetch still resolves to the recorded base. These searches do not
constitute a novelty proof.

The new certificate SHA256 is
`a814ec93439ea36878fd1b6ebd3c19c3151b27e474ca0edc3d0a14c290d82b7c`.
The verifier SHA256 is
`6e25f66fa5057265eac4c88075471ca480acd6a73e56b2add6510a0fc7f40548`.

No full repository suite, selected cold replay, physical supplier/compiler
admission, Lean formalization, runtime benchmark, hosted-CI success or independent
human review is claimed. The optional registered-package hook is not added;
the standard-library command above is the complete bounded replay.
