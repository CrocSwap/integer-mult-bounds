# Recorded validation

The frozen width-seven result is `kappa = 0.001600067494703216`.
Its conservative counterpart is `0.001600067491919801`.

The final portable reproduction passed all 71 fresh provider stages and all
seven global stages. It reused the complete, hash-bound PR564 baseline
reproduction, whose 36 stages had already passed. It rebuilt the new words,
native programs, wrappers and exact phases before global admission. See
[the replay receipt](global/replay-evidence/REPLAY.json) and its artifact/log
hashes. This is distinct from merely reading the retained result.

The global construction passed the full physical chronology and invoice,
sixteen invalid-owner controls, 89 invalid-assembly controls, two accepted
phase timing changes and two rejected phase semantic changes, both exact
moment engines, and all 47 outer inequalities under each arithmetic model.

Capacity duals passed standard-library exact replay and eight corruption
controls. Expanded stage/bank bounds passed both rational engines. After
publication was moved onto main, the capacity verifier and the nine-stage
bound were rerun with the external source path to confirm that the PR564
package need not be republished in this change. Supplementary model scripts
accept `GAIN_PR564_SOURCE=/path/to/pinned-PR564/research/complex-allcold`.

The mandated aggregate checks were attempted in a separate unchanged PR564
baseline checkout. The initial `make verify` passed its earlier targets but
stopped when the selected bank verifier needed SymPy. Installing the pinned
`sympy==1.14.0` in a temporary virtual environment resolved that prerequisite.
`make gen4-bank-verify` then passed all nine fresh stages and omitted-stage
controls in 250.4 seconds.

Continuing the remaining aggregate targets stopped in `frontier531-verify`:
the inherited C++ bit checker could not find
`boost/multiprecision/cpp_int.hpp`. Consequently the repository-wide
`make verify` is **not a pass**, and targets after that failure did not run.
No unrelated scientific source was changed to bypass it. This environment
limitation does not replace or invalidate the separately recorded, complete
width-seven reproduction.

The additional pre-PR review was canceled at the user's request. Earlier
independent mathematical and adapter checks are retained as historical
evidence; no new review verdict is implied by publication.
