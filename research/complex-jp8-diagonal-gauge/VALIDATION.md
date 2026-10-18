# Verification and handoff

Status: **completed finite research construction**, with a scoped exact
optimality certificate; **no new κ**. Prepared for Luis Leon (@mythrilium)
with substantial OpenAI Codex assistance. No second human reviewer is claimed.

Research-time base and research-time refreshed upstream main both equal
`66849e1475c930fd7732b1a0067ffee7e1e95f60`.
Branch: `research/jp8-diagonal-gauge-seed35`.
Only this package changes; `upstream/` and the selected certificate are untouched.

## Passed checks

Environment: Linux, CPython 3.12.14. Arithmetic verification uses only the
standard library. The optional nomination used NumPy 2.3.5 / SciPy 1.17.0.

- `python3 -I -B research/complex-jp8-diagonal-gauge/check.py`: passes the
  exact zero-gap certificate, both original/candidate full scalar programs,
  all 716 native plus eight arbitrary private-centre input columns, and all
  846 distinct coefficient primitive boundaries. Final output:
  `PASS_JP8_GAUGE_COMPLETE saved=6154/6154 optimal_cost=10326 tests=10 inherited_controls=25 kappa=unchanged`.
- Separate integer-dyadic row implementation agrees on the entire cleanup map
  in both orientations. All ten focused tests pass, including 12 distinct
  adverse mutations and 50 small arithmetic cross-checks.
- The unchanged pinned `hpe_emit_local.py` emits exactly the independently
  spliced candidate streams, including every boundary scale. The unchanged
  `hpe_audit_local.py` accepts both streams, their unchanged paid profiles,
  scalar endpoints, prefix bounds and wrapper/frame lifetimes; all 25 inherited
  controls reject.
- The complete command also passes under isolated **optimized parent** Python
  (`-I -O -B`). The harness explicitly runs inherited assertion-based auditors
  with optimization disabled and removes `PYTHONOPTIMIZE` from their environment.
- A minimal relocated checkout in a path containing spaces, with only this
  package and the seven pinned source files, passes from `/tmp`. Both gzip
  inputs were recompressed at level 1 with a different timestamp. The complete
  relocated check took 17.182 seconds in this environment; this is a reproduction
  receipt, not a performance comparison.
- Changing the committed saving receipt is rejected. Changing a pinned cleanup
  coefficient inside the source gzip is rejected. These controls ran only in
  the temporary relocated checkout.
- Optional rediscovery reproduces the exact committed primal/dual certificate
  in this environment, and the documented seven-sweep bounded-screen trace.
- `make selected-record-check` passes. Staged whitespace and clean-base
  patch-application checks pass in the final handoff.

One early synthetic negative test failed because its toy event stream did not
clear its arbitrary private centres, so it reached the centre guard before the
intended prefix guard. The test was fixed by explicitly clearing those centres;
the exact-identity `2**193` excursion is now rejected for the intended prefix
failure. No mathematical construction or acceptance condition was weakened.

## Coverage limits and overlap

The rational whole-program interpreter executes verified scalar macro semantics,
not every primitive on every full row. The separate coefficient interpreter
executes original Horner primitives on three formal inputs, including arbitrary
incoming work. The standalone cleanup integer replay tests arbitrary boundaries
rather than only states reachable from the front half of the supplier.

No global invoice, full repository `make verify`, selected cold rebuild,
remote CI, Lean or production integration was run or claimed. All inherited
uniform, physical, precision/tape/recovery and analytic assumptions remain.
The unchanged paid recursive profile means this result does not improve κ.

The initial complete open-issue scan found only ordinary issue #650, with no
sprint coordination issue, so the narrow claim is local. A later complete scan
covered 585 open PRs through #766. The 05:25:52 UTC refresh checked all recently
updated open PRs through #772, including #769's distinct private-work ladders.
No restored live-register JP8 diagonal sandwich or matching exact dual
certificate was found. This is an overlap check, not a claim about private work
or historical priority. Predecessors and concurrent mechanisms are credited in
README.md and no pending implementation is imported.

The contribution is prepared for the verified Personal GitHub account
`mythrilium`. Publication status will be recorded after the fork and PR steps.
Publication refresh: main is now `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.
The six executable/construction source files remain unchanged. The historical
selected record is retained byte-for-byte inside this package, with its original
source pin. The publication branch retains the original research base.
A final focused replay checks this portable packaging before submission.

## Apply and review

On the exact base above, apply the supplied format-patch with `git am`, then run:

```sh
python3 -B research/complex-jp8-diagonal-gauge/check.py
```

Suggested PR title: **Research: certify optimal restored JP8 diagonal gauge
(6,154 fewer primitives per orientation; no new kappa)**.

The exact proof and class limits are in README.md; source pins are in
SOURCES.json; the complete optimality witness is in CERTIFICATE.json.
The maintainer can integrate or independently review the package without
changing the selected frontier. Production adoption remains a separate task.
