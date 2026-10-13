# gen4: the paired-cube bit word

The word is PR168's p = 12 paired-cube bit word (h = 24, v = 1,760 ports), with three structural changes.
The roots, decoder and partner-pair source mixing are unchanged. Its virtual profile is:

- R = 17,904 (= c + q − |M| = 23,380 + 6,624 − 12,100);
- W = 21,424 and deficit 1,936;
- 3,960 gauges, 2,200 of rank 20 and 1,760 of rank 21.

PR200's word has R = 18,908 and main's PR168 word has R = 19,788.

| region | additions − carrier arcs, PR168 (L1) | gen4 |
| --- | ---: | ---: |
| local channels (220 cubes) | 220 × 22 | 220 × 16 |
| pair module + centre (24) | 24 × 191 | 24 × 184 |
| all-but-one module (132) | 132 × 15 | 132 × 12 |
| merges u/w, roots | 1,760 + 6,624 | 1,760 + 6,624 |
| **total R** | **19,788** | **17,904** |

## 1. Arc-aware local design

`local_design()` builds every per-cube plane channel by a recipe tree. The tree is any binary tree of
support-disjoint additions over the cube's sources, not only the edge, face-diagonal or fixed-coordinate
options of PR144, PR189 and PR200.

Each cube uses 29 additions, against 26 for L1. Those additions create 13 in-place carrier arcs, against
4, so the per-cube debt drops from 22 to 16:

- 5 partner-root arcs. The flip01 face-diagonal pairs feed only G01 and hand their control source to its
  partner root.
- 8 chain arcs. A dimension-2 edge pair hands a source on to its direct use at dimension 4.

A CP-SAT model over all 15 recipe trees per plane, with exact initial frames and creation-order ties,
proves 16 is the minimum. Of the 120 annealed designs at debt 16, seed 4 has the best saving.

## 2. Re-annealed all-but-one module

The module has 34 additions and 22 carrier arcs, so its debt is 12 against 15 before. It was annealed with
split-function moves against a one-instance compile of the generator.

## 3. Centre-sharing pair module

The pair module's 56th root is the sum of all 55 inputs, star(2i + bit). It costs 10 extra additions on
existing module nodes. `finish()` uses that root as the copied centre instead of a separate tree of 34
additions. Pair-plus-centre debt drops from 191 to 184.

The centre closure (phase one) grows but stays disjoint from every gauge. `prepare.py` checks this, and so
do PR200's classes and the PR168 checker.

## Physical layer

`producer/make_physical.py` adds 1,494 compensated reuse pairs. Each pairs a rank-21 gauged recipient,
read right before its first operation, with a dead ungauged non-root non-source donor whose last frame
lies in the recipient gauge. The pairing is a maximum Hopcroft–Karp matching. PR200's word has 1,760 such
pairs; gen4 has fewer because its leaner circuit leaves fewer dead registers.

`producer/descent.py` moves equal-frame connected operation groups to the join of their incoming frames
and node spans, or to the meet of their outgoing frames, repairing degenerate endpoints by one row. Gauge,
root, source and target frames stay fixed. A move is accepted only when the five-stage first-order cost
Σ r·ln(120/r) over all physical chains decreases. The result is 1,802 changed operation frames.

Physical R = 16,410.

## Reproduce

```sh
python3 -B gen4bit/producer/regenerate.py --work /new/scratch/dir
```

This runs the generator on frozen arcs, then both producers. It checks that all five pinned files in
`selected/bit` are reproduced exactly, and takes about two minutes. The generator is
`producer/paired_cube_bit_word.py`: eumemic's PR168 generator as integrated on main, plus `local_design()`
and the centre patch in `finish()`. It reads only the four p = 12 data files in `producer/data`.
`verify.py` never runs a producer; the pinned files are the mathematical inputs.
