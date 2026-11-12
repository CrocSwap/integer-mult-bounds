# Bound shared stage-9 Walsh basis assignments

**Outcome** — Scoped exclusion. The complete bound is unchanged.

Sharing the retained stage-9 Walsh basis across Type B caller contacts cannot reduce the paid moment. With clock 2866 forced to Walsh, the exact optimistic upper is minus one rank-eight charge per port, below −63.232 raw across all eight ports at the incumbent. Without that force, the same flow certificates give an exact gross upper of zero across every fixed-basis assignment in scope. The all-original assignment attains zero. The proof grants diagonal updates, routing, setup, extra storage, precision and tape free.

The independent role-time graph and collapsed contact graph agree on the 16 eligible even idle calls, forced cut value 17, two charged transitions around clock 2866 and unforced flow and cut value 16. The unforced conclusion uses the same optimum after removing one forcing path. [Proof](PROOF.md), [verification](VERIFICATION.md)

## Replay

From a clean checkout on a POSIX host, use CPython 3.12 with assertions and its standard library.

```sh
python3.12 -I -B research/p104-type-b-shared-walsh-stage9-bound/replay.py
```

The replay authenticates each bundled input by relative path. It reproduces both forced cut certificates and both unforced flow checks, compares the results and rejects a changed caller and a damaged flow. It uses no external checkout or network. The expected final line is `PASS_P104_TYPE_B_SHARED_WALSH_STAGE9_BOUND`.

## Open next questions

- Can an existing paid boundary provide the same Walsh basis without a new rank-eight conversion? Name one exact boundary, prove arbitrary-input basis and ownership compatibility and price the whole compatible interval with every remaining conversion charged.
- Can a different converter or basis give a positive fully charged change? Pin its literal action, calculate its rank and full transition price, then reprice the entire feasible contact set before building an instance. Changed native J9 action and altered odd-idle providers also require separate tests.

## Predecessors

- Clear1nsight’s exact #7334 head `aaeec8c0acf01e99a5f331ef363a698d9c084ace` supplies the independently reproduced comparator, κ = 0.00364665195644, and its complete stock. [Comparator PR](https://github.com/CrocSwap/integer-mult-bounds/pull/7334)
- Rohan Arun’s exact #7113 head `07a76c5e2738882c0cb322278e56f6cae3c9885d` supplies the signed caller, stage axes and physical Gaussian gate. [Signed caller PR](https://github.com/CrocSwap/integer-mult-bounds/pull/7113)
- Exact #7411 head `c44a551b92786725cc2b805d6cf3b2547e66d711` supplies the single-clock case and same-rank conversion tariff. The retained Walsh–C lowering follows the #7000 complete-root application. [Single-clock PR](https://github.com/CrocSwap/integer-mult-bounds/pull/7411), [#7000 proof review](https://github.com/CrocSwap/integer-mult-bounds/blob/e54523517d0f03e58352e647c403a5af3e525a57/docs/research/pr-intake-evidence/pr7000-application/PROOF-REVIEW.md)
- #7362 supplies the directed-price predecessor receipt and #7298 supplies the rational tariff implementation lineage, pinned in `PROVENANCE.json`. [Price receipt](https://github.com/CrocSwap/integer-mult-bounds/pull/7362), [tariff precedent](https://github.com/CrocSwap/integer-mult-bounds/pull/7298)

This contribution bounds basis sharing over the complete fixed Type B contact set. OpenAI Codex and subagents materially assisted the proof, implementation and independent replay.
