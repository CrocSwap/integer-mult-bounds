# Two-axis monomials need at most eight elementary records

**Exact finite certificate. No new kappa.** In the selected two-axis
affine-quadratic monomial alphabet, the directed diameter is exactly eight.
The particular monomial taking sixteen records under unpaidmoon's
[PR #7286](https://github.com/CrocSwap/integer-mult-bounds/pull/7286)
elimination has a shortest recipe of six records:

```text
C01, X1, C10, S1, omega, omega.
```

This contribution was produced by Nick Petalas. Apache-2.0.

## Result and exact alphabet

An address is (x0,x1), numbered x0+2*x1. C01 adds bit 0 to bit 1;
C10 adds bit 1 to bit 0. Xj flips bit j, Sj multiplies by i^xj, CZ
multiplies by (-1)^(x0*x1), and omega multiplies by i. Each record costs
one. Words execute left to right. S inverses and omega inverse each
cost three records. No absolute phase is discarded.

The finite group consists of all

```text
|x> -> i^(a+c0*x0+c1*x1+2*q*x0*x1) |A*x+b>,
A in GL(2,F2), b in F2^2, a,c0,c1 in Z/4, q in F2.
```

There are 3,072 distinct elements. The complete distance census is

| Distance | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
|---|---|---|---|---|---|---|---|---|---|
| Elements | 1 | 8 | 42 | 162 | 467 | 884 | 940 | 475 | 93 |

The six-record word has exactly the predecessor's witness parameters
`A=[[0,1],[1,1]], b=(1,1), a=c0=c1=3, q=1`. Its certified shortest
distance is six. A diameter witness is

```text
|x0,x1> -> i^(3+3*x1) |x1,x0>,
C01, C10, C01, X0, S0, X0, omega, omega.
```

[PROOF.md](PROOF.md) defines the finite certificate theorem and proves why
its exhaustive checks establish shortestness. It also derives both words
by hand. The predecessor's exact elimination count remains a cited result;
none of its scientific code is imported or replayed.

## Verification and reproduction

From the worktree root, CPython 3.12 and its standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-axis-monomial-geodesics/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-axis-monomial-geodesics/independent_check.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-axis-monomial-geodesics
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-axis-monomial-geodesics --check-source-history
```

Another CPython 3.12 executable may replace the local path. VERIFY.json
registers both scientific commands in warning-strict normal and optimized
modes, each with a sixty-second limit. Default runs write nothing.

The primary checker uses literal actions on four basis addresses. It
enumerates 3,072 states and 24,576 labeled transitions, then replays a
shortest word for every state. It includes four endpoint-changing controls
and two exact-reason domain rejections. The separate checker uses binary
matrix and phase-polynomial parameters, generates the full normal-form
inventory and checks every polynomial transition against literal gate
matrices. Distance inequalities on every edge and a decreasing predecessor
for every nonidentity certify optimality. Three damaged certificates and
one unavailable inverse gate must be rejected.

Both programs print generated receipts binding all seven package files and
the same sorted distance table. Its canonical SHA256 is
`4aec51eef32c395d364567018d10626bc96fe507b0591fa312ef3c3688ce1d4c`.
All four registered commands passed locally on CPython 3.12.15; the primary
checks took 0.045 and 0.047 seconds, and the separate checks each took
0.153 seconds. These are checker durations, not a runtime speedup claim.
The table can be exported outside the checkout and checked independently:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/two-axis-monomial-geodesics/verify.py --write-certificate /fresh/output/DISTANCES.json
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B research/two-axis-monomial-geodesics/independent_check.py --certificate /fresh/output/DISTANCES.json
```

The directory must exist; export refuses to overwrite an existing file.
Receipts are generated at execution, not hand-written or committed. The
normal-form checker does not import the primary program or any predecessor
module. These are separate implementations, not independent human review.

## Scope, sources and limits

This answers the n=2 first working example in Open next question 1 of
unpaidmoon #7286, head `a51fb99e3cf11c32d7318bd12c35f6d08e07927e`.
It does not alter or audit that pending package. The selected alphabet and
normal form are pinned through Cao Yifan / intqwq #4610's retained
[specialization](../final4610-independent-admission/SPECIALIZATION.md).
Its physical/compiler/native predecessors retain their credit. Classical
finite-group enumeration and shortest-path certificates are not new methods;
the exact synthesis distances and attaining words are the contribution.

The formal-interface-lemma card changes scope to this finite synthesis
side result. Canonical base is `e54523517d0f03e58352e647c403a5af3e525a57`,
priority revision 8, selected #7000. Its source-binding orientation passed;
that is not a selected construction replay. The advance
[claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19592092)
records the bounded question. Live open PRs, recent claims, local locks,
merged-PR searches and main-tree searches were checked before claiming.
These searches do not cover unpublished work or prove universal novelty.

The result is for one column, two axes and exactly the eight unit-price
directed records. More axes, extra workspace, a different phase price,
projective equality or a different gate set may shorten recipes. The
operator identities tensor-lift, but shortestness at other column counts
is unclaimed. No physical tape saving, source-word installation, new
supplier, selected-frontier change, uniform all-n optimum or complete
multiplication theorem is established. Independent human and formal
proof-kernel review are unclaimed. No Lean, Docker or selected cold replay
is run; all five inherited assumptions retain their status.

## Open next questions

- Can two-axis geodesics replace explicit local subwords in one actual
  selected normalizer? First find one literal contiguous subword, compare
  its complete endpoint and retain all restoration and record prices.
  This package does not search or install such substitutions.
- What is the three-axis directed diameter in the same alphabet? First
  design a certified reduction or bounded enumeration of that larger
  group. The present certificate gives no all-n diameter formula.

## Implementation bounds

Each group inventory contains 3,072 states. Every search is bounded by
3,072 state removals or eight layers, with eight generators per state.
An independent potential check visits exactly 24,576 labeled transitions;
failed-certificate controls may stop early. Each basis action has four
entries. Functions are below sixty lines. Explicit exceptions preserve
checks under -O; normal and optimized warning-strict commands are registered.
No runtime Git, network, subprocess, recursion or dynamic code evaluation
is used. Optional certificate input is a regular file capped at one MB.
Receipt reads cover seven regular files of at most one MB each.

Power of Ten rule 3 has a managed-runtime deviation: CPython dynamically
allocates bounded integers, tuples, dictionaries and sets. The fixed group
and file bounds limit live state; fixed-buffer allocation is not claimed.
Rule 9 has a bounded callback deviation for two rejection controls. Their
only targets are the named local step and word evaluator, with no external
dispatch. No repository-wide analyzer configuration is changed.
