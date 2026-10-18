# Independent algebraic verification of the selected complex moment

**Independent finite verification; no new κ.** The selected #626 complex
supplier's native and conservative recursive moments have the recorded strict
brackets at adjacent saving values separated by `10^-24`. This package checks
both brackets using repeated integer square roots and binary exponent brackets,
without importing any supplier, logarithm, exponential or binomial-series code.

The exact certificate reconstructs the complete profile from 72 invoice calls
(8 CK, 64 JP8) plus the separately recorded idle children. It recovers 262,707
children, rank mass 520,704, parent dimension 73, live stock 7,168 and deficit
2,560. The physical stock 7,670 is a different accounting quantity.

From the repository root, Python 3.11+ and the standard library suffice:

```sh
python3 -I -B research/pr626-root-moment/verify.py
```

Expected output:

```text
PASS_PR626_ROOT_MOMENT
4 strict endpoints; 72 calls; 262707 children; 1743 integer-power controls; 2 kernel mutants; 6 mathematical controls.
```

The default command is offline and reads without writing. `-O` gives identical
output: no checks depend on assertions. `--write-certificate` explicitly
recomputes and replaces only this package's certificate. The exact fractions in
[CERTIFICATE.json](CERTIFICATE.json) are the evidence; these decimal diagnostics
are rounded for readability:

| Model | Decision | Enclosed moment minus one, approximately |
|---|---|---:|
| Native, recorded lower saving | accept | -2.34607234900 × 10^-24 |
| Native, lower saving + 10^-24 | reject | +6.49310917479 × 10^-25 |
| Conservative, recorded lower saving | accept | -2.80409546824 × 10^-24 |
| Conservative, lower saving + 10^-24 | reject | +1.91287798245 × 10^-25 |

[PROOF.md](PROOF.md) derives the enclosure and states the cost formula. The
implementation brackets the saving by dyadic exponents with denominator
`2^163` and uses outward rounding on a `2^256` fixed-point grid. Every square
root is computed with `math.isqrt`; every final decision uses exact rational
comparisons. The seed selects the exponent depth and 83 additional deterministic
algebraic fixtures. This is a finite verification domain, not a supplier search.

The 1,743 independent kernel comparisons raise interval endpoints to integer
powers and compare them with exact rational powers, including dyadic and
nondyadic exponents. Two coarse fixtures expose exponent truncation and unsafe
upper-root rounding. Six mathematical controls cover the old surcharge at the
native endpoint, omitted conservative surcharge, omitted idle children,
physical-stock normalization, a changed profile with equal count/rank mass,
and the exact zero-saving rank-mass identity. Five invalid power inputs are
rejected. In particular, preserving count and rank mass alone does not preserve
the adjacent-endpoint decision.

Package and implementation corruption controls run separately:

```sh
python3 -I -B research/pr626-root-moment/test_verify.py
```

Expected: four tests `OK`. These replay a relocated minimal package, compare
normal/optimized output, reject corruption of all five source files and the
certificate, and reject five actual script mutations at their mathematical or
accounting checks. The tests capture failure output to keep the result concise.

## Sources, related work and scope

Exact base: `66849e1475c930fd7732b1a0067ffee7e1e95f60`. Selected #626 source:
`660de893d27bb7abd1d5b01b1640207528a5c851`; #622 construction source:
`f69477f4f6d3c7eb1f740b166881bffed4ffa9f6`.
[SOURCES.json](SOURCES.json) authenticates the five consumed inputs by SHA-256
and binds the assembly to `certificates/selected-result.json`. The selected
record's κ remains `51110230636731/31250000000000000`.

The selected maintainer review already checks the moment with two arithmetic
engines. This contribution adds a third, series-free arithmetic method and
exact power controls. Concurrent [#678](https://github.com/CrocSwap/integer-mult-bounds/pull/678)
checks #543's **bit** profile with generalized binomial enclosures;
[#667](https://github.com/CrocSwap/integer-mult-bounds/pull/667) and
[#672](https://github.com/CrocSwap/integer-mult-bounds/pull/672) accelerate
existing logarithm/exponential kernels. This package does not import those
contributions. [#675](https://github.com/CrocSwap/integer-mult-bounds/pull/675)
checks owner boundaries; this package consumes the preserved owner/invoice
receipts and checks their pricing consequence. The fixed-frame negative
results #661/#698 do not preclude this verification task and are not reopened.
The local sprint claim and overlap record are in [CLAIM.json](CLAIM.json).

This does **not** independently reconstruct scalar circuits, frame geometry,
ownership charts, restoration, or the validity of the profile/surcharge model.
It checks arithmetic and consistency of the pinned finite receipts, assuming
their construction-level justification. No production pricing engine,
selected certificate, generator, upstream source or frontier is changed.
The full repository suite, cold supplier replay, all 47 outer inequalities,
Lean and remote CI are outside this package's validation. The all-size compiler,
common-label/mutable-basis realization, whole-call hosting, precision/tape and
analytic transfer obligations remain inherited. This finite certificate is not
a formal proof of the multiplication theorem or a practical speedup claim.

Credit to Chafik Boukhalfa/chafreaky (#626 ownership and independent checks),
Jeremy Kothe (#622 construction and #623 dispatch), icekylinx's native assembly
lineage, DreamingOfClouds' cold-helper work, Rohan Arun's #559 recurrence
correction, eumemic's #543 bit supplier, and all predecessors retained in
`research/complex-k492-owner-repair/NOTICE.md`. The selected review and original
source notices remain authoritative for their cumulative attribution.
Prepared for **arkfx** with substantial **OpenAI Codex** assistance; Apache-2.0.
The checker and proof here are newly written; frozen inputs retain their
original authorship. AI-assisted review is not independent human peer review.
