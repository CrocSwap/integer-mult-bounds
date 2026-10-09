# Mixed-gap bit module and bit frame descent on #168's paired cubes

Under #168's retained interfaces, this finite witness certifies

$$T(n)=O\big(n(\log n)^{1-\kappa}\big),\qquad \kappa=\frac{6129700}{10^{10}}=6.129700\times10^{-4}.$$

That is **+0.547% over #168** (6.096379e-4) and **+0.31% over #171** (6.110684e-4). The bit supplier binds in #168, so this changes only the p = 12 bit word. The complex supplier and the assembly are #168's, unchanged.

## Change

#168's nested-prefix all-but-one module (n = 10) builds prefixes p_{k+1} = p_k + x_k and suffixes s_k = x_k + s_{k+1}. It forms every middle output y_j (all inputs except x_j) as the **left gap** L: p_{j-1} + (x_{j-1} + s_{j+1}). The mirror image is the **right gap** R: (p_j + x_{j+1}) + s_{j+2}. `module.py` chooses the form per output. A search over the patterns selected **RLLLRRRL**; no single flip of it scores higher. All-L is #168's module and reproduces its saving exactly. The selected module has one more addition than #168's (32 vs 31), but the re-solved carrier matching gains more links than that costs. Net, the bit word has 132 fewer roles per vertex.

The new word is built by #168's unchanged producer, `research/paired-cube-bit/paired_cube_bit_word.py`, with only its p = 12 module swapped. Its operation frames then get the same descent as #169: 1,320 frames, 264 of them leaving their original frame.

| Bit supplier, p = 12 | R | W | Replaced frames | Coarse saving |
|---|---:|---:|---:|---:|
| #168 | 22,252 | 25,772 | 0 | 6105820/10¹⁰ |
| #169 (descent only) | 22,252 | 25,772 | 1,716 | 6115023/10¹⁰ |
| **this** | **22,120** | **25,640** | 1,320 | **6139215/10¹⁰** |

## Verify

```sh
python3 -B research/paired-cube-bit-rl-module/prove.py        # about 3 minutes, standard library
```

0. **Rebuild.** `build.py` rebuilds `out/` byte-identically from the frozen `arcs_p12.json` through #168's producer.
   - #168's standalone bit checker, `check_paired_cube_bit.Checker.run`, then recomputes for `out/`: the exact frames, the decoder identity, every chain, the partner-pair chronology, nondegeneracy, an F2 replay and the ledger.
1. **Replaced frames.** #165's bit checker (`word.py`) applies `replacement-frames.json`. For every replaced frame it checks:
   - value span inside the frame;
   - exact nondegeneracy;
   - nested physical role chains;
   - preserved rank mass, with the full child histogram recounted.

   Then it checks the complete F2 identity and the defining integer decoder over all source, target and dirty columns. The adverse controls are rejected.
2. **Prime witnesses.** Every new Gram determinant factors as powers of 2, 3 and 5 times a residual below 2^80.
3. **Assembly.** #168's own `scripts/paired_cube_network.py` functions, unchanged, certify:
   - the bit moment with its contaminated fallback;
   - the complex supplier and the finite bridge;
   - all 47 strict constraints and 7 margins.

   The next 10⁻¹⁰ coarse and κ grid points are rejected, and so is the original-prefix control. `certificate.json` and `prime-witnesses.json` reproduce byte-identically.

`build.py --solve` re-solves and refreezes the carrier matching. `generate.py` regenerates `replacement-frames.json`; both are discovery steps whose output the checks above verify.

## Scope and credits

All of #168's conditional interfaces remain assumptions. This is not an unconditional multiplication theorem or a runtime claim, and no global optimum is claimed. #171's causal frame refinement (jon314159) is independent of the module and could be stacked on this word.

- Base: #169, on #168 at `98c115b53742b6613ad630de4d493f37b0119da7`.
- The nested-prefix module, word, producer and assembly are eumemic's #168, with its full lineage.
- The bit checker and prime witnesses are chafreaky's #165.
- The frame lemma is #130/#131.

Prepared by Joel Pulikkan (GamingPuzzled) with Anthropic Claude assistance; Apache-2.0.
