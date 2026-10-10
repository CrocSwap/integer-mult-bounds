# The p = 10 paired-cube bit word

This word is built by #285's gen5 generator (eumemic's PR168 generator with #276's gen4 local-design and
centre-sharing changes) at cube size **p = 10**: h = 20 coordinates and v = 8·C(10,3) = 960 sources.

The generator's only p = 10 changes are:

- the p = 10 entries of MODULES/QMODULES (`pm_p10.json`, `qmod_p10.json`);
- the variant-u output merge, which is on at p = 10 as at p = 12;
- the cube-local design, which is read from `producer/data/local_design_p10.json`.

Its virtual profile:

- R = 9,120 (= c + q − |M| = 11,820 + 3,620 − 6,320);
- W = 11,040, m = 3h = 60 and deficit 840 = 2v − 3h(h−2);
- 2,160 gauges: 1,200 of rank 16 and 960 of rank 17.

| data file | content |
| --- | --- |
| `pm_p10.json` | pair + copied-centre module, 36 inputs, 273 additions, 37 roots (36 outputs and the centre star) |
| `qmod_p10.json` | all-but-one module, 8 inputs, 24 additions |
| `local_design_p10.json` | per-cube recipe trees (cube-local, so independent of p) from a pair-aware local design search run on the p = 12 word, reused unchanged |
| `arcs_p10.json` | the frozen carrier matching (6,320 arcs) |

Both modules were annealed against the exact one-instance compile cost, starting from restrictions of gen5's
p = 12 modules.

## Physical layer

`producer/make_physical.py --bank-parity` adds the compensated reuse pairs. Each recipient is a rank h − 3 = 17
gauged role, read right before its first operation. Each donor is a dead ungauged non-root non-source register
whose last frame lies in the recipient gauge. The pairing is a maximum Hopcroft–Karp matching under PR200's
rules, and it matches 892 of the 960 recipient candidates.

`--bank-parity` then makes the 60-replica bank width divisible by m = 5h = 100: it drops the fewest trailing
pairs that achieve 60·width ≡ 0 (mod 100). At p = 12 this is gen5's parity rule. Here it drops two pairs,
[3454, 9119] and [3409, 9118]: each adds 3 to the width, and 144,204 ≡ 4 (mod 5). That leaves **890 pairs**.

`producer/descent.py` moves 998 operation frames under PR200's descent rules, with the five-stage first-order
cost r·ln(m/r) at m = 100.

The physical word has R = 8,230 and 1,270 independent entrances (1,200 of rank 16 and 70 of rank 17).

## Reproduce

```sh
python3 -B bitword/producer/regenerate.py --work /new/scratch/dir
```

This runs the generator on the frozen arcs, then both producers, and checks that all five pinned files in
`selected/bit` are reproduced exactly. It takes one to two minutes. `verify.py` never runs a producer.

For new module data, `regenerate.py --solve-matching --emit DIR` recomputes the matching on a scratch copy of
`producer/`, recompiles on the new frozen arcs, and writes the new five files and `arcs_p10.json` to DIR. See
`../discovery/REPIN.md`.

## PR200 classes

`bit/word.py` and `bit/base_word.py` are Chafik Boukhalfa's PR200 classes. `word.py` changes only its input file
names: PR200 named its own p = 12 files, and two lines (plus a comment) now read the cube size from the single
`graph_pP.json`; the frame-loading line also checks the graph's p and h. `base_word.py` is unchanged.
