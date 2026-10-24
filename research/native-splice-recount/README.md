# Independent recount of #4505: the installed borrowed adapters

**Claim type:** an independent logical recount by separately written code. **No new κ.** It covers
Dugongue's [#4505](https://github.com/CrocSwap/integer-mult-bounds/pull/4505). That PR installs #4502's
borrowed rank-one adapters into the complete THREE-base native word and reports a scalar-allowance saving of
100 per orientation.

## What is checked, in both orientations

The verifier reads the pinned original native word and #4505's `NATIVE.json`.

1. **Nothing paid moves.** Every non-scalar event (climb, center, warp, adapter, residual adapter, phase) is
   identical and in the same order. So the paid profile `{1:2487, 2:713, 3:232, 4:102, 5:28}`, the
   transports and the warps are unchanged by construction.
2. **The change is local and logically exact.** All differences lie inside **one** maximal scalar segment:
   the same segment (index 4,984) in both orientations, with 4,208 scalars before and 4,210 after. Replaying
   ADD, SCALE, CLEAR and COPY as exact rational linear maps, the old and new segments have the **identical
   effect on all 411 fields they touch**. Borrowed fields are therefore restored, and no field is left dirty.
3. **The tariff.** The scalar allowance is re-implemented from its stated rule:

   | Operation | Allowance |
   | --- | --- |
   | CLEAR, COPY | 2 |
   | dyadic unit SCALE | `2(|bitlen n − bitlen d| + [q<0])` |
   | ADD | `2(3 + bitlen n − 1 + popcount n + bitlen d − 1)` |

   It gives

   | Orientation | Original | Rewritten | Saving |
   | --- | ---: | ---: | ---: |
   | forward | 158,120 | 158,020 | 100 |
   | backward | 158,168 | 158,068 | 100 |

   This matches #4505.

## Not covered

- Physical frames, phases and the prefix envelope. #4505's own retained-interpreter replay covers those.
- Any cost model beyond the stated scalar tariff.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/native-splice-recount --check-only
python3.12 -B scripts/research_package.py --package research/native-splice-recount
```

The verifier prints `PASS_NATIVE_SPLICE_RECOUNT` in about a second, using only the standard library.

## Open next questions

1. **Can the same segment-level linear-map comparison audit #4510's suffix error weights?**
   - *First step:* propagate a unit defect through each scalar event with the same free-word replay, and
     compare with #4510's 1,328 δ forward and 4,879 δ backward totals.

## Credit

- The adapters and the installer are Dugongue's (#4502, #4505).
- The native word comes from the retained THREE-base lineage.

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
