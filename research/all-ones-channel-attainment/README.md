# Attain the all-ones channel bound at every depth

This contribution was produced by Nick Petalas. Apache-2.0.

For every g>=3, the balanced dirty word on n=2^g-1 free factors has
exactly 4g-3 maximum-mass channels at one explicitly specified cut and
register. Every selected channel has mass g-1. Together with the cited
upper bound of [PR5938](https://github.com/CrocSwap/integer-mult-bounds/pull/5938),
this proves

    E_k(2^g-1) = k(g-1),  1 <= k <= 4g-3.

Claim type: scoped written mathematical proof with exact finite
corroboration. Independent human and formal proof-kernel review are unclaimed.
No new kappa, precision policy or supplier admission is claimed.

The new step closes PR5938's first open question, attainment for every g.
That predecessor proves the all-g upper bound and records finite attainment
through g=6. Philippe Van Velzen's PR2177 reports a g=7 census and supplies
the transport lemmas used here. Those results are cited premises. Their
verifiers and numerical outputs are not replayed as this contribution.

## Construction

In the positive root call, take the completed leaf on the phase path

    V', V', U, followed by g-3 copies of V.

Read scratch level three. The cut follows exactly

    t_g = (43*4^(g-2)+2)/3 - 3*2^(g-1)

completed leaves. A recursive family supplies 2g-3 distinct error
injections in each of the root U and U' phases. Three more come from
the upper-half inverse pair. The resulting (4g-6)+3 channels all have
mass g-1. [PROOF.md](PROOF.md) gives the families, readout row and
noncancellation argument for every g>=3.

This is a free-algebra channel-mass statement for independent error
symbols. It does not assert simultaneous numerical attainment of the
separate polynomial norm bounds under one fixed operator assignment.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -B research/all-ones-channel-attainment/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -X dev -W error -O -B research/all-ones-channel-attainment/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/all-ones-channel-attainment
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/all-ones-channel-attainment --check-source-history
```

Other hosts may substitute their CPython 3.12 path. The last command checks
the committed publication. Each scientific command prints
`PASS_ALL_ONES_CHANNEL_ATTAINMENT` inside a generated JSON receipt bound
to all seven package files by SHA256. No receipt is handwritten. The
verifier writes nothing and needs no Git, network or predecessor code.

The bounded replay checks g=3,...,9, including the new larger witnesses
at n=255 and 511. At each specified cut it scans every injecting leaf,
requires that the constructed family is exactly the set of mass-(g-1)
channels there, and compares every selected channel polynomial with a
separate forward-column propagation. There are 147 selected channels
and 847 signed monomials in each propagation direction. It also checks
the literal prefix against the closed readout row, both position formulas,
and the four phase-group counts. Six invalid-input/duplicate-injection
rejections and five semantic controls cover changed cuts, wrong scratch,
factor order, inverse signs and a nonfamily leaf. Every check remains
active under optimized Python.

The universal result rests on the written induction. These finite checks
corroborate the new construction; they do not certify the predecessor's
upper bound over all cuts.

## Scope and credit

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority
revision 8, selected PR6030. The selected binding-only orientation passed.
The uniform-transfer-audit card is explicitly changed to a transport
attainment side result, rather than discharge of a selected assumption.
[SOURCES.json](SOURCES.json) pins predecessor proofs as historical
provenance. No external live inputs or imported implementations are needed.

Credit Nick Petalas's PR5938 for the all-ones upper bound and question;
Philippe Van Velzen's PR2177 for the model, complete-call identity,
exit/readout/inverse lemmas and the existing single-chain construction;
and Chafik Boukhalfa's PR628 for the balanced dirty word. Retain the
predecessor lineage of woklerx, Charles Bethin, Arham Tahir, Adam Gall,
Hanson Sun and ywz65. Word factorization and elementary recurrences are
classical. The new recursive family, common cut and all-g attainment
proof are the contribution. Predecessor files and credit are unchanged.

The source PR opened 2026-10-27 at 14:44:31 UTC, more than seven days
before the [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19377697).
Live handoffs, active Discussions, account/open PRs, merged/general-form
searches, all-main README formula/object searches and local reservations
were checked. The broader cached search had complete remote pagination
but incomplete sparse local notes. Unpublished work and arbitrary diffs
remain outside that coverage; no search proves novelty.

## Limitations and executable bounds

Lower channel mass levels, E_infinity, deterministic rounding, correlated
errors, internal leaf intermediates and a physical precision invoice are
outside the theorem. Physical access, storage, native legality, compiler,
stock, tape and analytic recovery remain separate obligations. No selected
cold replay, Lean, Docker, human review or proof-kernel review was run.
The selected frontier is unchanged.

The executable caps g at nine, n at 511, emitted leaves at 262,144,
phase paths at nine, and symbolic polynomials at 512 terms of degree
at most 511 with coefficients of at most 64 bits. Unsupported requests
fail; they are not counterexamples to the all-g theorem. All loops have
fixed bounds or bounds from these capacities. There is no recursion,
subprocess, external dependency, generated code or callback dispatch.
Functions fit within 60 physical lines. Warning-strict normal/optimized
execution and AST syntax inspection supply the local diagnostics.

Power of Ten rule 3 deviation: CPython allocates integers, tuples and
dictionaries during this bounded offline replay. The fixed event,
register, polynomial and degree capacities bound live state, and only
one case persists at a time. Both registered modes exercise these caps.
A fixed-allocation port would be required before using this as a
long-lived or native component. No production configuration changes.

Build the Lever led to the explicit witness constructor. Prove It Works
led to checking its full literal channel polynomials in two propagation
directions. The autonomous local run stops at this first proved result.

## Open next questions

- What is the next segment of E_k(2^g-1) after k=4g-3? Start with the
  mass-(g-2) histogram at this same explicit cut, then prove a matching
  upper bound over all cuts. The present theorem gives neither that
  global comparison nor the lower-mass optimum.
- Can a production precision contract use these independent channels?
  First bind its actual completed-leaf error model and reachable state
  to the transport definition. Numerical rounding correlations and the
  complete physical precision invoice remain blockers.
