# Exact rank-one repair of a weighted ordinary wrapper

This scoped written proof was produced by Nick Petalas. For every field and
invertible first map P, the exact minimum number of inserted invertible
rank-one linear corrections needed for ordinary interchange is

```text
rank(P^2-I).
```

The second map Q may be chosen freely. Corrections may be inserted at any cut
of the six-instruction word and may use arbitrary finite dirty workspace that
must be restored. An attaining construction chooses Q=P, uses no workspace,
and changes the middle addition from D += H to D += P^-2 H through a rank
factorization of P^-2-I. [PROOF.md](PROOF.md) gives the full contract and proof.

Jerry Chen / CubeJerry's [PR2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950)
already proves the optimum error rank of the unchanged word. The new step
constructs exact repairs and proves their minimum count under the changed
instruction alphabet, including arbitrary cut placements and dirty workspace.
The predecessor's census is not replayed. A correction is one abstract
rank-one linear map. Its native, scalar and physical cost is not one by claim.
No new kappa, supplier admission or selected-frontier change is claimed.

## Reproduce

From the repository root, using the standard library and CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/wrapper-rank-one-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/wrapper-rank-one-repair/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/wrapper-rank-one-repair
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/wrapper-rank-one-repair --check-source-history
```

Other machines may substitute their CPython 3.12 path. The direct verifier
prints a generated JSON receipt with status PASS_WRAPPER_RANK_ONE_REPAIR and
SHA256 hashes of all six package files. It writes nothing and imports no
predecessor executable. It also works in a six-file Git-free export.

## Finite evidence

The verifier executes the literal six operations and inserted corrections on
all basis inputs, comparing the complete linear map with interchange. It
checks every invertible first map in GL1 and GL2 over F2, F3 and F5, a total
of 541 maps. All constructions pass. Removing each individual correction
leaves a nonzero rank-one error in all 786 finite-field omission checks.
Two exact rational fixtures also pass, with correction counts two and one.

For P=((0,1),(1,1)) over F2, the defect rank is two. A separate exhaustive
shorter-repair check retains one arbitrary dirty helper and tests all six
second maps, all 465 distinct invertible rank-one perturbations on the full
five-dimensional state, and all seven cuts. All 19,536 zero- or one-correction
circuits fail the full required endpoint. The attaining two-correction word
is included in the construction checks. This is a complete finite domain,
not a claim of exhaustive search for arbitrary fields or workspace sizes.

Five further controls reject the wrong correction sign, the wrong cut, a
mismatched second map, a singular first map and a nonsquare first map. Checks
use explicit exceptions and remain active under optimized Python. The written
proof supplies the universal quantifiers; finite checks corroborate them.

## Scope, provenance and credit

Scientific base is canonical main 7c49fe32c55de02c2c873655c804b16e4c3fef0a,
priority revision 8, selected PR6030. [Advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19362351).
TASK.json records the changed card scope and bounded overlap coverage.
SOURCES.json authenticates the original card, selected record and PR2950 proof
as historical provenance. No predecessor source is a live executable input.

Credit Jerry Chen / CubeJerry for PR2950's fixed-word criterion, error-rank
bound and normalization seam; Nick Petalas for PR2808 and PR2786; David Arias
for PR2753; Jose Manuel / jmbarrancoml for PR2697 and PR2899; and the retained
caller lineage. Rank factorization and rank subadditivity are classical.
Nick Petalas's older PR4850 minimizes output-coordinate scales, and PR5228
classifies second maps in the unchanged word. The open PR6406 counts regular
J3 second maps. Its model and follow-up questions are not extended here; no
extra computation compares its numbers.

This is an algebraic side result on the joint-query-controller card. Actual
functional access, coefficient preparation, broadcast, routing, frames,
physical restoration, stock, precision, compiler, complete supplier and outer
costs remain unpriced. The selected cold replay, predecessor scientific suite,
Lean and Docker were not run. Independent human and formal proof-kernel review
are unclaimed. Apache-2.0. No general literature-priority claim is made.

## Open next questions

- Pin one actual weighted producer and price this correction schedule against
  a fully charged alternative normalization. The missing evidence is a native
  and physical implementation, including every restoration and movement cost.
- Fix an actual caller's accessible row and column dictionary and determine
  the minimum restricted factorization length of P^-2-I. The unrestricted
  rank tariff does not settle that problem. First fix the dictionary and cut.

Structured first steps and blockers are in TASK.json. These are follow-on
questions; no broader construction or second result is included here.

## Verifier constraints

The single verifier has no recursion, subprocesses, network access, dynamic
code generation or external mathematical runtime inputs. Matrices have at
most five rows and ten augmented columns. Each constructor enumeration has
at most 625 candidates. The shorter-repair domain has 31 nonzero vectors,
465 distinct correction matrices, six second maps and seven cuts. Functions
are shorter than 60 physical lines. All failures propagate; no assertions
can disappear under optimization.

Power-of-ten rule 3 deviation: CPython allocates managed tuples, integers and
Fractions during verification. Fixed domains bound live matrices, the largest
stored correction family has 465 matrices of 25 binary entries, and six file
reads are bounded at one MiB each. This is a one-shot verifier rather than an
embedded fixed-allocation implementation. Python has no compiler warning
mode; both registered commands use -W error and explicit runtime guards.
