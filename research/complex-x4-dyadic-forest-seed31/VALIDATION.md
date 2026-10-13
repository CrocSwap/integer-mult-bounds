# Validation and handoff

Validated on Windows on 2026-10-13 against base
018418fd789ce12a8c176279fe012138713ff53d.

## Executed checks

- Complete verify.py with isolated, optimized CPython 3.11.0: PASS.
  Both implementations agree on all 1,086 coefficient summaries and witnesses,
  all 13,501,152 comparisons, and the 10,883 floor. All 12,544 cycle inequalities
  pass. The independent literal check covers 1,087 coefficients including zero;
  its three endpoint fixtures reject 18 omissions/sign mutations in total.
- The nine package tests pass under CPython 3.11.0 with -I -O -B.
- Complete verify.py also passes under isolated CPython 3.14.5 from a working
  directory outside the checkout, reproducing the exact committed certificate.
- The same nine tests pass under CPython 3.14.5. Its first attempt could not
  write the sandbox's default temporary directory; rerunning with tempfile.tempdir
  set to a writable workspace scratch directory passed all nine. No assertion
  was disabled and no check was skipped. The runtime emitted a local executable
  location warning; it did not affect the successful verifier's exit status.
- python -I -O -B research/complex-x4-target-forest/verify.py: PASS;
  floor 10,883, 737 input columns, both orientations, predecessor compensation
 6,320->2,324, primitive saving 47,690 per orientation. This freshly checks the
  existing attaining witness; the new package does not emit another circuit.
- python -I -B scripts/verify_selected_result.py: PASS at unchanged
 1661957774647029/1000000000000000000.
- python -I -O -B tests/test_selected_result.py: five tests PASS.
- python -I -O -B tests/test_selected_proof_binding.py: ten pass; two skip
  because Windows sandbox symlink creation is unavailable.
- A separate AI worker reviewed the tail proof, forest exchange, both census
  implementations, verifier and certificate, and reported no actionable flaws.
  This is not independent human review or a proof-assistant check.

The core receipt digest from the independent expanded edge enumeration is
69d56df08131e475882bab07c54c2fa91456c0ae20d2785c38651611a79ebc53.
The certificate compares decompressed source payloads where relevant; the
committed immutable archive also retains its exact SHA-256 pin.

## Hypothesis correction

The first screen asked whether nonunit edges lose to their root. That stronger
claim is false: 970 nonunit edges beat the root and 34 tie. The completed
experiment instead checks replacement by the minimum of the root and the two
signed-unit edges to the same parent. Every nonunit loses strictly, with a
finite-core minimum gap 56. The proof accounts separately for both infinite
tails. No failed search is represented as an impossibility theorem: the
class-wide conclusion follows from complete finite coverage plus the two
written tail bounds and forest exchange lemma.

## Coordination and integration limits

The open-issue page had only #650 and #913, with no pinned sprint claim thread;
the claim is local. PR metadata was refreshed through #960. Relevant concurrent
#917 (historical CK helper basis), #937 (center shears), #945 (joint Horner),
and #947 (constant-row center shears) alter different blocks or lowering classes;
none supplies this all-dyadic single-parent forest exclusion. Source dependencies
are incorporated #909 and #932, pinned and credited in SOURCE-PINS.json.

Origin/main advanced to 00766430 after cloning; its changes concern historical
attribute pins/reconciliation receipts, not this package's inputs. The base and
source pins remain unchanged. GitHub CLI authentication was subsequently confirmed as @woklerx. The
contribution is submitted through that account’s fork as one focused PR.
Nothing is merged and the selected record and upstream/ are unchanged.

Full make verify, make frontier890-verify, hosted CI, native supplier regeneration
and Lean are not run: this isolated research package installs no supplier and
changes no existing generator, source or selected construction. The complete
new checker, inherited attaining witness, and selected-record checks above are
the directly affected coverage. Existing all-size, compiler, realization,
precision/tape, hosting and analytic obligations are not discharged here.
