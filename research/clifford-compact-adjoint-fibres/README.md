# A compact adjoint and an off-span canonical Clifford decoder

At four qubits and tensor width 13, one affine-quadratic observation gives **one eight-bit affine-quadratic chart per requested symplectic fibre** of the Hilbert adjoint $A^*y$. The chart gives all 256 Pauli-labelled coefficients with their absolute complex phases. It can be zero; otherwise its support is an affine subspace of size $2^d$, with every $0\le d\le8$ attainable. The computation reads the input chart once and uses one symbolic Gauss elimination per named target. [Construction, sharpness and costs](PROOF.md) · [Executable](adjoint.py)

For the repeated site observation $y=(\operatorname{vec}|a\rangle\langle b|)^{\otimes13}$ formed from any two normalized four-qubit stabilizer states in the indicated Gaussian-dyadic gauges, **five rational numbers encode every coefficient of the full Moore–Penrose solution** $A^\dagger y=(A^*A)^{-1}A^*y$. Exactly 8,338,459,852,800 coefficients are nonzero. The orthogonal projection $AA^\dagger y$ has squared norm $478566778595/5856573836677349376$, so these unit-norm observations lie strictly outside the Clifford column span. This covers all 1,348,358,400 ordered pairs of stabilizer lines, including all repeated matrix units. Finite linear combinations of these inputs can be queried by linearity. [Five-weight formula and proof](CANONICAL.md) · [Exact executable](canonical.py)

An arbitrary computational point observation, including different coordinates at the 13 sites, can force between **5,411,658,792,960 and 8,338,459,852,800** nonzero adjoint coefficients. Both extrema have explicit witnesses, and the support calculation counts the occupied coefficients on any supplied point by visiting just the 67 binary subspaces in four dimensions. [Exact census and witnesses](COORDINATES.md)

## Replay and input

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-compact-adjoint-fibres
```

`adjoint.py request.json` accepts either a 104-bit `chart` or a retained #5704 `circuit` with optional `initial`. Columns of each `target` are the binary images of the eight Pauli basis labels. A chart is the list `[width, offset, independent_columns, phase_terms, real, imag, denominator_bits]` with Gaussian integer scalar divided by a power of two. A term is `[variable_mask, coefficient_mod_four]`. Binary rows occupy the high 52 address bits and columns the low 52. This request computes the identity fibre on the zero basis coordinate.

```json
{"circuit":[],"targets":[[1,2,4,8,16,32,64,128]]}
```

It returns `[[8,0,[1,2,4,8],[],1,0,26]]`, with value $2^{-26}$ at all sixteen $Z$ labels. The first checker compares against literal products of 13 matrix entries, exhaustive small parametric Gauss sums and encoded charts with all nine possible support dimensions. An antisymmetric two-point observation cancels on every Clifford column. [Adjoint verification](verify_adjoint.py)

`canonical.py request.json` evaluates individual Moore–Penrose coefficients on a repeated site, using the observable row and column and an array of `[target, Pauli_label]` pairs. Optional `left_basis` and `right_basis` are the symplectic maps whose fixed lifts supply the desired stabilizer bases; both default to the computational basis. The example returns the exact real coefficient `279183413/16081633325721600` and zero imaginary part.

```json
{"row":0,"column":0,"queries":[[[1,2,4,8,16,32,64,128],0]]}
```

One implementation constructs the five-dimensional normal equations using the displacements of 2,295 Lagrangians under native conjugacy representatives. A second derives their spectral solution from the dual polar distance graph and previously published character degrees. [Canonical verification](verify_canonical.py) · [Independent spherical computation](spherical.py) · [Coordinate verification](check_coordinates.py)

## Open next questions

Which repeated *entangled* eight-bit stabilizer sites have a small spherical calculation for $A^\dagger y$? Classify their Schmidt ranks and the corresponding left/right stabilizers, then check whether the adjoint matrix coordinates still lie in a manageable invariant subspace. General affine-quadratic input now has a requested-fibre adjoint, but a compact canonical inverse on that full domain would also have to apply the inverse Gram to its potentially dense output.

## Sources and scope

Ali Romman's #5704 and #5727 supply the absolute-phase affine-quadratic engine, binary solves and one-pair contractions. The width-13 conventions, symplectic lifts and scalar central Gram reduction are from apoursh's #7800 and #7816, using the Clifford framework of alephnan and the spectral work of Nick Petalas and Ali Romman. The spherical cross-check uses the #7772 spectrum. The retained files have immutable hashes and the original attribution notices. This contribution addresses observation and decoder arithmetic under the supplied representation. Its results preserve the selected conditional multiplication exponent. Prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. [Source pins](SOURCE-PINS.json) · [Public claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19756928)
