# Reproduce the result and inspect its limits

## Executable checks

Use CPython 3.12 and its standard library. From the repository root run

```sh
python3.12 -B scripts/research_package.py --package research/clifford-ternary-product
```

Expected final line

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/clifford-ternary-product outcome=completed
```

The [registered manifest](VERIFY.json) specifies eight serial commands. The receipt records the observed outputs. [Machine-readable evidence](EVIDENCE.json)

- The projection checker compares 77,568 individual values against explicit binary sums. It covers all sets of two-variable affine equations and phase functions, followed by larger seeded charts. It tests absolute sign, inconsistent support, forced assignments and free doublings. [Projection oracle](check_contraction.py)
- Independent admission tests enumerate all 278 Boolean tables through three variables, of which 214 pass. Another 511 literal records exercise holes, short words and rejection. An independent character oracle supplies the consumers in 256 small products. [I/O tests](check_io.py)
- The public caller checks all 1,024 pairs of five-bit words and both period signs at lengths through 6,560 bits. The separate multi-chart test compares 480 Pauli readouts against a literal dense adjoint and checks all oriented sector pairs through six high sites. Its 16-by-16 chart product yields SHA-256 `21e748302ffb8b27c7fba46aa84ddd18505e8b3f45b5f2d9b424adc77ad15ae8` of 13,119 canonical low-first bit bytes. [Public caller](check_product.py) · [Independent sectors](check_sectors.py)
- A separately generated pair of dense 6,560-bit operands has 4,116 and 3,642 ones. Their 13,119-bit product has SHA-256 `8a003118ae650f5e2d24e1172d0df5f77ba8e1952239b9dbdf00ce93e34c3da9` in the same encoding. The single-chart delivery records 15,449 signed deposits, 9,242 ripples and 82,054 cursor moves. The latter includes ripples and rewinds. Full subtraction, clearing and the final output scans are separate linear terms. The witness also compares all literal coefficient magnitudes and a tensorised Karatsuba interpolation. [Comparator](check_comparators.py)
- Another executable independently checks 21,845 high pairs, 144 *individual* signed passes, 1,016 sector contractions, and twenty dense template and carry variations. These include a late cubic rejection, zero character sentinels, the maximum block carry and preservation of mutable inputs. [Adversarial checks](check_adversarial.py)
- The retained direct Fourier source computes 741503 × 466013 = 345550037539 on a 3-by-5 transform. The five nonzero base-256 coefficients are 11811, 10996, 4152, 868 and 77. The default public length controller rejects this pair from the Clifford branch. Another rejected pair exercises signed recursion past the primitive word cutoff. [Fallback binding](verify.py) · [Vendor hashes](vendor/PINS.json)

## Lean

Use the toolchain in [lean-toolchain](lean/lean-toolchain) and the immutable mathlib/dependency revisions in [lake-manifest.json](lean/lake-manifest.json). On first use, install the pinned mathlib cache if needed. From the repository root run

```sh
cd research/clifford-ternary-product/lean
lake exe cache get
lake --wfail build
lake env leanchecker -v CompleteProduct
```

To replay every local module in the kernel, run the following command from that same directory.

```sh
for file in *.lean; do lake env leanchecker -v "${file%.lean}" || exit 1; done
```

The build prints the axioms of the named results. The complete product theorem uses `propext`, `Classical.choice` and `Quot.sound`. The module hashes, replayed modules and printed declarations are in the receipt. Each statement was elaborated and kernel-checked. The proof uses finite sums, arithmetic and the standard Lean kernel with mathlib. It introduces no research axiom or unchecked numerical oracle.

| Statement | Formal coverage |
|---|---|
| The observation required at each address | An explicit bijection records both orientations of every mixed trit. Trace identities give the tensor-I/X/Z frame and its converse on arbitrary integer joint tables. [Address collection](lean/TernaryCollect.lean) · [Pauli readout](lean/PauliReadout.lean) · [Equivalence](lean/PauliEquivalence.lean) |
| Unknown phase and conditional observations | Origin, singleton and pair probes determine the quadratic on the affine coordinates. Constraint pivots and free derivatives implement exact signed Gaussian summation. A projected prefix has one surviving quadratic chart and a bounded power-of-two shift. [Interpolation](lean/RawInterpolation.lean) · [Gauss evaluator](lean/BooleanGauss.lean) · [Boundary](lean/BellBoundary.lean) |
| Construction of the sparse product | The three-child prefix traversal gives the correct term at each physical trit. All four signs, dual binary accumulators, exact division by four and high radix carries compose for arbitrary separately certified operand fibres. [Traversal-to-product](lean/TrieDelivery.lean) · [Literal blocks](lean/PhysicalBlocks.lean) · [Carry potential](lean/SignedCarry.lean) |
| Movement and dense assembly | Interpreting the ternary Clifford walk produces the addressed deposits. It uses at most 2·3^m−1 directional commands in one pass. Ripples, rewinds and output scans have separate charges. The chart-cost recurrence is linear in leaf count. The short arithmetic includes the protected period, the sliding window and independent residual signs. One theorem composes the unit-move chart-pair products, short-word shifts and windows. [Clifford walk](lean/CliffordHead.lean) · [Traversal price](lean/TapeTraversal.lean) · [Windows](lean/DenseTemplates.lean) · [Combined product](lean/CompleteProduct.lean) |

The final Lean theorem takes explicit equality of *every* raw residual site with its verified chart and zero on every high hole. The producer constructs and checks these predicates. Its affine-hull basis extraction, rejection completeness, raw-to-residual scans, Python row-bitmask and tape refinements, physical compiler constants and asymptotic comparison are written proofs with executable cross-checks. Lean establishes the mathematics on the indicated data, including the sliding arithmetic and signed traversal. There is no end-to-end formal semantics for CPython or for the fixed multitape implementation. [Construction proof](PROOF.md) · [Literal machine](IO.md) · [Cost comparison](COMPARISONS.md)

The bound is a bit-operation and movement result. A wall-clock speedup against a hardware integer library has not been measured. The Python reference uses byte arrays for literal tape tracks and host indices for head positions. The tape proofs implement the relevant traversals and small-table searches with sequential heads. The complex Fourier fallback and complete native supplier prices retain their predecessor proof obligations. Historical frontier and supplier suites were outside this replay. Independent human scientific review remains open.
