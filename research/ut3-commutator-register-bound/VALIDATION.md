# Local verification receipt — 2026-10-14

Base: `410026dc5513b87db92ae98571d1d5984c69a983`.
Host: Windows 11, build 26300, x86-64. Standard library only.

1. Python 3.12.14: `python -B scripts/research_package.py --package
   research/ut3-commutator-register-bound` passed metadata/source provenance and
   the complete registered replay, ending with `PASS_REGISTERED_RESEARCH_PACKAGE`.
2. Python 3.14.7: copied the eight package files to a different directory and
   ran `python -I -O -B verify.py`. The complete replay passed in 28.42 seconds.
   SHA256 of every copied input file before/after agreed; no generated files
   were created. Explicit predicates remain active with assertions disabled.
3. In that disposable relocated copy only, incremented the r=3 receipt's
   `ball_size` by one. The same optimized replay exited 1 with `ValueError:
   receipt drift` (23.44 seconds), after recomputing the census. The submitted
   package's receipt was never changed.

Both successful engines compare the full state sets and their minimum
distances, not only the hashes or layer counts. Positive endpoints, empty
two-target intersections, independently recovered single-target minima and
37 boundary/algebra controls passed. Python 3.12 and 3.14 agree on the committed
receipt. These are two implementations written in one Codex session, not
independent human review.

The initial prescribed `scripts/research_baseline.py` was attempted and failed
the selected-package inventory check because this sparse checkout omits large
frozen supplier inputs. No selected supplier circuit replay or baseline PASS is
claimed. This result has no selected-supplier runtime dependency.

Hosted Linux CI was not run locally. The opt-in `VERIFY.json` requests the full
bounded replay on Python 3.12 with a 120-second timeout. No historical suites,
physical/compiler/hosting checks, all-register proof, precision/tape audit or
outer analytic transfer were run. The selected frontier remains unchanged.
