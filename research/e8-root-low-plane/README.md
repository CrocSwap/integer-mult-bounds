# Exact basis tariff 78 for the first root-low E8 quotient

Scoped proof with an exact finite certificate, produced by Nick Petalas.
No new kappa or selected-frontier change.

For the explicit adjacent roots v=(0,1), a=(0,2) in the A8 E8 model, let
d be E_a restricted to the nonorthogonal neighbors H_v. It has 29 nonzero
entries and creates the mixed weight-seven word E_a-d. The natural
two-dimensional correction space D=span(delta_a,d) gives a ten-dimensional
reader space S=C+D with exact minimum basis profile

```
1, 7, 7, 9, 9, 9, 9, 9, 9, 9       sum = 78.
```

[PROOF.md](PROOF.md) proves that every basis has sorted weights at least
this profile, over every characteristic-zero field. The exact minimum for
every nondecreasing tariff F is F(1)+2F(7)+7F(9). All deficient vectors
lie in three specified planes inside one three-dimensional space. The
new mixed low direction therefore fails to make the complete reader
basis cheap. Under conorholds' PR4052 singleton-encoder hypotheses, its
strict-floor corollary gives the new conditional COPY lower bound 77
for this actual reader space. No exact COPY optimum is claimed.

The source question is [PR4052](https://github.com/CrocSwap/integer-mult-bounds/pull/4052),
Open next question 2, at `7541aca683b1c40881a478b9d0bb2b63291949f9`.
Its thresholds and COPY theorem are cited, not audited. The card changes
from a complete signed-moment experiment to this scoped negative result
on one named algebraic decoder candidate. It does not meet the physical
supplier acceptance gate. [TASK.json](TASK.json) retains the original card.

## Reproduction and evidence

From the repository root, CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/e8-root-low-plane/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/e8-root-low-plane/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/e8-root-low-plane
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/e8-root-low-plane --check-source-history
```

Other hosts can substitute their CPython 3.12 path. Direct checks are
read-only and print `PASS_E8_ROOT_LOW_PLANE` in JSON bound to all six
package hashes. An optional `--receipt PATH` creates a new receipt and
refuses to overwrite an existing file. No receipt is hand-written or
committed. No predecessor executable is imported or run.

The new certificate covers all 511 nonzero characters, with rational
kernel construction and separate integer/modulo-101 rank certificates.
It checks the seven nonempty support unions, the ten-vector attaining
basis, and seven controls. The controls reject incomplete, incorrect and
oversized kernels and distinguish the deficient locus, its span, the
unpunctured correction and the false bill 77. The finite table plus the
written scalar-extension and filtration arguments proves the quantified
claim; finite coefficient sampling alone would not do so.

## Limitations

The main result concerns exactly D=span(delta_a,E_a restricted to H_v)
at the displayed root pair. Arbitrary 29-coordinate spaces, other fields,
masked targets and shared or dynamic delivery are outside scope. The
conditional COPY consequence retains PR4052's normalization and singleton
classification premises. The selected #6030 record and all five framework
assumptions remain unchanged. No selected cold replay, Lean, Docker,
independent human or formal proof-kernel review is claimed.

The verifier has no recursion, dynamic code execution or external
dependencies. All matrix sizes are bounded by 120 rows and ten columns;
the complete character loop has 511 iterations. Functions are below sixty
lines. Python's managed allocation is a Power-of-Ten deviation, bounded
here by the fixed matrix and certificate sizes. Warning-strict normal and
optimized commands are registered. Ruff, mypy, Pyright and Pylint are
unavailable in the local PATH and interpreter environment; stronger static
analysis remains unclaimed.

## Open next questions

- Does a different correction space containing one 29-neighbor root-low
  word admit a reader basis at or below 72? Start by adding one explicitly
  independent correction to D and recomputing its character-kernel
  filtration. The present result shows that this particular D is too costly;
  it supplies no uniform answer for larger spaces.
- What is the exact coupled COPY optimum with actual reader space S?
  Start from the proved lower bound 77 and the source's exceptional-ray
  identities. An exact factorization attaining that bill or a stronger
  actual-basis argument is missing. Physical costs would still be separate.

## Credit

New quotient classification, basis tariff and verifier produced by Nick
Petalas. conorholds supplied PR4052's 29-neighbor opening, relative
thresholds and actual-basis coupling, building on PR3755's singleton and
one-coset results and PR3166's weighted root swaps. Retain DreamingOfClouds'
decoder programme and prefix relaxation, adamgall's concave accounting,
the original E8 root/label geometry and all predecessor notices. Linear
algebra, annihilator tests and rank filtrations are classical. No global
literature-priority claim is made. New files are Apache-2.0; predecessor
files and credit are unchanged. [SOURCES.json](SOURCES.json) pins the cited
proofs and model as historical provenance, not executable dependencies.
