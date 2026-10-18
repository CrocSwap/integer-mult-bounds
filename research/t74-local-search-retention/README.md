# T74 local-search retention and sentinel-cost scope

This receipt connects three related public artifacts to the review retained on
main. It resolves a narrow navigation gap: a reader of the PR1957 review can now
find the unchanged toolkit in PR2142 and the later correction to four
oracle-sentinel cases, without mistaking any of them for an integrated or
independently replayed general lower bound.

**Audit base:** `b4560d9e7216f72b73c5aa940ac099c05e33ccf9` (priority revision 5).
**Result type:** source/retention audit, not a new search or mathematical theorem.
The selected result and every frozen predecessor remain unchanged.

A final refresh reached main `1884c509efc004524786e9b7cfcc4aca572316d5`.
The receipt rechecks all 315 files there: original paths and exact-mode/blob
matches remain absent, and PR1957's disposition file is unchanged. The new
efficient1100 review still leaves PR1186's mechanism/proof review pending.
Priority revision 5 and this audit's conclusions remain compatible.

## Exact sources and retained content

| Artifact and credit | Pinned commit | Named source subtree | Files at original paths on audit base |
| --- | --- | --- | --- |
| [PR1957](https://github.com/CrocSwap/integer-mult-bounds/pull/1957), Rohan Arun | `e6a4d34874bb1aeba192c62629ebb633a6b5c424` | `research/t74-k554-local-exhaustion/` | 0 of 63 |
| [PR2142](https://github.com/CrocSwap/integer-mult-bounds/pull/2142), Ian Libânio | `5f2f608451252f3330e0d0d5fc7bca63be9d0400` | `research/t74-split-key-kernel-search/` | 0 of 155 |
| [Rounds 4–7, I-resolve](https://github.com/mdumitrean/integer-mult-bounds/tree/23b9ce546f6978bc017d2a970a7fc2b1f96ef6b0/research/t74-local-word-rounds4-7/r6/agents/I-resolve), Marius-Paul Dumitrean | `23b9ce546f6978bc017d2a970a7fc2b1f96ef6b0` | `research/t74-local-word-rounds4-7/r6/agents/I-resolve/` | 0 of 97 |

[RECEIPT.json](RECEIPT.json) lists every path, mode and Git object in these three
subtrees. It separately records identical mode/blob matches elsewhere on main;
same bytes at another path do not establish that an entire module, its review or
its dependencies were incorporated. Conversely, absence at an original path
does not establish absence of all mathematically equivalent content.

The complete 63-file PR1957 subtree is identical in the pinned PR2142 head.
PR2142's older, discussion-linked head
`0c5516bf5bfb5c9c4d09446d3b21028032060fec` differs from its live head, but **both
named scientific subtrees are exactly unchanged**, including file modes. This
is scoped tree equality, not whole-head equivalence or a reason to close a PR.

Main retains PR1957's [disposition](../community-efficient1000-audit/DISPOSITIONS.json),
[source packet](../community-efficient1000-audit/packets/1957.json) and
[check receipt](../community-efficient1000-audit/checks/check-1957.json).
That disposition is correctly **partially reviewed**: default verification
passed, including calibration, sampled frame re-solves, sixteen one-split
searches and packing ILPs. The full **1,797 deletion and 4,461 commuting-position
censuses** still require the declared full replay or an independent exhaustive
certificate. This audit does not perform that replay or change that disposition.

## Why the four sentinel cases need their own link

The pinned PR1957 `tools/costorc.py` uses `INF = 1 << 60`. Its `cost` routine
minimizes over a specified finite family of frame candidates; inadmissible
`zcost` inputs return the sentinel, and `best` starts at that sentinel. Reading
that value establishes failure of that oracle calculation, not a proof about
every legal insertion or compensation word. `tools/akernel.py` inherits this
sentinel and frame-cost convention.

The pinned PR2142 README groups 108 strict searches as 104 CP-SAT infeasibilities
and four “shape-infeasible” cases. Its four JSON records have `shape: false`
and empty `res` lists. Those fields are different evidence from a solver
infeasibility certificate.

The later public [I-resolve findings](https://github.com/mdumitrean/integer-mult-bounds/blob/23b9ce546f6978bc017d2a970a7fc2b1f96ef6b0/research/t74-local-word-rounds4-7/r6/agents/I-resolve/FINDINGS.md)
and [EVIDENCE.json](https://github.com/mdumitrean/integer-mult-bounds/blob/23b9ce546f6978bc017d2a970a7fc2b1f96ef6b0/research/t74-local-word-rounds4-7/r6/agents/I-resolve/EVIDENCE.json)
report explicit repricing of these sentinel candidates:

| Deleted read | Sentinel candidates | Reported within budget | Reported over budget | Corrected C status reported |
| --- | ---: | ---: | ---: | --- |
| B822 | 54 | 14 | 40 | INFEASIBLE |
| B840 | 53 | 14 | 39 | INFEASIBLE |
| B858 | 56 | 15 | 41 | INFEASIBLE |
| B876 | 54 | 15 | 39 | INFEASIBLE |

These are **source-reported results**, extracted without running the solver or
the imported research code. In that source, variant D excludes sentinel
candidates; variant C reprices them. All eight D/C restrictions have reported
HiGHS `INFEASIBLE` checks with the interaction ban; some SCIP checks are
`NOT_SOLVED`. A timeout is not an infeasibility result. The sentinel correction
therefore changes which evidence to inspect, but this receipt does not itself
certify the corrected search or declare the earlier scientific claim refuted.
The author's [public correction and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/2143#discussioncomment-18948791)
identifies the same artifact; it is not a maintainer acceptance decision.

## Model boundary: do not substitute the two searches

| Boundary | PR2142 strict search | Later I-resolve D/C evidence |
| --- | --- | --- |
| Key family | One level | Depth two |
| Coefficients | Half steps, absolute value at most 4 | Quarter steps, absolute value at most 4 |
| Insert count | At most 12 | At most 12 |
| Interaction | Direct write-then-read interactions banned | PR2142 direct interaction ban retained |
| Price information | Per-insert cap plus summed budget | Sentinel exclusion D; corrected sentinel prices C |
| Four recorded deletion prices | `ddel = -6100` | `ddel = -6118`, budget `6117` |

The later record must not be silently presented as a fresh replay of the exact
earlier model. The receipt preserves both price fields rather than reconciling
them by assumption. PR2142 concerns the base word used in 249 of 666 calls;
the extra word's 417 calls are outside its search. Interacting inserts,
multi-deletion kernels and unrestricted word resynthesis remain outside these
bounded negative claims.

The later no-cost B822 diagnostic is also weaker than an exhaustive negative
result: `status` is `UNKNOWN`; it records two exact zero-delta proposals, one
marked `relocation: false`. Do not turn that unfinished diagnostic into “only
relocations are possible,” or turn an empty `gains` list into a universal
impossibility statement.

## Reproduce this audit

Requires Python 3.12+ and Git. From a repository checkout, fetch the immutable
public source objects if they are absent:

```sh
git fetch https://github.com/CrocSwap/integer-mult-bounds.git b4560d9e7216f72b73c5aa940ac099c05e33ccf9
git fetch https://github.com/CrocSwap/integer-mult-bounds.git 1884c509efc004524786e9b7cfcc4aca572316d5
git fetch https://github.com/rohanarun/integer-mult-bounds.git e6a4d34874bb1aeba192c62629ebb633a6b5c424
git fetch https://github.com/ianlibanio/integer-mult-bounds.git 0c5516bf5bfb5c9c4d09446d3b21028032060fec
git fetch https://github.com/ianlibanio/integer-mult-bounds.git 5f2f608451252f3330e0d0d5fc7bca63be9d0400
git fetch https://github.com/mdumitrean/integer-mult-bounds.git 23b9ce546f6978bc017d2a970a7fc2b1f96ef6b0
python3 -I -O -B research/t74-local-search-retention/audit.py
```

Expected: `PASS_T74_LOCAL_SEARCH_RETENTION source_files=315 targets=4 solver_replay=not_run`.
The audit uses immutable Git objects, compares the complete generated JSON with
the frozen receipt, and binds inspected source files by Git blob and SHA-256.
It performs no network access, imports no predecessor program and does not
execute CP-SAT, SCIP, HiGHS or the full historical census. This Git-object audit
is an explicit opt-in command, not a registered source-export replay.

## Milestone and consumer boundary

Under the revision-5 family gate, the milestone is a bounded audit/navigation
result. **Decision: narrow** to the three named sources and stop after exact
retention checks and independent reading. This does not start a new mechanism
or numerical search family. Source and solver-model costs are reported inputs;
all-size precision, restoration, dispatch, transport, hosting and physical
composition costs are **unestablished here**, never zero. No consumer obtains
a cheaper operation from this note, and no prepaid cost is passed to a caller.

## Open next questions

1. Complete PR1957's outstanding full census review if that exact negative claim
   is needed. First use its pinned `--full` instructions or supply an independent
   exhaustive certificate; this source map does not discharge that work.
2. Before relying on the four corrected negatives, independently replay the
   pinned I-resolve candidate construction, repricing and solver restrictions,
   then explain the key/price-domain relation to PR2142. The price discrepancy
   and unfinished no-cost diagnostic are explicit blockers to broader transfer.

Credit remains with Rohan Arun, Ian Libânio and Marius-Paul Dumitrean for the
respective source artifacts, and with the PR1186 toolkit, PR1625 pivot-566 kernel,
PR1672 pivot-554 kernel and T74 word lineage acknowledged there. Prepared by
ywz65 with substantial OpenAI Codex assistance. Apache-2.0.
