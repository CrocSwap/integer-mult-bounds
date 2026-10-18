# A physical four-ADD boundary with a shared sign-fill guard

The forward A13–A16 block of the frozen PR3042 words admits a local bit-layer
saving of **6,144 CNOTs**, with the same Toffoli count and bit storage as four
separate PR3081 wired half-ADDs. This package also binds the block's completed
physical frame operators to a sufficient **quarter grid and `P+5` signed bits**
for signed P-bit integral entry components.

This is a finite local operator/caller result, not a new kappa or supplier
admission. The four rank-one frame climbs remain paid. Their implementations,
preparation interiors, routing, clean-stock production, hosting and the later
consumer of fractional targets are not supplied or priced at zero.

## Exact object and result

Both providers have this zero-based A slice, in compact native role numbers:

```text
A12     warp L83, +52, frame85 -> frame136
A13     L126 -= L83/2, frame136
A14     L153 -= L83/2, frame136
A15     L164 -= L83/2, frame136
A16     L218 -= L83/2, frame136
A17     warp L83, -52, frame136 -> frame85
```

Frame85 is `span(382)`, frame136 is `span(45)`, and each target starts at
frame zero. The native emitter inserts one paid rank-one climb immediately
before each target's ADD. Completing all four climbs before the first ADD gives
the same linear operator, since a target climb commutes with each other target's
ADD. This is an equality of completed operations, not a hosting-window theorem.
The source guard is borrowed only after those climbs finish.

At the end of zero-frame preparation, the target rows are exactly:

```text
Y126 = (L126 - L127 + L164 - L165)/2
Y153 = (L153 - L154 + L218 - L217)/2
Y164 = (-L164 + L217 + L126 - L154)/2
Y218 = (-L218 + L165 + L153 - L127)/2
```

Here `L` denotes entry arrays before preparation. All eight target-input roles
start at frame zero. The source L83 is unchanged before its entry adapter.
Reverse exact row propagation through every preparation instruction proves
these statements, including independence from all other dirty entry fields.
This does not bound temporary values inside that preparation.

For the native conventions in `vendor/bw_phases.py`, write `Tq` for the
canonical frame of `span(q)`, `Cq` for the old source operator, and `K52` for
the literal warp monomial. The physical source at the ADD cut is

```text
M L83 = T45 K52 T382^-1 T382 C382^-1 L83
      = T45 K52 C382^-1 L83.
```

Every column of M has exactly one Gaussian-unit entry. Thus M preserves the
integral component grid and component supremum norm. Each target at that cut
is `T45 Yr`, and the block returns

```text
T45 Yr - M L83/2,       r = 126, 153, 164, 218.
```

After the bit layer restores its source and the closing physical warp executes,
the source equals its pre-warp entry-adapted state exactly. Global phases are
included in both implementations of this check.

## Grid, range and sharp controls

A rank-one `T45` column has two complex entries with real and imaginary parts
of magnitude 1/2. Each real output row of a completed target has sixteen
distinct quarter-coefficient terms from preparation and one half-coefficient
term from L83. Its exact component row l1 norm is **9/2**. The four targets
therefore have 4,096 checked real rows. Their component grid is `1/4 Z`, while
the physical source components remain in `Z`.

If entry real and imaginary components have magnitude at most
`B = 2^(P-1)`, the prepared target is bounded by `2B`, the converted target by
`4B`, and the completed ADD by `9B/2`. At two fractional bits their encoded
magnitudes are at most `18B < 32B = 2^(P+4)`. Signed width `W=P+5` therefore
suffices at these macro endpoints. The encoded source is a multiple of four,
so in particular its low bit is zero, as the half-ADD caller requires.
This proof holds for every P >= 1. The circuit generator supports P <= 251.

The extra physical fractional bit matters. Setting just the real component
of entry L126 at coordinate zero to one, with every other entry component
zero, gives real output L126[0] = **1/4**. Omitting the paid climb produces the
wrong half-grid model. At P=5 a row-sign witness with components of magnitude
15 attains output `135/2`, encoded as **270**. One less total bit permits only
255. `RESULT.json` records both controls. The norm is sharp; a claim of optimal
bit-circuit size is not made.

## Shared guard and complete local bill

PR3081's wired signed half-ADD uses one zero source guard bit, fills it from
the source sign, applies the inverse MAJ/UMA adder, and clears the fill by its
inverse CNOT. The target's fractional bits remain output data.

For four ADDs with the same writable source, use:

```text
separate calls:  (fill; ADD target j; unfill) for j = 0..3
shared guard:    fill; (ADD target j for j = 0..3); unfill
```

Each MAJ/UMA adder restores its source and carry. While filled, the source's
wired active bits represent its exact signed half. Keeping that representation
between the four ADDs is legal under the local exclusive-source contract.
The final unfill restores every original source bit, including both fractional
zeros. One carry is reused and returned zero. All four quarter-grid target
outputs stay live. No target fraction is cleared or rounded.

For one real component, the separate baseline has `16W` CNOTs and `8W-8`
Toffolis. The shared version has `16W-6` CNOTs and the same `8W-8` Toffolis.
Both use `5W+1` bits. The baseline gate list is checked literally against four
rewired copies of PR3081's frozen generator, rather than an invented cost table.

At P=64, W=69, across 1,024 real components:

| ADD layer | CNOTs | Toffolis | Array bits plus one reused carry |
|---|---:|---:|---:|
| Four separate calls | 1,130,496 | 557,056 | 353,281 |
| Shared guard | 1,124,352 | 557,056 | 353,281 |
| Saving | 6,144 | 0 | 0 |

These are logical bit-gate counts with explicit indexed connections, not
physical routing or integer-multiplication runtime. The bill starts with five
appropriately encoded, disjoint arrays already available. Sign extension,
source adapters/warps, the preparation, four rank-one children, carry-stock
production and eventual target consumption remain additional obligations.
Retiming has no claimed physical hosting cost bound. Unknown costs are not zero.

## Evidence and reproduction

Both frozen native words are transported and emitted afresh. The verifier checks
the literal paid-climb/ADD/warp chronology and rejects an omitted child.
`operators.py` derives sparse Gaussian operators and exact preparation rows.
`native_audit.py` independently executes the retained native elementary
Clifford circuits on all 512 Gaussian input columns, without telescoping the
source adapter and warp. It checks the target, source and source closure,
including phases. The two implementations share conventions and a contribution
owner; this is not independent human or formal-kernel review.

`fanout.py` emits actual CNOT/Toffoli lists. They are serialized and read back
before a packed-state evaluator and a separately written bit-array evaluator
run the physical operands. Both baseline and shared circuits agree on the
entire final bit state. Fifteen complete vector fixtures at P=3,5,64 supply
15,360 four-target component calls. Behavioral tests also check 1,200 coupled
four-bit signed cases, the maximum supported width, insufficient grid/range,
missing sign fill/cleanup, dirty carry, source phase, literal word mutation,
source corruption and occupied-output preservation.

Python 3.12 and the standard library suffice. With RUN an existing external
session directory containing `tmp/`:

```sh
TMPDIR="$RUN/tmp" python3.12 -B scripts/research_package.py \
  --package research/rank7-physical-a13

# Optional retained regenerated native words, bit programs and diagnostics.
TMPDIR="$RUN/tmp" python3.12 -W error -B \
  research/rank7-physical-a13/verify.py --work "$RUN/a13"
```

`--work` refuses an existing directory. Default temporary outputs are removed.
The registered runner isolates Python bytecode caches. For a direct replay,
use a fresh `PYTHONPYCACHEPREFIX` as well if the source directory has caches.
The verifier compares mathematical JSON content, not regenerated gzip headers.
`VENDOR.json` binds every retained input by commit, Git blob and raw SHA-256.
`CHECKS.json` records the local environment and checks.

## Scope decision

This follows the released [PR3084 handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18984243),
not another root or fixed-frame census. The original `independent-moment` card
is changed to a completed physical-operator alignment implication and a small
caller improvement. PR3084 established a free-monomial scalar grid, explicitly
not the physical frame boundary. PR3081 supplied the separate guarded bit
caller. Neither result is contradicted or promoted into a supplier here.
Canonical base is `d8e0f83f00191df62174b641e9fff055c357f641`, priority revision 6.
The selected kappa remains 0.001672660197076918.

## Open next questions

Can this exact local block be admitted in a hosted finite-precision execution?
First bind its five arrays and one reusable carry to named physical buffers,
implement the preparation and the four completed children with internal grid
and range ledgers, and trace the retained quarter-grid targets to their actual
consumer. Price routing, stock and the retimed child windows. This can change
whether the local gate saving is usable; another fanout census cannot answer
it. Stop implementation expansion if that ownership/consumer bill is missing.
The full program, backward orientation and approximate recursive outputs remain
outside this contribution.

## Credit and license

Nick Petalas contributed this physical-boundary proof and shared-guard caller.
Credit PR3084/3083 for the reference-grid handoff, PR3081/3080/3078 for the bit
caller chain, dcharb78/PR3042 for the frozen words, Jeremy Kothe/PR3015,
Marius-Paul Dumitrean/PR2979, Cinna Davis/PR2226, icekylinx and the retained
native/geometry/owner lineage. The frozen notices preserve their attribution.
MAJ/UMA addition is due to Cuccaro, Draper, Kutin and Moulton. No novelty is
claimed for generic common-source guard sharing or rank-one Fourier arithmetic.
Apache-2.0. Development used substantial automated assistance; independent
human review remains open.
