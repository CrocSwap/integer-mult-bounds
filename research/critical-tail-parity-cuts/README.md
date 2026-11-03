# Sharp linear growth at the triangular parity compiler's critical tail

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written mathematical proof with exact finite
corroboration. For every dyadic dimension N and every real or complex unit
symbol whose coefficient tail has l1 norm at most one, the exact triangular
Toeplitz parity compiler satisfies

```text
T_N(f) = Q P
max(||P||_infinity, ||P^-1||_infinity,
    ||Q||_infinity, ||Q^-1||_infinity) <= N.
```

This holds at every complete-shear cut, including both endpoints, and for
every order-preserving interleaving of the disjoint children. For each N the
common constant is optimal. The inverse endpoint for f=1-z attains N.
[PROOF.md](PROOF.md) gives the complete induction and its critical a=1,b=0
branch. Infinite Neumann convergence is unnecessary.

The new result is the universal four-operator upper bound at the critical
tail. Brian's [PR4731](https://github.com/CrocSwap/integer-mult-bounds/pull/4731)
already gives 1/(1-eta) for eta<1, and his
[PR4737](https://github.com/CrocSwap/integer-mult-bounds/pull/4737) gives the
sharper forward-prefix bound 1+eta through eta=1. Nick Petalas's
[PR4831](https://github.com/CrocSwap/integer-mult-bounds/pull/4831) gives the
exact binomial suffix law. Those results and the elementary attaining
inverse endpoint retain their credit. No predecessor scientific verifier
is imported or replayed here.

## Reproduction and evidence

Use CPython 3.12 and its standard library, from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/critical-tail-parity-cuts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/critical-tail-parity-cuts/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/critical-tail-parity-cuts
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/critical-tail-parity-cuts --check-source-history
```

Any CPython 3.12 path can replace the local interpreter. Both registered
checks have 60-second limits. The standalone verifier writes nothing and
runs in a Git-free export. It emits `PASS_CRITICAL_TAIL_PARITY_CUTS` in a
generated JSON receipt binding all six package files by SHA256. No receipt
is handwritten or committed.

The exact checker covers 162 rational symbols, including 91 with tail norm
exactly one, and 557 nonleaf tree nodes. It enumerates every distinct legal
cut prefix for each fixture by taking all child-cut pairs. There are 951
cut quadruples. Each has a dense independently eliminated prefix inverse,
literal suffix and inverse suffix, endpoint identities and four norm checks.
Identical operators from different schedules are deduplicated; these are
counts of operators per fixture, not schedules.

The complete quarter-grid tail balls at dimensions two and four are included.
Dimension-eight fixtures cover signed single shifts, mixed odd/even tails and
the even-tail-one case. Six dimensions through 32 check every entry of the
attaining binomial inverse. Seven controls distinguish a wrong Schur sign,
wrong chronology, missing left shear, two invalid symbol domains, the
zero-denominator branch and the necessary dimension loss. These finite
domains corroborate the written real/complex theorem; they do not prove its
unbounded quantifiers or enumerate arbitrary complex symbols.

## Scope and implementation limits

This supplies a log2(N) macro amplification allowance at the critical
boundary. It does not install a precision change or admit eta=1 to the
Gaussian caller. Internal shear gates, additional rounding events,
coefficient preparation, native operations, owned storage and restoration,
movement, tapes, stock, compiler and outer recovery remain separate.
All five selected framework assumptions retain their status. No new kappa,
selected-frontier change, supplier admission, complete multiplication
theorem, independent human review or formal proof-kernel review is claimed.
The selected cold replay, Lean and Docker were unrun.

Power of Ten review is limited to this verifier. The compiler tree uses
bottom-up bounded loops and no recursion. Its census dimension is at most
eight, with at most 123 prefix matrices per node by the recurrence
c(1)=1, c(2m)<=2+c(m)^2. Dense sharpness matrices have dimension at most 32.
Every function has fewer than 60 physical lines. Mathematical checks use
explicit exceptions and remain active under optimization. The six source
reads are the fixed package inventory; there are no subprocesses, imports
of predecessor executables, network calls, dynamic code or mutable global
state. Python/Fraction allocation is a managed-runtime deviation from fixed
allocation. These fixed replay domains bound live data; allocation-free
execution is unclaimed. Warning-strict normal and optimized execution and
AST/function-size inspection provide the available diagnostics.

## Provenance and credit

Scientific base: canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. The selected-baseline orientation passed at kappa 0.003125804;
that check authenticates metadata, not a scientific supplier replay.
[TASK.json](TASK.json) explicitly changes the formal-interface card to a
written component theorem, without a proof-kernel or selected-caller claim.
[SOURCES.json](SOURCES.json) pins the compiler and credited predecessor
notes as historical provenance. Runtime depends only on package files.

The parity factorization retains Vlado Vojdanovski / PR1673 and Cinna Davis /
[PR4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) credit.
James Reed / [PR4699](https://github.com/CrocSwap/integer-mult-bounds/pull/4699)
supplies the earlier one-level shared-budget estimate. Brian's complete-cut
and forward-prefix results, Nick Petalas's binomial suffix law, Ryanson
Jonathan's numerical-ledger motivation and the retained Gaussian/compiler
lineage keep their attribution. Finite triangular inversion and elementary
matrix norm inequalities are classical. The new proof starts from the
retained factorization and finite inverse, without assuming a predecessor's
universal cut theorem.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362993)
records this original question. Live open/account PRs, recent handoffs,
active Discussions, local reservations, all-main README searches and merged
general-form searches were checked. The cached card search covered 412 open
PRs and 6,369 Discussion records with complete remote pagination, but only
108 of 8,917 main note paths were materialized. Targeted Git searches covered
the relevant main README text. Arbitrary diffs, unpublished work and later
posts remain outside coverage. These checks are not a novelty certificate.

## Open next questions

What is the best universal forward-suffix bound at tail norm at most one?
The common N bound is forced by inverse endpoints; the credited binomial
family only needs 1+log2(N) for forward suffixes. Start with a suffix-only
induction on independent even/odd budgets. No universal sharp suffix-only
bound is supplied here.

Can an actual critical-tail caller pay for every gate inside a complete
shear? Start with its literal microprogram, entry/exit contract, rounding
events and complete suffix/tape bill. Internal amplification, preparation
and physical accounting block that extension. No further work is reserved.
