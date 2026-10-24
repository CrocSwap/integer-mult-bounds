# Physical periodic Gaussian update

This package replaces the host-indexed update in PR5159 with a fixed-bank local
binary-tape implementation for the same385-row Reference. It pays for row-major
to offset-major coefficient layout, eight cyclic input scans, exact signed
accumulation, one final truncation per component, output and complete cleanup.
The hole192 and genuine periodic wrap couplings are retained.

The written result covers arbitrary admitted signed grid inputs at this fixed
geometry and33-bit fractional grid. The verifier checks all770 output components,
a second zero-data call on the same owner, exact instruction invoices, borrowed
bytes/backing identities/head returns, retained erasure and semantic mutations.
All80-bit arithmetic uses local bit/carry operations. Output has an explicit
pending/consume lifecycle; consumption performs real erasure and rewind.

The normal command regenerates all3072 original coefficients and compares the
entire authenticated packet. The optimized command reuses that exact packet and
replays the complete physical semantics; it does not repeat source preparation.

```sh
python3.12 -B research/physical-periodic-gaussian-update/verify.py
python3.12 -O -B research/physical-periodic-gaussian-update/verify.py --cached
```

Expected: `PASS_PHYSICAL_PERIODIC_UPDATE`. Normal takes about40 seconds, cached
about8 seconds on the development host. These durations are replay observations,
not physical machine speed claims. `--record PATH` is an explicit development
receipt-generation mode; normal validation requires RESULT.json and SOURCES.json.

The executed primary update uses12,170,793 reads,4,157,850 writes,17,181,404 moves
and22,109,852 finite-control steps. Constructor and final consumption are additional
separately recorded vectors. The exact universal correction formula and total
449,445 retained cells (including input, output and erased backing) are in PROOF.
A source-counted finite-controller allocation is separate from tape storage.

Coefficient generation and initial binary serialization remain a host preparation
premise; its original interval/cache bill is inherited, not converted to physical
cost here. The275-step numerical/error composition and its complete symbolic
copy/update/cleanup allowance are proved conditionally, but275 physical updates
were not executed. No variable-width controller, literal compiled instruction
tape, full Core/Tensor/multiplier, asymptotic speedup or new kappa is claimed.

See PROOF.md for the successful-domain theorem, exact bills, inherited assumptions
and **Open next questions**, and VALIDATION.md for execution/export evidence.
Credit Jose Manuel, Vlado Vojdanovski, Jeremy Kothe, Cinna Davis, Mason Hale,
Chafik Boukhalfa and the original numerical/physical lineage. Exact PR5159 source
captures retain predecessor notices. Prepared by JoyboyBrian with substantial
OpenAI Codex assistance; new work Apache-2.0.

## Open next questions

- Physically generate and serialize the original coefficient stream, including interval caches and installation.
- Execute the complete alternating-owner275-update lifecycle and its enclosing final consumer.
- Derive and implement a variable-width/geometry controller with a complete updated invoice.
