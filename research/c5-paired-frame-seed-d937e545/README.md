# Five-cycle dirty recursive echo

**Exact scoped construction; no new kappa.** This package replaces an order-four frame with an explicitly priced order-five frame on a 15-coordinate workspace and a five-coordinate dirty output. Five complete reader children admit a carried C5 phase schedule costing 560 ADDs for the dirty echo, compared with 800 ADDs for an eager-restoration control. Two optimized five-child echoes compose into one ten-child echo at 1,090 ADDs versus 1,120 separately, removing one 30-ADD copy/restore wrapper.

The five child readers select pentads `[0,1,2,0,1]` and intertwine the same 5-cycle on the workspace and output. Each child costs 41 ADDs, each complete echo includes its inverse and the 30-ADD outer source copy/restore, and all dirty state is retained. The proof gives the exact five-state phase recurrence; every one of the 3,125 five-child phase paths is enumerated. Exact integer maps are checked on all 35 basis columns.

This changes the frame group and reader instance from the order-four PR1391 interface. The prior `z4-persistent-pair-seed57` package mentioned order five as an unselected follow-up; it did not build or price this C5 construction. The nearby active order-four heterogeneous 3+7 echo claim changes reader sets and arity, while the selected T16 helper-reuse claim concerns a different boundary object.

## Reproduce

With Python 3.14 (the available local interpreter):

```sh
python3 -I -B research/c5-paired-frame-seed-d937e545/verify.py
python3 -B scripts/research_package.py --package research/c5-paired-frame-seed-d937e545 --check-only
make selected-record-check
```

Expected verifier result:

```text
PASS_C5_PAIRED_FRAME k5=60/180 eager root=560/800 k10=120 paired=1090/1120 paths5=3125 basis=35
```

The registered package replay is declared for Python 3.12; that interpreter is unavailable in this environment. The direct checker uses only the standard library.

## Exact model and limitations

The complete invoice charges the explicit signed-swap cycle circuits, every child and inverse, all frame transitions, and every outer source copy and restoration. The 560-versus-800 comparison is within this declared C5 macro alphabet; the cycle circuit is not claimed ADD-optimal among unrestricted integer circuits.

The optimized root echo has prefix row-L1 peak 22 versus 11 for the eager control; the joint ten-child echo reaches 42 versus 32 for the two separate optimized calls. This coefficient growth is measured exactly and no fixed-precision or tape admission is claimed. This package does not identify or instantiate a selected supplier with this interface; the selected source manifest is unchanged, and no selected-profile saving or new kappa follows.

The selected record at base `0b1cccf86e2f5132ed286a26ef0a681a495740ea` has SHA256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`; it retains conditional kappa=836330098538459/500000000000000000. Its review, source manifest, assembly and reproduction command are pinned in [SOURCES.json](SOURCES.json). This package does not rerun `make frontier1094-verify`.

## Coordination and credit

The scoped claim is [Discussion #1163](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18922127); its [result update](https://github.com/CrocSwap/integer-mult-bounds/discussions/1163#discussioncomment-18922332) records completion. The package is under review in [PR #1826](https://github.com/CrocSwap/integer-mult-bounds/pull/1826). The pre-claim overlap refresh at 2026-10-14 10:47:07 UTC covered 479 open PRs and 453 Discussions with no warnings. A final pre-submission refresh at 2026-10-14 11:01:40 UTC covered 485 open PRs and 464 Discussions with no warnings; the only exact C5 remote match was this task claim, and no third-party order-five match appeared. The only close matches were the previous order-four echo and current order-four/selected-T16 claims described above.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scope selection, derivation, implementation, exact checking and writing; no independent human review is claimed. Predecessor and selected-source attribution is pinned in `SOURCES.json` and `NOTICE.md`.

## Open next questions

- Does a selected supplier expose an order-five intertwining child family? The first step is to inspect the selected complex supplier's source-bound child maps; the blocker is no known supplier instance with this C5 boundary.
- Can the row-L1 peak be admitted by an actual fixed-precision and tape contract? The first step is to carry the exact prefix envelope into one named supplier's existing host schedule; the blocker is missing supplier embedding.
