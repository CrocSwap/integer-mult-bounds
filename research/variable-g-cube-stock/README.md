# One physical-H inventory across changing selected-bit counts

One fixed seven-tape inventory now serves rounds with different selected-bit
counts. This answers Open next question 1 of unpaidmoon's [PR6342](https://github.com/CrocSwap/integer-mult-bounds/pull/6342).
The new adapter uses checked active prefixes and reuses the butterfly arrays
after every selected bit. Its achieved stock is

`F = 6 M r (p + 2 + p + g_max + 2)`.

Claim type: scoped tape-model construction and written simulation proof, with
an exact finite certificate. No new kappa or selected-frontier change is claimed.
The predecessor arithmetic and one-round return are cited premises.

For `ell=3`, flags `(True, False)`, `k=1`, `p=4`, the first two heights have
`g=1` then `g=2`. They run on **21,504 cells**. Both complete one-round ledgers
and actual output packets equal fresh calls. The previous output reset adds
6,144 writes and 12,284 moves. [PROOF.md](PROOF.md) gives the induction, exact
buffer list and first witness invoice.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/variable-g-cube-stock/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/variable-g-cube-stock/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/variable-g-cube-stock
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/variable-g-cube-stock --check-source-history
```

Any CPython 3.12 executable may replace this installation path. Direct execution
prints `PASS_VARIABLE_G_CUBE_STOCK` followed by a generated receipt with computed
results and package file hashes. No handwritten receipt is supplied.

The verifier checks five schedules comprising fourteen rounds, including both
width-change directions, repeated changes, two chunk widths and a one-to-three
selected-bit change. It compares every output bit and the full charged ledger
with a fresh invocation. Eleven rejection controls cover prefix and capacity
bounds, inactive dirt, invalid allocation state, input bounds and restoration
on failure. Normal and optimized commands are registered in VERIFY.json.

## Scope and remaining obligations

The stock counts seven physical bit arrays. Python control objects, diagnostic
scans and verification snapshots are outside that bit-tape model. The executable
bounds layouts and schedules as stated in PROOF.md. Its privately loaded engine
module is used serially; its temporary Tape binding is restored on every exit.

Each round receives an external source presentation. Only the latest physical
root/consumer output remains live. This is not an inter-round diagonal or an
output-to-input transfer, nor a minimum stock theorem. Production widths,
physical control lowering, retained-output banks and the five framework
assumptions remain open. No selected cold replay, Lean, Docker, supplier
admission or complete multiplication theorem is supplied.

## Open next questions

- Compose the retained output, a fully charged framed diagonal and the next
  round on this stock. Start with the same ell=3 witness and specify the packet
  framing; initial framing and input transfer remain unpriced.
- Specify explicit banks when a caller needs both round outputs simultaneously.
  The current bound depends on resetting the previous root and consumer.

TASK.json records the corresponding first steps and blockers. Optimization
stopped at the first verified changing-width construction.

## Credit and sources

This construction, proof and verifier were produced by Nick Petalas.
Credit unpaidmoon for PR6342's question and stock scheduler and PR4127's
one-round physical tape program; Chris R / Clear1nsight for PR3623's matched
layout and tensor; Sagar Thakrar for PR3617's diagonal contract; and the
PR3493, PR3593, PR3599 and PR3611 lineage retained in the one-round source.
SOURCES.json binds the canonical base and cited source files without changing
their credit lines. Independent human and formal proof-kernel review are
unclaimed. Apache-2.0.
