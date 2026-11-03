# Compact G20 carry machines

All **444 released routes / 3,552 columns** now have a packed finite-table carry producer. The maximum state retained between input rows falls from PR6474's separate-counter bound of **78 bits to 26 bits**. The producer keeps the same interleaved input, odd-radix validation, canonical low-input checks and five-bit carry packet. This is a concrete state/storage tradeoff, not a runtime or kappa gain.

The 729 distinct columns use 23 shared quotient models. Their reachable-state closures and complete output refinements are in TABLES.json.gz. Each quotient component is minimal for its declared aggregate alphabet and integer quotient output. This does not prove a minimum for the full packet machine, its restricted valid inputs or its physical implementation.

The runtime uses **464,866 bytes of packed tables**, plus **2,679 bytes of metadata**. It reads the packed bits directly; no proof table is needed during production. These costs are explicit and are not free finite control. The largest quotient component has 2,406 states, stored in 12 bits. The other 14 bits cover eight input comparisons, the numerator residue, one radix residue bit, stream phase and final radix bit. Input-row buffering, digit calculation and table addressing are transient work outside this between-row count. Physical tape/head costs remain open.

Run `python3.12 -B scripts/research_package.py --package research/g20-compact-carry-machines`. Normal replay is read-only. `verify.py --write` regenerates every table, packed artifact and receipt. The independent certificate checker uses floor inequalities for every transition, validates reachability and the complete refinement history, and checks every compact and packed lookup. It does not trust a table hash alone.

The checks include 17,760 source-column cases, all 49,449 active q=3 inputs, seven 4,097-bit fixtures and seven rejecting controls. A separate modular-inverse oracle checks the emitted packet. Equality of the packet preserves the existing runtime-quarter-carry consumer interface; that unchanged physical consumer is not re-audited here. No low-cache access, complete physical producer/consumer caller, new native result or selected-frontier change is claimed.

## Open next questions

Bind the packed producer to the actual low-cache layout. Compare the full table access and input delivery cost with PR6474's explicit counters, including scratch reset, head return and the carry consumer. The smaller retained state can help that comparison, but does not decide it. The original owned fields, source roles and all five framework assumptions remain unchanged.

## Credit

[PR6474](https://github.com/CrocSwap/integer-mult-bounds/pull/6474), head `63c65d845d84ae47fa8264c48c289e55c44cdc76`, supplies the interleaved threshold identity, low-input checks and packet interface. This package changes its representation and supplies explicit compact tables; it does not claim the identity again. PR5820 and ToikY supply the released bases and routes. Nick Petalas, Tekalign, JoyboyBrian and all retained G20/native/ROW authors keep their credit. Classical reachable-state enumeration and Moore partition refinement supply the table method. Kyu's packed-carry automaton concerns a different repair interface. Ali Romman with substantial OpenAI Codex assistance; no subagents. Apache-2.0.
