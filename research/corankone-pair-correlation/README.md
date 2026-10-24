# Strict corank-one pair correlation over every finite field

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with finite corroboration. For two
requests I-U,I-V with orthogonal rank-one kernels on F_q^m, m>=2, and
uniformly weighted complete GL_m headers, let A,B be their full-leading-minor
passing events. Then

```text
Pr(A and B) < (1-q^(-m)) Pr(A)Pr(B) < Pr(A)Pr(B).
```

[PROOF.md](PROOF.md) answers Open next question 1 of
[#4747](https://github.com/CrocSwap/integer-mult-bounds/pull/4747).
It cites that predecessor's joint law and #4227's marginal law, then proves
the new inequality by two positive polynomial factorizations. The binary
and ternary strict-correlation cases retain #4261 and #4273's credit.
There is no cutoff or unrun infinite tail in the written proof.

## Reproduction and evidence

From the repository root, with CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/corankone-pair-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/corankone-pair-correlation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/corankone-pair-correlation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/corankone-pair-correlation --check-source-history
```

The direct verifier emits `PASS_CORANKONE_PAIR_CORRELATION` in generated
JSON with hashes of all six package files. It writes no receipt or other
file. Its evidence covers:

- Exact integer and rational comparisons for all 4,032 pairs
  2<=q<=64, 2<=m<=65. Non-prime-power integers test the algebra only.
  This checks the new comparison and normalization, not the predecessor
  counting proofs.
- An exact polynomial coefficient identity for
  q beta-alpha=(q-1)(2q^2-2q+1), independent of evaluations at chosen q.
- Nine controls covering independence, two correction-term mutations,
  restricted header domains and five invalid replay inputs. A separate
  reversed-polynomial-sign check also rejects its mutant.
- Exact joint-to-product ratios 28/243 at q=2,m=3, 24/49 at q=3,m=2,
  and 40/49 at q=5,m=2. These preserve the predecessor numerical values.

The written proof quantifies over every finite field and dimension. The
finite checks corroborate it; they are not formal proof-kernel acceptance.

## Scope and remaining obligations

This is an original consequence of cited formulas, not an independent audit
of them. Pending #4747 is an explicit mathematical dependency, pinned in
[SOURCES.json](SOURCES.json); no predecessor code or proof file is imported
at runtime. The source manifest binds retained-main provenance through
exact Git objects.
Its separate external citation records the pending theorem by immutable URL
and hash; the framework does not validate that bibliography entry.

The result assumes two orthogonal rank-one kernels and the complete uniform
header domain. Nonorthogonal kernels, restricted domains and three or more
requests are outside scope. PROOF.md gives a singleton-domain counterexample
to extending the inequality to restricted catalogues.

No producer, selection/emission, dispatch, dirty restoration, stock,
precision or complete physical invoice is supplied. These costs remain
unknown. No new kappa, supplier admission, selected-frontier change or
complete multiplication theorem is claimed. Independent human and formal
proof-kernel review are unclaimed. Selected cold replay, Lean and Docker
are unrun. Both registered package commands passed locally.

The verifier has fixed finite loops, no recursion and functions below
60 lines. CPython's required dynamic allocation is a deviation from fixed
allocation. Its scope is this bounded, read-only finite replay, with at most
one parameter pair active, six file hashes, three retained examples and
polynomials of at most seven coefficients. The declared q,m limits bound
integer sizes. Invalid-domain controls exercise exhaustion behavior.
Warnings are errors in both registered modes. Ruff E/F/B/UP passes locally.
Follow-up: retain these bounds if adding replay inputs; a larger search
needs a fresh resource bound.

## Related work and credit

- Nick Petalas's [#4747](https://github.com/CrocSwap/integer-mult-bounds/pull/4747),
  head f51dcebce79b8b8958427a9a9b7bc8feca352c9d, supplies the all-field
  joint law. At q=5,m=2, J=2/5 and p=7/10 give ratio 40/49, checked here.
- Nick Petalas's #4227 supplies the marginal law. #4261 and #4273 supply
  the binary and ternary pair laws and their strict negative correlation.
  New here is the all-field inequality and its explicit relative gap.
- #4599 and Ryanson Jonathan's #4607 prove binary four- and five-request
  product inequalities. Ryanson Jonathan's #4606 independently checks the
  four-event inequality. Their request counts differ from this two-event
  theorem; no four- or five-event number is claimed here.
- Ryanson Jonathan's #4605 recounts binary threshold headers. At its
  overlapping k=2,m=3 case, J=1/84 and p=9/28 give ratio 28/243,
  checked here; 168J=2 headers.
- Nick Petalas's #4598 and Ryanson Jonathan's #4619 count and classify
  five-request threshold decompositions. Their k=5 counts do not overlap
  this two-request theorem.

The earlier counting packages above are produced by Nick Petalas unless
otherwise attributed. Cinna Davis supplies the BIT request context;
source527, commdata2338 and Jose Manuel retain the normalizer lineage credit.
The card's scope change and overlap coverage are recorded in TASK.json.

## Open next questions

1. Does negative association hold for disjoint groups in larger orthogonal
   kernel families? First compare Pr(A1 A2 A3) with Pr(A1 A2)Pr(A3) using
   #4275's binary three-request law. Pairwise negative correlation alone
   does not imply this stronger property.
2. Can an actual odd-field producer exploit a shared header with a complete
   paid invoice? Pin its kernel lines and header domain before charging
   selection, emission, dispatch, restoration and stock. No caller is
   supplied here.
