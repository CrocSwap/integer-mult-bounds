# Exact phase-preserving width for a hyperbolic pair and one radical

For the three-dimensional binary form `H direct sum 0`, prescribe

    q(xa+yb+tz) = xy + alpha*x + beta*y + gamma*t.

An injective linear realization must preserve its Gram form and satisfy
`wt(f(v)) = 2*q(v) modulo 4` on every vector. Its exact minimum coordinate
width is:

| Radical phase gamma | Hyperbolic basis phases alpha,beta | Minimum |
|---|---|---:|
| 0 | 1,1 | 4 |
| 0 | 0,0 or 1,0 or 0,1 | 6 |
| 1 | any | 5 |

Claim type: scoped written proof with exhaustive finite corroboration and
explicit minimum embeddings. The prescribed phases can therefore cost one or
two coordinates beyond the cited Gram-only minimum four. This settles the
first working example of Open next question 1 in
[PR6456](https://github.com/CrocSwap/integer-mult-bounds/pull/6456), rather than
auditing that package. [PROOF.md](PROOF.md) proves the lower bounds and lists
attaining maps for all eight phase choices.

There is no new kappa, physical supplier, selected-frontier change or complete
multiplication theorem. This is a phase-sensitive label interface result.
Physical realization and a complete signed bill remain missing.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/quadratic-hyperbolic-radical-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/quadratic-hyperbolic-radical-width/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/quadratic-hyperbolic-radical-width
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/quadratic-hyperbolic-radical-width --check-source-history
```

Other CPython 3.12 executables can replace the local interpreter path. The
standalone verifier is read-only and Git-free. It emits a generated JSON
receipt bound to all six package-file hashes and the marker
`PASS_QUADRATIC_HYPERBOLIC_RADICAL_WIDTH`.

The finite domain is every width from zero through six and all eight refinements.
The literal row enumeration visits 37,450 even-vector triples, including zero
and dependent triples. A second enumeration visits all 3,003 column multisets
and weights them by their exact multinomial multiplicities. Their complete
phase-by-width embedding counts agree. There are 3,744 accepted ordered
embeddings across these widths. The first positive width for each phase equals
the proved minimum. Neither search prunes on the claimed answer.

All eight displayed witnesses pass every vector phase and every ordered vector
pairing. Twelve controls reject lost phases, collapsed radicals, wrong Gram
data, odd images and malformed inputs. Explicit checks stay active under
optimized Python. Receipts are computed, never handwritten.

The selected baseline binding command passed as source/metadata orientation.
No predecessor mathematical verifier, selected cold replay, native/caller
program, Lean or Docker was run. Independent human and formal proof-kernel
review are unclaimed. Hosted CI is recorded separately in the contribution PR.

## Scope and source credit

This contribution was produced by Nick Petalas. Apache-2.0.
Credit Nick Petalas's PR6456 for the Gram-only width problem and the explicit
phase-preserving first example; Maximus Putnam / Maximooch's PR831 for the
alternating trace and phase-interface motivation, with the retained Joel
Pulikkan / GamingPuzzled and endpoint-normal-form lineage; and THU New Media
Research Center / thu-nmrc's PR5464 for the related degenerate embedding
background retained there. These are cited premises and context. No predecessor
executable is imported. Binary polarization and even-weight code arguments
are classical; no literature-priority claim is made.

[SOURCES.json](SOURCES.json) pins the exact predecessor README/proof, catalogue
and selected-record provenance at canonical base
`e54523517d0f03e58352e647c403a5af3e525a57`. The historical card is
`complex-rank-shape-decoder`, priority revision 8. [TASK.json](TASK.json)
records the change from complete decoder accounting to this geometric
subproblem. The selected record remains #7000 with its five assumptions.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19571816)
has the same mathematical scope.

Live claims, account PRs, open/merged searches and canonical main README
searches were checked. The overlap helper reported incomplete sparse local
coverage and no usable cached Discussion snapshot; live GraphQL reads and
direct main searches supplemented it. Arbitrary historical diffs, unmaterialized
nested notes and unpublished work remain outside that coverage.

## Verification bounds

Every verifier function is shorter than sixty physical lines. There is no
recursion, subprocess, network, dynamic code generation or artifact write.
Widths are fixed at zero through six; row points number at most 32, column
tuples contain at most six entries, spans contain at most eight vectors, and
the receipt reads exactly six files of at most 128 KiB each. All loops have
finite bounds from those domains. Functions have direct calls and scoped local
state. Explicit argument and invariant checks remain enabled with `-O`.

Power-of-ten rule 3 has a managed-runtime deviation: CPython allocates integers,
sets, lists and JSON objects during verification. The fixed domains above bound
live resources; fixed allocation is not claimed. Warning-strict normal and
optimized execution and source AST inspection are the available diagnostics.
No repository-wide static-analysis configuration change is included.

## Open next questions

1. Determine the exact phase-preserving width for two hyperbolic blocks and one
   radical direction. Separate the radical phase and the quadratic type of the
   nonsingular part first. Higher-dimensional embedding bounds are missing.
2. Instantiate one minimum embedding in an actual source/read interface with
   specified phases and chronological frames. Native delivery, dirty restoration,
   owner allocation, precision and a complete signed bill are still blockers.

Structured first steps and blockers are in TASK.json. No follow-on scope is
reserved. Arbitrary binary forms and larger radicals are outside this result.
