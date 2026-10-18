Portability fix (no assertion changed): `reconstruct.py` and `lift_parent.py` write `.gz` files with `gzip.compress(...)`, whose OS header byte is platform dependent (0xff on the author's Linux, 0x0a on Windows). PLAN.json pins the compressed OWNERS.json.gz by file sha256, so a Windows rebuild failed `rebuilt-parent PLAN.json` although every decompressed payload matched. Both writers now set the OS byte to 255 (the same pattern `code/audit_allcold.py` already uses). With this, the rebuilt OWNERS.json.gz, ORDER/DISPATCH/PROFILE, GLOBAL-TEMPLATE.json.gz, PLAN.json and CONSTRUCTION.json are byte-identical to the committed files on Windows (Python 3.11, zlib 1.3.1); the deflate streams were already identical.

# Finer kappa grid on PR1319's exact-fill construction

This package is PR1319's construction unchanged (same words, owners, dispatch, plan, admission engines and controls). The only change is the outer assembler's final kappa grid in `code/assemble.py`: the three grid expressions `ticks=margin*10**18`, `Q(...,10**18)` and the `next_grid` control `Q(1,10**18)` become `10**24`, matching the already merged PR1019 refinement. With the same exact margin, the 47 strict outer inequalities hold at the finer floor and the next grid point is rejected (checked offline with the retained outer engine for both the native and conservative endpoints). kappa moves from 0.001676855229071321 (floor at 1e-18) to 0.001676855229071321886144 (floor at 1e-24): the construction itself is not improved. The receipts under `evidence/` and `PRICE.json` are PR1319's 1e-18-grid run; SPEC.json, CLAIM.json and the assembler are the refined pins.

Conditional **κ = 0.001676855229071321**, a **0.00001493392089%** improvement over PR1297 (0.001676854978651125). Doubling the four-kernel construction to 74 replicas admits one more extra-provider call and fills all four leftover rank-one gaps.

The complete package-owned finite replay passes. It reconstructs all 319,680 owner roles and the exact doubled parent; checks emitted chronology, charts, finite invoice, both exact moment engines and 47 outer inequalities; rejects 114 admission, 12 bit, 15 controller, eight independent owner and six new geometry/charge mutations. The generalized formulas also retain the 37-replica regression with 114 rejected admission mutations.

The scalar words are byte-unchanged from PR1297. This local release run explicitly reused their word-bound completed native receipts and reran their independent local, fusion, kernel and phase-premise checks; it does not claim fresh native runs. Hosted CI is separate and was queued at the last exact-head check.

The dispatch is 249 base / 417 extra among 666 calls. Exact alternating paths change whole width-four and width-five owner assignments. Idle H48=22,748 and no H1 gaps remain. Prefix use is 1,441 bits, charged at 2,048; row coefficient 19,545 is below the unchanged 20,161 limit. PROOF-NOTE.md explains the direct sum, namespace sharing and larger prefix charge. No pending idle axis is transferred between data streams.

Reproduce offline with Python 3.14 and SymPy installed:

```sh
python -B research/global-mixed-t74-exact-fill/verify.py --work /absolute/path/to/new/work
```

Default operation runs both native suppliers sequentially. Explicit `--base-native-from` and `--extra-native-from` accept completed predecessor native directories only after word and stage binding checks. Work must be outside the package and must not exist. `reconstruct.py --out /absolute/path/to/new/owners` runs the separate standard-library owner construction. See `evidence/FULL-ADMISSION.json` and the exact pinned predecessor under `vendor/pr1297`.

Conditional finite construction only. All-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, PR559 recurrence correction and PR589 bit H1-H5 assumptions remain. No unconditional theorem, full Lean certification, or global packing claim.

Credit: Rohan Arun / PR1297 and PR1286 for the four cold-kernel composition; Jeremy Kothe / PR1274 for the first helper-donor kernel; Jeremy Diviney / PR1193 for the mixed-provider flow and regular matching; Hao Yan / PR1074 for source-event windows and direct-sum lifting; Thomas DiFiore / PR1148, PR1195/1196 and the retained X54, owner and PR589 bit lineage. PR1240/1264 motivated the packing-headroom screen. Prepared by Rohan Arun with substantial OpenAI Codex assistance. Apache-2.0; predecessor notices retained.

## Open next questions

- Seek a new local paid profile or a compatible centre-path change. This result only removes the integral packing remainder of the existing two-provider construction.
- Further replication alone is not claimed to improve this exact-fill profile, and global optimality remains open. All inherited theorem obligations remain conditional.
