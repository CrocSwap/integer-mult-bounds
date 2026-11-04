# Split a public helper register of the native word under the rebalanced retirement

The complete conditional bound is **κ = 0.00329760**. The increment over
[PR6621](https://github.com/CrocSwap/integer-mult-bounds/pull/6621),
κ = 0.00329700, is **0.00000060**. The exact raw crossings are
0.0032976213479979 here and 0.0032970138574525 in PR6621, a difference of
6.075e-7 (0.01843%). This comparison excludes all inherited gains. The
selected frontier is unchanged.

Keep the PR6621 package: the PR6551 caller with the PR6545 retirement
identity and the child trees `(7,2,5,4)`, and the PR6621 native word. The
caller, trees and root are unchanged. Only the native word changes, by one
exact rewrite. Public helper register 607 is cut at frame 115. Its tail, the
part of its life from frame 115 to frame 127, moves to a new public register
770. Three compensating ADDs at the start of the program and three at the end
keep the arbitrary-input identity. One long helper thus becomes two shorter
ones. Per native call the paid and target profile changes by

```text
paid    {2:+1, 4:+1, 6:-1}
targets {4:+1, 5:+1, 9:-1}
```

The complete signed invoice (targets minus paid jobs) improves by

```text
18 * (H5 + H6 - H2 - H9).
```

For `H_r = r^t`, with `0 < t < 1`, this is positive by concavity: see
PROOF.md. The construction and its complete invoice change; the old invoice
is not priced more finely. No optimum over all words or callers is claimed.

## The edit to the PR6621 word

- **Cut.** Register 607 keeps its life through frame 115 (`final[607]` changes
  from 127 to 115). A new public register 770 starts at frame 115 and ends at
  frame 127 (`initial[770] = 115`, `final[770] = 127`). The owned registers,
  numbered from 770, shift up by one. The tail additions of frames 115 to 127 go to
  register 770 instead of 607.
- **Start.** Three ADDs in frame 3, at the start of the program, add
  `-r607/2`, `-r607` and `r607/4` to registers 173, 611 and 704.
- **End.** Three ADDs in frame 127, at the end of the program, add `r770/2`,
  `r770` and `-r770/4` to the same registers. With the start ADDs they
  compensate the cut; the verifier replays the edited word against all 800
  independent columns.
- **Frame 115.** An owned scratch register (795) is created and cleared in
  frame 115, and the existing move of register 3 into register 611 follows
  the cut.

The new word has 18,577 events (PR6621: 18,561), one more public register
and one more owned lifetime. The erasure obligation list is unchanged: it
holds the one shadow register of PR6621, renumbered by the shift.

### Declared package-local bounds

The new public register and the longer owned peak need two inventory
literals to move. These are verifier literals inherited from earlier
packages. They are not part of SPEC. The verifier changes each by an exact,
counted text replacement in the unpacked retained source, in two places (the
local replay and the forward replay):

| Literal | Before | After |
|---|---|---|
| public registers, `767 <= public <= 770` | 770 | 771 |
| owned peak, `0 < peak <= 13` | 13 | 14 |

The tail decay of the outer completion test also changes, from 97/100 to
33/34. The new delta ratio is above 97/100, so the old value no longer
suffices. The check keeps all charged ratios strict: the upper bound of delta
is 0.970283, below 33/34 = 0.970588; its lower bound still exceeds 31/32;
and `(33/34)^128 < 1/16`. See PROOF.md section 5.

| Complete inventory | PR6621 | This package |
|---|---:|---:|
| Native calls / thin queries | 18 / 17 | 18 / 17 |
| Native program events | 18,561 | 18,577 |
| Public registers | 770 | 771 |
| Owned lifetimes (peak) | 46 (13) | 47 (14) |
| Local scalar allowance | 137,866 | 137,990 |
| Native columns | 799 | 800 |
| Independent caller fields per port | 35 | 35 |
| Productive fields, including native helpers | 13,756 | 13,774 |
| Paid Gaussian jobs | 67,042 | 67,060 |
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
python3.12 -B scripts/research_package.py --package research/p104-helper-split-on-retirement-tree
```

The registered hook runs normal and optimized checks. A direct run is
`python3.12 -I -B research/p104-helper-split-on-retirement-tree/verify.py`.
The result marker is `PASS_HELPER_SPLIT_KAPPA_00329760`.
See [VALIDATION.md](VALIDATION.md) for checks that have run and their limits.

The two rational engines enclose the raw crossing in
`(0.00329762134799792561521137, 0.00329762134799792561521138)`. The claimed
saving is 0.00329760 and the tested saving 0.003297605, both below the raw
crossing. As in PR6551 and PR6621, the old completion decay does not
suffice; the check uses decay 33/34 and reserve 10^(-27) with power 1920 and
the full tail and compiler tests.

The verifier first regenerates the PR6529 word from its retained
construction and compares it with the base word. It then substitutes the
edited word and checks the declared public boundaries, its 800 columns, owned
lifetimes, helper maps, absolute phases and all 7,488 caller contacts, with
the base-word local profile replaced by the new one. The correction-drop
controls run on the edited word and must be rejected. It then replays the
PR6551 caller: full forward and reverse polynomial checks, the same two dual
pairs, physical target checks and a separate invoice count. Both rational
engines reject PR6621's claim at the new claim. Deletion, sign, target and
unpaid-job controls must fail.

[source.tar](source.tar) retains the PR6545 package with its nested PR6529
and PR6524 source archives. The PR6529 layer has the edited verifier, the
edited word `WORD.json.gz`, the base word `BASEWORD.json.gz` and the edited
pricing. The word retained here is the complete edited word, which contains
the PR6621 rewrites and this cut. [RETAINED.json](RETAINED.json) binds all
outer source files by path, Git blob and SHA256, and each nested manifest is
regenerated for the edited files. Replay needs neither network access nor
side branch Git objects.

[ADAPTERS.json](ADAPTERS.json) declares each driver, constructor and price
edit inherited from PR6621, with the new claim constants and tail decay.

## Scope and coordination

This contribution is a further κ improvement on the PR6621 construction.
The task and changed premise are in [TASK.json](TASK.json). The caller, the
trees, the retirement identity and the root are PR6551's and are not claimed
here. Only the native word and its price change.

The five inherited assumptions remain: `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape` and `analytic_recovery`. This is an
author-checked conditional construction. It is not independent scientific
acceptance, a materialized uniform word or a complete rounded integer
multiplier. No PR merge, closure or selected-result change is included.

## Open next questions

- Can an independent reviewer confirm the cut, its six compensating ADDs, the
  two declared package-local bounds and the complete invoice delta? Start
  with the delta in PROOF.md, then compare `BASEWORD.json.gz` with
  `WORD.json.gz` in the PR6529 layer.
- Can other long public helpers be cut in the same way, or the native word be
  rebuilt for the new profile? An edited word must supply its full
  arbitrary-input endpoint and every paid job.

The structured questions are in [TASK.json](TASK.json).

## Credit

Prepared by DreamingOfClouds with Claude Opus 5.5 (Anthropic), via Claude
Code. Apache-2.0.

The base is PR6621 (DreamingOfClouds), which merged paid jobs in the native
word under PR6551. Its lineage is credited as PR6621 credits it: the caller,
trees and package it extends are PR6551 (Ali Romman). Credit PR6545 for
independent Gaussian retirement, PR6529 for the native word and its scaled
transport fusions, PR6453 (Erwan L.) for the underlying compensated native
word, PR6398 and PR6399 for the binary suppliers and mixed root, and PR6524
for explicit replay services. PR5599/5602/5611/5615, PR6348, Rohan Arun's
PR6417, DreamingOfClouds' PR6375 and all retained predecessors keep their
credit. See [NOTICE](NOTICE) and the original archived notices for the
native, interval, compiler and analytic contributors.
