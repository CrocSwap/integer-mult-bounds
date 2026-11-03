# Sharp uniform error from transient transfer leakage

A fixed physical transfer table can have a small error at every width even
when it admits no positive contraction metric for its complete local operator.
This package proves a separate-block certificate and gives a sharp two-state
example outside the whole-table test in its stated representation.

Claim type: scoped written proof with finite exact corroboration. No new
kappa, physical supplier or selected-frontier change is claimed.

For a fixed triangular virtual table, suppose the active block has norm at
most one, the transient block has norm at most `rho<1`, and its leakage into
the active block has norm at most `delta`. Use the complete coherent physical
blocks and positive virtual metrics. With unit boundary norms, the complete
endpoint error satisfies

```text
||E_f||_op <= delta (1-rho^f)/(1-rho),       every f>=1.
```

[PROOF.md](PROOF.md) states the general boundary factors, fixed-table and
exact-zero hypotheses and proves the operator bound. It includes all physical
input/output entries and required role returns. There is no factor depending
on the exponentially growing payload dimension.

For diagonal physical tables with virtual matrices
`[[1,delta],[0,rho]]` and `[[1,-delta],[0,rho]]`, the bound is an equality at
every positive width. The uniform supremum is exactly `delta/(1-rho)`.
The choice `delta=1/1024, rho=1/2` gives error strictly below `1/512` at each
finite width. No positive-definite Hermitian metric can make both matrices
nonexpanding. This last statement concerns this two-state representation,
not every representation of the same endpoint.

## Source and contribution

The question comes from zxv's
[PR5441](https://github.com/CrocSwap/integer-mult-bounds/pull/5441), uniform
approximation direction. Ali Romman's
[PR5451](https://github.com/CrocSwap/integer-mult-bounds/pull/5451) supplies
the whole-table sufficient metric test and coherent physical norm argument.
The new step is a transient-leakage certificate and a sharp bounded family
that cannot pass that test in its given representation. Neither predecessor
is audited, replayed or claimed as this contribution.

Classical block-product expansions, Hilbert norms, geometric series and PSD
null-row arguments retain their credit. The predecessors' weighted-automata,
matrix-product, native, phase and compiler lineage retains its credit. No
global literature-priority or new general stability-algorithm claim is made.
This contribution was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

The formal-interface-lemma card has explicitly changed to this written
numerical-interface side result. It is not a formal-kernel proof or a binding
to an actual selected caller. The selected-baseline metadata orientation
passed; it was not a scientific replay. Canonical base is
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected PR6030.
[TASK.json](TASK.json) records the scope, overlap limits and next questions;
[SOURCES.json](SOURCES.json) pins the retained proof sources as provenance.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375359)
matches the delivered mathematical scope.

## Reproduce

From the repository root, CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/transfer-transient-leakage/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/transfer-transient-leakage/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/transfer-transient-leakage
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/transfer-transient-leakage --check-source-history
```

Another CPython 3.12 executable may replace this local path. Direct replay
prints a generated JSON receipt with status `PASS_TRANSFER_TRANSIENT_LEAKAGE`
and SHA256 bindings for every package file. It writes nothing and requires
neither Git nor network access. The registered hook runs normal and optimized
warning-strict modes. The source-history preflight requires committed files.

The checker enumerates all 65,520 physical words across eight rational
families at widths 1 through 12, confirming all 96 sharp norms. It constructs
24 complete physical matrices with 4,080 entries across six certificates at
widths 1 through 4. These include noncommuting virtual actions, coherent
physical mixing, two input/output roles and a nonidentity metric. Literal
weighted and unweighted endpoints agree entry by entry.

An independent principal-minor/permutation-determinant oracle agrees with
the Schur PSD test on all 729 symmetric three-by-three ternary matrices.
Another 32 exact fixtures corroborate the incompatible metric equations.
Thirteen invalid certificates reject, including a coherent cross-input
sum whose individual columns pass their stated leakage bound, and omitted
input/output role charges. The universal theorems rest on the written proof.

## Limits and implementation bounds

This is a sufficient certificate for a fixed linear residual representation.
It neither classifies every bounded family nor certifies nonlinear rounding
merely from a local table. The triangular zero and block/boundary norm bounds
must all be established for the complete residual. Failure to find these
data is inconclusive.

Actual native source/version extraction, physical realization, dirty restoration
outside the represented endpoint, coefficient access, tape movement, storage,
precision, stock, compiler and recovery budgets remain open. All five selected
framework assumptions remain. No selected scientific cold replay, predecessor
executable, Lean or Docker run is included.

The terminating checker has no external data input, recursion, subprocess,
network or filesystem writes. The fixed fixture domains bound every loop.
The largest literal endpoint is 32 by 32; the word iterator holds one word
of at most 12 bits. Matrix helpers enforce a 64-by-64 ceiling, and source
authentication reads exactly six files capped at 128 KiB each. Functions are
under 60 physical lines. Meaningful exception-based contracts remain active
under optimization. File hashing assumes a stable package during replay.

Power-of-ten rule 3 deviation: CPython and Fraction allocate bounded objects
during this offline checker. Fixed fixture dimensions and word lengths, streamed
word enumeration and 120-second registered timeouts constrain the work. A
fixed-storage implementation is needed before use in a steady service.
Rule 8 deviation: the standard-library frozen dataclass generates its fixed
record initializer; fields and the finite replacement controls are static.
No external registration or generated executable code is accepted.
An explicit record initializer is the replacement if this checker is ported
to an environment that prohibits generated initializers.
Warning-strict normal and optimized replay and AST inspection are the available
diagnostics. Ruff is absent in the local environment; no global lint setup is
changed. Build the Lever led to the rerunnable exact checker. Prove It Works
led to literal complete-operator checks and the separate PSD oracle. Laziness
Protocol kept the change within one six-file package.

## Open next questions

1. Can one actual consumer's complete residual be put in this triangular form
   with a useful `rho` and `delta`? First extract all role/version blocks and
   prove its exact lower-left zero. Source extraction, physical access and a
   separately justified recovery tolerance are the blockers.
2. Can a paid physical implementation preserve the transient splitting without
   introducing feedback or omitted returns? Start with one explicit local
   operator and charge its preparation, use and cleanup. No such realization
   or complete invoice is supplied here.
