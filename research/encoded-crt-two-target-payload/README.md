# Fuse two encoded CRT payload sorts

One live balanced CRT root now routes both right axes of the retained
`two_short_first` fixture. One combined destination key sorts its complete
16-record right-side rectangle in four literal radix passes. A matched
forward execution that sorts after each axis reaches the same exact frame in
eight passes. The fused inverse restores the entire input frame, encoded
source, physical backing and entry heads.

The fixture has moduli `(5,7,3,2)`, declared widths `(3,3,2,2)` and input
source `(1,5,2,1)`. The source becomes `(1,5,0,0)` and then returns to
`(1,5,2,1)`. Original tag `293` moves from slot 0 to slot 5. The independent
CRT oracle checks all 16 slots before accepting restoration. The primary
execution covers one fixed left state and its full padded right rectangle.

## Source and payload join

1. Select the live root from the retained #7352 iterator. The encoded axis
   cursor is at its first marker and the lease ends at the source suffix.
   The forward leg pays for two earlier read-only leaves. The inverse sees
   the root first and retires the remaining iterator after the root.
2. Walk the borrowed right source and numerical result in the same order.
   Copy each physical unary width and modulus and the corresponding P-bit
   offset. Consume each complete updated-coordinate field and require both
   terminal markers. The width sum supplies the radix pass count. Check that
   the borrowed tapes and their heads are unchanged before staging.
3. Run the existing encoded Beneš program once for each target on the same
   private and output backing. For each call, scan the actual payload tape.
   Two encoded position counters identify the current slot. Query all
   physical switch rows for the selected axis and write only that axis's key
   field. Skip the other field using its live unary width. Clear both ROM
   outputs and the active headers before reusing the bank.
4. Sort the entire frame once with the unchanged literal binary radix
   program. Stage the whole-node result, retire the numerical lease, then
   commit the source. The inverse reverses the row sequence within each
   target and repeats the same frame procedure.

For the fixed current left source, the independent oracle solves
`k ≡ 1 mod 5` and `k ≡ 5*5 mod 7`, so `k = 11` in `[0,35)`. For the two
right axes it solves `35*c ≡ 11 mod 3` and `105*c ≡ 11 mod 2`. Both
positive offsets are 1. The two axis maps on their padded four-slot
coordinates are `f = [1,2,0,3]` and `g = [1,0,2,3]`. A padded coordinate
is fixed on its own axis while the other coordinate can still move.

At physical position `4*a+b` the fused scan writes `f(a)` and `g(b)` into
the two fields before any record moves. The staged sort first puts that
record at `4*f(a)+b` with the key for its new physical slot. Counting
positions afresh at the second scan gives the same full key `4*f(a)+g(b)`.
This argument uses that the permutations act on separate fields and that
the offsets depend on the preserved left source and modulus prefix. Reversing
the layers of each axis inverts its permutation. Four stable last-bit passes
both sort the four-bit keys and restore their bit order.

## Observed work and storage

| Quantity | Fused forward | Staged forward | Fused inverse |
| --- | ---: | ---: | ---: |
| Literal radix passes | 4 | 8 | 4 |
| Literal radix bit and control instructions | 492,724 | 985,448 | 492,724 |
| Payload adapter bit actions, including bucket markers | 19,272 | 19,428 | 19,272 |
| Adapter symbol actions | 25,906 | 25,928 | 28,594 |
| Encoded source symbol actions | 373,976 | 373,976 | 264,989 |
| Beneš producer instructions | 9,681,707 | 9,681,707 | 9,681,707 |
| Actual row queries | 96 | 96 | 96 |
| Retained private symbol cells | 4,309 | 4,309 | 4,308 |
| Retained literal radix register bits | 288 | 576 | 288 |

The forward comparison saves 492,724 radix instructions and 156 bit-tape
marker actions. The comparator uses the same full-frame radix ABI and
performs one complete sort after each of the two axis scans. It models this
specific staged route. The shared ROM backing retains 3,031 private/output
cells at the end of either target, apart from the charged header storage.
Each execution retains 30 Beneš register symbols, 1,092 bucket bits and 143
private symbol roles. The fused round trip shares one 57-cell source and one
payload tape with a visited extent of 1,067 bits. The two legs retain their
private banks separately.

Counts use the respective source, symbol and binary execution models.
Fixture serialization and independent observers sit outside the measured
call. A common literal tariff, a complete multiplication caller and a
change in the asymptotic saving κ remain open.

## Replay and source credit

Run the registered package or direct replay with Python 3.12.

```sh
python3.12 -B scripts/research_package.py --package research/encoded-crt-two-target-payload
python3.12 -I -B research/encoded-crt-two-target-payload/replay.py
```

[RESULT.json](RESULT.json) records all three executions and the exact maps.
The dropped fast target control still commits the correct source but puts
tag `293` in slot 4. The retained `growing_bank` case separately checks
unequal widths and unequal offsets on the live header path. Reusing its
first offset for its second fails the ordered header oracle. The replay
also retains the noncommuting inverse-row-order and truncated-row controls.

[SOURCES.json](SOURCES.json) binds the live inputs to canonical main
`e54523517d0f03e58352e647c403a5af3e525a57` and the exact [#7388 predecessor](https://github.com/CrocSwap/integer-mult-bounds/pull/7388)
`d6f4a69202ad0bba4a915f4d4f3eaba1fe431c86`. This package imports its loader,
full-layer row traversal and literal radix wrapper without copying them.
The retained #7388 pins identify CubeJerry's [#7352](https://github.com/CrocSwap/integer-mult-bounds/pull/7352)
encoded endpoint and the shared forward writer from [#7351](https://github.com/CrocSwap/integer-mult-bounds/pull/7351).
Commdata2338's [#5519](https://github.com/CrocSwap/integer-mult-bounds/pull/5519)
at `53a034436f17ef5b8fdf7a02f5066528cdfe5446` supplies the fixture and
shared-bank alignment invariant. Ali Romman's
[#5625](https://github.com/CrocSwap/integer-mult-bounds/pull/5625) supplies
predecessor retirement evidence. JoyboyBrian's [#5092](https://github.com/CrocSwap/integer-mult-bounds/pull/5092),
[#5496](https://github.com/CrocSwap/integer-mult-bounds/pull/5496) and
[#5015](https://github.com/CrocSwap/integer-mult-bounds/pull/5015) supply
the producer, row query and literal consumer. OpenAI Codex and ChatGPT Pro
materially assisted. Pro derived the independent slot map and checked the
isolated radix component with supplied keys. Apache-2.0.

## Open next questions

To transfer this result into an actual multiplier, first bind a caller's
full normalized transform returns, payload layout and original-coordinate
extraction to the encoded source contract across left states. The next
product-level acceptance check
must use a production-admitted catalogue, consume the actual transform
returns and recover an exact integer product through CRT and carry.
