# Retain the G20 carry producer in 24 bits

Ali Romman's [PR6503](https://github.com/CrocSwap/integer-mult-bounds/pull/6503)
producer retains at most 26 logical bits between rows. This construction
reduces that bound to **24 bits**, with the same canonical-input validation,
five-bit packet and `L+1` abstract table lookups for a valid `L`-row input.

Claim type: scoped written proof and exact finite construction certificate.
This is a logical state representation result. No runtime or kappa improvement,
physical 24-bit machine, reversible-history reduction or supplier admission
is claimed. The selected frontier and all five framework assumptions remain.

## Construction

The first row's eight input bits determine its entire abstract state, so
retain that bitmap and delay its quotient lookup. From the second row on,
pack the quotient state, eight comparison bits and low-residue metadata
jointly. Empty and first-row states occupy codes 0 through 256. Mature states
use

```
257 + 4096*quotient + 16*comparison_bitmap + 4*residue + 2*radix_high + last_bit
```

For a source quotient component with `m` states this uses `4096*m+257` codes.
At the published source maximum `m=2406`, the complete representation has
9,855,233 codes, between `2^23` and `2^24`. The 24-bit bound is sharp for
this full representation domain, which deliberately includes unreachable
product states. It is not a minimum over reachable or valid-input machines.

[PROOF.md](PROOF.md) gives the all-width encoding and simulation proof.
[codec.py](codec.py) implements the new producer. Its per-call convenience
wrapper accepts at most 65,536 rows; the step and finish interface has no
stream-length cutoff. [TASK.json](TASK.json) records the explicit scope change
from helper-moment research to this backend storage side result.

## Evidence

The exact verifier checks:

- All 9,854,976 mature codes at the largest model, plus every first-row code.
- All 131,072 first-two-row pairs for an actual largest-model column.
- 33,280 mature transition fixtures across all 23 retained source models.
- 3,646 complete streams, totaling 36,902 rows, across all 729 retained source
  columns. Every decoded prefix matches the unpacked floor recurrence, and
  every final packet matches modular arithmetic. The longest stream has
  4,097 rows.
- Seventeen invalid-domain/stream controls and two faulty-encoding collision
  controls.

The source quotient tables are inputs. The verifier does not run the
predecessor's reachability, partition refinement or minimality checks. Those
results and the carry/packet identity retain their predecessor attribution.
The new verifier prints a generated JSON receipt bound to all package bytes
and its declared live input. No receipt is written by hand.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/g20-carry-state-codec/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/g20-carry-state-codec/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/g20-carry-state-codec
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/g20-carry-state-codec --check-source-history
```

The local absolute interpreter path can be replaced by another CPython 3.12.
Each registered check has a 120-second timeout. The expected scientific status
is `PASS_G20_CARRY_STATE_CODEC` with `retained_bits=24`.

## Sources and limits

Scientific base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priorities revision 8,
selected PR6030. [SOURCES.json](SOURCES.json) pins the main source-column
input and retains the exact PR6503 proof, descriptors and table bytes at
`03e47a1a258f87d4a5bce86292f1a1b815ed0f52`. The three upstream files are
included unchanged in `inputs/`; no pending Git object or network fetch is
needed to run the new verifier. Their SHA256 pins are checked before use.
The source-history preflight covers declared history pins; the external
predecessor's head is attribution for retained bytes, not a required ancestor.

The storage count excludes immutable coefficients/tables/descriptors, the
current input row, transient arithmetic and decoding scratch, and output
storage. Python object memory is not the logical bit count. Head travel,
lookup circuitry, scratch cleanup, arbitrary dirty restoration, reversible
history, native execution, precision, stock, compiler and complete caller
cost remain unpriced here. The full signed moment is unchanged.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19370123)
records live overlap checks and their limits. The separate contemporaneous
initialized joint-history investigation starts from PR6531 and asks about
inverse fibers; this package changes the forward state representation only.
No source construction was audited as the deliverable.

## Open next questions

1. Price one largest-model codec step on an actual tape or Boolean circuit,
   including decoding, table access, cleanup and head return. The logical
   state saving alone does not establish a physical saving.
2. Determine whether one actual column's reachable joint states admit fewer
   than 24 bits. Start with a fixed column and its shared row alphabet;
   preserve validation and packet semantics. The current product-domain
   lower bound does not answer this. Coordinate with the separate claimed
   inverse-history work before extending it.

Structured questions and blockers are in [TASK.json](TASK.json). Further
construction rounds require a complete physical bill; this result does not
justify a wider helper search.

## Credit

This contribution was produced by Nick Petalas. Credit Ali Romman for
PR6503's quotient tables and producer contract, PR6474's carry invariant
and packet construction, and PR5820's sparse routes; ToikY, Nick Petalas,
Tekalign, JoyboyBrian, Kyu and the retained G20/native/ROW lineage retain
their source credit. Mixed-radix encoding and delayed evaluation are
classical. The new contribution is the concrete 24-bit representation,
its state simulation proof and executable.

New work is Apache-2.0. Independent human and formal proof-kernel review
are unclaimed.
