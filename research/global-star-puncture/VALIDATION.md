# Validation and handoff scope

Local verification on Windows 11, Python 3.13.5, October 12, 2026 PDT:

```sh
python3 -B research/global-star-puncture/verify.py
python3 -I -O -B research/global-star-puncture/verify.py
python3 -I -O -B research/global-star-puncture/independent.py
python3 -I -O -B research/global-star-puncture/test_verify.py
python3 -B scripts/verify_selected_result.py
git diff --cached --check
```

The exact receipt passes in normal and isolated optimized execution. Both F2 implementations agree on ranks, minimum weights, pair-syndrome counts and all 960 correction rows. Twelve primary mathematical controls and the independent engine's repeated incidence controls pass. Four harness tests pass: relocation/export from a minimal copy launched outside the copied root, corrupted receipt rejection with existing output preserved, changed contextual source bytes rejected, and changed source-pin digest rejected. The first harness attempt used this sandbox's inaccessible default temporary directory; placing its freshly created temporary tree inside the checkout fixed the environment problem. Each test verifies its cleanup target before removal. No failed run is counted as a pass.

A separate Codex worker reviewed the written induction, binary-face lemma and generalized-cube construction, then reviewed both implementation methods and replayed the exact receipt. It independently enumerated the nonlocal example using coordinate combinations and all 131,072 local coefficient assignments: the ten-star identity holds, all 16 intersection cells survive, and no target-local decoder exists. This extra finite check is supporting local review evidence; the production verifier independently checks local infeasibility by exact elimination. No independent human peer review or proof-assistant theorem build is claimed.

The selected-record check passes with exact kappa `51110230636731/31250000000000000`; all pinned contextual source bytes match. Neither `make verify` nor the expensive `frontier626-verify` cold supplier replay was repeated for this additive decoder research package. No supplier, assembly, generator, selected record, or `upstream/` file changes. Scoped replay covers the new mathematical work; no full repository-suite success is claimed.

The new scoped workflow copies the existing repository's checkout and setup-python action pins, runs this package and selected-record integrity on Linux/Python 3.11 and 3.13, and requires a clean checkout. Hosted CI status is separate from local execution and is not asserted here before execution.

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. A final main fetch retains that base. PR metadata was refreshed through #721, including the actual descriptions of #669, #715 and #717. #669 leaves the arbitrary off-target puncture problem open; #715 is an E8 mixed-port equality case and #717 studies E8 complex decoder floors. None duplicates the paired-port minimum-distance argument or its global/local distinction. PR669's source remains pinned at `308f1e6ec3bb0b6ec0584cf7bfe219addc219b1e`.

The proof establishes a scalar statement for one retained target. It neither certifies simultaneous all-target delivery nor supplies a complete paid word, dirty restoration, frame schedule, recursive profile, physical host or new multiplication exponent. The review target is the general proof and finite evidence, not the selected construction.
