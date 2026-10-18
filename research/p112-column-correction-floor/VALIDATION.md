# Validation and boundaries

Validated on Linux x86_64, 2026-10-14 UTC, using Python 3.12.3 and 3.14.4.
The package is standard-library only. Research and refreshed submission base:
`410026dc5513b87db92ae98571d1d5984c69a983`. Both live source inputs and the
assignment/contribution instructions remain byte-identical at the refresh.

The required starting example passed:

```
python3 -B research/complex-decoder-field-extension-seed44/verify.py
PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44 p=0..24 examples=3 attaining=25 pairing=14400 controls=7
```

That is predecessor orientation, not new mathematical evidence.

## Registered complete replay

```
/usr/bin/python3.12 -I -B scripts/research_package.py --package research/p112-column-correction-floor
PASS_P112_COLUMN_GEOMETRY pairs=28 sites=112 survivor_slices=15680
PASS_P112_COLUMN_BOUNDARY ranks=7,8,7 COPY_sum_floor=64 q=0..1(open,closed)
PASS_P112_COLUMN_CORRECTION_FLOOR receipt_sha256=6d621ea5ffffc4079cc50a8bf4a0e4d83305ec48ce78b7d95e844da97a4c0627
PASS_REGISTERED_RESEARCH_PACKAGE research/p112-column-correction-floor outcome=negative-result
```

The registration also ran all seven test groups successfully (10.169 seconds
for the test command on this host). The earlier standalone test run passed.
The final canonical receipt above includes the explicit proof branch and its
per-term lower charges for every scalar fixture.

The complete check covers both geometry engines, 140 support strata, all
71,540 character evaluations, 15,680 complete odd-neighborhood erasures,
15,680 singleton erasures, 700 ordered support pairings and every receipt
field. Thirteen Gaussian-rational full nine-term fixtures check all 163,072
matrix entries, the free-mask requirement, projected coefficient identity,
full factor-matrix ranks, COPY charges and the appropriate proof-branch bounds.
The independent geometry checker does not reimplement the Gaussian-rational
fixture engine; that coverage boundary is explicit.

Seven semantic/integrity groups cover:

1. The exact (7,8,7) counterexample to extending the former per-child premise,
   rejection of a dropped compensation charge, and the q>1 boundary.
2. Nonfree diagonal changes, a nonsingleton second factor, zero singleton
   amplitude and repeated coordinate rejection; zero u remains a valid control.
3. Singular changes, inverse without transpose and conjugate-transpose failure.
4. Six independent finite-receipt corruptions: omitted stratum, wrong survivor
   rank, wrong pairing rank, wrong free distance, repeated boundary deletion
   and incomplete site coverage.
5. Missing/duplicate source inventory, duplicate JSON keys, nonfinite JSON,
   and integer/Boolean/float receipt substitution.
6. Full read-only isolated optimized export, byte preservation, actual source
   corruption rejection and actual stored-receipt corruption rejection.
7. Existing output preservation before replay starts.

## Separate environment replay

A second minimal export of twelve runtime files (including both live inputs)
was set read-only: files 0444, directories 0555. From `/tmp`, Python 3.14.4 ran

```
python3 -I -O -B /tmp/math-pass29-readonly/export/research/p112-column-correction-floor/verify.py
```

It produced the identical complete canonical receipt above, and all twelve
files remained byte-identical. Later overlap, attribution and publication
metadata edits do not change executable code, the mathematical receipt or
source input bytes. No external caches or nonstandard libraries are required.

## What this validation does not establish

Finite tests corroborate the written quantified argument; they do not exhaust
GL(3,C), arbitrary complex amplitudes or the continuum of exponents. Those
quantifiers are handled in PROOF.md. Neither engine is an independent human
review or a proof-assistant proof. Earlier support-stratum and erasure facts,
the three-active branch and the concurrent fixed-boundary example are credited
in README/PROOF rather than claimed as new.

No physical gathering/restoration word, frame itinerary, owner/hosting layout,
native 5/9/11-stage run, selected construction cold replay, packed precision,
tape proof, all-size compiler or analytic transfer was performed. The COPY
comparison assumes fixed normalization and separate charging and grants all
added overhead zero. It does not establish a new supplier or improved κ.
Hosted CI and maintainer review are separate from the passing local checks.
