# Clean literal circuit for the conservative Gaussian pair

This implements Ali Romman's exact PR #6509 center-dependent rounded Gaussian
pair, answering the kernel-internal clean-bit obligation released in ToikY's
PR #6523. For each public compile-time sign ±1 and width6..256, it returns the
four-component result in place and returns an explicitly supplied clean bank
to zero. The logical bill is

```text
Toffoli: 96W-80     CNOT: 276W-104     NOT: 0
Data: 4W bits      supplied-and-returned clean stock: 14W+6 bits
Total wires: 18W+6       complete gates: 372W-184
```

The promise is four signed W-bit components with absolute value<=2^(W-6).
Data/work operands may be temporarily written exclusively. This does not clean
arbitrary dirty bits or fund preparation/placement of the initial zero stock.
`PROOF.md` gives the center logic, actual HALF guard, reachable inverse headroom,
compute-copy-uncompute invariant and full stock/address/program encoding bill.

The exact unchanged PR #3152 adder/HALF emitter is called on legal LOCAL wire
IDs, then its gates are injectively renamed. The original guards are retained.
The HALF is its actual reversible rotation/sign-fill block; no discarded bit,
assignment, reset or nonzero CLEAR appears as an emitted gate. Arithmetic source
#6509 and primitive #3152 are explicitly declared executable dependencies,
authenticated before import; cached bytecode is bypassed. Eight other retained
source objects are inert context. The numerical kernel/inverse/minimum-error
and generic adder/compute-uncompute methods remain credited premises.

## Evidence boundary

The primary actually expands/counts/hashes all502 complete width/sign words.
GATE-INVENTORY.json retains those primary hashes; they are not independent
regeneration evidence. GATES.json.gz contains16 complete words at widths
6,7,8,16,32,64,128,256, both signs. Its decompressed canonical values are the
artifact equality contract, not gzip container bytes.

The primary Boolean truth-column interpreter executes all14814 frozen inputs,
checks all four outputs against authenticated6509 arithmetic, every owned bit
zero, and literal reverse recovery of the complete initial state. Small widths
6/7/8 exhaust the full promise boxes for both signs; larger widths have28 signed,
parity and boundary inputs per sign. The independent oracle's blind first is
explicitly arithmetic/bill forecast only. Its later normal/optimized checks read
the actual16 retained words as DATA and execute all14814 cases, owned-zero and
literal inverse, independently. It does not import the primary compiler.

The count formula is independently derived from the credited blocks; numerical
expectation alone is not labeled circuit verification. `RESULT.json` compares
the whole typed inventory/case profile. `VALIDATION.md` and `RUN-RECORDS.json`
record actual first/mode/independent checks, corrections and remaining transport
checks. Finite cases corroborate the all-supported-width proof; neither they
nor this logical implementation admit a complete native supplier or caller.

## Reproduce

From the repository root with CPython3.12:

```sh
python3.12 -I -W error -B research/conservative-gaussian-clean-bit-pair/verify.py
python3.12 -I -O -W error -B research/conservative-gaussian-clean-bit-pair/verify.py
python3.12 -B scripts/research_package.py --package research/conservative-gaussian-clean-bit-pair
```

`--emit /absolute/new/RESULT.json` regenerates a profile while checking retained
gates/hashes. Explicit `--write-gates /absolute/new/GATES.json.gz` and
`--write-inventory /absolute/new/GATE-INVENTORY.json` regenerate artifacts.
The source/case hashes, exact integer/version/keysets and whole profile/artifact
values are checked in normal/optimized modes. Managed Python uses dynamic
containers, packed integers, recursive JSON comparison and explicit compilation
of the two authenticated predecessor modules; these are declared deviations
from low-level Power-of-Ten style. New functions are below60 lines and acceptance
does not use assert. No extra dependency or external service is required.

## Attribution

Ali Romman6509 supplies the actual pair/center/numerical inverse/error/ports;
ToikY6523 supplies the actual MOVE9896 binding and released cleanup question.
Nick Petalas3152/3081 and Cuccaro-Draper-Kutin-Moulton supply scalar/MAJ-UMA
primitives; Ali Romman6511 supplies their selected-scalar integration/pointers.
Clear1nsight4017, Tekalign and retained Barenco/lifting lineage supply an earlier
literal circuit for a DIFFERENT Gaussian lifting map. Bennett's generic
compute-copy-uncompute principle is classical. The new contribution is this
source6509 pair's explicit clean elementary implementation and logical bill.
Exact heads/headers/credits are retained in SOURCES.md, SOURCE-PINS and NOTICE.

## Open next questions

- Fund the supplied clean bank in an actual caller. First identify the lifetime,
  zero-stock source and placement for14W+6 bits; no dirty-bit erasure or free
  allocation/routing is supplied here.
- Bind one actual native pair instance to the generated word, then account for
  the complete native layer and caller. Start from6523's endpoint contract;
  tape access, concurrency, precision/stock and all supplier assumptions remain.
- Optimize this logical construction under the SAME explicit resource model.
  First compare against the retained complete word, including uncomputation,
  swaps and selector syntax; no optimality or physical speedup is claimed.

No dynamic unknown-sign circuit, widths above256, full native256-pair circuit,
tape/decoder tariff, physical routing admission, field-preparation fee,
accelerated caller, κ or selected-frontier change is established.
