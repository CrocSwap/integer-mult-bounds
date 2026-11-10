# helper462-one-scale-21-shear

**Constructive witness. No new κ and no selected-frontier change.**

## Result

For the pinned helper-462 matcher `S`
(`research/bit-completed-backend-api/science/RESULT.json#matcher`, an 8 by 8
integer matrix of determinant `-16`), the alphabet of axis swaps,
single-coordinate rational scales and rational shears contains a zero-swap
word with exactly one scale and **21 shears**. The scale is the last letter,
on row 0, with coefficient `-16`. The shear denominators are `1, 2, 4, 8, 16`.

The shortest one-scale zero-swap word recorded before this package has 26
shears (unpaidmoon, open PR #7054), on the same matrix with the same scale.
The lower bound is 9 shears (unpaidmoon, open PR #7055). The open interval for
the one-scale shear length therefore moves from 9 through 26 to **9 through 21**.

Twenty-one is the length of this witness. It is not claimed to be minimal.

### The word

Letters apply first to last as row operations on the identity.
`t += a*s` means row `t` gains `a` times row `s`. This is the content of
[WORD.json](WORD.json).

| # | letter | # | letter | # | letter |
|---:|---|---:|---|---:|---|
| 1 | `7 += -1*2` | 8 | `0 += 3/4*1` | 15 | `5 += 1/2*1` |
| 2 | `1 += 1*3` | 9 | `1 += 4*0` | 16 | `4 += 1*7` |
| 3 | `5 += 1*3` | 10 | `0 += -3/16*1` | 17 | `4 += 16*0` |
| 4 | `3 += -2*1` | 11 | `2 += -8*0` | 18 | `6 += -1*3` |
| 5 | `5 += 2*0` | 12 | `0 += 1/8*2` | 19 | `3 += 1*6` |
| 6 | `0 += -1/2*5` | 13 | `0 += -1/16*4` | 20 | `6 += -1*3` |
| 7 | `4 += 2*2` | 14 | `1 += 2*3` | 21 | `1 += 1*2` |

Letter 22 is the scale: row 0 times `-16`.

### One word per scale row

A zero-swap word with one scale `c` on row `r` has determinant `c`, so `c = -16`
and the shears multiply to `D_r^{-1} S`. Conjugating by the scale moves it to
either end without changing the shear count, so only the row `r` matters.
[ROW_WORDS.json](ROW_WORDS.json) records one exact word for each row:

| scale row | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| shears | 21 | 21 | 24 | 21 | 21 | 21 | 21 | 23 |

Each count is an upper bound for that row. The larger counts on rows 2 and 7
are a search outcome. They are not a proof that those rows need more shears.

## Claim type and limits

- **Finite certificate.** Each frozen word multiplies exactly to `S` over the
  rationals. That is the whole proof of the upper bounds.
- **Not a minimum.** The words came from a beam search, which is a heuristic
  and not a census of rational words. Lengths 9 through 20 stay open.
- **Lower bound cited, not replayed.** The floor of 9 is the statement of open
  PR #7055. This package does not recheck it.
- No supplier admission, no P2 ordinary bill, no tariff, and no
  integer-coefficient claim. With integer shears no one-scale zero-swap word
  exists (merged PR #6954); this word uses the denominator 16.

## Evidence

`verify.py` uses the Python 3.12 standard library and exact fractions. It checks:

1. the pinned matcher is 8 by 8 with determinant `-16`;
2. the 21 shears followed by the scale reproduce `S`, by row operations on the
   identity and by an independent product of elementary matrices;
3. the shear part has determinant 1, and no two adjacent shears share a
   position, so no pair merges into one letter;
4. the same checks for the eight words of `ROW_WORDS.json`, whose row-0 entry
   equals `WORD.json`;
5. 406 failure controls: for the primary word and each row word, deleting any
   single letter misses `S`, and adding 1 to any single coefficient misses `S`.

Failures use an explicit exit, so the controls stay active under `-O`.

## Reproduce

From the repository root, with CPython 3.12:

```sh
python3.12 -B research/helper462-one-scale-21-shear/verify.py
python3.12 -O -B research/helper462-one-scale-21-shear/verify.py
python3.12 -B scripts/research_package.py --package research/helper462-one-scale-21-shear
python3.12 -B scripts/check_research_commit.py --package research/helper462-one-scale-21-shear --check-source-history
```

Expected first line: `PASS_HELPER462_ONE_SCALE_21_SHEAR`. The verifier runs in
well under a second.

### Search provenance (not a registered check)

`search.py` is the beam search that proposed the words. It reduces
`D_r^{-1} S` to the identity by row and column shears whose coefficient clears
one entry or sets one diagonal entry to 1, and keeps the matrices with the
fewest entries differing from the identity. It writes its output to a
directory outside the checkout:

```sh
python3.12 -B research/helper462-one-scale-21-shear/search.py "$OUT" 4000 1 0 "" 24
python3.12 -B research/helper462-one-scale-21-shear/search.py "$OUT" 300 1 0 "" 30 2,7
```

The first command took about 11 seconds on ten cores and returns the recorded
21-shear words for rows 0, 1, 3, 4, 5 and 6; it returns nothing for rows 2
and 7 within depth 24. The second returns the recorded 24-shear word for row 2.
The row-7 word came from
`search.py "$OUT" 1500 2 1.5 "1,-1,2,-2,0.5,-0.5" 23`, seed 1, a run of about
three minutes that was not repeated. The frozen words do not depend on the
search: the exact products are the certificate.

## Open next questions

Structured copies are in [TASK.json](TASK.json).

1. **What is the minimal one-scale shear length?** The interval is now 9
   through 21. First step: run `search.py` with a wider beam and depth cap 20
   on rows 0, 1, 3, 4, 5 and 6, and separately try to raise the rank-drop floor
   of PR #7055 from 9 to 10. A search that returns nothing is not a lower bound.
2. **Do scale rows 2 and 7 admit 21 shears?** The recorded words have 24 and
   23. First step: a wider or noisier beam on those rows, or an invariant of
   `D_r^{-1} S` that separates them from the other six rows.
3. **Does the 21-shear word help on the P2 ordinary bill?** Letter counts do
   not determine the signed moment, and this word has denominators up to 16.
   First step: evaluate it under the tariff model of merged
   `research/helper462-p2-ordinary-bill`.

## Credit

This package was produced by Nick Petalas. New work is Apache-2.0.

Predecessors, none of which is replayed here:

- The matcher and its five-swap elimination are from
  `research/bit-completed-backend-api` (Chris R / Clear1nsight, PR #4957),
  using the helper-462 witness of ai-nanachi #4760/#4814.
- unpaidmoon, merged PR #6954: a one-scale zero-swap word (53 shears),
  the determinant identity that forces the scale `-16`, and the integer-shear
  obstruction.
- unpaidmoon, open PR #7030 (head `98238eeed3faca9f0a5f1d4060db5d5da524a192`):
  a 29-shear one-scale word and the rank lower bound 8.
- unpaidmoon, open PR #7054 (head `ae1cf2af174cd4f8c89089a27fc58e470b5452bd`):
  the 26-shear one-scale word this package shortens. Its word format and
  application order are reused in `WORD.json`.
- unpaidmoon, open PR #7055 (head `0a6361ec1b63621ca5f985218892e0cdc79502ae`):
  the lower bound of 9 shears, which poses the open interval answered in part
  here.
