# Combining T37 and T16 chronology with staged-width suppliers

**Preparation in progress: complete T530 admission is running. No admitted T530 κ gain is claimed yet.**

This candidate combines the T37 chronology underlying Ross Richardson’s PR3605 with the retained T16 chronology from PR3413, preserved by our T16 provider-composition work. Ten copies of the combined 53-replica order give 530 replicas. Actual source windows are recomputed across the join and both supplier dispatches are preserved.

The finite profile root lies between `0.001730071864705779882540` and `0.001730071864705779882541`, above our published T450 contribution PR3624. All 1,946,160 literal roles pass the independent native-frame owner audit. Full physical, precision and outer admission remains pending.

From the repository root, run the finite checks using the dependencies in VERIFY.json:

```sh
python3 -B research/staged-width-t530/verify.py
```

For deterministic literal reconstruction, choose a fresh directory:

```sh
OWNER_SOURCE_REPO="$PWD" python3 -B research/staged-width-t530/owners/portable_expand.py --out /tmp/t530-owners
```

For complete replay, choose another fresh directory:

```sh
python3 -B research/staged-width-t530/replay.py --t8-package research/t8-rank7-two-swaps --main-files . --allocation /tmp/t530-owners --work /tmp/t530-release
```

The inherited T8 package supplies the source materializer and admission machinery; the candidate chronology is T37+T16. The portable entry reconstructs changed suppliers and freshly checks both native words, with explicitly authenticated retained parent reuse. The current separate execution instead reuses authenticated native caches freshly checked earlier in the same session. Its scientific driver and 648-source manifest match the portable materialization. The complete fresh portable CLI has not run end to end.

Private optimization tools and the journal are excluded. This finite construction retains all inherited conditional mathematical premises and does not change the selected result.

## Open next questions

Can combining both retained T8 and T16 chronologies improve the same supplier inventory? Recompute actual windows, obtain exact joint flows, and price the full profile before expansion. Can a different recursive interface improve the underlying supplier ceiling? Include source acquisition, restoration and all physical costs before a large search.
