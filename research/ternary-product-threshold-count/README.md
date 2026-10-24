# Exact ternary right-vector threshold count

Scoped counting proof with an exhaustive finite certificate. No new kappa.

For two roles over R=F3^4, exactly **9,216 of 5,308,416** invertible targets
need three paid factors I+u y^T with y over F3 and arbitrary common free
GL2(F3) maps anywhere. The exact fraction is **1/576**.

Their unordered projective actions are exactly the left cosets of the
regular cyclic and Klein four subgroups of S4. The eighteen cyclic cosets
give 6,912 ordered matrix targets; the six Klein cosets give 2,304.
[PROOF.md](PROOF.md) derives the classification and count. This quantifies
the first ternary obstruction population left undetermined by ToikY's
[#4334](https://github.com/CrocSwap/integer-mult-bounds/pull/4334).
Its common-unit-pivot criterion and three-factor upper bound are cited
inputs, not audit deliverables. The projective/Latin-square facts are
classical; the claimed contribution is their exact cost consequence.

## Evidence and reproduction

The standard-library verifier uses two counting routes. It enumerates all
10,626 four-element subsets of S4 and proves the 24 covering supports are
exactly the classified cosets. Separately, it constructs all 48 invertible
ternary matrices and enumerates all 48^4 ordered matrix tuples using their
sixteen literal bilinear pivot values. The second route does not call the
projective action or subgroup classifier. Its 9,216 obstructed tuples agree
with 24*24*16 from the support count. No tuple is quotiented out by the free
maps or by scalar multiplication.

It also checks all 2,304 projective multiplication pairs, both scalar lifts
of every action, 96 repeated-component controls, singular/wrong-size domain
rejections and a partial-input coverage control. Explicit exceptions remain
active under optimization. Each run emits a generated SHA256 receipt for
all six package files. It writes only stdout; no receipt is handwritten.

From the repository root, with CPython 3.12 and no third-party packages:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B -W error research/ternary-product-threshold-count/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -B -W error research/ternary-product-threshold-count/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/ternary-product-threshold-count
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/ternary-product-threshold-count --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path.
Expected marker is `PASS_TERNARY_PRODUCT_THRESHOLD_COUNT targets=5308416 cost3=9216 probability=1/576 no_new_kappa`.
Normal and optimized runs are separately registered with 120-second limits.
SOURCES.json pins the cited predecessor statements and historical task
context at main 624de9dc66858af0945e5f8a0942488d62280d43. The standalone
verifier imports no predecessor code and needs no Git or network access.

The connector-alphabet-change card is explicitly changed to an algebraic
counting side question in TASK.json. Its 945-pairing positive control passes.
This does not supply the changed native operation or favorable complete
budget sought by the original card.

## Limits and code inspection

The exact-cost interpretation uses the cited field-product theorem. The
new proof and enumeration cover F3, two roles, four ordered components and
invertible endpoints. Other fields, lengths, singular endpoints and local
lifts are outside scope. Native coefficient preparation, routing, control,
restoration, precision, stock and the complete supplier invoice remain
unknown. No supplier admission, selected-frontier update or complete
multiplication theorem follows. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and selected operator replay are unrun
and unnecessary for this isolated counting result.

The verifier has no recursion, process launch, network call or CLI input.
All domains are fixed: 81 candidate matrices, 48 invertible matrices, 24
permutations, 10,626 candidate supports, and 48^4 matrix tuples. The largest
census streams one tuple at a time; it stores no target table. All function
bodies are below 60 lines. Receipt reads are bounded to six files of at most
1 MiB each. Warning-strict ordinary and optimized checks provide recurring
runtime diagnostics; no separate static analyzer is claimed.

Power of Ten rule 3 has a managed-runtime deviation at verify.py. CPython
allocates integers, tuples and finite sets during enumeration. Fixed input
domains bound retained state to 24 supports, four subgroups and their 24
cosets, 48 matrices and masks, and at most 24 action entries. The two
10,626-subset scans are streamed. The registered checks exercise the full
capacity. If these domains grow, a fixed-buffer or explicitly budgeted
implementation is required before expanding the census. Python has no raw
pointer or preprocessing operations; data access is shallow and direct.

## Open next questions

1. Count cost-three invertible targets over F3^k for k>4. Begin with a
   finite inclusion-exclusion over missing entries in the four-by-four
   permutation coverage board. This would measure how quickly the common
   chart obstruction becomes typical; repeated projective components mean
   the threshold coset classification alone does not count longer tuples.
2. Count the first obstruction population over F4^5. Begin with the
   sharply transitive five-element subsets of PGL2(F4). Its image is a
   proper subgroup of S5, so unrestricted order-five Latin-square counts
   cannot be substituted.
3. Specify a literal native producer/consumer for this common-right-vector
   alphabet and price coefficient preparation, access, restoration and
   precision before using the count in a supplier. Those costs are unknown.

TASK.json gives relevance, first steps and blockers for these questions.
No follow-on census is included in this contribution.

## Credit

This contribution was produced by Nick Petalas. ToikY #4334 supplies the
field-product criterion, upper bound and sharp threshold. Nick Petalas
#4276/#4243 supplies the low-factor criteria and free-map normalization.
Wentao Li #4099, following #2513, supplies the alphabet and column bound.
Projective actions, elementary permutation groups and Latin squares
retain their classical credit. Predecessor files and credit are unchanged.
Apache-2.0.
