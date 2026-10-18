# R438 bit word: one improving transport, plus two PR1345 atlas crash fixes

**Status: finite conditional local construction (word, replay, interface checks, priced endpoint) and a tool fix. No new kappa. Conditional on PR1043 (open, not admitted); the hosted program was not emitted or audited.**
The bit supplier does not bind. At the selected frontier
(`certificates/selected-result.json` -> `research/community-frontier1094-audit/ASSEMBLY.json`)
complex is `0.001675462676808103522925`, bit (PR589) is
`0.001733427039589844234749`, and kappa is `0.001672660197076918`. Every bit value
below is larger than the complex value, so kappa is unchanged.

## Result

PR1043's R438 word (Ali Romman) reads source77 late, at frame186. That changes
receiver444's path from PR589's `[0,79,509,392,513,1]` to `[0,186,509,392,513,1]`,
so its first two climbs become `(2,2)` instead of `(1,3)`.

This package moves one elementary A addition:

- **Before:** op 2027, `444 += 77` at frame186. It is the single-source A gate 1992 of R438.
- **After:** elementary slot 154 (also gate index 154) at frame79. Source77 is
  still at its start frame79 there.

After the move, receiver444's path is again PR589's `[0,79,509,392,513,1]`. Every
surviving register path equals PR589's R439 path. Only helper470's `[0,79,1]` is
gone. The arithmetic is unchanged: the same ADDs, the same D, and the same F2 map.

| | PR589 R439 | PR1043 R438 | this word (R438-T154) |
|---|---:|---:|---:|
| helpers | 439 | 438 | 438 |
| local native ADDs (incl. D, C) | 24,305 | 24,248 | 24,248 |
| local records | 27,234 | 27,175 | 27,175 |
| local paid profile | `{1:1323,2:1342,3:79,4:44,5:102,6:11,7:19}` | `{1:1321,2:1344,3:78,4:44,5:102,6:11,7:18}` | `{1:1322,2:1342,3:79,4:44,5:102,6:11,7:18}` |
| local paid rank mass | 5,129 | 5,121 | 5,121 |
| fwd / rev bound, local / 9-stage bits | 49,347 / 1,113,070, 93 / 177 | same | same |
| hosted paid children / rank mass | 904,896 / 1,808,352 | 904,320 / 1,808,352 | 904,320 / 1,808,352 |
| bit c | 0.001733427039589844234749 | 0.001734176288479865766692 | **0.001734220472884893243548** |

- **Exact new c:** `433555118221223310887/250000000000000000000000`. It is accepted
  at c and rejected at `c + 1e-24 = 1734220472884893243549/10^24` by both engines,
  with the inherited surcharge.
- **Gain:** +4.418441e-8 over PR1043 (+0.002548%) and +7.934e-7 over PR589 (+0.045773%).
- **Hosted profile:** `{1:380736, 2:400256, 3:22752, 4:26784, 5:29376, 6:17344, 7:26496, 10:160, 12:96, 14:32, 42:288}`.
- **Why it gains:** relative to R438 the change is rank1 +1, rank2 -2, rank3 +1 per
  call, so 288x that is hosted. `d -> d(64/d)^c` is strictly concave, so `f(1)+f(3) < 2f(2)`.

**Content pins** (canonical-JSON sha256, PR1043's `word_sha256` convention):

- R439 `5642fd0e35a1acc11acff8d0c08350c1617e95f310d4d35ad63a651f9eeeba0b`
- R438 `27609b6880f8913900c0e1758c63a482f8588c16fede1bd0071c6df36ef2e285`. This
  equals PR1043's CERTIFICATE. FRAME-PATHS.json also matches.
- New word `7aad486877b8c03866b8f1e6f909d12085da347d86aaae891f86f4e2dbc550d1`.
  It is stored as `words/r438-t154.json.gz` (gzip file sha256
  `a353999bceac4ac957f540adfd3e5f8768297138b27132eeb83332e2ea4b1022`, mtime 0).

**Gate format: re-merged.** The original multi-source gate format is kept and no gate is split:

| Section | Gates | Note |
|---|---:|---|
| A | 2074 | Same as R438; the same 18 multi-source gates in the same order. |
| C | 2573 | PR1043 rule: literal reverse at frame 1. |
| D | 111 | Rebuild equals R438's D. |

Only the A and C fields differ from R438.

The scouting application split all A gates. That gives A 2129 / C 2628 gates: the
same elementary op sequence, ADDs 24,248 and the same profile, but word sha `9ad09c84…`.
**It is not used**, and we do not claim that every checker accepts it.

**Equivalent placements.**

- The commutation window of op 2027 is `[0, 2111]`.
- The events on 444/77 in that window are at 154, 155, 425, 2028-2034 and 2083.
- Insertion positions 0..425 at frame79 fall into the atlas segments represented by
  **154 (chosen), 155 and 425**. Only positions 154, 155, 230 and 425 were built; each of those gives the same
  profile, ADDs and frame paths.
- Their word shas: slot155 `5fbf512d…`, slot425 `d05f197e…`.
- Slot 230, R439's helper-birth position, gives `ae5f36b4…`. That is exactly PR589's
  word with the birth `A[230]: 470 += 77` retarget to `444 += 77`, the read
  `A[1993]: 444 += 470` deleted, and C and D rebuilt by PR1043's rules. In other
  words, it is PR1043's deletion done at the helper's birth rather than at its late read.

## Verification (exact outputs, CPython 3.14.4, Linux x86_64, 4 cores)

**Step (1).** The vendored PR1043 `build.py` rebuilds R438 from the pinned PR589 word
(`e3e301e6…`, blob `85a4499b…`). It matches PR1043's CERTIFICATE local receipts and
FRAME-PATHS.json. PR1043's own `local_controls` give five rejections and the paid
neutral pair.

**Step (3a). PR1043 `build.replay`** (arbitrary dirty endpoint, all 660 columns):
`adds 24248, records 27175, profile {1:1322,2:1342,3:79,4:44,5:102,6:11,7:18}, rank_mass 5121, copies 9, forward 49347, reverse 1113070, local_bits 93, nine_stage_bits 177`.
`wlib.paid` gives the same profile.

**Step (3b). `xcheck_p.py words/… --json`**, exit 0, stdout:
```
labels: 111 E8 root lines of the 120 (even unimodular lattice of rank 8, Gram det 1; 9 punctured lines); 636 frames, every one closed in the live labels
retained totals at the scatter: COPY ranks [7, 7, 7, 7, 7, 7, 7, 7, 7] (decoder constant 63); every total sits at the hyperplane of a distinct punctured line: True
legality and exact F2 replay on all 660 columns (sources, targets, 438 dirty helpers as symbolic inputs): PASS; gates D/A/B/C = 111/2074/712/2573
   H1_no_target_feeds_z                     holds
   H2_D_frame0_targets_from_helpers         holds
   H3_A_z_only_scatter_targets_B_split      holds
   H4_C_literal_reverse_at_full             holds
   H5_V_identity                            holds
   U_block_form                             holds
   J_identity                               holds
   K_equals_D                               holds
   C_is_U_inverse                           holds
   {"z_gates_A": 2074, "source_writes_A": 0, "z_gates_B": 499, ... "cleanup_gates": 2573}   (full line in the receipt)
PASS interleaved interface lemma: hypotheses H1-H5 hold and the conclusion decomposes as U, J = I, D = K, C = U^-1
```
The interleaving statistics are identical to R438's. On R438, xcheck's JSON equals
PR1043's certificate `native.candidate.interface` exactly.

**Step (4). Hosting and price.**

- **Hosting:** PR1043's own `pipeline.selection()` (vendored) runs on the nine-stage
  schedule of `bit589-width7-windows-seed72/windows.py`. That module anchors the
  schedule to `global_k.py` and checks its windows three ways. The window capacities
  `{0:14,1:7,2:28,3:7,4:42,5:7,6:42,7:28,8:14}` equal `bit589-width-packing`'s
  unique slot model.
- **Same hosting change as PR1043:** the output equals PR1043's recorded
  `hosting_change` exactly: the 9 removed slots, old `{2:435,4:444,6:444,7:666,42:9}`,
  and new `{2:430,4:441,6:443,7:666,10:5,12:3,14:1,42:9}` remainders per replica.
  This is expected because hosting depends on R, not on the local word.
- **Recount:** `288·local + 32·remainders` reproduces PR1043's audited R439 and R438
  hosted profiles. PR1043's `check_hosted_change` accepts the new word against the
  PR589 audit (a consistency check only: the hosted profile is assembled from the same `288·local + 32·remainders`
  identity it checks, so this is not an independent acceptance) (paid calls 904,896 -> 904,320, returned idle rank 2,304). Its
  `idle_control` rejects with "Wrong hosted rank mass".
- **Price:** the endpoint uses assemble9.py's lines (`moment.certify`, then the
  base-two engine with the surcharge at the lower and upper endpoint) and a second
  two-engine check at c and c+1e-24. It reproduces PR589's and PR1043's invoice c
  exactly and gives the new c above.

**Step (5). Local optimality.**

**PR886 `frameopt.py`** at the new c, about 22 s:

| Word | Improving components | Smallest alternative delta | Notes |
|---|---:|---:|---|
| new word | **0** | +9.114249e-4 | 157 free gates, 132 components |
| degraded positive control | 37 | | recovers the new profile exactly |
| R438 | 0 | | frame-only cannot see this transport |

**PR1345 atlas** with `atlas.patch`, line 28 set to the new c, on the new word:

| Section | Ops | Legal moves | Same profile | Strictly worse | Improving | Smallest strict loss |
|---|---:|---:|---:|---:|---:|---|
| A | 2129 | 5815 | 5579 | 236 | **0** | 8.0046e-6 |
| B | 934 | 3561 | 3226 | 335 | **0** | 1.9424e-3 |

- **Shared-register pairs:** A has 13,672 pairs, with 224,369 scored, 209,485 same,
  13,995 worse, 889 illegal and **0 improving**. B has 6,006 pairs, with 218,448
  scored, 202,222 same, 15,439 worse, 787 illegal and **0 improving**.
- **Not covered:** whole components exceed the budget (A: one of 1,923; B: five of
  149-206) and are not enumerated, as in PR1345.

**Negative controls (verify_transport.py; all must reject).** Each word control is
rejected by PR1043 replay and by xcheck_p, except where noted:

| # | Control | Rejection |
|---:|---|---|
| 1 | Read at frame79 after source77 climbed (slot 426) | "Frame descent"; xcheck "climb not nested: register 77 from frame 186 (dim 2) to frame 79 (dim 1)" |
| 2 | Early read kept at frame186 (slot 154) | same two rejections |
| 3 | Stale R438 C | Replay **accepts**: C is only reordered across commuting gates, so it is F2-correct. xcheck rejects ("H4 … FAILS", "REJECT interface"). So H4, not F2, guards the literal format. |
| 4 | One D operand dropped | "Wrong arbitrary-dirty endpoint"; xcheck "targets not y + x" |
| 5 | R438 hosted profile at the new c | rejected |
| 6 | New profile at c+1e-24 | rejected |
| 7 | Omitted returned idle charge | PR1043 `idle_control` rejects |
| 8 | Flipped byte in the pinned PR589 word | sha256 pin rejects |

PR1043's own 5 controls also run. Positive controls: the paid neutral ADD pair
(+2 ADDs, same profile), and the new profile is accepted at R438's c.

## PR1345 atlas bugs (`atlas.patch`, 3 changed lines)

The atlas file is research/bit589-transport-atlas/atlas.py at head b54a856a.

1. **Bug 1, line 250 / 282-284.** With any improving single,
   `dict(ops=…, **dict(stat), …, improving=improving[:5])` fails with
   `TypeError: dict() got multiple values for keyword argument 'improving'`.
   The fix counts under `stat['improving_count']`.
2. **Bug 2, lines 375 and 416.** `best = (d, moves)`, so `d[0] < best[0]` compares a
   Fraction with a tuple and fails with
   `TypeError: '<' not supported between instances of 'Fraction' and 'tuple'`.
   The fix uses `best[0][0]`.

The bug fix does not touch the hard-coded PR589 c on line 28. A separate, asserted
substitution changes it only for the new-word run.

**`atlas_bugs.py` results.** All PR1043/PR1345 inputs come from the pinned vendored copies.

| Run | Result | Time |
|---|---|---:|
| pristine file on R438 | exit 1, **TypeError at line 282** (bug 1) | 36 s |
| hunk 1 only on R438 | exit 1, **TypeError at line 416** (bug 2) | 95 s |
| patched on R438 | exit 0 (see below) | 139 s |
| patched on PR589 | output **equals PR1345's result.json** and passes verify.sh's census asserts | 140 s |
| pristine on PR589 (`--full`) | same, so the bugs are latent on PR589 | 169 s (earlier run, 5 jobs on 4 cores) |

On R438 the patched atlas reports exactly three improving singles: op 2027 -> slots
154/155/425 at frame79, delta -9.110061e-4 each at PR589's c. It also reports 190
improving A pairs; the best is `[[2027,154,79],[2030,2028,509]]`, which adds nothing
beyond the single move.

- **Line 375 on these words:** it is unreachable, because every component exceeds the
  200,000-combination budget. Its pristine condition is evaluated on sample values
  and raises the same TypeError; the patched condition returns True.
- **Patch controls:** the patch is checked to be the minimal difflib diff of its own
  application, and a patch with corrupted context is rejected.
- **Result-comparison controls:** a mutated result.json fails the census, and the R438
  output differs from result.json.

Prior art: `research/bit589-fixed-option-cross-pairs-seed16/atlas.py` (Cinna Davis)
already uses `best[0][0]` in its adapted cross-pair loop. PR1345's own file was not fixed.

## Commands and runtime

From the repository root, after moving this directory to `research/<slug>/`:

```sh
python3 -I -B research/<slug>/verify_transport.py --out          # 38-42 s; frameopt/xcheck in 4 subprocesses
python3 -I -B research/<slug>/verify_transport.py --full --out   # 183 s (atlas on the new word: 144 s)
python3 -I -B research/<slug>/atlas_bugs.py --out                # 140 s; 4 atlas runs in parallel
python3 -I -B research/<slug>/atlas_bugs.py --full               # adds the pristine PR589 run (about 3.5 min)
```

- **Options:** `--repo ROOT` overrides the default, which is three directory levels
  above the script. `--jobs N` sets the number of parallel subprocesses.
- **Output:** each script prints one final `PASS_…`/`FAIL_…` line and refuses `python -O`.
- **Receipts:** `--out` without a path writes `<script>.receipt.json` next to the
  script. The receipts from this session are `verify_transport.receipt.json` and
  `atlas_bugs.receipt.json`.
- **Final lines:**
  `PASS_R438_T154_TRANSPORT R=438 op2027(186:444+=77)->slot154@frame79 profile=1:1322,2:1342,3:79,4:44,5:102,6:11,7:18 ADDs=24248 c=0.001734176288479865766692->0.001734220472884893243548 frameopt_improving=0 atlas=singles0/pairs0 neg_controls=8+5(PR1043 own) no_new_kappa`
  and `PASS_PR1345_ATLAS_BUGS bug1=TypeError@282(pristine,R438) bug2=TypeError@416(hunk1-only,R438) patched_R438=ok(improving singles 2027->154/155/425@79, pairs A=190) patched_PR589=result.json …`.

**Inputs.**

- Main-tree inputs are checked against sha256 and the git blob id at main
  `0fdd7d82de03e43c9e5a1000dfbcd380d1b687d2` (`lib.py` `MAIN_PINS`).
- PR-only files are vendored byte copies (`vendor/`, `VENDOR_PINS`; see `vendor/NOTICE.md`).
- The selected-result context is read live through `certificates/selected-result.json`
  and its recorded certificate hash. It is not pinned because it moves. The script
  fails if the bit side would bind.

## Scope: what is and is not checked

**Checked:**

- The literal word, using PR1043's replay on all 660 dirty columns, xcheck_p
  (E8 labels, frame closure, nesting, F2 on all columns, H1-H5, U/J/K=D/C=U^-1) and wlib.
- The hosting change, using PR1043's selection code on the anchored schedule.
- The hosted profile, as a composition checked against PR1043's audited profiles and
  recount identity.
- The two-engine endpoint.
- Frame-only optimality (PR886).
- Single and shared-register-pair transport optimality (patched PR1345, fixed-option lists).

**Not run (needs NumPy/SymPy/SciPy/C++/Boost):**

- PR1043's native pipeline: `export_records`, native legality, `columns_k` 5/9/11-stage
  checkers, `global_k`/`audit_parent_k`, and `emit_k`/`audit_hosted_k` hosted emission
  and audit.
- assemble9's full invoice: the prefix/coefficient/two-level precision charges and
  the outer kappa assembly.

The forward/reverse bounds equal PR1043's, so its 93/177-bit precision claims
should carry over, but that is not re-derived natively. The hosted program is not
emitted or audited here.

**Not claimed:**

- triples or larger simultaneous transports;
- boundary-adaptive or cross-section pairs;
- other gate orders or structural rewrites;
- optimality of R438 itself;
- composition with other bit changes (PR1001/1015/1256/1179 etc.);
- any full multiplication theorem or practical speedup.

All inherited all-size, compiler, common-label, hosting, precision and analytic
assumptions of PR1043/PR589 remain.

**Overlap check (offline cache, local READMEs; not a novelty certificate):**

- seed11 (`bit-source-substitution-seed11`) and seed02 (`bit-source-span-seed02`)
  classify helper470/source77 substitution at the fixed gate order and explicitly
  exclude reordering. Seed02 notes the late frame79 read is illegal, which is our
  control 1.
- seed18 (`bit-kernel-entrance-seed18`) keeps all 439 helpers.
- PR1256 and `bit-helper470-native` convert helper470 to width 7.
- No local package or cached PR/discussion was found that moves the R438 read to the
  helper's birth frame.

## Open next questions

- **Native pipeline:** run PR1043's native pipeline (`verify.py` with C++/Boost) on
  `words/r438-t154.json.gz` to obtain the emitted hosted audit and full assemble9
  invoice.
- **Remaining transports on R438-T154:** are there improving triples, cross-section
  or boundary-adaptive transports?
- **Composition:** does birth-time inlining compose with PR1256's width-7 retirement,
  or with PR1015/PR1001's B-phase changes?
- **Other helpers:** for other deletable-helper candidates (none known at the fixed
  order), does birth-time rather than read-time inlining change the census of
  seed11/seed02 once reordering is allowed?

## Credits

- **Ali Romman (@aliromman), PR1043:** the R438 source-boundary construction, its
  stdlib builder, replay, controls, hosting `selection()` and certificate. These are
  vendored unchanged.
- **Andrzej Marszałek (@hipotures), PR1345:** the transport atlas (vendored unchanged;
  fixes in `atlas.patch`). The atlas first exhibited this transport on the R438 word
  once patched.
- **PR589/PR555 lineage:** the R439 word by DreamingOfClouds (PR589 tuning, wlib)
  on eumemic's PR555. The lineage also includes PR543/545/510, the `xcheck_p.py`
  checker (eumemic), the native/exporter lineage (Dylan Crow, PR370), PR381 (DaysSky)
  and PR442 hosting windows / `hosting_core` (DaysSky). It further includes the
  global_k/audit lineage (chafreaky PR443/444/472, DreamingOfClouds PR463/510),
  Zhihao Chen (PR425) and Jacob Sussman (E8 unit), plus the retained moment-engine authors.
- **Seth Burkart (@SethBurkart123), PR886:** `bit589-frame-optimum/frameopt.py`.
- **PR1023 `bit589-width-packing`:** Sagar Thakrar, for the slot model.
- **`bit589-width7-windows-seed72`:** Sagar Thakrar, for the global_k-anchored schedule.
  Its README credits mightyOil (#1281) and the hosting lineage above.
- **`bit-helper470-window-placement-seed14`:** Hanson Sun (@bbMisk), on Ross
  Richardson's PR1256. This is related helper470 work; its code is not used here.
- **Cinna Davis, seed16 cross-pairs:** the earlier `best[0][0]` usage.

## AI-assistance disclosure

Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance (Claude
Code, Anthropic): code, runs, checks and writing were produced by an AI agent in an
automated loop.

- An earlier AI scouting pass found the transport and the atlas bugs. Its scripts
  and results were treated as untrusted and everything was re-derived here.
- No independent human review is implied.
- New material is Apache-2.0. The vendored files keep their authors' notices.
