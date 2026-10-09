# Physical operation frames on the PR118 complex word

Under the inherited analytic, fixed-tape and stopped-product interfaces,

    κ = 111192082577 / 10^15 = 0.000111192082577

This is **2.44076665% above PR118** (0.000108542805968). It is an
asymptotic exponent saving, not a measured multiplication speedup.

| Quantity | PR118 | This witness |
| --- | ---: | ---: |
| Complex additions / roots | 91,770 / 8,120 | unchanged |
| Carrier links / physical roles | 71,185 / 28,705 | unchanged |
| Deferred roles | 3,020 | 4,107 |
| Complex saving | 0.000108566486 | 0.000111216930 |
| Final κ | 0.000108542805968 | **0.000111192082577** |

Each physical occurrence of a scalar operation gets its own binary frame.
A backward pass constructs legal nondegenerate frames, followed by local
changes that reduce the rank-moment cost while preserving both adjacent
frame inclusions. A logical value can consequently use different frames
at different copy operations. Partial deferred readouts are selected with
their exterior, first-transition and target-front costs included.

The scalar DAG, matching, rational center decoder (divisor 21), source
injections, retained center copies and endpoint charges remain unchanged.
The bit side is Swapnil Jain's pinned round-seven word under PR104's
one-child accounting, as used by PR118. No optimality is claimed.

```sh
python3 research/physical-frame-kappa/test_controls.py
python3 research/physical-frame-kappa/verify.py
```

The verifier regenerates the bit ledger from the two SHA-pinned inputs,
rebuilds the complex DAG and physical word, compares the full profile,
replays arbitrary data and scratch, and independently scans the literal
forward and reflected words. It checks exact integer source supports and
dirty readout coefficients, frame nondegeneracy and nesting, all recursive
children, the expanded scalar charge, 47 strict constraints, seven margins,
and rejection of the next moment and κ grid points.

See [PROOF.md](PROOF.md) for the finite argument and inherited assumptions,
[SOURCE.json](SOURCE.json) for source pins, and [VALIDATION.json](VALIDATION.json)
for the actual validation status. The numerical certificate alone does not
replace the literal-word checks.

## Attribution

- eumemic: PR117's scalar DAG and PR114's complex compiler integration.
- Rohan Arun: PR118's deferred composition and the independent reflection
  audit inherited through PR116.
- Avi Eisenberg: PR110's physical-role compiler and deferred complex word.
- Swapnil Jain: deferred readouts and the unchanged round-seven bit word.
- icekylinx: PR104's stopped-product/odd-grid interfaces and PR115's
  nondegenerate completion algorithm.
- The original authors and contributors named in the repository's NOTICE,
  SOURCES and the retained source headers.

Prepared for DanieleCorso with OpenAI Codex assistance. Apache-2.0.
