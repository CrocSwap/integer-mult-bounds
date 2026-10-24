# Exact right-vector cost over local algebras at every role count

Scoped algebraic proof with bounded finite corroboration. No new kappa.

Let K be a central field in an associative local K-algebra R. Its nonunits
form a proper two-sided ideal. For every n>=1 and every invertible target
M in M_n(R), use paid factors I+u y^T with u in R^n, y in K^n, and arbitrary
free GL_n(K) maps anywhere. Then

```text
cost(M) = delta(M) = rank_K(pi M|_{K^n}) <= n,
delta(M) = min_{T in GL_n(K)} dim_K ((MT-I)K^n),
pi : R^n -> (R/K)^n.
```

The residue division algebra may be larger than K and noncommutative.
Neither finite dimension nor nilpotence of the radical is required.
[PROOF.md](PROOF.md) constructs an attaining word with no auxiliary roles.
It first makes a maximal scalar subspace fixed, chooses unit pivots in
the complementary block by free row permutations, and replaces one column
per paid factor. The column lower bound is cited from #4243/#4099.

This settles the invertible arbitrary-role local case of #4265's open
question, extending Theorem D of #4276 beyond two roles. The finite binary
three-role agreement in #4265 is a credited predecessor, not a new census
claimed here. Products of local algebras and general semilocal algebras
remain outside this arbitrary-role theorem.

## Finite evidence

The standard-library verifier imports no predecessor code. It constructs
and checks literal words for 2,380 distinct sampled targets on three,
four and five roles over these algebras:

- F2[e]/e^2;
- F2[x,y]/(x,y)^2;
- F3[e]/e^3;
- F4, with base field F2;
- F4[e;Frobenius]/e^2, with base field F2 and e*a=a^2*e.

The last algebra is noncommutative, with residue F4. Complete multiplication
tables pass associativity, distributivity, central-field and nonunit-ideal
checks. For each algebra and role count, the sampler generates 32 candidates
at each nominal cost from zero through n, then deduplicates their actual
matrices. It uses triangular cores with non-scalar unit diagonals and two
independent base-field charts. These are bounded samples, not complete
target censuses. The generated receipt lists each count and cost histogram.

Every word passes literal matrix multiplication and a separate execution
on every base-field basis input of R^n, totaling 27,616 basis-data checks
on the sampled targets. A calibration computes delta directly over all
168 GL3(F2) charts for each of 16 binary dual-number targets, totaling
2,688 chart evaluations. The first working example
`[[1,e,0],[e,1,e],[0,e,1]]` has cost two and a non-coordinate fixed line.

Eight controls detect reversed factor order, a dropped factor, a changed
coefficient, missing free endpoints, a singular input, a required unit-pivot
permutation, discarded nilpotents and charging a free target. All checks
remain active with Python optimization. The verifier writes nothing and
prints a generated receipt binding its results to all six package files.

## Reproduce

From the repository root, with the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-local-all-roles/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-local-all-roles/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-local-all-roles
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-local-all-roles --check-source-history
```

Any CPython 3.12 installation can replace the local path. The direct verifier
ends with `PASS_RIGHT_VECTOR_LOCAL_ALL_ROLES targets=2380 controls=8 no_new_kappa`.
Both registered commands have 120-second limits. Exact base, Git blobs and
SHA256 pins are in [SOURCES.json](SOURCES.json). The selected record and
catalogue are historical provenance; the two predecessor files are pinned
live inputs. Full Git history resolves provenance. Direct replay also
works in a Git-free package export.

## Limitations and engineering notes

The universal result is the written scoped proof. Finite corroboration uses
base fields F2 and F3 and the listed samples only. Invertibility and locality
are essential to the stated construction. Singular targets, products of
local rings and nonlocal algebras are unclassified here. Native coefficient
preparation, frames, routing, restoration, precision, stock and a complete
recursive invoice remain unknown. No native supplier, selected-frontier
change or complete multiplication theorem is claimed. Independent human
and formal proof-kernel review are unclaimed. Lean, Docker and the selected
operator replay were not run or required by this isolated package.

The verifier has no recursion or external subprocesses. Every matrix has at
most five roles, every ring has at most 27 elements and four base-field
coordinates, every sampler has at most 192 candidates, and every function
fits within 60 lines. Explicit checks remain enabled under optimization.
Python allocates dynamically, so static allocation is not claimed. This
managed-runtime deviation is bounded by those fixed domains, a maximum of
192 stored target matrices per sampler and 168 stored calibration charts.
The ring methods use ordinary bounded dispatch to the five named algebras.
Warning-strict normal/optimized replay and in-memory compilation supply the
available Python diagnostics; no repository-wide configuration is changed.

The optional selected-baseline orientation stopped at the omitted sparse
input `research/fresh-helper-thinned/PROOF.md`. No baseline pass is claimed.
The connector card's 945-pairing positive control passed. [TASK.json](TASK.json)
explicitly records the change to this algebraic side question.

## Open next questions

1. For invertible targets with n>=3 over a product of two local algebras,
   which simultaneous pivot flags characterize cost equal to delta?
   Start with one three-role pair over F2 x F2. A common scalar chart and
   pivot order need not exist; the current proof chooses them in one local
   algebra. This would locate the first obstruction to a product extension.
2. Can one literal native producer and consumer realize a column replacement
   at a favorable complete cost? First specify algebra-valued coefficient
   preparation, access, frame conversion and restoration. Those costs are
   unknown, so this result does not initiate a supplier construction campaign.

## Credit

This contribution was produced by Nick Petalas. Nick Petalas #4265 supplies
the local-algebra question and finite three-role precedent; #4276 supplies
the exact two-role local theorem; #4243 supplies the free-map normal form
and column bound. The right-vector alphabet and original column expansion
are Wentao Li #4099 following #2513. ToikY #4334 and Nick Petalas #4601/#4749
supply the distinct two-role product and semilocal comparisons. Gaussian
elimination, basis extension, Schur complements and local-ring unit lifting
are classical. The new contribution is their exact arbitrary-role local
restricted-alphabet consequence. Predecessor files and credit are unchanged.
Apache-2.0.
