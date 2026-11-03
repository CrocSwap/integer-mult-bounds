# Post-call B/C helper feedback does not raise the moment

**Scoped negative screen. No new κ.** The selected conditional exponent stays
`781451/250000000`.

Ali Romman's whole-caller capacity gate shows that separated B and C calls
have a strictly negative complete moment for every saving exponent in `(0,1)`.
That argument leaves shared helper feedback unpriced. This package prices one
such feedback: after the call returns, ordinary complex-linear use of its
helper rows, including use of those rows as ingredients of later coordinate
Gaussian targets.

The character budget of those rows is exactly the separated helper moment
`H(t)`. Mixing them into the main output can move that budget. It cannot
duplicate it. With the audited paid profiles held fixed, the complete moment
remains at most

```text
F(t) <= -L_B Delta_B(t) - L_C Delta_C(t) < 0
```

for every `0<t<1` as soon as one B or C call is present. The same mass split
as the capacity gate gives the sign: B's residual rank masses are `4567`, and
C's are `4576`, with positive ranks at most 5 and negative ranks at least 6.
On the central-axis character the B helper block is already fully busy, 408
flipping rows plus the main cut of 112, so one extra flipping target does not
fit.

The argument is written in [PROOF.md](PROOF.md). The machine receipt is the
verifier below. It recomputes the 256-mask cut identity, both helper-block
distance polynomials, and the residual masses from the profile rows pinned in
the predecessor proof.

## Scope and evidence

Task card: `complex-new-helper-inventory`, scope **changed**. The card asks
whether a changed helper inventory can earn productive credit that survives a
complete bill. The concrete question is the open shared-producer gate in
[the capacity-gate README](../complementary-caller-capacity-gate/README.md),
which is the successor of handoff
[#1166 comment 19133514](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19133514)
after the fixed-224 serial loss. Discussion
[#5628](https://github.com/CrocSwap/integer-mult-bounds/discussions/5628)
is that gate's canonical thread.

This is not a decoder for the selected PR6030 word, and it does not spend
the #5599 helper-subspace credit. The connection to the bottleneck is the
revision-8 decoder/interface row: one changed producer contract, priced with
its optimistic full signed bill, stops when that bill is negative.

Base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`. The live input is
`research/complementary-caller-capacity-gate/PROOF.md` at that commit.

Not run: a native word replay, a Clifford phase suite, Lean, compiler or
outer admission, and the selected `make frontier6030-verify` cold replay.
Internal native rewrites that delete a paid factor, and maps outside the
coordinate algebra, are not claimed impossible.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3 -B research/shared-helper-feedback-bound/verify.py
python3 -B scripts/research_package.py --package research/shared-helper-feedback-bound --check-only
```

The direct command prints `PASS_SHARED_HELPER_FEEDBACK_BOUND` and
`no_new_kappa`.

## Open next questions

1. Can a helper read inside the native word delete a paid Gaussian and still
   leave a positive complete moment? First step: exhibit one internal use,
   the deleted paid factor, and the replacement endpoint, then rerun the
   paid-minus-helper mass split. Blocked until that word exists; this screen
   keeps the audited paid profiles fixed.
2. Can an odd input gauge or a noncommuting address map between calls evade
   the sign-cut charge? First step: name the gauge, its preparation cost, and
   one character on which the rank distance falls. Blocked because those maps
   are outside the coordinate algebra used here.

## Credit

The separated capacity theorem, the audited B/C profiles, and the statement
that helper feedback needed its own bill are Ali Romman's. The fixed-224
serial loss that this handoff continues is Chris R / Clear1nsight's, from
Dugongue's B/C source and Cao Yifan / intqwq's audit. This package does not
modify those sources.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
