# What PR2435's entrance raise really changes, and what further raises are worth

**Research note (structural pricing screen); no κ claim.**
[PR2435](https://github.com/CrocSwap/integer-mult-bounds/pull/2435) (Jeremy Kothe) reports a conditional +1.3164e-6 in κ. It raises
the entrance frames of 24 copy-buffer helpers per word from dimension 1 to 2 on
[PR2322](https://github.com/CrocSwap/integer-mult-bounds/pull/2322)'s words. This is a frame-only change; see
[PR2446](https://github.com/CrocSwap/integer-mult-bounds/pull/2446). The note decomposes the change and prices the
move class.

## Findings

1. **The raise is a width exchange paid for by the partners.** Recounting per register shows that 96 registers
   change in both providers:
   - the 24 raised helpers each turn a rank-3 child into rank 2 and drop from width 8 to 7, a delta of
     {3:−24, 2:+24};
   - **72 gate partners (6 X registers, 66 helpers) change their child profiles**: 48 replace one
     rank-3 child by rank 2 + rank 1; the other 24 replace rank 3 + rank 1 by two rank-2 children.
     The aggregate delta is {3:−72, 2:+96, 1:+24}. Both changes increase the moment for 0 < a < 1.

   The net gain comes mainly from packing: width-7 helpers fill the rank-16 bins exactly as [7, 9].
2. **The width-aware LP reproduces the realized gain.** The PR2387 bin-pattern LP ceiling moves by +1.3166e-6
   from PR2322 to PR2435. The proposed conditional κ gain is +1.3164e-6; this comparison does not validate its supplier admission.
3. **The sampled further-raise price ladder saturates quickly.** The price of k more raises at PR2435's point, each
   changing one helper from width 8 to 7:

   | k | average PR2435 pattern, partners included ({1:+1, 2:+5, 3:−4} per raise) | own climb only, no partner splits ({2:+1, 3:−1}) |
   |---|---|---|
   | 1 | +3.05e-8 | +3.84e-7 |
   | 4 | +1.22e-7 | +1.54e-6 |
   | 10 | **+3.05e-7 (best sampled)** | +3.85e-6 |
   | 12 | +9.6e-8 | **+4.35e-6 (best sampled)** |
   | 16 | −1.40e-6 | +4.26e-6 |
   | 26 | −6.02e-6 | +3.15e-6 |

   Among the sampled counts, the largest gain under PR2435's average partner cost is at k=10,
   about +3e-7; k=12 remains positive, while sampled k>=16 are negative. The script checks
   k in {1,2,4,6,8,10,12,16,20,26}, not every integer or every possible site combination. Partner splits consume about 92% of each raise's raw value.
   A raise whose partners do not split would be worth about 12 times more.
4. **The remaining sites.** On the PR2435 words, 112 entering helpers still enter at dimension 1.
   - Their (width, first climb) shapes are {(7,2): 30, (8,2): 26, (8,3): 52, (8,4): 4}. The 26 width-8,
     first-climb-2 helpers have the same shape as PR2435's 24.
   - For every one of them, the first gate sits at the entrance frame. For only 16 do those gates lie in A
     alone; the rest also have entrance-frame gates in B.
   - So any further raise is a joint frame refit with partners. In a scratch attempt outside the registered
     script, raising a single helper together with its A-gate frames failed nesting with partners for all 16
     A-only sites.

**Takeaway for the T74 line.** The entrance-raise lever left at PR2435's point is small, about +3e-7 under
average partner costs. It is worth pursuing only for sites whose partners are already at the raised frame, which
is a question for an exact frame re-solve with entrances as variables.

## Reproduce

From the repository root, standard library only:

```sh
python3 -I -B research/t74-entrance-raise-prices/entrance_raise.py --fetch    # ~25 s
```

`--fetch` fetches `refs/pull/2322/head` (002304ef) and `refs/pull/2435/head` (324d7d35) if absent. The four
words are blob-pinned. The vendored tools are this author's PR2387 `fill_check80.py` / `ceiling_lp.py` /
iteration-3 `price_check.py`, pinned.

Expected final line:
`PASS_T74_ENTRANCE_RAISE lp_gain=1.3166e-06 realized=1.3164e-06 best_further=+3.051e-07@k=10 own_only_k1=+3.839e-07 no_new_kappa`

All results were run on CPython 3.14.4; the registered Python 3.12 replay was not run locally.

## Scope and limits

- **Prices.** These are floating-point LP-root estimates on the fixed T74 bin stock, not directed
  rational certificates or a global optimization over possible raises. The discrete register recount is exact.
  The "average" ladder assumes each further raise has PR2435's average partner cost; actual sites differ.
- **Legality.** No raise is constructed or proven legal. Entrance delivery and native wrappers (Lemma A of
  PR458) are the open obligation, as in PR2446.
- **Interactions.** The ladder holds owner fills at their LP optimum and ignores interactions with other moves.

## Open next questions

- **Partner-split-free raises.** Which of the 112 remaining sites can be raised without partner splits?
  First step: run an exact frame re-solve with entrance frames as free variables, and keep raises whose
  partners' climbs do not split.
- **Raising further.** Do raises beyond dimension 2 pay? Examples are PR2435's 24 taken to their first-gate
  frame, or the 52 first-climb-3 sites. First step: extend the ladder to width 8 → 6 changes and price them.

## Credits and licence

- PR2435 / PR2374 / PR2312 (Jeremy Kothe): the entrance raise and the T74 line.
- PR2322 (Vlado Vojdanovski): the words.
- PR458 (chafreaky): Lemma A wrappers.
- PR2360 (Jeremy Diviney) and PR1129 (Ali Romman): the pattern-dual relaxation.
- PR2387 / PR2402 / PR2446 (this author): the tools, vendored with pins.

Prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). No independent human review is
claimed. Apache-2.0.
