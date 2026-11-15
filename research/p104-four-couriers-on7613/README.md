# CONDITIONAL κ = 0.00365455370060 — four courier (funded-return) moves on #7613 (premise: the inherited CLEAR #44 content)

**κ = 0.003654553700603812…, ×1.00040975 (+0.040975%) over
[#7613](https://github.com/CrocSwap/integer-mult-bounds/pull/7613)** (κ 0.00365305686569).
The official `evaluate_recursive_power` bracket (256 bits) is
[0.0036545537006, 0.0036545537007]; the claim 0.00365455370060 is below the exact crossing 0.00365455370060381.

> **Premise (inherited, nothing new).** Conditional on exactly the premise of
> #7608/#7612/#7613: owned CLEAR #44 (owned field 1557, chart 595) erases
> `{451:−1, 1495:1}` and `owned_erasure` must let a CLEAR discard that row.
> This word's CLEAR content is identical to #7613's at all 74 CLEARs. If that
> premise is refused, this word is void with #7613.

## The moves

The courier (funded-return) pattern is the crowd's, not ours: Clear1nsight's
#7244/#7274/#7314/#7334/#7481 funded-return chain with determinant-one
co-encoding, rohanarun's #7480 bypass (and #7277), CubeJerry's #7577 analysis
and petalas's #7326 (see [NOTICE](NOTICE)). This package applies it to four
further sibling pairs on #7613 (itself built on Clear1nsight's #7612).

In each move a transit register S drops a mid-chart visit (merging two hops).
A courier D, present with S at chart a, carries S's content through an
invertible shear re-basis, stops at S's next chart b, and the inverse shear
decodes there. Nothing is deleted; the pair (S, D) is only re-based.

| S / D | a | dropped by S | b | courier stop |
|---|---|---|---|---|
| 532 / 1464 | 3 | 744 | 746 | 1464 gains 746 |
| 1250 / 1464 | 3 | 744 | 746 | (shared with the first) |
| 226 / 990 | 719 | 907 | 127 | none (990 already stops at 127) |
| 7 / 779 | 743 | 922 | 245 | none (779 already stops at 245) |

The 226/990 move needs 226's MOVE 260→719 slid earlier, to just after its last
chart-260 op (event 33350), so that courier 990 is co-present at chart 719.

On #7613's word (76,666 events, unchanged in count; per native call ADD +3, MOVE −3):
three new public chart pairs, (3,746) (dimension 0→6), (719,127) (6→9) and
(743,245) (6→8), all strictly nested. Rows (all 1,569), end charts, header,
owned MOVEs (47), the 74 owned lifetimes, the peak (50) and the CLEARs equal
#7613's. [data/edits.json](data/edits.json) lists every event by #7613 index.

Coefficients: no non-dyadic event is added (5,901, as in #7613). All
coefficient denominators are 5-smooth and the word passes main's merged #7000
alphabet check; the common grid (odd denominator lcm 1125, 2-adic exponent 25,
40 numerator bits) is #7613's.

## Price

Native paid delta per call {1:−2, 3:−2, 4:−1, 6:+2}; over 17 calls:
- paid positions 110,247 → 110,196; productive 22,461; rank surplus S = 1,424 unchanged.

Official tools (`price.py`):
- `scripts/compare_recursive_invoices.py` against #7613: `uniformly_better`,
  strictly negative for r^(1−C), paid {1:−34, 3:−34, 4:−17, 6:+34}, targets unchanged.
- `scripts/evaluate_recursive_power.py` (256 bits): `new_cost_lower` at
  C = 0.0036545537006, 0.0036530568656 (#7613) and 0.0036527403112 (#7612);
  `new_cost_higher` at C = 0.0036545537007.

Ordinary bound (17 calls) 778,647,060 < 10^9 (#7613: 778,697,380); precision
bit bounds unchanged (303 / 299 / 299). Strictification gate (run offline, not
in this package): γ 0.941095, δ 0.908152, both below 31/32.
An independent read-only audit found the word sound relative to #7613.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-four-couriers-on7613
```

`check.py` (standard library) authenticates the vendored #7613 word, rebuilds
the new word from the edit list, replays both exactly over the rationals with
legality checks, requires every row, end chart, owned MOVE, lifetime and the
header to equal #7613's and all 74 CLEARs to erase #7613's content (CLEAR #44
asserted), checks that only registers 7, 226, 532, 1250, 1464 change
their MOVE chains (endpoints kept; S drops one chart, 1464 gains one stop),
locates the encode/decode shears and checks they are exact inverses in reverse
order around S's move, requires exactly the three new strictly nested chart
pairs and the 5-smooth coefficient alphabet with no non-dyadic event added, recomputes the invoice and κ and
reproduces #7613's crossing, and runs rejecting controls (wrong
coefficients, dropped or sign-flipped decodes or encodes, 226 slide undone, courier skipping its stop, transit
MOVE after its decode, flipped ownership flag, reversed or non-nested MOVE,
retagged encode, bare hop deletion without a courier) plus a tampered invoice.
`price.py` runs the repository tools above.

## Conditional premises and what is not rerun

On top of the inherited CLEAR #44 premise, the claim carries the framework
assumptions of #7605 (`native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, `analytic_recovery`), the signed #7113 caller, and the BIT
premise of the base. This package does not rerun the signed caller, outer
predicates or precision/tape counts (header, rows, grid and owned data are
unchanged). No upstream maintainer has reviewed the package.

## Credit

The move pattern is the crowd's (credits above); the base word is #7613 on
Clear1nsight's #7612; the lineage is in [NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

**The premise.** A ruling on `owned_erasure` (clear-form-gap Q1) decides #7608, #7612, #7613 and this word together. See [TASK.json](TASK.json).
