# X54 slot on the joint-entrance k8 word with exact T37 owner packing

Conditional **κ = 0.001675608585476885** (exact `335121717095377/200000000000000000`).
That is **+3.9910275352e-8**, or **0.0023819%**, above PR1169's `0.001675568675201533`.
The conservative endpoint is 0.001675608582632503.

## What changes

This package adds one ingredient to PR1169: the width-neutral eighth triangle-hybrid slot **X54/E589** from PR1130 (jeremykothe2), with holders 335 and 367.
PR1169 itself is PR1148's joint entrance choices (groups 603, 611, 635) with an exact T37 owner flow.

- **Recipe.** The edits and frames are identical to `RECIPE-X54-ends7.json`. The recipe is rebased onto PR1148's joint-entrance word (`k8-joint-entrances/FULL-WORD.json.gz`, content sha `1f666402…`).
- **Why the indices carry over.** The joint-entrance recipe changes only frames, so the gate indices are those of the eight-end word. None of the 39 changed B frames lies on an X54 position.
- **Local profile.** `{1:2364, 2:498, 3:412, 4:130, 5:82, 8:8}` becomes `{1:2364, 2:498, 3:414, 4:126, 5:84, 8:8}`. The target merges a (4,1) climb pair into one 5, and the holder splits a 4 into (3,1).
- **Helper widths.** The width inventory `{4:44, 5:44, 7:38, 8:114, 9:240}` is unchanged.
- **Owners and geometry.** PR1169's 159,840 whole-helper roles in 333 calls are reused unchanged: owner map, pattern flow, windows, parent geometry, and idle `{1:834, 48:11374}`. Only the provider identity is new; it is rebound to a fresh native replay of the new word.
- **Fixed-family ceiling.** The construction attains the all-T signed-dual grid ceiling for this fixed local word and inventory, again `0.001675608585476885`. That ceiling comes from `all_t_bound_x54.py`, PR1148's all-T bound with the X54 plan pinned.

Global profile: `{1:788046, 2:165834, 3:137862, 4:41958, 5:27972, 8:2664, 48:11374}`. Live stock is 33,152 and the deficit is 11,840.

## Validation (all passed)

- **Words and local audit:**
  - Rebuilt PR1148's joint-entrance word from its frozen recipe.
  - Built the X54 word (content sha `ac95ff95…`).
  - Independent exact local audit on all 704 columns in both orientations: `PASS_INDEPENDENT_EXACT_FORWARD_AND_DUAL_ENDPOINT_FRAMES_ENTRANCES_CONES`.
- **Local controls:**
  - PR1148's 27 entrance controls are rejected.
  - NewBArch's slot controls: C0 identity, the recipe, and four mutants (dropped restore, FULL restore, dropped pre-read, late donation), run globally and for X=54. All 10 outcomes are as pinned.
- **Native replay and rebind:**
  - Fresh native five-stage replay of the X54 word: native, ledgers, local replay, wrappers, phases.
  - The provider plan is rebound from that replay (15 identities) and must equal the shipped `PLAN-SOURCE-X54.json.gz`.
- **Owners and plan:**
  - PR1169's literal owner construction rebuilds the identical owner table.
  - The plan, profile and template are reconstructed with independently recomputed source-event windows.
- **Strict T37 admission** with the retained PR1129 engines:
  - bind, emit, audit, invoice and assembly;
  - 69 admission and 12 bit controls;
  - the independent owner checker with 7 controls;
  - all 47 outer inequalities.

  Result: `PASS_STRICT_T37_THREE_DEMOTIONS` at the stated κ.
- **Fixed-family all-T upper bound** equals κ.

```sh
python -B research/joint-x54-t37/verify.py --work /absolute/new/output-directory
```

Requirements:

- Python 3.11+, a C++ compiler and Boost headers.
- No network and no optimization solver.

`--native-from DIR` reuses a completed five-stage native replay; its word binding is checked. The run reuses PR1169's `upstream-layout.tar.gz`, `construct.py`, `PATTERN-FLOW.json`, `OWNERS.json.gz` and `GLOBAL-TEMPLATE.json.gz` from the sibling package. `SOURCE-PINS.json` pins them.

`evidence/` holds the receipts from a full run.

## Scope

This is a conditional finite construction. The following obligations remain:

- all-size compiler;
- common-label and mutable-source realization;
- whole-call hosting;
- precision/tape;
- exact recovery;
- analytic transfer;
- the PR559 recurrence correction;
- PR589 bit H1–H5.

No unconditional multiplication theorem, full formalization, global packing optimality or runtime improvement is claimed.

## Credit

- PR1130 (jeremykothe2): the X54 slot recipe.
- PR869: NewBArch triangle-hybrid builder and controls (vendored unchanged in `vendor/barch/`).
- PR1148 (Thomas DiFiore/Codex) and its full local ancestry: the joint-entrance word.
- PR1169: the T37 owner flow and packaging.
- PR1129 (Ali Romman/Codex): integer flow, matching and T37 audit.
- PR1131: wave order.
- PR942, PR795 and PR890: the dual all-T bound.
- PR589: the unchanged bit supplier.
- PR987 (Rohan Arun): the slot method lineage.

New composition by Rohan Arun with substantial AI assistance (Claude). Apache-2.0. Original notices are retained; see `NOTICE.md`.
