# Validation record

Observed locally on Windows with CPython 3.12.14, October 15, 2026:

- The original byte-pinned verifier completed the entire 37-mutant census on
  an ordinary canonical temporary root, matching every original receipt field.
- The original `prepare` rejected a benign `spelling/../work` root with
  `unsafe archive member`; the repaired function extracted both actual pinned
  archives through the same spelling and returned canonical roots.
- A real Windows directory junction reproduced the old rejection. The one-line
  repair passed through that junction. This uses an actual filesystem alias,
  separately from the portable dot-dot regression; no macOS execution is claimed.
- The registered replay passed with both `TEMP` and `TMP` set to that junction.
  It checked the source reconstruction, all five traversal/non-file controls,
  all 37 original mutations, the archived positive invoice and six downstream
  rejection probes. The emitted complete receipt was compared with type-sensitive
  recursive equality against unchanged `EXPECTED.json`.
- A Git-free export containing this package and only its nine declared external
  files passed the same complete replay, also using the junction temporary root.
  Default replay changed no exported bytes. Mutated external input, original
  receipt and reconstructed source were rejected; `-O` and an unknown CLI flag
  were rejected. All files matched their initial hashes after restoration.

The maintainer's c3c94c2e checkpoint already contains the macOS alias diagnosis
and `TMPDIR=/private/tmp` workaround. Its updated review reports a batch timeout;
this note credits that diagnosis and records the completed local replay rather
than inferring a mathematical failure from the timeout.

Prepublication overlap used the complete 767-open-PR title/body snapshot at
18:06:42 UTC and the complete cached Discussion snapshot at 15:22:22 UTC.
Later Discussion changes and every code diff are outside that coverage.
Targeted REST checks retained PR2158 head `8051d06d` with no owner repair.
Canonical main `c3c94c2e` has unchanged guidance and selected inputs relative to
the exact starting base `6bd33bc0`.

These are source portability and finite acceptance-boundary checks, not a
new invoice theorem, a general hostile-filesystem proof, independent human
review, hosted CI, selected cold replay or a complete supplier audit.
