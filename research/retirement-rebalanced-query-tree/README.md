# Rebalance the binary trees after Gaussian retirement

The complete conditional bound is **κ = 0.00329492**. The increment over
[PR6545](https://github.com/CrocSwap/integer-mult-bounds/pull/6545),
κ = 0.00329394, is **0.00000098**, or **0.0297516%**. This comparison excludes
all inherited gains. The selected frontier is unchanged.

Keep the PR6545 retirement identity and the exact PR6529 native word. Change
the four binary child sizes from `(7,2,2,7)` to `(7,2,5,4)`. The complete
signed invoice improves by

```text
208 * (H41 - H40 - H57 + H56).
```

For `H_r = r^t`, with `0 < t < 1`, the derivative decreases strictly with r.
Thus this expression is positive. This is a change to the construction and
its complete invoice. It is not a finer decimal claim for the old invoice.
No optimum over all trees or callers is claimed.

| Complete inventory | PR6545 | This package |
|---|---:|---:|
| Native calls / thin queries | 18 / 17 | 18 / 17 |
| Independent caller fields per port | 35 | 35 |
| Productive fields, including native helpers | 13,756 | 13,756 |
| Paid Gaussian jobs | 67,096 | 67,096 |
| Caller events | 609 | 611 |
| Rank-mass surplus | 760 | 760 |

Read [PROOF.md](PROOF.md) for the exact delta and the input-independence
argument. [ROOT.json](ROOT.json) gives the changed trees.
[CONTROLLER.json](CONTROLLER.json) contains every caller event.
[WITNESS.json](WITNESS.json) contains the unchanged retirement bases and cut.
[RESULT.json](RESULT.json) records both rational price engines, the compiler,
the physical maps and all outer inequalities.

## Verification

Use CPython 3.12 with its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/retirement-rebalanced-query-tree
```

The registered hook runs normal and optimized checks. A direct run is
`python3.12 -I -B research/retirement-rebalanced-query-tree/verify.py`.
The result marker is `PASS_REBALANCED_RETIREMENT_KAPPA_00329492`.
See [VALIDATION.md](VALIDATION.md) for checks that have run and their limits.

The two rational engines enclose the raw crossing in
`(0.00329492611057136286764342, 0.00329492611057136286764343)`.
The tested saving is 0.003294925. The old completion decay does not suffice
for this tree. The new check uses decay 97/100 and reserve 10^(-27), with
the same power 1920 and the full tail and compiler tests.

The verifier first rebuilds the complete retained native source and checks
its 799 columns, owned lifetimes, helper maps, absolute phases and all 7,488
caller contacts. It then checks the full PR6545 caller and requires every
source result to match its frozen receipt. The new caller passes full
forward and reverse polynomial checks, the same two dual pairs, physical
target checks and a separate invoice count. Both rational engines reject
PR6545 at the new claim. Deletion, sign, target and unpaid-job controls must
fail.

[source.tar](source.tar) retains the exact executable PR6545 package at
`775722aa94a5e85b05d1d704d7dca10cbf016f0c`, including its nested PR6529 and
PR6524 source archives. [RETAINED.json](RETAINED.json) binds all 23 outer
source files by original path, commit, Git blob and SHA256. The nested
manifests remain unchanged. Replay needs neither network access nor side
branch Git objects.

[ADAPTERS.json](ADAPTERS.json) declares each source edit. Two driver edits add
an explicit extension hook. Two constructor edits accept the tree data as an
argument. The price edits select the new invoice and rational parameters.
No source check is removed. Temporary adapted modules are separate from the
frozen source files.

## Scope and coordination

This contribution answers the explicit request for another κ improvement.
The task and changed premise are in [TASK.json](TASK.json). Canonical main is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8.

The [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5645#discussioncomment-19205459)
records the move from bounded native-transport searches to this fixed
retirement and tree allocation. The public PR6545 continuation had released
its scope, including its retirement-aware price screens. The present result
uses its published identity and gives the complete changed caller. It does
not claim a new retirement mechanism. Current caller claims and recent PRs
were checked. Unpublished work, arbitrary historical diffs and omitted
sparse-checkout notes remain outside overlap coverage.

The five inherited assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. This is an author-checked
conditional construction. It is not independent scientific acceptance, a
materialized uniform word or a complete rounded integer multiplier. No PR
merge, closure or selected-result change is included.

## Open next questions

- Can an independent reviewer confirm the tree substitution and the complete
  invoice delta? Start with the unchanged prefix through event 328, then the
  four histogram differences in PROOF.md. Independent review remains open.
- Can a different exact retirement or caller give a larger gain? A candidate
  must supply its full arbitrary-input endpoint and every paid job. This
  package supplies one allocation and no general optimality theorem.

The structured questions are in [TASK.json](TASK.json).

## Credit

New tree allocation, proof, integration and checks: Ali Romman with
substantial OpenAI Codex assistance; no subagents. Apache-2.0.

Credit PR6545 for independent Gaussian retirement, PR5599/5602/5611/5615 for
the causal handoff and basis methods, PR6348/6398 for the binary suppliers
and mixed root, PR6529 for the native word, and PR6524 for explicit replay
services. Rohan Arun's PR6399/6417, Erwan L.'s PR6453, DreamingOfClouds'
PR6375 and all retained predecessors keep their credit. See [NOTICE](NOTICE)
and the original archived notices for the native, interval, compiler and
analytic contributors.
