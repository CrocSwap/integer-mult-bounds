# Merge paid jobs in the native word under the rebalanced retirement

The complete conditional bound is **κ = 0.00329700**. The increment over
[PR6551](https://github.com/CrocSwap/integer-mult-bounds/pull/6551),
κ = 0.00329492, is **0.00000208**, or **0.0631275%**. The exact raw crossings
are 0.0032970138574524603 here and 0.003294926110571363 in PR6551, a
difference of 0.0000020877468811 (0.0633625%). This comparison excludes all
inherited gains. The selected frontier is unchanged.

Keep the PR6551 caller: the PR6545 retirement identity and the child trees
`(7,2,5,4)`, unchanged. Keep the PR6529 native word except for three edits.
Each edit is a legal rewrite of the word with its own compensation. Together
they change the native paid and target profile, per native call, by

```text
paid    {1:-3, 3:-1, 4:+1, 5:-1, 6:+1}
targets {8:+1, 9:-1}
```

The complete signed invoice (targets minus paid jobs) improves by

```text
18 * (3 H1 + H3 + H5 + H8 - H4 - H6 - H9).
```

For `H_r = r^t`, with `0 < t < 1`, this is positive: see PROOF.md. The
construction and its complete invoice change; the old invoice is not priced
more finely. No optimum over all words or callers is claimed.

## The three edits to the PR6529 word

Event numbers use the 18,493-event PR6529 word; the new word has 18,561.

- **A. Merge three paid hops into one.** The single-use owned register 770
  is created at event 9191 and carried through frames 549, 553, 1047 and 593
  (events 9194, 9196 and 9200). Its value is added to rows 169, 206 and 471
  on the way (events 9195, 9198 and 10386). The new word moves it directly
  from frame 549 to frame 593. Six rows (119, 169, 191, 193, 204, 206) receive
  `r471 + r525/2 + 2 r704` as 18 ADDs in frame 3 at the start of the program,
  and rows 9 and 61 receive ADDs from registers 471, 333, 525, 173 and 704 in
  frame 127. The paid jobs of ranks 1, 1, 1 and 3 become one job of rank 6.
- **B. Re-base register 471's addition.** Register 471 now receives
  `+r174` and `-r257/2` in frame 3 (events 2557 and 5664), compensated in
  frame 676 by `-r174` and `-r265/2` on register 471 and `+2 r471` on
  register 265 (events 9677 to 9679). This replaces the addition
  `2 r770` to register 471 in frame 593 (event 10386).
- **C. Re-base the helper-435 input.** Helper 435 takes its input in frame
  246 instead of 127 (`final[435]` changes from 127 to 246). Its input rows
  are prepared in frame 3, compensated in frame 516 by registers 37, 110 and
  435, and a clean shadow register 783 is created and cleared in frame 127.
  One rank-9 helper target becomes rank 8, and one rank-5 paid job rank 4.

In the new word the first 18 events belong to A and the next 15, ending with
`ADD 435 434` in frame 3, to C. The word has 69 more ADDs than before, three
fewer MOVEs and one more INIT/CLEAR pair (register 783).

| Complete inventory | PR6551 | This package |
|---|---:|---:|
| Native calls / thin queries | 18 / 17 | 18 / 17 |
| Native program events | 18,493 | 18,561 |
| Owned lifetimes (peak) | 45 (13) | 46 (13) |
| Local scalar allowance | 137,218 | 137,866 |
| Independent caller fields per port | 35 | 35 |
| Productive fields, including native helpers | 13,756 | 13,756 |
| Paid Gaussian jobs | 67,096 | 67,042 |
| Caller events | 611 | 611 |
| Rank-mass surplus | 760 | 760 |

Read [PROOF.md](PROOF.md) for the exact delta. [ROOT.json](ROOT.json) gives
the unchanged trees. [CONTROLLER.json](CONTROLLER.json) contains every caller
event. [WITNESS.json](WITNESS.json) contains the unchanged retirement bases
and cut. [RESULT.json](RESULT.json) records both rational price engines, the
compiler, the physical maps and all outer inequalities.

## Verification

Use CPython 3.12 with its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/p104-paid-job-merges-on-retirement-tree
```

The registered hook runs normal and optimized checks. A direct run is
`python3.12 -I -B research/p104-paid-job-merges-on-retirement-tree/verify.py`.
The result marker is `PASS_PAID_JOB_MERGES_KAPPA_00329700`.
See [VALIDATION.md](VALIDATION.md) for checks that have run and their limits.

The two rational engines enclose the raw crossing in
`(0.00329701385745246023380113, 0.00329701385745246023380114)`. The tested saving is 0.003297005. As in PR6551,
the old completion decay does not suffice; the check uses decay 97/100 and
reserve 10^(-27) with power 1920 and the full tail and compiler tests.

The verifier first regenerates the PR6529 word from its retained
construction and compares it with the base word. It then substitutes the
edited word and checks its 799 columns, owned lifetimes, helper maps,
absolute phases and all 7,488 caller contacts, with the base-word local
profile replaced by the new one above. The correction-drop controls run on
the edited word and must be rejected. It then replays the PR6551 caller: full
forward and reverse polynomial checks, the same two dual pairs, physical
target checks and a separate invoice count. Both rational engines reject
PR6551 at the new claim. Deletion, sign, target and unpaid-job controls must
fail.

[source.tar](source.tar) retains the PR6545 package with its nested PR6529
and PR6524 source archives. The PR6529 layer has the edited verifier, the
edited word `WORD.json.gz`, the base word `BASEWORD.json.gz` and the edited
pricing. [RETAINED.json](RETAINED.json) binds all outer source files by path,
Git blob and SHA256, and each nested manifest is regenerated for the edited
files. Replay needs neither network access nor side branch Git objects.

[ADAPTERS.json](ADAPTERS.json) declares each driver, constructor and price
edit inherited from PR6551, with the new claim constants.

## Scope and coordination

This contribution is a further κ improvement on the PR6551 construction.
The task and changed premise are in [TASK.json](TASK.json). The caller, the
trees, the retirement identity and the root are PR6551's and are not claimed
here. Only the native word and its price change.

The five inherited assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. The shadow register 783
is erased in frame 127 while nonzero, as register 781 already is, so the
`owned_erasure` assumption now covers one more erasure. This is an
author-checked conditional construction. It is not independent scientific
acceptance, a materialized uniform word or a complete rounded integer
multiplier. No PR merge, closure or selected-result change is included.

## Open next questions

- Can an independent reviewer confirm the three native edits and the
  complete invoice delta? Start with the delta in PROOF.md, then compare
  `BASEWORD.json.gz` with `WORD.json.gz` in the PR6529 layer.
- Can the remaining rank-6 and rank-9 paid and target jobs be merged
  further, or the native word be rebuilt for the new profile? A candidate
  must supply its full arbitrary-input endpoint and every paid job.

The structured questions are in [TASK.json](TASK.json).

## Credit

Native-word edits, price and integration: DreamingOfClouds with Claude Opus
5.5 (Anthropic), via Claude Code. Apache-2.0.

The caller, trees and package this extends are PR6551 (Ali Romman). Credit
PR6545 for independent Gaussian retirement, PR6529 for the native word and
its scaled transport fusions, PR6453 (Erwan L.) for the underlying
compensated native word, PR6398 and PR6399 for the binary suppliers and mixed
root, and PR6524 for explicit replay services. PR5599/5602/5611/5615,
PR6348, Rohan Arun's PR6417, DreamingOfClouds' PR6375 and all retained
predecessors keep their credit. See [NOTICE](NOTICE) and the original
archived notices for the native, interval, compiler and analytic
contributors.
