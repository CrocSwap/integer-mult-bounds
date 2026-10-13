# Terminal elimination on #144's bit word

Under #144's retained interfaces this package certifies

    T(n) = O(n (log n)^(1 - kappa)),   kappa = 4646633/10^10 = 4.646633e-4

That is +0.813% over #144 (4609169/10^10). #144 is bit-limited, so this bit-side change moves kappa directly.

Only the bit word changes. #144's bit branch shares Swapnil Jain's round-seven PR97 word in dimension-69 completed
cores, with 9,543 selected entrance gauges and 2,022 dirty reads moved to the zero frame. Here, 1,549 terminal output
slots of that word are eliminated (PR122's operation, applied to the bit word). Each eliminated slot is a deferred
output accumulator that never sources an update. Its read, output read, inverse writes and V^-1 are deleted, and each
of its forward writes is applied to its target at the same time and frame. The 4,725 candidates are all selected
gauge slots. Eliminating one removes its gauge and its read. The remaining target chains are subsequences of #144's
certified chains, and every new target-chain adjacency is re-certified exactly.

| | roles R | W per vertex | coarse bit saving | stopped bit saving | kappa |
|---|---|---|---|---|---|
| #144 | 28,866 | 32,408 | 4617656/10^10 | 4613422943/10^13 | 4609169/10^10 |
| + 1,549 eliminations | 27,317 | 30,859 | 4655227/10^10 | 1162739093/(2.5*10^12) | **4646633/10^10** |

The deficit per vertex (2,024) is unchanged. The complex side (4856569/10^10) still has 4.5% headroom.

## Verify

From the repository root (Python 3.10+ standard library, about 5 minutes; do not use `-O`):

    python3 research/bit-elim-144/verify.py

The script runs these checks:

1. It reproduces #144's coarse saving, stopped saving and kappa exactly, using `scripts/paired_cube_network.py`'s own
   functions.
2. It rebuilds the exact frames from the pinned PR97 witness with Swapnil Jain's `check_lifted.py`.
3. It regenerates `plan.json`. A subset is accepted only if every merged target chain is nested exactly over Q.
4. It regenerates the reduced row `row-elim.json`.
5. It replays the reduced word literally over Z and over F2, with arbitrary scratch and data. Two tamper controls
   must be rejected: a missing redirected update and a sign-flipped one.
6. It prices the reduced row with #144's own assembly: 47 constraints and 7 margins, with the next grid points
   rejected.

`price144.py` changes exactly one check in #144's code. The bit dimension check now accepts R < 28866; every other
check of `shared_profile()` is kept. Both savings are reported as the largest points of #144's 10^-10 grids.

[PROOF.md](PROOF.md) gives the argument and the scope.

## Credits

- icekylinx: #144 and #130 (paired-cube and three-stage cover framework, selected gauges, pricing and assembly), and
  #104.
- Swapnil Jain: the round-seven deferred bit word and its exact frame tools.
- Zhihao Chen: the PR97 ledger.
- an664 / Andrey Mas: #128 completed-core sharing.
- SovereignSteak: #122 terminal accumulator elimination.
- jamesyc: #124 birth-read reuse.

Applying elimination to this bit word, and its re-certification, were prepared by William Porter with Anthropic
Claude assistance.
