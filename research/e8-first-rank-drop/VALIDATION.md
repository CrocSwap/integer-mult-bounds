# Verification receipt

Base: `47481c89fd30a43f8f882eb4b391e89c29273fd0`.
Local macOS runs on 2026-10-14 Australia/Melbourne (2026-10-13 UTC).
All commands below use only Python's standard library.

- **CPython 3.14.6:** the primary builds the committed certificate, checking
  all 255 punctures, all 65,280 available-word ranks (including zero), the
  two required-code classes, all 130,305 distinct nonzero-reader pairs,
  256 standard flats and seven mathematical rejection controls.
- **CPython 3.14.6:** the separate Fraction/reflection implementation passes.
  It checks 512 rational ranks at two representatives, transports their
  tables to every case, verifies all explicit bases, and independently
  examines all 11,440 sorted nine-rank profiles for the retained-rank bound.
- **CPython 3.12.12, isolated optimized mode (`-I -O -B`):** both primary and
  independent checkers pass against the same committed certificate. One
  measured run took 10.32 s and 2.02 s respectively; these are local timings,
  not performance claims or stable benchmarks.
- **Five package tests pass** on CPython 3.14.6 (22.113 s). They reconstruct
  all 64 scalar source columns for both kinds of bases in both classes,
  reject invalid/duplicate reader patterns, wrong geometric parity, omitted
  cases, dimension and cost mutations, and corrupted source/evidence files.
  A copied package in an unrelated path containing spaces passes both
  checkers with `-I -O -B` and regenerates identical certificate bytes.
  Existing output is preserved; source failure produces no output.
- **`make selected-record-check` passes** for the unchanged PR890 result
  `1661957774647029/10^18`. This is record/source integrity, not a cold
  supplier replay.

A staged-Git-tree export passes both checkers from `/private/tmp` under
`-I -O -B`. Its code, certificate, source manifest and retained sources are
byte-identical to the final package; subsequent edits concern handoff
metadata only. No generated inputs outside this package are needed. No assertion depends on Python's optional `assert`.
The primary compares every reconstructed certificate field by default.

Upstream refreshed to `007664306fff84fbb1c9a1b4053b69f439764034` during
verification. The selected κ and both consumed PR heads were unchanged,
and the 367 changed upstream paths do not overlap this new package.
The original task base is retained. OVERLAP.json records the complete
702-open-PR inventory count through #949 and related pinned heads.

The large unchanged repository-wide and supplier cold-replay suites were
not rerun for this standalone mathematical package. No hosted CI pass,
proof-assistant proof, full multiplication-theorem audit or independent
human peer review is claimed. The independent checker independently
replays the new boundary; the through-55 theorem is credited to the pinned
PR939 written argument, not relabelled as new execution evidence.
