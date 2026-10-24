# Physical three-lane record reversal

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

One fixed419-instruction local-symbol program reverses n records of runtime
width B on15 fixed tape ports. It realizes PR5148's three-lane stable route
on actual records, including incomplete final blocks, with no host sorting,
per-record tape allocation, decoded loop bounds or virtual payload padding.
The input and binary width descriptor are borrowed; output is distinct and
caller-owned. All work is erased and heads return. This is a valid-input
contract, not a rollback guarantee for malformed input.

For L=floor(log2 B)+1 and k=ceil(log3 n) (k0 for n0/1), the complete instruction
count is at most256((n+1)(B+1)(k+1)+B(L+1)+1). Retained tape backing is at most
K0+6nB+7n+B+2L+60, including historical high-water capacity. [PROOF.md](PROOF.md)
gives the all-n refinement, full invoice, supplied-input costs and limitations.
The abstract pass count alone is not a physical tariff or a numerical gain.

The verifier checks492 cases with independent record-array expectations,
translated origins, full borrowed/unused frames, every work tape and head,
written action/backing bounds, eight additional power-of-three/binary-carry
cases through n244 and B1024, and the exact seven-record two-pass source
example. Eight controls include actual output-bit and guide corruption.
These are finite corroboration of the scoped proof, not a proof kernel or a
complete multiplication theorem.

Reproduce from the repository root with Python3.12:

```sh
python3.12 -I -B research/physical-three-lane-reversal/verify.py
python3.12 -I -O -B research/physical-three-lane-reversal/verify.py
python3.12 scripts/research_package.py --package research/physical-three-lane-reversal --check-only
python3.12 scripts/research_package.py --package research/physical-three-lane-reversal
```

`--write-result` is the explicit receipt-generation mode. Normal replay
requires both SOURCES.json and RESULT.json; frozen receipts use typed canonical
JSON equality. The source proof from PR5148 is retained byte-for-byte and
hash-checked with exact public head/path metadata. It is external publication
provenance, not a local Git-history assertion. The retained local instruction
source is authenticated by the base Git blob and SHA256 and declared as a live
export input. No predecessor source is modified.

Credit Nick Petalas's PR5148 construction, Matarener's PR3825 obstruction,
James Reed's PR3839 finite census, and the PR5090 physical instruction semantics
following Jose Manuel PR2786 and Nick Petalas PR3503. The canonical claim is
[discussion1166 comment19144825](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19144825).

## Open next questions

Can an actual bit-free supplier consume this layout with its complete numerical,
movement and backing budget? First bind one real supplier call and its other
permutations; this standalone reversal does not establish supplier admission.
Can heterogeneous runtime lane capacities be encoded on a fixed bank with a
complete tariff? That is separate from the present fixed-three-lane theorem.
The selected frontier is unchanged.
