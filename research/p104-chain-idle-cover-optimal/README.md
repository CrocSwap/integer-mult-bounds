# Idle cover, top targets and shape optimality of the chain-nested root (no κ)

**No new κ.** This package proves lower bounds and a structural theorem about the chain-nested root of #6833, checks them
exactly on the literal words, and records what is not covered.

## Results

1. **Idle cover (Theorem 1).** For the chain-nested root of shape `(g|g)` (site `i` has `|M_i| - 2 = i` idle directions), every
   cover by whole idle jobs, each lying on one side, with a native active part of rank at most two and price `H(8m) = (8m)^t` for
   `0 < t ≤ 1`, costs at least `2 Σ_{s=1}^{g-1} H(8s)`. For `0 < t < 1` equality holds exactly for job lengths `g-1, ..., 1` per side,
   which is the chain. The proof is rank subadditivity, a Gale-Ryser majorization of the job lengths and Karamata's inequality.
   Targets are fixed by the masks, so every other cover has a strictly larger paid side. No idle line is transported from a left site to a
   right site through the three thin queries (exact, `g = 3, 4, 9`).
2. **Top targets (Theorem 2).** For a shortest root (`n` fields, `n + 1` square-zero queries, constant bases, one variable per
   site, `J = -I`): the rank-one Gram identity forces a field in every full mask (target rank `8W + 1 = 145` for 18 stages), and
   the three largest target ranks sum to at least `16W + 3 = 291`. The multiset `{145, 73, 73}` of #6726 and #6833 attains it; the sum is
   forced, the split `73 + 73` is not.
3. **Retirement (Proposition 3).** On #6726's root, the two published retirements are mask reductions and give exactly the masks
   of the chain gate `(4,4,1|1,4,4)` up to relabelling; the outer histograms differ by one cancelling pair of rank-32 jobs; the
   literal chain `(9|9)` word has no retirement candidate. The general statement is not proved.
4. **Shape (Proposition 4).** At the 18 stages of the retained native word, `(9|9)` is the unique best chain shape on both the
   complex histogram (crossing `0.00337180047549672`) and the binary histogram (crossing in `(0.0038525393934, 0.0038525393935)`):
   all `2^17` compositions per side were searched; the runner-up `(8|10)` loses `1.5e-6` (complex) and `1.9e-6` (binary) in `κ` at first order.

## Hypotheses and scope

Theorem 1 needs one-sided jobs, an active part of rank at most two per site, a concave increasing price, one stage per site; jobs spanning
both sides, native stages of rank three or more, and convex prices lower the minimum (controls in `verify.py`). Theorem 2 needs `J = -I`,
exactly `n + 1` queries, a polynomial product identity and one variable per site (tree children enter only through weights). Proposition 3
is finite. Proposition 4 is the additive ledger of the chain-nested family, checked against four built words and the literal `CALLER.json`;
shapes outside the four are priced by the formula, and only `N = 18` uses a literal native word. Pricing, native phases and the five
framework assumptions of the cited words are not re-derived and no κ changes.

## Exact checks

| Item | Check |
|---|---|
| Idle cover | literal #6833 idle jobs against the demand of all 18 sites; exhaustive minimum for `g = 2..9`; 4,000 random covers; no transported spanning line (81 site pairs at `g = 9`) |
| Top targets | root identity at random `D`; rank-one Gram on all triples; residual identity on all 306 ordered pairs; top ranks `145, 73, 73`; same hypotheses on the #6726 root |
| Retirement | masks of #6726 with the two pivots removed against the gate; histogram difference `{T32:2, P32:2}`; census of the chain word (none) and of the unretired #6726 caller (cuts 158, 383, 392) |
| Shape | ledger against literal events; exhaustive search at `N = 18`; dynamic program for `N = 10..40` (scaled native, a model) |
| Controls | fourteen: convex price, spanning jobs, active rank three, deleted job, other lengths, perturbed query, flipped sign, flipped triple, wrong masks, census sensitivity, changed native histogram, other shapes |

## Reproduce

Python 3.12, standard library only. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-chain-idle-cover-optimal
```

or directly (about 20 s):

```sh
python3 -I -B research/p104-chain-idle-cover-optimal/verify.py
```

Expected markers: `PASS_CHAIN_IDLE_COVER_OPTIMAL`, and for the launcher `PASS_REGISTERED_RESEARCH_PACKAGE`.
`retained/` holds unmodified copies of the inputs with their pull-request pins in `retained/SOURCE-PINS.json`;
`SOURCES.json` binds the base-commit files.

## Relation to earlier work

#6833 (DreamingOfClouds) gives the chain-nested root, its caller and the chain merge; this package adds the lower bound on the idle cover,
the all-field and top-target statement and the shape search. #6832 supplies the `N ≥ r + 1` count used in the setting. #6827 supplies
the retirement census, #6726 (zxv) the root, witnesses and the binary native word, #6716 (thu-nmrc) whole common idles and the pricing of
paid jobs, #6834 the binary transfer whose crossing is reproduced.

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude Code. Apache-2.0.

## Open next questions

* Is there an idle job that spans a left and a right site once it may be conjugated through the other sites it does not commute with,
  or be non-contiguous or non-idempotent?
* Is every retirement of a shortest root the reduction of one mask?
* Does `(9|9)` stay optimal among roots whose masks are not chain-nested (two all-fields, fields supported on both sides)?
