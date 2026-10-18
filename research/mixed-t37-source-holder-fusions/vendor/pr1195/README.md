# Two source-holder fusions on #1148's joint-entrance k8 word

The conditional finite witness is

$$
\kappa=\frac{837829001135967}{500000000000000000}=0.001675658002271934,
$$

**+9.705×10⁻⁸ (0.00579%) over #1148's joint-entrance witness 0.001675560947524449**, and above that word's fixed-family
all-replica ceiling 0.001675568675201533. It is an exponent saving, not a measured runtime.

**This package builds on the unmerged #1148** (Thomas DiFiore): it is branched from #1148's head `f1d8dc59` and uses its
joint-entrance word, owners, parent geometry and admission driver unchanged. The pull request therefore contains #1148's
commits until #1148 is merged; only `research/k8-source-holder-fusions/` is new. The branch base is #1148's head `e7d0d016`;
the files consumed here are byte-identical at its earlier head `f1d8dc59`.

## What changes

Two of the seven triangle-hybrid slots of the k8 word (#987/#1018, sites X=439 and X=444) use a two-donation form: the
packet register X is donated into a source holder (10, resp. 34) for one target, and the entering copy E (584, resp. 590)
into a second holder (74, resp. 98) for another target, restored by an early-cleanup tail. At each of these two sites this
package keeps only the source-holder donation (with its FULL-cleanup restore, as in the slot) and replaces the second
donation by the **full read-set exchange** of the copy pair (E, X) in BRoute's SW4 sense: the second target reads X
directly and its entrance pre-read of E is deleted. The other five slots, every entrance and end frame, the helper widths
and #1148's owners are unchanged. All A, B and tail frames are refitted exactly.

| | local paid profile | κ (T16, #1148 owners) |
|---|---|---|
| #1148 joint entrances | `{1:2364,2:498,3:412,4:130,5:82,8:8}` | 0.001675560947524449 |
| this package | `{1:2358,2:504,3:408,4:134,5:80,8:8}` | **0.001675658002271934** |

The local change is exactly twice `{1:−3, 2:+3, 3:−2, 4:+2, 5:−1}`, one per site. Rank mass and width are unchanged, so the
idle profile `{1:360, 24:1, 48:4918}` and all 69,120 whole-helper roles in 144 calls are reused. See [PROOF.md](PROOF.md).

## Verification

```sh
python -B research/k8-source-holder-fusions/verify.py --base "$BASE" --work /absolute/new/output-directory
```

`BASE` is the original R480 k8 + seven-slot word pinned in `research/k8-eight-ends/RECIPE.json` (as for #1148). The
verifier rebuilds #1148's parent geometry (or reuses a completed `k8-eight-ends-t16` replay with `--parent-from`), builds
the word from #1148's joint-entrance word with the standard-library `build_word.py` and its checked literal `RECIPE.json`,
runs #645's independent `audit_local.py`, ten fusion negative controls (`controls.py`), PR635's native local chain (or
reuses one with `--native-from`), checks the native semantic identities against `PLAN.json.gz`, and then runs #1148's
unchanged strict T16 admission (`research/k8-three-demotions/run_global.py`) with #1148's frozen owners. Expected final
line: `PASS_K8_SOURCE_HOLDER_FUSIONS_COMPLETE_ADMISSION 0.001675658002271934`. No optimizer runs; no C++ compiler or Boost
was needed on the author's machine (macOS, Python 3.14, NumPy/SymPy/SciPy as for the selected frontier).

Completed here (`evidence/`): fresh native exact forward and dual replay of all 704 columns and all native phase checks;
`audit_local` PASS; 10/10 fusion controls rejected (dropped restore, dropped or sign-flipped donation, kept fused read,
dropped donation and restore, at each site); 69 admission, 12 bit-supplier, 15 controller and six independent T16 controls;
both exact moment engines and all 47 strict outer inequalities. `PLAN.json.gz` is #1148's PLAN with only word-dependent
fields rebound (provider artifact hashes, semantic identities, program hashes, paid profile); `SPEC.json` was re-derived by
the package engines' discovery → freeze protocol before the strict run.

The same two-site change was also admitted strictly on earlier hosts: 0.001672756914849856 on #1094's T16 owners (selected
record), 0.001674194854569677 on #1129's T37 owners, and 0.001675218651386511 on #1148's three-demotion word. These are
recorded in [SEARCH.json](SEARCH.json) and are not separate claims.

## Search and limitations

The sites were found by an exhaustive exact sweep of read fusions with enlarged-reader repairs (2,405 fusions on the
pre-slot k8 word: exactly these two gains; 2,217 on the seven-slot word: none). The search tools are submitted separately
as `research/exact-frame-toolkit` (tooling PR, no new κ). They are not needed to verify this package. The change is width-neutral, so it also applies to #1169's T37 packing of the same joint-entrance word (idle
`{1:834,48:11374}`): priced exactly at **0.001675665730846312**, but not strictly replayed here and not claimed. Other words
(for example #1152's rank-seven-end word) were not rebuilt.

All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery,
analytic-transfer and bit H1–H5 assumptions remain. This is not an unconditional multiplication theorem or a Lean
certification. See [NOTICE.md](NOTICE.md) for credit.
