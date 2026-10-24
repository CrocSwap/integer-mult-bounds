# Corrected PR5270 reference transcription, checked against the formal controller

Successor package to the audit in PR #5349. Author-checked, not yet
independently reviewed. No selected-result change and no new kappa.

PR #5349 showed that the physical listing in PR5270 agrees with its
`standard()` reference, but that reference differs from the thinned formal
controller whose invoice is priced. It isolated three transcription
differences and checked a corrected interpreter at p=2 and p=19. The audit
README named the first open step: correct the bridge and idle transcription
in a successor package and compare the corrected path against the formal
controller. This package is that step, for the reference path only.

## What the repair is

`verify.py` takes the emitted gate list from the retained `listing(p)`
source and rewrites it in three ways, and in no other way:

1. **Bridge direction.** The first 2(p-1) odd-role `BRIDGE` gates (the
   forward loop) have their endpoints swapped. Later odd bridges belong
   to the final reverse sweep. Their direction is already correct, so
   they stay as written.
2. **Middle idles.** `IDLE` gates tagged `middle` sit at even stages.
   Thinning removes those stages, so their power becomes 0.
3. **Outer idles.** `IDLE` gates tagged `initial` or `terminal` cover an
   interval of stages. Only the thick stages survive thinning, which is
   half of each such interval in this listing, so their power is halved.

The repaired list has the same gate count as the original. At p=19 the
repair touches 72 of 259 gates: 36 bridges swapped, 18 middle idles
zeroed, 18 outer idles halved.

## What is checked

From this package directory, using the Python 3 standard library only:

```sh
python3 -B verify.py
```

Runtime here: about 2.5 seconds. `RESULT.json` records the run.

- The vendor files are byte-identical to the pins in PR #5349's audit
  package (`SOURCES.json`).
- For every p from 2 to 19, the original gate list, read by the plain
  interpreter in `verify.py`, differs from the formal thinned controller
  at the audit specialization (q=1, odd stage letters i, even stage
  letters 1). The mismatch count at p=19 is 351, the audit's number.
- For every p from 2 to 19, the repaired gate list, read by the same
  plain interpreter with no correction flags, equals the formal
  controller exactly. Mismatches after repair: 0 at every p.
- The repaired p=2 matrix is the formal diagonal from the audit, entry
  for entry.
- Negative controls: at p=2, p=3 and p=19, leaving out any one of the
  three corrections breaks the equality. All nine controls are rejected,
  so each correction is doing work at each tested size.

## What this does not do

This package does not edit PR5270's own source files. The repair is
an explicit gate-list transformation in this package, so a successor to
PR5270 can adopt it gate for gate and be checked against the same
verifier. It also does not bind a native invocation or recalculate any
invoice. Those are the open questions below.

## Open next questions

- Bind one actual rank-eight native reverse invocation, its code changes
  and independent-block spectators to the corrected path, charging every
  additional Gaussian child. The full-R gauge identity in the original
  listing does not discharge this.
- Only after that binding, recalculate the complete paid and target
  profiles and use the generic tail and compiler theorem with newly
  certified constants.

Environment for the recorded run: CPython 3.12, Linux, standard library
only. Commands: `python3 -B verify.py` and `python3 -I -O -B verify.py`,
both from this package directory. Both pass.

Credit: DaysSky for PR5270's listing and physical gauge work, Cayden
Burkart / SethBurkart123 for PR4940's formal coded controller, Dillon for
PR4933's physical normalizers, Dugongue / mdumitrean for PR4929's
center-free producer, and Cinna Davis, Cao Yifan, zxv and Jacob Alan
Sussman for the retained lineage. The audit package in PR #5349 supplied
the retained vendor files, the formal-controller execution and the
interpreter pattern this package follows. Source notices and Apache-2.0
licensing are preserved.
