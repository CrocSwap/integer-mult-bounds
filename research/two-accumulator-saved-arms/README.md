# Two accumulators: eight exact rewrites and their complete cost

This package gives eight explicit two-accumulator rewrites of the selected
seven-slot R480 local word. The second accumulator keeps one pair sum while
the first accumulator completes a packet. All 256 subsets pass the exact
local scalar, frame, entrance, and helper-cone checks.

The complete cost gives a negative result for this method. Each rewrite
changes one helper width from 7 to 9. A whole-helper packing inequality then
shows that **every nonempty use of these rewrites has a smaller complex root
than the unchanged-word optimum in PR1129**. The theorem permits different
subsets in different calls, every positive replica count, and every whole-helper
owner assignment with the retained capacity stock. It does not assume that
the current owner map stays fixed.

This is a construction and a scoped obstruction. It is not an impossibility
theorem for all two-accumulator programs. Arbitrary new partitions, rational
changes of basis, other schedules and frames, mixed encodings of several
packets, and the other eight packet roles remain outside the proved family.
The broader question in the initial research claim remains open.

The exact base is `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. At that base,
the selected PR1094 result is `kappa = 0.001672660197076918`. The stronger
applicable comparison is PR1129 at
`a007dc2e1cc7ae7e8f7ec1343e8883fe43259f21`: its unchanged-word whole-helper
optimum gives `kappa = 0.001674097969905390` under the inherited admission
and outer recipe. This package does not change the selected result.

## Reproduce

Use Python 3.10 or newer with the standard library. Run from the repository
root. The command takes several minutes and writes its receipt outside the
package.

```sh
python3 -I -B research/two-accumulator-saved-arms/verify.py --output /tmp/two-accumulator-check.json
```

Expected last line:

```text
PASS_TWO_ACCUMULATOR_SAVED_ARM_FAMILY
```

The command checks all 256 subsets on all 704 local input columns in both
orientations. It checks the all-eight word with eight extra independent
private centre inputs, for 712 columns. It checks the 1,163 legal bin patterns
by enumeration and an independent fill recurrence. Exact rational intervals
certify the supporting moment inequalities at the baseline root. Integer
partial sums check the two majorization relations used in the proof.
Three negative controls remove a required dirty-column correction, restore
an unpaid low helper end, and request a mask outside the declared family.

The fast mathematical check is:

```sh
python3 -I -B research/two-accumulator-saved-arms/owner_bound.py
```

Its status is `PASS_ALL_REPLICA_SAVED_ARM_OBSTRUCTION`.

The source binding and the feasible raw CF0 frame control have separate
short commands:

```sh
python3 -I -B research/two-accumulator-saved-arms/check_sources.py
python3 -I -B research/two-accumulator-saved-arms/frame_control.py
```

The frame control reproduces a feasible order after 57,478 states, then
checks the order with explicit binary spans. It is a local positive control,
not a complete supplier. The registered `VERIFY.json` runs these two checks
and the complete family check with Python 3.12.

To produce the all-eight local word:

```sh
python3 -I -B research/two-accumulator-saved-arms/build.py --mask 255 --output /tmp/two-accumulator-word.json.gz
```

The decompressed canonical JSON SHA256 is
`25e6b6b9de424b83795a4050ce065130d34826a9f217b4b61f2d591d3383dad2`.
Compression-container bytes do not define mathematical equality.

## The paid change

Let `E` and `O` count the even and odd selected recipe groups in one call.
Each is between 0 and 4. The local profile and width changes are

```text
delta H1 = -2 E
delta H2 =  2 E + O
delta local rank mass = 2(E+O)
delta width-7 count = -(E+O)
delta width-9 count =  (E+O)
```

All other local ranks, helper counts, centre paths, and data endpoints stay
fixed. The all-eight profile is
`{1:2404,2:430,3:432,4:142,5:82,8:8}`, with mass 5602. Its helper widths are
`{4:56,5:32,7:22,8:122,9:248}`. The total deficit remains 320 per replica.

It is not valid to remove two arbitrary rank-one idle children for each
rewrite. The new width-9 helpers change the legal bin fills. The exact dual
forces the residual moment to increase by at least
`(22/37) H1 - (2/37) H48` per switched call. After the local change, both
recipe types have a strictly positive complete moment increment. See
[PROOF.md](PROOF.md).

## Evidence and limits

`RECIPES.json` contains the full gate replacements, source-gate pins,
frames, and cleanup corrections. `build.py` applies these data without a
search. The independent local checker does not import this builder.
`evidence/` retains the completed check receipts and the native local
admission receipts. `NATIVE-REPLAY.md` gives the native replay commands and
their source pins. Native phase and wrapper checks cover the all-eight
word. The subset matrix checks have the separate coverage stated above.

No new global owner map or physical operator stream is claimed. The cost
obstruction already holds in a relaxation that removes owner chronology
and physical matching constraints. The unchanged zero-switch construction
uses the existing PR1129 owner map. Its earlier admission receipts are
source-bound predecessor evidence, not a new cold replay in this package.

The local checks do not prove the all-size multiplication theorem. The
all-size/compiler, common-label/mutable-source, whole-call hosting,
precision/tape, exact-recovery, analytic-transfer, and bit H1-H5 obligations
remain inherited. A finite native check does not discharge these obligations.

## Open next questions

1. Can another two-accumulator schedule preserve a width-7 endpoint or
   produce a better rank distribution? This can change the dual penalty.
   Start with a complete dirty-input identity and new endpoint bill for one
   selected packet. The present proof fixes the eight recipes and does not
   constrain that synthesis problem.
2. Can mixed encodings across several packets use fewer paid versions?
   Such an encoding can leave the independent-recipe class. Start with its
   exact arbitrary-input map and reader interface. A clean-input identity
   alone does not resolve the restoration and source-access costs.
3. Do the other eight correctly rebound packet roles admit a useful
   reconstruction? Their selected carriers differ from the raw PR1238
   numbering. Start from the binding data described in `RESEARCH-NOTES.md`.
   The missing step is an exact construction or an all-order lower bound.

Prepared by Ali Romman with substantial OpenAI Codex assistance. The license
is Apache-2.0. See [NOTICE.md](NOTICE.md) for predecessor credit.
