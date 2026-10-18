# Shifted diagonal order and repacked owner fill on PR2530's source-partner words: conditional κ = 0.0017140322985876819

**Credit first: PR2530 (zxv, with OpenAI Codex).** The eight source-partner aliases, the 422-helper words, the diagonal call order and windows, and the whole native/global/outer pipeline are PR2530's (`research/source-partner-lifetimes`). They rest on PR2462 and its lineage (Jeremy Kothe and the authors credited there). This package changes **only the physical call order and the owner fill** (PR2530's first open question: diagonal-order variants and a sharper fill). The local words, providers and every pipeline stage are unchanged.

## Result

Conditional **κ = 0.0017140322985876819089159999999999999999999998999999999999999999999999**. The exact rational is in [CLAIM.json](CLAIM.json).

- Exceeds PR2530 (0.0017137379215475043467…) by **2.943770e-07**.
- The certified complex endpoint is 428508074646920477229/250000000000000000000000, at the same 1e-24 endpoint grid and outer settings as PR2530.

## What changed

**Order.** PR2530 sorts calls by `(4*stage + replica, stage, replica)`. This package delays every call with stage ≥ 1 by four key units: `(4*stage + replica + 4*[stage ≥ 1], stage, replica)`.

- Each replica still runs its nine stages in order, and its thirty source events keep their order.
- The windows are recomputed from the order by the package's own `vendor/build_parent.py` (`actual_windows`).
- The shift lengthens the first rank-16 windows, which in the diagonal order could draw only on the first few calls. Window (0, 0) was [0, 5]; it now spans the first eleven calls.
- Under PR2530's order those windows forced 172 empty rank-16 bins and 114 empty rank-8 bins. Here no rank-16 bin is left empty.

**Fill.** The fill was nominated with PR2530's own search: the pattern MILP with interval and max-flow cuts (`search/interval_pack.py`) and the flow realization (`search/realize_pack.py`), both unchanged and run on the shifted order. It was then verified literally.

- Idle remainders: `{1:21976, 3:6662, 5:440, 8:114, 16:172, 32:3, 48:26488}` before, **`{1:21978, 3:6612, 5:524, 8:124, 48:26540}`** now.
- Unchanged: the local profile `{1:2369, 2:632, 3:320, 4:118, 5:26, 7:8}`, the width inventory `{4:33, 5:9, 7:62, 8:78, 9:240}`, rank mass, live stock and deficit.
- Global profile: [PROFILE.json](PROFILE.json).

**Screened variants** (pattern MILP estimates of the root, same search code):

| Order key | Estimated root |
| --- | --- |
| 4·stage + replica (PR2530) | 0.00171373562 |
| 3·stage + replica | 0.00169750271 |
| 5·stage + replica | 0.00171362710 |
| 6·stage + replica | 0.00171291702 |
| 8·stage + replica | 0.00170301749 |
| 4·stage + replica + 4·[stage ≥ 1] (**this package**) | **0.00171403230** |
| 4·stage + replica + 8·[stage ≥ 1] | 0.00171365295 |
| 4·stage + replica + 16·[stage ≥ 1] | 0.00168480138 |

The pattern LP of PR2387/PR2442 (thakrarsagar) caps any whole-helper fill of these words at b < 0.0017142284, whatever the order.

## Reproduction

```sh
python3 -B research/source-partner-repack/verify.py            # bounded: build, literal owners, controls, bindings
python3 -B research/source-partner-repack/full_replay.py --work /fresh/absolute/dir
```

`build.py` runs PR2530's unchanged `build.py`, including its own word regeneration and checks. It then substitutes `evidence/repack-order.json` (checked to be the shifted-diagonal permutation of the same 666 calls) and `evidence/repack-fill.json.gz`, and re-runs the package's own `reconstruct.py` and `lift_parent.py`.

`full_replay.py` runs the same stages as PR2530's: retained parent, natives, rebind, discovery, strict global admission, geometry controls, exact outer ledger, independent balance and the nineteen outer evidence replays. It can reuse a completed retained-parent directory and native directories, each status- and hash-checked; the defaults are fresh.

Receipts are in `receipts/`: the full replay and its stages, and the bounded run.

## Open next questions

- **Can other order families close the remaining gap?** This package is about 2e-7 below the window-free LP cap of 0.0017142284. Non-uniform shifts per stage and late-order variants are untested.
- **Can the remaining 124 empty rank-8 bins be filled?** A large-neighbourhood exact repack of the shifted-order fill found no gain in a short run.

## Scope

This is a conditional finite construction, exactly as PR2530. These obligations remain: all-size compiler, common-label/mutable-source realization, whole-call hosting, precision/tape, exact recovery, analytic transfer, the PR559 recurrence correction and PR589 bit H1–H5. No unconditional theorem, independent human review or global packing optimality is claimed.

## Credits

- PR2530 (zxv): source-partner lifetimes, the diagonal order, the pattern search and realization code, and the whole package this one builds on.
- PR2462, PR2447, PR2435 and the T74 line (Jeremy Kothe).
- PR2436 (tekuuu).
- PR2322 (Vlado Vojdanovski).
- PR2226 (Cinna Davis).
- PR2387, PR2442 and PR2466 (thakrarsagar): the pattern-LP ceiling and owner-optimality method.
- Everyone credited in the source package's READMEs and notices.

New here: the shifted order, the screening, the resulting fill and this wrapper, by Rohan Arun with AI assistance (Claude). Apache-2.0.
