# The frozen native op stream: the specification, and what it covers

## Where the specification is

`research/kappa-lean-verification-20261022/` holds the PR4470/PR4610 lineage's own transcription of
the native word. It is the authority for the record encoding, and it is pinned in
`P19_NATIVE_APPLY.json` by path and SHA-256:

| file | what it defines |
|---|---|
| `NativeCore.lean` | the event kinds, the `step` transition with its frame guards, the `scalarAllowance` tariff, and `checkSegment` — all checked by ordinary kernel reduction |
| `native_generate.py` | the record -> event `encode`, the `paid_index`/`warp_index` catalogues, and the chunked state loop |

Upstream these run under Lean on the word whose payload SHA-256 is
`4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc`
(the word frozen in `research/warp-interface-20261022/`, present here).

## The schema

Event kinds, from `NativeCore.lean`: `0 marker, 1 climb, 2 center, 3 warp, 4 add, 5 scale, 6 clear,
7 copy, 8 adapter`. Persistent roles are `0..631`; role `632` is the owned C₀. A record maps to a
nine-field event `(kind, role, source, input, output, reference, operator, numerator, denominator)`:

| record | event |
|---|---|
| `["phase", name]` | kind 0, no state change |
| `["adapter", name, a, b]` | kind 8, no state change |
| `["climb", tag, role, from, to, rank]` | kind 1: the role moves `from -> to`, `paid[rank] += 1`; must be ascending |
| `["center", a, b, rank, …]` | kind 2: role 632 moves `a -> b`, `paid[rank] += 1` |
| `["warp", ["L", role], op, from, to]` | kind 3: the role moves `from -> to` under operator `op` (negative = inverse) |
| `["scalar", ["add", dst, src, ca, cb], field]` | kind 4, both roles must hold frame `field` |
| `["scalar", ["scale", dst, num, den], field]` | kind 5 |
| `["scalar", ["clear", dst], field]` | kind 6, targets role 632 |
| `["scalar", ["copy", dst, src], field]` | kind 7 |

## What the specification deliberately excludes

`NativeCore.lean`'s own docstring: *"This file deliberately does not model amplitudes, Clifford
phases, or the free noncommutative endpoint algebra."* So it certifies the **frame trace, the paid
histogram and the scalar tariff** — not operator equality.

## What this package does with it

`p19_native_apply.py` re-implements `encode` + `step` + `scalarAllowance` in Python, independently of
the Lean run, and executes both orientations of the frozen word this package prices: 21,449 records
and 20,991 state steps each, every declared input frame equal to the role's current frame, the
persistent roles ending on `canonical.final`, and the paid histogram `{1:2201, 2:412, 3:510, 4:127,
5:40, 8:8}` plus the tariff (158,120 forward / 158,168 backward) **derived** from the trace. As a
control the lineage word derives its own `{1:2201, 2:412, 3:506, 4:135, 5:36, 8:8}`.

The operator side is covered separately by `P19_LOWERING.json`, which binds each emitted gate to the
primitive stated in `research/coded-native-caller/PHYSICAL.md`.

## What is still missing

Encoding the 259 p19 chain gates *into* this event stream — i.e. the producer's own operator/phase
lowering of a unit. That artefact exists upstream, not in this repository, so producer instantiation
of the chain remains an inherited premise.
