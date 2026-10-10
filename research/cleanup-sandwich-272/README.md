# Cancelling cleanup sandwiches on #272's word

Under the interfaces retained by #272, this package certifies

    T(n) = O(n (log n)^(1 - κ)),   κ = 713662156389609974540991/10^27 = 7.13662156389610e-4

That is +0.223% over #272 (712074434532274423885827/10^27 = 7.12074434532274e-4). The package adds this directory
and one workflow; no existing file changes.

## What changes

**Idea.** Some helpers climb to the full frame only to take part in cleanup. When that part is redundant, here the F2
identity `t += a; a += b; t += a = a += b; t += b`, the climb can be removed: 99 helpers in #272's word stop at
dimension 4 instead of 24, saving two rank-21 climbs each and shrinking their banked endpoints from rank 23 to rank 3.

After #272's first kernel cut, 99 helpers appear in exactly three gates, all in the full-frame cleanup:

    t += a,   a += b,   t += a        (F2)

with t never a control between the first and the last. Over F2 these three gates equal `a += b; t += b`. This package
moves `a += b` to the first cut, where a and b already sit at frames whose sum is a nondegenerate four-dimensional
frame, and keeps `t += b` at the position of the middle gate. Nothing else in the word moves. [PROOF.md](PROOF.md)
gives the argument and its scope.

| | normalized stock | coarse bit saving | κ |
|---|---|---|---|
| #272 | 519,887 | 712581842140497/10^18 | 712074434532274423885827/10^27 |
| this package | 517,907 | 714171830081841/10^18 | **713662156389609974540991/10^27** |

Per helper the child histogram loses two rank-21 climbs and gains two rank-1 steps and one rank-20 step, so the
rank mass falls by 20 per helper. Over #272's 120 replicas the banks re-tile with 1,980 fewer banks per stage. The
deficit is unchanged and the bit supplier still binds.

## Verify

    python3 -m pip install sympy==1.14.0
    git fetch https://github.com/CrocSwap/integer-mult-bounds 4d23d0ee5682c99b792614bae4bc5330da19ff13
    git archive 4d23d0ee5682c99b792614bae4bc5330da19ff13 research/filtered-kernel-target120 | tar -x -C /tmp/base272
    python3 -B research/cleanup-sandwich-272/verify.py --base /tmp/base272/research/filtered-kernel-target120 \
        --boost-include /usr/include --output /tmp/cleanup-sandwich-272

About 8 minutes; 7 of them are #272's own replay. `verify.py` runs these checks:

1. The base package matches `SOURCE.json`: its manifest hash and every file the manifest lists.
2. #272's own `verify.py` regenerates the base word from its pinned sources and passes; word hash and κ are pinned.
3. Every frozen helper has exactly the sandwich after the cut. Each new frame is nondegenerate for 9I − J, each new
   connector is an exact rational inclusion, and the F2 replay of all 20,107 formal source, target and dirty
   columns is the identity. Omitting either new gate is rejected.
4. #272's native checkers, compiled from its pinned sources and unchanged, check the new word: frame legality,
   multi-cut prefix kernels, bank charts and role census, and five-stage columns.
5. Each shortened endpoint is the rank-3 projector difference P_F − P_S, with an exact chart, and the bank review
   is re-tiled exactly for the shortened residuals.
6. Every new frame, connector and endpoint has an exact chart within the chart-factor bound, entries below 2^80.
7. #272's price engine reproduces its baseline and prices the new word (47 strict constraints, adjacent grid point
   rejected); #272's finite invoice and fixed-prime refinement pass.
8. All results equal `expected.json`.

## Files

- `sandwich272.py`: the rewrite, the new frames and the F2 formal replay.
- `endpoints272.py`: shortened endpoints, bank re-tiling and normalizer charts (exact, SymPy).
- `selection.json`: the 99 helpers. `SOURCE.json`: the pinned base. `expected.json`: the certified values.

## Limits

- This is a finite conditional construction. Every interface #272 retains (all-size compiler, common weighted
  chart, restored rows, routing, prime supply, precision and recovery, analytic reduction) stays an assumption.
- #272's bank review charges every role as if its chain ended at full; the re-tiling for the 99 shorter chains is
  done and checked here, not by that tool.
- The 99 helpers were found by a frame-dimension screen of the cleanup suffix. Verification does not use the
  screen; it checks the frozen list. No claim is made that 99 is the largest such set.

Credits are in [NOTICE](NOTICE).
