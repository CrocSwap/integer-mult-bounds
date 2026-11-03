# A ceiling for every monotone frame assignment on two P104 words

**No new kappa is proved.** This package excludes a large gain from a whole
class of frame changes, including joint changes that a local search can miss.
For the exact PR6529 scalar word, every allowed assignment fails at
**kappa 0.003293** and at every larger value through 0.0034. The fixed mixed
root can use every positive child size, every binary tree, and a different
allowed native variant at each leaf. Thus this class has less than
**0.143 percent** headroom over PR6529's reported 0.003288299.
At the 0.003293 ceiling, different leaves can also use different source words.

A second result applies to **any root in the stated fresh-stage billing
model**, not only this fixed root. Its favorable raw-budget search needs at
most **22 leaves per binary child** for kappa>=0.003293, or **21 leaves** at
the current one-percent target 0.00332118199. The proof gives a bound on each
child increment, with no bound on the number of root fields or full sites.
This converts an unbounded child-size search into a finite one. It does not
provide a new root or a positive invoice. See `PROOF.md`, Section 6.

The proof keeps the scalar events, contact equalities, public forward moves,
owned reverse moves and main boundaries. It permits all binary subspaces at
all contacts, including new subspaces absent from the source. Helper input
and output frames can change. Every paid rank and changed helper credit is
charged. A rank-zero helper has zero credit. The proof also covers PR6453,
with ceiling 0.0032915. These ceilings do not apply to a changed scalar word,
nonnested Clifford frames, different main boundaries or a different caller.

| Exact source | Native saving upper bound at its ceiling | Caller ceiling |
| --- | ---: | ---: |
| PR6453 | less than 0.053864 | 0.0032915 |
| PR6529 | less than 0.053888 | 0.003293 |

The saving is the paid-minus-helper moment per native call, before division
by 104. It is not a kappa increment. The full raw caller margin is negative
at each ceiling. Ordinary work, routing, precision, compiler and outer fees
are granted zero cost in this exclusion. Adding their nonnegative costs
cannot repair the failure. This is a necessary-budget proof, not a new
supplier or a replay of the complete multiplication theorem.

`PROOF.md` gives the domain, its reduction to exact constraints, the rational
dual bound and the all-size tail. `RESULT.json` contains exact fractions.
The two models have 119,534 and 119,463 inequalities. Their original words
satisfy every constraint and reproduce the complete signed local invoices.
The original 7,2,2,7 callers pass their published raw prices as controls.
Four rational certificates supply the price and uniform derivative bounds.
A solver is not required for replay.

## Reproduction

Use Python 3.12 and the standard library:

```sh
python3 -I -B research/p104-monotone-frame-ceiling/verify.py
python3 -I -O -B research/p104-monotone-frame-ceiling/verify.py
python3 -B scripts/research_package.py --package research/p104-monotone-frame-ceiling
```

The default replay is read-only. It authenticates every retained predecessor,
rebuilds both models, checks all dual coefficients and residuals, and compares
its full result with the retained receipt. `--write` replaces that receipt
with a fresh result. `SOURCES.json` records exact original heads, paths, Git
blobs and SHA256 values. The retained bytes permit offline replay without
pending branch objects or a Git checkout.

`VALIDATION.md` records completed checks and their limits. Local exact replay
is author-side evidence. Independent scientific review, formal proof-kernel
acceptance and the five framework assumptions remain separate obligations.
The selected frontier is unchanged.

## Open next questions

- Change the scalar word or its contact graph. Identify a precise chronological
  value relation that removes paid work. Prove every public endpoint and charge
  each target loss before using the new invoice.
- Change the frame contract or caller. Nonnested Clifford coframes and different
  query roots are outside this theorem. Check current claims first, then prove
  one complete endpoint and price it. The structured questions are in `TASK.json`.

## Credit and coordination

New proof, exact certificate and checker: Ali Romman with substantial OpenAI
Codex assistance; no subagents. Weak duality, dimension inequalities and
interval series are classical methods. The source-specific combined model,
uniform bound over all frame assignments and leaf mixtures, and complete
all-size caller consequence are this contribution.

PR6529 supplies the scaled transport word. Erwan L. supplies PR6453's third
anchor; Rohan Arun supplies the PR6399 merge and PR6417 composition;
DreamingOfClouds supplies the shared-carrier lifts. PR6398 supplies the mixed
root, normalization, binary-tree recurrence and concave tail. The earlier
P104, Gaussian, helper, BIT, compiler and analytic authors retain their credit.
Their source notices are copied unchanged under `input/`. See `NOTICE`.

The canonical investigation is [Discussion5593, comment19362959](https://github.com/CrocSwap/integer-mult-bounds/discussions/5593#discussioncomment-19362959).
Main, priority 8 and selected6030 were checked before work and at each pivot.
The general coframe, period-six caller, source-word and intermediate-retirement
claims were kept separate. The overlap snapshot cannot cover unpublished work.
The user's requested large complete kappa improvement remains unmet.
