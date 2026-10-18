# P104 all-survivor projection width audit (seed 67)

**Research audit, finite proof certificates, no new κ.** Extends [Ali Romman's PR #1125](https://github.com/CrocSwap/integer-mult-bounds/pull/1125) from zero/one erasures to the full nonempty survivor family in the P104 cube-support model.

## Reproduce

Requires Python 3.10+ and only its standard library, from any working directory:

```sh
python3 -I -B research/p104-all-projections-seed67/verify.py
```

Expected terminal header:

```text
PASS_P104_ALL_PROJECTIONS orbits=21 subsets=255 negative_controls=10 no_new_kappa
```

Regenerate (developer-only) and compare the file exactly with the committed certificate:

```sh
python3 -I -B research/p104-all-projections-seed67/generate.py
python3 -I -B research/p104-all-projections-seed67/verify.py
```

`generate.py` derives the 104 supports from cube connectivity, solves the exact 255 finite posets, and writes 21 orbit-compressed antichain/chain-cover witnesses. `verify.py` does **not** import the generator and checks each witness and orbit action directly. An optional, separately implemented SciPy sparse-matching oracle is available as `python3 -I -B research/p104-all-projections-seed67/independent_scipy.py` (requires SciPy and NumPy); it repeats all 255 width calculations independently. The pin for the 104 source masks is independently committed in the checker as SHA-256 of compact JSON.

## Result

| Erasures | Width(s) | Multiplicity |
|---|---|---|
| 0 | 32 | 1 |
| 1 | 26 | 8 |
| 2 | 18 or 20 | 24 or 4, respectively |
| 3 | 10 | 56 |
| 4 | 6 | 70 |
| 5 | 3 | 56 |
| 6 | 2 | 28 |
| 7 | 1 | 8 |

For two erasures, the stronger width 20 holds precisely when the deleted vertices are opposite on the cube. See `PROOF.md` for the proof, conditional delivery-rank corollaries and remaining assumptions.

**Scope:** no selected frontier edits; `upstream/` unchanged; no κ claim or all-size theorem; PR #1125 is an open predecessor as of this handoff. This package is an independent finite extension, but it depends on #1125's terminal-read premise to draw scheduling conclusions.

**Attribution:** Prepared for GitHub user `@Chrisbryan17` with substantial OpenAI GPT-6 assistance (analysis, implementation, verification and documentation). Original P104 support uniformity, theorem and initial width certificates: Ali Romman, PR #1125. Prior fixed-delivery findings and underlying frames: PR #1071 and PR #968 and their predecessors. Apache-2.0 repository license applies; retain all predecessor credits.
