# Conditional κ = .00363797977 with a 17-stage signed caller

This package composes the exact [#7112](https://github.com/CrocSwap/integer-mult-bounds/pull/7112)
native word with a new asymmetric signed 8+9 caller. The conditional
claim is `363797977/100000000000`, above #7112 by .000000562650059.
The raw crossing is between .00363797978 and .00363797979.

The caller uses five noncommuting quarter turns and six inverse pairs.
Its grouped idles use arithmetic over Z[1/30]. The exact integer replay
charges caller scale 675 separately from native scale 1125 and rejects
insufficient powers of 3 and 5. All 72 output fields replay, with 13,600
physical native contacts, 110,638 paid positions, and 22,172 productive
fields. See [APPLICATION.md](APPLICATION.md) for the owner, phase,
precision, and finite-tape bounds.

## Reproduction

```sh
python3.12 -B scripts/research_package.py --package research/signed-caller-8x9
```

The replay regenerates the exact caller, verifies rational and integer
Laurent endpoints, and checks physical binding, precision, ordinary
work, the compiler and all 58 outer inequalities. It authenticates
the three completed native catalogue slices on identical word bytes.
Re-run a slice separately with `short_native_catalogue.py --start START --stop STOP`
from `replay/supplier7112/short-caller`. The intervals are [0,1000),
[1000,2000), and [2000,3047). The five inherited assumptions are
`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`,
and `analytic_recovery`, with the selected completed BIT predecessor.
A compiled multiplier execution and independent maintainer review are
outside the local checks.

## Open next questions

[TASK.json](TASK.json) records the next source-bound native sign-capacity
experiment, its relevance and the current obstruction.

## Credit

Rohan Arun with substantial OpenAI Codex assistance. Credits include
DreamingOfClouds for the native and chain lineage, CubeJerry for the
shared native, paired BIT and compiler work, ToikY for the signed rank-nine
caller and #7108–#7110, dillona and Ali Romman for helper splitting and
#7112, and the #7000 application reviewers. Apache-2.0. Upstream source
notices are preserved.
