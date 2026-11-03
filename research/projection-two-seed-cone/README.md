# Exact monotone seeds for the block-two projection recurrence

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. For the
unstrengthened projection recurrence, start with a_2=(0,a,b), a>0 and b>=0.
The top ratios T_m=a_m(m)/a_m(1), including block two, are nondecreasing
at every later block exactly when

    3b <= 7a.

They are strictly increasing if 3b<7a. At equality only the first step is
a tie. If 3b>7a, the first step decreases and the next increases, so the
sequence is not monotone. No seed in this domain is nonincreasing.

[PROOF.md](PROOF.md) gives the complete real-parameter argument. Two boundary
seeds, thirty exact prefix differences and two parity checkpoints certify
the infinite tail through a cited uniform matrix bound. Linearity covers
the continuum between the boundary seeds. Finite tests alone do not prove
the universal statement.

This answers the block-two part of Nicholas Stone / [PR5416](https://github.com/CrocSwap/integer-mult-bounds/pull/5416)'s
open monotone-seed question. Krzysztof Wojt / [PR5193](https://github.com/CrocSwap/integer-mult-bounds/pull/5193)
supplies the fixed triangular operator and uniform transfer bound. Jacob
Alan Sussman / PR4628 and Maximilian Lutz / PR4643 supply the recurrence
and engine context; Nick Petalas / PR5151 supplies the general limit;
JoyboyBrian / PR5184 supplies the separate fixed block-four descent theorem.
Credit eumemic / PR288, Swapnil Jain and their retained lineage. Predecessor
scientific verifiers and hook ranks were not replayed or audited here.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/projection-two-seed-cone/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/projection-two-seed-cone/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projection-two-seed-cone
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projection-two-seed-cone --check-source-history
```

Substitute another CPython 3.12 path on another machine. Expected scientific
marker: `PASS_PROJECTION_TWO_SEED_CONE`. The verifier writes no files and
emits a generated receipt bound to all six package files. It compares literal
integer coefficient-pair profiles, full triangular eigenmode profiles and
an independently evaluated scalar top recurrence through block 64. It also
checks the finite tail certificate, a bounded rational seed family and
rejecting controls. Exact counts are emitted by the checker.

The metadata source pins are historical provenance. Direct replay needs
no predecessor files, Git, network service or third-party dependency.

## Limits

The result classifies this arithmetic seed domain. It supplies no new engine
lower bound, hook-rank certificate, physical caller, native supplier, rounded
implementation, complete invoice, multiplication theorem or kappa. Higher
seed blocks, the optional triangle/max recurrence and a=0 are outside scope.
All five selected framework assumptions remain. No selected cold replay,
Lean, Docker, independent human or formal proof-kernel review is claimed.

## Open next questions

1. Classify block-three seeds. This would test whether a finite polyhedral
   cone still suffices. Start with its three-mode adjacent differences and
   separate parity limits; equality on a tail face and finite-prefix control
   remain unresolved. This package reserves no continuation.
2. Bind a qualifying seed to a certified physical engine before using the
   classification as a bound. First supply its actual hook ranks and
   representation proof. The arithmetic criterion alone supplies neither.

## Verifier resource contract

All loops are bounded by block 64, two modes, or the fixed rational seed and
control families. Functions stay below sixty lines. Checks use explicit
exceptions and remain active under optimized Python. No recursion, dynamic
evaluation, subprocess, network or file write occurs. Six regular files of
at most two MiB each are read for receipt hashes. Python integer, Fraction
and collection allocation is a Power of Ten rule 3 deviation; the fixed
block and fixture bounds constrain live memory. Warning-strict development
mode provides interpreter diagnostics. No separate static analyzer or
fixed-memory runtime is claimed.
