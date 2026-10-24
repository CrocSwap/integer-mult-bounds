# A three-power header law over every finite field

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped counting proof with finite corroboration. Let U,V be
orthogonal rank-one idempotents on F_q^m, m>=2, and let P=I-U,Q=I-V.
A complete header passes a request when every leading principal minor
through its rank is nonzero. For uniformly weighted complete GL_m(F_q)
headers, the exact probability of passing both requests is

```text
(q-1)^2 [((q^2-q+1)^2)^n - 2(q^3-q+1)^n + (q^3-q^2+1)^n]
----------------------------------------------------------------, n=m-1.
             q^2 (q^m-1)(q^m-q) q^(2m-4)
```

[PROOF.md](PROOF.md) reduces the full partial-Gram transfer to the invariant
span of three functions. The proof works in arbitrary characteristic and
in nonprime fields. For q=5 the numerator before division by the normalized
pair count is `(16/25)(441^n-2*121^n+101^n)`, with first values 192 and
112256. The joint fraction at m=2 is 2/5.

This answers the all-field closed-form question left open by
[#4261](https://github.com/CrocSwap/integer-mult-bounds/pull/4261) and
[#4273](https://github.com/CrocSwap/integer-mult-bounds/pull/4273), both
produced by Nick Petalas. Their partial-Gram transfer and binary/ternary
special cases are cited steps. The new result is the all-field invariant
space and closed form. Cinna Davis supplied the BIT request context;
source527, commdata2338 and Jose Manuel retain the normalizer lineage
credit. No predecessor implementation is imported or replayed.

## Reproduction and evidence

From the repository root, use CPython 3.12, standard library only:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/corankone-all-field-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corankone-all-field-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corankone-all-field-law --check-source-history
```

The marker is `PASS_CORANKONE_ALL_FIELD_LAW`. The verifier prints a generated
receipt with finite domains, counts and SHA256 hashes of all six package
files. It writes no artifacts. Registered replay runs both normal and
optimized modes, with warnings as errors and explicit checks active under -O.

It checks all source states over F_2,F_3,F_4,F_5 and every normalized orbit
representative over F_7,F_8,F_9. F_4 and F_8 use irreducible binary
polynomials; F_9 uses x^2+1 over F_3. Every target state is included in
each identity sum. Literal factor enumeration checks the zero and rank-one
weights separately. Every complete GL_2 header over these seven fields is
inverted and both conjugated full guards are checked. Independent full-state
evolution over F_2,F_3,F_4,F_5 checks n=0..8. Eleven exact integer evaluations certify the two displayed
initial-value polynomial identities of degree at most ten. Seven controls
distinguish boundary cases, wrong eigenvalues/coefficient, independence,
and confusing F_4 with Z/4Z.

## Scope and obligations

This is a complete-domain counting theorem for the stated two requests.
It makes no statement about arbitrary restricted header families, nonorthogonal
kernels or three or more kernels. A producer and the costs of selection,
emission, dispatch, dirty restoration, stock, precision and the full physical
caller remain unknown. No new kappa, supplier admission or selected-frontier
change is claimed. Independent human and formal proof-kernel review are
unclaimed. Lean, Docker and the selected construction's cold replay are unrun.

The card's scope is changed from proof-assistant interface work to this
explicitly open algebraic side question. TASK.json records that change.
SOURCES.json pins predecessor proof text as historical provenance; there
are no external runtime inputs.

The verifier uses bounded loops, no recursion and functions below 60 lines.
The largest full transfer has 400 states and 160,000 stored weights.
The largest identity domain has 5,184 targets and ten source representatives.
CPython's dynamic allocation is a managed-runtime deviation from fixed
allocation, bounded by these fixed domains. Warnings are errors in both
registered commands. Ruff E/F/B/UP and AST function-size inspection pass
locally. The executable result is finite corroboration, not a
formal proof-kernel check of the written theorem.

## Open next questions

1. Does the exact two-event formula imply strict negative correlation over
   every finite field? Start by comparing it with #4227's marginal squared;
   no all-field correlation theorem is claimed here.
2. Can three requests admit a similarly small all-field invariant space?
   Start with rank-one increments on 3 by 3 matrices; this proof uses the
   specific 2 by 2 determinant structure.
3. Can a real odd-field request producer use the count with a fully paid
   shared-header caller? Pin its header domain before charging selection,
   emission, dispatch, restoration and stock. Those costs remain unknown.
