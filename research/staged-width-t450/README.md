# Combining T37 and T8 chronology with the staged-width suppliers

**Complete source-bound T450 admission passes, with conditional κ = `0.001730047552093344159584 − 10^−46 − 10^−70`.**

This candidate combines the 37-replica chronology underlying Ross Richardson’s PR3605 with our retained eight-replica chronology from PR3494. A new integer allocation uses ten copies of the combined 45-replica order, for 450 replicas in total. It preserves both staged-width suppliers from PR3605.

The complete finite profile has its root between `0.001730047552093344159584` and `0.001730047552093344159585`, above the T740 profile at PR3605 commit `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. All 1,652,400 individual assignments passed an independent native-frame owner audit. The full physical, precision and outer release passes.

The package contains the integer certificate, deterministic builder and verification code. Private optimization tools and the research journal are excluded. From the repository root, run the bounded finite checks with Python 3.12 and the dependencies declared in `VERIFY.json`:

```sh
python3 -B research/staged-width-t450/verify.py
```

This authenticates declared source inputs, reconstructs the actual aggregate profile, checks its rational root and predecessor comparison, and runs semantic and import-authentication rejection controls. It does not rerun every literal role or full admission. The separate `verify_price.py` convenience command prices the pinned expected profile only.

For deterministic literal reconstruction, choose a fresh output directory:

```sh
OWNER_SOURCE_REPO="$PWD" python3 -B research/staged-width-t450/owners/portable_expand.py --out /tmp/t450-owners
```

For complete source/native/physical/precision/outer replay, use another fresh output directory:

```sh
python3 -B research/staged-width-t450/replay.py --t8-package research/t8-rank7-two-swaps --main-files . --allocation /tmp/t450-owners --work /tmp/t450-release
```

The portable command explicitly authenticates retained parent-cache reuse, reconstructs the changed supplier sources, runs both changed native suppliers freshly, and invokes full admission with the original stock checker. The completed separate admission run instead reused those same-session freshly checked changed native caches with exact source and word bindings. The complete portable T450 command has not been run end to end with fresh changed-native execution; the completed admission used authenticated same-session native caches. Stored evidence, finite checks and full replay have different coverage; `VALIDATION.json` records the exact coverage. The finite command also authenticates the stored completed release receipts; that is not a fresh complete replay.

Independent native-frame literal-audit instructions are in `owners/README.txt`. That audit checks every assignment but does not replace the complete release.

See `PROOF.md` for the construction argument and `CREDITS.md` for attribution. All inherited conditional premises remain; this is not an unconditional multiplication theorem or a change to the selected result.

## Open next questions

Can a different combined chronology improve the profile further? Start with source-derived windows and an exact integer certificate before literal expansion. For this fixed 45-replica chronology and proportional profile, ten copies are the minimum permitted by integer profile counts; that is not a lower bound for other profiles or orders.

Can a changed supplier or recursive interface improve the underlying cost? Estimate source acquisition, delivery, restoration and the full physical bill before a large search.
