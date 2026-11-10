# The other rank-2 coframed carriers

## Statement

On the pinned PR5713 word, the legal rank-2 coframed boundary carriers are exactly three. All three reproduce the terminal output defect of the published partner-154 split. Partner 154 has the unique minimum ordinary prefix among them, so neither remaining carrier improves that published bill.

## Source and carrier rule

The source is the canonical JSON inside `research/p104-temporal-updates/WORD.json.gz` in the pinned tar `research/p104-two-boundary-helper-split/inputs/pr5713-source.tar`. Its SHA-256 is `32adce6656e49aa020d3e6317f1c45c11fccadeeb67a8d506172d101703d2138`.

A carrier is legal when all of the following hold at one program index:

- the two registers occupy one frame whose basis has length 2;
- the pivot is a non-main public register, starts on the empty frame 3, ends on the rank-9 frame 127, and has row coefficient 1 on itself;
- the partner is a main input, meaning a live register or that register plus 112;
- the coefficient `q` is a nonzero dyadic with denominator a power of two and `abs(q) + 1 < 2**16`;
- `h = row(pivot) + q * row(partner)` is supported only on registers whose initial frame is 3, and the partner coefficient in `h` is nonzero.

The coefficient is solved from the rows. A meeting is counted only when that linear condition fixes one legal `q`. A meeting whose unwanted support already vanishes for every `q` would be a free family. This word has none at rank 2.

## Census

Replaying the word and solving at every rank-2 frame gives exactly these spans, all on pivot 708 and frame 602:

| partner | q | first index | last index | nuisance terms | ordinary prefix |
| --- | --- | --- | --- | --- | --- |
| 154 | +1/2 | 13657 | 14336 | 87 | 1118 |
| 127 | -1/2 | 13653 | 14139 | 89 | 1142 |
| 119 | +1/4 | 13658 | 13658 | 104 | 1612 |

The published cut, source event 14330, lies inside the partner-154 span. On that span the nuisance `k = h - e_708` is constant, including at 13657, 14330 and 14336. Partner 127 leaves frame 602 at event 14140, and partner 154 leaves at event 14337, which fixes the closed ends above. Partner 119 meets the rule at event 13658 only.

## Output identity

For each carrier the terminal program is the predecessor construction: add the negation of `k` into 708 on frame 3, apply `126 -= 2*708` and `188 += 2*708`, replay the source with the pivot renamed to fresh register 743 after the cut and with owned ids at least 743 shifted up by one, then restore `708 += q*partner` on frame 602.

At each carrier’s last legal index, and at the published index 14330 for partner 154, the suffix column of `e_708` is exactly `{126: -2, 188: 2, 708: 1}`. The three terminal programs leave the same dirty rows, 126, 188 and 743, with identical linear defects. The prefix inserts only additions, so it adds no paid move. The ordinary prefix scalar uses the predecessor addition formula `2*(2 + a.bit_length() + a.bit_count() + b.bit_length() - 1)` for `q = a/b`, summed over the nuisance terms, the two cleanup additions and the restore. Those costs are 1118, 1142 and 1612, so partner 154 is the unique minimum.

## What this decides

The two carriers other than partner 154 reproduce the published output functional and have a strictly larger ordinary prefix. They do not improve the published #5718 bill. This classification adds no new conditional kappa and does not touch the selected frontier. Rank-1 carriers, a native caller, and the short 146-anchor transfer remain outside this check.
