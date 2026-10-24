# Exact five-factor cost for binary three-role products

A complete finite certificate gives a sharp formal-alphabet result. Every
invertible three-role target over F2^k costs at most five paid factors
I+u b^T, where b is a common binary vector and u may vary by component.
The target over F2^168 listing all elements of GL3(F2) costs exactly five,
even with arbitrary free GL3(F2) maps anywhere. Its column lower bound is
only three. No new kappa or native supplier is claimed.

The chronological upper directions are e1,e2,e3,e1,e2. All 2401 ordered
four-direction words reach at most 144 of the 168 group elements. The
[proof and scope](PROOF.md) explain why this finite census gives the
all-k upper bound and survives arbitrary interleaved free maps. This
extends ToikY's #4334 two-role product-field result. The contribution is
the exact common-direction obstruction and certificate in this model;
classical short register-update programs retain the credit listed there.

## Evidence and reproduction

From the repository root, using CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-three-role-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-three-role-products/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-three-role-products
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-three-role-products --check-source-history
```

Any CPython 3.12 installation can replace the local interpreter path.
Expected scientific marker:

```text
PASS_RIGHT_VECTOR_THREE_ROLE_PRODUCTS group=168 words4=2401 max4=144 upper=5 delta=3 controls=7
```

Two algorithms compare every complete four-word endpoint set. The second
enumerates 614656 parameter tuples as permutations of the eight binary
vectors. The fixed upper word has 1024 parameter tuples and reaches all
168 endpoints; its chosen witnesses pass all 1344 component/input cases.
All 168 free right translations and delta cases, 4704 labelled
conjugations and seven rejection controls pass. A generated JSON receipt
binds results and file hashes; nothing is written into the checkout.

The four-word histogram, indexed by reachable-set size, is
`{4:7,16:126,24:420,64:504,96:672,144:672}`. The verifier derives it afresh
and checks the complete masks with a second implementation. This is a
finite certificate with a scoped algebraic consequence. It is not a search
failure offered as a universal obstruction.

## Limits and implementation discipline

The field is F2, there are exactly three roles, and only invertible product
components are covered. The sharp witness uses 168 components; minimal
component count is open. Native preparation, routing, storage, dirty-state
restoration, precision, stock and the full supplier invoice remain unknown.
The selected construction is unchanged. Lean, Docker and a selected cold
replay are outside scope and unrun. Independent human and formal
proof-kernel review are unclaimed.

The verifier uses bounded loops, explicit exceptions and no recursion.
Its largest direction census has 2401 states, each with at most 168
endpoints; the action multiplication table has 168^2 entries. CPython
requires dynamic allocation, so fixed allocation is a documented managed
runtime deviation, with collection sizes bounded by those finite domains.
Functions stay under 60 lines. Warning-strict ordinary and optimized
commands are registered. The negative-control dispatcher has seven fixed
call targets; it is the only callback-based test dispatch. File errors
propagate, and all file handles are owned by pathlib's bounded read calls.
No package-wide configuration change is needed for this isolated script.

## Open next questions

1. What is the minimum k for which an invertible target over F2^k costs
   five? This would replace the deliberately large universal witness.
   Start with the complement sets of the already computed four-word masks
   and their common right translates. This is a new covering problem;
   the present certificate does not settle it.
2. Which changed physical contract realizes one of these shared-direction
   factors? Start with a named producer and consumer and account for
   coefficient preparation, overwrites and restoration. All such physical
   costs are unknown; this formal result does not authorize a supplier
   construction campaign.

## Credit

This contribution was produced by Nick Petalas. Credit ToikY #4334 for the
product-field question and two-role common-direction construction;
Nick Petalas #4243/#4265/#4276/#4749 for the retained cost framework; and
Wentao Li #4099 following #2513 for the alphabet and column bound. Classical
memoryless-computation work by Gadouleau, Riis, Cameron and Fairbairn is
linked in PROOF.md. Predecessor files and credit are unchanged. Apache-2.0.
