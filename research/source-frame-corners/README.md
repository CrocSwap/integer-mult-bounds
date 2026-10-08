# Source frames plus data corners: conditional kappa = 9.0799e-7

This contribution combines eumemic's [PR #13](https://github.com/CrocSwap/integer-mult-bounds/pull/13)
source frames with our [PR #12](https://github.com/CrocSwap/integer-mult-bounds/pull/12)
dimension-30 producer and two additional data-edge blocks. The candidate is

    kappa = 90799/100000000000 = 9.0799e-7,

**17.936% above PR #13's 7.699e-7** at commit
`3ef246fa4f69c87ebfed78376418afa9ffcad145`. This compares exponent savings,
not measured running time. The result is conditional and unreviewed.
No worldwide priority or formal verification is claimed.

## The new compatibility argument

All changes must use one rational controlled basis. The new proof combines
the source-frame exit minors with the data-corner minors as a finite product
of nonzero polynomials in the same `K,G_i` parameters. This establishes
simultaneous existence; separate successful bases would not suffice.

At h=30, auxiliary source frames replace the old entrance and sink edges.
Their 840-, 900-, and 25,200-coordinate blocks are removed, and one
26,940-coordinate block replaces them. We do not add incompatible gains.
The two additional data blocks do survive this change:

| Edge class | Copies | Singletons per edge | Contiguous widths |
|---|---:|---:|---|
| Stage 1/3 auxiliary join | B | 60 | 26,880 |
| Stage 2 auxiliary exit with source frame | B | 30 | 26,940 |
| Stage 3 data entrance | 2N | 87 | 25,142 and **842** |
| Stage 2 data entrance | 2N | 59 | **782** |

Here `v=142506`, `R=17515487`, `B=v^2 R`, and `N=v^3`. The scalar producer,
matching, rank deficit and common gate matrices are unchanged from PR #12.
The total singleton count is `65379670780393117512`. All other rank units
remain singleton calls, and all child widths contract strictly.

The data-corner arguments are in [the preceding local proof](../controlled-corners/proof.tex).
The new [compatibility proof](proof.tex) explains the common basis and exact
rank accounting. The earlier local kappa=2.0156e-7 candidate was held back
when PR #13 appeared; this contribution consumes only its compatible parts.

## Exact exponents and assembly

- Bit saving: `1816/10^9 = 1.816e-6`; certified moment gap exceeds `1.9154e-10`.
- Complex saving: `18179/10^10 = 1.8179e-6`; gap exceeds `2.1196e-11`.
  This uses the identical three classes and rational logarithm bounds of
  PR #13, with a sharper choice of exponent. Its construction is unchanged.
- `beta=1/1000`, so the complex leaf saving is `1.8160821e-6`, still strictly
  above the bit saving. Checking only the raw complex saving would miss this
  additional constraint.
- `epsilon=499999/10^6`, `c=1`, `delta=1/10^10`, `zeta=1/10000`,
  `C1=11999/10000`, `lambda=tau+1/10^16`, `lambda'=tau+2/10^16`.
- All 29 constraints and seven margins are strict. The final absorption gap is
  `40919500001/5000000000000000000000 > 8.1839e-12`.

See [certificate.json](certificate.json) for exact rational quantities, source
hashes, retained producer provenance and integer common-basis witnesses.

## Validation and reproduction

```sh
make source-frame-corners
make verify
python3 research/source-frame-corners/make_patch.py --materialize build/source-frame-corners/manuscript
```

The new verifier reproduces PR #13's numerical certificate and checks hashes
of the pinned source snapshot under `pr13/` and the retained PR #12 producer.
The full repository check reruns the dimension-30 producer, its 456 canonical
templates, dirty-scratch checks, and all 142,506 matching images.

Independent exact rational tests at h=3 and h=4 construct integer unimodular
`K,G_i`, check their inverses, verify idempotency, track both lower-triangular
factors, and verify their product with each of six projector prototypes equals
the required partial permutation. These tests use one common basis for all
six profiles at each dimension, including the new source-frame exit and the
two data blocks. A modular test only screens nonzero minors; reconstruction
is over Q. The stage-two data block is positive at h=4; h=3 leaves it unbatched.
The tested prototypes are finite representatives, not every label in the
full h30 network. Rational existence for that finite network is supplied by
the general polynomial argument, which still requires mathematical review.

Negative controls reject omission of either new data block at the chosen
saving, oversized bit and complex exponents, and a zero final absorption gap.
Five relevant PR #13 tests were also rerun, including its nonorthogonal h5
source-frame model. Its standalone patch test is replaced by checks on our
complete [integrated patch](../../patches/source-frame-corners.patch).

The integrated manuscript retains and attributes the preceding arguments,
appends the new interfaces and redirects the active assembly. Its complete
PDF is [source-frame-corners.pdf](../../artifacts/source-frame-corners.pdf).
For Tectonic, three inherited pdfLaTeX-only metadata commands are guarded
in the disposable build copy; the published patch does not alter them.

## Review priorities and attribution

Review the two data residual tensor forms, the common-basis argument and
physical pivot order, the replacement of auxiliary edges without double
counting, and the complex leaf inequality. Exact arithmetic and finite
matrix examples do not establish the general theorem by themselves.

Eumemic supplied the source frames and third complex class in PR #13, with
Claude assistance. IcekyLinx supplied controlled batching and dependency-path
guards in PR #10. Zhihao Chen supplied the ternary producer in PR #7. The h30
producer, matching extension, data corners and this integration were prepared
by Rohan Arun with substantial OpenAI Codex assistance. Earlier contributors
remain credited in NOTICE. All inherited analytic, tape, Gaussian and finite
producer assumptions remain explicit dependencies.
