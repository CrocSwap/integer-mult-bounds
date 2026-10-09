# Recycled bit registers on #144's shared cores

Under the interfaces retained by the merged #144, this package certifies

    T(n) = O(n (log n)^(1 - κ)),   κ = 471809569/10^12 = 4.71809569e-4

That is +1.54% over #147 (4646633/10^10) and +2.36% over the merged #144 (4609169/10^10). It adds this directory
and one workflow; no existing file changes.

## What changes

Only the bit word changes, and #144 is bit-limited. Starting from #147's reduced word:

- The selected deferred reads keep their order but run as late as the word allows, instead of in one block.
- 3,338 auxiliary registers that are dead (never touched again) are handed to a later deferred slot whose entrance
  frame contains the dead register's frame. The recipient's inherited read cancels what the donor left. This is
  jamesyc's #124 birth-read operation, applied to the bit word.

Each hand-off removes one physical role, the donor's final step and the recipient's gauge child, and adds one
shorter step. [PROOF.md](PROOF.md) gives the argument and its scope.

| | roles R | W per vertex | coarse bit saving | κ |
|---|---|---|---|---|
| #144 (merged) | 28,866 | 32,408 | 4617656/10^10 | 4609169/10^10 |
| #147 | 27,317 | 30,859 | 4655227/10^10 | 4646633/10^10 |
| this package | 23,979 | 27,521 | 472689442/10^12 | **471809569/10^12** |

The deficit per vertex (2,024) is unchanged. The complex side (4856569/10^10) still has about 2.9% headroom.

The headline keeps the merged atom exponent 1/1000. At gupt1156's 1/2000 (#148) the same row gives
472026274/10^12 = 4.72026274e-4; `verify.py` checks both.

Not composed here: Th0rgal's exact min-cut gauge subset (#146). #144's own 9,543 selected gauges are used.

## Verify

    python3 research/bit-reuse-147/verify.py          # stdlib only, about 2 minutes; do not use -O
    python3 research/bit-reuse-147/verify.py --all    # also re-checks every inherited frame move, about 9 minutes

`verify.py` runs these checks:

1. It reproduces #144's coarse saving, stopped saving and κ exactly on #144's own grid.
2. With no elimination and no recycling, the delayed-read word reproduces every histogram of #144's row.
3. It runs the frame ledger of the frozen plan: every scalar gate at one common frame, no register retreating. The
   row rebuilt from the actual moves must equal `row.json`.
4. It checks all 4,878 new adjacent frame pairs for exact nesting over Q, with bases rebuilt by `check_lifted.py`.
   A control must reject mismatched hand-offs.
5. It runs the literal word on the 23,979 physical registers with all 27,521 inputs as formal variables, over F2
   and over Z, and requires the exact identity. This is complete, with no random vectors. A random replay then
   confirms that three tampered words break the identity.
6. It prices the row with #144's assembly (47 constraints, 7 margins); the next grid points are rejected.

## Files

- `word147.py`: timetable, literal events, scalar replay, frame ledger and row.
- `frames147.py`: exact integer frame bases and nesting over Q.
- `price147.py`: pricing with #144's `paired_cube_network.py` functions. As in #147, the one relaxed check is the
  bit dimension test, which accepts R <= 28866.
- `plan.json`: the eliminated slots (#147's plan, unchanged), the remaining gauge slots and the 3,338 pairs.
- `row.json`, `expected.json`: the resulting row and the certified values.
- `make_plan.py`: how the plan was found (needs numpy and scipy). Verification does not use it.

## Limits

- This is a finite conditional construction. Everything #144 retains stays an assumption, and the pinned PR97
  frame audits are relied on, not rerun.
- The replay runs one core on its own bank, as in #147.
- The plan is one legal choice from a matching heuristic. No optimality is claimed.
- The complete `make verify` and the formal targets were not run locally; the fork's CI runs them.

Credits are in [NOTICE](NOTICE).
