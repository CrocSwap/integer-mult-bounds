# Reverse parked records to remove one POP scan

This contribution was produced by Nick Petalas. Claim type: a new finite
controller with a scoped written all-size proof and exact finite corroboration.
For the valid matched-packet interface of ywz65's
[PR2635](https://github.com/CrocSwap/integer-mult-bounds/pull/2635), storing each
record in reverse order reduces POP from `3n+4` to `2n+3` steps. PUSH remains
`2n+3`. Packet order, returned heads, cleanup and opaque ancestors are preserved.

For total matched payload V, r packet pairs and d frame pairs:

| Complete parking charge | PR2635, cited | New controller | Saving |
| --- | --- | --- | --- |
| Steps | 5V+7r+3d | 4V+6r+3d | V+r |
| Reads | 10V+14r+6d | 8V+12r+6d | 2V+2r |
| Writes | 4V+4r+2d | 4V+4r+2d | 0 |
| Unit head moves | 8V+8r+2d | 6V+6r+2d | 2V+2r |

The new table has nine states and 441 entries over the same two tapes and
seven-symbol alphabet. Occupied storage is unchanged. The construction and
all-size induction are in [PROOF.md](PROOF.md); the compiled finite table and
sparse interpreter are in [controller.py](controller.py).

## Evidence and reproduction

Use CPython 3.12 and its standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/reverse-record-parking/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/reverse-record-parking/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/reverse-record-parking
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/reverse-record-parking --check-source-history
```

Another installed CPython 3.12 may replace that path. Direct replay emits
`PASS_REVERSE_RECORD_PARKING` in a generated JSON receipt, bound to every
package file by SHA256. It writes only stdout. No predecessor executable or
mathematical receipt is consumed. The package launcher checks historical
source pins through Git, so that command requires full repository history.

The checker enumerates all 2,047 packets through length ten, totaling 18,434
payload bits. A separate dense-array interpreter agrees with the sparse
interpreter and every expected packet, head, preserved cell and tariff.
There are 21 translated cases through length 16,384, plus unequal and empty
records nested to depths 1, 2, 7, 32 and 129. The largest translated cases
use the sparse interpreter. Thirteen controls cover boundary rejection,
invalid tables, five semantic mutations and the malformed-port scope limit.
Every check remains enabled under optimized Python.

## Scope and source status

POP requires a blank destination port. Unlike the predecessor's preflight,
it may modify an earlier cell before rejecting a later occupied output cell.
That stronger malformed-input guarantee is unclaimed and has an executable
counterexample. Commands are trusted and well-bracketed; arbitrary partial
pops and hostile-command isolation are outside the contract. All owners of
one parking region must use the new record format. No free migration of live
forward-format records is claimed.

This is a physical-interface side result, with an explicit change from the
picker's `portable-replay` card. It can lower a caller's parking subbill after
an actual format-compatible substitution. Packet production, consumption,
invocation dispatch, complete physical reserve, native/frame/precision costs
and the selected supplier's five assumptions remain separate obligations.
No shortest-controller result, selected cold replay, new kappa, complete
multiplication theorem, Lean or Docker run is claimed.

The scientific base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372174)
precedes construction. Live open PRs, recent account work and handoffs,
distinctive main README terms and merged-PR terms were checked. The overlap
cache covered 539 open PRs and 6,558 Discussion records, with complete remote
pagination and incomplete sparse local notes. Arbitrary diffs, private work
and unpublished work remain outside that coverage. Source hashes in
[SOURCES.json](SOURCES.json) bind cited provenance, not reverified mathematics.

## Open next questions

Bind one actual caller's matching whole-packet park/return sequence to this
representation and replace its parking subbill, retaining all serialization,
port production/consumption and backing charges. The first step is to identify
any direct readers of the old forward-format records. A mixed-format live
stack or a caller requiring the predecessor's malformed-port preflight blocks
an automatic substitution. No larger construction search is needed first.

## Credit and implementation limits

Credit ywz65 for PR2635's matched-record interface, finite two-tape model,
published invoice and frame induction, and PR2574/2534/2483/2250/2287 and
their retained physical/native/compiler lineage. Reversed stack storage is
a classical technique. The contribution is this format-compatible valid-input
construction, exact improved invoice, proof and standalone checker. No broad
priority claim is made. New work is Apache-2.0. Independent human and formal
proof-kernel review are unclaimed.

The simulator bounds each tape input at 100,000 occupied cells and each run
at 200,000 transitions. Dense interpretation caps its interval below 500,000
cells. Fixture loops and mutation inventories are finite, and functions have
at most 60 lines. Dynamic Python allocation and dataclass construction are
managed-runtime deviations from Power of Ten rules 3 and 8. Cell/step/table
bounds constrain live data; the mathematical tape machine itself has no
runtime descriptor and applies to every finite valid packet. Warning-strict
normal/optimized runs and in-memory syntax checks supply diagnostics. No
fixed byte-capacity guarantee or new global analyzer configuration is claimed.
