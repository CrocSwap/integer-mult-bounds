# Validation receipt

Checked 2026-10-13 on macOS arm64 with bundled CPython **3.12.14**.
Only the new package is added to base
`f567884aeb8851b6e794af1184119a3bfbe1e631`.

Passing commands (normal and optimized receipts agree exactly):

```sh
python3 -I -B research/complex-x4-compensation-pairs/verify.py --out /tmp/x4-seed39-first-replay
python3 -I -O -B research/complex-x4-compensation-pairs/verify.py --out /tmp/x4-seed39-optimized-replay
python3 -I -B research/complex-x4-compensation-pairs/test_package.py
python3 -I -O -B research/complex-x4-compensation-pairs/test_package.py
make selected-record-check
python3 -B -m unittest discover -s tests -p test_selected_result.py -v
```

The output directories above must be fresh. The first recorded run used
`--record` to create RESULT.json; subsequent runs compare every field.
Actual execution used the desktop's bundled Python executable, without an
installation or new dependency. The system Python 3.9.6 is below this package's
documented Python 3.10 minimum.

Results:

- Complete 24,864-score census reproduced; 2,978 profitable candidates;
  seed-39 greedy pass reproduces all 56 disjoint selected pairs.
- All 728 arbitrary logical input columns pass for baseline/candidate,
  forward/inverse-transpose, in the independent integer engine.
- Both literal primitive programs pass 728 logical plus nine private-input
  columns, including charged coefficient/centre erasure and dirty-helper
  restoration. Full costs and exact positive prefix bounds match RESULT.json.
- Nine focused tests pass normally and under optimized Python. These include
  six boundary corruptions, the omitted-preparation/helper-only countercontrol,
  both missing-restoration orientations, both dropped private CLEARs,
  overlapping/unpaid recipes, eight independent admission controls and every
  actual coefficient's numeric lowering boundary.
- Package tests accept recompressed/reformatted JSON and standalone optimized
  relocation with spaces. They reject changed sources, repaired outer source
  manifests and changed stored result prices. Exported candidate program
  hashes agree with the directly constructed programs.
- The selected-record integrity command and its five existing regression
  tests pass. The selected certificate, source packages, proof supplements and
  upstream inputs remain unchanged.

A delegated read-only review independently ran the optimized nine-test suite,
checked the algebra, prices, private-input contract and receipt scope, and
reported no material defect. This is an AI-assisted review, not independent
human or proof-assistant verification.

## Development corrections

The first comparison used the untransported raw word against transported
canonical registers; exact equality failed despite matching 6,320 coefficients.
The final experiment derives its matrix directly from the pinned **canonical
selected X4** word and matches every compensation gate after sorting target
and helper indices. Historical `evidence/local` is a predecessor and is not
the input to this package.

The initial integer checker rejected legitimate scale gates with denominator
`-1`, used by the retained inverse convention. It now normalizes denominator
sign before dyadic validation, still rejects zero denominators, and includes
a negative-denominator cancellation control. Full replays subsequently pass.
These were implementation/admission failures, not mathematical counterexamples
to the selected construction.

## Verification limits

This contribution supplies a complete finite scalar and frame-boundary
substitution with explicit lowering and local prefix evidence. It does not
modify the selected compiler or source-bound supplier wrappers. No fresh
Clifford/phase construction, global owner admission, complete global invoice,
47-constraint outer assembly, full supplier cold replay, repository-wide
`make verify`, hosted CI or Lean multiplication theorem was run or is claimed.
The broad Make target regenerates unrelated historical artifacts and replays
unchanged suppliers; scoped checks above cover this isolated research package.
The global integration and inherited hypotheses listed in README remain open.

Final overlap refresh at **2026-10-13 11:03 UTC**, through PR897, found no PR for this X4
compensation construction. Targeted all-state searches returned #881
(independent word verification) and #869 (different B deliveries), with the
earlier credited #749 on JP8. PR883's complete metadata was inspected: its
changed 168-macro target precondition is retained here, while this contribution
changes only the following helper compensation. Its head and attribution are
credited in README. No pending implementation is consumed or combined saving
claimed. A fresh `git fetch origin` confirmed main still equals the exact base.
