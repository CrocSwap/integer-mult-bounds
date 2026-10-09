# Cyclic interval strips on both axes of the stopped product-ring bound

Under all of PR104's inherited and newly proposed interfaces (as used by PR107–PR109),
this finite replacement gives conditional
**κ = 1715630240171/(2·10^16) = 8.578151200855×10⁻⁵** —
**7.278% above PR109** (7.9961717358×10⁻⁵), 7.384% above PR108 and 9.999% above PR107.

## Idea

Both axes of PR104 compute their leave-one-out ("strip") sums with the ordinary
prefix/suffix identity `s_j = A_{j-1} + B_{j+1}`. We replace them with **cyclic interval
strips** (the interval construction of PR62 on the h23/h25 frame-compiler lineage):
every cyclic interval `I(a,m) = I(a,m-1) + v_(a+m-1)` is built and `s_j` is the
complementary interval. Each interval has a later consumer with a containing cover, so the
**unchanged** legal carrier matchers join many more additions. Nothing else changes.

| | PR107/108 | This |
|---|---:|---:|
| **bit h23** (retained-total producer, positive labels) | | |
| additions / matched / roles | 34,764 / 1,324 / 38,776 | 57,162 / 30,197 / **32,301** |
| certified stopped coarse saving | 4019/5·10^7 = 8.038e-5 | **898920417/10^13 = 8.98920e-5** |
| **complex h24** (all-disjoint rational centers) | PR108 | |
| matched / roles | 15,422 / 43,270 | 37,802 / **38,506** |
| strict complex saving | 7989584037/10^14 | **8579641984/10^14** |
| **κ** | 7.988289e-5 (PR108) | **8.578151e-5** |

- Bit axis: only `PairedExclusionCircuit.block`'s strip layout changes (cyclic, carry last),
  loaded privately (`bit_paired.py`); positive labels are recomputed for the new graph by the
  unchanged labeler, and the positive matching equals the envelope matching.
- Complex axis: PairedTriple strips use cyclic intervals (`producer.py: cyclic_vector`),
  pair stars keep PR108's dual-suffix identity, and the coordinate order returns to PR104's `((i^1) in (a,b), i)`.
- The complex leaf still binds: bit parameter = min(AB, (1−10⁻⁶)·b − 10⁻¹⁰) exactly as in PR107.

## Checks

```sh
python3 research/cyclic-strips-both-axes/verify.py
(cd research/cyclic-strips-both-axes && python3 test_controls.py)
make verify
```

`verify.py` regenerates **both** rows from source (bit: graph → scalar/frame verify → export →
unchanged `match_exported_dag` → recomputed positive labels → unchanged `match_positive_dag`;
complex: every exact support, center, rational-scatter and frame-nesting assertion, unchanged
`match_complex_general`), certifies the stopped coarse moment at the new COARSE and rejects
COARSE+10⁻¹³, certifies the complex moment and rejects b+10⁻¹⁴, and checks all 47 strict
constraints and seven margins, rejecting κ+10⁻¹⁷. Controls reject the PR104 bit row, the
PR108 complex row, unpaid cleanup, omitted loss and an unpaid role. Full verification passed on `fb550b9b1a3c60cc419701e530494ed754d08cef` in 2409.831 seconds, completed 2026-10-09T00:45:01.380047+00:00: `make -j1 verify` (78 isolated test modules and 20 historical patch checks), both producer regenerations, exact assembly and six adversarial controls. All 39 research-head GitHub checks passed; no source drift. See `research/cyclic-strips-both-axes/validation.json` for evidence hashes.

Scope: finite conditional witness; PR104's opposite-bank factorization, stopped streaming and
odd-denominator grid interfaces remain written proof dependencies. No optimality/runtime claim.

Credit: icekylinx (PR104), Avi Eisenberg (PR62 interval strips, PR53), the PR55 dual-suffix
authors, PR107–PR109, and all predecessors in PR104's NOTICE/SOURCES. Prepared by Rohan Arun
with Anthropic Claude assistance, Apache-2.0.
