# Excluding 48 flagless span-six dirty-auxiliary pools

Scoped mathematical proof with finite exact corroboration. This contribution
was produced by Nick Petalas. No new kappa or selected-frontier change.

In the four-register abelian bit model, eight nonzero rank-one calls at
rational frame span six cannot realize three invertible 3-by-3 targets when
their noncoordinate projectors belong to any of 48 specified flagless pools.
The fourth role is arbitrarily dirty and may end at any diagonal monomial.
These are 48 of the 72 exceptional pools left by unpaidmoon's
[PR4119](https://github.com/CrocSwap/integer-mult-bounds/pull/4119).
The other 24 pools, and span five, remain open here.
The scalar catalogue and its 24/48 orbit split were already established
by woklerx's [PR1846](https://github.com/CrocSwap/integer-mult-bounds/pull/1846).
The new result rules out realization of its 48-pool orbit.

The new step keeps the target coordinate-diagonal. A common left or right
kernel supported on two coordinates forces the noncoordinate subword to
contribute zero on both. One invertible data target then consumes three
coordinate calls. The resulting five-call subword would have to realize two
invertible targets, contradicting waynenilsen's six-call theorem with dirty
auxiliaries. [PROOF.md](PROOF.md) gives the quantified argument and names
its inherited mathematical premises.

The excluded pools are the disjoint coordinate-permutation orbits of
`(0x0003,0x0022,0x0dd0)` and its transpose. Bit `4i+j` is entry `(i,j)`.
The first pool has common right kernel `e_2+e_3` and common left kernel
`e_3`. Each orbit contains 24 pools. The remaining orbit has representative
`(0x0003,0x0022,0x0550)` and both kernels supported on the same coordinate.
No arbitrary change of basis is used to preserve a coordinate target.

## Evidence and reproduction

Use CPython 3.12 and the standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/flagless-kernel-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/flagless-kernel-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/flagless-kernel-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/flagless-kernel-obstruction --check-source-history
```

Any CPython 3.12 installation can replace the displayed interpreter.
The direct checker emits `PASS_FLAGLESS_KERNEL_OBSTRUCTION` in a generated
JSON receipt bound to the six package-file hashes. It writes only to stdout,
imports no predecessor code, and works in a Git-free package export.
Correctness checks use explicit exceptions and remain active under `-O`.

The finite evidence includes the three disjoint coordinate orbits and their
kernel supports, independent literal binary matrix products, 1,920 formal
words through length three and 7,632 coefficient matrices, 3,888 diagonal
label assignments, and 96 critical eight-call rank allocations. Every
critical allocation has five noncoordinate calls and would require the
cited two-target theorem's impossible endpoint. The nine-call budget
control survives this relaxation; it is not a nine-call construction in
the excluded pools. Named controls preserve the remaining coordinate-kernel
orbit and distinguish coordinate interleaving from subword kernel invariance.

The written proof supplies the universal rational-frame exclusion. The
finite word checks corroborate its kernel identity, rather than enumerate
all rational frame relations or certify every possible endpoint.

## Scope and provenance

Canonical base is `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority
revision 7. The `bit-new-register-model` card is refined to this explicit
four-register handoff. Its current source-binding orientation command,
`scripts/research_selected_baseline.py`, passes. This authenticates selected
metadata only; it is not a selected cold replay.

[SOURCES.json](SOURCES.json) pins the predecessor statements, catalogue and
selected record as historical provenance. No predecessor implementation or
scientific receipt is imported. The relation-support reduction from PR4119
and the two-target theorem from PR1882 remain cited proof dependencies.
Their scientific suites were not replayed as this contribution.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19146123)
follows live PR, Discussion, recent-account, main-tree and merged-term checks.
The cached entry scan reports 341 open PRs and 4,446 Discussion records with
complete remote text pagination, but only 162 of 6,996 local notes. Sparse
notes, arbitrary unsearched diffs and unpublished work limit novelty coverage.
Search absence is not a novelty certificate.

This is a partial formal-register obstruction, not a native supplier or a
complete multiplication theorem. Physical legality, caller/frame/access costs,
dirty restoration in an actual implementation, stock, precision/tape,
compiler and outer admission remain unpriced. Independent human and formal
proof-kernel review are unclaimed. No Lean, Docker, predecessor scientific
suite or selected operator replay was run.

## Open next questions

- Can the remaining 24 coordinate-kernel pools realize the eight-call
  endpoint? Start with the literal representative and retain both cube
  relations and target coordinate projectors. The support union has size
  one, so the new rank budget does not decide this branch.
- Can one changed register mechanism occur in a literal native caller with
  a favorable complete bill? First specify independent targets, arbitrary
  dirty inputs and every frame/access/restoration charge. No such caller
  or physical invoice is supplied here.

## Credit and implementation limits

Credit woklerx/PR1846 for the exceptional scalar catalogue and orbit split;
unpaidmoon/PR4119 for the relation-support
reduction and open question; JoyboyBrian/PR5075 for the surviving-branch
handoff; waynenilsen/PR1882 for the dirty-auxiliary two-target theorem; and
Ali Romman/PR468 for the formal alphabet and low-span method. The retained
lineage includes eumemic/PR288 and huxint/PR203. Classical kernel and rank
arguments are not claimed as new techniques. The new obstruction and its
48-pool application were produced by Nick Petalas. Apache-2.0.

The code has no recursion, solver, subprocess or network access. Its matrix
domain is fixed at four binary coordinates; formal words have at most three
letters and eight monomials. Coordinate budgets stop at nine calls, and the
largest allocation loop has at most 7^4 candidates. Functions stay below
60 lines. Power of Ten rule 3 has a managed-runtime deviation: Python exact
integers, dictionaries and standard iterators allocate dynamically within
these fixed domains. No fixed-pool memory implementation is claimed.
Warning-strict normal and optimized replay supplies interpreter diagnostics;
no unavailable external static analyzer or proof kernel is claimed.
