# H2-sem matching F invoice: seed-7 dominates seed-42

**Priced finite invoice under the H2-sem replacement interface; no new κ.**
Answers open question 1 of
[CrocSwap/integer-mult-bounds#1805](https://github.com/CrocSwap/integer-mult-bounds/pull/1805):
can a different disjoint helper-sharing matching lower forward envelope `F`
while keeping most of the ADD saving?

Yes. The same PR848 ADD-greedy rule with shuffle seed **7** (instead of the
published seed **42**) produces a disjoint matching that **strictly dominates**
the #1805 seed-42 invoice on ADD count, `F`, and `B`:

| word | pairs | ADDs | D ADDs | F | B | local / nine-stage |
|---|---:|---:|---:|---:|---:|---:|
| baseline PR589 | — | 24,305 | 18,085 | 49,347 | 1,113,070 | 93 / 177 |
| seed-42 matching (#1805) | 205 | **18,074** | 11,854 | **75,381** | 1,196,402 | 95 / 180 |
| **seed-7 matching (this)** | **208** | **18,060** | **11,840** | **73,805** | **1,187,790** | 95 / 180 |
| seed-7 minus seed-42 | +3 | **−14** | −14 | **−1,576** | −8,612 | — |

Complete dirty F2 boundaries and semantic `N` are unchanged from baseline on
both wraps; paid profile mass **5,129** is unchanged; local/nine-stage guards
remain strict. The unordered pair sets overlap in 150 pairs and differ in the
rest (tie-breaking among equal ADD savings). Champion pair `277→434` is present
in both matchings.

A bounded screen of ADD-greedy shuffles over seeds `0..255` (233 matchings with
saving ≥ 6,200 invoiced) found no point that beats seed-7 on both ADD saving and
`F` simultaneously; seed-7 is the unique maximum-saving point in that screen and
also the minimum-`F` point among savings ≥ 6,231. This is **not** a claim of
optimality outside ADD-greedy shuffle tie-breaks.

## Reproduce

Python **3.12**, standard library only, from the repository root:

```sh
python3.12 -I -B research/h2sem-matching-f-invoice/verify.py
python3.12 -I -O -B research/h2sem-matching-f-invoice/verify.py
python3.12 -I -B research/h2sem-matching-f-invoice/test_package.py
python3.12 scripts/research_package.py --package research/h2sem-matching-f-invoice
```

Expected:

```text
PASS_H2SEM_MATCHING_F_INVOICE seed42_pairs=205 adds=24305->18074 F=75381 seed7_pairs=208 adds=24305->18060 F=73805 delta_adds=-14 delta_F=-1576 profile_mass=5129 columns=661 controls=7 no_new_kappa
PASS_REGISTERED_RESEARCH_PACKAGE research/h2sem-matching-f-invoice outcome=completed
```

Read-only replay compares to [CERTIFICATE.json](CERTIFICATE.json) and
[MATCHING7.json](MATCHING7.json). Pass `--write` only to regenerate those
receipts. Admission uses `need()` (not `assert`); `-O` also passes.

## Evidence map

| Claim | Where |
|---|---|
| Seed-42 invoice reproduces #1805 | `verify.py` bills `match42` |
| Seed-7 ADD-greedy matching + full invoice | `MATCHING7.json`, bills `match7` |
| Strict dominance deltas | `CERTIFICATE.json` `deltas_7_minus_42` |
| H2-sem shape, semantic N, 661-column boundary | `verify.py` |
| Paid profile / rank mass 5129 | owner checker `xcheck_p.py` |
| Prefix-50 does not dominate full seed-7 | bill `prefix50_seed7` |
| Bounded seed screen summary | [SWEEP.json](SWEEP.json) |

## Scope limits

No new kappa, frontier, native/hosted admission, or compiler/tape claim. Paid
profile unchanged; bit side nonbinding. Does not claim optimality over all
matchings or non-greedy constructions. Does not re-derive #1782/#1194; prices
wraps under that admitted interface. Open #2033 already answers #1805 question 2
(composition onto the PR1062 star word) and is not consumed.

## Open next questions

1. **Is there a non-greedy disjoint matching with saving ≥ 6245 and F < 73805?**
   Why it matters: the seed screen only varies ADD-greedy tie-breaks. First step:
   local search from seed-7 with single pair swaps scored by exact `F`. Blocked by:
   no cheaper exact point is known.
2. **Can a joint (ADD, F) objective on the star word (#2033) recover a net saving?**
   Why it matters: #2033 showed the fixed pair costs +3 to +9 on PR1062; a
   different matching might still help. First step: port this invoice to the
   11,500-ADD star D. Blocked by: star composition overhead.

## Credit

Credit **Aaron Wang / PR848** (pair census and ADD-greedy matching rule),
**navinor / PR1782** (H2-sem admission), **Wentao Li / PR1805** (seed-42 invoice
and the open F question answered here), **woklerx / PR1194** (H2-sem contract),
**DreamingOfClouds / PR589** and **eumemic / PR555** (R439 word). Prepared by
Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance.
Apache-2.0. No independent human review or multiplication theorem is claimed.
