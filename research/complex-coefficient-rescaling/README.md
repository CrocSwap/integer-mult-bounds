# JP8 cleanup: reuse coefficient work across different magnitudes

**Status: finite complex-supplier circuit improvement / research note; no new
κ.** Rescaling a prepared coefficient between consecutive additions saves
**10,338 real-component primitives beyond equal-magnitude sharing** in the
selected #626 JP8 forward program. The backward program has no eligible joins.

| Complete scalar program | Original #626 lowering | Equal-magnitude sharing (#722 method) | This rescaling lowering |
|---|---:|---:|---:|
| JP8 forward | 257,232 | 237,544 | **227,206** |
| JP8 inverse-transpose | 257,280 | 257,280 | 257,280 |

The 30,026 total saving includes 19,688 already obtained by @ellipsi2 in
[#722](https://github.com/CrocSwap/integer-mult-bounds/pull/722). Only the
additional **10,338** is new here. The comparison implements that PR's
equal-**magnitude** rule, including opposite signs, with the original binary
Horner preparation. Its pinned implementation was inspected; no pending code
is imported. This is an arithmetic operation count, not a runtime benchmark.

## Reproduce

From the repository root, Python 3.11+ and its standard library suffice:

```sh
python3 -I -B research/complex-coefficient-rescaling/verify.py
```

Expected:

```text
PASS_JP8_COEFFICIENT_RESCALING incremental_real_saved=10338 blocks=1015 columns=716 orientations=2 controls=11
```

The command is offline and read-only. It checks all source pins, the binding
to #626's SPEC, every block's primitive count and arbitrary-input map, both
complete scalar projections, the exact positive prefix envelopes and the
committed [certificate](EXPECTED.json). It retains the selected program's
paid-child census. It does not re-prove the unchanged Clifford operations.

Additional adversarial and finite-domain checks:

```sh
python3 -I -B research/complex-coefficient-rescaling/test_verify.py
make selected-record-check
```

## A concrete new block

Forward event indices `[18840, 18843)` contain, in order, at the full frame:

```text
L655 -= 2 * L470
L97  -= (1/4) * L470
L656 -= (1/2) * L470
```

All three magnitudes differ, so equal-magnitude sharing does not change this
block. Prepare `W = 2 * L470`, perform the first subtraction, halve W three
times, perform the second subtraction, double W, perform the last subtraction,
and clear W. Including the entry clear and first source read, this costs 11
primitives per real component instead of 16: **22 instead of 32** for the
complex value. L470 is never written. Arbitrary incoming target values are
preserved with the stated updates, and arbitrary incoming W is erased.

## Circuit and complete price

The domain is consecutive, full-frame cleanup additions
`t_i += q_i * s`, with one unchanged live source s, no `t_i = s`, and nonzero
dyadic coefficients satisfying `|q_i| != 1`. Target updates keep their original
order, including repeated targets. A block may join magnitudes only when their
ratio is an integral power of two. No operation crosses a phase, scalar-kind,
source, or frame boundary. Unit coefficients are excluded to keep this
comparison separate from the unit lowering in #696.

Write `|q_i| = m * 2**e_i`, where m is a positive odd integer, and set
`d(m) = floor(log2(m)) + popcount(m)`. The inherited Horner preparation costs
`1 + d(m) + |e_i|`: entry clear, every source addition, binary doubling and
denominator halving. Accumulation and final clear add two. Thus r separate
macros cost, per real component,

```text
C_separate = r * (d(m) + 3) + sum_i |e_i|.
```

[lowering.py](lowering.py) emits the same preparation for the first magnitude,
one signed target accumulation per macro, `|e_i-e_(i-1)|` doubles or halves
between magnitudes, and one final clear:

```text
C_block = d(m) + |e_1| + 2 + r + sum_(i=2..r) |e_i-e_(i-1)|.
```

There are no extra helper registers, source copies, frame changes, recursive
children or restoration operations. The existing private coefficient stream
is the only scratch. Both real components are counted, so every table entry
is twice its component cost. Unchanged scalar macros are also fully priced;
adapters, wrappers, compiler overhead and recursive calls lie outside this
scalar subcount and retain their inherited costs.

Joining an edge saves
`d(m) + 2 + |e_i| - |e_i-e_(i-1)|` per component. These savings are additive
and do not depend on the other cuts. The planner takes strictly profitable
edges and cuts ties. Therefore it minimizes this explicit prepare/rescale/
clear cost among segmentations in the stated class. This is not an optimum
over other arithmetic circuits, register allocations or supplier designs.

## Exact map, prefix and interface argument

At block entry, clear W. The first Horner preparation gives `W=|q_1|s`.
Rescaling by `2**(e_i-e_(i-1))` gives `W=|q_i|s`; the signed accumulation
therefore gives the original target update. Induction works for arbitrary
source/target values, not only for reachable clean inputs. The final clear
erases W. The independent checker tests all touched-register basis vectors
and a separate incoming W basis vector for every block.

The source's positive envelope is constant throughout a block. The first
preparation is unchanged. Later W rescalings are monotone between their two
endpoint magnitudes, so their envelope is at most
`max(|q_(i-1)|, |q_i|) * envelope(s)`. Each endpoint magnitude is bounded by
the corresponding old Horner numerator. Live-register envelopes agree after
each target accumulation. Thus the maximum over a complete block is dominated
by the old maximum; an aligned-microstep domination claim is unnecessary.
The complete forward and inverse-transpose upper envelopes reproduce exactly
as 64 and 101 bits respectively, below the inherited 192-bit allowance.

**Changed local interface:** W is cleared at block boundaries, rather than
after every macro inside the block. The selected emitter currently advertises
macro-boundary clearing. Integration must explicitly admit this block contract
and refresh its scalar invoices. This package supplies the replacement
primitive circuits and their evidence; it does not silently change that emitter.

All changed reads and writes are at the full frame, on registers whose native
final frame is full. No wrapped helper is used beyond its existing lifetime;
the pinned event stream's wrappers and children remain in their original
positions. The full scalar replay checks all 716 live input columns, including
492 arbitrary helper inputs, in **both separately emitted orientations**.
The inverse-transpose program is not obtained by reversing a forward block.

## Completed finite coverage

The OS assignment seed **39** selected the complex track and JP8 by parity.
There is no random search after that choice, time-based stop or incomplete
solver run. Both fixed 27,909-event programs are scanned completely.

- Each orientation contains 5,909 eligible nonunit cleanup additions.
- Forward: 1,611 maximal fixed-source runs; the separate DP evaluates 18,925
  permitted candidate blocks and reproduces all 1,015 selected blocks covering
  4,249 additions. Of these blocks, 556 contain a magnitude change.
- The accepted edges comprise 2,023 equal-magnitude edges and **1,211 distinct
  magnitude edges**. There are 1,015 incompatible odd-numerator edges.
- All 49 nonprofitable power-of-two edges are cut: 28 tie and 21 cost more.
  For example, `16 -> 1/2` costs two extra real primitives if merged. The
  certificate records every rejected transition class, not just successes.
- Backward: all 5,909 fixed-source runs are singletons; no join is possible in
  this class. This does not exclude other backward-circuit improvements.

[crosscheck.py](crosscheck.py) uses dynamic programming instead of greedy edge
selection and scalar basis propagation instead of sparse row propagation. Its
6,279 basis cases check every emitted block. Eleven primary controls cover
initial/final erasure, signs, rescaling, source aliasing, changed source/odd
numerator/frame, an endpoint-neutral prefix excursion, nonprofitable joining,
and phase boundaries. Four further independent semantic mutations reject.
The tests also cover all 343 triples over a stated seven-value signed domain,
early-ended helpers, endpoint-neutral extra instructions, input corruption and
receipt corruption. These are finite checks, not a formal proof of the full
multiplication theorem.

## Pins, attribution and remaining scope

Base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Selected #626 source:
`660de893d27bb7abd1d5b01b1640207528a5c851`; #622 construction:
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`; retained #543 bit supplier:
`2065fe4f72a914d907f1046603f5a36f17018535`.
[SOURCE-PINS.json](SOURCE-PINS.json) records every consumed source with exact
Git blob identities and full-payload SHA-256 hashes. Gzip container headers are
not mathematical inputs. The canonical word and event hashes are additionally
checked against the preserved #626 SPEC. The checker does not depend on a
future mutable selected-frontier pointer.

Credit to Jeremy Kothe and the #622 Claude Code contributors; Chafik Boukhalfa's
#626 packaging; icekylinx's direct-delivery, scalar architecture and emitter
lineage; DreamingOfClouds' cold-helper and verifier work; Dugongue's preceding
circuits; eumemic's retained bit supplier; and the earlier contributors in
the [source notice](../complex-k492-owner-repair/NOTICE.md) and
[maintainer review](../../docs/research/community-k492-review.md).
Eumemic's #411 is also credited for its earlier explicit paid dyadic
microcircuits; the present result changes reuse between macros.

@ellipsi2's #722 at `a0766ab0fab379e1997fadc3ca157578d57986c1` is the direct
methodological predecessor and comparison. Sagar Thakrar's #696 and #723 alter
single-macro preparation; the latter recodes numerators with signed digits.
No composition with those lowerings is asserted. #681 changes a raw factory,
#698 changes the frame search class and #719 studies a CK rank obstruction;
none is an implementation dependency. See [the claim](CLAIM.md) for their pins.
The final overlap check also found Chris Pagolu's #734 at
`21606831df4b08f79d87fd420c558a520dca571e`, which bounds signed-Horner prefixes
inside each macro. Its separate contribution is credited; this experiment
retains ordinary Horner preparation and instead changes work sharing between
macros. No combined savings with #734 are claimed.

Prepared for **Jeffrey Cox (@namredips)** with substantial **OpenAI Codex
assistance** in research, implementation, proof analysis, testing and writing,
including one scoped AI reviewer who supplied the independent checker. This
does not claim independent human review. New work is Apache-2.0.

The selected κ remains **0.001635527380375392** at the base commit. Native
geometry, paid profiles and global ownership are not redesigned; no new
assembly is submitted. Uniform compilation, common-label/mutable-basis
realization, hosting, precision/tape/recovery, analytic transfer and the bit
supplier assumptions remain inherited. This contribution neither proves a
stronger exponent nor closes those obligations. `upstream/` is untouched.
