# The radial cost of finite-order Gaussian rounding

Every injective exact-sum Gaussian-pair rounder with error at most one
and optimal forward radial slack **1/sqrt(2)** has unbounded cycle lengths.
On the sum-one shell of odd difference taxicab radius R, it must have two
cycles of length R or one cycle of length 2R. No finite global order is
possible at this optimum.

For the class with **F^4=id**, the sharp radial optimum is
**sqrt(19)-sqrt(13)**, even without F^2=swap, phase covariance or a
quarter-turn matching premise. The new lower bound combines with
CubeJerry's retained global upper construction from
[PR #7570](https://github.com/CrocSwap/integer-mult-bounds/pull/7570).
The upper construction and its attaining cycle remain prior work.

[PROOF.md](PROOF.md) gives the classification, a positive necessary gap
for every prescribed finite order, and the fourth-power argument.
[RESULT.json](RESULT.json) retains both complete ten-point maps at the
critical ring, all critical exterior edges and the exact cycle checks.
The general finite-order bound is not claimed sharp for other orders.
No new kappa or selected-assumption discharge is claimed.

## Evidence and reproduction

Use CPython 3.12 and its standard library from the repository root:

```sh
python3.12 -I -W error -B research/gaussian-radial-order-classification/verify.py
python3.12 -I -W error -B -O research/gaussian-radial-order-classification/verify.py
python3.12 -B scripts/research_package.py --package research/gaussian-radial-order-classification
python3.12 -B scripts/check_research_commit.py --package research/gaussian-radial-order-classification --check-source-history --check-modes
```

Expected markers are PASS_GAUSSIAN_RADIAL_ORDER_CLASSIFICATION,
PASS_REGISTERED_RESEARCH_PACKAGE and PASS_RESEARCH_COMMIT_BYTES.
The checker enumerates all matchings in 33 complete rings, with exactly
two per ring. Direct orbit traversal and a separate gcd calculation agree
on all 66 maps. All 2244 exterior edges have cost strictly above the
optimal threshold and direct Gaussian error one. The two critical squares
retain their complete boundary costs. Sixteen finite-order gaps and the
source's attaining four-cycle pass exact integer checks. Collision,
forbidden outward-edge and strict-threshold controls pass. A credited
affine control checks 625 inputs and shows that the fourth-power class
is strictly larger than the square-to-swap class.

The all-ring result follows from the written proof. The finite cycle is
not a standalone global upper construction; that conclusion uses the
pinned all-input source proof. Full predecessor package replays, selected
cold replay, Lean and Docker were not run. Independent human and
formal-kernel review are unclaimed.

## Scope and source

The classification is on the sum-one fiber. The no-finite-order conclusion
applies to every global map in the stated optimum class. The fourth-power
lower bound uses no additional symmetry; its upper map is not promised to
have conjugation as inverse. Larger blocks, extra state, changed error
allowances and relaxed sum constraints remain outside this theorem.
No physical provider, native tariff, full caller or complete multiplication
invoice is supplied. The selected frontier and all five assumptions remain.

Base: canonical main e54523517d0f03e58352e647c403a5af3e525a57, priority
revision 8. The uniform-transfer card changes scope to the local precision
and functional-order implication. [TASK.json](TASK.json) records the family
decision and remaining obligations. The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19707892) follows
the exact-sum handoff. Live handoffs, source-reference intake, refreshed
PR/Discussion overlap and the complete closed snapshot with an updated-order
delta show no competing claim. Sparse local and unpublished work remain
coverage limits. Affine translation periods are a different model.

## Open next questions

For a specified finite order other than four, what global construction
attains the best possible radial budget? First fix the order, conserved
observables and error allowance. A necessary gap alone does not establish
its optimum. A larger-block or stateful caller needs a separate contract.

## Credit

Prepared by Ali Romman with substantial OpenAI Codex assistance.
Credit CubeJerry/Jerry Chen for the half-grid and prior upper construction,
Ali Romman for the global optimum and ring map, and Nick Petalas for the
forward-only exact-sum question. [CREDITS.md](CREDITS.md) links the exact
proofs and distinguishes the new classification/lower bound from prior
constructions. New work is Apache-2.0.
