# Exact repeated-st tariffs for independent monotone prices

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped written proof with exact finite corroboration; no new kappa.**
For d repeated A2 targets st, the exact formal bill with different
nonnegative nondecreasing rank-price tables is

    H_s(d) + H_t(d),
    H_u(0)=0,
    H_u(m)=min_{1<=k<=min(b_u,d,m)} [tau_u(k)+H_u(m-k)].

The separate finite rank caps b_s,b_t may differ. The two optimal rank
partitions may differ. Concavity is unnecessary. The theorem holds over
every field with arbitrary rank-capped scalar couplings, free scalar GL
mixing and any finite number of restored dirty spectators. The complete
endpoint is diag([st] repeated d,[e] repeated r-d) in M_r(K[S3]), including
every off-diagonal group coefficient.

[PROOF.md](PROOF.md) gives the proof and exact model. ToikY's
[#6821](https://github.com/CrocSwap/integer-mult-bounds/pull/6821) supplies
the separate-letter rank demands and the common-concave predecessor.
Those results are cited inputs, not rechecked deliverables. The new step
removes common pricing and concavity through monotone rank-list truncation
and independent full formal constructions. The integer-partition method
is classical; the related UT3 precedent is Nick Petalas's older #4846.

At d=7 with cap four, let tau_s(k)=3+k^2 for k>0 and tau_t(k)=k/(k+1).
The s-partition is 2,2,2,1, of price 25; the t-partition is 4,3, of price
31/20. The exact bill is 531/20. Using parts 4,3 for both letters costs
651/20. This six-unit improvement concerns the stated abstract tariff,
not an admitted recursive invoice. The first verified extension ends this
investigation.

## Evidence and reproduction

Use CPython 3.12 with the standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/a2-st-monotone-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/a2-st-monotone-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/a2-st-monotone-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/a2-st-monotone-tariff --check-source-history --check-modes
```

Another installed CPython 3.12 can replace the local interpreter path.
Expected markers are `PASS_A2_ST_MONOTONE_TARIFF`,
`PASS_REGISTERED_RESEARCH_PACKAGE` and `PASS_RESEARCH_COMMIT_BYTES`.
`--emit-receipt` prints a freshly generated source-hash-bound JSON receipt
to stdout. Default execution recomputes and compares [RESULT.json](RESULT.json),
writes no files and needs no Git or network. No receipt is handwritten.
Source-provenance validation is separate from the standalone mathematics.

The new checker compares the optimizer with an independently enumerated
integer-partition oracle, including nonconcave tables and zero prices.
It exercises monotone truncation on excess-rank lists, constructs complete
signed group-algebra words over Q, F2, F3 and F5, checks actual paid ranks,
and mixes an arbitrary dirty role through invertible scalar gauges with
both endpoint maps included. A separate faithful regular-action engine
checks every basis column of the smaller fixtures. Every omitted paid
call must change its full endpoint. Invalid optimizer inputs must reject.
The generated receipt records 1,125 partition optima, including 846
nonconcave cases; 17,772 truncation cases; 212 full formal endpoints,
including 64 with unequal caps; 1,344 regular-action basis columns;
1,180 rejected paid-call omissions; 212 rejected missing scalar boundary
maps; and seven invalid-input controls. There are 424 genuinely
dirty-coupled calls among the 1,180 checked paid calls.

The universal lower bound comes from the written proof and its credited
rank-demand premise. Finite checks do not enumerate arbitrary circuits or
establish a multiplication theorem. No predecessor scientific suite,
selected cold replay, Lean or Docker run is part of this work. Independent
human and formal proof-kernel review are unclaimed. Hosted CI remains
separate from local evidence and scientific acceptance.

## Scope, provenance and overlap

The base is canonical main e54523517d0f03e58352e647c403a5af3e525a57,
priority revision 8, selected #7000. The selected source-binding orientation
passed; it was metadata orientation, not a scientific replay. The catalogue
still describes #5599 and is treated as historical assessment context.
TASK.json explicitly changes `bit-new-register-model` to a formal price
side result. This does not satisfy the original native-conversion gate.

[Advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19538484).
Overlap checks covered live open PR metadata, this account's latest 200
PRs, recent handoffs, active Discussions, the cached card search, main-tree
README searches, and merged/all-state searches for Coxeter, repeated st,
monotone and nonconcave tariffs. #6821's repeated-st common-concave
restriction is the direct source. #6817 supplies the earlier common
concave framework and different longest-element questions.
Arbitrary code diffs, sparse local notes and unpublished work limit these
searches. Absence of a match is not a novelty guarantee.

[SOURCES.json](SOURCES.json) pins the source prose, original catalogue and
selected record as historical provenance. The standalone verifier imports
no predecessor code. Frozen packages, upstream and the selected frontier
are unchanged. Retain ToikY #6821; Adam Gall #1941; Ross Richardson
#1966/#1989; Benny Zhao / zhaobenny #6817; David Arias #2738; and their
ywz65, eumemic, Ali Romman and Gareth Davidson register-model lineage.
The new complete monotone-price statement and verifier were produced by
Nick Petalas. No global literature-priority claim is made.

## Open next questions

Can one physically implemented rank-capped call support a complete
nonconcave or letter-dependent price table that profits from independent
partitions? First give its arbitrary-input entry/exit boundary and charge
scalar mixing, movement, ownership, frames, restoration, stock, precision
and all-size compilation. Native realization and the map from scalar rank
to recursive child rank are unknown, so the abstract price does not admit
a supplier. All five selected framework assumptions remain.

For decreasing price tables, the monotone truncation proof fails. A next
mathematical step would exhibit a complete formal counterexample or prove
an exact replacement under a specific decreasing table, including dirty
restoration. This work makes no claim for that changed hypothesis. These
questions are structured in TASK.json; no continuation is reserved.

## Verifier bounds and diagnostics

The verifier has no recursion, subprocess, solver, network, dynamic import
or shared mutable state. Optimizer demand and cap are at most 32; oracle
demands are at most eight with cap at most five. Construction matrices
have at most nine rows and six group labels. Every loop ranges over a
fixed finite domain. Every function fits within sixty physical lines.
Explicit exceptions preserve checks under optimization.

Power of Ten rule 3 has a managed-Python allocation deviation confined to
the bounded finite checker. Tuple/list/Fraction allocation and allocator
internals are not fixed-capacity native memory. The finite domain bounds
live collections; normal and optimized warning-strict replays check the
same invariants. Reassess capacity and diagnostics before increasing these
domains. File reads are restricted to the seven named package artifacts;
no untrusted external input is read. No repository diagnostic configuration
is changed. Full formal dirty-column checks and the separate regular
action exercise the complete declared boundary.
