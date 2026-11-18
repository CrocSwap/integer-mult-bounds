# The sharp global exact-sum Gaussian rounding bound

The minimum forward radial slack for an injective exact-sum Gaussian-pair
rounder with Euclidean error at most one is **1/sqrt(2)**. A stated
bijection attains this supremum and has the same inverse and absolute
radial suprema. Every finite input has a strictly smaller radial change.
The lower bound needs no phase, order, period or surjectivity condition.

[PROOF.md](PROOF.md) gives the full Hall family and the individual-ring
construction. [verify.py](verify.py) is a direct integer implementation
with an explicit inverse. [RESULT.json](RESULT.json) records the exact
checks. This resolves the global question left by
[PR #7673](https://github.com/CrocSwap/integer-mult-bounds/pull/7673);
its finite lower bound sqrt(13)-3 is strictly below the global optimum.

## Evidence and reproduction

Use CPython 3.12 and its standard library from the repository root:

```sh
python3.12 -I -W error -B research/gaussian-exact-sum-global-optimum/verify.py
python3.12 -I -W error -B -O research/gaussian-exact-sum-global-optimum/verify.py
python3.12 -B scripts/research_package.py --package research/gaussian-exact-sum-global-optimum
python3.12 -B scripts/check_research_commit.py --package research/gaussian-exact-sum-global-optimum --check-source-history --check-modes
```

Expected markers are PASS_GAUSSIAN_EXACT_SUM_GLOBAL_OPTIMUM,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The checks cover 129 complete rings with 66564 points, 14641 Gaussian
pairs in the full cube [-5,5]^4, 80 signed inputs through 4097 bits,
32 complete Hall squares and rational-threshold neighborhood counts.
They check direct ideal errors, both inverse identities, exact radial
inequalities, translation/swap covariance and failure controls.
Finite checks corroborate the written all-input proof.

## Contract and limits

The map preserves exact sums, common Gaussian translations and wire swap.
It is exact on integral ideal images. Its negative provider is the stated
inverse formula. Phase covariance and the square-to-swap identity fail.
The distinct stronger class in
[PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570)
has optimum sqrt(19)-sqrt(13); the new map cannot replace that contract
without an explicit caller change. No tensor commutation is supplied.

No physical finite-width graph, range envelope, scratch restoration,
tape cost, native tariff or complete caller is supplied. No new kappa or
selected-assumption discharge is claimed. The selected frontier and all
five assumptions remain unchanged. Full predecessor scientific replays,
selected cold replay, Lean and Docker were not run. Independent human
and formal-kernel review are unclaimed.

## Source and scope

Base: canonical main e54523517d0f03e58352e647c403a5af3e525a57, priority
revision 8. [SOURCES.json](SOURCES.json) pins selection and task metadata.
The uniform-transfer card changes scope to this exact local precision
contract; [TASK.json](TASK.json) records the boundary and remaining costs.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19707397) follows the existing exact-sum handoff.
Fresh open PR and Discussion checks, source-specific PR intake and the
complete closed snapshot with its updated-order delta show no competing
global claim. Sparse local and unpublished work remain coverage limits.

## Open next questions

Can a pinned caller accept the explicit inverse and missing phase/square
identities? First state its algebraic requirements and ordered-stage
contract. A physical implementation also needs complete range, temporary,
restoration and bit/tape costs. A numerical optimum does not discharge
these obligations.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Credit Nick Petalas for the exact-sum forward question and first finite
witness, CubeJerry/Jerry Chen for the half-grid and annular geometry,
and Ali Romman for the next finite witness and ideal pair.
[CREDITS.md](CREDITS.md) links the exact proofs and identifies what is new.
New work is Apache-2.0.
