# Cancelling cleanup sandwiches on #263's word

Under the interfaces retained by #263, this package certifies

    T(n) = O(n (log n)^(1 - κ)),   κ = 44484434094527/(6.25·10^16) = 7.117509455124319e-4

That is +0.101% over #263 (355516119100349/(5·10^17) = 7.11032238200698e-4). The package adds this directory and one
workflow; no existing file changes.

## What changes

**Idea.** Some helpers climb to the full frame only to take part in cleanup. When that part is redundant, here the F2
identity `t += a; a += b; t += a = a += b; t += b`, the climb can be removed: 45 helpers in #263's word stop at
dimension 4 instead of 24, saving two rank-21 climbs each and shrinking their banked endpoints from rank 23 to rank 3.

After #263's first kernel cut, 45 helpers appear in exactly three gates, all in the full-frame cleanup:

    t += a,   a += b,   t += a        (F2)

with t never a control between the first and the last. Over F2 these three gates equal `a += b; t += b`. This package
moves `a += b` to the first cut, where a and b already sit at frames whose sum is a nondegenerate four-dimensional
frame, and keeps `t += b` at the position of the middle gate. The helper then has no gate after the cut. It stops at
dimension 4 instead of climbing to the full frame, and its completed endpoint becomes a rank-3 partial swap instead
of a rank-23 one. Nothing else in the word moves. [PROOF.md](PROOF.md) gives the argument and its scope.

| | normalized stock | coarse bit saving | κ |
|---|---|---|---|
| #259 | 173,435 | 177883827203061/(2.5·10^17) | 142205877210807/(2·10^17) |
| #263 | 173,435 | 71153816501917/10^17 | 355516119100349/(5·10^17) |
| this package | 173,135 | 712257895988781/10^18 | **44484434094527/(6.25·10^16)** |

Per helper the child histogram loses two rank-21 climbs and gains two rank-1 steps and one rank-20 step, so the
rank mass falls by 20 per helper and 900 in all. The deficit (35,200) is unchanged; the bank stock falls by 1,500
literal units (300 per normalized vertex). The bit supplier still binds.

## Verify

    python3 -m pip install sympy==1.14.0
    git fetch https://github.com/CrocSwap/integer-mult-bounds 87129308f762f86a9d8e9a60f5d6c8ef23ce1f6e
    git archive 87129308f762f86a9d8e9a60f5d6c8ef23ce1f6e research/multicut-kernel-condensation | tar -x -C /tmp/base263
    python3 -B research/cleanup-sandwich-263/verify.py --base /tmp/base263/research/multicut-kernel-condensation \
        --boost-include /usr/include --output /tmp/cleanup-sandwich-263

About 7 minutes; 6 of them are #263's own replay. `verify.py` runs these checks:

1. The base package matches `SOURCE.json`: its manifest hash and every file the manifest lists.
2. #263's own `verify.py` regenerates the base word from its pinned sources and passes; the word hash is pinned.
3. Every frozen helper has exactly the sandwich after the cut. Each new frame is nondegenerate for 9I − J, each new
   connector is an exact rational inclusion, and the F2 replay of all 20,107 formal source, target and dirty
   columns is the identity. Omitting either new gate is rejected.
4. Each shortened endpoint is the rank-3 projector difference P_F − P_S, with an exact chart. The width-120 banks
   re-tile exactly.
5. Every new frame, connector and endpoint has an exact chart within #259's factor bound, with entries below 2^80.
6. #263's native checkers, compiled from its pinned sources and unchanged, check frame legality of the new word and
   its five-stage columns.
7. #263's price engine reproduces #263's price on #263's word, then prices the new word: 47 strict constraints
   positive and the adjacent grid point rejected.
8. #263's finite invoice passes on the new word and bank inventory.
9. All results equal `expected.json`.

## Files

- `sandwich263.py`: the rewrite, the new frames and the F2 formal replay.
- `endpoints263.py`: shortened endpoints, bank re-tiling and normalizer charts (exact, SymPy).
- `price263.cpp`: a main that calls #263's unchanged price engine on a histogram.
- `selection.json`: the 45 helpers. `SOURCE.json`: the pinned base. `expected.json`: the certified values.

## Limits

- This is a finite conditional construction. Every interface #263 retains (all-size compiler, common weighted
  chart, restored rows, routing, prime supply, precision and recovery, analytic reduction) stays an assumption.
- The 45 helpers were found by a frame-dimension screen of the cleanup suffix. Verification does not use the
  screen; it checks the frozen list.
- Not composed here: #267, #268, #269 and #270, which change other parts of the same lineage.

Credits are in [NOTICE](NOTICE).
