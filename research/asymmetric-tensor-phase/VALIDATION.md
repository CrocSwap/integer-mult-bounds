# Validation record

Environment: Linux, CPython 3.12.14, standard library only. Exact base:
`a7638a4ce2a29947457ae8d6bf8cd70a234dfeac`. No shared source files changed.

## Executed scientific checks

```sh
python3 -B scripts/research_package.py --package research/asymmetric-tensor-phase --check-only
python3 -B scripts/research_package.py --package research/asymmetric-tensor-phase
```

Both pass. The second executes all six normal/optimized commands declared
in VERIFY.json and ends with `PASS_REGISTERED_RESEARCH_PACKAGE`.
The primary, independent and mutation checkers also passed directly:

```sh
python3 -I -W error -B research/asymmetric-tensor-phase/verify.py
python3 -I -O -W error -B research/asymmetric-tensor-phase/verify.py
python3 -I -W error -B research/asymmetric-tensor-phase/independent.py
python3 -I -O -W error -B research/asymmetric-tensor-phase/independent.py
python3 -I -W error -B research/asymmetric-tensor-phase/mutation_check.py
python3 -I -O -W error -B research/asymmetric-tensor-phase/mutation_check.py
```

Primary coverage: 10,201 angular pairs, 101 exact angular threshold points,
160 rational phases, 16 dense matrix pairs (12 noncommuting), 1,344 tensor
Gram entries, 33 rational squared-budget jump points, 64 one-sided tests,
and 15 invalid-input/false-bound/domain controls. Two unchanged predecessor
files pass SHA256 and Git blob authentication. RESULT.json was generated
by `verify.py --output NEW_PATH`; later normal checks require exact receipt
agreement, including package hashes. A stale receipt after a README
formatting edit was correctly rejected and regenerated before final replay.

Independent polynomial oracle: 289 quarter-grid budget pairs, 97 exact
jump/one-sided cases, and 23 adversarial endpoint/common-root cases pass.
The latter include rational gaps of `2^-65`, `2^-100`, and `2^-160`.
The quarter-grid enumeration digest is:
`624aeedf67d57a92a2ec8df1295d65b9460b6dcd14d35342093aef465f8e6837`.
Four wrong endpoint controls reject. This oracle uses Sturm root counts
and polynomial gcds; it does not use the angular classification or rational
branch predicate when computing the maximum.

Actual corruption checks: five changed envelope bodies, one changed oracle
isolation condition, two changed predecessor files, and one altered receipt
reject in both Python modes.
Temporary copies are discarded; canonical sources are unchanged.

## Mathematical review

The lead independently reconstructed the four arc intersections and the
sign-safe squared-budget guard. Review caught and corrected an initially
incorrect ordinary-power counterexample in the scope discussion; the final
nonunitary example uses literal scalar tensor powers. Review also prompted
the full rational jump-curve parametrization and explicit count of the
noncommuting matrix fixtures.

A separate adversarial review found a genuine bug in the first polynomial
oracle candidate: at squared budgets `(s,t)=(0,4-2^-100)`, it returned a
near-four enclosure instead of the exact zero optimum. Stripping the
endpoint root four allowed an interior root bracket to retain endpoint
four; a gcd root count then confused that stripped root with the represented
root. The final isolator retains the original square-free polynomial and
requires both interior bracket endpoints to be nonroots of it. The original
counterexample now returns `(0,0)` exactly. The oracle mutation reinstates
the faulty condition and must reproduce the wrong result. The separate
reviewer checked the repaired invariant and 16 independent exact-answer
endpoint/common-root fixtures. All six registered commands were rerun after
the correction. The theorem and envelope were unaffected; the earlier
candidate was not accepted for publication.

These are AI-assisted mathematical checks, not independent human or formal
proof-kernel acceptance.

## Publication checks

Committed-byte/mode validation passed for all 13 package/input files. The
official exporter and `check --check-inputs` both passed, including the two
declared predecessor inputs. All six direct checker commands then passed
from the exported Git-free tree with empty PATH and read-only file/directory
modes; all 14 exported files (including the export manifest) retained their
bytes and modes. The export replay used the same CPython 3.12.14 interpreter.

```sh
python3 -B scripts/check_research_commit.py --package research/asymmetric-tensor-phase --check-modes
python3 -B scripts/export_research_package.py export --package research/asymmetric-tensor-phase --output /tmp/asymmetric-phase.tar.gz
python3 -B scripts/export_research_package.py check --check-inputs /tmp/asymmetric-phase.tar.gz
```

Full-history source preflight is intentionally unrun in this shallow partial checkout;
no repository-wide fetch is needed for this additive package. Exact base
and input blobs are authenticated by the metadata check. The declared
predecessor proof/README blobs also match their originating #5916 head
`f0d87ad28e09055fd44e5a93437be5eeba284491` in targeted GitHub reads.

No selected cold replay, native/physical caller, Lean, Docker, hosted CI,
full-history preflight, or complete multiplication theorem is claimed.
