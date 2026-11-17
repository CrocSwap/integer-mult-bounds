# Conditional κ = 0.0036490213053944 from token-settled helper drops on #7546

This P104 word is the word of ToikY's
[#7546](https://github.com/CrocSwap/integer-mult-bounds/pull/7546) (head
`99438c43df7aac1e5dbcc43c1578fcd886c119ec`, `expected/role902-WORD.json.gz`
SHA256 `6e03624b…cd32`) with two exact edits, each removing one paid rung from
a public chain. #7546 itself builds on our
[#7542](https://github.com/CrocSwap/integer-mult-bounds/pull/7542) and
Clear1nsight's #7334. All 1,569 final rows, all end charts, the 74 owned
lifetimes, the owned MOVEs and the content erased at each owned CLEAR, the
header, the signed #7113 caller data and the coefficient grid are #7546's.

**Main 134** climbs 0→3 in one MOVE, where #7546 has 0→1→3 (chain 0→3→5→7→8
instead of 0→1→3→5→7→8).
- The owned read `134 += −2·owned1503 @595` is deleted together with the stop
  at chart 595.
- Premix ADDs at the empty frame {0}, where every operand already sits, supply
  the helper-token values the read carried. 152 such ADDs are inserted at the
  start of the program, for both edits.
- Three correction ADDs at charts 789 and 913 restore row 134 exactly.

**Main 100** climbs 3→6 in one MOVE, where #7546 has 3→5→6.
- `166 += −½·100 @783` is deleted together with the stop at chart 783.
- One correction `166 += ½·990 @907` restores row 166.

[data/edits.json](data/edits.json) lists every deleted and inserted event by
#7546 index (6 deleted, 158 inserted; 76,490 → 76,642 events). Each native
word has 154 more ADDs and 2 fewer MOVEs. Its paid histogram changes by
P₁ −2, P₂ −2, P₃ +2; the target histogram is unchanged.

## Price

The complete invoice is #7546's with the native delta charged 17 times:
- paid positions 110,468 → 110,434;
- productive positions 22,461;
- rank surplus S = 1,424;
- zero empty-root credits.

The crossing of Σ(T−P)·r^(1−C) is

- **κ = 0.0036490213053944204892137903671…**, up from #7546's
  0.0036484112947908453248116499202… (×1.0001672, +0.0167%).

The repository's own tools certify the claim:
- `scripts/compare_recursive_invoices.py` classifies the change against
  #7546 as `uniformly_better` (strict for r^(1−C)).
- `scripts/evaluate_recursive_power.py` gives `new_cost_lower` at
  C = 0.0036490213053 (and at #7546's 0.003648411294790) and
  `new_cost_higher` at C = 0.0036490213054.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-token-settled-drops
```

- `check.py` (standard library) does the following:
  - authenticates the vendored #7546 word and rebuilds the new word from it
    and the edit list;
  - replays both words over the rationals from arbitrary inputs, with the
    legality checks listed in its docstring;
  - requires the header, every row and end chart, the owned MOVEs, lifetimes,
    peak and erased CLEAR contents to equal #7546's, and that only mains 100
    and 134 change their MOVE chains;
  - recomputes the census, invoice and κ, and reproduces #7546's crossing;
  - runs six rejecting controls (altered premix coefficients, a deleted
    correction, a premix at a chart where its operands are absent, the owned
    read deleted without the premixes, a tampered invoice).
- `chart.py` checks the two new chart pairs ({0}→rank 3 and rank 3→rank 6,
  both nested) on all 512 columns with exact Gaussian dyadic arithmetic.
  #7546's own pairs of the same shapes pass the same check, and a non-nested
  target and a target without its quadratic phase are rejected. The
  phase-free control is only informative for the 3→6 pair.
- `price.py` runs the two repository tools above.

## Conditional premises and what is not rerun

The claim has the same conditional status as #7546's: the framework
assumptions `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape` and `analytic_recovery`, the signed #7113 caller, and the
BIT premise of the base. The gain is small (+0.0167%).

This package does not rerun #7546's signed caller, outer predicates,
precision/tape counts, or ordinary bill (154 more ADDs per native call).
Header, rows, grid and owned data are identical to #7546's, and the content
erased at every owned CLEAR is identical, which carries the interface over.
The two new chart pairs are checked here. No human has reviewed the package.

## Open next questions

**Further stops.** The same premix-and-correct pattern may shorten other
mains' chains. The first step is to apply it to the next chain and run
`check.py` against the new word. See [TASK.json](TASK.json).

## Credit

The base word and all retained work are ToikY's #7546 and the authors it
credits, with our #7542 beneath it (see [NOTICE](NOTICE)). DreamingOfClouds
with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.
