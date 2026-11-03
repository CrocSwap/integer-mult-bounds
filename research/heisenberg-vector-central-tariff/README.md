# Exact vector-label Heisenberg central-target tariff

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new κ.** In the binary
group algebra of H(m,n), allow a paid rank-one register call to carry any
nonzero vector label x(u) or y(v), at one call per vector. For nonzero
central targets Z_t on P independent dirty roles, put K=Σ_t rank(Z_t).
The exact minimum is

    2(K+P) = 2 Σ_t (rank(Z_t)+1),

for every finite number of exactly restored dirty spectator roles.
Arbitrary invertible scalar mixing and nilpotent rank-one couplings are
allowed. Zero target matrices need no calls.

The [written proof](PROOF.md) gives an explicit closed vector walk of this
length in the full group, and matching natural/contragredient rank-nullity
bounds. Its rank-two example takes six calls instead of the eight needed
by two separate rank-one commutator words:

    x(e1) y(e1) x(e1+e2) y(e2) x(e2) y(e1+e2) = z(I2).

This is a new tariff for an enlarged alphabet. Cinna Davis's
[PR2258](https://github.com/CrocSwap/integer-mult-bounds/pull/2258) supplies
the coordinate-edge H(m,n) model and proof strategy. Its edge theorem is
cited, not audited or replayed. The cost of producing a vector label from
coordinate operations is outside the changed unit-call model. In
particular, this is no claim of a physical supplier saving.

## Evidence

The standard-library [verifier](verify.py) is standalone and read-only:

- It enumerates all 682 central matrices for 1≤m,n≤3. Independent minor
  ranks agree with the constructive decomposition. Complete Cayley BFS
  covers 37,448 group elements across these nine groups and proves the
  predicted one-role minimum for every central matrix in that domain.
- For Z=I2 with a restored second dirty role, its 54 generators include all
  nine nonzero rank-one binary 2×2 matrices and all six vector labels.
  Exact full-formal balls have layers 1, 54, 1,971 and 64,044. All 2,026
  radius-two join queries have no radius-three hit for the target. This
  covers every normalized word of length at most five. The explicit
  six-call witness is also found by the same join adapter at split 3+3.
- Five literal four-role formal endpoint fixtures include different target
  ranks, zero targets and arbitrary restored dirty spectators, through a
  rank-four central matrix. Every one of the 56 single-call omissions is
  rejected. Four invalid matrices and a chronology mutation are rejected;
  reversal is checked as a valid inverse control.

Finite checks corroborate the proof; they do not establish its universal
quantifier. Each invocation prints a generated JSON record with source
hashes for the verifier and proof, followed by
`PASS_HEISENBERG_VECTOR_CENTRAL_TARIFF`. No receipt is hand-written.

## Reproduce

From the repository root, with CPython 3.12 and no third-party dependencies:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/heisenberg-vector-central-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/heisenberg-vector-central-tariff/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/heisenberg-vector-central-tariff
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/heisenberg-vector-central-tariff --check-source-history
```

Any CPython 3.12 path may replace the local interpreter above. Normal and
optimized scientific replays are registered separately in [VERIFY.json](VERIFY.json).
The source/history check requires the package to have been committed.
The optional `--skip-mixed` direct mode omits the finite two-role search
and is not the registered complete replay.

## Limits and credit

This counts formal paid calls. Arbitrary vector labels cost one by
hypothesis; their production, physical scalar mixing, native implementation,
source access, hosting, caller scheduling, precision/tapes, compiler closure,
recursive invoices and recovery are unproved. All five selected framework
assumptions remain. No selected record is changed. Independent human and
formal proof-kernel review are unclaimed.

Credit Cinna Davis / 1337isnot1337, PR2258, for the main predecessor,
including its eumemic / woklerx normalized-register and UT3/UT4
shared-middle lineage. Rank factorization, unitriangular representations,
rank-nullity and closed-walk accumulation are classical. No general
literature-priority claim is made. [SOURCES.json](SOURCES.json) pins the
predecessor proof and README as provenance, not scientific replay inputs.

The `bit-new-register-model` card has changed scope to a formal
changed-alphabet cost theorem. The selected binding-only first example
passes. This is a small mechanism/obstruction result rather than a native
implementation or complete multiplication theorem. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19376637)
records the proposed formula before the checks.

Overlap checks inspected canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, live open/account PR lists,
recent handoffs, active Discussions, targeted all-state/merged searches,
and a complete cached scan of 598 open PRs and 6,673 discussion records.
Distinctive and general-form terms included Heisenberg, vector labels,
compound labels, central matrices and rank-based commutator tariffs.
The cached scan is timestamped November 3, 2026, 14:58 UTC. Closed PRs
outside targeted searches, arbitrary diffs and unpublished work remain
coverage limits; no-match searches are not novelty certificates.

## Open next questions

1. What is the exact tariff when label costs depend on the support size of
   u or v? The unit-vector-label assumption is the unpriced physical step.
   Start with the rank-two six-call word and charge each coordinate
   constituent, then seek a weighted lower bound. The blocker is a specified
   native vector-label interface and cost model.
2. Can a concrete bit supplier realize these labels and central outputs at
   a favorable complete signed bill? Start by binding the six-call rank-two
   word to one exact source/consumer boundary, including every dirty return.
   No such mapping or caller invoice is supplied here.

## Verification design

The verifier has no recursion, subprocesses, network, dynamic code or writes.
Its fixed replay dimensions bound every loop: the largest Cayley domain is
32,768 elements, the mixed search has at most 1+54+54²+54³ stored states,
and formal fixtures have four roles with m,n≤4. Python allocates integers
and collections dynamically, a managed-runtime deviation from Power of Ten
rule 3. Live memory is bounded by these finite capacities; formal group
supports have at most 2^24 bits per matrix entry. Increasing these domains
requires a new capacity review. Functions fit within 60 physical lines;
explicit `require` checks remain active under optimized Python. Strict
warnings and AST compilation provide available interpreter diagnostics;
no additional static analyzer is installed in the command environment.
