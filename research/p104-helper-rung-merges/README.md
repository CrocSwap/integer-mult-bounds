# Conditional κ = 0.0036475398277 from two helper rung merges on #7334

This P104 word is the word of Clear1nsight's
[#7334](https://github.com/CrocSwap/integer-mult-bounds/pull/7334) (head
`aaeec8c0acf01e99a5f331ef363a698d9c084ace`, `WORD.json.gz` SHA256
`4b9fd118…d9bb2a`) with two independent exact edits. Each one removes a
paid rung from a public helper's chain. All 1,569 final rows, all end
charts, the mains, the owned MOVEs, the 73 owned lifetimes, peak owned
storage 50 and the signed #7113 caller are #7334's.

**Helper 761** now climbs 0→7 in one MOVE, where #7334 has 0→5→7.
- `1266 += ½·761` moves from chart 1053 to chart {0}, where 761 already
  sits. 761 has no operation between the two points, so 1266 receives the
  same value.
- `1438 += −½·761 @1053` becomes `1438 += 591` and `1438 += −2·760` at
  chart 1053.
- Four ADDs at the end, at chart 127, restore 1438's final row exactly:
  `1438 += 311`, `−591`, `+2·760`, `+1439`.
- The MOVEs are re-derived: 591 reaches 1053 earlier, and 1266's MOVE to
  1053 is the last event.

**Helper 1077** now climbs 4→6 in one MOVE, where #7334 has 4→5→6.
- Delete `1077 += ½·902 @789` (event 37703 of #7334's non-MOVE list).
- Insert 14 ADDs, each where target and source already sit (charts 3,
  595 and 913).
- Re-derive the MOVEs of 230 and 757.
- We posted this edit publicly as a
  [hand-off on discussion #1166](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166).

[data/edits.json](data/edits.json) lists every deleted and inserted event
by #7334 index. Each native word has 18 more ADDs and 2 fewer MOVEs. Its paid
histogram changes by P₁ −2, P₅ −1, P₇ +1, and its target histogram is unchanged.

## Price

The complete invoice is #7334's with the native delta charged 17 times:
- paid positions 110,519 → 110,485;
- productive positions 22,461;
- rank surplus S = 1,424;
- zero empty-root credits.

The crossing of Σ(T−P)·r^(1−C) is

- **κ = 0.003647539827762350774438515…**, up from #7334's 0.003646651956440447906995540…
  (×1.000243476, +0.0243%).

The repository's own tools certify the claim:
- `scripts/compare_recursive_invoices.py` classifies the change against
  #7334 as `uniformly_better` (strict for r^(1−C)).
- `scripts/evaluate_recursive_power.py` gives `new_cost_lower` at
  C = 0.0036475398277, and `new_cost_higher` at C = 0.0036475398278.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-helper-rung-merges
```

- `check.py` (standard library) does the following:
  - authenticates the vendored #7334 word and rebuilds the new word from it
    and the edit list;
  - replays both words over the rationals from arbitrary inputs, with the
    legality checks listed in its docstring;
  - requires every row and end chart to equal #7334's, and the owned data
    to be unchanged;
  - reproduces #7334's published native census and crossing;
  - recomputes the invoice and κ;
  - runs eight rejecting controls.

  The intermediate coefficient grid is #7334's: 2-adic exponent 25, odd
  scale 1125, 40 numerator bits.
- `chart.py` checks the two new chart pairs ({0}→rank 7, and rank 4→rank 6;
  both nested) on all 512 columns with exact Gaussian dyadic arithmetic.
  - Each composite is a rank-g child with g = the dimension gap.
  - #7334's own pairs of the same shapes pass the same check.
  - A non-nested target and a target without its quadratic phase are rejected.
- `price.py` runs the two repository tools above.

## Conditional premises and what is not rerun

The claim has the same conditional status as #7334's. It keeps the five
framework assumptions `native_all_columns`, `owned_erasure`, `compiler`,
`precision_tape` and `analytic_recovery`, the signed #7113 caller, and
#7334's BIT premise (.00376669, margin 1.19·10⁻⁴).

This package does not rerun the following #7334 replays:
- the signed caller;
- the physical catalogue of unchanged chart pairs;
- the fixed-tape counts;
- the ordinary bill (18 more ADDs per native call);
- the outer predicates at the new claim.

Row equality, unchanged ownership and the unchanged grid carry the native
interface over. The two new chart pairs are checked here. No human has
reviewed the package.

No register is touched both by these edits and by the events that
#7480/#7481 change (fields 54, 449, 485, 824, 1206, 1455, 1477 and owned
field 1501). The edits should therefore compose with those, but no composed
word or price is computed here.

## Open next questions

**Composition with #7480/#7481.** Applying both edit lists to #7481's word
and replaying should give the sum of the two paid deltas. The first step is
to rebase [data/edits.json](data/edits.json) onto #7481's word and run
`check.py` against it. See [TASK.json](TASK.json).

## Credit

The base word, its caller application and all retained work are
Clear1nsight's #7334 and the authors it credits (Rohan Arun for #7113, ToikY
and others; see [NOTICE](NOTICE)). DreamingOfClouds with Claude Opus 5.5
(Anthropic), via Claude Code. Apache-2.0.
