# Paid causal operation-frame search on PR168

This additive experiment improves PR169's operation-frame plan on PR168's finite bit word by alternating causal frame descents and ascents. It keeps all 41,288 scalar operations, 22,252 auxiliary roles, 5,720 entrance gauges, root order and source-mixing events.

| Exact paid quantity | PR169 initial frames | New frames |
|---|---:|---:|
| Coarse saving, `10^-18` grid | 0.000611502306907378 | **0.000611792601240870** |
| Ordinary saving, least paid atom | 0.0006111520908422553 | **0.0006114420415235511** |
| Operations using replacement frames | 1,716 | 2,196 |
| Persistent stock `W` | 25,772 | 25,772 |

The ordinary savings in the table use the same exact least-atom rule on both profiles; they are not a comparison against PR169's published fixed `10^-3` atom. Both pay the complete inherited `10^-16` bad-class envelope with `32*m^2` fallback children per edge. The adjoining refinement package reprices the resulting row with its separately certified envelope and full assembly. This package alone certifies the finite supplier and does not claim a final assembled multiplication bound.

The search starts from Joel Pulikkan's (GamingPuzzled) [PR169 replacement plan](https://github.com/CrocSwap/integer-mult-bounds/pull/169), retained byte-for-byte in `initial.json`. It accepts 240 downward prefix moves and 120 upward suffix moves. Every accepted move improves the complete paid boundary moment by an exact rational interval comparison. The final plan stabilizes after two alternating sweeps. No optimality claim is made.

Three controlled starts were tested: PR169's plan, its pointwise intersection with our earlier 2,172-frame plan, and their pointwise span. All three passed exact frame checks. The PR169 start and span start produced identical final replacement frames; the intersection start retained the earlier paid profile. The simpler PR169 start is selected. Relative to our earlier plan, its paid coarse saving rises from 0.000611783537629951 to 0.000611792601240870.

From the repository root:

```sh
python -B research/paired-cube-bit-descent/verify.py
python -B research/paired-cube-bit-descent/search.py
```

The first command independently checks all final frames, physical and target chains, conservative value spans, every F2 and integer source/target/dirty-register column, exact Gram determinant factors, the complete recounted child profile, adjacent coarse-grid acceptance/rejection and the strict atom toll. Seven adverse controls must fail. The second command reproduces `frames.json` without writing. `verify.py --reproduce-search` performs both. `--write` is an explicit authoring mode.

`SOURCE.json` pins the checker, plan, search, arithmetic, source inputs and notices. The 1,728 distinct replacement bases have fully factored Gram determinants; their largest determinant has 103 bits, but every prime factor is below `2^80`. Bounding the unfactored determinant itself is unnecessary. All retained primes remain allowed.

See [PROOF.md](PROOF.md) for the finite argument and [NOTICE](NOTICE) for the inherited construction and code lineage. The source-specified all-size compiler, tensor, internally borrowed/restored row and analytic contracts remain assumptions.
