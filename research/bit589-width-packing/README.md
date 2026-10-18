# Width packing of the selected PR589 bit hosting

**Status: research note and scoped negative result (bit supplier). No new κ; the selected result is
unchanged and complex-bound.**
Track 00–19 (bit supplier), assignment seed 16 (OS CSPRNG via Python `secrets`).
Base commit `2921874911956718fcaaaf9396fe8267b3cfa9f0`.

## Question

The selected bit supplier is DreamingOfClouds' PR589 on eumemic's PR555, with
c = 0.001733427039589844234749. It hosts all 3,951 width-8 helper residuals per replica in the
nine-stage idle windows, with no banks, yet its idle remainders are fragmented:
`{2:435, 4:444, 6:444, 7:666, 42:9}` per replica. Can re-hosting improve the bit profile, and
what would a different helper width be worth?

## Findings

1. **Slot model (exact, unique).** The nine slot indices of the frozen selection hold one pair's
   222 families each. Their capacities are `{14, 7, 28, 7, 42, 7, 42, 28, 14}`, so per replica there
   are 666 slots of capacity 7, 444 of 14, 444 of 28 and 444 of 42. The total, 41,958 coordinates,
   equals the coverage-identity pending capacity `2v·42 + 6v·49`. These are the template's one-,
   two-, four- and six-level windows at 7 coordinates per level, the same window structure the
   complex template has at 8 per level. The deficit satisfies `live − 63·calls = 10,272`.
2. **Width-8 re-hosting cannot help (certified).**
   - 8 divides no capacity, so every slot keeps a remainder of at least 7, 6, 4 or 2. Every
     no-bank placement therefore has exactly one idle child per slot.
   - Only 45 width-8 units of slack exist per replica (1,440 in total).
   - At c* = c0 + 10⁻²⁴, the per-unit cost of a fully idle capacity-42 slot is certified strictly
     below every other (capacity, unused units) option. The runner-up is (42, 4), behind by a
     certified 0.0026 in units of g(r) = r(64/r)^c.
   - So the selected placement, with 9 fully idle 42-slots per replica, minimizes the moment.
     No re-hosting raises the bit endpoint on the 10⁻²⁴ grid, and the +12.3%
     "free-concentration" relaxation is unreachable at width 8.
3. **Width-7 residuals fill every slot exactly.** A helper of width 7 (a hyperplane end or a
   rank-one entrance) leaves no remainder in a 7k slot. Converting all 439 helpers per call leaves
   2,043 units of slack per replica. The majorization optimum then leaves only `{42: 340, 21: 1}`
   idle children per replica, against 1,998 now. The bit c rises by +17.4% to +23.4%.
4. **Partial conversion already pays.** Converting k helper indices in every call, with their
   width-7 residuals filling empty 7-slots and the freed width-8 slack going to fully idle
   42-slots, gives the table below.
5. **Window timing: supporting evidence only.** The 7-slots are the template's one-level windows.
   In the selected complex T37 hosting on the same nine-stage template, all six one-level windows
   (children 1, 3, 5, 7, 9 and 11) are completely hosted: 198,912 coordinates, 0 idle. That
   suggests one-level windows admit hosted residuals, but the bit-side timing check is not done.

## Exact prices

Each bit endpoint is certified by both pinned engines, with the inherited bad-residue surcharge:
the moment is below one at c and above one at c + 10⁻²⁴. The κ cap is the selected T37 outer
witness with the bit side binding: 7 bootstrap steps, all 47 inequalities, and κ + 10⁻¹⁸
rejected. The selected κ stays 0.001661960547713947 because the complex side binds.

| Scenario (one unit removed from one local child per converted helper) | Bit c | Gain | Bit-bound κ cap |
|---|---|---:|---|
| selected PR589 profile (reproduced exactly) | 0.0017334270395898442 | — | 0.001730427469823602 |
| 1 helper per call width 7, rank-one child removed / largest child trimmed | 0.0017348463 / 0.0017346035 | +0.082% / +0.068% | 0.001731841784869670 / 0.001731599905939462 |
| 10 helpers per call | 0.0017482911 / 0.0017458293 | +0.857% / +0.715% | 0.001745239939229085 / 0.001742786661941923 |
| 37 helpers per call | 0.0017896275 / 0.0017805126 | +3.24% / +2.72% | 0.001786430419444784 / 0.001777348059220582 |
| 74 helpers per call (all 666 empty 7-slots used) | 0.0018497057 / 0.0018312021 | +6.71% / +5.64% | 0.001846290613254756 / 0.001827854925395469 |
| all 439 helpers width 7, slot-exact optimum | 0.0021391622 / 0.0020357077 | +23.41% / +17.44% | 0.002134595909222345 / 0.002031571973028065 |
| relaxation: width-8 idle mass in rank-42 children | 0.0019472877 | +12.34% | 0.001943503128837276 |

The bracket gives two bounds for a conversion that removes exactly one unit from one local child.
Removing a rank-one child gives the largest gain and trimming the largest children gives the
smallest, because g is concave. The partial rows use one constructive slot-exact placement, so
for those k they are achievable values in the slot model, not optima. The last row ignores the
slot structure that finding 2 proves binding.

## What this means

- These numbers are **bit headroom**. They give the κ that the selected outer recipe would allow if
  the complex side improved past the bit side. Today's bit cap, 0.001730427469823602, matches the
  value recorded in PR974.
- No hosting or owner work on the current bit word can raise c. The lever is helper width.
  Converting one helper index in every call, with its residuals in empty 7-slots, is worth about
  +0.07% to +0.08% bit c, more than the whole PR589 tuning step (+0.0216%).
- Width-7 mechanisms already exist on the complex side: hyperplane-ended helpers (PR601, PR593)
  and width-seven entrance promotions (PR569). Their bit analogues are the natural next
  construction targets. The first obstruction is the bit word's literal reverse cleanup at the
  full frame (interface hypothesis H4): a hyperplane end needs that helper's cleanup retimed.

## Remaining obligations (none attempted)

1. Construct width-7 bit helpers, either as hyperplane ends with cleanup retiming or as rank-one
   entrances with kernels. Keep H1–H5 or state a replacement interface, with exact scalar and
   dirty-state checks.
2. Check window timing: the one-level bit windows must admit the converted residuals, with owner
   inactivity and one helper per family per call, through the PR510/PR463 hosting audit.
3. Re-emit the hosted template and rerun the hosted audit, the finite invoice (prefix bits, row
   coefficient) and the bit assembly.
4. A real conversion may change more than one unit of one child, which the bracket does not cover.

## Scope and limits

- The slot model comes from the frozen selection and the pinned record. It is the unique solution
  consistent with the observed remainders and the coverage capacity. Findings 2–4 do not impose
  window timing or per-call ownership rules; the baseline placement satisfies them as selected.
- Finding 2 compares no-bank placements only. Banks add live stock without free coordinates.
- All inherited assumptions remain: all-size compilation, common-label/mutable-source
  realization, whole-call hosting, precision/tape, analytic transfer, bit H1–H5 and the bit
  bad-residue surcharge, which every price above keeps. This is not a construction and not a
  formal proof of the multiplication theorem.

## Reproduce

```sh
make bit589-width-packing-verify
```

The same check without make:

```sh
python3 -B research/bit589-width-packing/verify.py --work /new/empty/dir
python3 -B -m unittest discover -s research/bit589-width-packing -p test_package.py -v
```

The expected last line is `PASS_BIT589_WIDTH_PACKING_REPLAY`, followed by 6 tests OK. It runs in
about 3 s on standard-library Python 3.10+ with no network.

- `verify.py` regenerates `RESULT.json` and requires it to equal the committed file.
- It checks the T37 one-level-window evidence from the pinned T37 archive, read in memory.
- It runs six negative controls:

| Control | Rejected because |
|---|---|
| C1 one residual moved between slot indices | stage and pattern totals disagree |
| C2 a capacity divisible by 8 | the per-unit argument refuses exact width-8 fits |
| C3 corrupted record pin | digest mismatch |
| C4 bit endpoint c + 10⁻²⁴ | both engines exceed one, surcharge included |
| C5 a width-7 profile that drops the freed coordinates | rank mass changes |
| C6 more converted residuals than empty 7-slots | the constructive placement refuses |

## Sources and pins

See [`SOURCES.json`](SOURCES.json).

- **Bit record.** `research/e8-bit-p111-tuned/tune/EXPECTED.json` (`b9f0e5ca…`). This digest is
  the `package:inputs/PR589-EXPECTED.json` input of the selected `ASSEMBLY.json`.
- **Hosting selection.** `research/e8-bit-p111-tuned/data/selection9-p111.json` (`4ab1ed45…`).
- **Engines.** The pinned engines recorded in the selected assembly.
- **Outer witness.** Transcribed from the selected T37 archive.
- **Supporting evidence.** The selected T37 hosted template (payload `956e0c0e…`).

## Credit

- DreamingOfClouds: the PR589 word and the PR510/PR463 nine-stage bit template.
- eumemic: the PR555 punctured unit and selection.
- DaysSky: the idle-axis hosting of PR442.
- Jeremy Kothe: hyperplane-ended helpers (PR601).
- Dominik Scholz: width-seven complex providers (PR569, `research/larger-gain`).
- avirazza: the bit cap value of PR974.
- Prepared by Sagar Thakrar (thakrarsagar) with substantial AI assistance from Claude
  (Anthropic) via Claude Code. New material is Apache-2.0.
