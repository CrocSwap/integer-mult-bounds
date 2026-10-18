# Validation record

Executed on Linux on 2026-10-13, from base
`7ee02b7c96d85f22b38d28bd7ed49bb8c1aeb261`. This record describes local
execution. Hosted GitHub checks have not been claimed as passing.

| Check | Result |
|---|---|
| CPython 3.14.4, isolated normal primary verifier | Six programs, 962 coefficients, 14 controls pass; deterministic receipt reconstructed |
| CPython 3.14.4, `-B -I -O` primary verifier | Complete committed receipt matches; all guards remain effective |
| CPython 3.14.4, isolated optimized integer checker | All 962 coefficient records and 13,286 grid inputs agree |
| CPython 3.14.4 focused tests | Eight tests pass, normally and with optimization |
| `/usr/bin/python3.12`, 3.12.3, `-B -I -S` | Primary receipt, integer crosscheck and eight tests pass without site packages |
| CPython 3.12.3 minimal relocation, `-B -I -O` | Complete primary verifier passes with only the package and pinned inputs, from a path containing spaces |
| Source corruption | Appending whitespace to pinned SW4 SPEC fails the source digest check |
| Receipt corruption | Adding two to a primitive invoice fails complete receipt comparison |
| Typed receipt corruption | Replacing an integer event count with its equal-valued JSON float fails comparison |
| Actual circuit mutation | Changing the reverse halving into doubling fails a scalar boundary check |
| Gzip and tar repackaging | Different compression level/timestamps for CK programs and both consumed SW4 archive members passes |
| Existing output file | `--write` fails before work; sentinel content is preserved |
| `make selected-record-check` | Selected κ, original source inventory and proof supplement pass |

The packaging mutations were applied one at a time to the disposable minimal
checkout and restored between checks. Only the described source, circuit and
receipt checks were deliberately corrupted. No production sources were edited.

## Mathematical coverage

The primary verifier freshly checks all scalar primitives in six orientations,
including 716+9 or 728+9 arbitrary columns, complete endpoints, scratch erasure,
unchanged paid-event histograms, original and replacement bills and positive
prefix envelopes. All four coefficient candidates are checked wherever
applicable. The integer implementation has a separate dense state model,
binary-denominator arithmetic and closed-form cost computation. Its agreement
is implementation diversity, not independent authorship or a formal theorem.

The 14 primary controls and eight tests include arbitrary dirty work, the
negative initial NAF digit, forbidden aliases, omitted reads/halves/clears,
wrong signs, understated cost and an endpoint-neutral excessive prefix. The
grid's stopping rule is exactly `1<=n<=511`, `0<=k<=12`, both signs; all
13,286 inputs were completed. The main receipt covers the full coefficient
census of the pinned programs separately from that grid.

## State and overlap refresh

The initial queue contained 633 open PRs through #820. Before packaging,
646 open PRs through #833 were checked. Searches for fractional/bidirectional
Horner, reversed digit order and related coefficient work found the known
cross-macro #751 and new #830. Their scope differs as recorded in README.md.
The #815 head changed to include a current-word frame search; it is neither
imported nor used to establish this circuit result. Source and relation pins
are recorded in CLAIM.json. Main still pointed to the exact base above.

While publishing, upstream advanced to
`f567884aeb8851b6e794af1184119a3bfbe1e631`, selecting #799. The complete
verifier was rerun with the actual consumed files from that commit and its
new selected pointer. It matches the original receipt. The #741 record moved
to `certificates/checkpoints/frontier741.json` with exactly identical bytes;
the source check now accepts that official archive path under the original
digest. A corrupted archive record is rejected. This is a #741/#626 result,
not a claim to optimize #799. [PR #837](https://github.com/CrocSwap/integer-mult-bounds/pull/837)
is the single submission for this pass.

Only issue #650 (requesting Discussions) was open outside PRs; no sprint
coordination issue was available, so the scope/result claim is local.

## Checks outside scope

No full repository `make verify`, supplier cold regeneration, global
admission/assembly, native phase or wrapper regeneration, Linux hosted CI or
Lean run is claimed. These unchanged construction obligations remain inherited.
The selected record and `upstream/` are unchanged. The result neither promotes
a supplier nor claims a new κ or a practical runtime improvement.

Prepared for Gareth Davidson (@bitplane) with substantial OpenAI Codex
assistance. Apache-2.0.
