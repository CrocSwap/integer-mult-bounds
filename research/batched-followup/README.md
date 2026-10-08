# Dimension 30 with controlled batching: conditional kappa = 1.2649e-7

This candidate combines icekylinx's [PR #10](https://github.com/CrocSwap/integer-mult-bounds/pull/10)
batching interface with the producer rules in [PR #9](https://github.com/CrocSwap/integer-mult-bounds/pull/9)
and the matching extension in [PR #11](https://github.com/CrocSwap/integer-mult-bounds/pull/11).
It supports the conditional witness

    kappa = 12649/100000000000 = 1.2649e-7

in `T(n) = O(n (log n)^(1-kappa))`, approximately **2.84% larger** than
PR #10's `6149999/50000000000000`. This is an exponent comparison, not a
practical speedup. **The result is unreviewed and conditional.**

The bit producer uses five-subsets of 30 points, exact support merging,
and the three previously published star-selection rules. It has 16,089,992
addition nodes and 1,425,495 output uses, hence 17,515,487 auxiliary roles.
The explicit intersection-two matching from PR #11 removes the earlier
multiple-of-four dimension restriction. All 142,506 images are checked.

Dimension 30 lost under the old uniform child-cost model. Under PR #10's
controlled mixed-width recursion, its larger contiguous child blocks make
the certified bit saving improve from `246/10^9` to `253/10^9`. The complex
network stays at dimension 28 with saving `7/10^7`; its arithmetic-depth
guard and Gaussian precision correction are unchanged.

## Proof and exact checks

The incremental argument is [proof.tex](proof.tex). It explains the source
spans, finite producer, matching, and why every dimension-dependent step of
the controlled-basis argument still holds at h=30. The complete independent
patch [batched-dimension30.patch](../../patches/batched-dimension30.patch)
retains the earlier h28 proofs, appends the stronger bit interchange lemma,
adds a layer proposition consuming it, redirects downstream transforms and
resampling, and replaces the active rational assembly parameters, including
the integer-power test for the new epsilon. Bundled upstream is unchanged.

The new exact parameter choices are:

| Parameter | Value |
|---|---|
| tau | `1-253/10^9` |
| sigma | `1-7/10^7` |
| epsilon | `49999993/100000000` |
| c | `1` |
| beta | `1/1000` |
| delta | `1/10^10` |
| zeta | `1/10000` |
| C1 | `11999/10000` |
| lambda | `tau+1/10^16` |
| lambda prime | `tau+2/10^16` |

All 29 constraints and seven final margins are strict. The bit moment has
a certified gap greater than `9e-12` below one. The final assembly margin
exceeds kappa by approximately `9.98219e-12`. Exact values and source hashes
are recorded in [certificate.json](certificate.json).

Verification reconstructs the complete h30 producer twice, compares its
boundary demands byte-for-byte, and checks all 27,405 stars using all 456
selected templates. Every template passes compiled forward and reverse
role-support checks and exact F3 checks on all source, output, and arbitrary
dirty-scratch basis directions: 164,002 basis directions per orientation
across the templates. Negative controls reject an oversized bit exponent,
an inflated role count, and a headline equal to the smallest assembly margin.

The inherited PR #10 baseline passed 166 tests and all 18 patch checks
locally. These checks do not independently establish its controlled-basis,
fixed-tape row, arithmetic-path, Gaussian, or upstream analytic arguments.
The review found no blocking defect in those examined arguments; this is
not a formal proof audit of the entire multiplication theorem.

From the repository root, with Python 3.11 and C++17:

```sh
make batched-dimension30
make verify
```

The producer uses several GB of memory and writes its intermediates under
`build/geometric-dimensions/`. To materialize the complete manuscript:

```sh
python3 research/batched-followup/make_patch.py --materialize build/dimension30-manuscript
```

## Attribution

The ternary source geometry, paired degree-three circuit, retained-total
schedule, and paired complex producer are Zhihao Chen's PR #7 contribution.
The controlled batching, whole-residual recursion, row construction,
dependency-path guard, and Gaussian correction are icekylinx's PR #10
contribution, pinned at `62691e395a0458ce089a1c7b5d89e74291e95e29`.
The source pins and preceding attribution in NOTICE and SOURCES.json are
preserved. Research dependencies from PRs #9 and #11 are included unchanged.
This dimension-30 combination, exact checks, and integration were prepared
with substantial OpenAI Codex assistance at Rohan Arun's request. No
worldwide priority or OpenAI endorsement is asserted.
