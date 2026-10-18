Extend PR968's explicitly real-matrix exact eight-term decoder floor to
arbitrary complex coefficients in the same all-pairs, ordinary-transpose
model: `cost >= max(72-p,56)` for every `p<=24`. Existing real attainments
keep the bound sharp over puncture choices of each size.

The bridge is not independent real projection. An exact Q(i) isotropic
example shows that cross-term nonparallelism, used in the real argument,
can fail over C. The written proof instead establishes nonisotropy only
for reduced sides at p<=15, which must be complex proportional to real
root or D7 directions. That is precisely enough for the counting step.
This is not a flaw in PR968's stated real theorem.

Parallel PR1071 by JosieElliston independently rederives the support floor,
characterizes mixed root bases, and bounds copy-chain delivery for an
explicit P104 decoder. The contribution here is the arbitrary-complex
coefficient and restricted-nonisotropy bridge, with exact counterexamples
to two tempting shortcuts; no delivery construction is claimed.

```text
python research/complex-decoder-field-extension-seed44/verify.py
```

Expected: `PASS_COMPLEX_DECODER_FIELD_EXTENSION_S44 p=0..24 examples=3 attaining=25 pairing=14400 controls=7`.

The source-pinned replay checks the required predecessor census and
attainment chain, all 14,400 independently constructed pairing entries,
exact Gaussian-rational examples and seven rejection controls. PR968's
standard real flat-classification premise F6 remains inherited. Finite
examples support the written proof; they do not enumerate complex space.

No new supplier, native circuit or kappa. Nine or more terms, masked
identities and p>=25 are excluded. Prepared for @woklerx with substantial
OpenAI Codex assistance, Apache-2.0. Credit themilkman216's PR968 and
DreamingOfClouds's PR717, with full attribution in NOTICE.md.
