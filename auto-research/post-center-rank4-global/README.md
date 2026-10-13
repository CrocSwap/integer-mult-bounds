# Rank-four post-center kernels: a global κ delta from PR531

**Conditional global saving: `κ = 0.001584931111785787`.** This is
**4.42560686% above PR531** (`0.001517760977820331`) and **3.98391577% above
PR533**. The package is named `integer_mult_round21_rank4_delta` and contains
an incremental construction and its component evidence, using the scientifically
unchanged PR531 package as its baseline.

| Quantity | Exact certified lower endpoint |
|---|---:|
| New complex supplier, rank-four kernel construction | `b = 0.001589991533606044174031` |
| Adopted PR510 bit supplier | `c = 0.001587447106092548137108` |
| Combined conditional global saving | **`κ = 0.001584931111785787`** |
| Control: new complex supplier with the former PR493 bit supplier | `κ = 0.001562995248531632` |

The new complex supplier exceeds the old bit endpoint. The bit side now binds,
so the final composition adopts PR510's already published nine-stage R480 bit
supplier. Its exact rational endpoint is
`396861776523137034277 / 250000000000000000000000`. The PR493 control records
the gain available without this dependency change. The final κ is also
2.67486649% above the earlier post-center-only checkpoint.

## New construction and adopted components

The new contribution is by **icekylinx with GPT-6 Astra assistance**. It
composes post-center dirty compensation with larger response kernels:

1. Helpers that are untouched by the source prefix and center cut still contain
   exactly their initial dirt at the start of delivery. Their compensation can
   therefore be performed there, after the center cut.
2. The 112 ordinary-M helpers form 14 disjoint groups of eight. Within each
   group, four response columns span the other four, and all eight first native
   frames contain a common frame of rank four.
3. Execute the retained gauge compensations first. Then inject each pivot into
   its donors at the common rank-four frame. A donor may itself have been gauged:
   the earlier compensation reads its original dirt, and the later injection
   cancels the pivot's response without changing the donor's initial column.

The scalar relations are exact, the frame containments are paid, and the new
source/helper operations are included in full-frame inverse cleanup. The word
retains 112 ports, 504 helpers, local dimension 9, and the existing center cut.
The original whole-call owner intervals remain in force.

The entrance inventory is **40 rank-one kernel pivots, 112 rank-one gauges,
and 56 rank-four pivots**, for total entrance rank **376**. Residual widths are
**56 × 5, 152 × 8, and 296 × 9**. The coalesced local paid profile is

```text
rank       1    2    3    4   5   6  8
count   2208  728  184  280  56  56  8
```

Its rank mass is **6016**. The global evidence includes actual whole-residual
owners, the paid invoice, and exact outer assembly; the reported κ is not
inferred from the local inventory alone.

PR531 supplies the SAME504 scalar architecture, source/target geometry,
coalescing construction, and unchanged certificates. PR510 supplies the bit
rate and its conditional interfaces. **PR510's bit improvement is adopted and
credited; it is not presented as a new bit construction here.** No cold bit
replay was performed for this delta. PR533 is a numerical comparison source.

## Fast incremental replay

Provide the baseline package from PR531 at final head
`e07a8a3f9f79c22113398a0c5dbbc7601f489b3e`. Its relevant scientific files match
the original Round20 baseline pins. The baseline argument is the package
directory `research/direct-delivery504-global`, not the repository root.

```sh
python -B replay_delta.py \
  --baseline /path/research/direct-delivery504-global \
  --work /tmp/rank4-check
```

Use a fresh work directory. The default mode reuses the completed phase evidence
bound to the packaged word and pinned baseline. The default replay uses the Python standard library. `--delta-phases` also
requires NumPy. Optional flags are:

- `--rebuild-local`: reconstruct the changed local word.
- `--delta-phases`: repeat the targeted phase check for the changed frame pairs.

For example:

```sh
python -B replay_delta.py \
  --baseline /path/research/direct-delivery504-global \
  --work /tmp/rank4-check-rebuild \
  --rebuild-local --delta-phases
```

## Checks completed and their scope

The component checks completed before packaging include exact scalar/frame
replay (**2.15 seconds**), the targeted phase delta (**2.29 seconds**), and
the independent check (**6.88 seconds**). Phase coverage consists of **126 new
frame pairs, 2801 pairs reused from bound baseline evidence, and 224 endpoint
adapters**. The new global owner/invoice checks and the combined exact outer
assembly passed. A separate small exact adjoint audit checks all 56 rank-four
response relations and every gauge-to-kernel-to-native frame containment.

These timings describe completed component runs on the preparation machine.
The assembled `replay_delta.py` default wrapper passed end to end in
**22.71 seconds**, including all dependency bindings, the small rank-four
adjoint check, changed scalar/frame replay, actual owner reconstruction and
admission, fresh finite invoice, and both moments plus the 47 outer constraints.
See `evidence/fast-replay/RESULT.json`. The optional reconstruction and phase
flags have separate component evidence; they were not repeated by this wrapper run. The default fast mode also does not imply that predecessor
phase certificates or PR510's full bit pipeline were freshly rerun.

## Conditional scope and sources

This is a **finite conditional global witness**. It retains the all-size
compiler, common-label/mutable-basis and target-label realization, normalized
Lemma A realization, whole-call correlated-helper hosting, compressed-window,
restored-work, common-grid/tape, precision, row, and analytic transfer contracts.
The included PR510 carryover note explains why source-register writes use the
same role-independent address pullback at nine stages. It does not replace
those all-size assumptions with a finite scalar replay. No unconditional
multiplication theorem or Lean formalization is asserted.

- [PR531: baseline SAME504 global construction](https://github.com/CrocSwap/integer-mult-bounds/pull/531).
- [PR510: adopted R480 nine-stage bit supplier](https://github.com/CrocSwap/integer-mult-bounds/pull/510), pinned to `64edee18af02aab0c1696b677a0287dd0146381b`.
- [PR510 pinned README and declared interfaces](https://github.com/DreamingOfClouds/integer-mult-bounds/blob/64edee18af02aab0c1696b677a0287dd0146381b/research/e8-r480-nine-stage/README.md).
- [PR493: former bit supplier and the mutable-source word](https://github.com/CrocSwap/integer-mult-bounds/pull/493).
- [PR484: attributed gauge/kernel primitives](https://github.com/CrocSwap/integer-mult-bounds/pull/484).
- [PR472: common-label and whole-call realization argument](https://github.com/CrocSwap/integer-mult-bounds/pull/472).
- [PR533: latest numerical comparison](https://github.com/CrocSwap/integer-mult-bounds/pull/533).

The original PR531 and PR510 notices are retained separately. See `NOTICE.md`
and the packaged proof/evidence files for the contribution boundary and pins.

## Submission validation

The optional local reconstruction and changed-phase replay passed on Python
3.14.8 with NumPy 2.3.5 in 15.68 seconds. The intermediate checkpoint phase
delta was also freshly checked against the merged #531 baseline (194 edges),
followed by the final 126-edge delta. Independent emitted-program and all 21
residual-wrapper checks passed. See `LOCAL-VALIDATION.json`.

The submission starts from main at `f19cb621be2caf3a7291a37c343c1c55afe935e0`.
Logs remain outside the committed package and its manifest.

## Cross-version reconstruction

The word comparison excludes only `local_entropy_before` and
`local_entropy_after` inside `report.frame_coalescing`. These floating
diagnostics may round differently across Python versions. Every instruction,
coefficient, frame, exact rank and move count still must match. The rational
moment and assembly checks do not consume these diagnostics. Python 3.11.17
reconstruction passed after this adjustment; the previous Python 3.14 CI
passed the full changed-phase and wrapper workflow.
