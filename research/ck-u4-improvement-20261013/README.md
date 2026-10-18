# Four additional CK ends and concentrated owner packing

Conditional **κ = 0.001636464689763295**, exceeding
[PR639](https://github.com/CrocSwap/integer-mult-bounds/pull/639) by
**0.000000003096986179**.

The four PR637 dim-8 cold ends also apply to CK: raw helpers 233, 265, 425 and
441 now end at U* instead of FULL. The CK paid-profile delta is
`{1:+8,2:-4,4:+4,5:-4}`, and each corresponding helper width drops from 9 to 8.
The 71 JP8 / 1 CK dispatch is unchanged. A 21-owner integer neighborhood
consolidates unused capacity into `{40:1,48:2229}`; the portable exporter records
38 changed rows relative to pinned PR638, including interval compaction.

Exact global admission and both moment engines pass, as do separate rational
native/owner checks and five corruption controls. The new CK construction passes
native, reflected, independent local, wrapper and phase checks. All 23 core
admission files remain unchanged from PR637. The full fresh replay passed **64/64 stages**, without reuse, in 371.07 seconds.
All 51 artifact and 64 log hashes, supplemental proofs, mutation controls and
exact reconstructions passed. Complete evidence is in [validation/](validation/).
Execution was on macOS; no Linux replay is claimed.

The [complete witness](witness/README.md) contains pinned dependencies,
the CK constructor and the owner exporter. Reproduce with Python 3.10+, a C++
compiler and Boost headers:

```sh
PYTHON=python3 sh research/ck-u4-improvement-20261013/witness/verify.sh /tmp/ck-u4-fresh
```

This is a conditional research bound with the inherited all-size, compiler,
realization, analytic-transfer and bit H1–H5 assumptions. Prepared by Chi Zhao
with substantial OpenAI Codex assistance. Upstream construction credits are
preserved in the witness.

The fresh replay used commit `3bd7400b78f6f155fc200247f0853e742af13bbe`. After success,
only the witness README and its manifest entry changed. The
[documentation update record](DOCUMENTATION-UPDATE.json) confirms that all
316 other manifested files are unchanged.
