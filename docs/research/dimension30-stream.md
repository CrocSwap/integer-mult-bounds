# Dimension 30 with batched stream roles

This separate experiment uses the explicit even-dimension matching from
[PR #12](https://github.com/CrocSwap/integer-mult-bounds/pull/12), pinned at
`35d31e30f28bc5da0ae6a88e7b03d75ebc855534`. Its unmodified matching source,
generic-moment example and attribution are retained under `references/pr12`.
The F3 five-set motif is inherited from Zhihao Chen's PR #7; batching and
controlled tensor coordinates are IceKylin's PR #10 contribution.

The selected h30 circuit splits the ground set into 16 and 14 points. It uses
the previously selected local template patterns, then rebuilds four-point
stars and applies the bilateral saturated-frame register compiler at ancestor depth 4.
The checked result is **13,056,812 auxiliary roles**, with center loss 12,180
and no additional frame loss. Its batched arithmetic supports
**κ = 168478/10^12**, or about 103.74 times the starting aligned-bit witness.
This is conditional on the general compiler, tensor, batching and inherited
multiplication arguments. Exact finite checks do not formally verify them.

## Finite checks

The rewritten circuit has 142,506 inputs, 142,941 designated outputs and
14,381,873 retained additions. The physical compiler removes 1,468,002
delivery roles from the 14,524,814-role binary embedding. It checks the full
allocation, every producer-frame transition and every protected output.
The physical rank sum is 399,994,068 in each invocation orientation. The
bilateral extension adds 35,652 dual-frame continuations. An independent
exact-rational dirty-scratch control exercises a strict 24-to-27-dimensional
dual transition and checks its coefficients, frames and wrapper.

The repaired source/dual cut delays 60 source nodes. All resulting frames are
nondegenerate, the source region is ancestor-closed, and all retained pair
totals remain in the source region. The central loss is
`binom(30,2)*(30-2) = 12180`. These properties preserve the scalar interfaces
needed by the tensor-stage and controlled-basis arguments.

PR #7's particular Euler-tour construction does not cover every even
dimension. PR #12 instead gives a Hamilton cycle in the line graph of a
complete graph. Consecutive edges share exactly one vertex; substitution
into the two-full-pair case gives an intersection-two permutation of all
five-sets. The certificate checks all 142,506 images and their intersections.

The retained source-span checker stores 28 coordinates. Reproduction creates
isolated copies with 32 coordinates and records the original and generated
source hashes. This is a storage extension: a five-set row has norm√5,
so every square minor through dimension 32 is bounded by 5^16, below 2^61−1.
Modular rank therefore still agrees with rational rank. The star extractor
and independent DAG audit receive corresponding dimension-guard extensions;
their algorithms and the retained source files are unchanged.

Candidate generation uses fingerprint interning for speed. After star
rewriting, an independent canonical-ZDD evaluation checks every addition is
disjoint, every source core is exact, and every output is the required full
intersection-two or pair-total family. The certificate accepts only that
final exact check; no collision assumption enters the claimed result.

## Batched arithmetic

The five recursive widths are 1, `m-4h`, `m-2h²`,
`m-2h²-2h+2`, and `h²`, with `h=30` and `m=h³`.
The controlled stage-two corner remains one block of width `h²`.
Rank masses are recomputed from the final role count. Positive rational
logarithm enclosures, rounded upwards to multiples of 10^-9, certify
`a_b = 336958/10^12`. Increasing this by 10^-12 fails the same conservative
moment comparison.

The complex network remains the h28 PR #7 construction. Its PR #10 batching
saving is 7/10^7 and its whole-residual guard has `C1=11999/10000`.
Using `epsilon=499999915710/10^12`, `c=1`, `beta=1/1000`,
`delta=1/10^10`, `lambda=1-a_b+10^-16` and
`lambda'=1-a_b+2*10^-16` makes all 29 assembly constraints strict.
The minimum final margin is
`84239485748905098429/(5*10^26)`, above the selected κ by
`485748905098429/(5*10^26)`.

## Reproduction

From the repository root:

```sh
python3 scripts/dimension30_stream_network.py --workdir /tmp/dimension30-check
python3 -m unittest discover -s tests -p 'test_dimension30_stream_network.py' -v
python3 -m unittest discover -s tests -p 'test_ternary_dimension_sweep.py' -v
```

The first command needs Python 3, a C++17 compiler and several GB of memory.
It reconstructs the plan, checks the final DAG, frames and physical allocation,
and writes separate producer and assembly certificates. It needs no saved
discovery files. `--quick` checks the arithmetic without rebuilding the
producer. The h26 and h32 screens were weaker. Their selected circuits were
not promoted to full exact producer certificates.
