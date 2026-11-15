# CONDITIONAL κ = 0.00365305686569 — contact 902/1091 rechart on #7612 (premise: the inherited CLEAR #44 content)

**κ = 0.003653056865686921592…, ×1.0000867 (+0.00867%) over
[#7612](https://github.com/CrocSwap/integer-mult-bounds/pull/7612)**
(exact crossing 0.00365274031123; #7612 claims 0.003652740309). The official
`evaluate_recursive_power` bracket is [0.0036530568656, 0.0036530568657].

The edit applies the contact-rechart move that Clear1nsight's #7612 made at
public fields 134/329 to a second pair, 902/1091. The move pattern is theirs;
this package only applies it to another contact. #7612 is built on our
[#7611](https://github.com/CrocSwap/integer-mult-bounds/pull/7611) and
[#7608](https://github.com/CrocSwap/integer-mult-bounds/pull/7608) (see
[NOTICE](NOTICE)).

> **Premise (inherited, nothing new).** Conditional on exactly the premise of
> #7608/#7612: owned CLEAR #44 (owned field 1557, chart 595) erases
> `{451:−1, 1495:1}` and `owned_erasure` must let a CLEAR discard that row.
> This word's CLEAR content is identical to #7612's at all 74 CLEARs. If that
> premise is refused, this word is void with #7612.

## The edit

On #7612's word (76,667 events → 76,666):
- `ADD 1091 += 1/2·902` is retagged from chart 618 to chart 373.
- Field 902 goes 3→373→913 (was 3→618→913), with a `MOVE 902 3→373` placed just
  before the ADD. Field 1091 goes 373→733 (the hop 373→618 is deleted).
  Dimensions: 902 0→3→7→8 becomes 0→2→7→8; 1091 …2→3→4… becomes …2→4….
- Two adjacent MOVEs of different registers (1087 237→238 and 1091 733→238)
  swap order; they commute and nothing runs between them.

It is legal because 1091 already sits at 373 and 902 arrives there just before
the ADD, 373 ⊂ 913 and 373 ⊂ 733 keep every changed MOVE a strict ascent, and
the chart of an ADD is a tag only. No new chart pair appears: (3,373),
(373,913) and (373,733) all occur in #7612. All 1,569 rows and end charts, the
header, the 47 owned MOVEs, the 74 owned lifetimes, the peak (50) and the
coefficient grid (2^25, odd denominator 1125, 40 bits) equal #7612's.
[data/edits.json](data/edits.json) lists every event by #7612 index.

## Price

The invoice is #7612's with the native delta charged 17 times (native paid
delta {1:−2, 2:+2, 3:−1, 4:−1, 5:+1}):
- paid positions 110,264 → 110,247; productive 22,461; rank surplus S = 1,424
  unchanged.

Official tools (`price.py`):
- `scripts/compare_recursive_invoices.py` against #7612: `uniformly_better`,
  strictly negative for r^(1−C), paid {1:−34, 2:+34, 3:−17, 4:−17, 5:+17},
  targets unchanged.
- `scripts/evaluate_recursive_power.py` (256 bits): `new_cost_lower` at
  C = 0.0036530568656, 0.0036527403112 (#7612's crossing) and 0.0036524238118
  (#7611's); `new_cost_higher` at C = 0.0036530568657.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-contact902-1091-on7612
```

`check.py` (standard library) authenticates the vendored #7612 word, rebuilds
the new word from the edit list, replays both exactly over the rationals with
the legality checks in its docstring, requires every row, end chart, owned MOVE,
lifetime and the header to equal #7612's and all 74 CLEARs to erase #7612's
content (CLEAR #44 asserted), requires that only registers 902 and 1091 change
their MOVE chains with endpoints kept and no new chart pair, recomputes the
invoice and κ and reproduces #7612's crossing, and runs 12 rejecting controls
(ADD kept at 618 or at 101, coefficient changed, ADD dropped, the 902 MOVE
after the ADD, dropped or reversed or non-nested MOVEs, 1091 still moving from
618, ownership flag flipped) plus a tampered invoice. `price.py` runs the two
repository tools above.

The strictification gate was run offline by us and is not part of this package:
γ 0.941030, δ 0.908151, both below 31/32 (#7612: γ 0.941017, δ 0.908150).
An independent read-only audit found the word sound relative to #7612.

## Conditional premises and what is not rerun

On top of the inherited CLEAR #44 premise, the claim carries the framework
assumptions of #7605 (`native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, `analytic_recovery`), the signed #7113 caller, and the BIT
premise of the base. This package does not rerun the signed caller, outer
predicates, precision/tape counts or ordinary bill (header, rows, grid and
owned data are unchanged). No upstream maintainer has reviewed the package.

## Method

For every public ADD (both registers public) and every chart, the contact was
retagged and each register's stay moved or split where legal, keeping every
path a strict ascent. On #7612's word exactly one of 1,356 valid single moves
has positive gain, this one; a rescan of the new word finds none.

## Open next questions

**The premise.** A ruling on `owned_erasure` (clear-form-gap Q1) decides #7608, #7612 and this word together. See [TASK.json](TASK.json).

## Credit

The move pattern and the base word are Clear1nsight's #7612; the lineage below
it is in [NOTICE](NOTICE) (#7611, #7608, #7605 and the authors credited there).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
