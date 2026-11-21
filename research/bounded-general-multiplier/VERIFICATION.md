# Verification and limits

From the repository root use CPython 3.12. The registered portable package has no third-party Python dependency. Its ten external input files are pinned on canonical main. The two pending native/source programmes, the changed mixed price and selected predecessor code are included as authenticated bytes. The scientific commands read the exported package without fetching pull-request refs. [Manifest](VERIFY.json) · [Source hashes](SOURCES.json) · [Run receipts and exact bounds](EVIDENCE.json)

```sh
p=research/bounded-general-multiplier
python3.12 -B scripts/research_package.py --package "$p"
python3.12 -B scripts/check_research_commit.py --package "$p" --check-source-history --check-modes
```

The seven registered commands exercise the following boundaries.

- Recompute the exact carrier and stock arithmetic and the first direct-caller geometry using integer comparisons. Enumerate the complete small group and test a low-to-low action and its pivot rule. Rehash every retained local file, including the documented local modifications. A partially scaled invertible matrix becomes singular, so removing singular slots between its *row* instructions loses real data. [Numerical and source checks](check_resources.py)
- Re-read the raw binary and complex native configurations and both priced callers. Recover 20,706 and 52,512 productive labels and 107,460 and 283,152 separately ordered paid labels. Check two powered binary paths at equal total rank with different real first-position cutoffs and the literal complex floor. Exercise the powered producer and periodic scheduler together, including live nonzero private centres. [Powered tag check](check_powered.py)
- Replay 2,080 incidence maps, including 1,953 with a repeated coordinate. Check exact independent Walsh spectra on 64 arbitrary dense Gaussian fields of 4,096 entries each. Check full noncoordinate weighted swaps over $\mathbb Z/27$ and nested exits on 256 independent fields. These fixtures instantiate the parameterized compiler on small native words. [Periodic check](check_periodic.py)
- Recover all 636 raw chart frames, 111 port frames, 2,874 MOVE occurrences and 458 helper occurrences. Compare 1,216 physical terminal outputs over full residue rings and compare 738 complete coefficient words against the independent earlier dense implementation. Execute the full nontrivial ternary high flow and 95,940 cold records. [Ternary check](check_ternary.py)
- Exercise 60 true-type splitter fixtures with 7,808 records and five right-route shapes with 384,426 records. Compare every genuine returned address with direct modular matrix multiplication before applying inverses. Use the output of a distinct ordinal construction to verify the lexicographic low enumeration. Require the earlier high-swap receiver whenever a higher-width exchange is used. Inspect all real swap widths, prefix, gap and suffix volumes. [Independent stream oracle](check_streaming.py)
- Check stable forward and changed-return layouts and recursively consume and erase sibling packets. The explicit top-of-stack test prevents a hidden traversal of the other $G-1$ packets. [Sibling test](stack_cut.py)
- Run the public finite multiplication dispatcher with signed, imbalanced, maximal-digit and zero inputs. Check normalized NTT directions with a separate direct sum. Compare 104 packed products and force a case above the chosen test transform capacity to issue multiple genuine children. Run both input CRTs, both forward transforms, the spectral product, the opposite transform, normalization, inverse CRT and carry for 741503 times 466013. Compare the ternary physical receiver independently on dirty signed complex coordinate labels. [Product test](check_product.py)

The compiled checks used Apple clang 21.0.0. The sanitizer executable uses an independent byte-schoolbook oracle and the packed ABI. The private-grid test routes actual 4,100-bit scalar products from a complete signed Fourier product into the new packed implementation.

```sh
p=research/bounded-general-multiplier
cc -std=c11 -O3 -Wall -Wextra -Werror -fPIC -shared "$p/short_product.c" -o "$p/short_product.so"
python3.12 -IB "$p/check_product.py" "$p/short_product.so"
python3.12 -IB "$p/check_machine_words.py" "$p/short_product.so"
cc -O1 -g -Wall -Wextra -Werror -fsanitize=address,undefined -fno-omit-frame-pointer "$p/short_product.c" "$p/check_packed_c.c" -o /tmp/bounded-multiply-sanitized
/tmp/bounded-multiply-sanitized
```

Expected terminal markers are `PASS_GENERAL_PRODUCT`, `PASS_PACKED_FOURIER_WORDS` and `PASS_SANITIZED_PACKED 1073 products and 3 extent guards`. The wide-grid check made 116,534 packed multiplications. The larger public benchmarks, GMP adapter, separate process-memory checks and full sample distributions are in [the measurement record](MEASUREMENTS.json). To time only the package and CPython, omit the optional GMP library. To reproduce that comparator, compile the GMP adapter with the system's GMP headers and library.

```sh
python3.12 -IB "$p/benchmark.py" "$p/short_product.so" --sizes 4096 16384 65536 262144 1048576 4194304 --rounds 5
python3.12 -IB "$p/benchmark.py" "$p/short_product.so" --sizes 33554432 --rounds 3 --skip-profile
python3.12 -IB "$p/measure_storage.py" 4194304 --library "$p/short_product.so"
python3.12 -IB "$p/measure_storage.py" 4194304
```

## Kernel checks

Use Lean 4.34.1, Lake, mathlib commit `d13f23b723b8a846827a245b89c10fc7d3f11612` and the pinned transitive dependencies in the Lake manifest. Install or cache these dependencies first. The verification script builds the 18 modules, checks all reported axioms and uses `leanchecker -v` independently on each output. A local exact power enclosure uses kernel reduction. Decimal arithmetic is used only to propose the dyadic endpoints. [Toolchain](lean/lean-toolchain) · [Manifest](lean/lake-manifest.json) · [Kernel driver](verify_formal.py)

```sh
python3.12 -IB research/bounded-general-multiplier/verify_formal.py
```

The declarations cover the complex static tensor debit at its actual rational powers, the row and owner debit, the induction from counted recursive occurrences to both actual carrier prices, chronological finite-order cancellation, the weighted ternary terminal, low-cube padding and regularity, changed returns, and the simultaneous six-stage stock cutoff. The axiom union at the reported endpoints is `propext`, `Classical.choice` and `Quot.sound`. No added axiom, `sorry` or native decision shortcut is used. [Applied terminal prices](lean/CarrierApplication.lean) · [Chronological action](lean/PeriodicCover.lean) · [Weighted physical leaf](lean/TernaryRouting.lean) · [Exact group size bound](lean/CubeFacts.lean) · [Stock](lean/StockThreshold.lean)

The correspondence from raw native opcode to the priced per-node recurrence, the proof of the sequential tape clocks, the binding of the inherited Fourier precision proof to the numerical code and the final all-size multiplication theorem are written mathematics. Source tests and finite replays serve as independent checks of these bindings. There is no Lean theorem here that runs a general multitape machine from two input strings to the final product or computes its best time constant. No production-size uniform template was materialized. Earlier raw native identity and analytic suites outside the changed path were not rerun in full. The published source proofs and credits remain dependencies. [Complete proof and resource bounds](STREAMED-MACHINE.md) · [Attribution](NOTICE.md)
