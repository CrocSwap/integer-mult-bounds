# Exact binary parameter law for the Desargues interface

This contribution was produced by Nick Petalas. Claim type: scoped algebraic
proof, direct construction and exhaustive finite corroboration. No new kappa.

For every field K of characteristic two, normalize the labelled projective
frame (O,A0,A1,A2) to (e1,e2,e3,(1,1,1)) and write

```
B0=(u,1,0), B1=(v,0,1), B2=(1+w,1,1).
```

The resulting Desargues 10_3 candidate has exactly its thirty designated
point-line incidences if and only if 1,u,v,w are F2-linearly independent.
Thus the exact number of normalized labelled candidates over Fq is
`(q-2)(q-4)(q-8)`, and such a candidate exists exactly when the binary
field dimension is at least four. Any supplied binary basis beginning
with 1 gives a direct constructor. F32 works without an F16 subfield.

[PROOF.md](PROOF.md) gives the normalization argument, all point and line
coordinates, and the complete 100-entry factored dot-product table. The
fourteen nonconstant binary affine forms all occur as nonincidences.
This supplies the explicit parameter criterion and constructive answer to
Open next question 4 of Sagar Thakrar's
[PR2274](https://github.com/CrocSwap/integer-mult-bounds/pull/2274).
The predecessor's finite field exclusions and decoder-cost results are
cited context and were not replayed.

## Reproduce

From the repository root, use CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/desargues-binary-parameter-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/desargues-binary-parameter-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/desargues-binary-parameter-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/desargues-binary-parameter-law --check-source-history
```

The first two commands also work from an unrelated directory when the
script path is absolute. Each prints a generated JSON receipt bound to all
six package files, then `PASS_DESARGUES_BINARY_PARAMETER_LAW`. The receipt
reports 30 symbolic incidences, 70 nonincidences and 14 required affine
forms. Its independent cross-product implementation checks all 32,768
triples over F32, with 20,160 exact and 12,608 rejected. All fourteen
single-relation cases occur, so omitting any one affine condition admits
an invalid candidate. It also checks one degree-four construction, two
symbolic corruptions and rejection of an unsupported field argument.
Normal and optimized execution retain the same checks. No receipt is
hand-written or stored as an acceptance oracle.

## Scope and credit

This is a side result for exact frame-universal decoder certificates.
It changes the formal-interface-lemma card to a written field-interface
proof, without a proof-kernel claim or a binding to the selected caller.
It covers normalized labelled realizations. Unlabelled orbit counts,
physical native realization, dirty restoration, a complete supplier
invoice, supplier admission and the selected frontier are outside scope.
Independent human and formal proof-kernel review are unclaimed. No Lean,
Docker, predecessor scientific suite or selected cold replay was run.

Sagar Thakrar / thakrarsagar supplied the explicit question, exact
incidence contract and normalization in PR2274, retained at
`67294e7dd5bc7caa0d253b74e1d39c376ca99663`. DreamingOfClouds supplied the
three-total and CR2 context; its inherited cost implications are not used
in this proof. The contribution retains the classical Desargues,
projective-frame and finite-field lineage. Bruen, Bruen and McQuillan's
[primary paper](https://arxiv.org/abs/2007.09175), Theorems 3.2 and 4.3 and
Section 10, supplies the simplex-section context and the distinction
between general configurations and the strict incidence interface. It
also cites Puystjens and Thas for earlier strict enumeration. No
literature-wide embedding or counting priority is claimed. The new
repository contribution is the explicit normalized parameter law,
constructor and complete polynomial certificate, rather than a new
classical geometry theorem.

Live claims, local reservations, main README and merged/open PR searches,
and recent account work were checked before claiming and will be refreshed
before publication. Main-tree and API searches do not cover arbitrary
historical diffs or unpublished work. No open PR in the checked live list
studied this normalized Desargues quantity.

## Open next questions

1. Can the binary-independence constructor replace the stored
   frame-universal assignments for an actual support-restricted frame?
   First transport the normalized coordinates through one named frame
   and prove every required zero and nonzero support constraint. A general
   projectivity need not preserve those constraints.
2. Can the same explicit parameter method settle field requirements for
   another rich configuration? First derive its normalized dot-product
   factors. There is no reason to assume they form all binary affine
   forms, and mixed-frame support restrictions remain a separate problem.

## Verifier bounds

All loops have fixed finite bounds. The largest enumeration is 32^3
triples, with 100 point-line tests per triple. Polynomial products have
three variables and total degree at most two, hence at most ten monomials.
Functions are shorter than sixty physical lines; failure checks use
explicit exceptions and survive optimized Python. The verifier has no
recursion, network, subprocess, mutable shared state or output files.

Power of Ten rule 3 has a managed-runtime deviation: Python allocates
integers, sets, tuples and the JSON receipt during execution. Fixed field
sizes, ten-point/ten-line geometry and the polynomial degree limit bound
live mathematical state. Only one triple is retained at a time. The six
receipt inputs have a 256 KiB per-file admission bound. Direct normal and
optimized checks verify this bounded implementation. A fixed-memory
rewrite would be needed only for deployment on a constrained runtime;
none is claimed. Python runtime allocations themselves are not audited.
