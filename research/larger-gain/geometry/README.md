# Structural geometry headroom after PR564

The pinned PR564 construction has `kappa = 0.001593134158181640`, with
`v=112`, `h=9`, `m=73`, 72 complete calls, 504 helpers, live stock 7168 and
rank deficit 2560. The scalar factory and every helper remain charged in
the calculations below. The geometry and LP screens are research bounds,
not supplier admissions.

The subsequent frozen width-seven candidate has a separate conditional
physical admission at `kappa = 0.001600067494703216`. Its independent
[literal geometry and adapter review](WIDTH7-REVIEW.md) passed without
correctness findings. The following ceilings explain which larger changes
still have arithmetic room beyond that concrete construction.

The most useful result is that a substantial improvement must alter the
local word or its geometric decomposition. PR564's width alphabet and
pending capacities already attain their certified capacity ceiling; merely
repacking those words cannot move the next kappa grid point. See the
[independent model review](CAPACITY-MODEL-REVIEW.md). The earlier
[free-concentration ceiling](PACKING-CEILING.json), allowing arbitrary idle
mass rearrangement, left 1.4132% headroom, but the stronger pattern bound
accounts for the unavoidable remainders of indivisible helpers.

## Exact screens of puncturing and ambient compression

[geometry_screen.py](geometry_screen.py) reproduces
[GEOMETRY-SCREEN.json](GEOMETRY-SCREEN.json) using only the standard library.
It reads the inherited Hamming prototype used by the actual local factory.
All ranks, incidences and orthogonality checks are exact.

* The 112 binary ports and their binary Gram matrix have rank nine. An
  isometric relabeling into dimension eight cannot preserve this geometry.
* All 511 binary hyperplane restrictions were checked. They retain at most
  64 ports. Even the best inherited coordinate-total architecture has
  `8v - 9C = 8`, compared with 320 before restriction. This is a deficit
  screen, not a cost estimate that omits the remaining helpers.
* Reducing any one existing coordinate center's support rank from eight
  requires deleting at least 24 ports. Exactly eight binary hyperplanes
  support any nonzero linear combination of the coordinate totals; each
  allows just one independent coordinate total. No dimension-seven subspace
  supports a nonzero such total. A simple change of the eight-center basis
  therefore cannot lower the current center rank sum 64.

The bit PR555 construction uses nine pseudo-targets at rank-seven
hyperplanes. Copying that count directly into this complex height-nine
geometry gives nine rank-eight centers, cost 72 rather than the current 64.
Its bit gain does not transfer by reusing the headline port count.

A stronger lower-rank-decoder obstruction comes from the root geometry.
There are exactly 1260 orthogonal eight-frames among the 112 live root lines,
and each port belongs to exactly 90 frames. For a rank-`j` decoder fitting
the inherited zero pattern, each surviving frame gives a diagonal principal
submatrix, so it contains at most `j` live ports. Summing this statement over
all frames gives `90v <= 1260j`, or `v <= 14j`.

Consequently, a rank-seven decoder needs at least 14 deleted ports. With
seven rank-eight centers, even the best possible `v=98` has
`C/v = 56/98 = 64/112`, the same center cost per port as the baseline. The
tempting scenario of deleting eight or nine ports and dropping to seven
centers is impossible under this zero pattern. This does not rule out new
lower-rank frames, nonmonotone charged schedules, or a different zero pattern.

## Reverse puncturing: retain 120 ports but only 64 center ranks

The full 120-port geometry was checked separately. For every nonzero
coordinate linear total, its source support spans all nine binary
dimensions. Equivalently, for each of the 511 proper hyperplanes, the real
root rows outside it have rank eight, certified by exact modular minors.
Every coordinate total therefore needs a rank-nine frame in a monotone
common-frame program. The eight such totals cost 72 center ranks.

For example, full `T_i` contains its coordinate source and the 56 other
sources spanning that coordinate port's perpendicular hyperplane. Their
joint span has rank nine. Using the coordinate **source register** as a
mutable center carrier changes its storage, not this support requirement.
By induction, at every monotone common-frame gate the clean source support
of a register is contained in its frame. Cancellations and reversible changes
of register version do not invalidate that invariant.

Nor can a rank-one target gauge remove the final unit of descent: the center
serves the coordinate target and those 56 non-coordinate targets. Their
common perpendicular intersection is zero. A nested center-scatter chain
still descends through all nine dimensions. Keeping the old 112-port totals
and treating the eight added coordinate diagonals separately instead pays
`64 + 8 = 72`, as in the earlier construction.

Thus **carrier reuse alone does not realize `v=120, C=64`**. This screen
leaves two substantive possibilities open: a different center-response
factorization outside the coordinate-total row space, or a nonmonotone
schedule whose extra recursive transitions are explicitly charged. Either
must produce the complete scalar endpoint on arbitrary source, target and
helper columns, with exact phase and frame recipes. Merely renaming a helper
as a source does not suffice.

## A measurable target for a new word

A smaller seven-stage controller is useful only after a substantial helper
reduction. In the analogous `K=3`, `h=9` geometry its dimension is 57 and
its available idle residual capacity per invocation is
`2*(K-1)*v*(h-1) = 3584` axes. PR564's average residual width is
`4536 - 381 - 448/72 = 4148.777...`, exceeding that capacity by
`564.777...` axes per invocation. An optimistic volume-only placement
therefore already requires additional banks; reducing the dimension while
keeping the old helpers is not a free improvement.

At the same average entrance rank, a factory with at most 441 helpers would
cross the aggregate no-bank threshold. A 448-helper factory would still
need about 61 more entrance axes per invocation. These are concrete design
targets for a new factorization, not claims that such a word exists. The
current source explicitly has 504 helpers, including the eight ordinary
two-consumer packet copies per Hamming block; its alternative output basis
does not secretly reduce that count to 448.

A later [measured helper sensitivity screen](HELPER-TARGETS.md) gives more
attainable targets when banks are allowed: saving six expensive helper paths
per invocation would suffice for a 1% gain in the dimension-73 relaxed model;
17 would suffice in dimension 57. These are hypothetical endpoint-preserving
savings with no replacement cost, not a claim that current helpers can be
removed. The exact adjacent target checks are source-bound to the original
three four-cold providers.

## Exact stage-count relaxation with optional banks

The later [stage_relaxation.py](stage_relaxation.py) screen includes the three
additional checked cold relations in **all** zero-, four- and eight-pivot
provider inventories. Relative to PR564 each invocation pays
`3*e1 + 6*e2 - 6*e3`, with three width-nine helpers replaced by width-eight
helpers. It permits arbitrary fractional mixtures, drops all owner windows
and same-call conflicts, and allows any number of mixed-width auxiliary
banks. Every local paid child and every bank padding child is charged.

Both independent rational engines verified exact dual upper bounds:

| Stages | Ambient dimension | Optimistic banks | Best relaxed provider mix | Nominal kappa upper bound |
| --- | ---: | ---: | --- | ---: |
| 5 | 41 | 2560 | 40 zero-pivot four-cold | < 0.001383783631879096 |
| 7 | 57 | 2240/3 | 56 zero-pivot four-cold | < 0.001563195324390482 |
| 11 | 89 | 0 | 88 eight-pivot four-cold | < 0.001549720481841910 |

All three are below PR564's admitted `0.001593134158181640`. Thus a better
asynchronous schedule cannot rescue these stage counts **within the screened
provider and padding model**. This conclusion does not come from failure
of a synchronous placement heuristic: every legal asynchronous placement
in the model maps into the larger fractional program.

The source-bound certificates are
[five stages](FIVE-STAGE-BANK-CEILING.json),
[seven stages](SEVEN-STAGE-BANK-CEILING.json), and
[eleven stages](ELEVEN-STAGE-BANK-CEILING.json). Each contains a feasible
exact primal, its actual paid histogram and bank count, adjacent `10^-24`
moment endpoints, and a rational dual checked against every column by both
engines. There are respectively 275, 847 and 4742 columns. Verification
requires only standard-library Python; SciPy was used only to nominate bases.

The provider alphabet was then expanded to include both the measured
`all32width7` and `combined72` constructions. The latter combines 32 width-seven
promotions with 40 additional width-four promotions. The script derives
the complete width alphabet `4,5,7,8,9` from all five source inventories;
the older duals are not reused for these new columns.

| Stages | Dimension | Optimistic banks | Best relaxed provider mix | Expanded kappa upper bound |
| --- | ---: | ---: | --- | ---: |
| 5 | 41 | 2400 | 40 all32width7 | < 0.001395405041134436 |
| 7 | 57 | `1792/3` | 56 all32width7 | < 0.001577284319911712 |
| 9 | 73 | 0 | `1776/25` all32width7 + `24/25` combined72 | < 0.001600616266460206 |
| 11 | 89 | 0 | `1648/25` all32width7 + `552/25` combined72 | < 0.001554604133543484 |

The expanded exact ceilings are retained for
[five stages](WIDTH7-5-STAGE-BANK-CEILING.json),
[seven stages](WIDTH7-7-STAGE-BANK-CEILING.json),
[nine stages](WIDTH7-9-STAGE-BANK-CEILING.json), and
[eleven stages](WIDTH7-11-STAGE-BANK-CEILING.json). They respectively check
550, 2023, 5933 and 14837 columns. Optional banks do not improve the
nine-stage relaxation. Five, seven and eleven stages remain below PR564,
even with the new words and completely unrestricted asynchronous placement
in the model. The nine-stage value is an optimistic capacity ceiling,
not a physical admission or an outer-assembly kappa.

[STAGE-CEILING-VERIFICATION.json](STAGE-CEILING-VERIFICATION.json) records a
separate standard-library replay of the source-bound certificates, including
an intentionally increased provider dual potential that was rejected. To
nominate an expanded receipt, append both source constructions:

```sh
/tmp/larger-gain-opt-venv/bin/python research/larger-gain/geometry/stage_relaxation.py \
  --pairs 3 \
  --provider research/larger-gain/providers/promotions/all32width7/CONSTRUCTION.json \
  --provider research/larger-gain/providers/promotions/combined72/CONSTRUCTION.json \
  --out /tmp/width7-seven-stage.json
```

For `K` pair stages, the model uses `L=2K+1`, `m=16K+9`, `T=8`, `v=112`,
and `W0=2KvT`. There are `2(K-1)vT` pending bins of capacity eight and `4vT`
bins of each capacity `16j`, `1<=j<K`. Bank count `B` is variable, with
`W=W0+B`. Every provider's paid mass minus helper residual mass is 1856,
so the complete invariant is

```text
m*W - paid_mass = T*(2K*v - L*64).
```

The bank-dependent live stock therefore disappears correctly from the
rank-excess objective: its padding is counted, and rejection occurs when
`b * sum[r*((m/r)^b-1)/b]` exceeds the fixed deficit. Bank stock is neither
free nor hidden in a baseline denominator. Remainders larger than
`floor(m/sqrt(2))` are split into the most favorable allowed pieces. This
last restriction retains the requested two-level halving condition; a
different padding-depth contract lies outside these particular bounds.

For example, verify the seven-stage bound with

```sh
python3 research/larger-gain/geometry/stage_relaxation.py \
  --verify research/larger-gain/geometry/SEVEN-STAGE-BANK-CEILING.json
```

Any successful candidate must then pass actual chronology and whole-owner
placement, including active data exclusion, normalized residual/spectator
charts, all helper compensation and cleanup, both orientations and exact
phases, a complete finite invoice and both rational recurrences. The current
geometry screens do not replace those admission requirements.

Primary repository sources used here are
[the local construction](../../direct-delivery504-global/proof/LOCAL-CONSTRUCTION.md),
[the punctured 112-port construction](../../punctured112-global/README.md),
[PR564's actual-word proof](../../complex-allcold/proof/CONSTRUCTION.md), and
the fetched immutable PR555 head's `research/e8-bit-p111/README.md`.
