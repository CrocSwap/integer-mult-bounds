# Graded box convolution: replace exponential tensor padding

This supplies an exact convolution layout for the recentered weighted-tensor
experiment following #489. It replaces per-axis zero padding by a carry-count
grade. A product occupies fewer than **4DN coefficient slots** for a D-dimensional
box with N entries, including unequal axis lengths. **No new κ is claimed.**

The earlier legal counterfamily had an independent-axis padding ratio exceeding
`2^(D/2)`. Here it is below `4D < 4*p^(2/5)`. This removes that particular
representation obstruction. It still leaves a dimension factor, table setup,
packing/extraction and routing costs, tile interactions, tensor Schur boundaries
and the outer small-field/dimension constraints.

```sh
python3 -B research/graded-box-convolution/verify.py /absolute/new/output
```

Python 3.11 or later, standard library only. No optimizer, network, external
solver or cached result is used. Inputs and outputs are kept separate.

The verifier checks:

- 37,205 exact carry identities, rejecting 28,799 invalid flattened aliases;
- 72 signed convolution cases against independent quadratic oracles;
- 10,657 outputs in two larger separable cases against tensor-product oracles;
- all basis vectors and two signed dense vectors in eight weighted cases,
  at 32/64 fractional bits and both orientations;
- five invalid layout/sign controls.

It executes 2,040 actual integer products. For the 12-axis binary case the full
product uses 188,391 slots versus 531,441 with independent-axis padding; the
eight-axis ternary case uses 196,813 versus 390,625. This is a representation
comparison, not a runtime benchmark. The weighted cases retain the previous
exact rational rounding bound and meet the 2^-12 target. They are rational
analogues, not certified transcendental instances of every source hypothesis.

PROOF.md gives the general carry identity and size bound. SOURCE.json pins the
#489 proof and distinguishes earlier local fixtures from upstream sources.
Rank-filtered convolution is established literature; no originality claim is
made. This package does not establish a full weighted Gaussian tensor algorithm,
an all-size multiplication bound, a Lean theorem, or κ=1.

Prepared by chafreaky with OpenAI Codex assistance; Apache-2.0.
