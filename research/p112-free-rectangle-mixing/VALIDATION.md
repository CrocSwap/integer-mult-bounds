# Validation and coverage

Prepared on 2026-10-13 from main commit
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`, on an isolated contribution
worktree. Environment: macOS/Darwin 25.3.0, arm64; CPython 3.14.7 and 3.12.14.
All computations use integers, F2 elimination, Fraction, or exact Q(i).

The canonical JSON mathematical receipt SHA256 is
`b52c5e63afe59f91c79e799906b3ca358152ef8e43590cd6eb34c3078c47857c`.
Canonicalization is `json.dumps(value, sort_keys=True, separators=(',', ':'))`
encoded as UTF-8. Whitespace in the committed receipt is not mathematical data.

## Executed checks

- The card's first working command:
  `python3 -B research/complex-decoder-field-extension-seed44/verify.py`.
  Passed: 25 punctures, three examples, 25 attainments, 14,400 pairings and
  seven controls. This is orientation, not a new result or supplier replay.
- `python3 -B scripts/research_baseline.py` passed the selected source bindings
  and identified the complex side as binding. `make selected-record-check`
  passed the selected record, exact kappa, source inventory and supplements.
- `python3 -I -B research/p112-free-rectangle-mixing/verify.py` passed all
  896 seven-dimensional slices, 100,352 ordered cross pairs, eight all-entry
  Q(i) fixtures and nine mathematical/source controls.
- `python3 -I -B research/p112-free-rectangle-mixing/independent_check.py`
  separately passed all finite geometry premises, all 6,272 stored basis rows,
  the complete cross-pair recount and six receipt mutation controls.
- `python3.12 scripts/research_package.py --package research/p112-free-rectangle-mixing`
  passed historical catalogue/selected-record provenance, working source pins,
  and both registered mathematical commands, reporting `outcome=negative-result`.
- A minimal export copied only the new package and its two declared live inputs
  to a fresh temporary directory. Both direct commands passed with
  `python3.12 -I -O -S -B` from an unrelated working directory. Primary and
  independent execution took approximately 1.68 s and 0.57 s respectively.
  Every exported byte and the file inventory were unchanged after replay.
- Actual CLI corrupt-receipt checks (an omitted slice and a changed sharp
  fixture cost) both exited one with `complete mathematical receipt mismatch`.
  The independent checker also rejects duplicate coverage, false dimensions,
  duplicate basis rows, erased rank-six cases and an on-mask correction.
- Staged whitespace validation: `git diff --cached --check`.

## What this verifies

The commands establish exact finite premises and compare the complete saved
receipt; PROOF.md supplies the quantified arbitrary-complex argument.
The independent implementation uses explicit nine-bit labels and different
elimination, but shares the pinned geometry as an oracle. No independent
human review or proof-assistant formalization is claimed.

The power-bill comparison is an elementary conditional inequality at unchanged
width, role normalization and COPY multiplicity. No entire supplier histogram,
physical program, owner/frame admission, precision/tape contract, native or
all-size compiler, analytic transfer or full multiplication theorem was checked.
The selected cold replay and unrelated historical replays were not run.
Hosted CI results are not asserted by these local checks.

## Coordination

The entry check completely paginated 804 open PRs and 56 discussion records.
The scoped claim was posted in
[Discussion 1316](https://github.com/CrocSwap/integer-mult-bounds/discussions/1316).
TASK.json records entry and final overlap coverage, exact nearby heads, warnings
and search limits. These are novelty leads, not mathematical acceptance or an
exhaustive search of every prior code diff.

No predecessor, upstream input, frozen package or selected-result file was
modified. New work is confined to `research/p112-free-rectangle-mixing/`.
