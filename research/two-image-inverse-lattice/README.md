# Exact dyadic input lattice for the compensated two-image inverse

Claim type: scoped all-width proof with finite corroboration. No new kappa.
This contribution was produced by Nick Petalas.

For either prefix G_f in Cinna Davis's [#4998](https://github.com/CrocSwap/integer-mult-bounds/pull/4998),
let D = Z[i,1/2], n = 8^f, and

    a = (4^f + 2^f)/2,   b = (8^f - 4^f)/4.

The new result is the exact inverse-input lattice quotient

    D^n / G_f D^n = (D/(3))^a direct-sum (D/(15))^b.

Consequently an independent input y has dyadic Gaussian inverse output
G_f^-1 y on exactly the fraction 9^(-a-b) * 25^(-b) of every complete
residue period on any fixed dyadic Gaussian grid. At width one the fraction
is 1/164025. The least odd denominator needed for unrestricted exact inputs
is exactly 15 at every positive width. Merely increasing dyadic precision
cannot supply literal exact outputs on every input.

[PROOF.md](PROOF.md) gives the all-width module proof and explicit input
congruences, including the actual phase-repaired frames. The denominator 15
and its sufficiency were already explicit in #4688/#4998. The contribution
here is its necessity, the complete quotient and the exact safe-input lattice
and density. No predecessor program is imported, replayed or audited.

This answers the exact-grid feasibility part of #4998 Open next question 2.
Exact odd-denominator encodings, rounded realizations and inputs deliberately
restricted to the safe lattice remain available changed contracts. No physical
cost or rounding error estimate is supplied. The selected frontier is unchanged.

## Evidence and reproduction

From the repository root, with the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-image-inverse-lattice/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/two-image-inverse-lattice/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-image-inverse-lattice
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-image-inverse-lattice --check-source-history
```

Any CPython 3.12 executable can replace the local interpreter path. The direct
verifier also runs without Git or predecessor files. It writes nothing and
prints a freshly generated result with hashes of every package file.

Expected marker: `PASS_TWO_IMAGE_INVERSE_LATTICE`.

The verifier enumerates cycles at widths 1 through 5 and all 50,865 real
residue vectors on cycle lengths 1, 2 and 4. Their safe counts are 5, 75
and 3375. It separately constructs the literal Gaussian operators and checks
realified ranks modulo 3 and 5 at widths 1 and 2 for both variants. Those
ranks are (8,14) at width one and (84,104) at width two. A separate rational
inverse at width one checks the sharp odd denominator, 128 input-membership
probes and 32 forward-image columns. False unweighted cycle congruences and
single-prime denominator replacements have explicit counterexamples. Finite
checks corroborate the written proof; they do not establish its universal
quantifiers by enumeration.

## Scope and source record

Base: `4c0a359d88f22f05189d51f48387750b801a45d4`, priority revision 7.
The `complex-new-helper-inventory` card is explicitly changed to a numerical
interface side result. Its historical first command fails with
`KeyError: 'complex_profile'` against the newer selected schema; the current
`scripts/research_selected_baseline.py` control passes. That control only checks
source-bound metadata. No frozen supplier, shared script or predecessor file
is changed.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19141364)
reserves this exact lattice question. The initial overlap cache covers 329
open PR bodies and 4,185 Discussion records with complete remote pagination.
Only 147 of 6,760 local note paths were materialized at the targeted scan;
separate main-tree and merged-PR searches cover distinctive object and formula
terms. Sparse notes, arbitrary diffs and unpublished work limit coverage.
[SOURCES.json](SOURCES.json) records historical provenance; the verifier has
no external mathematical inputs.

## Limitations

The exact-output obstruction assumes literal D-valued input and output
coordinates. It does not exclude rational encodings, odd-denominator arithmetic,
rounded outputs or safe-lattice inputs. Complete-period density need not equal
an actual caller's input distribution. Powers of two in a finite precision
format are unpriced. Physical routing, storage, precision, a useful Gaussian
consumer, supplier admission and the complete multiplication theorem remain
unproved. Independent human and formal proof-kernel review are unclaimed.
Lean, Docker and the selected scientific cold replay are unrun.

The verifier uses managed allocation. The largest orbit census has 32,768
addresses; literal matrices have at most 128 real coordinates; rational inversion
uses 16 coordinates. All loops have bounds from those fixed domains, no recursion
or dynamic evaluation is used, and functions stay below 60 lines. Python's
runtime and ordinary library dispatch allocate dynamically; no fixed-memory
runtime guarantee is made. Both registered commands treat warnings as errors
and keep their checks active under optimization.

## Open next questions

1. Can an actual caller produce its independent inverse input directly in
   G_f D^n without paying back the intended benefit? Begin with one named
   producer and the explicit cycle congruences. Independence, input distribution
   and complete preparation/restoration costs are unresolved.
2. Can a rationally encoded or rounded invocation meet a complete native
   precision/storage/routing bill? Begin with one exact odd-denominator output
   representation or one rounded return contract. The lattice theorem supplies
   no numerical error or complete physical cost bound.

## Credit

Cinna Davis #4998 supplies the compensated interface and its exact-grid open
question, following #4991. lee-phys #4688 supplies the original prefix and its
order-four inverse polynomial. Yiyang #4710 supplies the phase repair.
Dugongue #4743 supplies arbitrary-input triangular ports. Jacob Alan Sussman
#4628, eumemic #288 and Swapnil Jain P1/P2 supply the retained small-unit and
certificate lineage. The cyclic presentation and finite-module counting tools
are classical; their application to this exact inverse input lattice is proved
here. Original sources and notices are unchanged. Apache-2.0.
