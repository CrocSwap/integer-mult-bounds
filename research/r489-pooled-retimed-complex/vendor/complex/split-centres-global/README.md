# Conditional κ = 0.001120864952258278

This package combines a split-centre Hamming complex construction with a
source-centre bit construction in compressed nine-stage windows. The resulting
conditional exponent saving is

$$
\kappa=\frac{560432476129139}{500000000000000000}
       =0.001120864952258278.
$$

This is approximately **6.9522% above PR425**. Both components change:

| Component | Helpers | Ambient width | Certified saving |
|---|---:|---:|---:|
| Complex | 560 | 73 | 0.001183986549206329 |
| Bit | 758 | 64 | 0.001122122700265139220566 |

The bit component limits the final assembly. The complex construction removes
coordinate contributions that cancel in the decoder, replacing eight full
centres with eight rank-eight and eight rank-one copies. The bit construction
starts from PR426's R767 word, computes its nine retained forms reversibly in
source rows, and uses PR386's compressed windows.

## Verification

Python 3.11+ and its standard library suffice. Use a new output directory:

```sh
python3 -B research/split-centres-global/verify.py /tmp/split-centres-check
```

The default replays both changed words, reflected/inverse-transpose programs,
bank ownership, costs, two rational moment engines and 47 strict outer
inequalities. Exact complex phase evidence is reused only when the regenerated
canonical word and complete recipe hashes match. To regenerate every selected
Gaussian phase pair as well:

```sh
python3 -B research/split-centres-global/verify.py /tmp/split-centres-full-phases --replay-phases
```

The unchanged historical repository suite and PDF build are not required by
this package. `EXPECTED.json` binds the result to both emitted global templates;
`MANIFEST.json` binds the package files; `SOURCES.json` pins imported sources.

## Scope

[PROOF.md](PROOF.md) supplies the changed finite construction. The all-size
compressed-window and correlated dirty-bank semantics, recursive compiler,
restored-work/tape/common-grid precision, and analytic transfer interfaces remain
conditional. This does not claim unchanged legacy gx/gxcore acceptance, a new
Lean proof, or an unconditional multiplication theorem.

Contributor history and AI assistance are recorded in [NOTICE.md](NOTICE.md).
Original notices and the inherited proofs are retained separately.
