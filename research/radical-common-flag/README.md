# Exact radical reachability through a common flag

This contribution was produced by Nick Petalas. Apache-2.0.

For every field K, n>=1 and finite coefficient tuple, a pure square-zero
target with an invertible coefficient has a complete reachability criterion:

```text
R=K[t_0,...,t_s]/(all t_i*t_j), C_0 invertible,
M=sum_j t_j*C_j,
paid factors I+u*v^T, u in R^n, v in K^n; free GL_n(K) maps.

M is reachable exactly when C_0^-1*C_1,...,C_0^-1*C_s
have a common complete invariant flag over K.
When reachable, the exact paid cost is n.
```

Claim type: scoped written algebraic proof with exact finite corroboration.
The theorem concerns exactly n roles and the stated formal alphabet.
No new kappa or supplier admission is claimed.

[PROOF.md](PROOF.md) answers Open next question 1 of
[PR5854](https://github.com/CrocSwap/integer-mult-bounds/pull/5854).
The new argument identifies a common invariant subspace at every scalar
rank drop, giving the full flag. A column-replacement word attains the
lower bound. The earlier common-eigenrow obstruction and PR4776's
two-generator classification are credited results, not audit targets.
A four-role example passes the split-determinant and common-eigenrow
tests but fails the new complete criterion over every field.

## Exact evidence

The standalone verifier imports no predecessor code. Two separately
constructed finite descriptions, projective lines and planes versus every
invertible change of basis, agree on all ordered coefficient pairs in:

- M_2(F2)^2, all 256 pairs, with 148 reachable;
- M_2(F3)^2, all 6,561 pairs, with 2,457 reachable;
- M_3(F2)^2, all 262,144 pairs, with 47,968 reachable.

These counts concern targets `t_0 I+t_1 A+t_2 B`. They are new finite
corroboration of the criterion, not a classification of all radical matrices.
The checker also records the complete common-flag multiplicity histogram.

Exact square-zero matrix multiplication checks 5,062 attaining words.
They include every pair of upper-triangular coefficients in the three
domains, all 168 binary three-role basis changes of one noncommuting
tuple with a nonidentity distinguished coefficient, one- and four-role
boundaries, odd characteristics and the vacuous coefficient tuple.
A separate literal coefficient interpreter checks 2,272 arbitrary-input
basis columns. At 1,150 chronological cuts, the rank, image, coefficient
and invariance identities hold. The abstract cut check covers all 58
binary two-by-two scalar pairs with SH=0 and all 1,584 indexed (H,S,X,Y)
cases with X invertible. It enumerates each cut's coefficient
image from every D/E choice before deduplication.

Twelve controls cover six invalid constructor contracts, three omitted
paid factors, reversed chronology, a singular distinguished coefficient
and a counterexample when SH=0 is omitted. The four-role strict
obstruction is checked separately over F3. The universal claim rests on
the written proof, not extrapolation from these finite domains.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -X dev -B research/radical-common-flag/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -X dev -B research/radical-common-flag/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/radical-common-flag
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/radical-common-flag --check-source-history
```

Any CPython 3.12 path can replace the host-specific interpreter. The direct
marker is `PASS_RADICAL_COMMON_FLAG`. Each run generates a stdout JSON
receipt bound to all six package files by SHA256. No receipt is handwritten
or stored in the package. Both registered modes run the same checks and
write nothing to the checkout. Each command has a 120-second limit.

[SOURCES.json](SOURCES.json) pins the task catalogue, selected record and
two predecessor texts as historical provenance. None is an executable or
runtime input. The direct verifier works in a Git-free package export;
the repository metadata and source-history checks require Git history.

## Scope and verification limits

The formal-interface-lemma card is explicitly changed to this algebraic
side question in [TASK.json](TASK.json). Base is canonical main
`7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8, selected
PR6030. The source-binding orientation passed; it authenticates metadata,
not a mathematical or native supplier claim. The
[advance CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19375372)
followed live overlap and reservation checks. Cached overlap covered 572
open PRs and 6,639 Discussion records with complete remote pagination.
Sparse local notes omitted most main-tree packages, so targeted Git-tree
and merged/general-form searches supplement that incomplete coverage.
Unpublished work and arbitrary historical diffs remain outside coverage.

Without an invertible coefficient, with a nonzero scalar endpoint, with
higher nilpotency or with restored extra roles, a new argument is needed.
The paid factors may be singular. Native realization, physical coefficient
preparation, reversible restoration, precision, stock, tape, complete paid
invoice, compiler and outer admission remain separate. No selected-frontier
change or complete multiplication theorem follows. All five framework
assumptions remain. Selected cold replay, Lean, Docker, independent human
and formal proof-kernel review are unrun or unclaimed.

The verifier has no recursion, subprocesses, network, dynamic evaluation or
write path. Matrices have at most four rows and coefficients are in F2,
F3 or F5. Complete pair domains stop at 512^2. Invertible basis inventories
stop at 168 matrices. The largest cut-vector domain has 625 vectors. All functions are
below 60 physical lines and all gates use explicit exceptions under -O.
Six file reads are capped at 128 KiB each. Warning-strict normal and
optimized execution and syntax/AST inspection provide diagnostics.

Power of Ten rule 3 has a managed-runtime deviation in verify.py. Python
allocates integers, tuples and sets during execution; the fixed domains
above bound live collections, including at most 512 matrix masks of
168 bits and one active finite pair scan. No fixed-memory runtime or
allocator-overhead bound is claimed. A larger input domain requires new
capacity limits before changing this verifier. No shared build setting or
historical implementation is changed.

## Open next questions

- Can a restored extra role enable an excluded target? Start with diag(M,1)
  for the four-role example and preserve every dirty-input column. The
  scalar endpoint is then nonzero and the distinguished coefficient is
  singular on the larger space, so the present cut equality does not apply.
- Which zero-residue targets without an invertible coefficient are reachable?
  Start with one explicit singular tuple and its source/image flags. Excess
  dimension in the cut image prevents the current invariant-flag conclusion.

Structured first steps and blockers are in TASK.json. No further extension
is included in this contribution.

## Credit

Nick Petalas / PR5854 supplied the explicit question and common-eigenrow
obstruction; PR4773 supplied the first-zero argument; PR4776 supplied the
two-generator split-pencil classification; and PR4243 supplied the free-map
normal form. Retain Wentao Li / PR4099 following PR2513 and ToikY / PR4334
for the paid alphabet and shared-chart context. Rank-nullity, rank-one
perturbations and adapted bases are classical. The new contribution is the
all-cut flag criterion, exact attaining cost and finite corroboration.
Predecessor bytes and credit remain unchanged. No general literature
priority is claimed. Independent human and formal proof-kernel review
are unclaimed.
