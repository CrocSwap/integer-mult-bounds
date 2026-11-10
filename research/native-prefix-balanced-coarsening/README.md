# Prefix-balanced native coarsening

This contribution was produced by Nick Petalas.

Claim type: scoped mathematical proof with exact finite corroboration. Replacing
PR6540's shared coordinate threshold with a cumulative carry gives every fixed
output prefix its minimum unbiased grid variance, at most `h^2/4`. Coordinate
marginals and their minimum Euclidean mean squared error remain the same.
The Gaussian native codec keeps its `2kN`-bit residue and `k+ceil(rf/2)`-bit
fresh seed, with an exact two-sided inverse for arbitrary fine-grid inputs.

The new result is the native codec substitution, translation proof, simultaneous
prefix optimum and explicit extra scan cost. Cumulative rounding, scalar
variance inequalities and Gaussian Smith coordinates are credited prior work.
See [PROOF.md](PROOF.md) for the proof and full limitations.

On a canonical 512-coordinate rank-eight native example, the full sum of real
components has error variance `262144*h^2` with the shared threshold and zero
with the carry. A second input attains the new uniform `h^2/4` bound. This is
a fixed-reader precision improvement, with no new kappa or selected-frontier
change. Investigation stopped at this first verified improvement.

## Evidence and reproduction

The exact standard-library verifier checks:

- 5,050 complete small residue vectors through length four, with signed integer
  translates, 38,860 seed vectors and 10,100 translation cases.
- 3,264 arbitrary coarse-output/label/seed endpoints of the new two-sided codec.
- All 1,920 seeds for eight canonical 512-coordinate native ranks, and 48
  additional fine/coarse codec round trips.
- The strict-improvement and sharpness examples, nine rejected domains, a
  reset-carry mutant, a missing-seed mutant and a missing-residue collision.

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/native-prefix-balanced-coarsening/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/native-prefix-balanced-coarsening/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/native-prefix-balanced-coarsening
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/native-prefix-balanced-coarsening --check-source-history
```

Any CPython 3.12 path can substitute. Expected scientific marker:
`PASS_NATIVE_PREFIX_BALANCED_COARSENING`. Optional `--receipt /absolute/path.json`
writes a generated receipt outside the package, binding every package file hash
to the computed counts. The verifier writes no checkout artifacts by default.
Normal and optimized modes use the same executable contracts.

## Sources, scope and costs

Ali Romman's [PR6540](https://github.com/CrocSwap/integer-mult-bounds/pull/6540),
head `5f7c893b6af9a75cb19ad22c6db06ed22eea6f54`, supplies the native grid and
Gaussian quotient premises. Its exact proof and attribution are retained with
a hash in [ORIGIN.json](ORIGIN.json). No predecessor scientific executable or
selected cold replay is run. The new finite reference instantiates canonical C
axes; the written proof applies to the cited monomial recipes at every width.
Knuth and Doerr, Friedrich, Klein and Osbild retain the controlled-rounding
credit linked in the proof. The quotient lineage includes Dugongue's PR5815,
Ali Romman's PR5821 and Nick Petalas's PR5880. Cinna Davis's native interfaces,
DreamingOfClouds's selected word and the retained Gaussian/native/compiler
lineage keep their credit. No general literature-priority claim is made.

An encode/decode round trip adds `4N` remainder extractions and two carry
initializations. The added live carry needs `k+ceil(rf/2)` bits. Native
evaluations, quotient transforms and label digits retain their existing costs.
The scan is serial in the chosen output order. Reversible temporary cleanup,
seed sampling, storage lifetimes, physical routing and the complete tape and
recursive invoice remain unpriced.

The original `centre-path-sharing` card is changed to a numerical boundary side
result. It supplies no selected consumer or eliminated paid operation. Arbitrary
later linear readers, an order chosen after observing the seed, adaptive seed
reuse and complete accumulated caller error are outside the result. All five
selected framework assumptions remain. Lean, Docker, complete native admission,
independent human review and formal proof-kernel review are unrun or unclaimed.

The package is based on canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8 and selected
PR6030. The live selected binding command passed. Main/merged searches, account
contributions, open PRs, handoffs and local reservations were checked. The
overlap cache covered 521 open PRs and 6,527 Discussion records; local sparse
notes, arbitrary historical diffs and unpublished work remain coverage limits.

## Open next questions

1. Can a selected native consumer use the declared fixed prefix order? Pin one
   event and enumerate its actual readers. A source-bound consumer and complete
   error/precision invoice are missing.
2. Can the carry scan and residue codec fit a physical caller budget? Start with
   one 512-coordinate round trip, including its 2,048 added remainder steps,
   seed/residue lifetimes and temporary cleanup. Physical routing, reversible
   gates and a complete paid invoice remain blockers.

The structured questions are in [TASK.json](TASK.json).

## Implementation bounds

The exact reference permits at most 512 complex coordinates, eight active
axes, precision at most 16 and integer payloads at most 4,096 bits. There is
no recursion. Functions are at most 31 lines; all loops have bounds from these
limits or the fixed verification fixtures. Explicit `require` contracts remain
active under optimized Python.

Power-of-Ten rule 3 has a managed-runtime deviation in `model.py` and
`verify.py`: Python allocates tuples and arbitrary-precision integers during
operation. Finite shapes and payload guards bound live data. Verification uses
at most 1,024-component moment accumulators and a 16,384-bit residue label.
No hard allocator or hardware memory bound is claimed. A physical fixed-buffer
implementation is the follow-up when a consumer contract is selected.
Warning-strict normal/optimized replay and in-memory syntax compilation are
the available diagnostics; no standalone type checker is required by this
standard-library package.

Apache-2.0, under the repository license.
