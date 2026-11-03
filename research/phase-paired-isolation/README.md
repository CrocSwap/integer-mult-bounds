# Exact isolation capacity for shared phase charts

This contribution was produced by Nick Petalas. Apache-2.0.

Scoped written algebraic proof with exact finite corroboration. For invertible
maps L and R over any field, the largest identity block that the same input
and output bases can isolate in both maps is

    A = L^-1 R,   N = A-I
    capacity = 2 nullity(N) - nullity(N^2).

Both cross blocks must vanish on arbitrary inputs. A common completed row
readout has only the weaker bound nullity(N). The difference is exactly
nullity(N^2)-nullity(N), and can be arbitrarily large. [PROOF.md](PROOF.md)
constructs attaining bases without Jordan form and applies the criterion to
ordinary bases over Q(i)[q^2] inside Q(i)[q]/(q^4-1). The four-phase capacity
is the smaller of the two signed-pair capacities.

The dyadic example M(q)=I+((1+q)/2)E12 has a completed second readout and a
literal inverse, yet its capacity is zero even with all Gaussian rational
even-q charts. For m copies and b independently restored identity workspace
coordinates, the exact capacity is b. The workspace supplies no additional
independently isolated data channel. Multiplying the data map by q^-1 instead
gives completed central Gaussian readouts. Its exact Gaussian isolation capacity
is zero for any finite restored identity workspace. This is a scoped
all-dimension obstruction,
not a finite search failure or a complete multiplication theorem. No new kappa
is claimed.

## Evidence and reproduction

The constructive elimination and separate exhaustive finite oracles check
both zero cross blocks. Exact counts and a hash-bound receipt are generated
to stdout; no expected receipt is handwritten. The finite coverage is:

- All 175 binary relative maps through order three and 28,261 conjugations.
- All 36 ordered binary map pairs of order two and 1,296 pairs of input/output bases.
- All 48 ternary relative maps of order two and 2,304 conjugations.
- 54 rational profiles, 64 four-phase branches including 16 with positive
  capacity, twelve identity and twelve Gaussian workspace profiles, and eleven
  rejecting controls. The universal statements rest on the written proof.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/phase-paired-isolation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/phase-paired-isolation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/phase-paired-isolation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/phase-paired-isolation --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. Expected markers
are PASS_PHASE_PAIRED_ISOLATION, PASS_REGISTERED_RESEARCH_PACKAGE and
PASS_RESEARCH_COMMIT_BYTES. The direct verifier has no predecessor runtime
inputs and works from a Git-free copy. It writes no files. Registered commands
have 120-second limits; their local times are recorded in the PR body.

## Scope and credit

This is an original question under the joint-query-controller card, explicitly
changed to an algebraic interface side result. The baseline binding check passed
on canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a, priority revision 8,
selected conditional kappa .003125804. [Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19371214).

Invariant complements, primary decomposition, rank-nullity and interpolation
by orthogonal idempotents are classical. No global literature priority is
claimed for them or the general direct-summand formula. The new contribution
is the explicit paired ordinary-chart criterion, constructive interface and
workspace-stable Gaussian example separating readout from independent isolation.
No predecessor construction, word, invoice or executable is used as the main step.

Recent Gaussian-retirement work, including Ali Romman's PR6545 and PR6551,
motivates the need for a complete two-sided separation. Those constructions
and their credited lineage remain their authors' work. PR6398 and Cinna Davis's
credited native/thin-query lineage supply the Gaussian central-symbol context.
The synthetic maps and capacity proof here use no predecessor word. This package
neither extends nor audits them, and its synthetic obstruction rejects no
published caller. Live claims, open/account PRs, local reservations, main README and
merged object/formula searches and the overlap helper were checked. Sparse
notes, arbitrary historical diffs and unpublished work remain coverage limits.

Dillon / dillona's merged PR4623 supplies a different even-q alphabet
obstruction for exactification of a two-query controller border. It does not
compute this simultaneous direct-summand capacity. Its construction and cost
claims are not replayed or extended here.

The theorem grants all rational field bases. Actual dyadic synthesis, a
source-bound native cut, intermediate chronology, restored outputs, physical
source access, paid jobs, precision, stock, tapes and a complete caller invoice
remain open. All five selected framework assumptions remain. Independent human
and formal proof-kernel review are unclaimed. Selected cold replay, Lean and
Docker are unrun. The selected frontier is unchanged.
The formal ring requires all four phase branches. A representation omitting
some branches needs a criterion for its actual spectrum.

## Open next questions

- Bind one actual cut to the four phase maps, scalar target and allowed charts.
  The absent caller is the blocker to applying this optimistic obstruction.
- Decide when the rational attaining bases admit dyadic Gaussian realizations.
  Begin with kernel/image primitivity; the field proof does not settle it.

Structured relevance, first steps and blockers are in TASK.json. No larger
construction campaign follows from the synthetic example.

## Implementation bounds

The proof has no dimension bound. The implementation accepts square dimensions
1 through 12 over Q or F2, F3, F5 and F7, with at most 128 bits in each input
numerator/denominator. The scientific grids are fixed and smaller. All loops
are bounded by those dimensions, fixed grids or complete groups through order
three. No recursion, dynamic code generation, subprocess or network is used.
Functions are below sixty lines, and explicit exceptions remain active under -O.

Power of Ten rule 3 deviation: CPython allocates managed integers, Fractions
and containers while checking. The one-shot driver retains only one group
of at most 168 binary matrices and their inverses, matrices of order at most
nine in its fixtures, the fixed counters and eight package files capped at
one MB each. Elimination has at most 24 rows and 24 columns. Each group and
profile is released after its bounded loop. A fixed-allocation port would be
needed for embedded or long-running use. Rule 9 deviation: eleven rejecting
controls call only the named local validation operations through a fixed list
of local lambdas. Warning-strict normal and optimized execution and in-memory
syntax checks provide diagnostics; external static analysis is recorded only
if actually run. No shared repository configuration is changed.
