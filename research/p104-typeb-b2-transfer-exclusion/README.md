# Exclude the fixed four-clock Type B B2 transfer

**NO VERIFIED GAIN.** On the exact signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) caller, removing B2 from IDLE_ONEs 1855 and 1869 and adding it to IDLE_ONEs 2324 and 2337 changes the Type B boundary map. The test fixes the four owners, all ordinary factors, every other mask and all clocks. The exact window is `[1855,2338)`.

At Type B port 15, use width one, central eigenvalue +1 and minus Walsh labels on axes 17 and 18. This realizes B2 = −1 with all other bodies +1. On the unit boundary input at role 36, the old and edited output at role 36 are respectively `−17/36` and `−13/36`. Five output rows differ on this input. All 36 boundary columns were tested. The unchanged surrounding maps are invertible on this specialization, so the difference also excludes this literal full-caller edit. The single planned case exhausted with zero unresolved within scope.

## Price and source pins

The exact comparator is [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481) at `89eaa9d8cae37c1540de98f2d29a3abaabb96a2b`, conditional κ `0.003647081039689`, with signed [#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) at `07a76c5e2738882c0cb322278e56f6cae3c9885d`. Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`.

The old ranks `56,56,64,64` become `48,48,72,72`. Over eight Type B ports, the signed paid delta is `{48:+16,56:−16,64:−16,72:+16}`. The productive delta is zero. Before support and ancillary charges, the directed gross is in `[0.12311985005206546, 0.12311985005206547]` raw units. The counterexample stops this edit before a construction or complete price comparison. No paid saving was realized.

## Replay

From a clean POSIX checkout, use CPython 3.12 and its standard library. The bundled inputs are authenticated by package-relative path. The direct and registered replays run offline.

```sh
python3.12 -I -B research/p104-typeb-b2-transfer-exclusion/replay.py
python3.12 -B scripts/research_package.py --package research/p104-typeb-b2-transfer-exclusion
```

The forward Fraction replay and independent reverse covector replay recover the same witness. The unit-body control gives equal full matrices. Omitting only the old reflection at 1855 changes the witness output from `−17/36` to `+17/36`. After normalization by the ordinary map, both reflection products have trace 32, so trace alone would miss this difference. Both exact engines completed under their 30-second caps.

## Open next questions

The result excludes only the named four-clock relocation under unchanged ordinary factors. Changed wrappers, coframes, alternate layouts and other clocks remain open. The negative specialization stopped positive all-body, physical construction and full application checks.

A distinct next test would try to concentrate the common B9–B15 factors of the existing even idles at 2324 and 2355. Check the exact conjugated reflection projectors through their literal interval before pricing or building a square replacement.

[#7113](https://github.com/CrocSwap/integer-mult-bounds/pull/7113) supplies the signed caller. [#7481](https://github.com/CrocSwap/integer-mult-bounds/pull/7481), [#7480](https://github.com/CrocSwap/integer-mult-bounds/pull/7480) and [#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) supply the comparison lineage. [#7402](https://github.com/CrocSwap/integer-mult-bounds/pull/7402) supplies a fixed-slot body-transfer precedent, [#7315](https://github.com/CrocSwap/integer-mult-bounds/pull/7315) and [#7360](https://github.com/CrocSwap/integer-mult-bounds/pull/7360) the projector precedents, and [#7298](https://github.com/CrocSwap/integer-mult-bounds/pull/7298) the directed tariff. OpenAI Codex and subagents materially assisted implementation and independent verification.
