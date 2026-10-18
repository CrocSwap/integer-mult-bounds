# Priced H2-sem admission of the PR848 copy-path helper-sharing wraps

**Priced finite invoice under the H2-sem replacement interface; no new κ.** The
selected frontier, selected bit supplier and `upstream/` are unchanged. The bit
side does not bind.

PR848 priced helper-temp sharing on the selected R439 word as an arithmetic
source-read upper bound and rejected it under gate-local H2. PR1194 supplies the
replacement contract H2-sem. Open PR1782 checks that the wraps satisfy H2-sem,
but leaves F/B envelopes and the paid profile uncomputed. This package completes
that invoice.

## Result

| word | ADDs | D ADDs | F | B | local / nine-stage bits | paid profile |
|---|---:|---:|---:|---:|---|---|
| baseline PR589 | 24,305 | 18,085 | 49,347 | 1,113,070 | 93 / 177 | `{1:1323,…,7:19}` mass 5129 |
| single pair 277→434 | **24,240** (−65) | 18,020 | 50,535 | 1,113,070 | 94 / 177 | unchanged |
| seed-42 matching (205 pairs) | **18,074** (−6,231) | 11,854 | 75,381 | 1,196,402 | 95 / 180 | unchanged |

Both wraps keep the complete dirty F2 boundary, semantic N equal to the baseline
N, and the inherited 104/192-bit guards. Syntactic H2 and `K_equals_D` fail
exactly on the wraps; H1/H3/H4/H5 and U/J/C remain true. Frame paths and nine
rank-7 COPY ranks are unchanged, so the paid recursive profile is unchanged.

## Reproduce

```sh
python3 -I -B research/h2sem-copyshare-priced/verify.py
python3 -I -O -B research/h2sem-copyshare-priced/verify.py
python3.12 scripts/research_package.py --package research/h2sem-copyshare-priced --check-only
python3.12 scripts/research_package.py --package research/h2sem-copyshare-priced
```

Expected:

```text
PASS_H2SEM_COPYSHARE_PRICED single=277->434 adds=24305->24240 matching_pairs=205 adds=24305->18074 profile_mass=5129 columns=661 controls=7 no_new_kappa
```

The verifier recomputes the PR848 census, builds both wraps, checks H2-sem shape
and all 661 D columns, replays the full literal COPY/ERASE stream both ways,
recomputes F/B and precision guards, extracts the paid profile from frame-path
climbs plus COPY ranks via the pinned owner checker, and rejects seven controls
(unrestored helper, wrong restore, target→helper feedback, source read in D,
partial matching unrestored, mutated body N, and the +2 target-temp positive).

## Scope

- **No new κ.** Paid profile unchanged; bit supplier nonbinding.
- Native C++/Boost, hosted emission, all-size compiler, tape/rounding and
  analytic transfer are not run.
- Matching optimality is not claimed. Intermediate envelopes rise even as ADD
  counts fall; that trade-off is recorded, not optimized away.
- Complementary to PR1782 (interface admission without this invoice) and PR848
  (H2 barrier). Does not vendor their executables.

## Open next questions

1. **Can a different matching lower F while keeping most of the ADD saving?**
   The seed-42 matching raises F from 49,347 to 75,381. A first step is to
   re-score pairs by a joint (ADD, F) objective on a frozen shortlist. Blocker:
   no favorable completed (ADD, F, B) point is known.
2. **Does the single-pair wrap compose with an already H2-sem-legal star D?**
   First splice pair 277→434 onto the PR1062/PR1194 candidate and recompute the
   full invoice. Blocker: maintained acceptance of H2-sem on the composed word.

## Credit

Credit **Aaron Wang / PR848** (pair census, greedy matching, helper-temp wrap),
**woklerx / PR1194** (H2-sem contract), **navinor / PR1782** (interface admission
that left pricing open), **DreamingOfClouds / PR589** and **eumemic / PR555**
(the R439 word and checker lineage). Prepared by Wentao Li with substantial AI
assistance. Apache-2.0. No independent human review or full multiplication
theorem is claimed.
