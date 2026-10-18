# Eight-slot k8 word (X54 added) with the T37 owner optimum

```text
kappa = 334827562021037 / 2*10^17 = 0.001674137810105185
```

This is **+3.98402e-8 over the current best open result**, #1129/#1131 (`0.001674097969905390`: the T37 owner optimum on
the seven-slot k8 word). It is also above every open local-word variant: #1130 (X54 and rank-seven ends with T16
owners) is at 0.001673006105142741. The complex side binds, and the PR589 bit supplier is unchanged.

## What changes

The change is a composition of two width-neutral pieces that have not yet been combined.

1. **Local word.** Jeremy Kothe's eighth triangle-hybrid slot **X54/E589** (#1130) is applied to the seven-slot k8
   word `c2b29430…` (#1018/#1074). #1130 applies it to the rank-seven-ends word; here it goes onto the seven-slot word
   directly.
   - `construction/x54/RECIPE-X54-k8.json` keeps #1130's `RECIPE-X54-ends7.json` byte for byte in its edits and frames:
     5 B deletes, 5 inserts, one FULL restore of holder 335 and one early restore of holder 367. Only the base and
     result pins and the profile change.
   - NewBArch's unchanged `build_tri.py` gives word content `512452c0…`.
   - Local profile: `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` → `{1:2412, 2:418, 3:434, 4:138, 5:84, 8:8}`.
   - Widths `{4:56, 5:32, 7:30, 8:122, 9:240}` (R=480) and the local prefixes (52/68 bits) are unchanged.
2. **Owners.** Ali Romman's exact T37 owner optimum for this capacity inventory (#1129; same map as #1131) is used
   unchanged: owners, order, pattern flow, 159,840 roles, idle `{1:5622, 48:11302}`.
   - Its all-replica bound is rerun with the eight-slot local profile and still attains the ceiling, so the bound and
     the construction agree at **0.001674137810105185**.
   - Global profile: `333 × local + {1:5622, 48:11302}` =
     `{1:808818, 2:139194, 3:144522, 4:45954, 5:27972, 8:2664, 48:11302}`.

## Verification

```sh
# from a checkout of this branch (no network, solver or third-party package)
python3 -B research/k8-x54-t37/check.py --work /tmp/k8-x54-check
# PASS_K8_X54_ALL_REPLICA_OPTIMUM_AND_ATTAINING_CONSTRUCTION 0.001674137810105185
```

`check.py` runs four steps:

1. The all-replica certificate (`verify.py`).
2. 18 certificate controls.
3. The literal owner reconstruction (`construct.py`).
4. The strict global replay (`replay.py`): bind, emit, controller audit with 15 mutations, the full finite invoice
   (prefix 775 < 1024, row 17,495 < 20,161), assembly with all 47 outer inequalities, 69 admission and 12 bit
   controls, and the independent owner check.

The native locals of the eight-slot word are committed in `inputs/local`. They are rebuilt from the seven-slot word by
`construction/x54/build_x54.py`, which runs, all pinned in `X54-PINS.json`:

- the unchanged builder;
- the 10 slot controls;
- the independent `audit_local`;
- PR635's native chain: native, ledgers, replay, wrappers and phases.

The seven-slot word itself is #1018's `research/gauge44-slots` step on #1005's leaver chain.

## Changes relative to `research/r480-owner-optimum`

The package is #1129's, copied with these changes:

- `inputs/local`: the eight-slot locals.
- `inputs/SPEC.json` and `inputs/PLAN.json`: the source local-profile contract.
- `vendor/pr1074/T8/PLAN.json`: its provider identities are rebound to the eight-slot locals (11 identities: semantic
  artifact ids, the LOCAL-CHECKS pin and both program hashes) plus the paid profile.
- `vendor/pr1074/data/SPEC-T8.json`: plan pin, expected profile and semantic ids, re-recorded by the unchanged bind
  code in discovery mode.
- `CERTIFICATE.json`: the root interval `[0.001676945247549584231285, …286]` and the κ grid.
- `controls.py`: the shifted-root and next-grid control values.
- `replay.py` and `check.py`: the new κ constant and the final marker.
- `data/PLAN.json` and `data/SPEC.json`: re-frozen by the package's own `replay.py --discover`.
- `SOURCES.json` and `SOURCE-FREEZE.json`: refreshed.
- New: `construction/x54/` and `evidence/`.

`OWNERS.json.gz`, `ORDER.json`, `PATTERN-FLOW.json`, `construct.py`, `lift.py`, `verify.py`, `independent_owner.py` and
`code/` are byte-identical to #1129. #1129's README is kept as `README-R480-OWNER-OPTIMUM.md`.

## Credits

- **Ali Romman** (#1129): the R480 owner theorem, the attaining T37 construction and this package's machinery.
  **Chafik Boukhalfa** (#1131) published the same optimum; his PR795 supplied the signed prices.
- **Jeremy Kothe**: the X54 slot recipe (#1130), the seven-slot k8 word (#1018/#1074) and the leaver chain (#1005).
- **NewBArch**: the triangle-hybrid move and the unchanged builder and controls.
- **Rohan Arun** (#987): the slot search used to find the k8 slots.
- **Hao Yan**: the T16 machinery.
- Every upstream contributor credited in the retained notices.

Composition prepared by Rohan Arun with Claude (Anthropic).
