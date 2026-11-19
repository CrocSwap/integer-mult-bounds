# Exact canonical Clifford readout with two variable sites

At width thirteen, fix eleven copies of a four-qubit stabilizer matrix unit and supply any joint tensor on the other two sites. This package returns the exact Moore–Penrose coefficient at any requested Clifford label, including for entangled inputs. It answers the two-singleton question in [PR #7823](https://github.com/CrocSwap/integer-mult-bounds/pull/7823).

- The decoder uses 354 orbital weights, shared across all queries. A given symplectic target uses at most 256 Walsh transforms of length 256 for the supplied tensor, then reuses their results across Pauli translates. [Proof](PROOF.md) · [Readout formula](DOUBLE-READOUT.md)
- Exactly 32,896 of the 65,536 input directions are detectable. The kernel consists of the antisymmetric tensors under site exchange. The raw adjoint has thirteen distinct positive squared singular values on the symmetric sector and squared condition number $2{,}100{,}225/2$. [Rank proof and complete spectrum](TWO-SITE-SPECTRUM.md)
- The least common odd denominator for Gaussian-dyadic joint inputs has 115 bits. A single query on a three-term integer input attains it. [Arithmetic proof and witnesses](DENOMINATOR.md)
- The 65,536 ordered pairs of computational matrix units with a fixed repeated unit attain seven different raw adjoint support sizes. The counting formula depends only on three binary ranks. [Support distribution](ADDRESS-CENSUS.md)

## Reproduce

Run the registered checks from the repository root with CPython 3.12.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-two-site-canonical
```

The included example uses $E_{00}^{\otimes11}\otimes E_{10}\otimes E_{01}$. At the identity its raw adjoint entry is zero and its canonical coefficient is $q=3639905331779/47774121329355220800000$. The other two requested labels give $-q$ and zero. Each item of `joint` contains four four-bit matrix indices and a pair of rational real and imaginary components. Each query contains the binary symplectic action (the images of the eight basis vectors) and an eight-bit Pauli label. Optional `left_basis` and `right_basis` supply the stabilizer bases in the same format.

```sh
python3.12 -B research/clifford-two-site-canonical/double_readout.py research/clifford-two-site-canonical/example.json
```

## Open next questions

1. What are the principal angles of the complete two-site subspace with the full dictionary span? Contract the raw and canonical readouts inside the one- and two-dimensional symmetry blocks. The raw normal spectrum already supplies the block indexing; an exact shell average of the cross terms is still needed.
2. What does a tape pay to emit these canonical coefficients from a structured two-site input? Begin with a sparse tensor and compare shared Walsh evaluation and single-coordinate evaluation at the same requested precision. Input production, storage and routing must enter the invoice.

## Attribution and scope

This work builds on the four-qubit Clifford class and character calculations of alephnan, Nick Petalas and Ali Romman, the exact affine-quadratic evaluator by Ali Romman, and the #7816 scalar Gram, #7821 stabilizer phases and #7823 pointed-flag readout by apoursh. The executable predecessor files retain their original bytes, notices and license. The coefficient formula, marked-flag interpolation and two-site calculations here were prepared by apoursh with substantial OpenAI Codex assistance under Apache-2.0. The selected conditional multiplication exponent is $0.00363005817$. [Pinned sources](SOURCE-PINS.json) · [Research claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19757639)
