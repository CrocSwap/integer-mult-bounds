# A one-query obstruction up to the combined carrier width

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped written proof with exact finite corroboration. No new kappa.
For the triangular carrier

    C = [[Q-I,N],[Q,0]],       T = C direct-sum I_K,

one coordinate query of width w, arbitrary restored dirty helpers and invertible
endpoints with carrier-block column supports s,t must satisfy

    w >= 2M   or   s t >= min(mu_Q^-2,mu_N^-2),

when Q,N are M by M unitaries with maximum entry moduli mu_Q,mu_N.
The general all-field version uses an explicit sparse-vector separation
condition. [PROOF.md](PROOF.md) gives the full contract and proof.

This extends Ross Richardson's [PR4057](https://github.com/CrocSwap/integer-mult-bounds/pull/4057)
width regime from w<=M to every w<2M. In particular, merely widening one query
into the range M<w<2M does not bypass that endpoint obstruction. Its native
specialization has support threshold 4^f; under its ADD support contract the
inherited floor of 2f endpoint ADDs applies throughout the larger width range.
Neither the threshold 4^f nor the coefficient 2f is claimed as new.

The new step is the dimension inequality 2M+K-w<=K after the predecessor's
carrier-row vanishing argument. It permits arbitrary query-coordinate positions
and unrestricted helper row blocks. At w=2M an arbitrary query on the combined
carriers attains the algebraic width threshold. That attainer supplies no native
query implementation or physical bank merger. An exact rational example shows
why the support inequality in the obstruction must be strict.

## Evidence and reproduction

From the repository root, using the standard library on CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/wide-one-query-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/wide-one-query-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/wide-one-query-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/wide-one-query-threshold --check-source-history
```

Substitute another host's Python 3.12 executable as needed. The direct checker
prints a generated JSON receipt followed by `PASS_WIDE_ONE_QUERY_THRESHOLD`.
The generic runner adds `PASS_REGISTERED_RESEARCH_PACKAGE`. Normal verification
writes no files. Optional `--receipt /absolute/path/outside/checkout.json`
writes the generated receipt with SHA256 hashes of all six package files,
refuses an existing destination and rejects paths inside the checkout.

The finite checks are newly written examples of the extended width contract,
not a replay or audit of the predecessor's native matrices or certificate:

- Every one of the 147,456 pairs of invertible monomial endpoints over F3 in
  dimension four is tested for one fixed dense two-carrier map. The checker
  computes the smallest coordinate set containing every nonidentity row and
  column of F^-1 T G. Every pair requires all four coordinates.
- All 50,304 permutation/active-coordinate-set pairs with M=2 and K=0,1,2
  are enumerated. Untouched literal columns obstruct all 33,720 cases with
  w<4, including 15,696 cases at the newly covered width w=3. For the 3,144
  feasible active sets the checker constructs and checks the query with F=G.
  No scaling choices are enumerated in this separate helper census.
- The eight invertible fully nonzero two by two matrices over F3 give 64
  ordered pairs Q,N. The checker constructs 960 queries of width at least
  four with up to four helper coordinates, verifies their invertibility,
  and executes all 6,400 arbitrary-input basis columns. Thirty-two nonzero
  one-sparse input checks establish the small separation fixtures.
- The rational unitary H4/2 checks 80 nonzero vectors from {-1,0,1}^4,
  including 40 support-uncertainty equalities. Exact two-sided inverses and
  literal query matrices verify the width-2M attainer, the support-equality
  zero-query counterexample and a monomial zero-query control. Four malformed
  query descriptors reject in both Python modes.

The all-parameter claim is the written dimension proof. These finite checks
corroborate it; they are not human acceptance or a formal proof-kernel result.

## Scope, sources and credit

Canonical base is `7c49fe32c55de02c2c873655c804b16e4c3fef0a`, priority revision 8,
with selected PR6030 unchanged. The card's first baseline command passed with
`PASS_RESEARCH_BASELINE_BINDINGS_ONLY`. This changes the card's scope to one
consumer-width obstruction, rather than a completed supplier or invoice.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19372332)
records the question before the new finite work.

[SOURCES.json](SOURCES.json) pins the predecessor proof and README at
`bf793d8739ad26f2aaba023de6bebca50fc67356` as historical provenance. No
predecessor executable or external scientific input is imported. Credit Ross
Richardson for the carrier, untouched-column argument, support method, native
amplitudes and prior w<=M result; icekylinx/PR531, Rohan Arun/kernel92,
Clear1nsight/PR3987 and ToikY/PR4002 for the retained native/compiler and
signed-lift lineage. Rank-nullity and support uncertainty are classical.
Independent human and formal proof-kernel review are unclaimed.

Live open/account PRs, recent handoffs and local reservations, all-main README
searches for the object and general width formula, and merged-PR searches were
checked. Sparse local overlap coverage is incomplete; arbitrary historical
diffs and unpublished work are not covered. No literature-priority claim is
made for the linear-algebra methods.

The theorem requires exact helper return, coordinate queries, the stated
carrier and sparse endpoint blocks. Dense active subspaces, multiple
interleaved queries, discarded helpers, rounded execution and changed carrier
maps are outside it. Rectangular helper dictionaries must actually satisfy
the column-support bounds. Native realization, ownership, hosting, precision,
tape work, compiler closure and a complete paid supplier bill remain unproved.
No selected cold replay, Lean or Docker run is warranted or claimed.

## Engineering constraints

Power of Ten inspection covers this checker only. All functions stay below
60 lines; loops have fixed domains with matrices at most eight by eight,
384 monomial endpoint descriptors, 147,456 endpoint pairs and at most 720
permutations in the helper loop. There is no recursion, project import,
dynamic code loading or subprocess. Explicit exceptions keep invariants
enabled under optimization. Python's managed arithmetic, iterators and
collections allocate during the finite run, a rule-3 deviation; live storage
is bounded by those domains and the six small source files. Allocator internals
are not inspected. A variable-size implementation needs its own capacity
review. Warning-strict normal and optimized replay supply interpreter
diagnostics; local lint availability and results are recorded in the PR.

## Open next questions

Can a physically legal query of width at least 2M improve the complete matched
caller bill? First specify one widened query bank, acquisition word, arbitrary
dirty inputs and full restoration. Then price every operation. The relaxed
attainer supplies neither a native implementation nor a favorable full invoice.
This contribution stops at the width obstruction; it proposes no construction
expansion. [TASK.json](TASK.json) records the same question and blocker.
