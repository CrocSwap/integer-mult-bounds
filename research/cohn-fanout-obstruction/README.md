# A unit demand ideal does not guarantee one-insertion fanout

Scoped algebraic proof with exact finite corroboration. This contribution
was produced by Nick Petalas. Apache-2.0.

For every field K, the polynomial demand pair `(1+xy,x²)` over K[x,y]
generates the whole ring, but no two-row dirty-fanout word can realize it
with a single nonzero source insertion. This answers Open next question 1
of lee-phys's [#5139](https://github.com/CrocSwap/integer-mult-bounds/pull/5139).
Its finite-commutative-ring theorem remains a cited predecessor. The new
step is the fanout consequence of Cohn's classical elementary-matrix
obstruction, followed by the matching exact tariff.

With positive stationary coefficient-independent insertion prices mu0,mu1
and row-addition prices c0,c1, the exact optimum is

```text
min(mu0+mu1, 2mu0+2c1, 2mu1+2c0).
```

The contract has exactly two arbitrary dirty output rows and one disjoint
preserved source. Gates are polynomial source insertions and elementary
row additions, priced into their destination row. Both dirt columns must
return, and there are no extra rows or free general linear maps.
[PROOF.md](PROOF.md) gives the full contract and all-word proof, including
the three exact Pareto-minimal count vectors and restoring words. The
statement includes characteristic two and every positive data width.

## Evidence

The standard-library verifier checks exact integer polynomial Bezout,
inverse, affine-endpoint and completion-coset identities. It checks three
attaining words and all ten individual call deletions. It enumerates
60,621 forward/inverse scalar-input pairs over F2,F3,F5,F7 and 625 positive
integer price vectors. Seventeen controls cover omissions, order, invalid
domains, false polynomial division and the changed alphabet that grants
the entire Cohn matrix as a row gate.

Every one of the 87 field-evaluated demand pairs has a checked
one-insertion word. Those finite specializations cannot establish the
polynomial obstruction. The lower bound uses Cohn's **cited** theorem,
not a finite search or a machine verification of that theorem. The
verifier explicitly records that distinction in its generated receipt.
It writes nothing and binds every package source file by SHA256.

## Reproduce

From the repository root, using the CPython 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/cohn-fanout-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/cohn-fanout-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cohn-fanout-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cohn-fanout-obstruction --check-source-history
```

Another CPython 3.12 installation can replace the local interpreter path.
Expected direct marker:

```text
PASS_COHN_FANOUT scalar_pairs=60621 specializations=87 prices=625 controls=17 no_new_kappa
```

Both registered checks have 120-second limits. Normal and optimized checks
remain active because the verifier uses explicit exceptions. Its direct
replay also supports a Git-free package export.

## Scope and provenance

The original `bit-helper-contract` card is explicitly changed to #5139's
algebraic interface question in [TASK.json](TASK.json). This is a local
obstruction, not an admission claim for the original helper-star circuit.
Base is canonical main `ec2780e8aeb1c88acaf5e9e470ef8c68e7fbbb6c`, priority
revision 7. [SOURCES.json](SOURCES.json) pins predecessor proof text as
historical provenance. No predecessor code or verifier is imported or
replayed. Selected source-binding orientation passed; the selected
conditional kappa remains 60403/20000000.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19145584)
followed live PR/Discussion checks, cached card overlap and distinctive
main-tree/merged-PR searches. Cached remote pagination covered 315 open
PRs and 4,395 Discussion records. Local coverage was sparse and incomplete;
these searches cannot exclude unpublished or later work.

## Limits and code constraints

The universal obstruction is the written reduction to Cohn's theorem.
Its non-elementarity premise is a classical cited result, inherited
without an audit or proof-kernel verification. The finite checks
corroborate only their stated identities and domains. The coefficient
ring, elementary gate alphabet and exact two-row contract matter.
Additional workspace, clearing, observations, general free basis maps
and input-dependent coefficients are excluded.

No native coefficient producer, physical routing, restoration tariff,
precision/tape implementation, stock, recursive supplier, new kappa or
complete multiplication theorem is supplied. Lean, Docker and the selected
scientific cold replay are outside scope and were not run. Independent
human and formal proof-kernel review are unclaimed.

The verifier has no recursion, subprocess, network or write path. Its
functions are below 60 lines, matrices have three rows, word length is
at most eight, field sizes are at most seven, and the price grid has
5^4 points. Polynomial operations enforce at most 289 temporary terms
and exponent at most 16 in either variable. The receipt reads at most
12 files of at most 128 KiB each. Python dynamically allocates within
these fixed finite domains, a managed-runtime deviation from static
allocation. Runtime allocator internals are not measured. Warning-strict
normal/optimized replay and in-memory compilation supply the available
diagnostics; no shared build or verifier settings change.

## Credit

Paul M. Cohn supplies the classical non-elementary matrix. Its exact
primary-source location and characteristic scope are in
[REFERENCES.md](REFERENCES.md). No novelty is claimed for that theorem.
lee-phys #5139 supplies the finite-commutative-ring criterion and the
explicit nonsemilocal elementary-orbit question, building on #5089.
Krzysztof Wójt #5045 supplies the source-count classification,
directional return lemma and attaining repeated-insertion templates.
Nick Petalas #4916 supplies the earlier ring-valued contract. Retain the
Ross Richardson, Cinna Davis, Anthony, Oscar Fennell, Tekalign and other
predecessor credit recorded in those packages. Their files are unchanged.

## Open next questions

Can one extra restored dirty row remove this polynomial one-insertion
obstruction, and at what complete price? Start with a stabilized Cohn
matrix, retaining all three independent dirt columns and all paid row
directions. This would separate two-row elementary reachability from
stabilized reachability. A fully charged restoring word and matching
tariff remain unproved here. No further construction is claimed.
