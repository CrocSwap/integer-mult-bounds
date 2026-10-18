# Exact block-4 circuit and whole-word cost

## Fixed target and replacement

The baseline is the canonical word from `research/e8-bit-r420/data/plan-l3.json`
and the PR543 R420 generator at base
`bce54fb3f895cbe5cd4c0eb477c3afeed100190f`. It reconstructs with the published
2,000 randomized-LU samples per block and has canonical decoded hash
`e597e3885c0a8daa262afa5985ee2930443329126aece76d33159d81882bdcc2`.

Block index 4 is the twelve-input transform at frame 546, occupying the
half-open baseline interval `B[313:371]`. The target rows in the input basis
and exact 51-operation replacement are in `search-certificate.json`. Each
local operation `(a,b)` is the transvection `wire[a] ^= wire[b]`. Starting
from the twelve unit vectors, replaying these operations places each target
row on the certified `output_to_wire` register. The output assignment differs
from the baseline assignment; the generator propagates that assignment to the
later D6 needer gates. Seven complete register frame paths consequently
change. The candidate word records those changed consumers and regenerates C
as the literal reverse of all source/helper writes in A and B.

The operation list itself is not claimed to preserve the old value on each
physical wire. The proof obligation is the complete word's exact endpoint:
the independent R420 checker replays all 660 symbolic columns at once,
including arbitrary dirty helper contents. It confirms H1-H5 and the
decomposed `U`, `J=I`, `K=D`, and `C=U^-1` conclusions for the regenerated
candidate.

## Complete invoice

Seven fewer forward block operations require seven fewer literal inverse
cleanup operations. The complete local count is therefore 14 scalar ADDs
lower, not seven:

| Quantity | Baseline | Candidate |
|---|---:|---:|
| Block 4 XOR operations at frame 546 | 58 | 51 |
| Phase-B gate records | 837 | 830 |
| Literal cleanup C records | 2,661 | 2,654 |
| Scalar ADDs including D, A, B, scatter, and C | 26,916 | 26,902 |
| Exported records | 29,874 | 29,860 |
| Helpers / retained totals | 420 / 9 | 420 / 9 |
| Local paid rank mass | 5,112 | 5,112 |

The exporter and native cohort checks recompute costs from the full candidate.
They confirm the unchanged paid histogram
`{1:1320, 2:1440, 4:60, 5:120, 8:9}` and the 100-bit local payload bound at
five, nine, and eleven stages. The nine-stage whole-owner audit hosts all
120,960 residuals without banks; the eleven-stage audit hosts all 36,960
residuals without banks. Thus the changed routes and their source access,
frame moves, copies, and restoration are included in the actual replay.

The R420 bit values remain exactly
`413456747036699736067/250000000000000000000000` (nine stages) and
`82015816228313440961/50000000000000000000000` (eleven stages). No new κ
follows: both are the bit certificates for this historical R420 package, and
the candidate preserves their paid profile and payload charges. The current
selected record at the pinned base is separate and unchanged.

## Bounded search

The only varied optimization is block 4's randomized pivoted-LU circuit. The
baseline replays the plan with 2,000 draws for each of the ten blocks. The
candidate repeats that baseline with the same plan and seeds, except block 4
gets exactly 20,000 draws. Its RNG seed is 28 under the upstream rule
`7 * block_index`; the outer plan seed is 0 and the plan succeeds without a
retry. The optimizer retains its minimum cancellation-free cost, then the
full word is checked. Search ends after the 20,000th draw. No exhaustive
enumeration or gate-minimality claim is made.

## Reproduction and limits

Run `python3 -I -B research/r420-block4-resynthesis/verify.py` for source-pin
checks, deterministic search regeneration, exact artifact comparison, full
symbolic endpoint replay, and the inherited negative controls. `VALIDATION.json`
records the separate native and hosted replay outputs. In particular, a finite
replay does not prove the all-size compiler, physical realization, analytic
transfer, or complete multiplication theorem.
