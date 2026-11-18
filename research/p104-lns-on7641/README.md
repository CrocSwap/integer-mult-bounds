# CONDITIONAL κ = 0.0037167669978: large-neighbourhood search on #7641, five edits and a hub re-settle (premises: the same as #7641's)

**κ = 0.00371676699784491874716723569687617891…, ×1.00084424 over
[#7641](https://github.com/CrocSwap/integer-mult-bounds/pull/7641)** (κ 0.0037136318149561756687…, our 20 swap-then-delete composites on
[#7637](https://github.com/CrocSwap/integer-mult-bounds/pull/7637)). The base word is #7641's word, vendored unmodified as data
(decompressed sha256 `6a472688…2b4f`). The official `evaluate_recursive_power` bracket (256 bits) is [0.00371676699784, 0.00371676699785].
The claim 0.0037167669978 is an 11-significant-digit value below the exact crossing.

> **Premises: conditional on exactly #7641's, which are #7637's.** Those are #7620's five framework assumptions (`native_all_columns`,
> `owned_erasure`, `compiler`, `precision_tape`, `analytic_recovery`) with its CLEAR reading, over #7637's 233 lifetimes plus #7641's
> one zero-join split (234 in all, unchanged here), and the changed entrance `initial[457] = 281`, which this word inherits unchanged. The
> common-U lifetime tariff affects bill totals only, not κ. If #7620's premises are refused, this word is void with #7641, #7637 and their lineage.

## The edits

Base: #7641's word (`data/base-7641-word.json.gz`, 219,147 events). New word: `data/word.json.gz`, 150,010 events. Every interior edit is
listed in base-word coordinates in [data/edits.json](data/edits.json): five edits E1–E5, 40 interior deletions and 29 insertions in all,
then the re-derived hubs. No INIT, CLEAR or owned MOVE changes.

| id | register(s) | what changes | route before → after | deletions / insertions |
|---|---|---|---|---|
| E1 | helpers 360, 537 | SWAP-NULL relabel at chart 407 (both born at {0}, both end at V), then deletion of 537's stay at 407. 360 takes 537's old tail; 537 takes 360's old tail, entered directly from {0}. The ADDs at 407 are re-signed and one is re-sourced (`538 += -1·1522`); every later contact of the two follows the relabel | 360: 3→55→407→824→948→200→127 becomes 3→55→407→416→868→127; 537: 3→407→416→868→127 becomes 3→824→948→200→127 | 27 / 21 |
| E2 | main 176 | drops its stop at chart 1065; `176 += -1/2·379` at 1065 becomes `176 += -1/4·1000` at 928. The same main has this route in #7636's word | 3→449→1065→928→186 becomes 3→449→928→186 | 3 / 2 |
| E3 | helper 236 | drops its fifth stay (chart 928); its two contacts with main 176 at 928 go with it | …→751→928→127 becomes …→751→127 | 3 / 1 |
| E4 | helper 370 | drops its last stay (chart 819); the give to 1132 is re-placed at chart 432 together with one further ADD to 1130 | 3→62→425→432→819→127 becomes 3→62→425→432→127 | 3 / 3 |
| E5 | helper 461 | drops its first stay (chart 285); the read of register 10 at 285 is taken by the co-resident 1214 with coefficient −4 | 3→285→127 becomes 3→127 | 4 / 2 |

E3 is a contact re-chart of the type introduced by Clear1nsight's [#7612](https://github.com/CrocSwap/integer-mult-bounds/pull/7612) and
ToikY's [#7643](https://github.com/CrocSwap/integer-mult-bounds/pull/7643); it becomes legal here after E2 has moved main 176's stop. E1 is
the swap-null relabel of our [#7630](https://github.com/CrocSwap/integer-mult-bounds/pull/7630)/[#7636](https://github.com/CrocSwap/integer-mult-bounds/pull/7636)/[#7641](https://github.com/CrocSwap/integer-mult-bounds/pull/7641)
lineage, with free ADDs repairing the content that the plain composite leaves unsupplied. E4 and E5 come from the search below.

**The search.** Destroy a small region (one interior stay deletion, or one swap pair) of #7641's mid-chart events, then repair it with free
ADDs `x += g·y` between registers that are already co-resident at existing stops (no new MOVEs, so κ moves only through the destroyed
stops). The repair is one forward pass plus one adjoint pass per Newton step, solved modulo a prime with rational reconstruction; a
candidate is accepted only if the joint {0}/V hub test holds, and then it is built and checked exactly (all rows, legality, price). Gates:
destroying nothing rebuilds #7641 byte for byte; destroying the coefficients of three known stays recovers #7641's exact coefficients.

**Joint hub re-settle.** Every ADD/SCALE at the {0} chart and at V is solved jointly and exactly, so all 1,569 final rows and end charts
equal #7641's. The re-derived hubs have 133,936 events (203,062 in #7641), which is why the word is shorter overall. The word has hub
events only of that kind (ADD/SCALE).

**No exact-zero join** occurs in either word; `check.py` detects them with its own exact replay.

## Price

Native paid delta per call {1:−1, 2:−3, 3:−3, 4:−1, 5:+1, 6:+1, 9:+1} (5 fewer MOVEs, some re-ranked); helper targets unchanged. Over 17
calls: paid {1:−17, 2:−51, 3:−51, 4:−17, 5:+17, 6:+17, 9:+17}. Paid positions 108,683 → 108,598; rank surplus S = 1,424 unchanged.
Ordinary bill (17 calls, the repository `independent.py` formula with its call count set to 17): 878,834,276 for #7641 → 809,783,948 for
this word, below 10^9. Coefficients stay 5-smooth. The replayed grid moves from #7641's (2-adic exponent 21, odd lcm 10,125, 30
numerator bits) to (14, 225, 20); odd 3/5-smooth literal divisions go from 26,482 to 6,707 (the odd lcm is 225, against 1,125 in #7637).
Official tools (`price.py`):
- `compare_recursive_invoices` against #7641 gives `uniformly_better`.
- `evaluate_recursive_power` (256 bits) gives `new_cost_lower` at C = 0.0037167669978 and 0.00371676699784, `new_cost_higher` at
  C = 0.0037167669979 and 0.00371676699785, and `new_cost_lower` at #7641's C = 0.0037136318149.

## Checks

```sh
python3.12 -B scripts/research_package.py --package research/p104-lns-on7641
```
`VERIFY.json` registers five commands:
- `core`: words, interior edit list, exact replay and legality of both words, rows, end charts and owned data, zero joins, routes,
  coefficients, invoice and κ.
- `certificates`: all 234 CLEAR certificates, with 2 rejecting controls.
- `controls`: 15 rejecting controls and 2 accepting.
- `columns1`: the column tests.
- `price.py`.

**Census.** #7641 publishes no chart-pair census. The census here is every old- and new-route pair of the six changed registers plus the
4 new MOVE pairs (32 pairs in all: (3,824), (432,127), (449,928), (751,127) are new); `check.py` runs 512 forward and 512 adjoint
Gaussian columns, signed Pauli action, absolute phase, exact ascent rank and a wrong-phase rejection on each. It does not retest pairs this
word leaves untouched.

Independently of the package, the word passed our exact pricer, an independent exact Fraction replay (all 1,569 rows equal #7641's, no
chart, ascent or ownership violation), a replay modulo 2^89−1 and 2^107−1, the repository's `independent.py` native audit (bad_inputs 0)
and caller identity, `full_verify` of the 17-call route including the interval gate on the κ bracket, and its six rejecting controls.

## Conditional premises and what is not rerun

The claim carries exactly #7641's premises (above), over 234 lifetimes with individually certified contents, and the signed #7113 caller
and BIT premise of the base. This package does not rerun #7620's full native/signed 17-stage application, catalogue, outer predicates or
precision/tape counts, nor #7637's own odd-grid and precision accounting: the replayed grid differs from both #7637's and #7641's (above)
and its effect on those counts is not rechecked here. No upstream maintainer has reviewed the package.

## Credit

The base word is our #7641, built on SYLforge's [#7637](https://github.com/CrocSwap/integer-mult-bounds/pull/7637) (the H5B
frame-restored construction), vendored as data with its notices. Its credited lineage: Ali Romman's #7605, Clear1nsight's
#7631/#7633/#7626, Rohan Arun's #7113 signed caller, and the construction inside it from SYLforge's #7616/#7620 and our #7630. The
contact re-chart of E3 follows Clear1nsight's #7612 and ToikY's #7643. The swap-null relabel and the repairs are ours (#7630, #7636, #7641,
#7634). See [NOTICE](NOTICE).
DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

- **Larger neighbourhoods.** The accepted repairs are single-stay deletions whose content is re-placed on the same helper; the same
  destroy-and-repair machinery applies to other neighbourhoods (two-stay destroys, purifier and chart-pair regions) and to other bases.
- **The premises.** A ruling on #7620's inherited assumptions and its CLEAR reading, and on the inherited entrance `initial[457] = 281`,
  decides #7620, #7637, #7641 and this word together.
- **Grid.** Whether #7620's precision/tape accounting absorbs the replayed grid (odd lcm 225) is not rechecked here.
