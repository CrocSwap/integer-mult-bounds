# Validation

`analyze.py` generates the exact certificate from the pinned selected record
and predecessor certificate. It enumerates the 945 restricted-growth source
words, constructs witnesses for ten representative normal-weight/parity
classes, expands them by coordinate permutation to all 62 affine
hyperplanes, and checks each output's boundary pair. It exhausts 246,016
unit-width dirty scalar cases.

`independent_check.py` enumerates perfect matchings of ten positions using a
separate recursion, confirms the 945-word set digest, checks the odd-family
coverage obstruction and query minima, and independently replays all 62
plans. Negative controls reject a ten-toggle cover claim for the odd family,
an omitted dirty-target readout, and an unpaired source toggle.

The mathematical proof is the prefix-difference identity in `PROOF.md`; the
finite replay is evidence for the literal schedules and boundary tables. No
independent human review is claimed.

The selected baseline is pinned in `TASK.json` and `SOURCES.json`; this
package does not rerun the full `make frontier1094-verify` selected
construction reproduction. The repository's Python 3.12 registered replay
may be run when that interpreter is available. Direct checkers use only the
standard library and passed under Python 3.14.7.
