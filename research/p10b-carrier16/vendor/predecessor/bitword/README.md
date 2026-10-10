# The p = 10 paired-cube bit word

This word is built by #285's gen5 generator (eumemic's PR168 generator with #276's gen4 local-design and
centre-sharing changes) at cube size **p = 10**: h = 20 coordinates and v = 8·C(10,3) = 960 sources. It replaces
#315's p = 10 word.

The generator's only p = 10 changes are:

- the p = 10 entries of MODULES/QMODULES (`pm_p10.json`, `qmod_p10.json`);
- the variant-u output merge, which is on at p = 10 as at p = 12;
- the cube-local design, which is read from `producer/data/local_design_p10.json`;
- the cube orientation, which is read from `producer/data/cube_orient_p10.json` when that file is present.
  Without it, cubes are sorted as before.

Its virtual profile:

- R = 9,060 (= c + q − |M| = 11,460 + 3,620 − 6,020);
- W = 10,980, m = 3h = 60 and deficit 840 = 2v − 3h(h−2);
- 2,160 gauges: 1,200 of rank 16 and 960 of rank 17.

| data file | content |
| --- | --- |
| `pm_p10.json` | pair + copied-centre module, 36 inputs, 273 additions, 37 roots (36 outputs and the centre star), carrier debt 92 |
| `qmod_p10.json` | all-but-one module, 8 inputs, 24 additions (#315's, unchanged) |
| `local_design_p10.json` | per-cube recipe trees, re-searched at p = 10: 24 local additions per cube |
| `cube_orient_p10.json` | for each 3-subset in combinations order, the ordered triple used as cube positions 0, 1, 2 |
| `arcs_p10.json` | the frozen carrier matching (6,020 arcs) |

**Pair module.** It was re-annealed from #315's module. The objective is the exact one-instance compile cost with
five-stage weights plus λ·debt (λ = 150 to 300). The debt counts module additions that do not donate to a carrier
arc. Additions stay at 273, carrier arcs go from 178 to 181, and the debt goes from 95 to 92. #315's modules were
themselves annealed from restrictions of gen5's p = 12 modules.

**Local design.** #315 reused a design found by a pair-aware search on the p = 12 word. This design was found at
p = 10 by 1-move steepest ascent from #315's design, scored on the five-stage virtual price of the full word. It
stopped at a local optimum after two moves, which changed 2 of the 12 plane recipes. Because subtrees are shared,
a cube takes 24 local additions instead of 27 and 8 local carrier arcs instead of 11 (local debt 16, unchanged).

**Cube orientation.** Position 0 of a cube carries face0, the generator's 4-target root. With sorted cubes,
coordinate 0 is position 0 in C(9,2) = 36 cubes and coordinate 9 in none. The file instead lists each cube as a
cyclic rotation of its sorted triple whose position 0 follows the largest cyclic gap (mod 10). In the one rotation
orbit with gaps 4, 4, 2, position 0 is the element between the two gaps of 4. The rule is rotation-equivariant,
so each coordinate is position 0, 1 and 2 in exactly 12 cubes each. In the research runs, orientation alone left R
and the five-stage virtual price unchanged; it changes which reuse donors fit which recipients (below).

## Physical layer

`producer/make_physical.py --bank-parity` adds the compensated reuse pairs. Each recipient is a rank h − 3 = 17
gauged role, read right before its first operation. Each donor is a dead ungauged non-root non-source register
whose last frame lies in the recipient gauge. Those are PR200's rules, unchanged.

Among the maximum matchings under those rules, the producer now picks one by tiered augmentation. #315 used
Hopcroft–Karp, which ignores donor value. The first-order five-stage value of a pair grows with the donor's
end-frame dimension e. Donors are therefore admitted in tiers of decreasing e. Each tier extends the current
matching by Kuhn augmenting paths until none is left among the donors admitted so far. An augmenting path never
unmatches a matched donor, so this is the greedy algorithm on the transversal matroid of donors. For every
threshold t, as many donors with e ≥ t are matched as any matching allows. The last tier is the whole candidate
graph, run until no augmenting path remains, so the result is a maximum matching (Berge). It matches all 960
recipient candidates. On sorted cubes #315's maximum matching reached only 892.

`--bank-parity` would then drop the fewest trailing pairs needed to make the 60-replica bank width divisible by
m = 5h = 100. Here the width is 4·1,200 + 20·6,900 = 142,800 ≡ 0 (mod 5), so **no pair is dropped** and all
**960 pairs** remain. #315 dropped two of its 892.

`producer/descent.py` moves 1,183 operation frames under PR200's descent rules, with the five-stage first-order
cost r·ln(m/r) at m = 100.

The physical word has R = 8,100 and 1,200 independent entrances, all of rank 16.

## Reproduce

```sh
python3 -B bitword/producer/regenerate.py --work /new/scratch/dir
```

This runs the generator on the frozen arcs, then both producers, and checks that all five pinned files in
`selected/bit` are reproduced exactly. It takes one to two minutes. `verify.py` never runs a producer.

For new module, design or orientation data, `regenerate.py --solve-matching --emit DIR` recomputes the matching
on a scratch copy of `producer/`, recompiles on the new frozen arcs, and writes the new five files and
`arcs_p10.json` to DIR. See `../discovery/REPIN.md`.

## PR200 classes

`bit/word.py` and `bit/base_word.py` are Chafik Boukhalfa's PR200 classes. `word.py` changes only its input file
names: PR200 named its own p = 12 files, and two lines (plus a comment) now read the cube size from the single
`graph_pP.json`; the frame-loading line also checks the graph's p and h. `base_word.py` is unchanged.
