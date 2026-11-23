# Strict frame prices in the 48-call Gaussian supplier

At the target trial κ = 0.0039, changing one eligible frame or two internal frames of the #8072/#8073 Gaussian word gives **3,083,991,930 strictly worse physical-subspace assignments and 172 ties**. The 172 include the original placement exactly once. The best price in these families retains the source’s negative raw margin, between −1.539342547620186178215 and −1.539342547620186178214. With the installed weights and 1,008 paid splits, the deficit exceeds 1,406.078231652772. This is a finite exclusion at the target trial. [Proof](PROOF.md) · [Exact result](RESULT.json)

| Sites changed from the original assignment | Strictly worse | Tied |
|---|---:|---:|
| One internal chart | 78,689 | 18 |
| One chart carrying only helper endpoints | 8,731 | 0 |
| Two adjacent internal charts | 3,114,632 | 0 |
| Two nonadjacent internal charts | 3,080,789,878 | 153 |
| Original placement | 0 | 1 |

The search fixes the 210 chart IDs carrying a main input or output, all 1,291 public role labels, all normalized rational forms, and the 5,674 ordered paid transfers. It admits every binary subspace of the appropriate dimension for each mutable site that satisfies the source’s strict incidence requirements. There are 706 active purely internal charts and 62 helper-only charts. A changed helper endpoint contributes its productive grade and every incident paid occurrence with its actual sign. The least strictly losing helper case is chart 1094, dimension five to six. Its fifteen placements each lose more than 0.00843834771094 per unscaled native invocation.

All eighteen neutral single changes can be installed together because their sites share no MOVE. A separate full-source check compiled 2,971 directed chart pairs and 104 public adapters, and checked 1,291 normalized columns with 88,780,788 adjoint terms. The portable verifier rechecks the 72 changed directed pairs with signed Pauli action and absolute Gaussian phase. It also compares all 512 columns of one changed operator and rejects a phase-only corruption. [Signed factors](neutral-factors.json.gz) · [Replay](verify.py)

### Reproduce

From an upstream checkout, run

```sh
python3.12 -IB scripts/research_package.py --package research/p104-gaussian-frame-price
```

For a standalone offline replay, run `python3 -IB verify.py` inside this directory. All calculations use the Python standard library. The packaged source projection retains the frame bases, ordered public endpoints, ordered MOVE labels, chronological paid order and fixed caller histograms. Its SHA-256 is `dc5f08a2499662a0d228583aa0fd092b1946bea7b2657899a22fbe46bcf4123c` over canonical uncompressed JSON. The optional source rebuild authenticates the original drivers and source archive before comparing those bytes. Supply the indicated research directory from an exact checkout of either external head.

```sh
python3 -IB rebuild.py --pr 8072 /path/to/research/p104-weighted-capped-allocation-490950
python3 -IB rebuild.py --pr 8073 /path/to/research/p104-weighted-k7-suffix
```

### Source and prior work

ToikY’s #8072 and #8073 use the same normalized Gaussian word and layout. #8073 improves the ordinary K7 price. The port grades and signed Gaussian transfer compiler in this investigation come from Ali Romman’s literal graph and weighted supplier. The frame comparison preserves their ordered transfers. [#8072 at 75f7e1c](https://github.com/CrocSwap/integer-mult-bounds/commit/75f7e1c44f48c43983016bcf8878c4d9e5e87c62) · [#8073 at cf4c4b7](https://github.com/CrocSwap/integer-mult-bounds/commit/cf4c4b7ea4b746be174ee4ba4e49f03b5bc79f8e) · [#8057](https://github.com/CrocSwap/integer-mult-bounds/pull/8057) · [#8027](https://github.com/CrocSwap/integer-mult-bounds/pull/8027)

The campaign previously examined 25,692 late exit-chart replacements on #7121 and 52,879 same-cut multi-read coframe states. Rohan Arun’s output rechart #7124 and its composition #7131 give positive precedents for changing a public interface. This package fixes the main frames of the later 48-call word and counts the incidence-compatible binary subspaces for the specified one- and two-site families. Clear1nsight prepared the investigation with substantial OpenAI Codex assistance. [Campaign board](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111) · [Output-rechart credit](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19530793) · [#7124](https://github.com/CrocSwap/integer-mult-bounds/pull/7124) · [#7131](https://github.com/CrocSwap/integer-mult-bounds/pull/7131) · [Attribution](NOTICE.md)

### Open next questions

Could a connected set of three internal charts, a helper endpoint changed jointly with another chart, or a changed contact schedule produce a positive net margin? A candidate needs the full incident paid and productive tariff, followed by signed compilation and owner return. Equal-frame contractions also require a changed transfer schedule and removal or replacement of an original positive-grade MOVE. They form a distinct family outside these counts. [Task and accepted scope](TASK.json)
