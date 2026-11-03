# Restore the complete G20 carry producer

All 23 released quotient components now have exact inverse transitions. The
worst transition merges 20 predecessor states, so **five history bits are both
necessary and sufficient** under the stated known-letter transition contract.
The full producer uses at most **12 history bits per input row**, including the
eight input comparisons, then clears every history record and logical work
register by a reverse pass. A complete 373,248 source-row census improves
the separate 13-bit estimate to 12. A 3,328-predecessor witness proves this
12-bit width sharp on the stated unrestricted product-state row contract. It preserves the packet and arbitrary dirty output.

This fills a logical cleanup gap in PR6503. It retains every current source
column: 444 routes, 3,552 columns and 729 distinct columns. The new interface
requires immutable rows that can be read backwards and returns five packet bits
plus one validity bit. It is not an automatic physical-consumer replacement.
No new kappa, physical runtime gain or global minimum-state claim is made.

[PROOF.md](PROOF.md) states the contract and proof. [RESULT.json](RESULT.json)
records all 304,894 inverse edges, largest-fiber witnesses, 3,645 column/radix
cases, 49,449 exhaustive active q=3 inputs, 1,472 dirty-output cases, 23 cases
at 4,097 bits and rejection controls. Invalid canonical inputs also return all
work to zero and report a zero validity bit. The predecessor source proof and
all exact input bytes remain in inputs.

The complete logical protocol uses 2L row accesses, 7L+1 table queries and at
most 88L+5 table bits read. It adds 1,525,010 inverse-table bytes and 17,093
metadata/witness bytes to the retained 464,866-byte forward table. Static
storage, history, input retention and return access are explicit costs.
These are table-interface counts, not Boolean-gate or physical tape tariffs.
Python allocation, cursor and lookup scratch are not claimed to fit 26 bits.

Run with CPython 3.12, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/g20-reversible-carry
```

Both registered modes reproduce the same exact receipt. Committed-byte/mode,
official export/input, read-only Git-free empty-PATH replay and source-corruption
checks are required before publication. The optional full-history preflight is
not claimed in this shallow checkout. No Lean, Docker, independent human review,
materialized multiplier or framework admission is claimed. No known fragile
workaround is used.

Credit PR6474's interleaved carry invariant, PR6503's compact quotient machines,
PR5820, ToikY, Nick Petalas, Tekalign, JoyboyBrian, Kyu and the full G20/native/ROW
lineage. The generic reversible method is standard. Ali Romman with substantial
OpenAI Codex assistance; Apache-2.0. Selected PR6030 remains unchanged.

## Open next questions

Lower this restored protocol to the actual tape layout and price both directions
of a literal lookup. Join it to a preserved source cache and an actual packet
consumer. If that consumer changes the source rows, specify a separate recovery
or packet-retirement contract. See TASK.json for the bounded next step.
