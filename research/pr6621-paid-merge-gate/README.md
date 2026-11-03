# PR #6621 paid-job merge gate

**Audit; no new κ.** The selected frontier stays 0.00310045.

## Scope and evidence

Original card: `supplier-boundary-audit`, refined to one latest candidate.
PR [#6621](https://github.com/CrocSwap/integer-mult-bounds/pull/6621) at
`e772ff8f300f4687bd8fa059f9e8f98719de121c` reports conditional κ = 0.00329700
by three edits of the PR #6529 native word, on the unchanged PR #6551 caller.
The published signed change per native call is

```text
paid    {1:-3, 3:-1, 4:+1, 5:-1, 6:+1}
targets {8:+1, 9:-1}
```

and the complete invoice is that delta times 18. This package checks that
claim against the published receipts and records one coverage gap. It does
not replay the native word or the rational moment engines.

### What the receipts establish

Against published PR [#6551](https://github.com/CrocSwap/integer-mult-bounds/pull/6551)
at `11ca568cd1a16776ade02b4df09ea04a784cc674`, the PR #6621 `complete_cost`
histograms differ by exactly `18` times the stated per-call delta. Productive
fields stay 13,756, paid calls fall 67,096 to 67,042, and the rank-mass
surplus stays 760. Both public ordinary-work bounds equal the closed form in
`pricing.py` at 611 caller events, namely 254,932,208. The `+68` native
program events therefore do not move that bound: the formula never reads the
native program length. The local route allowance rises by 1,000, which equals
`1000 * (-3 + 4)` when the per-call paid-job count falls by 3 and one owned
lifetime is added. That is an accounting identity of the published totals, not
a replay.

The multisets `{1,1,1,3,5,8}` and `{4,6,9}` both sum to 19, and the first is
strictly majorized by the second. For `H(r) = r^t` on `0 < t < 1`, strict
concavity gives

```text
3 H(1) + H(3) + H(5) + H(8) - H(4) - H(6) - H(9) > 0.
```

The same conclusion splits into the two brackets in PR #6621's PROOF.md.
Strict subadditivity of `r^t`, which follows from `s^t > s` for `s, t` in
`(0, 1)`, gives `3 H(1) + H(3) > H(6)` because `1+1+1+3 = 6`. The derivative
`t r^{t-1}` is strictly decreasing, so the unit interval `(4, 5)` contributes
more than `(8, 9)`. The verifier checks the integer comparisons. It does not
replace the concavity argument.

The native words agree with the event census in the README, independently of
the replay. `word-pr6529.json.gz` is the program inside PR #6551's
`native-source.tar` and is byte-identical to `BASEWORD.json.gz` inside PR
#6621's archive. The new program has length 18,561 rather than 18,493:
`ADD +69`, `MOVE -3`, `INIT +1`, `CLEAR +1`. The only `final` change is index
435, from frame 127 to frame 246.

### The gap

`invoice.compare` in the PR #6621 package demands that the candidate differ
from `research/gaussian-root-retirement/RESULT.json` inside its `source.tar`
by only the retirement change

```text
208*(H41 - H40 - H57 + H56).
```

That archived file still carries status
`PASS_GAUSSIAN_ROOT_RETIREMENT_KAPPA_00329394` and kappa `164697/50000000`.
Its paid and target histograms, local scalar allowance, and raw-root interval
are not the receipt archived by PR #6551. Relative to that unmodified receipt
(sha256 `13639e4770964ded237b79d72ad517448de269b34d724beaa70757dbe0be6fe2`),
the PR #6621 archive already contains the same native merge delta as the
public candidate. The compare gate therefore still sees only the retirement
delta. The rewritten raw-root lower endpoint
`164801644010225711532641/50000000000000000000000000`
lies strictly above the unmodified upper endpoint
`82348659273829759207423/25000000000000000000000000`
and strictly above the kappa string the file still prints,
`164697/50000000`.

PR #6551's own public histogram really does differ from its own archived
predecessor by the retirement delta. The same numerical gate on PR #6621 does
not additionally certify the merge. The merge is visible only by comparing
the public #6621 receipt with the public #6551 receipt, or with the
unmodified archived predecessor. Neither comparison is the check
`invoice.compare` performs.

PR [#6554](https://github.com/CrocSwap/integer-mult-bounds/pull/6554) audits
the #6551 retirement cut. It does not inspect this native merge or the
rewritten predecessor receipt.

## Reproduce

From the repository root, with Python 3.12:

```sh
python3 -B research/pr6621-paid-merge-gate/verify.py
python3 scripts/research_package.py --package research/pr6621-paid-merge-gate --check-only
python3.12 scripts/research_package.py --package research/pr6621-paid-merge-gate
```

The marker is `PASS_PR6621_MERGE_GATE_DOES_NOT_SEE_THE_MERGE`.

Vendored bytes, copied from the named commits and checked against the GitHub
blob ids of the two public `RESULT.json` files:

| File | sha256 | Git blob |
|---|---|---|
| `evidence/pr6551-result.json` | `90e096089e661a82f551feb022ff4fa49a5847b76abb5116c89cb7ed26c3d27f` | `38d840ae0f36b5a922fe288ca422f8d942d0008e` |
| `evidence/pr6621-result.json` | `878e15f5797219311175ae177fea8c4a10f4da5f4c463814721f5bd8b7d6dc27` | `0c31219eccb0d9f8e73b39da7819545795f7d964` |
| `evidence/archive6551-retirement-result.json` | `13639e4770964ded237b79d72ad517448de269b34d724beaa70757dbe0be6fe2` | extracted from PR #6551 `source.tar` |
| `evidence/archive6621-retirement-result.json` | `020728f015b8493b975a6c3d25115e00cef1c4bb62c062148f546723c509b75d` | extracted from PR #6621 `source.tar` |
| `evidence/word-pr6529.json.gz` | `15ca0c4ee15ad5a58dfc178d7b44d89ca202021c2907fbf9ef2ed50ba1ed8513` | `WORD.json.gz` in the #6551 native archive; also `BASEWORD.json.gz` in the #6621 native archive |
| `evidence/word-pr6621.json.gz` | `25b350a56ce11436fccf4c987da466cb002fa28dfc9b7e9d88e8b1b748b79df3` | `WORD.json.gz` in the #6621 native archive |

PR #6551 `source.tar` blob `025b8b9c6d9b21e31ad7499ebb04132abfa7e88c`. PR #6621
`source.tar` blob `0c254b78790851e78fc43b0f72b2d47e4723517b`.

## Open next questions

1. Replace the archived Gaussian-retirement `RESULT.json` with the unmodified
   PR #6551 copy and rerun the published verifier. The first assertion to
   inspect is `invoice.compare`. This matters because a green run of the
   shipped package does not show the merge. It is blocked here by the nested
   replay and moment engines, which this session did not execute.
2. Assign the Gaussian ranks of the two vendored words with an independent
   census. The opcode and `final[435]` facts above do not identify ranks
   1, 3, 4, 5, 6, 8 and 9. The rank map is the retained native replay.

## Credit

The construction, retirement identity and reported conditional kappa are
DreamingOfClouds' PR #6621, building on Ali Romman's PR #6551 and the retained
PR #6545 / PR #6529 lineage named there. PR #6554 by DLamdata is the open
audit of the retirement cut and is not reused as evidence for the merge.
Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
