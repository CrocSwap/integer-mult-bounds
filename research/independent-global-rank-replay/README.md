# Independent replay of two P104 native words

This package replays two existing native words, rebuilds their invoices, and checks them with one script.
The words are the one in #7000 (`research/shared-wire-split-composition`) and the one in #6030
(`research/p104-helper470-twin-rung-removal`). It adds no new construction, no new kappa and no supplier.
Python standard library only, 3.11 to 3.14. Base commit `e54523517d0f03e58352e647c403a5af3e525a57`.

```sh
python3 -I -B research/independent-global-rank-replay/replay.py
python3 -I -B tests/test_independent_global_rank_replay.py
```

Each run ends with `PASS` and takes about 40 seconds. The script compares its output with the committed
`RESULT.json`. Rerun with `--write` to regenerate it.

## What the script checks

1. Every input file matches its sha256 in `SOURCES.json`.
2. A forward replay of each word over exact fractions, with every public input a free symbol. It checks
   frame continuity, that every scalar is nonzero, that every public MOVE goes strictly up in frame, that
   all owned rows are cleared, and that every helper has a positive credit with nested frames.
3. The main rows equal the block the word declares: a unit shear on ordinary ports, the declared mix on the
   other live ports, and the declared hosted pairs.
4. The double-credit test. Every helper row is the identity, no input appears in two helper rows, and no
   helper row reads a main input. Nothing is inferred from a rank count.
5. The paid and target profiles (T and P) rebuilt from the replay and the caller data.
6. One crossing solver for both words. It proves the root is unique on [0, 0.01] by a derivative bound, and
   it refuses empty profiles and rank 0.
7. For #7000: the root is at least the tested value in `FULL-RESULT.json` (checked at the root and by the sign
   of the moment at the tested value).
8. For #6030: a known-answer test. T and P are rebuilt from the replay, including the query term
   (15 query shears times 104 ports on P[1]), and must equal the record exactly. The solver sees only the
   rebuilt profiles. The root must lie in the recorded interval.
9. Seven mutation controls.

## Results

| Item | Value |
|---|---|
| #7000 credit mass per call / paid mass per call | 7650 / 10962 |
| #7000 rank surplus (18 calls) | 1520 |
| #7000 crossing | 0.00363005817468836708593357676489... |
| #7000 tested value / margin | 0.00363005817007, root is 4.6e-12 above |
| #6030 productive / paid / surplus | 13444 / 66834 / 760 |
| #6030 root | 0.00312581155791189724625134438... |
| #6030 recorded interval | (0.00312581155791, 0.00312581155792) |
| Derivative bound on [0, 0.01] | -387072 (#7000), -214612 (#6030), both below 0 |
| Owned erasures of a nonzero field | 53 (#7000), 30 (#6030). Allowed, reported as information. |

Both words pass every check. Both moments change sign many times when ordered by rank (15 and 19 changes),
so Descartes' rule of signs would only bound the number of roots by 15 and 19. Uniqueness comes from the
derivative bound instead: the moment falls strictly on the whole interval, so it has at most one root there.

## Mutation controls

Each control edits the word, or the rebuild, and must be rejected by its target check. The unmutated input
passes that same check in the same run. A control passes only if the target check fails and nothing outside
its listed side effects fails.

| Control | Target check | Also fails |
|---|---|---|
| Insert `ADD 1478 += 759` at event 40637 (frame 660) | double credit | none |
| Flip the scalar of one main-row ADD | main rows | none |
| Insert an ADD with scalar 0 | nonzero scalars | none |
| A public MOVE goes down and back up | public moves up | record profiles |
| Delete a public MOVE | frame chain | record profiles |
| Rebuild #6030 without the query term | P equals record | paid calls, surplus, interval |
| Remove one rank-8 credit per call from #7000 | root at least tested | none |

The first control is the leak that a symbol-renaming alias test missed: with it the per-field credit and the
paid mass do not change, but a helper row stops being the identity and one input is shared.

## What is independent and what is not

Independent of the audited packages: the forward replay, the check list above, the profile rebuild from the
replay, the #6030 known-answer test and the mutation controls. No code from the audited packages is imported.
Their JSON files are read as data.

Not independent:

- The crossing uses the repository's own invoice formula (the sum of (T - P)(r) r^(1-k)). Matching the
  #7000 record is a reproduction of that formula, not a second derivation of it.
- The caller tables are read from the records: `caller.json` for #7000, and for #6030 the main targets,
  idle jobs, port count and the 15 query shears in `RESULT.json`.
- The main-row block is read from the word's own declared parameters (alpha, beta, alpha2, beta2, Dports).
  It catches edits to the word, not a wrong declaration.
- The #7000 record is also used for comparison: its T, P, surplus, bracket and tested value. These are read
  after the solve and never enter it.

## What is not covered

- No claim about kappa, the supplier, the caller identity or the outer gate. Those checks are in the audited
  packages.
- Split tails are not identified from the word. The two proof files name the pivot helper and the cut
  frame. The tail rank is derived from the frames. For helper 450 two helpers (496 and 1479) have the same
  frames and rank, so the unsplit sensitivity in `RESULT.json` uses ranks only.
- The derivative bound uses 70-digit decimal arithmetic with a margin above 2e5, not interval arithmetic.
- Nothing here checks the public/owned MOVE costs against the physical model, only the replayed counts
  against the records.

## Sensitivities (information)

`RESULT.json` lists the #7000 crossing if one field of rank r lost its credit in every call, for each r
from 1 to 9 (rank 2: 0.0035437, rank 8: 0.0032862), and if the two named splits were valued as unsplit
rank-9 helpers (0.0036288). They are derived from the replay output, not from a fixed rank or fixed tuples.
The rank that an aliased tail would lose depends on field order, so all ranks are listed.

## Files

- `replay.py`: the script.
- `RESULT.json`: its output, regenerated with `--write`.
- `SOURCES.json`, `VERIFY.json`, `TASK.json`: inputs and their hashes, replay commands, task record.
- `../../tests/test_independent_global_rank_replay.py`: unit tests plus the full replay with the controls.

## Open next questions

- Can the main-row block be checked against the symbolic caller identity instead of the word's own
  declaration? It would catch a wrong declaration. First step: compare the expected main matrix with
  `data/caller.json` in #7000. No blocker.
- Can split tails be identified from the word alone? The 450 split has two tail candidates. First step:
  trace which tail reads the cut vectors in `data/split759_450.proof.json`. No blocker.

## Credit

Audited work: the #7000 package and the #6030 package, with their predecessors credited there. An independent reviewer found the weaknesses in the first version of these checks, and this version fixes them. This package was
written and run by Claude models (Anthropic) under human oversight. Apache-2.0.
