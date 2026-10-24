# A transported CRT key on binary tapes

**Fixed finite implementation and tape-action census; no new κ or uniform
machine-time bound.** This takes the physical-key handoff in
[PR4716](https://github.com/CrocSwap/integer-mult-bounds/pull/4716), exact head
`d9913fe24f119f9d431f324dbbe7d90de409a856`. Its unchanged caller is retained in
[`vendor/pr4716-caller.py`](vendor/pr4716-caller.py), with origin/hash in
[`VENDOR.json`](VENDOR.json). The three main-branch reference modules are pinned
in [`SOURCES.json`](SOURCES.json). No cached foreign Git object is needed.

The new [`engine.py`](engine.py) evaluates one literal exceptional key
`T(S^-1(q))`. Current coordinates are copied anew at each of its three source
queries. CRT reconstruction, modular updates and lookup selection use binary
tape reads and bit flags. A complete 544-bit read-only source table is scanned
at every query; no dynamic data word indexes a Python table. Work and scratch
are erased and every head returns. The program never invokes the predecessor
oracle or converts a runtime data word to a Python integer.

## Exact boundary

This is PR4716's transported root with widths `(4,4,5,5)`, moduli
`(11,13,17,19)`, root target axis 2, reservoir axis 3, row 6,
`H=G=1`, `K=5`. The geometry is below production constants. There are 17 active
Word bits `(u,t,y)` with `y` of width 15 and one back spectator. The input and
output are the actual 18-bit **MSB-first** address encoding
`u,t,y14,...,y0,back`; the spectator is physically copied and preserved.

Five fixed tape roles are reused: protected input (18 bits), protected ROM
(544 bits), owned output (18 bits), private work (18 bits) and private scratch
(64 bits). Output, work and scratch start clean. No arbitrary dirty-scratch
contract is claimed. Each tape has a fixed bounded extent and begins with its
head at cell 0. Each read, write and one-cell move is an event. `seek` emits
every intervening unit move; it does not jump over cells for free.

Pre-admission validation of these fixed lengths/bit symbols, Python object
allocation, parameter/descriptor compilation, modular-inverse setup, ROM
generation and observer logging are outside the invocation census. The
read-only ROM must already contain the source-authenticated row-6 tables for
all 17 offsets. It is an explicit borrowed input, not a free general-purpose
data oracle. This does **not** execute PR4192's uniform arena compiler or
adopt PR4650's all-parameter tariff.

The Python program represents the fixed loop schedule and Boolean finite
control. Exact event totals exclude control-instruction time. Thus they are
**tape actions**, not total bit steps, wall-clock predictions or a bound for
arbitrary `p,ell`. In particular this is not a certificate of
`E(p,ell) = 2^(4 ell)(p+2)^16`.

## Why the local arithmetic is the intended key

The source-bound physical descriptors, expressed as little-endian bit
positions in current `y`, are

```
a: (12,0,1,2)     b: (3,4,5,6)     target: (7,8,9,10,11).
```

The verifier derives them from the retained placement, including the
transported high bit; they are not selected from a successful witness. In the
MSB-first work tape `y[j]` is cell `16-j`.

For valid `a<11,b<13`, the retained cached CRT identity specializes to
`k=(78a+11b) mod143`, then `offset=5k mod17`. Invalid padded left coordinates
disable the shift by using offset zero. The verifier checks the constants
against the original modulus-only setup. `add_constant` is the binary full
adder. `remainder` shifts one input bit into the remainder and subtracts the
fixed modulus if necessary; its invariant is `0<=r<m`. The extra bit ensures
`2r+bit` fits. The accumulator's maximum is 1335, the first remainder uses nine
bits, the product is at most 710, and the final remainder uses six bits.
These widths retain all intermediate information. Every register read/write
crosses the same charged scratch tape, including movement between regions.

The ROM lookup compares all six offset bits and all five target bits against
each fixed scan position, reads that ROM cell, and continues to the end.
It requires exactly one match. Invalid target values 17 through 31 are part
of the retained padded permutation; they are not rejected or truncated.

With `G=H=1`, subtraction and addition to `u,t` both reduce to XOR. The inverse
visits source steps `9,8,...,0`. Its two `y` update forms are a conditional
`±2^9` and `-2^10`, propagated bit by bit through bit 14 and reduced modulo
`2^15`. The other updates read the latest `u,t,y9`. The final `T` obtains a
third fresh source query before toggling `y9`. This is the literal inverse
word, without the good-set simplification. The proof of the original compact
word and its CRT semantics remains predecessor work.

## Evidence and discriminators

[`verify.py`](verify.py) compares 24 deterministic physical addresses with
the unchanged caller at all three query epochs, including invalid-left,
padded-target and high carry/borrow boundary cases. Borrowed input/ROM bytes,
both private tapes, every head and the copied spectator are checked. Its
separate event interpreter reconstructs every tape from initial contents,
rejects discontinuous head positions or wrong reads, and checks the final
state against the execution. [`RESULT.json`](RESULT.json) freezes exact
operation/phase counts and a digest of every case's complete event stream.

The two original stale-offset discriminators now execute as physical tape
programs:

| Input `(u,t,y)` | Current `y` at the three queries | Key | Tape actions |
|---|---|---|---:|
| `(0,1,4)` | `4,31236,31236` | `(0,1,30724)` | 171,252 |
| `(1,1,4)` | `4,4,31236` | `(1,1,30724)` | 171,266 |

Across the 24 cases, the recorded range is 170,140–171,266 actions. These are
measured cases, not asserted extrema over all addresses. The bit flags and
the predecessor's Python oracle are not included in these tape-action counts.

Nine controls reject stale offsets at the second or third query, dropped high
carry/borrow, omitted private clearing, omitted head return, a wrong CRT
weight, failure to disable an invalid left coordinate, a wrong transported
descriptor and a missing unit-move ledger event. A separate Codex agent
reviewed the runtime data/control separation and independently replayed
unit events and endpoint ownership. That is AI review, not independent
human acceptance or formal verification.

## Reproduce

Python 3.12, standard library, approximately a few seconds:

```sh
python3.12 -B scripts/research_package.py --package research/crt-transported-key-tape --check-only
python3.12 -B scripts/research_package.py --package research/crt-transported-key-tape
python3.12 -O -B research/crt-transported-key-tape/verify.py
python3.12 -B scripts/check_research_commit.py --package research/crt-transported-key-tape --check-source-history
```

Only explicit `--write-result` authors the receipt; ordinary replay compares
it. Source authentication precedes compilation, and the verifier compiles
authenticated bytes rather than trusting predecessor bytecode caches. The
committed export supports the same direct replay without Git.

## Family decision

The inherited #4100/#4169/#4716 logical key and current-state semantics are
the reference. This adds one complete fixed invocation's tape representation
and measurable traffic. Setup/cache production, a uniform control compiler,
actual scanner-to-key/repair continuation, many targets and the full tape
tariff remain **unknown here**, not zero-cost components. The decision is to
stop at this local implementation; a larger parameter census would not close
any of those obligations.

## Open next questions

1. Replace a fixed ROM scan's control loops by encoded tape counters and
   charge parameter decoding, ROM production and restoration. This matters
   for a uniform `E(p,ell)` bound; the missing uniform compiler and control
   cost proof block that claim.
2. Join one key invocation to the scanner-owned address port in #4637,
   counting every adapter/copy and preserving its ownership contract. This
   matters for an actual repair caller; the producer/mask and full repair
   continuation are not executed here.

These structured next steps are also in [`TASK.json`](TASK.json). The selected
conditional κ remains 0.00302015 and no selected files are changed. No complete
frontier replay, Lean, Docker or full physical repair was run.

## Credit and coordination

Cinna Davis supplies #4100's CRT construction; Hiroki KUMAZAKI supplies
#4169/#4174's inverse/placement and #4716's caller, cached reconstruction and
discriminators. Ryanson Jonathan's #4328/#4409 motivate the key cost boundary;
unpaidmoon's #4377/#4644/#4650 provide the complementary counting and unary
join results; ToikY supplies #4192/#4201/#4208's arena, scanner and producer.
Jose Manuel, John-Michael Smith and Douglas Colkitt retain the underlying
physical-repair/compact-control lineage, and codyw912's #4637 identifies the
scanner-mask port. This does not claim the first physical repair or a new
reverse-key formula.

Prepared by JoyboyBrian with substantial OpenAI Codex assistance, including a
separate agent accounting review. Apache-2.0. The canonical claim is
[this scoped comment in Discussion4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19130274).
