# One fewer main-state bit for an initialized G20 carry column

This contribution was produced by Nick Petalas.

For the released scale-free port 8 inverse column 1,
`(-1/4,0,-1,0,-1,0,0,-1)`, a joint initialized representation uses
**19 main-state bits instead of the cited predecessor representation's 20**.
Its active closure has exactly 23,789 states and 761,248 transitions. The row
history alphabet needs at most **3,248 values**, compared with the predecessor's
3,328-element unrestricted product-state witness. Both still need twelve bits
per independent fixed-width row record.

Claim type: finite construction certificate with a scoped written all-width
proof. The changed hypothesis couples the quotient thresholds to the four
active input comparisons from their initialized state. The four inactive
comparisons remain charged separately. This is a new representation and domain;
it does not audit or contradict the predecessor's sharp unrestricted-domain
history result. No global state or history minimum is claimed.

[PROOF.md](PROOF.md) defines the exact boundary, integer-prefix invariant,
finite certificate, packet, literal inverse and complete component ledger.
For `L` rows, a concrete mixed-radix history register needs at most
`bit_length(3248^L-1)` allocated bits. Its growing-integer arithmetic is an
additional physical cost. The displayed ideal packed table layout needs
5,067,117 bytes before descriptors, alignment and addressing. Table storage,
lookup scratch, input retention, cursor, residue and radix bits are additional
to the main state. A saved state bit does not establish a total-space saving.

## Evidence and reproduction

The source column is bound to canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a` through [SOURCES.json](SOURCES.json).
The independent edge oracle appends bits to full integer prefixes and checks
all states and edges by integer division. Every inverse edge is checked.
The checker also tests canonical packets against a direct modular oracle,
all dirty six-bit outputs on a bounded domain, 32,768 arbitrary three-row
streams, complete returns through 4,097 rows and ten rejecting controls.
Exact counts and source/code hashes are generated in [RESULT.json](RESULT.json).
No predecessor scientific suite is run.

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/g20-initialized-joint-state
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/g20-initialized-joint-state --check-source-history
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/g20-initialized-joint-state/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/g20-initialized-joint-state/verify.py
```

The generic hook runs both warning-strict scientific commands. Each requires
exact equality with the generated receipt. To regenerate a receipt after an
intentional source change, add `--emit` and redirect stdout outside the checkout.
The marker is `PASS_G20_INITIALIZED_JOINT_STATE`. The executable caps streams
at 4,097 rows; the all-width statement rests on the written induction.
[ENGINEERING.md](ENGINEERING.md) records resource bounds and verification limits.

## Limits and remaining obligations

This is one logical carry component, preserving immutable input rows, the
five-bit packet plus validity and a dirty output through complete return.
No packed backend, physical Boolean/tape tariff, full G20 caller, compiler
admission, new kappa or complete multiplication theorem is supplied. Native,
precision, stock, tape, analytic/outer and all five selected assumptions remain.
The selected PR6030 frontier is unchanged. Independent human and formal
proof-kernel review are unclaimed.

The local expansion decision is to stop at this component result. A larger
search needs evidence that its complete table, lookup, history arithmetic and
consumer bill can benefit an actual caller. Unknown costs are not zero.

## Open next questions

1. Can a physical lookup implementation make the new table competitive with
   the retained separate quotient/comparison producer? Start with one actual
   forward/return lookup and include static storage, addressing, scratch and
   head return. Physical tariffs and a matched caller are the blockers.
2. Can canonical-prefix restrictions further reduce this column's joint state
   or row history? Start by distinguishing merely initialized prefixes from
   prefixes extendible to valid complete inputs. A changed count must preserve
   arbitrary low inputs and complete restoration. No continuation is reserved.

## Credit and related work

Credit Ali Romman's [PR6531](https://github.com/CrocSwap/integer-mult-bounds/pull/6531)
for the reversible-history contract and its explicit warning that reachable
canonical prefixes may correlate the states. Its quotient and producer sources
are [PR6503](https://github.com/CrocSwap/integer-mult-bounds/pull/6503) and
[PR6474](https://github.com/CrocSwap/integer-mult-bounds/pull/6474).
[PR5820](https://github.com/CrocSwap/integer-mult-bounds/pull/5820) supplies the
literal column. Their exact heads, source and retained ToikY, Tekalign,
JoyboyBrian, Kyu, Nick Petalas and G20/native/ROW lineage are in the proof.
Finite-state reachability, predecessor ranks, mixed-radix coding and
compute/copy/uncompute are classical. General literature priority is unclaimed.
The new contribution is this finite joint closure, its smaller representation
and row-record alphabet, and the accompanying certificate and proof.
