# Closure argument

Let `A` be the byte-pinned selected replay archive and `R` its archived `RESULT.json`.

1. Every entry is a unique relative POSIX path, a bounded regular non-executable file; no extraction occurs.
2. `R.artifacts` equals `members(A) - {RESULT.json}` and every declared SHA-256 equals bytes read from `A`. The separately pinned archive digest binds the self-excluded result too.
3. `STAGES.json` equals `R.stages`; the ten fixed names, zero exit codes and log digests are checked.
4. Six promoted public receipts equal their archived bytes.
5. Exact frozen historical selected and integration record pins bind the value, source head, certificate, source manifest, archive and promoted receipts. The selected record is package-local data copied byte-for-byte from the pinned base; the live selected pointer is outside this historical audit.

Therefore all 458 capsule bytes and stated publication edges are authenticated relative to `PINS.json`. This says nothing about execution history or the inherited multiplication theorem assumptions.
