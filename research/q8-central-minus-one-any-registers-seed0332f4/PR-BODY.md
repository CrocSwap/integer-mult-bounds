## Result

This adds a uniform four-call minimum for the 12 mixed diagonal targets in `F2[Q8]` with one central `[-1]` entry and two `{[i],[j]}` entries, for every finite register count `r >= 3` and arbitrary dirty identity-target roles.

The direct word costs four calls (`2+1+1`). In `J/J^2`, the traces of the two generator coefficient matrices force every exact word to have even length. At length two, the exact central term `[-1]+[1]=([i]+[1])^2=([j]+[1])^2` is absent: with equal labels, the two rank-one idempotents that sum to the rank-two target projection have zero product; with different labels, the first-order matrices force distinct coordinate projections, also with zero product. Thus lengths zero through three are impossible at every finite width.

This resolves the arbitrary-dirty-role gap left by Q8 PR #1925 for these 12 tuples. PR #1925's `r=3,4` exact search is retained as predecessor evidence; the new all-`r` statement is a written algebraic argument, not a larger finite search. Q8 PR #1822 addresses a different two-role repeated central-commutator target.

## Reproduction

```sh
python3.12 scripts/research_package.py --package research/q8-central-minus-one-any-registers-seed0332f4
```

The registered replay checks 8-element Q8 multiplication, the augmentation quotient, all twelve exact four-call words at `r=3,4`, every relevant idempotent pair for rank-two coordinate projections, three negative controls, exact source pins, and four package tests under optimized Python. Expected verifier marker:

```text
PASS_Q8_CENTRAL_MINUS_ONE_ANY_R q8=8 dim_J_over_J2=2 idempotents=28,120 pair_checks=54 direct=24 controls=3 exact_min=4 no_new_kappa
```

The package is pinned to base `c676548106012571fefa1dce0ec16f1bcfe11dce` and selected-record SHA-256 `10b9e340fd8e354a37a0c4813c90e5de1dd42044b5f6aca4a3fc5a42b685fa32`. The selected supplier and frontier remain unchanged; this is not a physical supplier mapping or new `kappa` claim.

Prepared by Cinna Davis with substantial OpenAI Codex assistance. No independent human review or proof-assistant formalization is claimed. Apache-2.0.
