# Fully priced 205-pair R439 helper-sharing wrap

**Local bit-word construction: 6,231 fewer ADD gates; both inherited precision guards pass. No selected-supplier or κ claim.**

This package answers the explicit open question from [PR1782](https://github.com/CrocSwap/integer-mult-bounds/pull/1782): bill the semantic-H2-admitted helper-sharing wrapper. On the pinned R439 word, the fixed seed-42 matching of 205 disjoint helper pairs reduces the complete ADD invoice from 24,305 to 18,074 while preserving the full F2 boundary and paid profile. The official record exporter agrees with the literal envelope recurrence, and the local and nine-stage bills remain at 95/104 and 180/192 bits.

## Exact object and scope

The object is the pinned selected R439 word `bitE8mut-p111-tuned` at `v=111`, `R=439`. Its D section has 111 frame-zero gates and 18,085 source ADDs. The inherited PR848 census has 430 non-retained helper operands; its deterministic seed-42 greedy matching contains 205 disjoint ordered pairs. This package reuses that exact matching and does not claim it is optimal.

For each selected pair `(a,b)`, the circuit prepares `a <- a+b` before D, substitutes `a` by `a+b` in every dependent D source row, then restores `a <- a+b` after the D body. All 410 one-source preparation/restoration ADDs are charged. The resulting D has 521 gates. The semantic H2/K contract from PR1194 admits this helper-writing word; the inherited gate-local `H2_D_frame0_targets_from_helpers` and `K_equals_D` flags remain false.

## Exact result

| Quantity | Pinned word | Wrapped word |
|---|---:|---:|
| Complete ADD gates | 24,305 | **18,074** |
| Net ADD saving |  | **6,231** |
| D source ADDs | 18,085 | 11,854 |
| D gates | 111 | 521 |
| Forward envelope `F` | 49,347 | 75,381 |
| Reverse envelope `B` | 1,113,070 | 1,196,402 |
| Local payload bits | 93 / 104 | **95 / 104** |
| Nine-stage bits | 177 / 192 | **180 / 192** |
| COPY / ERASE records | 9 / 9 | 9 / 9 |

The local bill uses `64 F^3 B^2`; the nine-stage bill uses `2^18 F^5 B^4`. Both the literal stream calculation and the repository's `export_records.py` produce the same ADD count, `F`, `B`, and local payload precision. The paid profile is unchanged:

```text
{1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}
rank mass = 5129
```

The full 661-column map is replayed forward and backward. The D boundary is unchanged, the chronological cut state and register frame paths are identical, and the semantic `N` equals the raw K derived from A/scatter/B. The candidate has exactly the two inherited flag failures listed above.

## Predecessors and overlap

PR1782 (`1cfe5e10ce38b04209699c1a6b0e62b87e21833f`) established the H2-sem admission and left this complete integer invoice open; this package supplies that priced construction. The current complete overlap snapshot covered 435 open PRs and 877 Discussion records, fetched at 23:03:49Z and 23:05:44Z. The task terms produced no current PR or Discussion match. A live open-PR search also found no same-word construction. Its nearest result, [PR2033](https://github.com/CrocSwap/integer-mult-bounds/pull/2033), studies a fixed pair on a different PR1062 star-composed word and reports no saving there. This package takes the one-word invoice left open by PR1782; it does not repeat PR2033's word or transfer its result.

## Reproduce

From the repository root:

```sh
python3 -I -B research/r439-copyshare-priced-wrap-seedaaa3e40/verify.py
python3 scripts/research_package.py --package research/r439-copyshare-priced-wrap-seedaaa3e40 --check-only
```

The verifier rebuilds the fixed matching and wrapper from pinned predecessor code, checks source hashes, replays both directions, compares the paid profile, verifies the full ADD and precision invoices against the official record exporter, and runs five negative controls. Expected final line:

```text
PASS_R439_COPYSHARE_PRICED_WRAP pairs=205 ADDs=24305->18074 saved=6231 F=49347->75381 B=1113070->1196402 guards=95/104,180/192 profile_mass=5129 controls=5 no_kappa
```

`CERTIFICATE.json` holds the exact census, exporter record hashes, boundary results, paid profile and rejected controls. `SOURCES.json` pins the source word, semantic admission package, bound routines, exporter and base.

## Limits

This is a source-bound construction for one finite R439 word. It is not a proof that the seed-42 matching is optimal, a reusable all-size compiler, a selected bit-supplier admission, or an integer-multiplication exponent improvement. The selected bit side remains nonbinding; hosting, outer assembly and κ are outside this package. The replacement H2-sem argument is inherited from PR1194 and PR1782 rather than reproved here.

## Open next questions

- **Can this wrapper be admitted as a complete supplier candidate under source realization and outer assembly?** That would connect the 6,231 local ADD saving to the conditional multiplication bound. A feasible first step is to build a source-bound supplier manifest and run the existing all-size compiler and hosting checks against the exact candidate. Blocked by the missing source-realization, tape and outer analytic obligations; this package supplies only the local priced word.

## Credit

Credit Aaron Wang's PR1782 (`1cfe5e10ce38b04209699c1a6b0e62b87e21833f`) for the semantic H2/K admission, PR1194 for the semantic D contract and chronological bridge, and the PR848 lineage for the helper-pair census and seed-42 matching. PR2033's fixed-pair result concerns a different PR1062 star-composed word and is not reused as evidence here. The source R439 word and inherited review lineage retain their original attribution.

Prepared by Cinna Davis with substantial OpenAI Codex assistance in scoping, construction, exact invoice verification and packaging. This package's new work is Apache-2.0; inherited source files remain pinned and unmodified.
