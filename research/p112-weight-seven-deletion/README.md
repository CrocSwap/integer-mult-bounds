# A weight-seven P112 residue closes by deleting that piece

Nine independent pieces of weights at most `4^3,6^6` have intersection
of dimension at most four with the P112 root code, over every
characteristic-zero field. Therefore ten pieces with code intersection
at least six cannot have the actual TWOSIDE `(6,4)` profile `4^3,6^6,7`.
The tenth piece can be unrestricted.

Remove that piece first. At least five code dimensions survive, so Nick
Petalas/PR3169's existing root-A5 coordinate budget applies to the other
nine pieces, with three small supports and quotient dimension four. It
requires `795<=784`, a contradiction with margin eleven. The old incidence bound gives 816 and is insufficient.
See [the complete proof](PROOF.md).

This continues [PR3192's weight-seven handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/3156#discussioncomment-19000918).
A concurrent [PR3195](https://github.com/CrocSwap/integer-mult-bounds/pull/3195)
proved the initial target `5,5,6^6,7`; that profile is not counted as new.
The one bounded pivot here is the distinct ten-piece caller above.
It does not prove full C5, `C(P112)>=64`, supplier admission or a new κ.
The selected frontier is unchanged. The proof uses the standard
Weyl-chamber theorem and the inherited original decoder reduction.
Evidence is author-checked, not independent human or proof-kernel review.

## Evidence and reproduction

[RESULT.json](RESULT.json) records all 4,097,782 five/six-flats, the exact
chamber and root-plane checks, all 117,649 six-endpoint patterns, the
historical sixty-nine-profile inventory and the single new application.
The retained unmodified TWOSIDE checker corroborates the inventory count.
Fifteen behavioral groups cover dimension loss, quotient normalization,
invalid hypotheses, a losing support boundary, source mutations and output
safety. [CHECKS.json](CHECKS.json) records commands and environment.

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p112-weight-seven-deletion
```

For direct replay, run `python3.12 -B research/p112-weight-seven-deletion/verify.py`
and then `test_verify.py` in the same directory. Neither writes results into
the checkout. An optional `--output /absolute/external/new-file.json` creates
an exclusive external receipt. Source-only exports must preserve the package
and the declared `research/one-sided-six-multisets/data/data.txt` input under
the same relative paths. Direct replay does not need pending PR Git objects.

[TASK.json](TASK.json) declares the changed scope and stop rule.
[SOURCES.json](SOURCES.json) pins canonical main, exact predecessor heads,
Git blobs and source hashes. [ENGINEERING.md](ENGINEERING.md) records the
bounded implementation and verification limits. The geometry and retained
predecessor files are unchanged copies, not edits to frozen source packages.

## Open next questions

Before another geometric census, bind an actual still-open weight-seven
profile to its quotient and support hypotheses. A first step is to refresh
Discussion3156 and audit the historical `(6,4)` profiles against existing
dimension-deletion and rank-six bounds. The blocker is that a historical
survivor list is not a current scientific disposition ledger. The structured
question and stop rule are in [TASK.json](TASK.json).

## Credit

DreamingOfClouds/PR3154 supplied TWOSIDE and the original decoder-floor
reduction. Nick Petalas/PR3169 supplied the coordinate inequality; PR3164
and PR3161/3162 supplied its root geometry and retained exact label checks.
PR3192 supplied the weight-seven handoff and distinct no-seven profile
application. Concurrent PR3195 supplied the earlier deletion application
for `5,5,6^6,7`, which was independently derived here before the overlap
refresh and is not claimed as a new result. The E8/P112 lineage, including
joaqcoo's model, remains credited in the predecessor sources. See [the retained-source notice](vendor/NOTICE.md).
New work is Apache-2.0. Development and local checks used substantial
automated assistance.
