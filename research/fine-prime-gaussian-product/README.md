# Fine-prime Gaussian multiplication from binary operands

`product.py` accepts two unsigned binary strings. It chooses its geometry, generates and encodes the Gaussian coefficients, reads them back, and uses them to produce an exact binary product. Two forward transforms and one opposite transform use the same generated source and target coordinates. The fast path calls neither a dense Fourier transform nor whole-input integer multiplication.

On the (5,7) source and (8,8) target it returns **345550037539** for 741503 × 466013. Before carrying, its 35 base-256 coefficients are **11811, 10996, 4152, 868, 77**, followed by 30 zeroes. The earlier physical sandwich returned zero on its diagnostic packet and rejected that packet in production. This implementation gives that packet no production entry. On a second admitted source of size 31 × 29, two padded cells are strict interiors of a pure Gaussian block. The same public multiplier recovers 899 base-16 coefficients, with a uniform rounding radius below 0.000247. [First predecessor execution](../physical-tensor-crt-sandwich-recovery/README.md) · [Product checks](verify_product.py) · [Interior product](verify_interior.py)

## Construction and scope

The coefficient producer replaces the old concentration ABI with a short, gauged circulant on each complete dyadic block and an exact correction on the edges and holes. A bordered Schur solve supplies the inverse correction. The dense reference matrices are private, input-independent setup. Every online circle, convolution, sparse correction and coordinate conversion operates on the real payload. The caller generates the chirps, executes polynomial convolution with a single compensating scale, restores both source-size factors and all three Gaussian normalizers, then rounds and carries in ordinary digit order. [Construction and complete invoice](PROOF.md) · [Numerical proof](ACCURACY.md)

The growing geometry uses q=8p₀, p₀=6ceil(log₂ n). It admits every sufficiently large input length under the source results listed in the proof. Its largest charged time power before log factors is 0.998268211 in log₂ n, with O(n) backing plus the fixed source constant. This fits the proposed #4100 budget. The comparison depends on the retained dyadic all-column template, the logical compact BIT caller and its row/stock bounds, and the physical short-word multiplication theorem. The product supplies the actual Gaussian, ring, CRT and recovery connections. It makes no change to the selected conditional κ. [#4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) · [Exact scope and sources](SOURCES.md)

The finite runs exercise small primitive branches. The eventual funded recursive word and the complete production-prime GL₆₄ payload exceed practical replay sizes. The Python interpreter supplies executable finite instances and a record-head model. The all-size complexity statement concerns the uniform fixed-tape algorithm. The receipts do not measure wall-clock speedup, interpreter memory or peer acceptance. [Physical ordinary binding](ORDINARY.md) · [Verification coverage](VERIFICATION.md)

## Reproduce

Use Python 3.12 and the standard library from the repository root. The first command takes the two operands as literal binary strings.

```sh
python3.12 -I -B research/fine-prime-gaussian-product/product.py 10110101000001111111 1110001110001011101
python3.12 -I -O -B research/fine-prime-gaussian-product/verify_product.py
python3.12 -I -O -B research/fine-prime-gaussian-product/verify_interior.py
python3.12 -B scripts/research_package.py --package research/fine-prime-gaussian-product
```

The CLI returns exactly twice the larger input length in bits, including leading zeros. With `--receipt`, the optional JSON diagnostic gives the actual route, geometry, grid, normalization, pre-carry coefficients, a rational error upper bound and model counters. The small fixture returns `0101000001110100011000110010001000100011`. [Implementation](product.py) · [Replay manifest](VERIFY.json)

## Open next questions

1. Can an independent reviewer verify the full physical compact436 refinement at its retained root and stock interfaces? Start with the correspondence between chronological source calls and continuation labels. [Ordinary proof](ORDINARY.md)
2. Can the crossover of a funded simultaneous butterfly be brought within executable reach? The proof identifies an eventually found fixed word. The tests execute the same recursion on smaller checked words. [Butterfly proof](BUTTERFLIES.md)
3. Does the selected shared-native construction itself admit this changed outer parameter choice and its faster numerical target? This package proves a comparison against #4100. The selected application has its own stricter budgets and assumptions. [Selected record](../../certificates/selected-result.json)

Prepared for Ali Romman with substantial OpenAI Codex assistance in research, implementation, adversarial checks and writing. New material is Apache-2.0. [Predecessor credit](SOURCES.md) · [Coordination](https://github.com/CrocSwap/integer-mult-bounds/discussions/7832)
