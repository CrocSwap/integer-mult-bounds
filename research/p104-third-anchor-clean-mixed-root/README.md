# Conditional kappa 0.003287014: PR6417's clean mixed-root composition with a third group-1091 anchor

Conditional claim: **kappa 0.003287014** (tested 0.003287019), against PR6417's 0.003286849, that is **+1.65e-7**
(+0.00502 percent). The exact raw crossing of this stacked word under the unchanged PR6398 caller is
(0.00328701955375063425072028, 0.00328701955375063425072029), printed by the full run in `RESULT.json`
(`complete_cost.raw_root_interval`); the raw crossing gain over PR6417's crossing is +1.627e-7. The compiler grid
is PR6417's (gap 1/1.4e9, H 138,100,200,000,000, test exponent 98,643).
All checks are author checks and the five inherited framework assumptions remain.

## What changes against PR6417

Only the native word changes: PR6417's word is PR6399's clean merge of the PR6375 word. Ours is
(PR6353 word) -> three-anchor contraction (`construct3.py`, `SPEC.json`) -> the PR6375 lift rounds ->
the PR6399 merge, rebuilt with the cache label **782** (`merge_construct.py`, a parametrized copy of the PR6399
constructor; PR6399 uses 781, which is one of the new shadow rows' labels and trips its "no CLEAR of the cache at
frame 127" assertion). With cache 781 it reproduces the published PR6399 word exactly (checked in `verify.py`).

- `final[234]` goes from 127 to 246: helper 234 is the third anchor of group 1091 (224 and 227 at frame 245).
- Against the PR6399 word: paid +1 at rank 4, -1 at rank 5; productive +1 at rank 8, -1 at rank 9 per call.
- Local inventory (770, 29, 45, 13, 131560, 5925): one more owned lifetime than PR6399 (44) and 1,382 more scalar
  allowance (130,178), both charged by the unchanged checkers. The caller, root, compiler, outer ledger and
  price adapter (apart from the claim constants) are PR6417's.

## Construction and capacity

On the transposed PR6353 word group 1091 has response-free directions U_245 and U_246 of dimension 2 each,
7 helper-only departure functionals, and pairing rank exactly 3, so three anchors fit: PR6372 used two. The dyadic
solution in `SPEC.json` places 224, 227 at frame 245 and 234 at frame 246. `construct3.py` reproduces the PR6372
word exactly without a spec. The capacity computation is exploratory; acceptance rests on the exact replay.

## Reproduce

Python 3.12, standard library only:

```sh
python3.12 -I -B research/p104-third-anchor-clean-mixed-root/verify.py --build-only   # cheap: rebuild, deltas, controls
python3.12 -I -B research/p104-third-anchor-clean-mixed-root/verify.py --write-result # author run, writes RESULT.json
python3.12 -I -B research/p104-third-anchor-clean-mixed-root/verify.py
python3.12 -I -O -B research/p104-third-anchor-clean-mixed-root/verify.py
```

The same third anchor was also published on the PR6398 root alone as PR6436 (kappa 0.00328637739144124222748802);
this package stacks it on PR6417 (PR6399 merge plus the PR6398 root). `verify.py` marks every change from PR6417's verifier with `# CANDIDATE CHANGE`. Replaced checks: the native word
and local/native receipts describe the PR6399 word, so they are checked against that word (published word and local
receipt exactly) and the stacked word is checked differentially (exact deltas, exact inventory, native receipt equal
except the new chart, helper histogram and payload hash). The PR6399 `owned_zero.py` and `construct.py` are not
executed: `zero_scratch.py` is an independent exact re-implementation and `merge_construct.py` is regression-checked.
Added controls: seven third-anchor controls (wrong entrance 245, entrance reverted, MOVE, response, input
correction and dyadic restore dropped, response doubled), the merge label collision, a dropped merge cleanup event and
a corrupted spec.

## Assumptions and limits

The shadow rows of the contraction are not exactly zero at their forward CLEAR; that is the inherited
`owned_erasure` assumption (the same as PR6372's). The claim constants satisfy the repository's strict grid and crossing checks in the full verifier.
Pins `head:a928a7aa...` (PR6399), `head:dee2663...` (PR6398), `head:b556600f...` (PR6372) and `head:247b5c3...`
(PR6375) need those commits reachable in a real submission. No independent review is included.

## Open next questions

Independent review of the capacity argument, the 782 relabelling and the new constants; exact joint capacity of
all output-side classes with the published anchors as free variables (a randomized mod-p search found no better
joint set, but it is not exact). Structured questions are in [TASK.json](TASK.json).

## Credit

New third-anchor construction, stacking, adapted verifier and documentation: Claude Sonnet 5.5 via Claude Code,
orchestrating subagents, for Erwan L. (substantial AI assistance), Apache-2.0.

This package builds directly on **Rohan Arun** (PR6399 clean donor-transport merge and PR6417 composition),
**Ali Romman (aliromman)** (PR6398 mixed root, PR6353, PR6372, PR6348, PR6349), **DreamingOfClouds** (PR6375 lifts,
PR6314) and, through their notices retained byte for byte in the source archives, Cinna Davis, Mason Hale,
Pierre-Loic Doulcet, Chris R / Clear1nsight, Jacob Alan Sussman, zxv, Cao Yifan and the other contributors named
there. The new code is not authored by any predecessor; they are credited as sources and lineage in [NOTICE](NOTICE).
