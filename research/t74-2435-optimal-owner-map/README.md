# PR2447's owner fill is exactly optimal (independent check), and a 4-move map attains the same optimum

**Independent verification plus a minimal alternative construction; no κ claim.**

[PR2442](https://github.com/CrocSwap/integer-mult-bounds/pull/2442) certified the bin-pattern integer optimum for the
[PR2435](https://github.com/CrocSwap/integer-mult-bounds/pull/2435) T74 words: idle `{1:20822, 3:6694, 5:2, 48:25302}`,
root 0.0016985119240027768. Every legal whole-helper owner fill has b at most that root plus 10⁻¹⁵.
[PR2447](https://github.com/CrocSwap/integer-mult-bounds/pull/2447) (Jeremy Kothe) then claims
κ = 0.001698511924002761… with "the pattern-optimal fill" for those words.

**1. Independent check of PR2447.**
- Its pinned `OWNERS.json.gz` (head `805bbadd`) passes this author's independent checker, PR2387's
  `fill_check80`, which shares no code with PR2447:
  - R-a..R-e: roles, widths, families, active pair, windows rebuilt from GLOBAL-TEMPLATE, capacity, prefix;
  - R-f: namespace, physical 66,826;
  - R-g: X2 pending axes, and 9,531 distinct 73-column charts, equal to its SPEC.
- Its recount equals its SPEC and PROFILE.
- Its idle multiset is **exactly PR2442's certified optimum**, and its κ equals the optimum root to within 10⁻¹⁵.
- Combined with PR2442's certificate, **PR2447's fill is provably optimal** among all legal whole-helper fills of
  these words. No further owner-map gain on them exceeds 10⁻¹⁵.

**2. A minimal realization of the same optimum.** Four role moves on PR2435's pinned map (`MOVES.json`) reach the
optimum, against 287,264 changed rows in PR2447. They re-pattern four bins:

| bin | before | after |
|---|---|---|
| A (48) | [8,8,9,9,9] + 5 | [4,8,9,9,9,9] |
| B (48) | [9,9,9,9,9] + 3 | [4,8,9,9,9,9] |
| C (32) | [4,9,9,9] + 1 | [9,9,9] + 5 |
| D (32) | [4,9,9,9] + 1 | [9,9,9] + 5 |

- The resulting map passes R-a..R-g.
- Its root is certified within ±10⁻¹⁵ of the optimum: **+5.80e-10 over PR2435**.
- It has **9,131 distinct 73-column charts**, against 9,531 for PR2447 and 9,129 for PR2435. A smaller chart set
  can only help the invoice row bound; this is not re-run here.

**Controls.**
- The unmodified PR2435 map reproduces its own idle multiset and root.
- Each single move alone is rejected (capacity) or misses the optimum.
- An out-of-window move is rejected (R-d).
- A same-call family clash is rejected (R-e).

Integration review corrected the negative-control harness: a control's own failure
must not be caught as a successful rejection. Window and family mutants now require
their specific rejection reasons; a single move reaching the optimum fails outside
the pipeline exception handler. The full replay and accept-all/wrong-reason controls
pass with the same owner map, endpoint and chart counts.

## Reproduce

From the repository root, standard library only:

```sh
python3 -I -B research/t74-2435-optimal-owner-map/optimal_map.py --fetch     # ~30 s
```

`--fetch` fetches `refs/pull/2435/head` (324d7d35), `refs/pull/2447/head` (805bbadd) and `refs/pull/2269/head`
(template DATA-PHASES) if absent. All inputs are blob- and sha256-pinned. `--write-map` also writes the full
optimal map, `OWNERS-OPT.json.gz`.

Expected final line:
`PASS_T74_2435_OPTIMAL_MAP moves=4 idle={"1":20822,"3":6694,"48":25302,"5":2} root=0.0016985119240028 gain=+5.803e-10 charts=9131 controls=6 pr2447=verified no_new_kappa`

All results were run on CPython 3.14.4; the registered Python 3.12 replay was not run locally.

## Scope and limits

- **No κ claim for the 4-move map.** PR2435's admission (invoice with the new chart count, outer ledger) is not
  re-run for it.
- **PR2447's κ is not re-derived.** Only its owner map, recount and complex endpoint are checked. Its outer
  formula, κ = C − 1/F − B, and its admission are its own.
- **Entrance raise.** The words are PR2435's. The obligation that the raised entrances are delivered at dimension 2
  is inherited; see PR2446 and PR2453. PR2447 adds an explicit width binding for it.

## Open next questions

- **PR2462's new words.** PR2462 claims κ 0.0017035523 with PR2436's aliases on the entrance-raised words. Is its
  owner fill also at the pattern optimum for its words? First step: run PR2442's `owner_optimum.py` with PR2462's
  inventory and idle multiset.

## Credits and licence

- PR2447 / PR2435 / PR2374 (Jeremy Kothe): the audited fill and the T74 line.
- PR2322 (Vlado Vojdanovski): the words.
- PR2360 (Jeremy Diviney) and PR1129 (Ali Romman): the pattern-dual relaxation.
- PR2442 / PR2446 / PR2387 (this author): the optimum certificate and the checker, vendored with pins.

Prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). No independent human review is
claimed. Apache-2.0.
