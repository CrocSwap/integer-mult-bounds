# Route a marked payload from an encoded CRT leaf

The live encoded CRT leaf now drives the existing Beneš row query and
literal binary radix mover for one padded right-axis fiber. On the
retained non-root fixture, slots 0 and 1 exchange their payloads and
padded slots 2 and 3 preserve theirs. The inverse restores the same
physical payload tape, its keys, the encoded source, and their heads.

| Boundary | Source coordinates | Payload tags in physical order |
| --- | --- | --- |
| Input | (3, 2, 1, 1) | 293, 730, 905, 3681 |
| Forward | (3, 2, 1, 0) | 730, 293, 905, 3681 |
| Inverse | (3, 2, 1, 1) | 293, 730, 905, 3681 |

The input uses moduli (5, 7, 3, 2) and declared widths (3, 3, 2, 2) from
the `nonroot_roundtrip` case of [#5625](https://github.com/CrocSwap/integer-mult-bounds/pull/5625).
Each payload is an opaque 12-bit record in the binary radix format.
The replay checks the entire frame, including its two-bit position
keys and its physical backing identity. It also checks the source's
metadata and inaccessible historical tail.

## Source and payload join

1. Acquire the retained encoded iterator and its clean private roles.
   Select its last leaf at the level with unary half length one, with
   a nonempty axis prefix. Retire earlier numerical leases without
   writing their coordinates. Both directions pay for every visited
   lease, including the skipped leases.
2. While the selected lease is live, scan the actual right record for
   its unary width and modulus and copy the offset from the numerical
   result stream using the existing precision guide. The measured
   fields give width 2, modulus 2, precision 5 and offset 1 in both
   directions. The source and result return to their entry heads
   with their bytes preserved before source staging.
3. Run the unchanged encoded Beneš producer on those framed headers.
   For each physical input slot, follow all produced rows by the
   existing row-bit query. The adapter keeps the slot address on a
   binary tape, walks the target bit from low to high and back, and
   writes the destination as an MSB-first key in the allocated
   radix cells. It reads the row tape backwards by rows for the
   inverse, keeping the bits of each row in wire order.
4. Run the literal radix pass once per unary width mark. Its stable
   last-bit pass rotates that bit to the front, so two passes sort
   the two-bit destination keys and return them to their initial
   orientation. Each tag moves with its key on the actual bit tape.
   Stage the coordinate result, retire the numerical lease, commit
   the source and clear the adapter and bucket storage.

For the selected leaf the left modulus and coordinate are 3 and 1.
The direct CRT oracle solves 3c ≡ 1 modulo 2, giving c = 1. It maps
valid positions x to (x+c) modulo 2 and fixes the two padded positions.
The offset depends on the left child, which is preserved here. The
inverse therefore uses the same offset and the switch layers in reverse
order. Every switch layer is its own inverse, so the reversed layer
product undoes the forward product. The independent oracle checks the
nonidentity forward placement before checking exact restoration.

The input positions are enumerated by an encoded counter. The adapter
uses the existing key cells for storage and derives its addresses from
physical positions. Fixture serialization and all independent
observers are outside the measured runtime.

## Measured work and storage

| Quantity | Forward | Inverse |
| --- | ---: | ---: |
| Encoded source symbol actions, including numerical work | 113,295 | 372,489 |
| Adapter symbol actions | 3,481 | 3,817 |
| Beneš producer instructions | 2,363,816 | 2,363,816 |
| Payload adapter bit actions | 1,694 | 1,694 |
| Literal radix instructions, including finite control | 43,162 | 43,162 |
| Retained private symbol roles | 136 | 136 |
| Retained private symbol cells | 2,253 | 2,633 |
| Retained bucket bit extent | 208 | 208 |
| Retained radix register bits | 144 | 144 |
| Retained Beneš registers | 15 | 15 |

The symbol counts include header and key-address preparation, row
scans, source staging and retirement. The bit counts include the
physical key writes and bucket initialization and retirement, with
radix instructions counted separately. Both directions' private roles
remain retained for the measurement. They share one 57-cell source
and the original payload tape, whose visited extent is 183 bits.
These are observations in the respective execution models. A common
literal tariff for the combined source controller and payload path
requires further lowering.

## Replay and source credit

From a checkout or an official Git-free export with the declared
inputs, run:

```sh
python3.12 -I -B research/encoded-crt-leaf-payload/replay.py
```

[RESULT.json](RESULT.json) records the observed headers, exact
endpoints, cost and backing. The checks include a separate direct CRT
oracle, noncommuting layers that distinguish reverse traversal, a
truncated layer stream that must fail, and suppressed switches that
must fail the forward-placement check.

[INPUT-PINS.json](INPUT-PINS.json) binds the runtime to canonical main
`e54523517d0f03e58352e647c403a5af3e525a57` and four byte-exact
runtime files from CubeJerry's [#7352](https://github.com/CrocSwap/integer-mult-bounds/pull/7352)
at `8c0e55c9ba25ff2c8199b01539a4d56ae71a1473`. The forward writer
is also byte-identical to the one in [#7351](https://github.com/CrocSwap/integer-mult-bounds/pull/7351).
Ali Romman's [#5625](https://github.com/CrocSwap/integer-mult-bounds/pull/5625)
supplies the fixture and the paid retirement boundary.
JoyboyBrian's [#5092](https://github.com/CrocSwap/integer-mult-bounds/pull/5092),
[#5496](https://github.com/CrocSwap/integer-mult-bounds/pull/5496)
and [#5015](https://github.com/CrocSwap/integer-mult-bounds/pull/5015)
supply the encoded producer, physical row query and literal payload
consumer, respectively. OpenAI Codex and ChatGPT Pro materially assisted
the work. Pro produced a separate witness with the same placement and
restoration using different tags and a different input-key policy.
Apache-2.0.

## Open next questions

A complete balanced payload stage must route all right-axis fibers in
order, including idle and padded rows. A concrete next test is to
bind one retained multi-target fixture and check its synchronized
row and header streams. This package establishes one finite fiber.
A full integer product and a combined cost proof remain open.
