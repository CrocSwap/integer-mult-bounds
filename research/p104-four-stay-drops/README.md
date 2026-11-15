# CONDITIONAL κ = 0.00365242381187 — four stay drops on #7608 (premise: #7608's CLEAR #44 content)

This P104 word is the word of our
[#7608](https://github.com/CrocSwap/integer-mult-bounds/pull/7608) (head
`24b082992`, `research/p104-dual-scan-drop-902/data/word.json.gz`, SHA256
`37dc87b2…9118`, κ 0.00365074956598) with four stay drops and one joint exact
repair. #7608 is aliromman's
[#7605](https://github.com/CrocSwap/integer-mult-bounds/pull/7605) with one
edit; the chain below it is FanPUYen's #7604, SYLforge's #7603, ToikY's #7546
and our #7601 (see [NOTICE](NOTICE)). Result: **κ =
0.00365242381186666478…, ×1.0003978 (+0.03978%) over our
[#7610](https://github.com/CrocSwap/integer-mult-bounds/pull/7610)**
(κ 0.00365097153936), which this package supersedes: the main-46 drop of
#7610 at the 245 stay is one of the four drops here.

> **Premise (inherited, nothing new).** The claim is conditional on exactly
> the premise of #7608: owned CLEAR #44 (owned field 1557, chart 595) erases
> `{451:−1, 1495:1}` and `owned_erasure` must let a CLEAR discard that row. This
> word's CLEAR content is identical to #7608's at all 74 CLEARs, so it adds no
> premise. If #7608's premise is refused, this word is void with #7608.

## The edits

Four non-owned stays are dropped, so three mains go straight from source to
target chart:
- **Main 185** (stay 1062): 401→1062→922 becomes 401→922 (dimensions 2→5→7
  become 2→7).
- **Main 82** (stay 1062): 740→1062→1071 becomes 740→1071 (3→5→6 becomes 3→6),
  and `ADD 185 += 82 (−1/2) @1062` is removed.
- **Main 46** (stays 914 and 245): 513→914→245→127 becomes 513→127 (3→7→8→9
  becomes 3→9).

One joint exact repair (all four stays in one linear solve, 5 corrections at
charts 922, 914 and 245: `185 += 779 (−1/4)`, `185 += 7 (−5/4)` at 922,
`145 += 818 (−1)` at 914, `588 += 818`, `1456 += −818` at 245) plus **40 premix
operations at chart 3 (frame {0})** at the start of the program (38 ADDs and 2
SCALEs, of 588, 1456, 161, 145, 185, 196) make all 1,569 final rows equal
#7608's. Events go 76,631 → 76,668 (+39 ADD, +2 SCALE, −4 MOVE per native call).

**Three new public chart pairs**, each a strictly nested ascent:
(401, 922) dimensions 2→7, (513, 127) 3→9, (740, 1071) 3→6. Every other MOVE
uses a pair #7608 already uses. All end charts, the owned MOVEs (47), the 74
owned lifetimes, the peak (50), the header, the signed #7113 caller data and the
coefficient grid (2^25, odd denominator 1125, 40 bits) are #7608's.
[data/edits.json](data/edits.json) lists every event by #7608 index.

## Price

The complete invoice is #7608's with the native delta charged 17 times
(native paid delta {1:−3, 2:−2, 4:−1, 5:+1, 6:+1}):
- paid positions 110,349 → 110,281; productive positions 22,461;
- rank surplus S = 1,424 unchanged; zero empty-root credits;
- D0 392,815.1147.

The crossing of Σ(T−P)·r^(1−C) is **κ = 0.00365242381186666478…**, up from
#7610's 0.00365097153936 and #7608's 0.00365074956598.

Official tools (`price.py`):
- `scripts/compare_recursive_invoices.py` classifies the change against #7608
  as `uniformly_better` (strictly negative for r^(1−C)), paid {1:−51, 2:−34,
  4:−17, 5:+17, 6:+17}, targets unchanged.
- `scripts/evaluate_recursive_power.py` (256 bits) gives `new_cost_lower` at
  C = 0.0036524238118, at #7610's 0.0036509715393 and at #7608's
  0.003650749565983, and `new_cost_higher` at C = 0.0036524238119.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-four-stay-drops
```

- `check.py` (standard library, about 1 minute) does the following:
  - authenticates the vendored #7608 word and rebuilds the new word from it
    and the edit list;
  - replays both words over the rationals from arbitrary inputs, with the
    legality checks listed in its docstring (every ADD/SCALE operand at the
    event's chart, public MOVEs strictly ascending by span inclusion, owned
    rules);
  - requires the header, every row and end chart, the owned MOVEs, lifetimes
    and peak to equal #7608's, and that only mains 46, 82 and 185 change their
    MOVE chains, with endpoints kept;
  - requires the three new chart pairs to be exactly those listed above, each a
    strictly nested ascent;
  - requires all 74 CLEARs to erase #7608's content (CLEAR #44 asserted as
    `{451:−1, 1495:1}`);
  - recomputes the census, invoice and κ, and reproduces #7608's crossing;
  - runs ten rejecting controls (a premix coefficient changed, a premix SCALE
    dropped, either of two corrections dropped, a correction at the wrong
    chart, the drops without premixes and corrections, a MOVE from the wrong
    chart, a reversed MOVE, a non-nested MOVE target, a flipped ownership flag)
    and a tampered invoice.
- `price.py` runs the two repository tools above.

The strictification gate (the repository's separation check) was run offline
by us and is not part of this package: γ 0.941004, δ 0.908150, both below
31/32 (#7608: γ 0.940932, δ 0.908149).

## Conditional premises and what is not rerun

On top of #7608's CLEAR #44 premise, the claim carries the framework
assumptions of #7605 (`native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape`, `analytic_recovery`), the signed #7113 caller, and the BIT
premise of the base. This package does not rerun the signed caller, outer
predicates, precision/tape counts or ordinary bill (header, rows, grid and
owned data are unchanged). An independent read-only audit found the word sound
relative to #7608. No upstream maintainer has reviewed the package.

## Method

Single-stay drops (#7601's token-settled engine) of mains 185 and 82 at stay
1062 and of main 46 at stays 914 and 245 do not conflict, so all four are
repaired in one exact solve from #7608's word (order-independent), with the
premix obtained as a unique solve over the full birth frame and row-reduced to
ADD/SCALE operations.

## Open next questions

**The premise.** A ruling on `owned_erasure` (clear-form-gap Q1) decides #7608,
#7610 and this word together. See [TASK.json](TASK.json).

## Credit

The base word and all retained work are #7608, aliromman's #7605 and the
authors it credits (see [NOTICE](NOTICE)); the main-46 merge is our #7610.
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
