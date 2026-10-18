# Local validation

Executed on 2026-10-13 with CPython 3.12.3, Linux x86_64, standard library only.
The package uses one busy process at a time and no GPU. No packages were
installed. All source and evidence generation ran in one donated agent session.

## Completed checks

```sh
python3 -B research/complex-decoder-field-extension-seed44/verify.py
python3 -B scripts/research_baseline.py
python3 -I -B research/a8-p112-decoder-screen/verify.py --write
python3 -I -B research/a8-p112-decoder-screen/independent.py
python3 -I -B research/a8-p112-decoder-screen/test_package.py -k missing_receipt
python3 -B scripts/research_package.py --package research/a8-p112-decoder-screen --check-only
python3 -B scripts/research_package.py --package research/a8-p112-decoder-screen
python3 -B -m unittest discover -s tests -p 'test_research_*.py'
python3 -B scripts/verify_selected_result.py
```

Every command passed. The registered replay reran the primary checker, separate
checker and full six-test package file in **58.024 seconds**; its six tests took
39.221 seconds. The 20 repository research-workflow tests passed with no skips
(0.386 seconds reported by unittest). These are host-specific verifier timings,
not multiplication-runtime measurements. No broad historical replay was run.

The primary check covers 390,915 planes across all nine anchors, 19,299 partner
space tuples and 462,141 compatible subspace choices. It re-derives the sharp
cost 71, both witnesses, the 945-frame orbit, and eight semantic controls. The
separate checker uses different label coordinates, annihilator algebra and
Cartesian products, checks 86,870 planes for two symmetry representatives,
and proves its transport to all nine anchors using explicit permutations.

The eight semantic controls comprise six deliberate rejection cases, a check
that dropping mutual compatibility admits the false deficiency allowance 11,
and a positive non-real kernel-shift fixture. The six package tests check:

- isolated optimized replay in a relocated read-only directory with unchanged
  file hashes;
- the separate checker with the primary checker file absent;
- rejection of an altered cost claim, a missing anchor, a missing receipt, and
  malformed JSON.

The initial predecessor command is a source-bound positive control, not the
selected supplier's cold replay. The baseline and selected-record integrity
checks confirmed the recorded selected kappa and pins; no selected file was
edited. The new scripts use explicit exceptions, so their checks remain active
under `python -O`.

## What was not checked

No other P112 frame orbit, arbitrary nine-normal family, masked identity,
shared-copy implementation or physical supplier is certified. No delivery,
restoration, frame, hosting, precision/tape or complete moment invoice was
constructed. `make frontier1094-verify`, native/Lean builds, hosted CI, an
all-size compiler and the complete multiplication theorem were not run or
proved. The written covering argument has no independent human review.

PR1248 and PR1224 were fetched anonymously and read at the exact heads in
SOURCES.json. Their code and certificates are not runtime dependencies; the
new package recomputes its own needed finite facts. The predecessor head/hash
references are attribution evidence and are not checked by the generic runner,
which checks the main-tree source inventory in `SOURCES.json.files`.

The final overlap query used a shared offline snapshot: 788 open PRs
fetched 2026-10-13T21:54:03.402700+00:00 and 40 discussion records fetched
2026-10-13T21:54:12.002645+00:00, both marked complete pagination. It does not
cover later updates or every diff. The claim is in discussion #1241.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
