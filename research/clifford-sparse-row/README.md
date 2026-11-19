# What the width-13 Clifford decoder reads

The width-13 construction in #7799 specifies an exact Gaussian-dyadic left inverse for the full four-qubit Clifford alphabet. This package compiles it into **4,265 signed Bell-block reads for one symplectic fibre**. Those blocks are shared by all 256 Pauli coefficients of that fibre. It also prices the identity coefficient when the input is supplied as ordinary dense tensor coordinates. [Construction](PROOF.md) · [Input costs](COST.md) · [Width-13 precursor](https://github.com/apoursh/integer-mult-bounds/blob/7f08a74037788311cc6b7da27297b25f1b188e45/research/clifford-bell-fibres/PROOF.md)

| Input access and requested output | Cost for this implementation |
|---|---:|
| Transported 16 × 16 Bell blocks to recover one fibre | 4,265 block reads |
| Ordinary dense coordinates for one complete Bell block | 2⁵⁶ scalar reads |
| Ordinary dense coordinates for the identity trace of one block | 2⁵² scalar reads |
| Ordinary dense coordinates for the combined identity coefficient | **151 × 2⁴⁷ = 21,251,360,741,654,528 scalar reads** |

The last number counts every nonzero coordinate once. The 4,265 traces share 22 patterns of addresses. Within each pattern their signs are Walsh characters on at most ten independent parity bits. Combining their weights before reading gives four distinct nonzero raw weight values, ±1/32 and ±1/8. On arbitrary dense input every one of those coordinates can change the answer. A streaming schedule attains the count. This lower bound applies to the particular emitted row. A producer that supplies compressed Clifford operators or already-transformed blocks has a different access cost. No change to the selected multiplication exponent κ follows. [Raw weights, precision and tape movement](COST.md#the-complete-compiled-identity-row) · [Compact operator interface](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/research/clifford-exact-contractions/README.md)

The signed group certificate expands the reads into 34,120 terms on 8,304 distinct group elements. Their weights cancel at every element except the requested one. This proves exact recovery on the entire Clifford-mixture image. Choosing one representative per coset also defines a specific extension to arbitrary observations: its normalized coefficient rows have squared Euclidean norm **2⁴⁵**, and its full operator norm is at most **4¹²√(1319/64) < 2²⁷**. [Certificate and norm derivation](PROOF.md#counts-and-euclidean-bounds)

## Run the compiler

Use CPython 3.12 and the standard library. These examples run from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-sparse-row
python3.12 -B research/clifford-sparse-row/bell_reads.py --emit
python3.12 -B research/clifford-sparse-row/raw_row.py --probe-index 0
python3.12 -B research/clifford-sparse-row/raw_row.py --entry 513 139777
```

The second command emits the 4,265 weights, six input and six output Bell labels, and Gaussian phase corrections as JSON lines. In Python, `bell_reads.iter_reads(target)` accepts any symplectic target as the binary images of the eight standard basis vectors, with four low Z bits and four high X bits. Use the Weyl corrections in the proof with each emitted block. The raw row commands refer to the identity representative and return the signed numerator over 4,096. An address is a 52-bit row and a 52-bit column. The first probe in this schedule is entry (513, 139777) with weight −1/32. The Python iterator `raw_row.iter_probes()` streams only nonzero coordinates. The indexed command accesses a single scheduled coordinate directly.

The registered checks cover finite group cancellation, every Walsh cell, all 4,265 transport pairs, independent literal Bell contractions and Pauli phases, and recovery from a coherent 64-operator mixture for two target fibres. All use exact arithmetic. The raw support is counted by the sizes of disjoint affine sets. The large dense tensor and a full physical multiplier are not materialized. [Replay manifest](VERIFY.json) · [Source pins](SOURCES.json)

## Credit and coordination

Prepared by **apoursh** with substantial OpenAI Codex and separate agent assistance under Apache-2.0. The group identity, plane choice and Bell phase correction follow #7799. Ali Romman, Nick Petalas and alephnan supplied earlier Clifford, spectral and Pauli work. Walsh transforms, normalizer quotients and binary linear algebra are classical. This package follows the implementation-cost handoff on upstream main `e54523517d0f03e58352e647c403a5af3e525a57`. [Public claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19753796) · [Scope and overlap record](TASK.json)

## Open next questions

1. Can a compact producer evaluate one of the active Walsh cells at its actual precision and storage layout? Include the cost of acquiring its inputs, moving scratch and restoring the caller.
2. Can changing which tuple represents an equal coset sum shrink the raw support further? Preserve the group identity and recompile all affected sign cancellations before comparing costs.
