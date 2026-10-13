# X4 profile changes and ideal gain additivity

PR799's four paired exchanges have exactly additive child-profile changes.
Their ideal exponent-saving gains are strictly increasing, so those gains are
not exactly additive. This audit corrects the arithmetic interpretation of
one sentence in the imported proof note. It does not change the selected
conditional saving, κ = 0.001661634653669567.

The source statement is in
[PROOF-NOTE-FRAMES-X4.md](../gauge44-frames-x/PROOF-NOTE-FRAMES-X4.md),
in the paragraph beginning "Effect against #741's word". It says each
instance gives an ideal gain of approximately 1.0798e-7, "exactly additive".
The stated approximation describes the scale of the gain. Exact additivity
holds for the profile counts, but fails after solving the moment equation
and mapping its root b to ideal κ = b/(1+b).

[PROOF.md](PROOF.md) proves strict convexity across the entire interpolated
profile family. The executable audit reconstructs all sixteen subsets of the
four paired exchanges and checks the profile formula. It then proves root
brackets with both retained rational interval engines. These checks compare
the five distinct profiles, indexed by the number of paired exchanges.

For ideal κ_j with j exchanges, the exact interval checks establish

```text
8.4541370845e-11 < κ_4 - 4κ_1 + 3κ_0 < 8.4541370846e-11.
```

Every consecutive second difference is strictly positive. Adding four copies
of the first exchange's ideal gain therefore underestimates their combined
ideal gain. The selected verifier already prices the complete final profile,
so this observation does not change its certified bound.

Suggested replacement wording for the source note is

> Each paired instance replaces two rank-one children with one rank-two
> child in the local profile. These profile changes are exactly additive.
> The ideal κ gains are approximately 1.08e-7 per instance and increase
> slightly as the instances are combined. Price the complete combined
> profile to obtain its ideal κ gain.

The imported proof note and its manifest remain unchanged. This package
records the correction separately so the original contribution stays
reproducible.

## Reproduce

From the repository root, run

```sh
python3 -B -I research/x4-gain-additivity-audit/verify.py --check research/x4-gain-additivity-audit/RESULT.json
python3 -B -I research/x4-gain-additivity-audit/test_audit.py
```

The first command prints `PASS_X4_PROFILE_ADDITIVE_IDEAL_KAPPA_NONADDITIVE saved receipt matches`. The second runs five tests, including an optimized Python replay and mutation controls.

The audit uses the retained SW4 replay archive, PR799's explicit recipe and
builder, and the two pinned rational moment engines. Its input inventory is
in [SOURCES.json](SOURCES.json). Decimal output displays exact rational
enclosures; floating-point comparisons do not determine the reported signs.

## Scope and credit

Jeremy Kothe contributed PR799's X4 construction and proof note. Chafik
Boukhalfa, chafreaky, contributed the eight PR741 frame changes. Their work
and the inherited SW4 construction retain their original attribution. This
audit uses the unchanged Mercator engine and maintainer base-two engine
vendored in `complex-k492-owner-repair/vendor/multicold/engines`, with their
source provenance retained.

The subset checks establish the finite builder's scalar/frame conditions and
the additive profile identity. They do not replace a complete native/global
replay for each intermediate construction. The real-valued interpolation in
the proof is an arithmetic device, not a family of fractional physical
circuits. The inherited realization, all-size, precision/tape and analytic
hypotheses remain. No new κ or unconditional multiplication theorem is
claimed.

Prepared for @AmnonTamsut with substantial OpenAI GPT-6 Astra and GPT-6 Sol assistance.
Apache-2.0, under the repository license.
