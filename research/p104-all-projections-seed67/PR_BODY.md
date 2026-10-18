## Status

**Mathematical audit / scoped finite proof extension; no new κ.** Independent all-survivor width classification in the P104 fixed cube-support family. Depends on the currently open PR #1125's support-uniformity claim and term-preserving terminal-read theorem for its delivery-cost interpretation; it does not change the selected frontier.

## New finite result

- Classifies all **255 nonempty survivor masks** using 21 exact cube-automorphism orbits and antichain/chain-cover dual certificates.
- Erasing two opposite cube vertices leaves width **20**; the other 24 pairs leave width **18**. With 3, 4, 5, 6 or 7 erasures the widths are respectively **10, 6, 3, 2, 1**, independent of the deletion geometry.
- The inherited inequality `L >= q + 2 max(0, width(F_K)-P_K)` now has exact finite width inputs for every `q` from 0 through 7. For exactly two erasures and `P <= 18`, this implies `L >= 6`, or `L >= 10` for opposite erased vertices, under #1125's explicit interface.

## Reproduce

```sh
python3 -I -B research/p104-all-projections-seed67/verify.py
```

Expected `PASS_P104_ALL_PROJECTIONS orbits=21 subsets=255 negative_controls=10 no_new_kappa`.

Optionally, with SciPy installed:

```sh
python3 -I -B research/p104-all-projections-seed67/independent_scipy.py
```

Expected `PASS_SCIPY_INDEPENDENT_MATCHING subsets=255 antipodal_pairs=4 no_new_kappa`.

The default acceptance is standard-library only, checks every literal antichain, chain partition and cube symmetry, and deliberately rejects 10 corrupted certificates. The optional SciPy implementation uses a disjoint matching backend. The 104-mask data is pinned to source PR1125 at head `9f7c0679d64bab954b7161d8586dc626a59b92ee`, certificate blob `9a2cd574df48361579167e39aa6198f39059f70c`, and also reconstructed independently from induced cube trees.

## Scope and credit

Base `ba82555c64e1879e4b7decce28186f208fcb8262`, refreshed main `ce7ad1b6ab09452c3478723a2e96ed5ff212dc08` at check. No changes to `upstream/` or selected frontier; no full theorem or runnable supplier claimed. The PR should be reviewed after or alongside PR #1125; if #1125 changes, reconfirm pins and assumptions.

Prepared for `@Chrisbryan17` with substantial GPT-6 assistance. Source decoder, theorem and initial widths: Ali Romman (#1125). Additional context: #1071 and #968. Licensed under Apache-2.0.
