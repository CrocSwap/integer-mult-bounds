# The selected complex rank ledger, rebuilt from the emitted program it certifies

**Independent verification. No new κ, and no check is changed or weakened.**
- Card: `independent-moment` (ledger method), with the scope refined in [TASK.json](TASK.json).
- Track 75–84, assignment seed 78 (OS CSPRNG via Python `secrets`).
- Base commit `dadfea6e8a78ff6ba901705f87532a71c6f5bbb8`. At that base the selected record is
  frontier1094, κ = 0.001672660197076918.

## The obligation

The selected certificate `research/community-frontier1094-audit/ASSEMBLY.json` (`1122cb3a…`) prices
the complex profile `{1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152, 48:4866}`. That
profile is the aggregate that the authors' controller audit (`OWNERS-AND-PROFILE.json`) derived from
the emitted hosted program `GLOBAL-TEMPLATE`, whose digest the certificate records.

The selected κ uses the native complex recurrence, which has no bad-class surcharge. The review that
allows this is pinned by the selected record as `research/complex-multicold/vendor/pr559/PROOF.md`
(`d5d498ed…`, byte-identical to [native-complex-moment552/PROOF.md](../native-complex-moment552/PROOF.md)).
The review rests on two premises:

- **(a)** The emitted controller has an *exact exhaustive recursive-child profile* (lines 17 and
  24). Every positive-rank frame climb and centre descent is a recursive child, and the profile is
  their sum over all local invocations plus every nonempty idle remainder.
- **(b)** There is *no good/bad q-adic selector* (lines 9 and 24).

**This package checks part of (a) at source level: the priced aggregate equals the emitted recursive
children of the program the certificate binds.** It does not address (b). It also does not re-prove
the classification rule or the whole-owner hosting semantics.

### Existing checks of this link

Author and in-lineage checks:
- `audit_allcold` (the authors' ASYNC audit) reads the template and programs but counts declared
  ranks.
- The in-package #858 `indep16` replays the word and binds the backward profile to the receipt.
- `hpe_audit_local.py`, the "PR514/PR433 independent replay" pinned in `SELECTED-SOURCE.json`,
  replays both programs' frames. Its receipt `INDEPENDENT-LOCAL-REPLAY.json` is in the capsule.

Non-author checks:
- The maintainers' `INDEPENDENT1094.json`, produced by
  `research/community-batch1099-audit/check_frontier1094.py`, audits the owner map and prices the
  profile. It takes the local factor (804384 of the 1041408 rank mass) from the word's self-reported
  `local_profile` (line 21) and hard-codes `live=14336, calls=144` (line 32).
- Open #1209 audits the pending axes and the owner map against package inputs and a parent template.

Neither non-author check reads the emitted template or the dispatched programs.

## What this package checks

`verify.py` uses the standard library only. It reads the committed replay capsule's members in
memory, parsing exactly the hashed bytes. It imports nothing from the repository and executes no
package code.

**New in this package:**
- **Byte binding (B1–B9).**
  - The capsule digest matches the integration pin, and the tar members are safe.
  - The repository certificate equals the capsule certificate and the record's
    `certificate_sha256`. The record is a checkpoint once the frontier moves; otherwise it is the
    selected record.
  - The template digest equals `ASSEMBLY.template_sha256`, and the owner-audit digest equals
    `ASSEMBLY.input_sha256.owner_audit`.
  - `LOCAL-PROGRAMS`, `CANONICAL-WORD`, `DATA-PHASES` and `INDEPENDENT-LOCAL-REPLAY` equal the owner
    audit's `source_artifacts`. The replay receipt names the same programs and word.
  - The literal remainder frames match their receipt.
  - The owner map matches the template and the source manifest, and `FULL-WORD` is `SLOT-PINS`-pinned.
  - Members are resolved by full path. The `split-centres` copies under `global/` and `global8/` are
    decoys, and the controls reject the `global/` ones. `global8/base/providers` holds byte-identical
    copies of the bound members.
- **The template's dispatch (L1–L3, L9–L12).**
  - Every `(local stage, replica)` is called exactly once.
  - The local sweeps of the schedule dispatch exactly those calls (stage, replica and provider), and
    every schedule event acts on one replica.
  - `gauge44` is the only provider, and each idle sweep occurs once.
  - Orientation and pair follow the recipe.
  - Each call is bound to its program by compact-JSON sha256, and the programs equal the copy
    embedded in the template.
  - In every call, the routes are 704 distinct live families, and the data routes are the active
    pair's families.
  - **Every owner-map slot is executed by exactly one call route** in a live replica, and each
    helper route equals its slot.
- **A code-disjoint frame replay of the dispatched programs, bound to those calls (L4–L7).**
  - Every register runs from `start` to `final`.
  - Each climb leaves the register's current frame for a strictly larger frame that contains it, in
    its own phase. Its F2 rank is recomputed, and declared ranks are only compared.
  - Centre *i* runs from `center_frames[i]` to the empty frame (forward) or back (backward), in the
    `centers` phase, with its carrier register at that frame.
  - Adapters and residual adapters sit at their registers' start or final frames, and every scalar
    operand is at the scalar's frame tag.
  - The phase sequence is fixed, and the program and schedule vocabularies are closed.
- **The chain to the certificate (L23).** The rebuilt ledger equals `ASSEMBLY.complex_profile`,
  the owner audit's `paid_profile` and `INDEPENDENT1094.owner.profile`.

**Cross-checks of existing work (not claimed as new):**
- Against #1209: helper widths (L13); joint F2-orthonormality of sibling pending axes, which implies
  the direct sum (L15); contiguous hosted prefixes (L18); and the idle-remainder recount, matched one
  for one with the emitted `idle_children` and literal frames (L19–L20).
- Against the in-lineage replay: the per-call ledgers equal its receipt (L25).
- Against #1091 rule R7 and `INDEPENDENT1094`: the mass and deficit identity (L22).
- Per-family conservation (L21): every live family carries m−1 = 72 data or pending units. This is
  #1012's coverage identity, checked per family on the emitted T16 programs. It pins any rank-mass
  error to a single family. Errors that change the histogram's shape are caught by L23 and L25
  instead.
- The helper climb totals equal the width vector of the pinned `FULL-WORD` (L24).

The receipt carries `local_profile_per_call` and `idle_histogram` as discussion #1200 item 3 asked.
It also carries `live_families_per_call` (W, N, 896 live families per replica, 9 stages), which
matches #1200's "2·pairs·V/stages", and `owner_families_per_call` (224 data + 480 helper routes). All
four are derived from the emitted program. A package receipt is not the per-record field #1200 asked
for, but it supplies the same values.

## Results ([RESULT.json](RESULT.json), reproduced byte for byte on every full run)

The same unchanged code checks the selected record, the previous checkpoint, and two in-capsule
ancestor assemblies. The ancestors are bound only through the capsule pin. All four use the T16/T8
gauge44 layout.

| Case | W | N | Rebuilt ledger | Idle remainders | Rank mass | D = W − 64N |
|---|---:|---:|---|---:|---:|---:|
| **frontier1094 (selected)** | 14336 | 144 | {1:349604, 2:60192, 3:62585, 4:20448, 5:11808, 7:7, 8:1152, 48:4866} | 7526 | 1041408 | 5120 |
| frontier1042 (previous checkpoint) | 14336 | 144 | {1:349577, 2:60193, 3:62608, 4:20448, 5:11808, 7:3, 8:1152, 16:47, 48:4850} | 7550 | 1041408 | 5120 |
| slots T8 (in-capsule ancestor assembly) | 7168 | 72 | {1:174763, 2:30105, 3:31283, 4:10224, 5:5904, 7:54, 8:576, 16:23, 48:2419} | 3783 | 520704 | 2560 |
| leaver T8 (in-capsule ancestor assembly) | 7168 | 72 | {1:174763, 2:30105, 3:30275, 4:12240, 5:4896, 7:54, 8:576, 16:23, 48:2419} | 3783 | 520704 | 2560 |

For the selected record:
- The per-call ledger is `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` in both orientations, with 80
  forward and 64 backward calls.
- Families of pairs 0, 1, 2 and 3 are called 3, 2, 2 and 2 times.
- Rank mass is 1041408 = 144 × (1792 data + 3730 hosted-helper + 64 centre units) + 237024
  idle-remainder units. The pending mass is 774144 = 537120 hosted + 237024 remainder.

Each rebuilt ledger equals the assembly it is compared with.

How much each case tests:
- The frontier1042 case shares its programs, word and phases with #1094, so it mainly exercises
  hosting and the idle layer.
- The T8 cases change W and N. The leaver case also has a different word and different programs.
- Constants are read from the data (`v`, `h`, `R`, the recipe's pairs, `m`, `live`), not
  hard-coded.

## Controls ([test_package.py](test_package.py): 43 tests, about 10 s)

The four-record positives come from `verify.py`. The test suite runs the frontier1094 positive, plus
a check that the result does not depend on the order of the idle children and remainder frames.

Each control mutates the decoded inputs. The test asserts the **first** check that rejects it.
Program edits are consistent forgeries: the template's embedded copy and every call hash follow the
edit.

**Frame replay**
- A climb's rank is relabelled (L6).
- A climb is given a non-nested target (L5).
- A climb is moved to another register (L5).
- A climb is made descending (L5).
- A climb's start is chain-broken: a same-dimension nested from-frame (L5).
- A centre's direction is flipped (L7).
- An adapter is placed at the wrong frame (L5).
- A scalar is placed at the wrong frame (L5).
- An extra phase marker is added (L4).
- An unknown program event or schedule kind is added (L4).

**Dispatch**
- The embedded programs differ from the dispatched ones (L3).
- A program hash is swapped (L3).
- An orientation is swapped and rehashed (L2). This is a consistency check only, since both
  orientations have the same ledger.
- A call is duplicated (L1).
- W is changed (L9).
- A local sweep is repointed, so one call runs twice and one never (L9).
- A foreign provider is added (L9).
- A sweep acts on several replicas (L9).
- A bank sweep reads the idle children (L8).
- An extra bank-padding child is added (L8).
- A data-route family is duplicated (L10).
- A helper route is moved to another family (L11).
- A slot is parked in a phantom replica, leaving a ghost copy (L11).
- A whole pair-0 stage is dropped together with its recipe, calls and sweeps (L11). L21 to L23 would
  also reject it.
- Spectators are shortened (L12).

**Hosting and remainders**
- A pending axis is made label-disjoint but F2-dependent (L15).
- A rank-0 child is made pending with an axis that keeps every sibling union orthonormal (L19).
  L20 to L23 also reject it.
- A slot gap is kept consistent across the map, template and route (L18).
- An owner-map field that no other check reads is changed (L16).
- An idle child is dropped (L19).
- A mass-preserving hosted/rank shift is applied (L19).
- A remainder frame is duplicated (L20).
- A remainder frame is made dependent (L20).

**Certificate**
- The certificate profile is tampered with (L23).
- The independent profile is tampered with (L23).

**Packaging**
- The decoy `split-centres` programs are substituted (B6).
- The decoy `split-centres` template is substituted (B4).
- A foreign local-replay receipt is substituted (B6).
- Another record's owner map is substituted (B7).
- One capsule byte is flipped (B1).
- Duplicate or `..` tar members are added (B2).

## Reproduce

```sh
python3 -I -B research/frontier1094-emitted-ledger-seed78/verify.py        # ~3 s; PASS_FRONTIER1094_EMITTED_LEDGER
python3 -I -B -m unittest discover -s research/frontier1094-emitted-ledger-seed78 -p test_package.py
python3 scripts/research_package.py --package research/frontier1094-emitted-ledger-seed78 --check-only
python3.12 scripts/research_package.py --package research/frontier1094-emitted-ledger-seed78
```

- **Requirements.** Standard-library Python 3.10+; the generic replay uses 3.12. No network is
  needed.
- **Checks.** They use `need()`, not `assert`, so they also pass under `-O`.
- **`--case`.** A run limited with `--case` prints `PASS_PARTIAL` and does not compare
  `RESULT.json`.
- **Source pins.** Source commits, Git blobs and SHA256 pins are in [SOURCES.json](SOURCES.json),
  and the case configuration is in [CASES.json](CASES.json).
- **Records and pins read live.** `certificates/selected-result.json` and the batch integration
  JSONs are tagged as provenance. They are read live only to find the record and the archive pin,
  so a later frontier move or integration update that keeps the pin does not invalidate the package.
- **No Makefile target.** The batch1099 audit pins the Makefile by digest, so none is added.

## Overlap and credit for shared checks

- **Open #1209** (akiva8201-dotcom, head `d1ba2631`, `research/selected1094-pending-axis-audit`)
  already checks:
  - the cross-child pending-axis independence on all 896 bases, with an XOR-dependent control;
  - helper widths;
  - prefixes;
  - the idle suffix profile and the complete profile.

  Those are cross-checks here.
- **The in-lineage `hpe_audit_local.py`** replay, ported by open **#1184** (woklerx, head
  `2f1c9e0e`), already frame-replays both programs, including their scalar and wrapper frames
  (receipt status `PASS_INDEPENDENT_LOCAL_SCALAR_FRAME_AND_WRAPPER_REPLAY`). This package's replay
  is code-disjoint and adds the binding to the template's calls, sweeps and owner map. It checks
  scalar *frame tags*, not scalar arithmetic. Open **#1149** (woklerx) checks the
  canonical-frame rank identity.
- **The coverage identity** is from our open **#1012**.
  - Our merged #1069's pricing code, applied to this profile by `INDEPENDENT1094`, records D = W − 64N.
  - Open **#1240** (Douglas Colkitt / Mister-Meeseeks) uses the identity as the premise of its
    packing ceiling and re-checks it arithmetically. Its #1042 idle histogram matches our second
    case.
- **#1091** (Josie Elliston, seed67) audits the owner map, including rule R7. It excludes the
  emitted controller.
- **Open #1255** (bitplane, head `add1e267`; claimed in discussion #1237) audits the exact phase of
  the residual charts. L11–L12 bind only route structure and spectator counts. Charts and phases are
  **not** validated here.
- **Complementary checks:**
  - #1112 (Wronskode): the PR1042 invoice, guards, bootstrap and outer slacks.
  - #1142 (martinxxx9): PR1042 capsule closure.
  - #1198 (Scratch-net): the scalar macro map and omissions; it excludes frames.

## Trusted, and not checked here

- **Event classification.** These classifications are the PR552/PR559 semantics:
  - positive-rank climb and centre events are recursive children;
  - scalar, adapter, phase and residual-adapter events are finite work;
  - the non-sweep schedule kinds (`bridge`, `terminal`, `terminal_Y_translations`,
    `translate_every_live_family`, `bank_padding_cover_sweep`) are not recursive-child work.

  Closed vocabularies make the classification exhaustive but do not re-prove it. Only
  `execution_schedule` is vocabulary-checked, and `async_schedule.source_schedule` is not read.
- **Scalar arithmetic.** It is not re-executed. Only frame tags are bound.
- **Pending axes.** The `DATA-PHASES` axes are taken as the inherited PR558 idle-child subspaces. They
  are checked for rank, port independence and joint orthonormality.
- **Family layout.** The layout `replica·896 + (2·pair+side)·112 + port` follows #1091's rule R3.
  Conservation holds only if it is right.
- **Capsule bytes.** They are bound by hash, not re-executed.
- **Downstream pricing.** Moments, the κ reduction, invoice, guards, bootstrap and the 47 outer
  inequalities are not checked.
- **Premise (b) and inherited assumptions.** The review's premise (b), and the all-size/compiler,
  hosting, precision/tape, analytic-transfer and PR589 H1–H5 assumptions, are untouched.

## Open next questions

1. **Does the rebuild hold for the mixed-provider T37 templates of the open claims?** These include
   #1183, #1192, #1193, #1201, #1207, #1218 and #1239.
   - Why it matters: they would replace the selected record, and their layout differs from the
     T16/T8 gauge44 layout assumed here.
   - First step: generalize the provider-dispatch and family-layout bindings, then run the checker on
     one claim's maintainer capsule.
   - Blocked by: no such capsule exists on main yet.
2. **Can the event-kind classification, premise (b) and the hosting semantics be checked from the
   compiler rules?**
   - First step: state each kind's operator from `notes/general-clifford-frames.tex` and test its
     fixed-frame action on a toy word.
3. **Do the 73-axis spectator charts and residual phases match the routes bound here?**
   - First step: combine #1255's chart-phase criterion with this package's call and route bindings,
     so that charts are checked on exactly the priced routes.

## Credit

- Rohan Arun (rohanarun), with OpenAI Codex assistance: #1094. Also the PR987 slot search.
- jeremykothe2, with Claude assistance: PR1087, PR1018 (built on PR987) and the T16 owner-packing
  lineage.
- FanPUYen: PR858.
- PR1005, NewBArch PR869, and the retained PR799/741/685/645/589 lineage.
- The PR552/PR559 review, the PR558 data phases, and the PR514/PR433 local replay.
- Josie Elliston: #1091.
- akiva8201-dotcom: #1209.
- woklerx: #1184, #1149.
- Douglas Colkitt (Mister-Meeseeks): #1240.
- bitplane: #1237/#1255.
- Wronskode: #1112.
- martinxxx9: #1142.
- Scratch-net: #1198.
- Douglas Colkitt, with OpenAI Codex assistance: the maintainer replay capsules and the independent
  pass.

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude (Anthropic) via
Claude Code. Parallel read-only scout and judge subagents selected and designed the check. Two
adversarial judges, a live Discussions sweep and a post-PR soundness review found the overlaps and
holes fixed above. New material is Apache-2.0.
