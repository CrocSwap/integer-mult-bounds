# Validation record

Run on 2026-10-13 from base
`66849e1475c930fd7732b1a0067ffee7e1e95f60`, on Linux x86-64 with CPython 3.12.14,
GCC 14.2.0 and Boost 1.85.0. Optional hosted dependencies were NumPy 2.3.5,
SciPy 1.17.0 and SymPy 1.14.0. No remote CI or independent human-review pass
is claimed.

## Local and independent checks

```sh
python3 -I -B research/r420-optimal-composed-pairs/verify.py
python3 -I -B research/r420-optimal-composed-pairs/independent_check.py
python3 -I -B -O research/r420-optimal-composed-pairs/verify.py
python3 -I -B -O research/r420-optimal-composed-pairs/independent_check.py
make selected-record-check
```

All passed. The primary checker verifies the 1,442 optimum using all 7,140
unordered edges, validates all 660 inputs of both complete words in both
directions, checks every frame with the original E8 checker, and reproduces
the entire PR681 comparator receipt exactly. It rejects twelve mutations and
accepts one neutral endpoint only with its two ADDs charged. The separate
column-incidence checker covers all 50,400 matrix coefficients and 540 literal
Boolean D inputs, and rejects four certificate corruptions. Its implementation
imports neither the main checker nor a matching solver.

The original H2 and direct K extractor remain false for the substituted D.
The canonical composed body with the original D passes H1-H5 and their
conclusions. Exact D-boundary equality justifies the substitution. The original
guards were not relaxed.

## Fresh native and hosted replay

```sh
BOOST_INCLUDE=/directory/containing/boost python3 -I -B research/r420-optimal-composed-pairs/verify.py --hosted --out /absolute/fresh/output
```

Passed for the actual reconstructed PR681 comparator and this replacement.
`NATIVE.json` and `HOSTED.json` retain all deterministic fields; only runtime
`seconds` fields are omitted. Full commands compare the generated receipts
with these files.

- Fresh unchanged C++ legality checks accepted both physical words, including
  all 660 register paths, nine COPY/ERASE lifecycles and rank mass 5,112
- Five-, nine- and eleven-stage replays covered 900, 1,380 and 1,620 independent
  formal columns per word, with all 96 bridge-omission controls rejected
- Removing one helper-return ADD is rejected by all three native checkers
  with `local defining-decoder full formal column`, rather than by an unrelated
  parser or precision failure
- Both parent auditors rejected all 17 controls; both hosted auditors rejected
  all 16 controls
- All 120,960 helper invocations remain hosted whole with zero banks
- Emitted local-invocation events fall **6,144,768 -> 6,140,160**, exactly 288
  times the local saving of 16. This counts the expanded local streams only;
  69,120 bridge ADDs and schedule/hosting work are separately charged and
  unchanged. It is not a complete-machine instruction counter
- Both fresh invoices retain **196 raw prefix bits charged at 256**, and
  **432 two-level coefficient bits charged at 512**
- Both exact moment engines reproduce bit lower bound
  `413456747036699736067/250000000000000000000000`

The native body counts are 18,378 and 18,362. Their D costs are 11,562 and
11,546. Both positive prefix maxima are 253,149 and 4,334,338; the exact local
payload bound is 19505369118995241654063407203584, strictly below 2^104.
The selected baseline remains 26,916 ADDs. The cumulative 8,554 reduction from
that baseline includes predecessor work and is not attributed to this change.

The primary checker additionally reconstructs PR733's exact pinned 57-pair
recipe on the **same PR681 body**. It gives 18,370 total ADDs and 11,554 D ADDs,
with the identical 253,149 / 4,334,338 prefix bounds and 104-bit local envelope.
Full scalar endpoints in both directions and frame paths pass. Thus **eight**
ADDs are new beyond the strongest prior matching on this body; **16** is the
reduction from PR681's published complete word. A separate third native/hosted
replay for the same-body comparator is not claimed.

The PR484 calculation inside the inherited hosted driver is a historical
control. This run does not rebuild the selected complex supplier or assert
a new selected outer assembly. The selected record/source-inventory check
passes without modifying its source files.

## Portability and rejection checks

A minimal tree containing only this package and the 143 pinned inherited files
was copied to a path containing spaces. From an unrelated working directory,
normal/optimized primary checks and the independent checker passed.

`PACKAGE-TESTS.json` records these nine process-level checks:

1. Relocated normal primary replay passes
2. Relocated optimized primary replay passes
3. Relocated independent replay passes
4. Recompressing the original word with a different gzip level/header passes
5. Altering its decompressed payload fails the source binding
6. Altering the claimed saved-ADD count fails exact receipt comparison
7. Altering a matching score fails its recomputed oriented price
8. An existing output directory is refused and its sentinel is preserved
9. Removing the pinned input fails instead of reporting success

Python compilation and staged whitespace checks pass. Generated bytecode is
excluded from the patch. Only the new research package is changed; selected
artifacts and `upstream/` are untouched.

## Live comparison and scope

The initial scan inspected 598 open PRs through #779. A refresh through #799
confirmed that PR681 and PR733 still have the pinned heads; `main` remains at
the exact base. PR794's 19,037-ADD target-basis word retains a smaller 192-bit
hosted charge and is explicitly compared in the README. PR789/790 alter
different B blocks; PR799 uses different suppliers. No duplicate certificate
for this fixed PR694-basis disjoint target-pair optimum was found.

The independent review before publication is separate from the author's
checks above. Finite certificate success is not a formal multiplication
theorem. Repository-wide `make verify`, selected-frontier cold replay, Lean,
remote CI and all inherited uniform/compiler/physical/tape/analytic obligations
are outside the claimed validation.
