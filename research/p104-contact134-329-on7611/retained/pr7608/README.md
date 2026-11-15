# CONDITIONAL κ = 0.00365074956598 — hosted main 902 skips F595 on #7605 (premise: owned CLEAR #44 may discard a 2-term row)

This P104 word is the word of aliromman's
[#7605](https://github.com/CrocSwap/integer-mult-bounds/pull/7605) (head
`e1d2756eecf03e146338239fee81772a99ba8d4c`, `research/p104-timed-helper757/data/word.json.gz`,
SHA256 `37358c49…467d`) with one exact edit. #7605 builds on FanPUYen's #7604,
SYLforge's #7603, ToikY's #7546 and our #7601
(see [NOTICE](NOTICE)). The claim is **conditional on one premise that the
earlier packages did not need**, stated first:

> **Premise.** Owned CLEAR #44 (owned field 1557, chart 595, event 42713 of
> the new word) erases `{451:−1, 1495:1}` where #7605 erases
> `{451:−1, 902:−3/2, 985:−3/2, 1495:1}`. The word is valid only if
> `owned_erasure` lets a CLEAR discard that different (two-term) row. The
> other 73 of the 74 CLEARs erase exactly #7605's content. Every earlier link
> of the chain (#7546 → #7601 → #7604 → #7605) changed no erased content.

If the premise is refused, #7605's κ 0.0036504442446 stands and this word
is void. Whether `owned_erasure` admits a different erased row is an open
upstream question: `research/p104-6372-clear-form-gap`, Q1.

## The edit

**Main 902** climbs 3→618 in one MOVE, where #7605 has 3→595→618 (chain 0→3→7→8 instead
of 0→1→3→7→8 in dimensions). Six events are deleted and one inserted (net −5; per native
call: 4 ADDs and 1 MOVE fewer):
- `MOVE 902 3→595` becomes `MOVE 902 3→618`;
- the ADDs `1532 += 2·902`, `1479 += −½·902`, `1255 += −1·902`,
  `1495 += −3/2·902`, all at chart 595, and `MOVE 902 595→618` are deleted.

[data/edits.json](data/edits.json) lists every event by #7605 index. The pair
3→618 is already used by #7605, so there is no new chart pair. All 1,569 final
rows, all end charts, the owned MOVEs (47), the 74 owned lifetimes, the peak
(50), the header, the signed #7113 caller data and the coefficient grid are
#7605's; only main 902's MOVE chain differs.

The deleted `1495 += −3/2·902` is what fed owned 1557 at event 39612. That is
why CLEAR #44 changes. 1557 lives only at chart 595 (events 39611–42713) and
902 no longer visits 595, so no local repair exists. An exact linear search
over extra ADDs among registers live at 595 (4,673 candidates, 50 times) is
inconsistent. A repair needs a new MOVE that carries x902+x985 to 595, which
repays the 17 saved positions, or an extra owned lifetime.

## Price

The complete invoice is #7605's with the native delta charged 17 times
(native paid delta {1:−1, 2:−1, 3:+1}):
- paid positions 110,366 → 110,349;
- productive positions 22,461;
- rank surplus S = 1,424; zero empty-root credits.

The crossing of Σ(T−P)·r^(1−C) is

- **κ = 0.0036507495659836771294008126936…**, up from #7605's
  0.0036504442447168877637990594571… (×1.0000836, +0.00836%).

The repository's own tools certify the price:
- `scripts/compare_recursive_invoices.py` classifies the change against #7605
  as `uniformly_better` (strict for r^(1−C)), paid {1:−17, 2:−17, 3:+17}.
- `scripts/evaluate_recursive_power.py` gives `new_cost_lower` at
  C = 0.0036507495659 (and at #7605's 0.003650444244716) and
  `new_cost_higher` at C = 0.0036507495660.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-dual-scan-drop-902
```

- `check.py` (standard library, about 3 minutes) does the following:
  - authenticates the vendored #7605 word and rebuilds the new word from it
    and the edit list;
  - replays both words over the rationals from arbitrary inputs, with the
    legality checks listed in its docstring;
  - requires the header, every row and end chart, the owned MOVEs, lifetimes
    and peak to equal #7605's, and that only main 902 changes its MOVE chain;
  - **prints and asserts the erased-content diff: exactly one CLEAR (#44,
    owned 1557) differs, with the two rows above**;
  - recomputes the census, invoice and κ, and reproduces #7605's crossing;
  - runs seven rejecting controls (re-added ADD at the wrong chart, a changed
    1557 coefficient, a 3→595 MOVE without 595→618, an owned write at 595
    after 902 left, a descending MOVE, a partial drop on #7605, a tampered
    invoice).
- `price.py` runs the two repository tools above.

The strictification gate (the repository's separation check) was run offline
by us and is not part of this package: γ 0.940932, δ 0.908149, both below
31/32 (#7605: γ 0.940920, δ 0.908149).

## Conditional premises and what is not rerun

On top of the premise above, the claim carries the framework assumptions of
#7605 (`native_all_columns`, `owned_erasure`, `compiler`, `precision_tape`,
`analytic_recovery`), the signed #7113 caller, and the BIT premise of the base.
This package does not rerun #7605's signed caller, outer predicates,
precision/tape counts or ordinary bill (four fewer ADDs and one fewer MOVE per
native call). No human has reviewed the package.

## Method

Frame-perp duality: the dual of a word is a cost-identical admissible native.
Running the token-settled drop scan (#7601) on the dual explores the V-side
edit class, whose edits the primal scan does not see. This drop was found
that way and then rebuilt and replayed on the primal word, exactly.

## Open next questions

**The premise.** A ruling on `owned_erasure` (clear-form-gap Q1) decides this
word. Absent one, a repair that restores 1557's erased row without paying the
saved positions would turn it into an unconditional drop. See [TASK.json](TASK.json).

## Credit

The base word and all retained work are aliromman's #7605 and the authors it
credits (see [NOTICE](NOTICE)). DreamingOfClouds with Claude Opus 5.5
(Anthropic), via Claude Code. Apache-2.0.
