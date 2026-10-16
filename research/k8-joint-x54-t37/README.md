# X54 slot on the joint-entrance k8 word, with exact T37 owners

```text
kappa = 335121717095377 / 2*10^17 = 0.001675608585476885
```

This is a conditional finite construction. It composes three published pieces:

1. Thomas DiFiore's joint-entrance k8 word (#1148, `research/k8-joint-entrances`, head `3ba07f19`).
2. Jeremy Kothe's eighth triangle-hybrid slot X54/E589 (#1130). Rohan Arun's #1178 rebased it onto
   #1148's earlier three-demotion word; here it is rebased onto the joint-entrance word.
3. A literal whole-helper T37 owner map at the exact all-replica bin optimum. The machinery is Ali Romman's
   #1129 (`research/r480-owner-optimum`), with Chafik Boukhalfa's #795 signed prices (also #1131/#1152) and
   the #890/#942 all-replica argument. The integer pattern flow is new; #1129's flow does not fit this
   width inventory.

Comparison at submission: #1148 (T16) `0.001675560947524449`, #1169 (T37 on the same joint word,
without X54) `0.001675568675201533`, and #1183 `0.001675603180601302`. This package is
`+3.9910275e-8` above #1169 and `+5.4049e-9` above #1183.

## What changes

- **Local word.** `construction/word/RECIPE-X54-joint.json` copies #1178's `RECIPE-X54-dem.json` exactly in
  its edits and frames: 5 B deletes, 5 inserts, the FULL restore of holder 335 and the early restore of holder 367. Only the
  base pin (joint word `1f666402…`), the result pin (`ac95ff95…`) and the report profile change.
  - NewBArch's unchanged `build_tri.py` builds the word.
  - Its unchanged `run_controls.py` accepts the recipe and rejects all eight mutants: `drop_restore`, `restore_full`,
    `drop_preread` and `donation_after`, each globally and at slot 54.
  - The independent `audit_local` passes.
  - PR635's native chain passes: native, ledgers, local replay, wrappers and all 2,904 phase edges.
  - Local profile `{1:2364, 2:498, 3:412, 4:130, 5:82, 8:8}` → `{1:2364, 2:498, 3:414, 4:126, 5:84, 8:8}`.
  - The slot is width-neutral. Widths stay `{4:44, 5:44, 7:38, 8:114, 9:240}`.
- **Owners.** The width inventory is #1148's, which differs from #1129's (`{4:56, 5:32, 7:30, 8:122, 9:240}`).
  A new integer pattern flow on #1129's T37 call order and source-event groups uses 15 of the 20 tight
  patterns (see `CERTIFICATE.json`).
  - `construct.py` (byte-identical to #1129's) expands the flow by bipartite matching into 159,840 literal roles in
    333 calls.
  - The idle profile is `{1:834, 48:11374}`. This is the all-replica optimum that #1148's own `ALL-T-BOUND.json`
    states for this inventory: credit 20,850 per replica, so `I1/T = 834/37`.
- **Complete profile:** `333 × local + idle` =
  `{1:788046, 2:165834, 3:137862, 4:41958, 5:27972, 8:2664, 48:11374}`. Live stock is 33,152 and the deficit is 11,840.
- **Root:** `0.001678420962050942454559 < b < 0.001678420962050942454560`. The PR589 bit supplier is unchanged and
  the complex side binds.

## Verification

```sh
python3 -B research/k8-joint-x54-t37/check.py --work /new/dir
# PASS_K8_JOINT_X54_T37_ALL_REPLICA_OPTIMUM_AND_ATTAINING_CONSTRUCTION 0.001675608585476885
```

`check.py` runs four steps:

1. The all-replica certificate, `verify.py`: 1,163 bin patterns, two exact moment engines and all 47 outer inequalities.
2. 18 certificate controls.
3. Literal owner reconstruction, `construct.py`.
4. The strict global replay, `replay.py`:
   - bind and lift;
   - emit;
   - controller audit with 15 mutations;
   - full finite invoice (prefix 775 < 1024, row 17,495 < 20,161);
   - assembly;
   - 69 admission and 12 bit-supplier controls;
   - the independent owner and pending-axis audit.

The native locals in `inputs/local` are rebuilt from the repository by:

```sh
CPLUS_INCLUDE_PATH=/path/to/boost python3 -B research/k8-joint-x54-t37/construction/word/build_local.py --out /new/dir
```

This runs #1148's `build_word.py`, then the X54 build and controls, `audit_local`, and the native chain. It checks every
pinned identity in `WORD-PINS.json`. Receipts are in `evidence/`.

## Changes relative to `research/r480-owner-optimum` (#1129) / `research/k8-x54-t37` (#1157)

- `inputs/local`: the X54-on-joint-entrance locals.
- `inputs/SPEC.json` / `inputs/PLAN.json`: the source width and profile contract for this word.
- `vendor/pr1074/T8/PLAN.json`: provider identities, widths and paid profile rebound to these locals.
- `vendor/pr1074/data/SPEC-T8.json`: re-recorded by the unchanged bind code in discovery mode.
- `PATTERN-FLOW.json`, `OWNERS.json.gz`, `CERTIFICATE.json`: the new flow, the owners and the certificate.
  `ORDER.json` and the flow's groups and patterns are #1129's.
- `lift.py`, `replay.py`, `controls.py`, `check.py`: idle profile, κ constant, control values and final marker.
- `independent_owner.py`: the width-inventory predicate only (`INDEPENDENT-DERIVATION.patch`).
- `data/PLAN.json` and `data/SPEC.json`: re-frozen by `replay.py --discover`.
- `SOURCES.json` and `SOURCE-FREEZE.json`: refreshed.
- New: `construction/word/` and `evidence/`.

`construct.py`, `verify.py`, `code/` and `vendor/pr1074/code` are byte-identical to #1129.

All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact
recovery, analytic transfer, PR559 recurrence correction and bit H1–H5 obligations remain. The packing
optimum is scoped to this fixed word, inventory, bin family and outer recipe. See `PROOF.md` and `NOTICE.md`.
