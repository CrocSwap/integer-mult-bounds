# Positive correlation for a common-covector full-guard pair

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped counting proof with finite corroboration. Over any finite
field F_q, let a,c be independent columns, b a row with ba=bc=1, and
P=I-ab, Q=I-cb on F_q^m, m>=2. For complete uniformly weighted GL_m(F_q)
headers, the joint full-guard passing fraction is exactly

```text
           (q-1)[(q^2+(q-1)^3)^(m-1) - (q^2-q+1)^(m-1)]
J(q,m) = ------------------------------------------------- .
                    (q^m-1)(q^m-q)q^(m-2)
```

Over F_2 these two guard events are strictly positively correlated in every
dimension m>=2. At m=2, J=1/3 exceeds the marginal product 1/4; at m=3,
J=4/21 and each marginal is 9/28. Thus negative correlation for the known
orthogonal and one-way cases does not extend to every two-way pair.

[PROOF.md](PROOF.md) counts the common-covector header orbit by two partial
sums, subtracts exactly the equal-column paths, and proves the binary
comparison for all dimensions. This answers one case of Open next question 1
in [#4778](https://github.com/CrocSwap/integer-mult-bounds/pull/4778). That
question and #4769/#4274's contrasting one-way law retain Nick Petalas's
credit, as do #4227's marginal law and #4261's partial-sum/header method.
Cinna Davis supplied the BIT request context; source527, commdata2338 and
Jose Manuel retain the normalizer and recursive-closure lineage credit.
No predecessor implementation is imported or replayed.

## Reproduction and evidence

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/common-covector-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/common-covector-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/common-covector-header-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/common-covector-header-law --check-source-history
```

Another CPython 3.12 installation may replace the local interpreter path.
The direct marker is `PASS_COMMON_COVECTOR_HEADER_LAW`. The verifier writes
no files. It prints a generated receipt with every domain's counts and
SHA256 hashes of all six package files. Both registered modes keep explicit
checks active, including optimized Python.

The verifier enumerates all 34,290 complete headers in eight domains:
GL_2 over F_2,F_3,F_4,F_5,F_7, GL_3 over F_2,F_3, and GL_4 over F_2.
It inverts each header, conjugates both literal projectors and tests every
leading minor through rank m-1. Both marginals and the joint count agree.
F_4 is F_2[x]/(x^2+x+1), rather than integers modulo four.

A separate vector enumeration counts all 26,070 independent orbit triples
in nine domains: q=2,m=2..5; q=3 or 4,m=2..3; q=5,m=2. Ten coordinate
transfers enumerate the actual increment factorizations for widths one and
two over F_2,F_3,F_4,F_5,F_7, at path lengths zero through eight. Their
difference agrees with the joint formula at m=2..9. Exact rational checks
corroborate binary positive correlation in all 255 dimensions m=2..256.
Fourteen fixture, mutation and invalid-input controls distinguish the
field arithmetic, independence, orthogonal substitution, omitted diagonal
subtraction, omitted row fiber and invalid finite-check parameters.

## Scope and implementation limits

The all-field and all-dimension claims rest on the written proof. Finite
execution corroborates the explicitly enumerated domains. Only two distinct
rank-one kernels with a common right covector and complete equally weighted
headers are covered. Other two-way pairs, larger families, restricted
headers and odd-field correlation signs are outside the proved claims.

Header selection, emission, dispatch, dirty restoration, stock, precision,
producer compatibility and the complete paid physical caller remain unknown.
No new kappa, supplier admission, selected-frontier change or complete
multiplication theorem is claimed. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and the selected operator replay are unrun.

[TASK.json](TASK.json) records the change from the formal-interface card to
this algebraic side question. [SOURCES.json](SOURCES.json) binds predecessor
text, the catalogue and selected record as historical provenance on canonical
main. There are no runtime dependencies outside this package and no pending
Git-object dependency. Provenance/history checks require full Git history;
the direct verifier also runs from a standalone exported package.

Power of Ten inspection finds no recursion or subprocesses in the verifier.
Every loop is bounded by fixed domains: at most 65,536 candidate matrices
of size four, 64 vectors per triple coordinate, 49 transfer states, nine
transfer rounds and 255 correlation dimensions. Functions fit within 60
lines. Explicit require checks enforce input and mathematical contracts.
CPython allocates dynamically, a managed-runtime deviation from fixed
allocation; the stated domains bound live collections. Diagnostics use
warnings as errors. No shared implementation is changed.

## Open next questions

1. Determine the law for two-way pairs with independent covectors. Start
   with one normalized pair whose two cross products are nonzero; its
   partial-Gram orbit differs from the shared-covector model here.
2. Determine the correlation signs for this common-covector family over
   odd fields. Compare the new joint formula with #4227's marginal squared,
   starting with q*delta-alpha^2=q-1; a quantified sign proof is unclaimed.
3. Find a named physical producer and fully charged shared-header caller.
   Pin its header domain before charging selection, emission, dispatch,
   dirty restoration, precision and stock. Those costs are unknown.
