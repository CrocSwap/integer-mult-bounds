# Finite verification and limits

Windows CPython 3.11.9; standard library only. Base and predecessor heads are
listed in SOURCES.json. The original PR781 verifier and complete PR855 verifier
were freshly reproduced before this experiment. No hosted CI pass is claimed.

The normal eight-word replay passed. An isolated optimized parent also replayed
all eight words with assertion-enabled native children. Each new word is rebuilt,
its paid profile discovered, and then freshly audited for all 714/717 columns in
both orientations. Exact model recounts and square-root enclosure controls pass.

During review, signed profile deltas were tightened to use upper power bounds
for negative coefficients. The corrected least margin remains greater than
0.018922942318. EXPECTED.json was regenerated from the audited receipts and exact
recount, then the final verifier was rerun from fresh native programs.

Five native mutation controls and three potential controls pass. Corrupting a
vendored core or the selected-context snapshot is rejected by source preflight.
Canonical JSON comparison distinguishes integer receipts from Boolean values.

Offline relocation uses a root whose name contains spaces, this package and
only the five pinned repository inputs. The first relocated native replay passed
all eight words but its final receipt comparison failed because it had loaded the
earlier signed-rounding implementation before the correction. The final relocated
replay uses the corrected implementation and frozen receipt and passes the
full eight-word audit, exact cost screen and strict receipt comparison under
`python -I -O -B`. Its final status is
`PASS_EARLY8_CONSTRUCTION_AND_EXTENDED_COST_OBSTRUCTION`.

The selected-record checker passes at the pinned current PR799 target. No
selected record, upstream source, accepted construction, Make target or workflow
is changed. The broader repository suite was run for the companion PR865 and
stopped on eleven ten-second subprocess timeouts in an unchanged historical
test; no repository-wide pass is claimed here.

The complete-cost rejection grants timing, labels, physical restrictions and
additional preparation/phase/access/scalar overhead free. Consequently these
words are not submitted as admitted phase/global suppliers, and no new kappa
or full multiplication theorem is claimed. See PROOF.md for the exact scope.
