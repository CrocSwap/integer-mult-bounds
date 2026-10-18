# Independent owner-map audit of the open T16 claims on the seven-slot k8 word

**Status: research audit / independent verification. No new κ.** The selected
result is unchanged. No counterexample was found.

Track 60–74 (adversarial audit), OS-random seed 67. Base `abdc6a70`. PR heads
are pinned in [SOURCES.json](SOURCES.json) (snapshot 2026-10-13 18:40 UTC).

## What this covers

Fifteen open PRs claim κ ≈ 0.001672 by putting a new sixteen-replica owner map
on the same local word (#1018's seven-slot k8 word `c2b29430…`). Earlier audits
covered other parts of these claims:

- #1049 checked the local word.
- #1069 and #1051 checked the arithmetic from the committed profile to κ.

Nobody had independently checked the step in between: whether each frozen
`OWNERS.json.gz` is a legal whole-helper hosting that yields the claimed idle
profile. The packages check this only with `lift16.py` and `indep16.py`. Both
are #858's code with generic-R edits, and they ship inside the audited packages.

`verify.py` re-implements the hosting rules of
[research/complex-double-replica-owners/PROOF.md](../complex-double-replica-owners/PROOF.md)
from that text. It uses only the standard library and does not import or run
any file from the audited packages. It reads their owner maps, plans and specs
as git blobs at pinned ids. Its other three inputs are pinned as follows:

| Input | Source | Used for |
|---|---|---|
| ROUND20 parent template | main, vendored under `research/complex-k492-owner-repair/` | 30 source events per replica, stage→pair |
| PR558 `DATA-PHASES.json` | main, `research/community-k492-audit/pr622/replay/baseline558/` | pending axes of each idle child |
| seven-slot word | copied from #1049 (`inputs/`), content `c2b29430…` | helper widths, span(final) − span(start) |

For each claim, every role is checked against these rules:

- **R1:** there are 144 complete invocations in the two-group interleave, and every replica sees its 30 source events in order.
- **R2:** each invocation hosts helpers 0..479 exactly once, each at the width derived from the word.
- **R3:** the physical family is `owner·896 + (2·pair+side)·112 + port`. It lies in the live data namespace and is not the caller's active pair.
- **R4:** each family hosts at most one helper per invocation.
- **R5:** the invocation lies strictly inside the owner's actual window. The window runs from the last touch of the pair (local sweep or either end of a bridge) to that child's idle sweep. It is rebuilt from the event stream, not read from PLAN.
- **R6:** slices stay within the child's rank, do not overlap within a bin, and fill an occupied prefix.
- **R7:** the idle remainders are recounted. The full profile is 144 × the word's local profile plus those remainders. It must equal SPEC, PLAN and RESULT, with deficit 5120 and the halving guard.

Two checks go beyond what the audited checkers do:

- **X1:** the windows rebuilt from events must equal the committed `PLAN.json` windows, for all 288 windows and their time lists. The same builder must also reproduce the shared T8 PLAN.
- **X2:** distinct idle children of one physical family have disjoint pending axes at every port, giving 2,016 (family class, port) checks. R6's per-child bins rely on this. The check is load-bearing here: in each map, about 8,400 of the roughly 11,800 host families hold slices of two or more children.

## Result

All 15 owner maps pass, and so does the shared T8 map of #1018 (34,560 roles).
In total, 1,036,800 T16 roles are checked. Every recount matches the claim.

| PR | head | author | κ (claimed) | recounted idle remainders | cross-replica roles |
|---|---|---|---|---|---:|
| #1022 | `58618bcb` | jeremykothe2 | 0.001672081255752945 | {1:2241, 2:16, 3:344, 7:33, 16:58, 48:4845} | 56,087 |
| #1028 | `be4bd89c` | jeremykothe2 | 0.001672166670891177 | {1:2251, 3:389, 7:10, 16:49, 48:4849} | 56,410 |
| #1031 | `e900534f` | jeremykothe2 | 0.001672167430672016 | {1:2249, 2:1, 3:389, 7:10, 16:49, 48:4849} | 56,536 |
| #1042 | `7e8ef087` | jeremykothe2 | 0.001672188119205421 | {1:2249, 2:1, 3:400, 7:3, 16:47, 48:4850} | 56,764 |
| #1050 | `c87242f8` | jeremykothe2 | 0.001672241870811633 | {1:2249, 2:1, 3:413, 7:2, 16:36, 48:4853} | 56,609 |
| #1053 | `6f92ce88` | jeremykothe2 | 0.001672245809535804 | {1:2256, 2:1, 3:410, 16:37, 48:4853} | 56,725 |
| #1055 | `a8ea3089` | jeremykothe2 | 0.001672251604432734 | {1:2249, 2:1, 3:406, 7:5, 16:36, 48:4853} | 57,220 |
| #1056 | `d0201efb` | rohanarun | 0.001672267698427438 | {1:2255, 3:398, 7:2, 8:3, 16:36, 17:1, 48:4853} | 56,611 |
| #1061 | `223f581a` | jeremykothe2 | 0.00167259071506618 | {1:2268, 3:402, 7:2, 16:1, 48:4865} | 56,821 |
| #1063 | `d9377d32` | rohanarun | 0.001672285678298543 | {1:2255, 3:400, 7:2, 16:36, 35:1, 48:4853} | 56,664 |
| #1065 | `387d935e` | jeremykothe2 | 0.001672644568760139 | {1:2275, 3:389, 7:2, 48:4866} | 57,780 |
| #1068 | `cc71375e` | jeremykothe2 | 0.001672650458698046 | {1:2276, 3:384, 7:4, 48:4866} | 57,488 |
| #1074 | `052afc12` | jeremykothe2 | 0.001672651218919025 | {1:2274, 2:1, 3:384, 7:4, 48:4866} | 58,061 |
| #1082 | `0c2e294e` | rohanarun | 0.001672653061493085 | {1:2274, 3:383, 5:1, 7:4, 48:4866} | 58,064 |
| #1087 | `589d1ced` | jeremykothe2 | 0.001672654541898561 | {1:2280, 3:378, 7:6, 48:4866} | 57,468 |

#1082 ships no `RESULT.json`, so its κ and profile are read from its
`CANDIDATE.json` and `PROFILE.json`. Every claim has rank mass 1,041,408 = 73·14,336 − 5,120. Together with #1069's
pricing of the same committed profiles, the chain from frozen owner data to the
claimed κ is now checked by code written independently of the authors' code.
The local word itself has #1049's audit. Its inherited interfaces have no
audit (see Scope).

### Negative controls

The controls are run on #1074. Each mutant must be rejected by the rule it
targets, not just rejected somewhere:

| Control | Rejected by |
|---|---|
| dropped role | R1 |
| narrowed width | R2 |
| duplicated helper index | R2 |
| family in the private namespace | R3 |
| consistent role placed on the caller's active pair | R3 |
| two helpers on one family in one invocation | R4 |
| role moved past its owner's idle sweep, swapped so R2 still holds | R5 |
| overlapping slices in one bin | R6 |
| last slice of a bin shifted up by one, leaving a gap | R6 |
| claimed idle profile tampered | R7 |
| committed PLAN window time list truncated | X1 |

## Reproduce

```sh
python3 -I -B research/t16-owner-audit-seed67/verify.py --fetch
```

`--fetch` downloads `refs/pull/N/head` for the 15 PRs. Leave it out once the
blobs are present. The run takes about 4 s. Expected last line:

```text
PASS_INDEPENDENT_T16_OWNER_AUDIT claims=15 roles=1036800 t8_roles=34560 controls=11
```

The full receipt is compared byte for byte with [RESULT.json](RESULT.json).
`--only N` audits one claim and skips that comparison.

## Observations for reviewers (not defects)

- **`evidence/` is not T16 evidence.** The `evidence/local`, `evidence/global`
  and `evidence/audit` files in the eleven jeremykothe2 `gauge44-slots-t16`
  packages checked (#1022–#1074) are byte-identical to #645's R = 492 files, also under
  `research/gauge44-barch-t16/evidence/`. For example, `OWNERS-AND-PROFILE.json`
  there reports 35,424 roles and deficit 2,560. The inherited #1005 README text
  says so (line 116, "Historical #645 files"). However, its later "Proof and
  evidence" list still describes `evidence/audit/` as the actual controller and
  invoice. The only committed T16-specific receipt is `RESULT.json`, with
  stage-log hashes. The T16 independent-checker, assembly and invoice outputs
  are produced only by running `verify_t16.py`.
- **The rules give a temporary borrow a permanent price.** A cell of a pending
  axis can absorb at most one helper over its whole window (R6), even though
  each helper is restored at the end of its invocation. This is the accounting
  the proof uses: the idle child charges only the unoccupied suffix. The audit
  checks that accounting and does not question it.

## Scope

This audit covers whole-helper owner admission and the idle-remainder recount
for the listed frozen data. It does **not** cover:

- the 73-axis chart and route construction (indep16's chart step);
- the emitted controller;
- invoices and prefix/row reserves;
- moments and the outer assembly;
- the local word's admission;
- the inherited all-size/compiler, common-label/mutable-source realization,
  whole-invocation hosting, precision/tape, analytic and PR589 bit-interface
  assumptions.

The window semantics are taken from #858's PROOF.md, which this audit does not
re-prove. A pass here is a finite check of these rules on these files. It is not
a proof that the claims are sound.

## Credit and disclosure

The owner maps are by Jeremy Kothe (#1022–#1074, #1087) and Rohan Arun (#1056, #1063, #1082).
The T16 controller, actual-window semantics and the rules checked here are Hao
Yan's #858, with #870's adaptation. The word is #1018's, built on rohanarun's
#987 slots, #1005, NewBArch's #869 and the #645/#685/#741 lineage. The pinned
word file is copied unchanged from Sagar Thakrar's #1049 under Apache-2.0.
#1069 (pricing) and #1049 (local word) are the companion audits this one
completes.

Prepared by Josie Elliston with substantial assistance from Anthropic Claude
(Claude Code). New material is Apache-2.0.
