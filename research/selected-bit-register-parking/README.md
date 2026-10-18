# Reuse fixed numerical banks across recursive calls

I connect the selected BIT numerical registers to a fixed parking tape and
packet port. After a child reuses the banks, I restore the parent's values
into the same register objects and reset their heads. The codec supports
arbitrary finite nesting without allocating a checkpoint tape per ancestor.

This supplies one physical component left open by David Arias's concurrent
[PR2753](https://github.com/CrocSwap/integer-mult-bounds/pull/2753). He constructs
the all-size logical caller with separate dynamic numerical arenas. I retain
his logical result and contribute the numerical-bank serialization/reuse
boundary. Full caller integration and payload/controller serialization remain
open; I leave the selected exponent unchanged.

For C numerical slots, the component uses **C+4 physical tapes**, including
two templates, the parking tape and the packet port. I prove an exact
sequential read/write/move invoice, including slot labels, word initialization
and erasure, delimiters, boundary probes and rewinds. See [PROOF.md](PROOF.md).
The caller may pass separately owned input grants in the shared banks, then
must close them before restoring its parent.

## Reproduce

Use Python 3.12 and its standard library:

```sh
python3.12 scripts/research_package.py --package research/selected-bit-register-parking
```

The verifier checks source hashes before imports and compares the complete
typed [receipt](RESULT.json). The tests cover:

- All 64 pairs of three-bit words, including zero and all-one values.
- Sparse slots, empty frames, translated heads, opaque ancestors, 602-bit
  words and slot labels wider than their stored words.
- **1,501 nested frames**, 3,750 parked records and exact restoration while
  using at most three allocated slots in each bank.
- Modulus/width/depth grants and failures involving slot aliases, child
  cleanup, widths, capacities, corrupted bits and uncleared checkpoints.

For direct replay, run:

```sh
python3.12 -I -O -B research/selected-bit-register-parking/verify.py
```

The `--emit` option prints a new receipt without writing package files.
I distinguish the written
all-depth induction from these finite examples. I claim no independent human
or proof-assistant verification.

## Sources and coordination

I reuse ywz65's [PR2635](https://github.com/CrocSwap/integer-mult-bounds/pull/2635)
parking controller and my [PR2697](https://github.com/CrocSwap/integer-mult-bounds/pull/2697)
Word interface without changing their bytes. [SOURCES.json](SOURCES.json)
records exact commits, paths and hashes. I preserve David Arias's PR2753
Frame source as a reference; this verifier does not execute his full caller.

I narrowed my concurrent logical-caller investigation after PR2753 appeared.
The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/2319#discussioncomment-18957230)
records that decision and the original scope. Nick Petalas's numerical
scratch and continuation-content audits in [PR2759](https://github.com/CrocSwap/integer-mult-bounds/pull/2759)
and [PR2758](https://github.com/CrocSwap/integer-mult-bounds/pull/2758) remain complementary. Their counts
and the existing payload/directory reserves are not new results of this codec.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance in the
construction, proof, implementation and checks. Apache-2.0; predecessor
attribution appears in [NOTICE.md](NOTICE.md).

## Open next questions

- Can the complete PR2753 caller use the shared banks at its Frame boundary?
  Bind its child input grants and context cleanup, then check the actual
  internal return. The remaining work is caller integration, not another
  generic stack test.
- Can the caller serialize its payload, directories and continuation with
  the same fixed-tape discipline? Preserve role aliases and charge the
  transfers. This codec only handles numerical banks.
- Can the joined physical ledger fit the intended supplier contract? Combine
  actual codec charges with the existing component reserves and outer stock
  wrapper. No total reserve or exponent admission follows here.
