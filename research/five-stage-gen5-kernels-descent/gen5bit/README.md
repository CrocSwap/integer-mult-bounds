# gen5: the paired-cube bit word

gen5 is #276's gen4 word (PR168's p = 12 paired-cube bit word with the arc-aware local design and the
centre-sharing pair module) with two module circuits replaced. The generator is identical to #276's
apart from two added comment lines. Only the module data, `producer/data/pair_module_p12.json` and `producer/data/qmod_p12.json`,
and the frozen arcs differ. The roots, decoder, partner-pair mixing and local design are unchanged.

Its virtual profile:

- R = 17,292 (= c + q − |M|);
- W = 20,812 and deficit 1,936;
- 3,960 gauges.

For comparison, gen4 has R = 17,904, PR200's word 18,908 and main's PR168 word 19,788.

| region | additions − carrier arcs, PR168 (L1) | gen4 | gen5 |
| --- | ---: | ---: | ---: |
| local channels (220 cubes) | 220 × 22 | 220 × 16 | 220 × 16 |
| pair module + centre (24) | 24 × 191 | 24 × 184 | **24 × 164** |
| all-but-one module (132) | 132 × 15 | 132 × 12 | **132 × 11** |
| merges u/w, roots | 1,760 + 6,624 | 1,760 + 6,624 | 1,760 + 6,624 |
| **total R** | **19,788** | **17,904** | **17,292** |

## The modules, and why their objective is compile cost

Each module was annealed against the exact one-instance compile cost C. C is the Σ 3t·ln(72/t) ledger of
a single module instance compiled in its real geometry with the generator's own compiler. The search did
not minimize additions − arcs.

Minimizing debt alone is the wrong objective. A cyclic-interval all-but-one module reaches the proven
floor of debt 10 (80 additions, 70 arcs), yet the whole word then loses 4.5% of its saving, because it cuts
roles into many small rank steps. C predicted that loss.

| module | additions | arcs | debt | C | gen4 debt / C |
| --- | ---: | ---: | ---: | ---: | --- |
| all-but-one (n = 10) | 32 | 21 | 11 | 11,175.33 | 12 / 11,348.83 |
| pair + centre (n = 11, 56 roots) | 463 | 299 | 164 | 59,098.00 | 184 / 61,303.46 |

The annealer was fast because it used exact closed forms for node ranks.

- **Pair module, non-plain node:** rank = 24 − 2|V(E)| + c_b(E) − 2·[reaches the centre]. E is the graph of
  output pairs reachable through consumers and arc targets.
- **Pair module, plain node:** rank = span dimension.
- **All-but-one, non-plain node:** rank = 23 − 2|reach|.

With the compiler's Hopcroft–Karp order, these evaluators reproduce the compile up to a constant offset.

The all-but-one optimum was reached from several random restarts. It also has no improving 1- or 2-move
rewire, which is strong evidence that it is optimal, though not a proof.

## Physical layer

`producer/make_physical.py` (run with `--bank-parity`) adds 1,406 compensated reuse pairs. Each recipient
is a rank-21 gauged role read right before its first operation, and each donor is a dead ungauged non-root
non-source register whose last frame lies in the recipient gauge. The pairing is a maximum Hopcroft–Karp
matching, under PR200's rules.

The `--bank-parity` option drops one pair if the total residual width of the 60-replica banks would be
odd. That does not happen for gen5.

`producer/descent.py` moves 1,710 operation frames under PR200's descent rules.

Physical R = 15,886.

## Reproduce

```sh
python3 -B gen5bit/producer/regenerate.py --work /new/scratch/dir
```

This runs the generator on frozen arcs, then both producers, and checks that all five pinned files in
`selected/bit` are reproduced exactly. It takes about two minutes. `verify.py` never runs a producer.
