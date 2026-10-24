# Shared exit-chart visit for the centre-chain observation

**Scoped negative result. No new κ.** The selected conditional exponent stays
`60403/20000000`.

#4839 shows that stripping every touched register of the heterogeneous
centre-chain terminal loses on `C in [0,1]`. Its open question is whether one
changed physical word can avoid those chart strips and still preserve the
observations, the centre-to-Y corrections, and the original returns.

This package gives one such word. Every observation support already exits on
chart 1, and every affected Y chart is a width-8 subspace of chart 1. Each
selected centre makes one width-9 round trip onto chart 1. Each distinct Y
field makes a width-1 hop up to that chart, subtracts, and hops back. The
scalar endpoint matches the strip-all terminal on all eight singletons, all
28 pairs, and the octet. The raw inverse transpose matches for the same 37
words.

The incremental moment stays negative. For centre 0 the new bill is 112
width-1 requests and 2 width-9 requests, against one optimistic rank-8
reward. Its upper bound on `t = 1-C in [0,1]` is `-113`. Granting the width-9
round trip for free still leaves `-104`, because one rank-8 reward is worth
at most 8 and the width-1 hops cost 112. The strip-all bill for the same
endpoint was 112 width-8 requests and 114 width-9 requests.

The argument and the exact census are in [PROOF.md](PROOF.md). The machine
receipt is [RESULT.json](RESULT.json).

## Scope and evidence

Task card: `complex-new-helper-inventory`, refined to handoff
[#1166 comment 19133212](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133212)
and the first open question of #4839. The scope change is recorded in
[TASK.json](TASK.json). This does not beat a packing ceiling and does not
propose a new helper alphabet outside the retained chart model.

Base commit `ff3cc58e370d0f678e529246f8c73e8094e18fcf`. Live inputs are the
#4694 emitter, its ABI and native payload, and the helper-normalization
header. Pins are in [SOURCES.json](SOURCES.json).

Not run: a fresh Clifford lowering, a rounded or fixed-tape execution, and
any compiler or outer admission check. Unknown costs are not treated as a
reason to continue this schedule. The sign is already negative with those
costs set to zero.

## Reproduce

Python 3.12, standard library, from the repository root. The registered
command takes about one minute here.

```sh
python3 -B scripts/research_package.py --package research/shared-chart-centre-visit --check-only
python3 -B scripts/research_package.py --package research/shared-chart-centre-visit
python3 -B research/shared-chart-centre-visit/verify.py
```

The direct command prints `PASS_SHARED_CHART_CENTRE_VISIT_STILL_LOSES no_new_kappa`.

## Open next questions

1. Can a producer whose Y registers do not each occupy a private width-8
   subspace of chart 1 avoid the 112 width-1 hops while restoring every
   demanded output? The present loss survives even if the centre’s width-9
   round trip is free, so another visit to chart 1 is not the missing saving.
   First step: name a source-bound exit frame in which at least two affected
   Y fields already coincide, and price one correction there. Blocked by the
   actual frames: the 112 Y charts are pairwise distinct.
2. Does a changed output contract, rather than a changed transport, delete
   the centre-to-Y corrections? First step: state which of the 56 centre-0 Y
   outputs may legally stay contaminated, and reprice only the retained
   corrections. Blocked until that demand is part of the caller, not an
   omission inside this terminal.

## Credit

The terminal loss, evaluator contract and 640-input offer are Chris R /
Clear1nsight’s #4839, using Cinna Davis’s #4694/#4698 interface and Cao
Yifan / intqwq’s #4610 route, with the retained helper-normalization and
Clifford lineage named in that package. This package does not modify those
sources.

Prepared by unpaidmoon with substantial Cursor Grok assistance. New work is
Apache-2.0.
