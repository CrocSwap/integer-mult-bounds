# Exact affine centre access and its Haar-tree limit

This package gives exact access to one largest affine part of a correlated
phase sector. A reversible signed Haar code implements
`(x,y) -> (x,y+Pi x)` on two arbitrary physical fields. It retains every
input detail and restores the source. A combined projected quarter turn
uses one encode and one decode per field. Both constructions add no
complex native child and no owner family.

The package also proves a limit for this method. A literal affine Haar
tree for the complete all-odd sector needs `Omega(lambda V)` forward
split work at fixed native dimension. This statement permits different
affine tests and coordinate charts on different branches. It does not
cover general linear circuits, direct non-affine blocks, cancellation
between overlapping codes, or a query that does not form the projector.

There is no change to the complete kappa calculation. The local layer
does not supply the remaining controller, a complete finite invoice,
or recursive supplier admission.

## Results and assumptions

Let a Fourier address have `n>=2` rows and positive tensor width `lambda`.
Every odd row sum must have the same weight modulo four. The largest
affine part has dimension

```text
n floor(lambda/2) + (lambda mod 2).
```

Its codimension is `k=n ceil(lambda/2)-(lambda mod 2)`. The standard
pair code attains this bound at every width. The rigidity classification
requires `n>=3`. The fixed-residue product cover and its exact extension
counts have their own stated domains. Read the corrections with the
original proofs in [PROOF.md](PROOF.md).

Under the pinned fixed-tape stream assumptions, the local layer costs

```text
O(V ((e log p)^tau + 1)),  e=n lambda,  0<tau<1.
```

Here `n` is fixed. `V` includes complete guarded coefficient records and
the protected row, compact, spectator, and polynomial fields. The bound
includes the paid address maps. It is not an explicit finite constant.

The equal-frame shear needs `k` extra fractional bits and one extra
magnitude bit. The odd-width frame-matched shear needs `k+1` fractional
bits and two magnitude bits. The combined quarter turn needs `k`
fractional bits and two magnitude bits at equal frames; its direct
odd-width frame-matched version needs `k+1` fractional bits. These are
exact-grid prefix bounds for the stated words.

An internal recursive use must prove the dependency-path envelope in
the stream amendment. Zero added children alone does not prove it.
Completed native frames must meet the stated operator contract. Extra
outer address permutations need a separate binding. Actual owner-cut
binding is outside this package's new-result claim.

## Reproduction

Use Python 3.10 or later. Only the standard library is required.
No Git checkout, network, source archive, NumPy, or SymPy is required.
From this directory, run:

```sh
python3 -I -B verify.py
```

The last line is:

```text
PASS_AFFINE_CENTRE_ACCESS
```

The eight checks run one at a time. Seven fresh receipts must equal the
original frozen receipts byte for byte. The density check runs the
unchanged general quotient, Gauss-sum, walk, and distribution functions
from the independent reviewer. It compares their full results with the
frozen review. It does not replay the unrelated actual 17-axis route
maximality check. The one-pass-turn check uses producer primitives; its
separate review is a proof review. These checks are not human or
proof-kernel certification.

To save the fresh receipts, choose a directory that does not exist:

```sh
python3 -I -B verify.py --output /tmp/affine-centre-access-replay
```

For a source and porting check only:

```sh
python3 -I -B verify.py --check-only
```

This package does not run a complete native supplier, an actual owner
schedule, a fixed-tape machine implementation, or recursive admission.
The finite checks support the general written proofs; they do not
replace the proofs' quantifiers.

## Evidence and source boundaries

[SOURCES.json](SOURCES.json) records the exact source bytes.
[PORTABILITY.json](PORTABILITY.json) lists each path and output change
to the replay copies. The verifier checks those changes exactly and
checks that every non-main function and class has the same syntax tree
as its frozen source. The original proof, checker, and review files are
retained without edits under `evidence/`. The copied stream sources are
from commit `bce54fb3f895cbe5cd4c0eb477c3afeed100190f`.

The publication refresh on 22 October 2026 used canonical main
`b58ad9ef4d4e861b0eaa5dba41742bdc072dca51`. Its
[selected record](https://github.com/CrocSwap/integer-mult-bounds/blob/b58ad9ef4d4e861b0eaa5dba41742bdc072dca51/certificates/selected-result.json)
identifies [PR #4470](https://github.com/CrocSwap/integer-mult-bounds/pull/4470)
with conditional kappa `0.00302015`. The historical source pin above is
unchanged. Transfer of this local interface to the selected construction
has not been proved. This package does not update the selected record.

Some frozen source documents discuss additional route, CSS, Bell, or
owner results. They retain their historical text and references. Those
sections are background, not submitted claims or replay obligations of
this package. [PROOF.md](PROOF.md) gives the precise claim-to-proof map.
The package excludes the actual-owner binding files and their claim.

The all-odd sector is a sufficient phase sector. Its limiting density
is `2^-((n-1)(n+2)/2)`. At `n=73` this is `2^-2700`; the exact density
is within one percent of that limit from width 152. This very small
constant does not give a useful finite-budget lower bound. The package
does not claim that the sector is maximal for an actual supplier.

The source licenses and notices are retained. See [NOTICE.md](NOTICE.md).
Substantial OpenAI Codex assistance was used for research, code, proof
review, and packaging. No independent human review is claimed.

## Open next questions

These are the remaining obligations for a later use of the result.
The publication wrap does not start that work.

- **Bind one actual caller cut.** The local layer can be useful only if
  the caller supplies its completed-frame and storage contract. A first
  step is to name two fields in one pinned caller and verify their full
  frame operators, outer address maps, and arbitrary baseline behavior.
  The current package has no such binding to PR #4470. Internal use
  also needs a new dependency-path envelope and a complete paid invoice.
- **Test a different full-sector access method.** The Haar-tree limit
  rules out the stated sublinear scan bound within its literal grammar.
  A first step for an alternative is to specify one exact physical
  query operator and its arbitrary-input restoration contract. A useful
  proposal must price non-affine work, overlap cancellation, or productive
  children explicitly. The present package supplies none of those
  alternative implementations.
