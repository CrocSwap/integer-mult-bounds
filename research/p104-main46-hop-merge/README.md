# CONDITIONAL κ = 0.00365097153936 — hosted main 46 merges its final unit hop on #7608 (premise: #7608's CLEAR #44 content)

This P104 word is the word of our
[#7608](https://github.com/CrocSwap/integer-mult-bounds/pull/7608) (head
`24b082992`, `research/p104-dual-scan-drop-902/data/word.json.gz`, SHA256
`37dc87b2…9118`, κ 0.00365074956598) with one exact edit. #7608 is aliromman's
[#7605](https://github.com/CrocSwap/integer-mult-bounds/pull/7605) with one
edit; the chain below it is FanPUYen's #7604, SYLforge's #7603, ToikY's #7546
and our #7601 (see [NOTICE](NOTICE)). Result: **κ = 0.0036509715393606183607545417…,
×1.0000608 (+0.00608%) over #7608**.

> **Premise (inherited, nothing new).** The claim is conditional on exactly
> the premise of #7608: owned CLEAR #44 (owned field 1557, chart 595) erases
> `{451:−1, 1495:1}` and `owned_erasure` must let a CLEAR discard that row. This
> word's CLEAR content is identical to #7608's at all 74 CLEARs, so it adds no
> premise. If #7608's premise is refused, this word is void with #7608.

## The edit

**Main 46** goes 914→127 in one MOVE, where #7608 has 914→245→127 (dimensions
7→9 instead of 7→8→9). Net +10 events per native call (one MOVE fewer, 11 ADDs
more):
- `MOVE 46 914→245`, `ADD 1456 += 46 @245`, `ADD 588 += −46 @245` and
  `MOVE 46 245→127` are deleted, and `MOVE 46 914→127` is inserted in place
  of the last;
- two corrections at chart 245: `588 += 818`, `1456 += −818`;
- 11 premix ADDs at chart 3 (frame {0}) at the start of the program: a 3-ADD
  588/1456 shear, then `588 += −(228, 434, 443)`, `588 += 444` with the paired
  `1456` updates.

[data/edits.json](data/edits.json) lists every event by #7608 index. The pair
914→127 is already used by #7608, so there is no new chart pair. All 1,569 final
rows, all end charts, the owned MOVEs (47), the 74 owned lifetimes, the peak
(50), the header, the signed #7113 caller data and the coefficient grid
(2^25, odd denominator 1125, 40 bits) are #7608's; only main 46's MOVE chain
and the ADDs above differ.

## Price

The complete invoice is #7608's with the native delta charged 17 times
(native paid delta {1:−2, 2:+1}):
- paid positions 110,349 → 110,332; productive positions 22,461;
- rank surplus S = 1,424 unchanged; zero empty-root credits;
- D0 392,993.2743 → 392,969.7073 (−23.57).

The crossing of Σ(T−P)·r^(1−C) is **κ = 0.0036509715393606183607545417…**,
up from #7608's 0.0036507495659836771294008126936….

Official tools (`price.py`):
- `scripts/compare_recursive_invoices.py` classifies the change against #7608
  as `uniformly_better` (strictly negative for r^(1−C)), paid {1:−34, 2:+17},
  targets unchanged.
- `scripts/evaluate_recursive_power.py` (256 bits) gives `new_cost_lower` at
  C = 0.0036509715393 and at #7608's 0.003650749565983, and `new_cost_higher`
  at C = 0.0036509715394.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-main46-hop-merge
```

- `check.py` (standard library, about 2 minutes) does the following:
  - authenticates the vendored #7608 word and rebuilds the new word from it
    and the edit list;
  - replays both words over the rationals from arbitrary inputs, with the
    legality checks listed in its docstring;
  - requires the header, every row and end chart, the owned MOVEs, lifetimes
    and peak to equal #7608's, and that only main 46 changes its MOVE chain;
  - requires all 74 CLEARs to erase #7608's content (CLEAR #44 asserted as
    `{451:−1, 1495:1}`);
  - recomputes the census, invoice and κ, and reproduces #7608's crossing;
  - runs eight rejecting controls (premix coefficient changed, premix ADD
    dropped, correction dropped, the merge without premixes or corrections,
    correction at the wrong chart, premix at the wrong chart, a reversed MOVE,
    a MOVE from the wrong chart) and a tampered invoice.
- `price.py` runs the two repository tools above.

The strictification gate (the repository's separation check) was run offline
by us and is not part of this package: γ 0.940941, δ 0.908149, both below
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

Single-stay drop scan (#7601's token-settled engine): merge two adjacent hops
of a main, then repair the changed rows with an exact linear premix. The one
merge that settles exactly was rebuilt and replayed on #7608's word.

## Open next questions

**The premise.** A ruling on `owned_erasure` (clear-form-gap Q1) decides #7608 and
this word together. See [TASK.json](TASK.json).

## Credit

The base word and all retained work are #7608, aliromman's #7605 and the
authors it credits (see [NOTICE](NOTICE)). DreamingOfClouds with Claude Opus 5.5
(Anthropic), via Claude Code. Apache-2.0.
