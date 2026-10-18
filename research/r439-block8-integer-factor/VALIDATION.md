# Executed validation — 2026-10-13

Research and test base: `f567884aeb8851b6e794af1184119a3bfbe1e631`.
Linux x86_64, Python 3.12.3, GCC 13.3.0, Boost 1.83.

Completed:

- `python3 -I -B research/r439-block8-integer-factor/verify.py`: pass;
  exact source pins, local matrices, all 4,096 Boolean inputs, 661 symbolic
  dirty-input columns, frame geometry, H1–H5, exported records, ten negative
  controls, complete prefix bounds and deterministic certificate comparison.
- The same verifier with `-O`: pass, same result.
- Minimal temporary relocation containing only this package and the three
  execution inputs: pass. Separate certificate corruption (claimed saving
  changed to 11) and source corruption (comment appended to pinned auditor)
  both fail with their intended mismatch messages.
- `python3 -I -B research/r439-block8-integer-factor/search.py`: pass;
  regenerated 5,000 trajectories and compared the exact witness and report.
  333 identity completions, no shorter reverse-dominated candidates, best
  relaxed circuit 40 gates. No claim of exhaustive circuit coverage.
- `BOOST_INCLUDE=/tmp/r439-boost/extracted/usr/include python3 -I -B
  research/r439-block8-integer-factor/native.py --write-certificate
  --output /tmp/r439-block8-native-complete`: pass. Both words were rebuilt
  by the local verifier; unchanged C++ legality and 5/9/11-stage checkers were
  freshly compiled and run. All 883/1,327/1,549 columns per word and 96 total
  bridge-omission controls pass. Exact Python/C++ positive bounds, paid profiles
  and ADD counts agree. `NATIVE-CERTIFICATE.json` retains all receipt fields
  except timing and the temporary stream pathname.
- `python3 -B scripts/verify_selected_result.py`: pass for the unchanged
  conditional `1661634653669567/1000000000000000000` selection.
- Python AST parsing and staged `git diff --check`: pass; only this package
  is added. No pre-existing tracked file changes.

The first native compile found no system Boost headers. Resolved by downloading
Ubuntu's `libboost1.83-dev_1.83.0-2.1ubuntu3.2_amd64.deb` and extracting it into
`/tmp/r439-boost`; no repository or system package installation was needed.
The downloaded archive's SHA-256 is
`519ecf2c64308527e15b6582955681d192a832250baa4bc424967aaf7d02d68f`.
A machine with Boost installed can omit `BOOST_INCLUDE`.

The prototype strict and relaxed searches used the same 5,000 seeded paths.
The committed search reproduces both criteria together. The strict failure is
a failed sampled search, not an impossibility result. The observed growth of
the reverse bound is preserved in the certificate and accepted only because
the unchanged native precision obligation passes.

The relevant checks for this isolated research addition are listed above.
No selected supplier input or existing generator changed. The broad regenerating
`make verify` suite, selected cold replay, hosted-parent invoice, moment/outer
assembly, Lean and remote CI were not run. Native scalar and stage coverage
must not be confused with those further obligations or a full theorem proof.
