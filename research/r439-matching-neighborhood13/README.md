# Two-edge exchanges do not close PR941's precision gap

All **857** cost-preserving words in a complete four-endpoint neighborhood
of PR941's three pinned arithmetic-optimal matchings fail the 192-bit
nine-stage guard. Each retains the known 11,948-ADD floor and passes the
104-bit local guard. This is a bounded negative result; larger exchanges,
unmatched vertices and other optimal matchings remain open.

The search examines all 711,624 oriented replacements of two matched edges,
including simultaneous orientation reversals and both alternative pairings.
The best has F=72,467, B=10,522,512 and nine-stage bound
6422720960971889698335381712362626086444383357876503052288 > 2^192.
[PROOF.md](PROOF.md) defines the complete domain, charges every helper
preparation/restoration gate and states the inherited interface limits.

From the repository root with Python 3.12+ standard library:

```sh
python -I -O -B research/r439-matching-neighborhood13/verify.py
python -I -O -B research/r439-matching-neighborhood13/independent.py
python -I -O -B research/r439-matching-neighborhood13/test_package.py
```

Expected: 711,624 proposals / 857 words / zero admitted / six mathematical
controls; independent four-vertex permutation enumeration and 10,239,436
replayed ADDs per direction; relocated replay and six package controls.
The primary compares every regenerated field with EXPECTED.json.
`--write-certificate /new/path.json` exclusively creates a replay receipt.
SOURCES.json enforces the full immutable input inventory. Text hashes
normalize CRLF to LF; gzip sources are pinned exactly. Relocation uses only
the declared closure, with no Git, network or matching solver.

The proof and exact dual floor are Gareth Davidson's PR941 work, not new
results here. The contribution is this complete finite neighborhood and
independent price/coverage evidence. No chosen word is admitted or proposed
as a supplier. H2/K, native replay, hosted invoice, physical/analytic and
global realization obligations remain. No new kappa is claimed.

The frozen base selected PR942; upstream later selected PR1042 during this
round. The historical PR941/PR915 comparison and BASE-SELECTED.json remain
fixed and are not assertions about the newer selected supplier. See
[NOTICE.md](NOTICE.md), [OVERLAP.json](OVERLAP.json) and [VALIDATION.md](VALIDATION.md).
