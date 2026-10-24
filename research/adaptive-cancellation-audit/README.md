# Independent sharp-cancellation audit

Assignment D audits one quantified implication of zxv's adaptive compiler. The source-bound registered replay passes, and PROOF.md supplies an all-real proof with an exact sharpness statement. No new kappa, lower uniform rank, compiler bug or complete compiler admission is claimed.

## Result

Under I=B+F+A, 0<=beta<eta<1, nonnegative potentials and B<=beta I, the exact identity is

    (1-beta)(eta I-B-F)
      = (eta-beta)A-(1-eta)F+(1-eta)(beta I-B).

Therefore (eta-beta)A >= (1-eta)F guarantees exit contraction. For fixed A,F with positive sum, the largest permitted exit fraction is (beta A+F)/(A+F), attained at I=(A+F)/(1-beta), B=beta I. Necessity is for a guarantee over all admissible boundary masses, not for every individual flow. The zero-mass endpoint is handled without division. The source's A=(T-P)H-R includes the root debit. Omitting that debit can falsely pass while the actual exit fraction is 11/20 instead of at most 1/2. Dropping the leaf term similarly invalidates a weaker test. These are rejected controls, not counterexamples to PR4483.

The elementary extremal calculation carries no priority claim. The contribution is the exact source-bound proof audit, sharp scope and discriminating failure witnesses, separate from the numerical gate checks.

## Reproduce and actual evidence

Python 3.12, standard library only:

```sh
python -B scripts/research_package.py --package research/adaptive-cancellation-audit
python -I -O -B research/adaptive-cancellation-audit/verify.py --self-test
```

[VALIDATION.md](VALIDATION.md) records successful hosted workflow 39723357163 on CPython 3.12.15, the exact head and merge ref. RESULT.json retains all 6,120 rational cases, 1,800 extremiser checks, 120 zero-mass cases, four invalid-premise controls, nine coefficient checks and omission witnesses. Normal replay authenticates the proof and compares every receipt field. Optimised controls pass. No predecessor acceptance function is imported. The universal argument is written algebra, not extrapolation of a finite grid.

## Sources, scope and overlap

Canonical scientific base f9f85c1e4fa1e955ff39f10fca447e3e2a4e4adc, priority revision 7. The live source research/rank-convergence/PROOF.md is pinned by blob 75f451837204bd141f357e7f5e5d6c6f42e1423e and SHA256 in SOURCES.json and declared in VERIFY.json. Catalogue and selected record remain historical provenance.

PR4529 checks finite gates but excludes the theorem. PR4532 addresses broader gate existence, and PR4533 retunes witnesses without a new kappa. This work isolates the scalar cancellation inference rather than repeating those results. Targeted live searches and bounded Discussion reading are not exhaustive overlap coverage. The historical baseline helper and full selected cold replay were not run. TASK.json declares the user-assigned changed proof-audit scope.

## Open next questions

A better universal threshold cannot follow from these same scalar inequalities alone. First prove stronger actual-flow information, such as a joint boundary/leaf occupation bound, and compare it with the explicit extremisers. Separately audit one Chernoff occupation or root bound; those premises, mirror certification, majorant funding, native realisation, physical costs, precision and outer transfer remain open to this package. Refresh overlap before claiming them.

## Credit

Credit zxv for PR4483's cancellation argument, Jacob Alan Sussman for mixed-target recursion, Ryanson Jonathan for mirror/gate work, Dillon for the broader gate-existence follow-up, and the retained Cinna Davis/native/outer lineage. Prepared for Chris R / Clear1nsight with substantial OpenAI assistance, Apache-2.0. One session with separate workstreams does not constitute independent human or formal-kernel acceptance.
