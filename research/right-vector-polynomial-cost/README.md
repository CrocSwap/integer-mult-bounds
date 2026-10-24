# Two-role polynomial targets have unbounded right-vector cost

Claim type: scoped proof, with a finite exact certificate. No new kappa.

In the alphabet `I+u y^T`, with `u in F2[t]^2`, binary `y`, and free
`GL2(F2)` maps anywhere, put

```text
U = [[1,t],[0,1]], L = [[1,0],[t,1]].
M = (UL)^2 = [[1+t^2+t^4, t^3], [t^3, 1+t^2]].
cost(M) = 4; cost((UL)^k) = 2k for every k >= 1.
```

This answers Open next question 1 of
[Nick Petalas's #4276](https://github.com/CrocSwap/integer-mult-bounds/pull/4276)
negatively: reachable two-role targets need not have three-factor words over
every coefficient algebra. The gap from `delta`, which equals two on this
family, is unbounded. The algebra is commutative but not semilocal, so this
lies outside the three-factor theorem of
[#4749](https://github.com/CrocSwap/integer-mult-bounds/pull/4749), pinned at
`29e4d3a25225a219f97c3a2815ed3a5a8fd9b891`.

[PROOF.md](PROOF.md) reduces every invertible paid factor to a transvection,
removes its constant part using the free group, and proves uniqueness of the
resulting reduced word by polynomial degree. Its reduced length is the exact
paid cost. The normal-form structure is classical polynomial-matrix theory;
the contribution is its explicit cost consequence for the repository's
restricted alphabet and its open three-factor question.

## Evidence and reproduction

The verifier uses literal binary polynomial arithmetic and no predecessor
code. It enumerates every invertible 2x2 polynomial matrix whose maximum
entry degree is at most four. The 1,536 distinct targets have exact cost
histogram `[6,270,612,504,144]` for costs zero through four. The written degree
proof establishes why arbitrary larger coefficients cannot produce additional
shorter words in this domain. All 1,008 reduced expressions of degree four
and length at most three, including every free endpoint, miss M.

A separate literal alphabet check enumerates all three nonzero binary right
vectors and all `32^2` polynomial left vectors of degree at most four.
Exactly 96 parameter tuples are invertible, including repeated identities.
Every tuple passes the constant split and all six free conjugations.
Seven controls distinguish equal-direction cancellation, constant polynomial
relations, specialization at zero, a dropped factor, reversed order, a
singular factor and a changed target entry. Every comparison remains active
under optimized Python. No generated output is written to the checkout.

From the repository root, using the Python 3.12 standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B -W error research/right-vector-polynomial-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -B -W error research/right-vector-polynomial-cost/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/right-vector-polynomial-cost
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/right-vector-polynomial-cost --check-source-history
```

Expected marker: `PASS_RIGHT_VECTOR_POLYNOMIAL_COST targets=1536 cost4=144
target_cost=4 shorter_exclusions=1008 controls=7 no_new_kappa`.
The receipt is freshly generated from actual checks and hashes every package
file. It is not a handwritten verification receipt.

## Limitations

The universal argument is a written scoped proof. Its finite certificate
corroborates the degree-four domain; it does not prove the infinite statement
by enumeration. The base field is binary, the coefficient algebra is F2[t],
and there are two data roles with no scratch. Singular targets, other base
fields and multivariate algebras are not classified. Free maps must be binary.
Native preparation, conversion, routing, control, precision, restoration and
stock costs are unknown. No supplier, selected-frontier change or complete
multiplication theorem is claimed. Independent human and formal proof-kernel
review are unclaimed. Lean, Docker and the selected operator replay were not
run and are outside this result's obligations.

The verifier uses managed Python allocation with an explicit finite domain.
The census stores 256 normal words and 1,536 targets. Enumeration has at most
four factor rounds, three directions, 15 nonconstant coefficients and six free
maps; the literal control examines 3,072 tuples. Polynomial multiplication
accepts at most 32 bits per operand and iterates over at most 32 bits.
Functions are below 60 lines, recursion and dynamic code are absent, and both
registered commands make warnings errors. Python allocation is a documented
allocation deviation with these fixed bounds; no real-time claim is made.

## Open next questions

1. Classify exact costs over `F2[s,t]`. Start with a named reachable word and
   distinguish its cost from general reachability. The present one-variable
   normal-form and Euclidean arguments do not settle that algebra.
2. Identify one coefficient algebra in a literal native producer/consumer,
   then price left-coefficient preparation and the complete physical bill.
   All native costs listed above remain blockers to a supplier construction.

## Credit

This contribution was produced by Nick Petalas. The right-vector alphabet and
column lower bound are Wentao Li's #4099, building on #2513. Nick Petalas's
#4243 supplies the free-map normal form, and #4276 supplies the one-factor
criterion and asks the all-algebra three-factor question answered here.
ToikY's #4334 and Nick Petalas's #4601/#4749 supply the field-product,
local-product and semilocal predecessor boundaries. Their proofs and
certificates are cited, not re-audited.

The polynomial-matrix group structure and degree method retain Hirosi
Nagao's credit, *On GL(2,K[x])*, 1959, Theorem 2 and its proof
([original paper](https://www.i-repository.net/contents/osakacu/sugaku/DB-M-010-02-04.pdf)).
The restricted-alphabet cost consequence is proved here without relying on
a machine implementation of that theorem. Apache-2.0.
