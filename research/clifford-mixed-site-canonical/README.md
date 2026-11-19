# Canonical Clifford decoding of mixed width-13 sites

For four qubits, let $A$ be the full width-13 tensor-power Clifford dictionary. This package computes exact Moore–Penrose coefficients for two families of observations that can lie outside its column span.

| Supplied observation | Exact canonical readout |
|---|---|
| An arbitrary 52-qubit row observation $\psi$ and one repeated normalized input stabilizer column | A four-bit feature at each of 2,295 Lagrangians determines every requested label. A supplied entangled affine-quadratic row chart takes at most one Gaussian elimination per vertex. On unrestricted $\psi$, the map has exact rank **36,720**. [Construction and rank proof](PROOF.md) |
| Twelve copies of a rank-one stabilizer matrix $B$ and one arbitrary $16\times16$ matrix $C$ | The two-sided singleton uses a 20-class action on pointed Lagrangian flags. A single Walsh transform per symplectic target supplies weights for every entry of $C$. The 256-dimensional singleton subspace has three principal angles against the Clifford span. [Pointed-flag decoder](POINTED.md) |

When all input columns agree and the 13 output row coordinates vary, the support of the canonical coefficient vector is classified for *every* row list by a binary quadratic form. Exactly five support sizes occur. Changing one repeated zero row to one gives 6,670,767,882,240 nonzero adjoint entries and 8,338,459,852,800 canonical ones. The zero adjoint fibre at the identity acquires a nonzero canonical coefficient. [Support criterion and examples](SUPPORT.md)

The full inverse Gram on the 34,425 pointed flags has 11 distinct eigenvalues and least common odd denominator 4,073,770,240,465,467,939,271,875. A single orbital entry attains it. The restriction to the singleton matrix-unit inputs has a smaller odd denominator. Both checks use exact rational arithmetic. [Flag character spectrum and denominator witness](FLAG-SPECTRUM.md)

## Reproduce

Run from the repository root on CPython 3.12. The registered verifiers use only the standard library. They check literal mixed tensor products and complex phases, entangled observations, the quadratic-form orbit census, the full pointed orbital inverse and an independent permutation-character decomposition.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-mixed-site-canonical
```

For the one-sided query, pass the following JSON to the program as a file with `python3.12 -B mixed.py input.json`. The row chart uses the #5704 affine-quadratic representation on 52 bits. Four-bit nibbles are the thirteen sites, least-significant site first. Optional `right_basis` and `column` specify $b=U_R|c\rangle$ and default to the computational zero state. The output uses exact real and imaginary rational strings. [One-sided executable](mixed.py)

```json
{"row_chart":[52,1,[],[],1,0,0],"column":0,"queries":[[[1,2,4,8,16,32,64,128],16]]}
```

The result is `[["-1965636949/32404491151329024000","0"]]`. For the two-sided singleton, `pointed.py` takes the repeated site and the nonzero entries of $C$ in the specified left and right stabilizer bases. [Executable](pointed.py) · [Input example and expected result](POINTED.md)

## Open next questions

1. Can additional varying input columns be treated through a common flag module whose dimension is well below the symplectic group order? Begin with two independently varying singleton factors and compute the representation required for both compatibility projectors.
2. Can a row producer supply the Lagrangian features in tape order and synthesize a requested inverse entry at a competitive physical cost? The present operation counts begin at a supplied row chart or finite singleton matrix.

## Attribution and scope

Ali Romman's affine-quadratic computations in #5704 and #5727, the Clifford sector and spectrum work by alephnan, Nick Petalas and Ali Romman, and the #7772 character calculation underpin the retained inputs. Prior work by apoursh supplied the scalar Gram convolution (#7816) and the repeated-site canonical reduction (#7821). The present extension, proofs and verifiers were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. These decoder results leave the selected conditional multiplication exponent at 0.00363005817. [Source pins](SOURCE-PINS.json) · [Retained license and notices](predecessor/source/engine/source/) · [Coordination claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19757299)
