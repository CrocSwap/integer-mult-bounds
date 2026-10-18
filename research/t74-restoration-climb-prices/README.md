# End-of-call restoration climbs on the T74 PR2322 words: census and prices

**Research note (pricing screen); no κ claim.** This note finds the largest remaining paid item on the
current T74 line that is pure restoration work, and prices it. The PR2322 words underlie the open
PR2349 / PR2363 / PR2374 line.

**What the restoration climb is.** A *FULL-cleanup* helper climbs from its last gate frame to FULL at
the end of every call, only so that the inverse-reverse cleanup can run at FULL. That end climb pays
recursive children. A *cold-restored*, hyperplane-ended helper ends at its last frame instead and pays
no end climb. This mechanism comes from PR601's commuting cleanup, PR604/PR617's cold ends and PR2226's
exact cold restoration. Its cost is one private zero buffer.

| item (both providers, per call) | value |
|---|---|
| FULL-cleanup helpers / cold-restored helpers | 356 / 78 |
| end climbs of FULL-cleanup helpers | {1: 249, 2: 42, 3: 64}: **525 rank units, 9.8% of the local paid mass (5,371)** |
| end climbs of cold-restored helpers | none |
| one more cold-restored helper, end climb 1 / 2 / 3 (widths 8–9) | **+5.77e-7 / +1.04e-6 / +1.46e-6** in the LP ceiling b |
| one more cold-restored width-5 helper (end climb 1) | 0 |
| all 249 / 42 / 64 of one end-climb class | +6.31% / +2.33% / +4.00% |
| ideal: all 355 | **LP ceiling 0.0018806 (+10.8%)** |

For comparison, on the same words a PR2322-type handoff is worth +4.27e-8 and all remaining owner-fill
headroom is ≤ 8.1e-10 ([PR2402](https://github.com/CrocSwap/integer-mult-bounds/pull/2402)). One more
cold-restored helper is worth 14–34 times a handoff.

## Buffer capacity in the inherited accounting

The cost context is read from PR2374's pinned SPEC, OUTER-CLAIM and invoice.

- κ = C − 1/F − B with F = 1e3046 and B = 1e-3022, where C is the certified complex endpoint. Zero
  buffers, their CLEARs, adapters and routing reserves enter κ only through admission inequalities,
  and those must be rechecked for a proposed changed supplier. This script checks the stated formula and stock capacity, not every admission inequality.
- The physical stock would go from 66,826 to 67,181 with all 355 converted. The parent capacity is
  112,178.
- PR2322's private-namespace bound on zero buffers, NZ ≤ R = 434, would be 433. It fits.

Cold ends are a known move class on earlier word families: open #636/#640 (vectorsss), #676 (Jeremy Kothe,
"six dim-8 cold ends") and #685 (chafreaky, "72 cold ends"). What is new here is a census and price of the
move on the live T74 PR2322 words.

The open mechanism question is **legality**: can each helper's cleanup be moved before its end climb? The counted buffers fit the inherited stock capacity. This does not prove that every changed adapter, routing reserve, precision charge or admission inequality will fit.

The existing constructions already apply PR601's *sufficient* commutation test (a preceding gate that
only reads the cleanup partner, with the two additions commuting). They also apply PR604-style
multi-gate cold tails to some helpers. The 355 remaining helpers are presumably those that the
sufficient test, as implemented, rejects. The prices above are what a **stronger exact commutation
test, or a changed cleanup contract,** would be worth per helper. #1995/#2013 fix the cleanup contract,
so this is outside their scope.

## Method and checks

- **`restoration_prices.py`.** It recounts both pinned PR2322 words with the vendored PR2387
  frame-climb rule, patched only to record which register and phase pays each child. Each recount
  equals the word's reported profile. The script reads PR2374's pinned files for the cost context.
  It then prices conversions with the PR2387 width-aware bin-pattern LP, extended to widths 3–9
  (8,953 patterns). A converted helper loses its end-climb child and its width drops by the end climb.
  The extended LP reproduces the PR2322 LP ceiling as a control.
- **Independent recount.** A separate AI reviewer subagent wrote its own GF(2) replay from a plain
  statement of the rules. It agreed on every census number in both providers: profiles, 356/78,
  end-climb histogram {0:1, 1:249, 2:42, 3:64}, and the (width, end climb) classes.

## Reproduce

From the repository root, standard library only:

```sh
python3 -I -B research/t74-restoration-climb-prices/restoration_prices.py --fetch   # ~2.5 min
```

`--fetch` fetches `refs/pull/2322/head` (002304ef) and `refs/pull/2374/head` (5449da65) if they are
absent. All inputs are blob- and sha256-pinned.

Expected final line:
`PASS_T74_RESTORATION_PRICES full_cleanup=356 end_climb_mass=525 convertible=355 one_d1=+5.767e-07 one_d3=+1.463e-06 ideal=+10.80% no_new_kappa`

All results were run on CPython 3.14.4; the registered Python 3.12 replay was not run locally.

## Scope and limits

This is a census plus a pricing screen. **No conversion is constructed or shown legal.**

- Prices are floating-point estimates of LP-ceiling differences on the fixed PR2322 bin stock; windows and families are dropped. The discrete census is exact, but these price values have no directed rational enclosure in this package.
- They assume that moving a cleanup earlier changes no other register's climbs. PR601's review states
  that the intervening partner climbs remain paid. Any restoration tail of PR604 type, any premix and
  any added scalar work would have to be priced on the actual word.
- The ideal +10.8% is the numerical value of the optimistic LP relaxation for this lever, not a rigorously enclosed numerical bound or an achievable figure.

## Open next questions

- **Stronger commutation test.** Which of the 355 FULL-cleanup helpers admit an earlier cleanup under
  an exact commutation test, rather than PR601's sufficient one? First step: for each helper, compute
  the maximal suffix of the call's gates that commutes with its cleanup gates, exactly over the dyadic
  scalars, starting with the 64 end-climb-3 helpers worth +1.46e-6 each.
- **Cold tails.** Can a PR604-style cold tail restore one end-climb-3 helper on the PR2322 words, and
  at what price once its tail gates' frames are counted? First step: take PR604's tail constructor,
  apply it to one helper, and recount the word with this package's recount.
- **Same audit on the selected word.** Does the selected k8 word, with its 402 FULL-cleanup helpers
  (#2013), carry the same end-climb mass? First step: run this census on the selected word's frame
  paths.

## Credits and licence

- PR2322 (Vlado Vojdanovski): the words.
- PR2374 / PR2349 (Jeremy Kothe) and PR2363 (mason-hale): the outer, invoice and buffer accounting read
  here.
- PR601 / PR615 / PR617 / PR676 (Jeremy Kothe), PR604 (DreamingOfClouds), PR608 (higherbeing), PR636 / PR640
  (vectorsss), PR685 (chafreaky) and PR2226 (Cinna Davis): cold, hyperplane-ended helper mechanisms.
- PR1995 / PR2013: the fixed-contract frame bounds.
- PR2387 / PR2402 (this author): recount and LP tools, vendored with pins.
- PR2360 (Jeremy Diviney) and PR1129 (Ali Romman): the pattern-dual relaxation.

Prepared with substantial AI assistance (Claude Code, Anthropic, Claude Opus 5.5). An independent AI
subagent re-derived the census; no independent human review is claimed. Apache-2.0.
