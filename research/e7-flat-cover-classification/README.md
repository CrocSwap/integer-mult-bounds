# Covers of E7 by hyperplane flats: the D4-frame triples are the only covers

**No new κ is claimed.** Main's design-free cover numbers (`research/format-limits` §D,
`scripts/d1_cover_numbers.py`) establish that the 63 readers of a bit source need three hyperplane sections. The
readers are the lines of E7 = t⊥. Two flats cover at most 52 lines, and some three D6 flats cover all 63. This note
classifies the covers exactly.

1. **The covering triples are exactly the D4 frames through t.**
   - Three hyperplane flats of E7 cover all 63 lines if and only if they are E7 ∩ a⊥, E7 ∩ b⊥, E7 ∩ c⊥, where
     {t, a, b, c} is an orthogonal frame spanning a D4 subsystem.
   - There are 315 such triples, one per D4 through t.
   - The other 3780 orthogonal frames through t span only 4A1. Each of their triples leaves at least 8 lines
     uncovered.
2. **The near-covers are exactly the A3 subsystems through t.**
   - A near-cover is a triple that covers exactly 62 of the 63 lines.
   - Every near-cover is E6(A) + E6(B) + D6(m) for an A3 through t. Here A and B are the A3's two A2 subsystems
     through t, m is its one line orthogonal to t, and m is the missed line.
   - There are 378 = 63 × 6 of them, and no other type occurs.
3. **A cover count alone does not force 3 registers per D6 at rank 5.**
   - In a covering triple, each D6 has 16 private lines, covered by it alone. They span the D6.
   - Two rank-5 subflats never cover a whole D6: at most 28 of its 30 lines.
   - But two of them do cover the 16 private lines (75 such pairs per D6), and six rank-5 flats, two per D6, cover
     all of E7.
   - So "two 5-dim subflats cover ≤ 28 of 30" does not by itself force a third register in each D6 pool. A
     3-per-pool count needs a further argument about the shared lines.

**Consequences for bit skeletons:**

- The D4 skeletons of #493, #510 and #543 read each target through the three D6 frames {t, e}⊥, where e runs over
  the other lines of t's 4-frame. By (1), every top layer made of three hyperplane sections has this form.
- The only near-alternative is (2), with one line read separately.
- (3) corrects a counting step that has been proposed for a floor of 540 = 180 × 3 bit registers in this paradigm.

```sh
python3 -B research/e7-flat-cover-classification/cover_check.py
```

The check uses the standard library only and takes about 6 minutes. It ends with
`PASS_E7_FLAT_COVER_CLASSIFICATION (21 checks, ...)`.

## Method

- **Lines and flats.**
  - The E8 lines are rebuilt in Construction-A coordinates from the [8, 4, 4] Hamming code.
  - t is one fixed line. All lines are equivalent under W(E8), so one choice suffices.
  - The closed flats of E7 are enumerated by rank. The rank-(r+1) flats over a rank-r flat F are the classes of the
    remaining lines, grouped by direction modulo span(F).
- **Exact ranks.** All ranks are computed mod p = 2³¹ − 1. By Hadamard's inequality, a minor of at most 8 rows of
  squared norm 4 has |det| ≤ 2⁸, so ranks mod p equal rational ranks. No floating point is used.
- **Exhaustive searches.** Every search in the table below is exhaustive.

| Step | Check | Result |
|---|---|---|
| Flats | flats of E7 by rank 1–6 | 63 / 1281 / 10395 / 33411 / 36435 / 8821 |
| Hyperplane flats | by size | 5040 × 10, 2016 × 13, 1008 × 16, 666 × 21, 63 × 30 (D6), 28 × 36 (E6) |
| Agreement with main | `d1_cover_numbers.py` pins 8821 flats, the size histogram, best pair 52 and cover number 3 | identical |
| Identification | D6 flats = E7 ∩ a⊥ (63); E6 flats = E7 ∩ A⊥ for the 28 A2 subsystems through t | exact set equality |
| Pairs | best union of two hyperplane flats | 52; a larger union needs two flats of size ≥ 21, and all 757 such flats are tried |
| Covering triples | all triples, members in size order | 315, all D6 + D6 + D6 |
| Frames | orthogonal triples {a, b, c} ⊂ E7: span of {t, a, b, c} | 315 span a D4 (12 lines), 3780 span 4A1 (4 lines) |
| Classification | covering triples = D4-frame triples; each 4A1 triple misses ≥ 8 lines; each D4 through t has one frame through t | exact |
| Near-covers | for each of the 63 lines m, all triples covering E7 − {m} and avoiding m | 378 = 63 × 6, all E6 + E6 + D6 |
| A3 | the 378 A3 subsystems through t and their E6(A) + E6(B) + D6(m) triples | equal to the near-covers, with the same missed line |
| Inside a cover | private lines per D6; shared lines | 16 per D6, rank 6; 15 shared, 12 of them in all three |
| Rank-5 subflats of a D6 | count and sizes | 268: 120 × 8, 80 × 9, 30 × 13, 32 × 15, 6 × 20 |
| Pool step | best pair of rank-5 subflats on a D6; pairs covering the 16 private lines; a 2 + 2 + 2 cover of E7 | 28 of 30; 75 per D6; exists |

## Scope

- These are statements about covers by flats, which is the model behind main's §D cover numbers.
- (1) and (2) say which covers exist. They do not price a skeleton.
- (3) shows only that one counting step does not follow from coverage. It does not show that a design with 2
  registers per D6 pool exists: frame nesting, the readers' frames and restoration are not modelled.

## Related work

- Main: `research/format-limits/README.md` §D and `scripts/d1_cover_numbers.py` (#595, DreamingOfClouds). These give
  the census of 8821 flats, the best pair 52, and the existence of a three-D6 cover. The classification of all covers
  and near-covers is new here.
- #463 (DreamingOfClouds): the carrier bound, that two hyperplane sections cannot cover the 4-design s⊥.
- #493, #510, #543 (eumemic, DreamingOfClouds): the D4-skeleton bit words that use the D6 triples.
- Duplicates were checked against main at `f567884a` and against the titles and bodies of all hub PRs through #883.

## Credits

- DreamingOfClouds, for #595's cover-number census and #463's carrier bound.
- eumemic, for the D4 skeleton of #493 and #543.
- Prepared by DaysSky, with assistance from Claude.
