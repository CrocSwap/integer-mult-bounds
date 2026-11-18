# A word obstruction for every extremal irreducible binary core

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.

Consider binary scalar calls `I+([A_j]-1)P_j` over the paid-generated
torsion-free exponent group. Suppose the occurring projectors are
noncoordinate rank-one idempotents, their pattern dimension is `k>=2`,
their joint image is irreducible of dimension `2k-1`, their saturated
exponent relation rank is at most k, and the full ambient endpoint is
diagonal monomial.

Then all bridge calls lie in one consecutive block and their exponent
sum is zero. Deleting that block preserves the full ambient operator,
including spectator-input columns. The target exponents are sums of
disjoint paid subsets, so total rational target rank cannot exceed
paid rank.

Read [PROOF.md](PROOF.md), [RESULT.json](RESULT.json), [CREDITS.md](CREDITS.md)
and [TASK.json](TASK.json). The proof extends the prior five-core
restricted word theorem in
[PR #6782](https://github.com/CrocSwap/integer-mult-bounds/pull/6782).
The full ambient conclusion uses the unique ambient link from
[PR #7693](https://github.com/CrocSwap/integer-mult-bounds/pull/7693).

## Reproduce

Use CPython 3.12 and its standard library, from the repository root.

```sh
python3.12 -I -W error -B research/extremal-core-word-obstruction/verify.py
python3.12 -I -W error -B -O research/extremal-core-word-obstruction/verify.py
python3.12 -B scripts/research_package.py --package research/extremal-core-word-obstruction
```

Expected markers are `PASS_EXTREMAL_CORE_WORD_OBSTRUCTION` and
`PASS_REGISTERED_RESEARCH_PACKAGE`. The verifier compares its result
with the committed receipt and writes no file.

It checks 88748 degree-two type orders, 20532 full Laurent type orders,
the star quotient through 20 edge pairs, and ten ambient deletion
fixtures with nonsymmetric fresh factors and dirty spectators. Wrong
bridge signs, one extra relation and an incorrect ambient parity
kernel have explicit controls. The finite checks corroborate the
written all-length proof; they do not replace it.

## Limits

Coordinate calls, reducible or smaller images, and larger relation
budgets are outside this theorem. The one-extra-relation control
breaks the chronology claim but gives no rank saving. The normal-form
shear is a proof device, not a free physical operation.

No native supplier, rounding contract, complete multiplier invoice
or new kappa is supplied. The selected frontier and its five assumptions
remain unchanged. Independent human and formal-kernel review are
unclaimed. Full predecessor package replays, selected cold replay,
Lean and Docker were not run.

## Open next questions

Can a specified subextremal or reducible core, or an explicitly larger
relation budget, support a legal saving? Give the exact alphabet and
full paid/target invoice before searching. A scalar word would still
need native realization, dirty-state restoration and a complete cost
and precision account.
