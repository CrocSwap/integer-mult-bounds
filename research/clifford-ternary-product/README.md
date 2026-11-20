# Multiply binary integers from decoded Clifford observations

This multiplier reads two ordinary binary words, detects an affine-quadratic structure, and writes their exact carried product. For a dense structured family its complete running time on fixed sequential tapes is O(n), where n is the input bit length. A larger family admits a growing number of independently chosen Clifford charts per operand. Its time is O(n(log log(n+4))^0.831). Both use O(n) storage. Admission and rejection include all input reads. A rejected pair runs the existing complete multiplier. [Construction and complete costs](PROOF.md) · [Executable entry point](multiply.py) · [Comparisons](COMPARISONS.md)

An example of an admissible dense operand is an arbitrary repeated u-bit word plus or minus a shifted defect, where u grows as 2^floor(m/2) and 3^m is comparable to n. At positions whose ternary digits are zero or one, the defect bits can be arbitrary Boolean quadratics on an unknown affine support. Its other bits are zero. Both the period and the quadratic data can vary independently between operands. In the larger family the high address selects one of many independent quadratic charts. Binary carries in forming the dense operands are allowed. The input supplies none of these descriptions.

The decoder learns the diagonal Clifford sign operators from the bits and certifies every position. Each output trit requests |00⟩, the unnormalised Bell sum |01⟩+|10⟩, or |11⟩. These are the coordinate readouts of the local symmetric Pauli expansion. A partial observation of two chart states has one affine support, a quadratic sign and one power of two. The power changes by at most one per tree edge. The consumer can therefore deposit contributions directly at the destination bit and carry them in linear total travel. [Raw input and output tapes](IO.md) · [Clifford decoder](contraction.py) · [Independent-sector consumer](sectors.py)

On a proved subfamily, the ordinary uncarried defect coefficients need Ω(n log n) bits to write, even if the method omits all zero coefficients. The new construction produces the same ordinary product in O(n). Sparse pair enumeration would visit Ω(4^m) pairs. Examples also require exponential exact tensor-train bond under every ordering of the m address bits. The fixed complete Fourier schedule of [PR #7849](https://github.com/CrocSwap/integer-mult-bounds/pull/7849) and the grouped Gaussian schedule of [PR #7846](https://github.com/CrocSwap/integer-mult-bounds/pull/7846) both require superlinear field movement on those same inputs. These are source-specific lower bounds and a coefficient-output size theorem. Other representations can have different prices. The worst-case multiplication exponent remains the fallback's proposed κ=0.00387992803556. Main's selected conditional κ is 0.00363005817. [Full comparison and hard families](COMPARISONS.md) · [Selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/certificates/selected-result.json)

## Reproduce

Use CPython 3.12 at the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/clifford-ternary-product
```

Expected final line

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/clifford-ternary-product outcome=completed
```

The independent graph fixture produces a 13,119-bit answer from two dense 6,560-bit inputs. The larger-class fixture uses sixteen separate charts per operand and executes all 256 compatible block products. Each compares the exact output with an independent ordinary integer multiplication. The test harness alone uses that oracle. A separate check executes a rejected product through the retained Fourier code on a small geometry and checks the coefficients before carry. [Hard instance](check_comparators.py) · [Multi-chart and Pauli checks](check_sectors.py) · [Verification receipt](EVIDENCE.json) · [Formal coverage](VERIFICATION.md)

## Open next questions

- Can the decoder share equal intermediate charts between high sectors while preserving their absolute signs and all output credits? This could reduce the factor (4/3)^h on larger mixtures.
- Can the physical address map admit a denser set of interacting defect positions? An address carry can change the Bell condition. A successful extension must construct and price that extra state on every branch.

[Attribution and exact predecessors](CREDITS.md) · [Research Discussion](https://github.com/CrocSwap/integer-mult-bounds/discussions/7850)
