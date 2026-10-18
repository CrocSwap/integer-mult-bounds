# Source-holder fusions and the X54 slot on PR1193's mixed T37 construction

Conditional **κ = 0.001675809683500501** (`1675809683500501/10^18`).

This package composes three published local-word changes with Jeremy Diviney's PR1193 mixed T37 construction. The owners are unchanged.

1. **PR1193** (jeremydiviney), `research/mixed-demotions-t37`. This is the base: 125 calls of PR1148's joint-entrance word (D3) and 208 calls of its four-group variant (D4). The variant adds entrance group 627. The package keeps PR1193's frozen integer flow, owners, call order and dispatch, all unchanged.
2. **PR1195** (mdumitrean). Two source-holder fusions replace the two-donation triangle-hybrid slots at X=439 and X=444. Their refitted frames are taken from PR1195's word.
3. **PR1130** (jeremykothe2). The eighth triangle-hybrid slot X54/E589, with holders 335 and 367, in the recipe that PR1178 (rohanarun) rebased.

Both edits are width-neutral. They change no entrance, end, port or centre interface. The helper inventories therefore stay `{4:44,5:44,7:38,8:114,9:240}` (D3) and `{4:40,5:48,7:38,8:114,9:240}` (D4). PR1193's owners stay valid, with idle `{1:2,48:11374}`. Only the local profiles change:

| provider | calls | PR1193 profile | this package |
| --- | ---: | --- | --- |
| D3 | 125 | `{1:2364,2:498,3:412,4:130,5:82,8:8}` | `{1:2358,2:504,3:410,4:130,5:82,8:8}` |
| D4 | 208 | `{1:2356,2:506,3:416,4:126,5:82,8:8}` | `{1:2350,2:512,3:414,4:126,5:82,8:8}` |

Each word has the profile change `{1:-6,2:+6,3:-2,4:0,5:0}`. This is the sum of the fusion change `{1:-6,2:+6,3:-4,4:+4,5:-2}` and the X54 change `{3:+2,4:-4,5:+2}`.

## Composition

The fusion edits (PR1195 versus PR1148's joint word) and the X54 edits (the PR1178 recipe applied to the joint word) touch disjoint ranges of A and B. PR1193's group-627 edits are also disjoint from both. Cleanup and early cleanup are merged semantically:

- The X54 prepended restore goes first in cleanup.
- The X54 tail gate goes last in cleanup.
- The early entry for the X54 tail gate stays first in the early list.

`discovery/compose.py` records this merge. The verifier does not run it. Both final words are frozen as literal sequence-diff recipes from PR1148's joint word: `data/RECIPE-THREE.json` and `data/RECIPE-FOUR.json`. Each recipe checks every removed base element and pins its output.

## Verification

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -B research/mixed-fusions-x54-t37/verify.py --work /new/dir
# PASS_MIXED_FUSIONS_X54_T37_COMPLETE_ADMISSION 0.001675809683500501
```

This is PR1193's verifier with two additions. It first builds both words from the frozen recipes, and it also runs `composition_controls.py`. The full set of checks is:

- **Native and local replay (both new words):**
  - independent exact `audit_local` (all 704 columns, both orientations);
  - fresh PR635 native chain, including every phase edge.
- **Local controls:**
  - PR1193's 11 entrance controls on the new D4 word;
  - **28 new composition controls:** each of the 14 B/cleanup gates inserted by the fusions and X54 is removed in turn from each word, and the exact local audit must reject every mutant.
- **Owners and audit:**
  - PR1193's unchanged owner reconstruction (frozen owners must match);
  - 8 flow controls;
  - independent owner audit;
  - parent check.
- **Strict admission:**
  - bind, emit and controller audit with 23 mutations;
  - full invoice: prefix 775 < 1024, row 17,495 < 20,161;
  - assembly with all 47 outer inequalities;
  - 114 admission and 12 bit-supplier controls.
- **Pricing and ancestry:**
  - two-engine price;
  - cold PR589/741/799 ancestry replay (reusable with `--ancestry799`).

`data/PLAN.json.gz` keeps PR1193's plan; only the provider identities and the profile are rebound. `data/SPEC.json` was re-frozen through the engines' discovery → freeze protocol. Against PR1193's SPEC, only the global profile, κ and the complex-root fields change. Receipts are in `evidence/`.

## Changes relative to PR1193's `research/mixed-demotions-t37`

- `build_word.py` builds both words from frozen recipes; it previously built D4 only, with D3 taken as the raw joint word.
- `verify.py` builds both words, runs the composition controls and uses a new final marker.
- New files:
  - `composition_controls.py`;
  - `data/RECIPE-THREE.json` and `data/RECIPE-FOUR.json`;
  - `data/THREE-WORD.json.gz`;
  - `discovery/compose.py`.
- Updated files:
  - `data/FOUR-WORD.json.gz` (the D4 word with fusions and X54);
  - `data/PLAN.json.gz` and `data/SPEC.json`;
  - `CLAIM.json`, `MANIFEST.json` and `evidence/`.
- Unchanged files:
  - `data/FLOW.json.gz`, `data/OWNERS.json.gz`, `data/MIX.json`, `data/ORDER.json` and `data/FOUR-RECIPE.json`;
  - `construct.py`, `audit.py`, `controller.py`, `prepare.py` and `price.py`;
  - vendored sources.

Scope: all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape and exact recovery, analytic transfer, PR559 recurrence correction and bit H1–H5 obligations remain. No unconditional theorem and no optimality claim for mixed words.
